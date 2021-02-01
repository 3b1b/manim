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


def split_string_to_isolate_substrings(full_string, *isolate):
    """
    Given a string, and an arbitrary number of possible substrings,
    to isolate, this returns a list of strings which would concatenate
    to make the full string, and in which these special substrings
    appear as their own elements.

    For example,split_string_to_isolate_substrings("to be or not to be", "to", "be")
    would return ["to", " ", "be", " or not ", "to", " ", "be"]
    """
    pattern = "|".join(*(
        "({})".format(re.escape(ss))
        for ss in isolate
    ))
    pieces = re.split(pattern, full_string)
    return list(filter(lambda s: s, pieces))
