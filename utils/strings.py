import re
import string
import itertools as it


def to_camel_case(name):
    return "".join([
        filter(
            lambda c: c not in string.punctuation + string.whitespace, part
        ).capitalize()
        for part in name.split("_")
    ])


def initials(name, sep_values=[" ", "_"]):
    return "".join([
        (s[0] if s else "")
        for s in re.split("|".join(sep_values), name)
    ])


def camel_case_initials(name):
    return filter(lambda c: c.isupper(), name)


def complex_string(complex_num):
    return filter(lambda c: c not in "()", str(complex_num))


def break_up_string_by_terms(full_string, *terms):
    """
    Given a string, and an arbitrary number of possible substrings, returns a list
    of strings which would concatenate to make the full string, and in which
    these special substrings appear as their own elements.

    For example, break_up_string_by_terms("to be or not to be", "to", "be") would
    return ["to", " ", "be", " or not ", "to", " ", "be"]
    """
    if len(terms) == 0:
        return [full_string]
    term = terms[0]
    substrings = list(it.chain(*zip(
        full_string.split(term),
        it.repeat(term)
    )))
    substrings.pop(-1)
    substrings = filter(lambda s: s != "", substrings)
    return list(it.chain(*[
        break_up_string_by_terms(substring, *terms[1:])
        for substring in substrings
    ]))
