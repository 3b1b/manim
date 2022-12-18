import itertools as it


def merge_dicts_recursively(*dicts):
    """
    Creates a dict whose keyset is the union of all the
    input dictionaries.  The value for each key is based
    on the first dict in the list with that key.

    dicts later in the list have higher priority

    When values are dictionaries, it is applied recursively
    """
    result = dict()
    all_items = it.chain(*[d.items() for d in dicts])
    for key, value in all_items:
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts_recursively(result[key], value)
        else:
            result[key] = value
    return result


def soft_dict_update(d1, d2):
    """
    Adds key values pairs of d2 to d1 only when d1 doesn't
    already have that key
    """
    for key, value in list(d2.items()):
        if key not in d1:
            d1[key] = value
