import re
import tempfile
import subprocess
from pathlib import Path
from functools import lru_cache

from manimlib.config import manim_config
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.color import color_to_hex
from manimlib.utils.cache import cache_on_disk
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.geometry import RoundedRectangle
from manimlib.utils.typst_tex_symbol_count import (
    ACCENT_COMMANDS,
    TYPST_TEX_SYMBOL_COUNT,
    DELIMITER_COMMANDS,
)
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

        # horizontal line has no fill.
        for mob in self.family_members_with_points():
            if not mob.get_fill_opacity():
                rect = RoundedRectangle(width=mob.get_width(), height=0.025, corner_radius=0.01)
                rect.set_fill(mob.get_color(), 1).set_stroke(width=0).move_to(mob)
                mob.become(rect)
        self.set_symbol_count()

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

    def set_symbol_count(self):
        pattern = "|".join([re.escape(k) for k in TYPST_TEX_SYMBOL_COUNT.keys() if k.strip()])
        regex_pattern = rf"""
            (?P<cmd>[a-zA-Z][a-zA-Z0-9\.]{{2,}})|{pattern}|
            (?P<script>[_^])|
            (?P<fraction>\bfrac\b)|
            (?P<char>\S)
        """

        counts = [0] * len(self.string)
        group_stack = []
        current_group = "normal"

        for match in re.finditer(regex_pattern, self.string, re.VERBOSE):
            text = match.group()
            start = match.start()
            num = TYPST_TEX_SYMBOL_COUNT.get(text, 1)

            if text == "(":
                group_stack.append(current_group)
                to_hide = current_group != "normal"
                current_group = "normal"
                if to_hide:
                    continue

            elif text == ")":
                if group_stack:
                    if (group := group_stack.pop()) != "normal":
                        if group in ("frac", "delimiter"):
                            counts[start] += 1
                        continue

            elif text == ",":
                if group_stack and group_stack[-1] == "frac":
                    continue

            elif match.group("script") or (match.group("command") and num == 0):
                current_group = "wrapper"
                continue

            elif text in ACCENT_COMMANDS:
                current_group = "wrapper"

            elif current_group in DELIMITER_COMMANDS:
                current_group = "delimiter"

            else:
                current_group = "normal"

            counts[start] += num if match.group("command") else 1

        self.symbol_count = counts

    def select_unisolated_substring(self, pattern: str | re.Pattern) -> VGroup:
        counts = self.symbol_count
        pat = re.escape(pattern)

        if pattern[0].isalnum():
            pat = r"(?<![a-zA-Z0-9_])" + pat

        if pattern[-1].isalnum():
            pat = pat + r"(?![a-zA-Z0-9_])"

        result = []

        for match in re.finditer(pat, self.string):
            start, end = match.start(), match.end()
            start_idx = sum(counts[:start])
            end_idx = start_idx + sum(counts[start:end])
            result.append(self[start_idx:end_idx])

        return VGroup(*result)


class TypstTexText(TypstTex):
    tex_environment: str = ""

    def set_symbol_count(self):
        pattern = r"""
            (?P<escape_char>\\[\S])|
            (?P<char>\S)
        """
        counts = [0] * len(self.string)
        for match in re.finditer(pattern, self.string, re.VERBOSE):
            start = match.start()
            if match.group("escape_char"):
                counts[start + 1] = 1
            else:
                counts[start] = 1

        self.symbol_count = counts
