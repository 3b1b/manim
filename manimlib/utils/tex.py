from __future__ import annotations

import re
from functools import lru_cache

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Tuple


@lru_cache(maxsize=1)
def get_pattern_symbol_count_pairs() -> List[Tuple[str, int]]:
    from manimlib.utils.tex_to_symbol_count import TEX_TO_SYMBOL_COUNT

    # Gather all keys of previous map, grouped by common value
    count_to_tex_list = dict()
    for command, num in TEX_TO_SYMBOL_COUNT.items():
        if num not in count_to_tex_list:
            count_to_tex_list[num] = []
        count_to_tex_list[num].append(command)

    # Create a list associating each count with a regular expression
    # that will find any tex commands matching that list
    pattern_symbol_count_pairs = list()

    # Account for patterns like \begin{align} and \phantom{thing}
    # which, together with the bracketed content account for zero paths.
    # Deliberately put this first in the list
    tex_list = ["begin", "end", "phantom"]
    pattern_symbol_count_pairs.append(
        ("|".join(r"\\" + s + r"\{[^\\}]+\}" for s in tex_list), 0)
    )

    for count, tex_list in count_to_tex_list.items():
        pattern = "|".join(r"\\" + s + r"(\s|\\)" + s for s in tex_list)
        pattern_symbol_count_pairs.append((pattern, count))

    # Assume all other expressions of the form \thing are drawn with one path
    # Deliberately put this last in the list
    pattern_symbol_count_pairs.append((r"\\[a-zA-Z]+", 1))

    return pattern_symbol_count_pairs


def num_tex_symbols(tex: str) -> int:
    """
    This function attempts to estimate the number of symbols that
    a given string of tex would produce.
    """
    total = 0
    for pattern, count in get_pattern_symbol_count_pairs():
        total += count * len(re.findall(pattern, tex))
        tex = re.sub(pattern, " ", tex)  # Remove that pattern

    # Count remaining characters
    total += sum(map(lambda c: c not in "^{} \n\t_$", tex))
    return total
