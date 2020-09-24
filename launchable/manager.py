from nose.case import Test

TREE_TYPE = "tree"
TREE_NODE_TYPE = "treeNode"
TEST_CASE_NODE_TYPE = "testCaseNode"


def parse_test(test):
    def dfs(case):
        if type(case) is Test:
            return case, {"type": TEST_CASE_NODE_TYPE, "testName": case.id()}

        cases = []
        nodes = []

        for t in case:
            c, n = dfs(t)

            cases.append(c)
            nodes.append(n)

        # Access to _tests is through a generator, so iteration is not repeatable by default
        case._tests = cases
        return case, {"type": TREE_NODE_TYPE, "id": str(id(case)), "children": nodes}

    _, node = dfs(test)
    return {"type": TREE_TYPE, "root": node}


def reorder(test, order):
    if len(order) == 0:
        return

    node_type = order["type"]

    if node_type == TREE_TYPE:
        reorder(test, order["root"])
        return

    if node_type == TEST_CASE_NODE_TYPE:
        return

    if node_type == TREE_NODE_TYPE:
        for t, o in _reorder(test, order):
            reorder(t, o)
        return

    raise RuntimeError("Unexpected object type: {}".format(node_type))


def _reorder(test, order):
    test_case_node_map = {}
    tree_node_map = {}

    for t in test:
        if type(t) is Test:
            test_case_node_map[t.id()] = t
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

    test._tests = tests

    return tree_nodes
