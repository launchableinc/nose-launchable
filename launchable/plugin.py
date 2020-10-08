
import sys
import traceback

from nose.plugins import Plugin
from nose.plugins.capture import Capture

from launchable.client import LaunchableClientFactory
from launchable.manager import parse_test, reorder
from launchable.log import logger


class Launchable(Plugin):
    name = "launchable"
    # Grab stdout before the capture plugin
    score = Capture.score + 1

    def __init__(self):
        super().__init__()
        self._stdout = []

    def options(self, parser, env):
        super(Launchable, self).options(parser, env=env)
        parser.add_option("--launchable", action='store_true', dest="enabled", help="Enable Launchable API interaction")
        parser.add_option("--launchable-build-number", action='store', type='string', dest="build_number", help="CI/CD build number")

    def configure(self, options, conf):
        super(Launchable, self).configure(options, conf)
        self.enabled = options.enabled
        self.build_number = options.build_number

        if self.enabled and self.build_number is None:
            self.enabled = False
            logger.warning("--launchable flag is specified but --launchable-build-number flag is missing. "
                           "Please specify --launchable-build-number flag in order to enable nose-launchable plugin")

    def begin(self):
        self._stdout.append(sys.stdout)

    def prepareTest(self, test):
        try:
            t = parse_test(test)

            launchable_client = LaunchableClientFactory.prepare()
            self._print("Getting optimized test execution order from Launchable...")
            order = launchable_client.infer(t)
            self._print("Received optimized test execution order from Launchable")

            reorder(test, order)

            self._print("Test execution optimized by Launchable 🚀")
            return
        except Exception:
            logger.warning("An unexpected error occurred while optimizing test execution. "
                           "Please enable debugging by setting a `LAUNCHABLE_DEBUG=1` environment variable "
                           "and send the logs to Launchable team. "
                           "Test execution starts in standard order.")
            logger.warning(traceback.format_exc())
            return test

    # Bypass Capture plugin
    def _print(self, message):
        self._stdout[0].write(message + "\n")
