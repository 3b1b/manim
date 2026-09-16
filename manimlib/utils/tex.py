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


# Fraction commands which draw a rule between their two arguments. LaTeX ships that
# rule out after the numerator, not where the command itself sits in the source, so
# these are the commands whose glyph order does not follow their source order. The
# infix \over needs no entry: it already sits where its rule is drawn.
FRACTION_COMMANDS = (R"\frac", R"\dfrac", R"\tfrac", R"\cfrac")


def _iter_tex_tokens(tex: str) -> list[re.Match]:
    # A command, an escaped character, or a single character. Matching "\\" as one
    # token keeps the "frac" in "\\frac" (a line break followed by literal text)
    # from reading as a fraction command.
    return list(re.finditer(r"\\[a-zA-Z]+|\\.|.", tex, re.S))


def get_fraction_rule_positions(tex: str) -> list[tuple[int, int]]:
    """
    For every fraction command in `tex`, where the command sits and where its
    numerator ends.

    The second index is the position the fraction's rule is drawn at, since TeX
    ships a fraction out as numerator, then rule, then denominator.
    """
    tokens = _iter_tex_tokens(tex)
    result = []
    for i, token in enumerate(tokens):
        if token.group() not in FRACTION_COMMANDS:
            continue
        j = i + 1
        while j < len(tokens) and tokens[j].group().isspace():
            j += 1
        if j >= len(tokens):
            continue
        if tokens[j].group() == "{":
            # Walk to the brace which closes the numerator
            depth = 0
            while j < len(tokens):
                group = tokens[j].group()
                if group == "{":
                    depth += 1
                elif group == "}":
                    depth -= 1
                    if depth == 0:
                        j += 1
                        break
                j += 1
            if depth != 0:
                continue
        else:
            # An unbraced numerator, as in \frac12, is a single token
            j += 1
        result.append((token.start(), tokens[j - 1].end()))
    return result


def num_pending_fraction_rules(tex: str, index: int) -> int:
    """
    How many fraction rules `tex[:index]` names but has not yet drawn.

    A \\frac before `index` whose numerator is still open at `index` has not drawn
    its rule there, even though the command precedes that point in the source. The
    rule is drawn at the numerator's end, so an `index` which has reached that point
    is past the rule, as the denominator of an unbraced \\frac12 is.
    """
    return sum(
        1
        for command_start, rule_position in get_fraction_rule_positions(tex)
        if command_start < index < rule_position
    )


def remove_tex_environments(tex: str) -> str:
    # Handle \phantom{...} with any content
    tex = re.sub(r"\\phantom\{[^}]*\}", "", tex)
    # Handle other environment commands
    tex = re.sub(r"\\(begin|end)(\{\w+\})?(\{\w+\})?(\[\w+\])?", "", tex)
    return tex
