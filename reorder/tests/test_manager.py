import unittest
from unittest.mock import MagicMock

from nose.case import Test
from reorder.manager import get_test_names, reorder


class TestManager(unittest.TestCase):
    def setUp(self):
        mock_test0 = MagicMock(name="test0")
        mock_test0.id.return_value = "TestClass0.TestName0"

        mock_test1 = MagicMock(name="test1")
        mock_test1.id.return_value = "TestClass1.TestName1"

        mock_test2 = MagicMock(name="test2")
        mock_test2.id.return_value = "TestClass2.TestName2"

        mock_test_second = MagicMock(name="second")
        mock_test_second._tests = [Test(mock_test1), Test(mock_test2)]

        mock_test_root = MagicMock(name="root")
        mock_test_root._tests = [Test(mock_test0), mock_test_second]

        self.mock_test = mock_test_root

    def test_get_test_names(self):
        want = [
            {"className": 'TestClass0', "name": 'TestName0'},
            {"className": 'TestClass1', "name": 'TestName1'},
            {"className": 'TestClass2', "name": 'TestName2'}
        ]
        got = get_test_names(self.mock_test)

        self.assertEqual(want, got)

    def test_get_test_names_empty(self):
        test = MagicMock(name="test")
        test._tests = []

        want = []
        got = get_test_names(test)

        self.assertEqual(want, got)

    def test_reorder(self):
        test = MagicMock(name="test")
        test._tests = []

        ordered = reorder(test, [])

        want = []
        got = get_test_names(ordered)

        self.assertEqual(want, got)
