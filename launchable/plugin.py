
import os
import sys
import traceback

from nose.plugins import Plugin
from nose.plugins.capture import Capture

from launchable.client import LaunchableClientFactory
from launchable.log import logger
from launchable.manager import parse_test, reorder


class Launchable(Plugin):
    name = "launchable"
    # Grab stdout before the capture plugin
    score = Capture.score + 1

    REPORT_ERROR_KEY = "LAUNCHABLE_REPORT_ERROR"

    def __init__(self):
        super().__init__()
        self._stdout = []

    def options(self, parser, env):
        super(Launchable, self).options(parser, env=env)
        parser.add_option("--launchable", action='store_true', dest="launchable", help="Enable Launchable API interaction")

    def configure(self, options, conf):
        super(Launchable, self).configure(options, conf)
        self.enabled = options.launchable

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
        except Exception as e:
            if os.getenv(self.REPORT_ERROR_KEY):
                raise e

            logger.warning("An unexpected error occurred while optimizing test execution. "
                           "Please enable debugging by setting a `LAUNCHABLE_DEBUG=1` environment variable "
                           "and send the logs to Launchable team. "
                           "Test execution starts in standard order.")
            logger.warning(traceback.format_exc())
            return test

    # Bypass Capture plugin
    def _print(self, message):
        self._stdout[0].write(message + "\n")
