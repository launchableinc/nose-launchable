from logging import getLogger, DEBUG
import os

LAUNCHABLE_DEBUG_KEY = "LAUNCHABLE_DEBUG"

logger = getLogger("nose.plugins.launchable")
if os.getenv(LAUNCHABLE_DEBUG_KEY):
    logger.setLevel(DEBUG)


