from __future__ import annotations

import os
import re
import yaml
import subprocess

from pathlib import Path
import tempfile

from manimlib.utils.cache import cache_on_disk
from manimlib.config import get_custom_config
from manimlib.config import get_manim_dir
from manimlib.logger import log
from manimlib.utils.simple_functions import hash_string


SAVED_TEX_CONFIG = {}


def get_tex_template_config(template_name: str) -> dict[str, str]:
    name = template_name.replace(" ", "_").lower()
    template_path = os.path.join(get_manim_dir(), "manimlib", "tex_templates.yml")
    with open(template_path, encoding="utf-8") as tex_templates_file:
        templates_dict = yaml.safe_load(tex_templates_file)
    if name not in templates_dict:
        log.warning(
            "Cannot recognize template '%s', falling back to 'default'.",
            name
        )
        name = "default"
    return templates_dict[name]


def get_tex_config() -> dict[str, str]:
    """
    Returns a dict which should look something like this:
    {
        "template": "default",
        "compiler": "latex",
        "preamble": "..."
    }
    """
    # Only load once, then save thereafter
    if not SAVED_TEX_CONFIG:
        template_name = get_custom_config()["style"]["tex_template"]
        template_config = get_tex_template_config(template_name)
        SAVED_TEX_CONFIG.update({
            "template": template_name,
            "compiler": template_config["compiler"],
            "preamble": template_config["preamble"]
        })
    return SAVED_TEX_CONFIG


def get_full_tex(content: str, preamble: str = ""):
    return "\n\n".join((
        "\\documentclass[preview]{standalone}",
        preamble,
        "\\begin{document}",
        content,
        "\\end{document}"
    )) + "\n"


@cache_on_disk
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
        max_message_len = 80
        message = f"Writing {short_tex or latex}"
        if len(message) > max_message_len:
            message = message[:max_message_len - 3] + "..."
        print(message, end="\r")

    tex_config = get_tex_config()
    if template and template != tex_config["template"]:
        tex_config = get_tex_template_config(template)

    compiler = tex_config["compiler"]

    if compiler == "latex":
        program = "latex"
        dvi_ext = ".dvi"
    elif compiler == "xelatex":
        program = "xelatex -no-pdf"
        dvi_ext = ".xdv"
    else:
        raise NotImplementedError(f"Compiler '{compiler}' is not implemented")

    preamble = tex_config["preamble"] + "\n" + additional_preamble
    full_tex = get_full_tex(latex, preamble)

    # Write intermediate files to a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = os.path.join(temp_dir, "working")
        tex_path = base_path + ".tex"
        dvi_path = base_path + dvi_ext

        # Write tex file
        with open(tex_path, "w", encoding="utf-8") as tex_file:
            tex_file.write(full_tex)

        # Run latex compiler
        process = subprocess.run(
            [
                program.split()[0],  # Split for xelatex case
                "-interaction=batchmode",
                "-halt-on-error",
                "-output-directory=" + temp_dir,
                tex_path
            ] + (["--no-pdf"] if compiler == "xelatex" else []),
            capture_output=True,
            text=True
        )

        if process.returncode != 0:
            # Handle error
            error_str = ""
            log_path = base_path + ".log"
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as log_file:
                    content = log_file.read()
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

    if show_message_during_execution:
        print(" " * len(message), end="\r")

    return result


class LatexError(Exception):
    pass
