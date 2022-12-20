from __future__ import annotations

from manimlib.constants import MED_SMALL_BUFF, WHITE, GREY_C
from manimlib.constants import DOWN, LEFT, RIGHT, UP
from manimlib.constants import FRAME_WIDTH
from manimlib.constants import MED_LARGE_BUFF, SMALL_BUFF
from manimlib.mobject.geometry import Line
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.svg.mtex_mobject import MTexText


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.typing import ManimColor, Vect3



class BulletedList(VGroup):
    def __init__(
        self,
        *items: str,
        buff: float = MED_LARGE_BUFF,
        aligned_edge: Vect3 = LEFT,
        **kwargs
    ):  
        labelled_content = [R"\item " + item for item in items]
        tex_string = "\n".join([
            R"\begin{itemize}",
            *labelled_content,
            R"\end{itemize}"
        ])
        tex_text = MTexText(tex_string, isolate=labelled_content, **kwargs)
        lines = (tex_text.select_part(part) for part in labelled_content)

        super().__init__(*lines)

        self.arrange(DOWN, buff=buff, aligned_edge=aligned_edge)

    def fade_all_but(self, index: int, opacity: float = 0.25) -> None:
        for i, part in enumerate(self.submobjects):
            part.set_fill(opacity=(1.0 if i == index else opacity))


class TexTextFromPresetString(MTexText):
    tex: str = ""
    default_color: ManimColor = WHITE

    def __init__(self, **kwargs):
        super().__init__(
            self.tex,
            color=kwargs.pop("color", self.default_color),
            **kwargs
        )


class Title(MTexText):
    def __init__(
        self,
        *text_parts: str,
        font_size: int = 72,
        include_underline: bool = True,
        underline_width: float = FRAME_WIDTH - 2,
        # This will override underline_width
        match_underline_width_to_text: bool = False,
        underline_buff: float = SMALL_BUFF,
        underline_style: dict = dict(stroke_width=2, stroke_color=GREY_C),
        **kwargs
    ):
        super().__init__(*text_parts, font_size=font_size, **kwargs)
        self.to_edge(UP, buff=MED_SMALL_BUFF)
        if include_underline:
            underline = Line(LEFT, RIGHT, **underline_style)
            underline.next_to(self, DOWN, buff=underline_buff)
            if match_underline_width_to_text:
                underline.match_width(self)
            else:
                underline.set_width(underline_width)
            self.add(underline)
            self.underline = underline
