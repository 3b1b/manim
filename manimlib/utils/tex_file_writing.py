from __future__ import annotations

import os
import re
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
    return "\n\n".join((
        "\\documentclass[preview]{standalone}",
        preamble,
        "\\begin{document}",
        content,
        "\\end{document}"
    )) + "\n"


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
        LatexError: If LaTeX compilation fails
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

    # Write intermediate files to a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        tex_path = Path(temp_dir, "working").with_suffix(".tex")
        dvi_path = tex_path.with_suffix(dvi_ext)

        # Write tex file
        tex_path.write_text(full_tex)

        # Run latex compiler
        process = subprocess.run(
            [
                compiler,
                *(['-no-pdf'] if compiler == "xelatex" else []),
                "-interaction=batchmode",
                "-halt-on-error",
                f"-output-directory={temp_dir}",
                tex_path
            ],
            capture_output=True,
            text=True
        )

        if process.returncode != 0:
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
                "-v", "0",  # quiet
                "--stdout",  # output to stdout instead of file
            ],
            capture_output=True
        )

        # Return SVG string
        result = process.stdout.decode('utf-8')

    if message:
        print(" " * len(message), end="\r")

    return result


class LatexError(Exception):
    pass
