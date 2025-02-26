from __future__ import annotations

from colour import Color

from manimlib.config import manim_config
from manimlib.constants import BLACK, RED, YELLOW, WHITE
from manimlib.constants import DL, DOWN, DR, LEFT, RIGHT, UL, UR
from manimlib.constants import SMALL_BUFF
from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence
    from manimlib.mobject.mobject import Mobject
    from manimlib.typing import ManimColor, Self


class SurroundingRectangle(Rectangle):
    def __init__(
        self,
        mobject: Mobject,
        buff: float = SMALL_BUFF,
        color: ManimColor = YELLOW,
        **kwargs
    ):
        super().__init__(color=color, **kwargs)
        self.buff = buff
        self.surround(mobject)
        if mobject.is_fixed_in_frame():
            self.fix_in_frame()

    def surround(self, mobject, buff=None) -> Self:
        self.mobject = mobject
        self.buff = buff if buff is not None else self.buff
        super().surround(mobject, self.buff)
        return self

    def set_buff(self, buff) -> Self:
        self.buff = buff
        self.surround(self.mobject)
        return self


class BackgroundRectangle(SurroundingRectangle):
    def __init__(
        self,
        mobject: Mobject,
        color: ManimColor = None,
        stroke_width: float = 0,
        stroke_opacity: float = 0,
        fill_opacity: float = 0.75,
        buff: float = 0,
        **kwargs
    ):
        if color is None:
            color = manim_config.camera.background_color
        super().__init__(
            mobject,
            color=color,
            stroke_width=stroke_width,
            stroke_opacity=stroke_opacity,
            fill_opacity=fill_opacity,
            buff=buff,
            **kwargs
        )
        self.original_fill_opacity = fill_opacity

    def pointwise_become_partial(self, mobject: Mobject, a: float, b: float) -> Self:
        self.set_fill(opacity=b * self.original_fill_opacity)
        return self

    def set_style(
        self,
        stroke_color: ManimColor | None = None,
        stroke_width: float | None = None,
        fill_color: ManimColor | None = None,
        fill_opacity: float | None = None,
        family: bool = True,
        **kwargs
    ) -> Self:
        # Unchangeable style, except for fill_opacity
        VMobject.set_style(
            self,
            stroke_color=BLACK,
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=fill_opacity
        )
        return self

    def get_fill_color(self) -> Color:
        return Color(self.color)


class Cross(VGroup):
    def __init__(
        self,
        mobject: Mobject,
        stroke_color: ManimColor = RED,
        stroke_width: float | Sequence[float] = [0, 6, 0],
        **kwargs
    ):
        super().__init__(
            Line(UL, DR),
            Line(UR, DL),
        )
        self.insert_n_curves(20)
        self.replace(mobject, stretch=True)
        self.set_stroke(stroke_color, width=stroke_width)


class Underline(Line):
    def __init__(
        self,
        mobject: Mobject,
        buff: float = SMALL_BUFF,
        stroke_color=WHITE,
        stroke_width: float | Sequence[float] = [0, 3, 3, 0],
        stretch_factor=1.2,
        **kwargs
    ):
        super().__init__(LEFT, RIGHT, **kwargs)
        if not isinstance(stroke_width, (float, int)):
            self.insert_n_curves(len(stroke_width) - 2)
        self.set_stroke(stroke_color, stroke_width)
        self.set_width(mobject.get_width() * stretch_factor)
        self.next_to(mobject, DOWN, buff=buff)
