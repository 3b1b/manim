from __future__ import annotations

from functools import reduce
import operator as op
import re

from manimlib.constants import BLACK, WHITE, GREY_C
from manimlib.constants import DOWN, LEFT, RIGHT, UP
from manimlib.constants import FRAME_WIDTH
from manimlib.constants import MED_LARGE_BUFF, SMALL_BUFF
from manimlib.mobject.geometry import Line
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.tex_file_writing import display_during_execution
from manimlib.utils.tex_file_writing import tex_content_to_svg_file

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, List, Dict
    from manimlib.typing import ManimColor


SCALE_FACTOR_PER_FONT_POINT = 0.001


class SingleStringTex(SVGMobject):
    height: float | None = None

    def __init__(
        self,
        tex_string: str,
        height: float | None = None,
        fill_color: ManimColor = WHITE,
        fill_opacity: float = 1.0,
        stroke_width: float = 0,
        svg_default: dict = dict(fill_color=WHITE),
        path_string_config: dict = dict(
            should_subdivide_sharp_curves=True,
            should_remove_null_curves=True,
        ),
        font_size: int = 48,
        alignment: str = R"\centering",
        math_mode: bool = True,
        organize_left_to_right: bool = False,
        template: str = "",
        additional_preamble: str = "",
        **kwargs
    ):
        self.tex_string = tex_string
        self.svg_default = dict(svg_default)
        self.path_string_config = dict(path_string_config)
        self.font_size = font_size
        self.alignment = alignment
        self.math_mode = math_mode
        self.organize_left_to_right = organize_left_to_right
        self.template = template
        self.additional_preamble = additional_preamble

        super().__init__(
            height=height,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            path_string_config=path_string_config,
            **kwargs
        )

        if self.height is None:
            self.scale(SCALE_FACTOR_PER_FONT_POINT * self.font_size)
        if self.organize_left_to_right:
            self.organize_submobjects_left_to_right()

    @property
    def hash_seed(self) -> tuple:
        return (
            self.__class__.__name__,
            self.svg_default,
            self.path_string_config,
            self.tex_string,
            self.alignment,
            self.math_mode,
            self.template,
            self.additional_preamble
        )

    def get_file_path(self) -> str:
        content = self.get_tex_file_body(self.tex_string)
        with display_during_execution(f"Writing \"{self.tex_string}\""):
            file_path = tex_content_to_svg_file(
                content, self.template, self.additional_preamble
            )
        return file_path

    def get_tex_file_body(self, tex_string: str) -> str:
        new_tex = self.get_modified_expression(tex_string)
        if self.math_mode:
            new_tex = "\\begin{align*}\n" + new_tex + "\n\\end{align*}"
        return self.alignment + "\n" + new_tex

    def get_modified_expression(self, tex_string: str) -> str:
        return self.modify_special_strings(tex_string.strip())

    def modify_special_strings(self, tex: str) -> str:
        tex = tex.strip()
        should_add_filler = reduce(op.or_, [
            # Fraction line needs something to be over
            tex == "\\over",
            tex == "\\overline",
            # Makesure sqrt has overbar
            tex == "\\sqrt",
            tex == "\\sqrt{",
            # Need to add blank subscript or superscript
            tex.endswith("_"),
            tex.endswith("^"),
            tex.endswith("dot"),
        ])
        if should_add_filler:
            filler = "{\\quad}"
            tex += filler

        should_add_double_filler = reduce(op.or_, [
            tex == "\\overset",
            # TODO: these can't be used since they change
            # the latex draw order.
            # tex == "\\frac", # you can use \\over as a alternative 
            # tex == "\\dfrac",
            # tex == "\\binom",
        ])
        if should_add_double_filler:
            filler = "{\\quad}{\\quad}"
            tex += filler

        if tex == "\\substack":
            tex = "\\quad"

        if tex == "":
            tex = "\\quad"

        # To keep files from starting with a line break
        if tex.startswith("\\\\"):
            tex = tex.replace("\\\\", "\\quad\\\\")

        tex = self.balance_braces(tex)

        # Handle imbalanced \left and \right
        num_lefts, num_rights = [
            len([
                s for s in tex.split(substr)[1:]
                if s and s[0] in "(){}[]|.\\"
            ])
            for substr in ("\\left", "\\right")
        ]
        if num_lefts != num_rights:
            tex = tex.replace("\\left", "\\big")
            tex = tex.replace("\\right", "\\big")

        for context in ["array"]:
            begin_in = ("\\begin{%s}" % context) in tex
            end_in = ("\\end{%s}" % context) in tex
            if begin_in ^ end_in:
                # Just turn this into a blank string,
                # which means caller should leave a
                # stray \\begin{...} with other symbols
                tex = ""
        return tex

    def balance_braces(self, tex: str) -> str:
        """
        Makes Tex resiliant to unmatched braces
        """
        num_unclosed_brackets = 0
        for i in range(len(tex)):
            if i > 0 and tex[i - 1] == "\\":
                # So as to not count '\{' type expressions
                continue
            char = tex[i]
            if char == "{":
                num_unclosed_brackets += 1
            elif char == "}":
                if num_unclosed_brackets == 0:
                    tex = "{" + tex
                else:
                    num_unclosed_brackets -= 1
        tex += num_unclosed_brackets * "}"
        return tex

    def get_tex(self) -> str:
        return self.tex_string

    def organize_submobjects_left_to_right(self):
        self.sort(lambda p: p[0])
        return self


