import unittest
from unittest.mock import MagicMock

from nose.case import Test
from reorder.manager import get_test_names, reorder


class MockSuite:
    def __init__(self, tests):
        self._tests = tests

    def __iter__(self):
        return iter(self._tests)


class TestManager(unittest.TestCase):
    def setUp(self):
        mock_test0 = MagicMock(name="test0")
        mock_test0.id.return_value = "TestClass0.TestName0"

        mock_test1 = MagicMock(name="test1")
        mock_test1.id.return_value = "TestClass1.TestName1"

        mock_test2 = MagicMock(name="test2")
        mock_test2.id.return_value = "TestClass2.TestName2"

        self.mock_test = MockSuite([Test(mock_test0), MockSuite([Test(mock_test1), Test(mock_test2)])])

    def test_get_test_names(self):
        want = ['TestClass0.TestName0', 'TestClass1.TestName1', 'TestClass2.TestName2']
        got = get_test_names(self.mock_test)

        self.assertEqual(want, got)

    def test_get_test_names_empty(self):
        test = MockSuite([])

        want = []
        got = get_test_names(test)

        self.assertEqual(want, got)

    def test_reorder(self):
        order = [
            {"testName": "TestClass2.TestName2"},
            {"testName": "TestClass1.TestName1"},
            {"testName": "TestClass0.TestName0"}
        ]
        ordered = reorder(self.mock_test, order)

        want = ['TestClass2.TestName2', 'TestClass1.TestName1', 'TestClass0.TestName0']
        got = get_test_names(ordered)

        self.assertEqual(want, got)

    def test_reorder_empty(self):
        test = MockSuite([])

        ordered = reorder(test, [])

        want = []
        got = get_test_names(ordered)

        self.assertEqual(want, got)
