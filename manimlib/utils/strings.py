import itertools as it
import re
import string


def to_camel_case(name):
    return "".join([
        [c for c in part if c not in string.punctuation + string.whitespace].capitalize()
        for part in name.split("_")
    ])


def initials(name, sep_values=[" ", "_"]):
    return "".join([
        (s[0] if s else "")
        for s in re.split("|".join(sep_values), name)
    ])


def camel_case_initials(name):
    return [c for c in name if c.isupper()]


def complex_string(complex_num):
    return [c for c in str(complex_num) if c not in "()"]


def split_string_to_isolate_substrings(full_string, *substrings_to_isolate):
    """
    Given a string, and an arbitrary number of possible substrings, returns a list
    of strings which would concatenate to make the full string, and in which
    these special substrings appear as their own elements.

    For example, split_string_to_isolate_substrings("to be or not to be", "to", "be") would
    return ["to", " ", "be", " or not ", "to", " ", "be"]
    """
    if len(substrings_to_isolate) == 0:
        return [full_string]
    substring_to_isolate = substrings_to_isolate[0]
    all_substrings = list(it.chain(*list(zip(
        full_string.split(substring_to_isolate),
        it.repeat(substring_to_isolate)
    ))))
    all_substrings.pop(-1)
    all_substrings = [s for s in all_substrings if s != ""]
    return split_string_list_to_isolate_substrings(
        all_substrings, *substrings_to_isolate[1:]
    )


def split_string_list_to_isolate_substrings(string_list, *substrings_to_isolate):
    """
    Similar to split_string_to_isolate_substrings, but the first argument
    is a list of strings, thought of as something already broken up a bit.
    """
    return list(it.chain(*[
        split_string_to_isolate_substrings(s, *substrings_to_isolate)
        for s in string_list
    ]))
