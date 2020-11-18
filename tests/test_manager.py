import unittest
from tests.resources.module0 import MockTestClass0
from tests.resources.module1 import MockTestClass1
from tests.resources.module2 import MockTestClass2

from nose.suite import ContextSuite
from launchable.manager import parse_test, reorder


class TestManager(unittest.TestCase):
    def setUp(self):
        self.mock_suite1 = ContextSuite(tests=[ContextSuite(context=MockTestClass1), ContextSuite(context=MockTestClass2)])
        self.mock_suite0 = ContextSuite(tests=[ContextSuite(context=MockTestClass0), self.mock_suite1])

    def test_parse_test(self):
        want = {
            'type': 'tree',
            'root':
                {
                    'type': 'treeNode',
                    'id': str(id(self.mock_suite0)),
                    'children':
                        [
                            {'type': 'testCaseNode', 'testName': 'tests/resources/module0.py'},
                            {
                                'type': 'treeNode',
                                'id': str(id(self.mock_suite1)),
                                'children':
                                    [
                                        {'type': 'testCaseNode', 'testName': 'tests/resources/module1.py'},
                                        {'type': 'testCaseNode', 'testName': 'tests/resources/module2.py'}
                                    ],
                            }
                        ],
                },
        }

        got = parse_test(self.mock_suite0)

        self.assertEqual(want, got)

    def test_get_test_names_empty(self):
        suite = ContextSuite()

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
                            {'type': 'testCaseNode', 'testName': 'tests/resources/module0.py'},
                            {
                                'type': 'treeNode',
                                'id': str(id(self.mock_suite1)),
                                'children':
                                    [
                                        {'type': 'testCaseNode', 'testName': 'tests/resources/module1.py'},
                                        {'type': 'testCaseNode', 'testName': 'tests/resources/module2.py'}
                                    ],
                            }
                        ],
                },
        }

        reorder(self.mock_suite0, want)

        got = parse_test(self.mock_suite0)
        self.assertEqual(want, got)

    def test_reorder_empty(self):
        test = ContextSuite()

        reorder(test, {'type': 'tree', 'root': {}})

        want = {'type': 'tree', 'root': {'type': 'treeNode', 'id': str(id(test)), 'children': []}}
        got = parse_test(test)

        self.assertEqual(want, got)

    def test_reorder_unexpected_type(self):
        test = ContextSuite()

        with self.assertRaises(RuntimeError):
            reorder(test, {'type': 'graph', 'root': {}})
