from __future__ import annotations

import re

from manimlib.mobject.svg.string_mobject import StringMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.color import color_to_hex
from manimlib.utils.color import hex_to_int
from manimlib.utils.tex_file_writing import tex_content_to_svg_file
from manimlib.utils.tex import num_tex_symbols
from manimlib.logger import log

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.typing import ManimColor, Span, Selector


SCALE_FACTOR_PER_FONT_POINT = 0.001


class Tex(StringMobject):
    tex_environment: str = "align*"

    def __init__(
        self,
        *tex_strings: str,
        font_size: int = 48,
        alignment: str = R"\centering",
        template: str = "",
        additional_preamble: str = "",
        tex_to_color_map: dict = dict(),
        t2c: dict = dict(),
        isolate: Selector = [],
        use_labelled_svg: bool = True,
        pdf_flag: bool = True,
        documentclass: str = "",
        **kwargs
    ):
        # Combine multi-string arg, but mark them to isolate
        if len(tex_strings) > 1:
            if isinstance(isolate, (str, re.Pattern, tuple)):
                isolate = [isolate]
            isolate = [*isolate, *tex_strings]

        tex_string = (" ".join(tex_strings)).strip()

        # Prevent from passing an empty string.
        if not tex_string.strip():
            tex_string = R"\\"

        self.tex_string = tex_string
        self.alignment = alignment
        self.template = template
        self.additional_preamble = additional_preamble
        self.documentclass = documentclass
        self.tex_to_color_map = dict(**t2c, **tex_to_color_map)
        self.pdf_flag = pdf_flag

        super().__init__(
            tex_string,
            use_labelled_svg=use_labelled_svg,
            isolate=isolate,
            **kwargs
        )

        self.set_color_by_tex_to_color_map(self.tex_to_color_map)
        self.scale(SCALE_FACTOR_PER_FONT_POINT * font_size)

    @property
    def hash_seed(self) -> tuple:
        return (
            self.__class__.__name__,
            self.svg_default,
            self.path_string_config,
            self.base_color,
            self.isolate,
            self.protect,
            self.tex_string,
            self.alignment,
            self.tex_environment,
            self.tex_to_color_map,
            self.template,
            self.additional_preamble,
            self.documentclass
        )

    def get_file_path_by_content(self, content: str) -> str:
        return tex_content_to_svg_file(
            content, self.template, self.additional_preamble, self.tex_string, self.documentclass, self.pdf_flag
        )

    # Parsing

    @staticmethod
    def get_command_matches(string: str) -> list[re.Match]:
        # Lump together adjacent brace pairs
        pattern = re.compile(r"""
            (?P<command>\\(?:[a-zA-Z]+|.))
            |(?P<open>{+)
            |(?P<close>}+)
        """, flags=re.X | re.S)
        result = []
        open_stack = []
        for match_obj in pattern.finditer(string):
            if match_obj.group("open"):
                open_stack.append((match_obj.span(), len(result)))
            elif match_obj.group("close"):
                close_start, close_end = match_obj.span()
                while True:
                    if not open_stack:
                        raise ValueError("Missing '{' inserted")
                    (open_start, open_end), index = open_stack.pop()
                    n = min(open_end - open_start, close_end - close_start)
                    result.insert(index, pattern.fullmatch(
                        string, pos=open_end - n, endpos=open_end
                    ))
                    result.append(pattern.fullmatch(
                        string, pos=close_start, endpos=close_start + n
                    ))
                    close_start += n
                    if close_start < close_end:
                        continue
                    open_end -= n
                    if open_start < open_end:
                        open_stack.append(((open_start, open_end), index))
                    break
            else:
                result.append(match_obj)
        if open_stack:
            raise ValueError("Missing '}' inserted")
        return result

    @staticmethod
    def get_command_flag(match_obj: re.Match) -> int:
        if match_obj.group("open"):
            return 1
        if match_obj.group("close"):
            return -1
        return 0

    @staticmethod
    def replace_for_content(match_obj: re.Match) -> str:
        return match_obj.group()

    @staticmethod
    def replace_for_matching(match_obj: re.Match) -> str:
        if match_obj.group("command"):
            return match_obj.group()
        return ""

    @staticmethod
    def get_attr_dict_from_command_pair(
        open_command: re.Match, close_command: re.Match
    ) -> dict[str, str] | None:
        if len(open_command.group()) >= 2:
            return {}
        return None

    def get_configured_items(self) -> list[tuple[Span, dict[str, str]]]:
        return [
            (span, {})
            for selector in self.tex_to_color_map
            for span in self.find_spans_by_selector(selector)
        ]

    @staticmethod
    def get_color_command(rgb_hex: str) -> str:
        rgb = hex_to_int(rgb_hex)
        rg, b = divmod(rgb, 256)
        r, g = divmod(rg, 256)
        return f"\\color[RGB]{{{r}, {g}, {b}}}"

    @staticmethod
    def get_command_string(
        attr_dict: dict[str, str], is_end: bool, label_hex: str | None
    ) -> str:
        if label_hex is None:
            return ""
        if is_end:
            return "}}"
        return "{{" + Tex.get_color_command(label_hex)

    def get_content_prefix_and_suffix(
        self, is_labelled: bool
    ) -> tuple[str, str]:
        prefix_lines = []
        suffix_lines = []
        if not is_labelled:
            prefix_lines.append(self.get_color_command(
                color_to_hex(self.base_color)
            ))
        if self.alignment:
            prefix_lines.append(self.alignment)
        if self.tex_environment:
            prefix_lines.append(f"\\begin{{{self.tex_environment}}}")
            suffix_lines.append(f"\\end{{{self.tex_environment}}}")
        return (
            "".join([line + "\n" for line in prefix_lines]),
            "".join(["\n" + line for line in suffix_lines])
        )

    # Method alias

    def get_parts_by_tex(self, selector: Selector) -> VGroup:
        return self.select_parts(selector)

    def get_part_by_tex(self, selector: Selector, index: int = 0) -> VMobject:
        return self.select_part(selector, index)

    def set_color_by_tex(self, selector: Selector, color: ManimColor):
        return self.set_parts_color(selector, color)

    def set_color_by_tex_to_color_map(
        self, color_map: dict[Selector, ManimColor]
    ):
        return self.set_parts_color_by_dict(color_map)

    def get_tex(self) -> str:
        return self.get_string()

    # Specific to Tex
    def substr_to_path_count(self, substr: str) -> int:
        tex = self.get_tex()
        if len(self) != num_tex_symbols(tex):
            log.warning(f"Estimated size of {tex} does not match true size")
        return num_tex_symbols(substr)

    def get_symbol_substrings(self):
        pattern = "|".join((
            # Tex commands
            r"\\[a-zA-Z]+",
            # And most single characters, with these exceptions
            r"[^\^\{\}\s\_\$\\\&]",
        ))
        return re.findall(pattern, self.string)

    def make_number_changable(
        self,
        value: float | int | str,
        index: int = 0,
        replace_all: bool = False,
        **config,
    ) -> VMobject:
        substr = str(value)
        parts = self.select_parts(substr)
        if len(parts) == 0:
            log.warning(f"{value} not found in Tex.make_number_changable call")
            return VMobject()
        if index > len(parts) - 1:
            log.warning(f"Requested {index}th occurance of {value}, but only {len(parts)} exist")
            return VMobject()
        if not replace_all:
            parts = [parts[index]]

        from manimlib.mobject.numbers import DecimalNumber

        decimal_mobs = []
        for part in parts:
            if "." in substr:
                num_decimal_places = len(substr.split(".")[1])
            else:
                num_decimal_places = 0
            decimal_mob = DecimalNumber(
                float(value),
                num_decimal_places=num_decimal_places,
                **config,
            )
            decimal_mob.replace(part)
            decimal_mob.match_style(part)
            if len(part) > 1:
                self.remove(*part[1:])
            self.replace_submobject(self.submobjects.index(part[0]), decimal_mob)
            decimal_mobs.append(decimal_mob)

            # Replace substr with something that looks like a tex command. This
            # is to ensure Tex.substr_to_path_count counts it correctly.
            self.string = self.string.replace(substr, R"\decimalmob", 1)

        if replace_all:
            return VGroup(*decimal_mobs)
        return decimal_mobs[index]


class TexText(Tex):
    tex_environment: str = ""
