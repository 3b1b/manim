from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
import yaml
import subprocess
from functools import lru_cache

from pathlib import Path
import tempfile

from manimlib.utils.cache import cache_on_disk
from manimlib.config import manim_config
from manimlib.config import get_manim_dir
from manimlib.logger import log
from manimlib.utils.simple_functions import hash_string


def get_tex_template_config(template_name: str) -> dict[str, str]:
    name = template_name.replace(" ", "_").lower()
    template_path = os.path.join(get_manim_dir(), "manimlib", "tex_templates.yml")
    with open(template_path, encoding="utf-8") as tex_templates_file:
        templates_dict = yaml.safe_load(tex_templates_file)
    if name not in templates_dict:
        log.warning(f"Cannot recognize template {name}, falling back to 'default'.")
        name = "default"
    return templates_dict[name]


@lru_cache
def get_tex_config(template: str = "") -> tuple[str, str]:
    """
    Returns a compiler and preamble to use for rendering LaTeX
    """
    template = template or manim_config.tex.template
    config = get_tex_template_config(template)
    return config["compiler"], config["preamble"]


def get_full_tex(content: str, preamble: str = ""):
    return (
        "\n\n".join(
            (
                "\\documentclass[preview]{standalone}",
                preamble,
                "\\begin{document}",
                content,
                "\\end{document}",
            )
        )
        + "\n"
    )


# Tags dvisvgm uses for real geometry. A <path> only counts when it has a d attribute.
_DRAWABLE_SVG_TAGS = {"polygon", "polyline", "line", "rect", "circle", "ellipse"}

MISSING_GLYPH_OUTLINE_MESSAGE = (
    "dvisvgm produced an SVG with no glyph outlines "
    "(empty <defs/> and unresolved <use> references). "
    "dvisvgm --no-fonts needs Type 1 font outlines. "
    "On MiKTeX Basic, T1 Computer Modern (ecrm) does not include them "
    "unless cm-super is installed: mpm --install=cm-super, then initexmf --mkmaps. "
    "\\usepackage{lmodern} after \\usepackage[T1]{fontenc} also supplies Type 1 outlines."
)


def _local_svg_tag(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def svg_has_no_glyph_outlines(svg_string: str) -> bool:
    """True when dvisvgm referenced glyphs but did not embed vector outlines.

    ``dvisvgm --no-fonts`` still exits 0 in that case. MiKTeX Basic does this
    for T1 Computer Modern: the EC fonts have no Type 1 outlines unless
    cm-super is installed, METAFONT fails, and the SVG is an empty ``<defs/>``
    plus ``<use>`` elements.
    """
    if not svg_string or not svg_string.strip():
        return True
    try:
        root = ET.fromstring(svg_string)
    except ET.ParseError:
        return False

    has_outline = False
    has_use = False
    empty_defs = False
    for elem in root.iter():
        name = _local_svg_tag(elem.tag)
        if name == "defs":
            if len(elem) == 0:
                empty_defs = True
        elif name == "use":
            has_use = True
        elif name == "path":
            if (elem.get("d") or "").strip():
                has_outline = True
        elif name in _DRAWABLE_SVG_TAGS:
            has_outline = True
    return (not has_outline) and (empty_defs or has_use)


@lru_cache(maxsize=128)
def latex_to_svg(
    latex: str,
    template: str = "",
    additional_preamble: str = "",
    short_tex: str = "",
    show_message_during_execution: bool = True,
) -> str:
    """Convert LaTeX string to SVG string.

    Args:
        latex: LaTeX source code
        template: Path to a template LaTeX file
        additional_preamble: String including any added "\\usepackage{...}" style imports

    Returns:
        str: SVG source code

    Raises:
        LatexError: If LaTeX compilation fails, dvisvgm fails, or the SVG has no glyph outlines
        NotImplementedError: If compiler is not supported
    """
    if show_message_during_execution:
        message = f"Writing {(short_tex or latex)[:70]}..."
    else:
        message = ""

    compiler, preamble = get_tex_config(template)

    preamble = "\n".join([preamble, additional_preamble])
    full_tex = get_full_tex(latex, preamble)
    return full_tex_to_svg(full_tex, compiler, message)


@cache_on_disk
def full_tex_to_svg(full_tex: str, compiler: str = "latex", message: str = ""):
    if message:
        print(message, end="\r")

    if compiler == "latex":
        dvi_ext = ".dvi"
    elif compiler == "xelatex":
        dvi_ext = ".xdv"
    else:
        raise NotImplementedError(f"Compiler '{compiler}' is not implemented")

    # Use the custom LaTeX cache directory from the config
    temp_dir = Path(manim_config.directories.latex_cache)
    temp_dir.mkdir(exist_ok=True)  # Create the directory if it does not already exist

    # Define paths for the intermediate TeX and DVI files
    tex_path = temp_dir / "working.tex"
    dvi_path = tex_path.with_suffix(dvi_ext)

    # Write tex file
    tex_path.write_text(full_tex)

    # Run latex compiler
    process = subprocess.run(
        [
            compiler,
            *(["-no-pdf"] if compiler == "xelatex" else []),
            "-interaction=batchmode",
            "-halt-on-error",
            f"-output-directory={temp_dir}",
            tex_path.as_posix(),
        ],
        capture_output=True,
        text=True,
    )

    if process.returncode != 0 and not dvi_path.exists():
        # Handle error
        error_str = ""
        log_path = tex_path.with_suffix(".log")
        if log_path.exists():
            content = log_path.read_text()
            error_match = re.search(r"(?<=\n! ).*\n.*\n", content)
            if error_match:
                error_str = error_match.group()
        raise LatexError(error_str or "LaTeX compilation failed")

    # Run dvisvgm and capture output directly
    process = subprocess.run(
        [
            "dvisvgm",
            dvi_path,
            "-n",  # no fonts
            "-v",
            "0",  # quiet
            "--stdout",  # output to stdout instead of file
        ],
        capture_output=True,
    )

    if process.returncode != 0:
        error_str = process.stderr.decode("utf-8", errors="replace").strip()
        raise LatexError(error_str or "dvisvgm failed to convert DVI to SVG")

    # Return SVG string. dvisvgm exits 0 even when it could not embed outlines.
    result = process.stdout.decode("utf-8")
    if svg_has_no_glyph_outlines(result):
        raise LatexError(MISSING_GLYPH_OUTLINE_MESSAGE)

    if message:
        print(" " * len(message), end="\r")

    return result


class LatexError(Exception):
    pass
