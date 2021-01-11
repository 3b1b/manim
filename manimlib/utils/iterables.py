import itertools as it
import numpy as np


def remove_list_redundancies(l):
    """
    Used instead of list(set(l)) to maintain order
    Keeps the last occurance of each element
    """
    reversed_result = []
    used = set()
    for x in reversed(l):
        if x not in used:
            reversed_result.append(x)
            used.add(x)
    reversed_result.reverse()
    return reversed_result


def list_update(l1, l2):
    """
    Used instead of list(set(l1).update(l2)) to maintain order,
    making sure duplicates are removed from l1, not l2.
    """
    return [e for e in l1 if e not in l2] + list(l2)


def list_difference_update(l1, l2):
    return [e for e in l1 if e not in l2]


def all_elements_are_instances(iterable, Class):
    return all([isinstance(e, Class) for e in iterable])


def adjacent_n_tuples(objects, n):
    return zip(*[
        [*objects[k:], *objects[:k]]
        for k in range(n)
    ])


def adjacent_pairs(objects):
    return adjacent_n_tuples(objects, 2)


def batch_by_property(items, property_func):
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


def listify(obj):
    if isinstance(obj, str):
        return [obj]
    try:
        return list(obj)
    except TypeError:
        return [obj]


def resize_array(nparray, length):
    return np.resize(nparray, (length, *nparray.shape[1:]))


def resize_preserving_order(nparray, length):
    if len(nparray) == 0:
        return np.zeros((length, *nparray.shape[1:]))
    if len(nparray) == length:
        return nparray
    indices = np.arange(length) * len(nparray) // length
    return nparray[indices]


def resize_with_interpolation(nparray, length):
    if len(nparray) == length:
        return nparray
    cont_indices = np.linspace(0, len(nparray) - 1, length)
    return np.array([
        (1 - a) * nparray[lh] + a * nparray[rh]
        for ci in cont_indices
        for lh, rh, a in [(int(ci), int(np.ceil(ci)), ci % 1)]
    ])


def make_even(iterable_1, iterable_2):
    list_1 = list(iterable_1)
    list_2 = list(iterable_2)
    length = max(len(list_1), len(list_2))
    return (
        [list_1[(n * len(list_1)) // length] for n in range(length)],
        [list_2[(n * len(list_2)) // length] for n in range(length)]
    )


def make_even_by_cycling(iterable_1, iterable_2):
    length = max(len(iterable_1), len(iterable_2))
    cycle1 = it.cycle(iterable_1)
    cycle2 = it.cycle(iterable_2)
    return (
        [next(cycle1) for x in range(length)],
        [next(cycle2) for x in range(length)]
    )


def remove_nones(sequence):
    return [x for x in sequence if x]


# Note this is redundant with it.chain


def concatenate_lists(*list_of_lists):
    return [item for l in list_of_lists for item in l]
