"""
That selecting a substring of a Tex picks the glyph which draws it.

Tex.select_parts falls back to counting glyphs when a substring was not isolated: it
counts how many glyphs the source before the substring draws, and slices there. That
count assumes glyphs are drawn in source order, which a \\frac breaks. TeX ships a
fraction out as numerator, then rule, then denominator, so the rule is drawn after the
numerator even though \\frac is written before it. Counting \\frac where it is written
puts every glyph of the numerator one place late, and Tex(R"\\frac{1}{2}") colours its
rule when asked for its "1" (issue #2367).

This checks the mapping rather than a picture, so it needs no latex and no gpu. It is
the mapping that was wrong; the picture only showed it.

    python tests/tex_frac_indices.py
"""
from __future__ import annotations

import sys

from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.utils.tex import num_tex_symbols


# Each case is a tex string and, for substrings of it, the glyph the substring should
# land on. Indices are into the glyphs as drawn, counting from zero.
CASES = [
    # The report's case. Drawn as "1", rule, "2", so the numerator is glyph 0 and
    # counting \frac where it is written would say 1, which is the rule.
    (R"\frac{1}{2}", {"1": 0, "2": 2}),
    # Spaces inside the arguments draw nothing and must not shift anything
    (R"\frac{ 1 }{ 2 }", {"1": 0, "2": 2}),
    # Drawn as "1", inner rule, "2", outer rule, "3"
    (R"\frac{\frac{1}{2}}{3}", {"1": 0, "2": 2, "3": 4}),
    # A denominator holding the fraction instead: "1", outer rule, "2", inner rule, "3"
    (R"\frac{1}{\frac{2}{3}}", {"1": 0, "2": 2, "3": 4}),
    # Two fractions, so the count has to stay right across a finished one. Drawn as
    # "1", rule, "2", "+", "3", rule, "4"
    (R"\frac{1}{2} + \frac{3}{4}", {"2": 2, "+": 3, "3": 4, "4": 6}),
    # An unbraced numerator is a single token
    (R"\frac12", {"1": 0, "2": 2}),
    # Either side of a fraction, and so unaffected by it. The letters avoid those of
    # "frac", so that looking a substring up finds the glyph and not the command name.
    (R"p + \frac{q}{w} + z", {"p": 0, "+": 1, "q": 2, "w": 4, "z": 6}),
    # The infix form already sits where its rule is drawn, and should stay right
    (R"{1 \over 2}", {"1": 0, "2": 2}),
    # Nothing to reorder at all
    (R"x + y", {"x": 0, "+": 1, "y": 2}),
]


def make_tex(tex: str) -> Tex:
    """
    A Tex which was never rendered, carrying only what the glyph counting reads.

    Building one for real wants latex, and none of latex's output is under test here.
    """
    mob = object.__new__(Tex)
    mob.string = tex
    mob.tex_string = tex
    # substr_to_path_count warns unless the glyph count agrees with the string
    mob.submobjects = [None] * num_tex_symbols(tex)
    return mob


def main() -> int:
    failures = []
    for tex, expected in CASES:
        mob = make_tex(tex)
        for substr, glyph_index in expected.items():
            index = tex.index(substr)
            found = mob.count_paths_before_index(index)
            if found != glyph_index:
                failures.append(
                    f"{tex}: {substr!r} should be drawn by glyph {glyph_index}, "
                    f"counting found {found}"
                )

    for line in failures:
        print(f"FAIL {line}")
    cases = sum(len(expected) for _, expected in CASES)
    if failures:
        print(f"\n{len(failures)} of {cases} substrings land on the wrong glyph")
        return 1
    print(f"PASS all {cases} substrings across {len(CASES)} strings land on their glyph")
    return 0


if __name__ == "__main__":
    sys.exit(main())
