from __future__ import annotations

import re
from functools import lru_cache

from manimlib.utils.tex_to_symbol_count import TEX_TO_SYMBOL_COUNT


@lru_cache
def num_tex_symbols(tex: str) -> int:
    tex = remove_tex_environments(tex)
    commands_pattern = r"""
        (?P<sqrt>\\sqrt\[[0-9]+\])|    # Special sqrt with number
        (?P<escaped_brace>\\[{}])|      # Escaped braces
        (?P<cmd>\\[a-zA-Z!,-/:;<>]+)    # Regular commands
    """
    total = 0
    pos = 0
    for match in re.finditer(commands_pattern, tex, re.VERBOSE):
        # Count normal characters up to this command
        total += sum(1 for c in tex[pos:match.start()] if c not in "^{} \n\t_$\\&")

        if match.group("sqrt"):
            total += len(match.group()) - 5
        elif match.group("escaped_brace"):
            total += 1  # Count escaped brace as one symbol
        else:
            total += TEX_TO_SYMBOL_COUNT.get(match.group(), 1)
        pos = match.end()

    # Count remaining characters
    total += sum(1 for c in tex[pos:] if c not in "^{} \n\t_$\\&")
    return total


def remove_tex_environments(tex: str) -> str:
    # Handle \phantom{...} with any content
    tex = re.sub(r"\\phantom\{[^}]*\}", "", tex)
    # Handle other environment commands
    tex = re.sub(r"\\(begin|end)(\{\w+\})?(\{\w+\})?(\[\w+\])?", "", tex)
    return tex