class Tex(SingleStringTex):
    def __init__(
        self,
        *tex_strings: str,
        arg_separator: str = "",
        isolate: List[str] = [],
        tex_to_color_map: Dict[str, ManimColor] = {},
        **kwargs
    ):
        self.tex_strings = self.break_up_tex_strings(
            tex_strings,
            substrings_to_isolate=[*isolate, *tex_to_color_map.keys()]
        )
        full_string = arg_separator.join(self.tex_strings)

        super().__init__(full_string, **kwargs)
        self.break_up_by_substrings(self.tex_strings)
        self.set_color_by_tex_to_color_map(tex_to_color_map)

        if self.organize_left_to_right:
            self.organize_submobjects_left_to_right()

    def break_up_tex_strings(self, tex_strings: Iterable[str], substrings_to_isolate: List[str] = []) -> Iterable[str]:
        # Separate out any strings specified in the isolate
        # or tex_to_color_map lists.
        if len(substrings_to_isolate) == 0:
            return tex_strings
        patterns = (
            "({})".format(re.escape(ss))
            for ss in substrings_to_isolate
        )
        pattern = "|".join(patterns)
        pieces = []
        for s in tex_strings:
            if pattern:
                pieces.extend(re.split(pattern, s))
            else:
                pieces.append(s)
        return list(filter(lambda s: s, pieces))

    def break_up_by_substrings(self, tex_strings: Iterable[str]):
        """
        Reorganize existing submojects one layer
        deeper based on the structure of tex_strings (as a list
        of tex_strings)
        """
        if len(list(tex_strings)) == 1:
            submob = self.copy()
            self.set_submobjects([submob])
            return self
        new_submobjects = []
        curr_index = 0
        for tex_string in tex_strings:
            tex_string = tex_string.strip()
            if len(tex_string) == 0:
                continue
            sub_tex_mob = SingleStringTex(tex_string)
            num_submobs = len(sub_tex_mob)
            if num_submobs == 0:
                continue
            new_index = curr_index + num_submobs
            sub_tex_mob.set_submobjects(self.submobjects[curr_index:new_index])
            new_submobjects.append(sub_tex_mob)
            curr_index = new_index
        self.set_submobjects(new_submobjects)
        return self

    def get_parts_by_tex(
        self,
        tex: str,
        substring: bool = True,
        case_sensitive: bool = True
    ) -> VGroup:
        def test(tex1, tex2):
            if not case_sensitive:
                tex1 = tex1.lower()
                tex2 = tex2.lower()
            if substring:
                return tex1 in tex2
            else:
                return tex1 == tex2

        return VGroup(*filter(
            lambda m: isinstance(m, SingleStringTex) and test(tex, m.get_tex()),
            self.submobjects
        ))

    def get_part_by_tex(self, tex: str, **kwargs) -> SingleStringTex | None:
        all_parts = self.get_parts_by_tex(tex, **kwargs)
        return all_parts[0] if all_parts else None

    def set_color_by_tex(self, tex: str, color: ManimColor, **kwargs):
        self.get_parts_by_tex(tex, **kwargs).set_color(color)
        return self

    def set_color_by_tex_to_color_map(
        self,
        tex_to_color_map: dict[str, ManimColor],
        **kwargs
    ):
        for tex, color in list(tex_to_color_map.items()):
            self.set_color_by_tex(tex, color, **kwargs)
        return self

    def index_of_part(self, part: SingleStringTex, start: int = 0) -> int:
        return self.submobjects.index(part, start)

    def index_of_part_by_tex(self, tex: str, start: int = 0, **kwargs) -> int:
        part = self.get_part_by_tex(tex, **kwargs)
        return self.index_of_part(part, start)

    def slice_by_tex(
        self,
        start_tex: str | None = None,
        stop_tex: str | None = None,
        **kwargs
    ) -> VGroup:
        if start_tex is None:
            start_index = 0
        else:
            start_index = self.index_of_part_by_tex(start_tex, **kwargs)

        if stop_tex is None:
            return self[start_index:]
        else:
            stop_index = self.index_of_part_by_tex(stop_tex, start=start_index, **kwargs)
            return self[start_index:stop_index]

    def sort_alphabetically(self) -> None:
        self.submobjects.sort(key=lambda m: m.get_tex())

    def set_bstroke(self, color: ManimColor = BLACK, width: float = 4):
        self.set_stroke(color, width, background=True)
        return self


