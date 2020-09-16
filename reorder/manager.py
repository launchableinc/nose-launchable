from nose.case import Test


def get_test_names(test):
    names = []

    def dfs(case):
        if type(case) is Test:
            names.append(case.id())
            return case

        # Access to _tests is through a generator, so iteration is not repeatable
        case._tests = [dfs(t) for t in case]
        return case

    dfs(test)
    return names


def reorder(test, order):
    order_map = dict((t["testName"], i) for i, t in enumerate(order))

    def dfs(case):
        if type(case) is Test:
            return order_map[case.id()], case

        cases = []
        total_index = 0

        children = [dfs(t) for t in case]
        # TODO: Improve the reducing algorithm
        for i, c in sorted(children, key=lambda x: x[0]):
            cases.append(c)
            total_index += i

        case._tests = cases

        # Avoid dividing with zero when 'cases' are empty
        return total_index / max(1, len(cases)), case

    return dfs(test)[1]
