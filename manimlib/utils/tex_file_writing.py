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


@lru_cache(maxsize=128)
def get_tex_preamble(template: str = "") -> str:
    template = template or manim_config.tex.template
    config = get_tex_template_config(template)
    return config["preamble"]


@cache_on_disk
def tex2svg(content: str) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        tex_path = Path(temp_dir, "working").with_suffix(".typ")
        svg_path = tex_path.with_suffix(".svg")
        tex_path.write_text(content)

        process = subprocess.run(
            ["typst", "compile", "--format", "svg", tex_path, svg_path],
            capture_output=True,
            text=True,
        )

        # Handle error
        if process.returncode != 0:
            error_str = ""
            log_path = tex_path.with_suffix(".log")
            if log_path.exists():
                content = log_path.read_text()
                error_match = re.search(r"(?<=\n! ).*\n.*\n", content)
                if error_match:
                    error_str = error_match.group()
            raise LatexError(error_str or "LaTeX compilation failed")

        with open(svg_path) as file_svg:
            result = file_svg.read()
        return result


def latex2svg(
    latex: str,
    template: str = "",
    additional_preamble: str = "",
) -> str:
    preamble = get_tex_preamble(template)
    full_tex = "\n".join([preamble, additional_preamble, latex])
    return tex2svg(full_tex)


def get_tex_template_config(template_name: str) -> dict[str, str]:
    name = template_name.replace(" ", "_").lower()
    template_path = os.path.join(get_manim_dir(), "manimlib", "tex_templates.yml")
    with open(template_path, encoding="utf-8") as tex_templates_file:
        templates_dict = yaml.safe_load(tex_templates_file)
    if name not in templates_dict:
        log.warning(f"Cannot recognize template {name}, falling back to 'default'.")
        name = "default"
    return templates_dict[name]


class LatexError(Exception):
    pass
