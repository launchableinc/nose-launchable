import os
from types import ModuleType

from nose.failure import Failure
from nose.plugins.xunit import id_split
from nose.suite import ContextSuite
from nose.util import test_address

from nose_launchable.log import logger
from nose_launchable.test_path_component import TestPathComponent



# Parse tests and return a list of test names
def get_test_names(test):
    test_names = []

    def dfs(suite):
        logger.debug("Parsing a test tree: suite: {}".format(suite))
        if _is_leaf(suite):
            test_names.append(_get_test_name(suite))
            return suite

        # Access to _tests is through a generator, so iteration is not repeatable by default
        suite._tests = [dfs(t) for t in suite]
        return suite

    dfs(test)
    return test_names

# Subset tests based on the given order
def subset(test, order):
    def dfs(suite):
        logger.debug("Subsetting a test tree: suite: {}".format(suite))
        if _is_leaf(suite):
            name = _get_test_name(suite)

            score, is_target = 0, name in order
            if is_target:
                score = order[name]

            logger.debug("A leaf node: score: {}, is_target: {}, suite: {}".format(score, is_target, suite))
            return score, is_target, suite

        cases = []
        score = 0

        for t in suite:
            s, is_target, c = dfs(t)

            if not is_target:
                continue

            cases.append((s, c))
            score += s

        # The smaller the score is, the faster the test needs to be tested
        suite._tests = [c for _, c in sorted(cases, key=lambda x: x[0])]

        # Propagate a score to its parent by calculating its average
        # Avoid ZeroDivisionError with max(len(cases), 1)
        s, is_target = score / max(len(cases), 1), len(cases) != 0
        logger.debug("A non-leaf node: score: {}, is_target: {}, suite: {}".format(s, is_target, suite))
        return s, is_target, suite

    dfs(test)
    return test


# Check if test's context is a leaf
def _is_leaf(suite):
    if type(suite) is ContextSuite:
        context = suite.context

        # Fails to load a test
        is_failure = context is Failure

        # If __file__ ends with __init__.py, the context is a package so we need to dig further
        is_file = isinstance(context, ModuleType) and not context.__file__.endswith('__init__.py')

        # a leaf context can be a class if specifying a class directly: module:TestClass
        is_class = type(context) is type

        return is_failure or is_file or is_class

    return False


# Extract a test name from a leaf
def _get_test_name(suite):
    if not _is_leaf(suite):
        raise RuntimeError("_get_test_name method should run only against a leaf. suite: {}".format(suite))

    if suite.context is Failure:
        return "failure"

    file_path, _, _ = test_address(suite.context)
    return os.path.relpath(file_path)


# Return testPath like [{"type": "file", "name": "file_path"}, {"type": "testcase", "name": "function_name"}]
def get_test_path(test):
    test_path = []

    file_path, _, _ = test_address(test.test)
    test_path.append(TestPathComponent(TestPathComponent.FILE_TYPE, os.path.relpath(file_path)))

    head, tail = id_split(test.test.id())

    # If the test context is a class, we need a class name too to uniquely identify each test in the module
    is_class_test = type(test.context) is type
    if is_class_test:
        test_path.append(TestPathComponent(TestPathComponent.CLASS_TYPE, head.rsplit(".", 1)[-1]))

    test_path.append(TestPathComponent(TestPathComponent.CASE_TYPE, tail))

    return test_path
