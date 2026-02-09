import re
import tempfile
import subprocess
from pathlib import Path
from functools import lru_cache

from manimlib.config import manim_config
from manimlib.utils.color import color_to_hex
from manimlib.utils.cache import cache_on_disk
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.utils.tex_file_writing import LatexError, get_tex_template_config


@lru_cache(maxsize=128)
def get_tex_preamble(template: str = "") -> str:
    template = template or manim_config.tex.template
    config = get_tex_template_config(template)
    return config["preamble"]


@cache_on_disk
def typst_tex2svg(content: str) -> str:
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


def typst_latex2svg(
    latex: str,
    template: str = "",
    additional_preamble: str = "",
    short_tex: str = "",
    show_message_during_execution: bool = True,
) -> str:
    if show_message_during_execution:
        short_tex = f"Writing {(short_tex or latex)[:70]}..."
        print(short_tex, end="\r")

    preamble = get_tex_preamble(template)
    full_tex = "\n".join([preamble, additional_preamble, latex])
    print(" " * len(short_tex), end="\r")
    return typst_tex2svg(full_tex)


class TypstTex(Tex):
    tex_environment: str = "$"

    def __init__(
        self, *tex_strings: str, alignment: str = "center", fill_border_width: int = 0, **kwargs
    ):
        alignment = f"#set align({alignment})"
        super().__init__(
            *tex_strings, alignment=alignment, fill_border_width=fill_border_width, **kwargs
        )

        for mob in self.family_members_with_points():
            if not mob.get_fill_opacity():
                mob.set_stroke(width=2)

    @staticmethod
    def get_color_command(rgb_hex: str) -> str:
        return f'#set text(fill: rgb("{rgb_hex}"))'

    def get_content_prefix_and_suffix(self, is_labelled: bool) -> tuple[str, str]:
        prefix_lines = []
        suffix_line = ""

        if not is_labelled:
            prefix_lines.append(self.get_color_command(color_to_hex(self.base_color)))
        if self.alignment:
            prefix_lines.append(self.alignment)

        prefix_lines = "".join([line + "\n" for line in prefix_lines])

        if self.tex_environment:
            prefix_lines += f"{self.tex_environment} "
            suffix_line = f" {self.tex_environment}"

        return prefix_lines, suffix_line

    def get_svg_string_by_content(self, content: str) -> str:
        return typst_latex2svg(
            content, self.template, self.additional_preamble, short_tex=self.tex_string
        )


class TypstTexText(TypstTex):
    tex_environment: str = ""
