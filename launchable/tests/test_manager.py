import unittest
from unittest.mock import MagicMock

from nose.case import Test

from launchable.manager import parse_test, reorder


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

        self.mock_suite1 = MockSuite([Test(mock_test1), Test(mock_test2)])
        self.mock_suite0 = MockSuite([Test(mock_test0), self.mock_suite1])

    def test_parse_test(self):
        want = {
            'type': 'tree',
            'root':
                {
                    'type': 'treeNode',
                    'id': str(id(self.mock_suite0)),
                    'children':
                        [
                            {'type': 'testCaseNode', 'testName': 'TestClass0.TestName0'},
                            {
                                'type': 'treeNode',
                                'id': str(id(self.mock_suite1)),
                                'children':
                                    [
                                        {'type': 'testCaseNode', 'testName': 'TestClass1.TestName1'},
                                        {'type': 'testCaseNode', 'testName': 'TestClass2.TestName2'}
                                    ],
                            }
                        ],
                },
        }

        got = parse_test(self.mock_suite0)

        self.assertEqual(want, got)

    def test_get_test_names_empty(self):
        suite = MockSuite([])

        want = {'type': 'tree', 'root': {'type': 'treeNode', 'id': str(id(suite)), 'children': []}}
        got = parse_test(suite)

        self.assertEqual(want, got)

    def test_reorder(self):
        want = {
            'type': 'tree',
            'root':
                {
                    'type': 'treeNode',
                    'id': str(id(self.mock_suite0)),
                    'children':
                        [
                            {
                                'type': 'treeNode',
                                'id': str(id(self.mock_suite1)),
                                'children':
                                    [
                                        {'type': 'testCaseNode', 'testName': 'TestClass2.TestName2'},
                                        {'type': 'testCaseNode', 'testName': 'TestClass1.TestName1'},
                                    ],
                            },
                            {'type': 'testCaseNode', 'testName': 'TestClass0.TestName0'},
                        ],
                },
        }

        reorder(self.mock_suite0, want)

        got = parse_test(self.mock_suite0)
        self.assertEqual(want, got)

    def test_reorder_empty(self):
        test = MockSuite([])

        reorder(test, {'type': 'tree', 'root': {}})

        want = {'type': 'tree', 'root': {'type': 'treeNode', 'id': str(id(test)), 'children': []}}
        got = parse_test(test)

        self.assertEqual(want, got)

    def test_reorder_unexpected_type(self):
        test = MockSuite([])

        with self.assertRaises(RuntimeError):
            reorder(test, {'type': 'graph', 'root': {}})
