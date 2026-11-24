import shutil
import unittest
from unittest.mock import patch

from manimlib.mobject.svg.svg_mobject import get_svg_content_height
from manimlib.utils.tex_file_writing import LatexError
from manimlib.utils.tex_file_writing import MISSING_GLYPH_OUTLINE_MESSAGE
from manimlib.utils.tex_file_writing import full_tex_to_svg
from manimlib.utils.tex_file_writing import get_tex_config
from manimlib.utils.tex_file_writing import svg_has_no_glyph_outlines


# Shape reported for MiKTeX Basic: dvisvgm --no-fonts exits 0, but the glyph
# paths were never written because T1 Computer Modern has no Type 1 outlines.
EMPTY_DEFS_SVG = """<?xml version='1.0' encoding='UTF-8'?>
<svg version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' width='10pt' height='10pt' viewBox='0 0 10 10'>
<defs/>
<g id='page1'>
<use x='1' y='1' xlink:href='#g0-48'/>
</g>
</svg>
"""

PATH_SVG = """<?xml version='1.0' encoding='UTF-8'?>
<svg version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'>
<defs>
<path id='g0-48' d='M0 0 L10 0 L10 10 Z'/>
</defs>
<g id='page1'>
<use xlink:href='#g0-48'/>
</g>
</svg>
"""


def test_default_template_loads_latin_modern_after_fontenc():
    compiler, preamble = get_tex_config("default")
    fontenc_at = preamble.index("\\usepackage[T1]{fontenc}")
    lmodern_at = preamble.index("\\usepackage{lmodern}")

    assert compiler == "latex"
    assert fontenc_at < lmodern_at


def test_empty_defs_svg_has_no_glyph_outlines():
    assert svg_has_no_glyph_outlines(EMPTY_DEFS_SVG)
    assert svg_has_no_glyph_outlines("")
    assert not svg_has_no_glyph_outlines(PATH_SVG)


def test_empty_defs_svg_explains_missing_type1_fonts():
    try:
        get_svg_content_height(EMPTY_DEFS_SVG)
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        message = str(exc)

    assert "SVG has no content to measure" in message
    assert MISSING_GLYPH_OUTLINE_MESSAGE in message
    assert "cm-super" in message
    assert "lmodern" in message


def test_svg_with_path_has_a_height():
    height = get_svg_content_height(PATH_SVG)
    assert height > 0


def test_full_tex_to_svg_rejects_outline_free_svg():
    def fake_run(command, **kwargs):
        class Result:
            returncode = 0
            stdout = EMPTY_DEFS_SVG.encode("utf-8")
            stderr = b""

        if command[0] == "dvisvgm":
            return Result()

        class LatexResult:
            returncode = 0
            stdout = ""
            stderr = ""

        return LatexResult()

    # Call the uncached function so the stub runs instead of a previous SVG.
    with patch("manimlib.utils.tex_file_writing.subprocess.run", fake_run):
        try:
            full_tex_to_svg.__wrapped__(
                "\\documentclass{article}\\begin{document}0\\end{document}\n",
                "latex",
                "",
            )
            raise AssertionError("expected LatexError")
        except LatexError as exc:
            assert "cm-super" in str(exc)
            assert "lmodern" in str(exc)


@unittest.skipUnless(
    shutil.which("latex") and shutil.which("dvisvgm"),
    "latex and dvisvgm are required",
)
def test_latin_modern_text_svg_is_measurable():
    # article, not standalone: the font fix does not depend on the document class,
    # and standalone is not part of a minimal TeX install.
    full_tex = "\n".join([
        "\\documentclass{article}",
        "\\pagestyle{empty}",
        "\\usepackage[T1]{fontenc}",
        "\\usepackage{lmodern}",
        "\\begin{document}",
        "0",
        "\\end{document}",
        "",
    ])
    svg = full_tex_to_svg.__wrapped__(full_tex, "latex", "")

    assert not svg_has_no_glyph_outlines(svg)
    assert get_svg_content_height(svg) > 0
