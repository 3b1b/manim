from __future__ import annotations

from manimlib.constants import BLACK, GREY_E
from manimlib.constants import FRAME_HEIGHT
from manimlib.mobject.geometry import Rectangle

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manimlib.constants import ManimColor


class ScreenRectangle(Rectangle):
    def __init__(
        self,
        aspect_ratio: float = 16.0 / 9.0,
        height: float = 4,
        **kwargs
    ):
        super().__init__(
            width=aspect_ratio * height,
            height=height,
            **kwargs
        )


class FullScreenRectangle(ScreenRectangle):
    def __init__(
        self,
        height: float = FRAME_HEIGHT,
        fill_color: ManimColor = GREY_E,
        fill_opacity: float = 1,
        stroke_width: float = 0,
        **kwargs,
    ):
        super().__init__(
            height=height,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
        )


class FullScreenFadeRectangle(FullScreenRectangle):
    def __init__(
        self,
        stroke_width: float = 0.0,
        fill_color: ManimColor = BLACK,
        fill_opacity: float = 0.7,
        **kwargs,
    ):
        super().__init__(
            stroke_width=stroke_width,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
        )
