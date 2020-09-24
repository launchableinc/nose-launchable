import logging
import traceback

from nose.plugins import Plugin
from reorder.client import LaunchableClientFactory
from reorder.manager import parse_test, reorder

log = logging.getLogger("nose.plugins.reorder")


class Reorder(Plugin):
    name = "reorder"

    def options(self, parser, env):
        super(Reorder, self).options(parser, env=env)
        parser.add_option("--reorder", action='store_true', dest="reorder", help="Enable Launchable test reordering")

    def configure(self, options, conf):
        super(Reorder, self).configure(options, conf)
        self.enabled = options.reorder

    def prepareTest(self, test):
        try:
            t = parse_test(test)

            launchable_client = LaunchableClientFactory.prepare()
            order = launchable_client.infer(t)

            return reorder(test, order)
        except Exception as error:
            log.warning("An exception occurred while reordering. Executing tests in standard order: {}".format(error))
            log.warning(traceback.format_exc())
            return test
