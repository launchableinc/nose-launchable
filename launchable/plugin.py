
import traceback

from nose.plugins import Plugin

from launchable.client import LaunchableClientFactory
from launchable.log import logger
from launchable.manager import parse_test, reorder


class Launchable(Plugin):
    name = "launchable"

    def options(self, parser, env):
        super(Launchable, self).options(parser, env=env)
        parser.add_option("--launchable", action='store_true', dest="launchable", help="Enable Launchable API interaction")

    def configure(self, options, conf):
        super(Launchable, self).configure(options, conf)
        self.enabled = options.launchable

    def prepareTest(self, test):
        try:
            t = parse_test(test)

            launchable_client = LaunchableClientFactory.prepare()
            order = launchable_client.infer(t)

            reorder(test, order)

            print("Launchable has successfully reordered tests")
            return
        except Exception as error:
            logger.warning("An exception occurred while reordering. Executing tests in standard order: {}".format(error))
            logger.warning(traceback.format_exc())
            return test
