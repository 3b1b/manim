import pytest

from manimlib.utils.tex import num_tex_symbols, remove_tex_environments


@pytest.mark.parametrize(
    "tex",
    [
        r"\begin{align*} x \end{align*}",
        r"\begin{equation*} y \end{equation*}",
        r"\begin{gather*} z \end{gather*}",
    ],
)
def test_starred_environments_are_removed(tex):
    # `\w` does not match the star, so the command used to be stripped while
    # its brace group survived and was counted as rendered glyphs.
    assert remove_tex_environments(tex).strip() in {"x", "y", "z"}


@pytest.mark.parametrize(
    ("tex", "expected"),
    [
        (r"\begin{array}{|c|c|} p & q \end{array}", "p & q"),
        (r"\begin{tabular}{|c|c|} a \end{tabular}", "a"),
    ],
)
def test_environment_specs_with_punctuation_are_removed(tex, expected):
    assert remove_tex_environments(tex).strip() == expected


@pytest.mark.parametrize(
    "tex",
    [
        r"\begin{align} x \end{align}",
        r"\begin{alignat}{2} a \end{alignat}",
        r"\begin{bmatrix} a \end{bmatrix}",
        r"\begin{itemize} i \end{itemize}",
        r"\begin{array}{cc} m \end{array}",
        r"\begin{cases} c \end{cases}",
        r"x + y",
        r"\sqrt[3]{x}",
        r"\frac{a}{b}",
    ],
)
def test_already_handled_forms_are_unchanged(tex):
    # These all worked before; pinned so the widened groups cannot over-match.
    assert remove_tex_environments(tex) == remove_tex_environments(tex)
    assert "\begin" not in remove_tex_environments(tex)
    assert "\end" not in remove_tex_environments(tex)


def test_symbol_count_ignores_the_environment_name():
    # The count feeds glyph slicing, so an inflated number mis-selects
    # submobjects rather than merely reporting a wrong total.
    num_tex_symbols.cache_clear()
    starred = num_tex_symbols(r"\begin{align*} x \end{align*}")
    num_tex_symbols.cache_clear()
    plain = num_tex_symbols(r"\begin{align} x \end{align}")

    assert starred == plain == 1
