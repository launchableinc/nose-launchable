import os
import unittest

from nose_launchable.protecter import REPORT_ERROR_KEY, protect


class TestProtector(unittest.TestCase):
    def test_protect(self):
        @protect
        def error_func():
            raise Exception

        error_func()

    def test_protect_report_error(self):
        @protect
        def error_func():
            raise Exception

        current_config = os.getenv(REPORT_ERROR_KEY, "")
        os.environ[REPORT_ERROR_KEY] = '1'
        with self.assertRaises(Exception):
            error_func()

        if current_config:
            os.environ[REPORT_ERROR_KEY] = current_config
        else:
            os.environ.pop(REPORT_ERROR_KEY, None)
