import logging
import os
import traceback

from nose.plugins import Plugin
from reorder.client import LaunchableClientFactory
from reorder.client import S3ClientFactory
from reorder.manager import get_test_names, reorder

log = logging.getLogger("nose.plugins.reorder")


class Reorder(Plugin):
    DIR_NAME = "LAUNCHABLE_REORDERING_DIR_NAME"

    name = "reorder"

    def options(self, parser, env):
        super(Reorder, self).options(parser, env=env)
        parser.add_option("--reorder", action='store_true', dest="reorder", help="Enable Launchable test reordering")

    def configure(self, options, conf):
        super(Reorder, self).configure(options, conf)
        self.enabled = options.reorder

    def prepareTest(self, test):
        try:
            s3_client = S3ClientFactory.prepare()
            template = s3_client.get_template(os.environ[self.DIR_NAME])

            names = get_test_names(test)

            launchable_client = LaunchableClientFactory.prepare()
            order = launchable_client.infer(names, template)

            return reorder(test, order)
        except Exception as error:
            log.warning("An exception occurred while reordering. Executing tests in standard order: {}".format(error))
            log.warning(traceback.format_exc())
            return test
