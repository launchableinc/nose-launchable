import os
import traceback
from functools import wraps

from nose_launchable.log import logger

REPORT_ERROR_KEY = "LAUNCHABLE_REPORT_ERROR"


def protect(f):

    @wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            if os.getenv(REPORT_ERROR_KEY) is not None:
                raise e

            logger.warning('An unexpected error occurred while optimizing test execution. Please enable debugging by '
                           'setting a `LAUNCHABLE_DEBUG=1` environment variable and send the logs to Launchable team. '
                           'Test execution starts in standard order.')
            logger.warning(traceback.format_exc())

    return func
