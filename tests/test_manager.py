import unittest
from .resources.module0 import MockTestClass0
from .resources.module1 import MockTestClass1
from .resources.module2 import MockTestClass2

from nose.suite import ContextSuite
from nose_launchable.manager import get_test_names, subset


class TestManager(unittest.TestCase):
    def setUp(self):
        self.mock_suite1 = ContextSuite(tests=[ContextSuite(context=MockTestClass1), ContextSuite(context=MockTestClass2)])
        self.mock_suite0 = ContextSuite(tests=[ContextSuite(context=MockTestClass0), self.mock_suite1])

    def test_get_test_names(self):
        want = ['tests/resources/module0.py', 'tests/resources/module1.py', 'tests/resources/module2.py']

        got = get_test_names(self.mock_suite0)

        self.assertEqual(want, got)

    def test_get_test_names_empty(self):
        suite = ContextSuite()

        want = []
        got = get_test_names(suite)

        self.assertEqual(want, got)

    def test_subset_full(self):
        want = ['tests/resources/module2.py', 'tests/resources/module1.py', 'tests/resources/module0.py']

        subset(self.mock_suite0, {w: i for i, w in enumerate(want)})

        got = get_test_names(self.mock_suite0)
        self.assertEqual(want, got)

    def test_subset_partial(self):
        want = ['tests/resources/module2.py', 'tests/resources/module0.py']

        subset(self.mock_suite0, {w: i for i, w in enumerate(want)})

        got = get_test_names(self.mock_suite0)
        self.assertEqual(want, got)

    def test_subset_empty(self):
        want = []

        subset(self.mock_suite0, {w: i for i, w in enumerate(want)})

        got = get_test_names(self.mock_suite0)
        self.assertEqual(want, got)
