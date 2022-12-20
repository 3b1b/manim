from __future__ import annotations

from manimlib.constants import WHITE, GREY_C
from manimlib.constants import DOWN, LEFT, RIGHT, UP
from manimlib.constants import FRAME_WIDTH
from manimlib.constants import MED_LARGE_BUFF, SMALL_BUFF
from manimlib.mobject.geometry import Line
from manimlib.mobject.svg.tex_mobject import Tex, TexText
from manimlib.mobject.svg.mtex_mobject import MTex, MTexText


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.typing import ManimColor



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
