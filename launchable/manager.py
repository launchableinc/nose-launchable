import os
from types import ModuleType

from nose.failure import Failure
from nose.suite import ContextSuite
from nose.util import test_address

from launchable.log import logger

TREE_TYPE = "tree"
TREE_NODE_TYPE = "treeNode"
TEST_CASE_NODE_TYPE = "testCaseNode"


# Parse tests and create a test tree
def parse_test(test):
    def dfs(suite):
        logger.debug("Parsing a test tree: suite: {}".format(suite))
        if _is_leaf(suite):
            return suite, {"type": TEST_CASE_NODE_TYPE, "testName": _get_test_name(suite)}

        cases = []
        nodes = []

        for t in suite:
            c, n = dfs(t)

            cases.append(c)
            nodes.append(n)

        # Access to _tests is through a generator, so iteration is not repeatable by default
        suite._tests = cases
        return suite, {"type": TREE_NODE_TYPE, "id": str(id(suite)), "children": nodes}

    _, node = dfs(test)
    return {"type": TREE_TYPE, "root": node}


# Reorder tests based on the given order
def reorder(suite, order):
    if len(order) == 0:
        return

    node_type = order["type"]

    if node_type == TREE_TYPE:
        reorder(suite, order["root"])
        return

    if node_type == TEST_CASE_NODE_TYPE:
        return

    if node_type == TREE_NODE_TYPE:
        for t, o in _reorder(suite, order):
            reorder(t, o)
        return

    raise RuntimeError("Unexpected object type: {}".format(node_type))


def _reorder(suite, order):
    test_case_node_map = {}
    tree_node_map = {}

    for t in suite:
        if _is_leaf(t):
            test_case_node_map[_get_test_name(t)] = t
        else:
            tree_node_map[str(id(t))] = t

    tests = []
    tree_nodes = []
    for child in order["children"]:
        if child["type"] == TEST_CASE_NODE_TYPE:
            tests.append(test_case_node_map[child["testName"]])
        else:
            node = tree_node_map[child["id"]]
            tests.append(node)
            tree_nodes.append((node, child))

    suite._tests = tests

    return tree_nodes


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
