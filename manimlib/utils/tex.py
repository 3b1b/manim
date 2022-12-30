from __future__ import annotations

import re

from manimlib.utils.tex_to_symbol_count import TEX_TO_SYMBOL_COUNT


def num_tex_symbols(tex: str) -> int:
    """
    This function attempts to estimate the number of symbols that
    a given string of tex would produce.

    Warning, it may not behave perfectly
    """
    # First, remove patterns like \begin{align}, \phantom{thing},
    # \begin{array}{cc}, etc.
    pattern = "|".join(
        rf"(\\{s})" + r"(\{\w+\})?(\{\w+\})?(\[\w+\])?"
        for s in ["begin", "end", "phantom"]
    )
    for tup in re.findall(pattern, tex):
        tex = tex.replace("".join(tup), " ")

    # Progressively count the symbols associated with certain tex commands,
    # and remove those commands from the string, adding the number of symbols
    # that command creates
    total = 0

    # Start with the special case \sqrt[number]
    for substr in re.findall(r"\\sqrt\[[0-9]+\]", tex):
        total += len(substr) - 5  # e.g. \sqrt[3] is 3 symbols
        tex = tex.replace(substr, " ")

    general_command = r"\\[a-zA-Z!,-/:;<>]+"
    for substr in re.findall(general_command, tex):
        total += TEX_TO_SYMBOL_COUNT.get(substr, 1)
        tex = tex.replace(substr, " ")

    # Count remaining characters
    total += sum(map(lambda c: c not in "^{} \n\t_$\\&", tex))
    return total
