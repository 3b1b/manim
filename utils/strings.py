import re
import string


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
