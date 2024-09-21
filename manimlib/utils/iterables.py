from __future__ import annotations

from colour import Color

import numpy as np
import random

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Iterable, Sequence, TypeVar

    T = TypeVar("T")
    S = TypeVar("S")


def remove_list_redundancies(lst: Sequence[T]) -> list[T]:
    """
    Remove duplicate elements while preserving order.
    Keeps the last occurrence of each element
    """
    return list(reversed(dict.fromkeys(reversed(lst))))


def list_update(l1: Iterable[T], l2: Iterable[T]) -> list[T]:
    """
    Used instead of list(set(l1).update(l2)) to maintain order,
    making sure duplicates are removed from l1, not l2.
    """
    return remove_list_redundancies([*l1, *l2])


def list_difference_update(l1: Iterable[T], l2: Iterable[T]) -> list[T]:
    return [e for e in l1 if e not in l2]


def adjacent_n_tuples(objects: Sequence[T], n: int) -> zip[tuple[T, ...]]:
    return zip(*[
        [*objects[k:], *objects[:k]]
        for k in range(n)
    ])


def adjacent_pairs(objects: Sequence[T]) -> zip[tuple[T, T]]:
    return adjacent_n_tuples(objects, 2)


def batch_by_property(
    items: Iterable[T],
    property_func: Callable[[T], S]
) -> list[tuple[T, S]]:
    """
    Takes in a list, and returns a list of tuples, (batch, prop)
    such that all items in a batch have the same output when
    put into property_func, and such that chaining all these
    batches together would give the original list (i.e. order is
    preserved)
    """
    batch_prop_pairs = []
    curr_batch = []
    curr_prop = None
    for item in items:
        prop = property_func(item)
        if prop != curr_prop:
            # Add current batch
            if len(curr_batch) > 0:
                batch_prop_pairs.append((curr_batch, curr_prop))
            # Redefine curr
            curr_prop = prop
            curr_batch = [item]
        else:
            curr_batch.append(item)
    if len(curr_batch) > 0:
        batch_prop_pairs.append((curr_batch, curr_prop))
    return batch_prop_pairs


def listify(obj: object) -> list:
    if isinstance(obj, str):
        return [obj]
    try:
        return list(obj)
    except TypeError:
        return [obj]


def shuffled(iterable: Iterable) -> list:
    as_list = list(iterable)
    random.shuffle(as_list)
    return as_list


def resize_array(nparray: np.ndarray, length: int) -> np.ndarray:
    if len(nparray) == length:
        return nparray
    return np.resize(nparray, (length, *nparray.shape[1:]))


def resize_preserving_order(nparray: np.ndarray, length: int) -> np.ndarray:
    if len(nparray) == 0:
        return np.resize(nparray, length)
    if len(nparray) == length:
        return nparray
    indices = np.arange(length) * len(nparray) // length
    return nparray[indices]


def resize_with_interpolation(nparray: np.ndarray, length: int) -> np.ndarray:
    if len(nparray) == length:
        return nparray
    if len(nparray) == 1 or array_is_constant(nparray):
        return nparray[:1].repeat(length, axis=0)
    if length == 0:
        return np.zeros((0, *nparray.shape[1:]))
    cont_indices = np.linspace(0, len(nparray) - 1, length)
    return np.array([
        (1 - a) * nparray[lh] + a * nparray[rh]
        for ci in cont_indices
        for lh, rh, a in [(int(ci), int(np.ceil(ci)), ci % 1)]
    ])


def make_even(
    iterable_1: Sequence[T],
    iterable_2: Sequence[S]
) -> tuple[Sequence[T], Sequence[S]]:
    len1 = len(iterable_1)
    len2 = len(iterable_2)
    if len1 == len2:
        return iterable_1, iterable_2
    new_len = max(len1, len2)
    return (
        [iterable_1[(n * len1) // new_len] for n in range(new_len)],
        [iterable_2[(n * len2) // new_len] for n in range(new_len)]
    )


def arrays_match(arr1: np.ndarray, arr2: np.ndarray) -> bool:
    return arr1.shape == arr2.shape and (arr1 == arr2).all()


def array_is_constant(arr: np.ndarray) -> bool:
    return len(arr) > 0 and (arr == arr[0]).all()


def cartesian_product(*arrays: np.ndarray):
    """
    Copied from https://stackoverflow.com/a/11146645
    """
    la = len(arrays)
    dtype = np.result_type(*arrays)
    arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
    for i, a in enumerate(np.ix_(*arrays)):
        arr[..., i] = a
    return arr.reshape(-1, la)


def hash_obj(obj: object) -> int:
    if isinstance(obj, dict):
        return hash(tuple(sorted([
            (hash_obj(k), hash_obj(v)) for k, v in obj.items()
        ])))

    if isinstance(obj, set):
        return hash(tuple(sorted(hash_obj(e) for e in obj)))

    if isinstance(obj, (tuple, list)):
        return hash(tuple(hash_obj(e) for e in obj))

    if isinstance(obj, Color):
        return hash(obj.get_rgb())

    return hash(obj)
