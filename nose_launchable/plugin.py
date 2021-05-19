import os
import sys
from io import StringIO
from time import time

from nose.plugins import Plugin
from nose.plugins.capture import Capture
from nose.plugins.xunit import Tee

from nose_launchable.case_event import CaseEvent
from nose_launchable.client import LaunchableClientFactory
from nose_launchable.log import logger
from nose_launchable.manager import get_test_names, subset, get_test_path
from nose_launchable.protecter import protect, handleError
from nose_launchable.uploader import UploaderFactory

BUILD_NUMBER_KEY = "LAUNCHABLE_BUILD_NUMBER"


class Launchable(Plugin):
    name = "launchable"
    # Grab override sys.stdout after the capture plugin
    score = Capture.score - 1
    encoding = 'UTF-8'

    def __init__(self):
        super().__init__()

        self._capture_stack = []
        self._currentStdout = None
        self._currentStderr = None

    def options(self, parser, env):
        super(Launchable, self).options(parser, env=env)
        parser.add_option("--launchable-subset", action='store_true', dest="subset_enabled",
                          help="Enable Launchable subsetting")
        parser.add_option("--launchable-build-number", action='store', type='string', dest="build_number",
                          help="CI/CD build number")
        parser.add_option("--launchable-subset-target", action='store', type='string', dest="subset_target",
                          help="Target percentage of subset")

        parser.add_option("--launchable-subset-options", action='store', dest="subset_options",
                          help="Launchable CLI subset command options")

        parser.add_option("--launchable-record-only", action='store_true', dest="record_only_enabled",
                          help="Enable Launchable recording")

    def configure(self, options, conf):
        super(Launchable, self).configure(options, conf)

        self.subset_enabled = options.subset_enabled or False
        self.record_only_enabled = options.record_only_enabled or False

        self.build_number = options.build_number or os.getenv(BUILD_NUMBER_KEY)
        self.subset_target = options.subset_target
        self.subset_options = options.subset_options

        if not (self.subset_enabled or self.record_only_enabled):
            # we didn't get activated
            return

        if os.environ.get(LaunchableClientFactory.TOKEN_KEY) is None:
            logger.warning("%s not set. Deactivating"%LaunchableClientFactory.TOKEN_KEY)
            return

        if self.subset_enabled and self.record_only_enabled:
            logger.warning("Please specify either --launchable-subset or --launchable-record-only flag")
            return

        if self.build_number is None:
            logger.warning("Please specify --launchable-build-number flag")
            return

        if self.subset_enabled and not ((self.subset_target is None) ^ (self.subset_options is None)):
            logger.warning("Please specify either --launchable-subset-target or --launchable-subset-options flag")
            return

        try:
            self._client = LaunchableClientFactory.prepare()
            self._uploader = UploaderFactory.prepare(self._client)
        except Exception as e:
            handleError(e)
            return

        # only if every validation checks out we are good to go
        self.enabled = True


    @protect
    def begin(self):
        self._client.start(self.build_number)
        self._uploader.start()

    @protect
    def prepareTest(self, test):
        if self.subset_enabled:
            self._print("Getting optimized test execution order from Launchable...\n")

            self._subset(test)

            self._print("Test execution optimized by Launchable ")
            # A rocket emoji
            self._print("\U0001f680\n")
            return test

    @protect
    def startContext(self, context):
        self._startCapture()

    @protect
    def stopContext(self, context):
        self._endCapture()

    @protect
    def beforeTest(self, test):
        """Initializes a timer before starting a test."""
        self._timer = time()
        self._startCapture()

    @protect
    def afterTest(self, test):
        self._endCapture()
        self._currentStdout = None
        self._currentStderr = None

    @protect
    def addError(self, test, err, capt=None):
        type, value, traceback = err
        if type not in (ImportError, ValueError):
            self._addResult(test, CaseEvent.TEST_FAILED, self._uploader.enqueue_failure)

    @protect
    def addFailure(self, test, err, capt=None, tb_info=None):
        self._addResult(test, CaseEvent.TEST_FAILED, self._uploader.enqueue_failure)

    @protect
    def addSuccess(self, test, capt=None):
        self._addResult(test, CaseEvent.TEST_PASSED, self._uploader.enqueue_success)

    @protect
    def finalize(self, test):
        while self._capture_stack:
            self._endCapture()

        self._uploader.join()
        self._client.finish()

        self._print("Test results have been successfully uploaded to Launchable\n")

    def _subset(self, test):
        test_names = get_test_names(test)

        targets = self._client.subset(test_names, self.subset_options, self.subset_target)

        subset(test, set(targets))

    def _startCapture(self):
        self._capture_stack.append((sys.stdout, sys.stderr))
        self._currentStdout = StringIO()
        self._currentStderr = StringIO()
        sys.stdout = Tee(self.encoding, self._currentStdout, sys.stdout)
        sys.stderr = Tee(self.encoding, self._currentStderr, sys.stderr)

    def _endCapture(self):
        if self._capture_stack:
            sys.stdout, sys.stderr = self._capture_stack.pop()

    def _getCapturedStdout(self):
        if self._currentStdout:
            value = self._currentStdout.getvalue()
            if value:
                return value
        return ''

    def _getCapturedStderr(self):
        if self._currentStderr:
            value = self._currentStderr.getvalue()
            if value:
                return value
        return ''

    def _addResult(self, test, status, queueing):
        test_path = get_test_path(test)

        logger.debug("Adding a test result: test: {}, context: {}, test_path: {}".format(test, test.context, test_path))
        result = CaseEvent(test_path, self._timeTaken(), status, self._getCapturedStdout(),
                           self._getCapturedStderr())
        queueing(result)

    # Bypass Capture plugin
    def _print(self, message):
        sys.__stdout__.write(message)

    def _timeTaken(self):
        if hasattr(self, '_timer'):
            return time() - self._timer

        # test died before it ran (probably error in setup())
        # or success/failure added before test started probably
        # due to custom TestResult munging
        return 0.0
