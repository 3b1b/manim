from functools import reduce
import inspect
import operator as op


def instantiate(obj):
    """
    Useful so that classes or instance of those classes can be
    included in configuration, which can prevent defaults from
    getting created during compilation/importing
    """
    return obj() if isinstance(obj, type) else obj


def get_all_descendent_classes(Class):
    awaiting_review = [Class]
    result = []
    while awaiting_review:
        Child = awaiting_review.pop()
        awaiting_review += Child.__subclasses__()
        result.append(Child)
    return result


def filtered_locals(caller_locals):
    result = caller_locals.copy()
    ignored_local_args = ["self", "kwargs"]
    for arg in ignored_local_args:
        result.pop(arg, caller_locals)
    return result


def digest_config(obj, kwargs, caller_locals={}):
    """
    Sets init args and CONFIG values as local variables

    The purpose of this function is to ensure that all
    configuration of any object is inheritable, able to
    be easily passed into instantiation, and is attached
    as an attribute of the object.
    """

    # Assemble list of CONFIGs from all super classes
    classes_in_hierarchy = [obj.__class__]
    static_configs = []
    while len(classes_in_hierarchy) > 0:
        Class = classes_in_hierarchy.pop()
        classes_in_hierarchy += Class.__bases__
        if hasattr(Class, "CONFIG"):
            static_configs.append(Class.CONFIG)

    # Order matters a lot here, first dicts have higher priority
    caller_locals = filtered_locals(caller_locals)
    all_dicts = [kwargs, caller_locals, obj.__dict__]
    all_dicts += static_configs
    obj.__dict__ = merge_config(all_dicts)


def merge_config(all_dicts):
    """
    Creates a dict whose keyset is the union of all the
    input dictionaries.  The value for each key is based
    on the first dict in the list with that key.

    When values are dictionaries, it is applied recursively
    """
    all_config = reduce(op.add, [list(d.items()) for d in all_dicts])
    config = dict()
    for c in all_config:
        key, value = c
        if key not in config:
            config[key] = value
        else:
            # When two dictionaries have the same key, they are merged.
            if isinstance(value, dict) and isinstance(config[key], dict):
                config[key] = merge_config([config[key], value])
    return config


def soft_dict_update(d1, d2):
    """
    Adds key values pairs of d2 to d1 only when d1 doesn't
    already have that key
    """
    for key, value in list(d2.items()):
        if key not in d1:
            d1[key] = value


def digest_locals(obj, keys=None):
    caller_locals = filtered_locals(
        inspect.currentframe().f_back.f_locals
    )
    if keys is None:
        keys = list(caller_locals.keys())
    for key in keys:
        setattr(obj, key, caller_locals[key])

# Occasionally convenient in order to write dict.x instead of more laborious
# (and less in keeping with all other attr accesses) dict["x"]


class DictAsObject(object):
    def __init__(self, dict):
        self.__dict__ = dict
