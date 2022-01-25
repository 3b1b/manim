import inspect
import numpy as np
import math


def sigmoid(x):
    return 1.0 / (1 + np.exp(-x))


def choose(n, r):
    return math.comb(n, r)


def gen_choose(n, r):
    return np.prod(np.arange(n, n - r, -1)) / math.factorial(r)


def get_num_args(function):
    return len(get_parameters(function))


def get_parameters(function):
    return inspect.signature(function).parameters

# Just to have a less heavyweight name for this extremely common operation
#
# We may wish to have more fine-grained control over division by zero behavior
# in the future (separate specifiable values for 0/0 and x/0 with x != 0),
# but for now, we just allow the option to handle indeterminate 0/0.


def clip(a, min_a, max_a):
    if a < min_a:
        return min_a
    elif a > max_a:
        return max_a
    return a


def clip_in_place(array, min_val=None, max_val=None):
    if max_val is not None:
        array[array > max_val] = max_val
    if min_val is not None:
        array[array < min_val] = min_val
    return array


def fdiv(a, b, zero_over_zero_value=None):
    if zero_over_zero_value is not None:
        out = np.full_like(a, zero_over_zero_value)
        where = np.logical_or(a != 0, b != 0)
    else:
        out = None
        where = True

    return np.true_divide(a, b, out=out, where=where)


def binary_search(function,
                  target,
                  lower_bound,
                  upper_bound,
                  tolerance=1e-4):
    lh = lower_bound
    rh = upper_bound
    while abs(rh - lh) > tolerance:
        mh = np.mean([lh, rh])
        lx, mx, rx = [function(h) for h in (lh, mh, rh)]
        if lx == target:
            return lx
        if rx == target:
            return rx

        if lx <= target and rx >= target:
            if mx > target:
                rh = mh
            else:
                lh = mh
        elif lx > target and rx < target:
            lh, rh = rh, lh
        else:
            return None
    return mh
