from __future__ import annotations

from functools import lru_cache
import hashlib
import inspect
import math

import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable, TypeVar
    from manimlib.typing import FloatArray

    Scalable = TypeVar("Scalable", float, FloatArray)



def sigmoid(x: float | FloatArray):
    return 1.0 / (1 + np.exp(-x))


@lru_cache(maxsize=10)
def choose(n: int, k: int) -> int:
    return math.comb(n, k)


def gen_choose(n: int, r: int) -> int:
    return int(np.prod(range(n, n - r, -1)) / math.factorial(r))


def get_num_args(function: Callable) -> int:
    return len(get_parameters(function))


def get_parameters(function: Callable) -> list:
    return list(inspect.signature(function).parameters.keys())

# Just to have a less heavyweight name for this extremely common operation
#
# We may wish to have more fine-grained control over division by zero behavior
# in the future (separate specifiable values for 0/0 and x/0 with x != 0),
# but for now, we just allow the option to handle indeterminate 0/0.


def clip(a: float, min_a: float, max_a: float) -> float:
    if a < min_a:
        return min_a
    elif a > max_a:
        return max_a
    return a


def fdiv(a: Scalable, b: Scalable, zero_over_zero_value: Scalable | None = None) -> Scalable:
    if zero_over_zero_value is not None:
        out = np.full_like(a, zero_over_zero_value)
        where = np.logical_or(a != 0, b != 0)
    else:
        out = None
        where = True

    return np.true_divide(a, b, out=out, where=where)


def binary_search(function: Callable[[float], float],
                  target: float,
                  lower_bound: float,
                  upper_bound: float,
                  tolerance:float = 1e-4) -> float | None:
    lh = lower_bound
    rh = upper_bound
    mh = (lh + rh) / 2
    while abs(rh - lh) > tolerance:
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
        mh = (lh + rh) / 2
    return mh


def hash_string(string: str) -> str:
    # Truncating at 16 bytes for cleanliness
    hasher = hashlib.sha256(string.encode())
    return hasher.hexdigest()[:16]
