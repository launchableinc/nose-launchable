import os
import unittest

from nose_launchable.protecter import protect


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

        os.environ["LAUNCHABLE_REPORT_ERROR"] = '1'
        with self.assertRaises(Exception):
            error_func()
