import numpy as np
import operator as op
from functools import reduce


def sigmoid(x):
    return 1.0 / (1 + np.exp(-x))


def choose(n, r):
    if n < r:
        return 0
    if r == 0:
        return 1
    denom = reduce(op.mul, xrange(1, r + 1))
    numer = reduce(op.mul, xrange(n, n - r, -1))
    return numer // denom

# Just to have a less heavyweight name for this extremely common operation
#
# We may wish to have more fine-grained control over division by zero behavior
# in the future (separate specifiable values for 0/0 and x/0 with x != 0),
# but for now, we just allow the option to handle indeterminate 0/0.


def fdiv(a, b, zero_over_zero_value=None):
    """

    :param a: np.array type
    :param b: np.array type
    :param zero_over_zero_value:
    :return:
    """
    # converting a and b to numpy array to avoid error
    a = np.array(a)
    b = np.array(b)

    if zero_over_zero_value is not None:
        out = np.full_like(a, zero_over_zero_value)
        where = np.logical_or(a != 0, b != 0)
    else:
        out = None
        where = True

    return np.true_divide(a, b, out=out, where=where)


if __name__ == '__main__':
    v = fdiv([1, 2, 0], [2, 1, 0], zero_over_zero_value=1)
    print v