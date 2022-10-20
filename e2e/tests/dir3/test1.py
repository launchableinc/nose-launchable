from nose.plugins.skip import SkipTest


def test_evens():
    for i in range(0, 3):
        yield check_true, i, i


def test_evens_but_skip():
    for i in range(4, 6):
        yield check_skip, i, i+1


def check_true(n, nn):
    assert n == nn


def check_skip(n, nn):
    raise SkipTest("this is skip test n={} nn={}".format(n, nn))
    assert n == nn