class TexText(Tex):
    def __init__(
        self,
        *tex_strings: str,
        math_mode: bool = False,
        arg_separator: str = "",
        **kwargs
    ):
        super().__init__(
            *tex_strings,
            math_mode=math_mode,
            arg_separator=arg_separator,
            **kwargs
        )


class BulletedList(TexText):
    def __init__(
        self,
        *items: str,
        buff: float = MED_LARGE_BUFF,
        dot_scale_factor: float = 2.0,
        alignment: str = "",
        **kwargs
    ):
        super().__init__(
            *(s + R"\\" for s in items),
            alignment=alignment,
            **kwargs
        )
        for part in self:
            dot = Tex(R"\cdot").scale(dot_scale_factor)
            dot.next_to(part[0], LEFT, SMALL_BUFF)
            part.add_to_back(dot)
        self.arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=buff
        )

    def fade_all_but(self, index_or_string: int | str, opacity: float = 0.5) -> None:
        arg = index_or_string
        if isinstance(arg, str):
            part = self.get_part_by_tex(arg)
        elif isinstance(arg, int):
            part = self.submobjects[arg]
        else:
            raise Exception("Expected int or string, got {0}".format(arg))
        for other_part in self.submobjects:
            if other_part is part:
                other_part.set_fill(opacity=1)
            else:
                other_part.set_fill(opacity=opacity)


class TexTextFromPresetString(TexText):
    tex: str = ""
    default_color: ManimColor = WHITE

    def __init__(self, **kwargs):
        super().__init__(
            self.tex,
            color=kwargs.pop("color", self.default_color),
            **kwargs
        )


class Title(TexText):
    def __init__(
        self,
        *text_parts: str,
        scale_factor: float = 1.0,
        include_underline: bool = True,
        underline_width: float = FRAME_WIDTH - 2,
        # This will override underline_width
        match_underline_width_to_text: bool = False,
        underline_buff: float = SMALL_BUFF,
        underline_style: dict = dict(stroke_width=2, stroke_color=GREY_C),
        **kwargs
    ):
        super().__init__(*text_parts, **kwargs)
        self.scale(scale_factor)
        self.to_edge(UP)
        if include_underline:
            underline = Line(LEFT, RIGHT, **underline_style)
            underline.next_to(self, DOWN, buff=underline_buff)
            if match_underline_width_to_text:
                underline.match_width(self)
            else:
                underline.set_width(underline_width)
            self.add(underline)
            self.underline = underline
