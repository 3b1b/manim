"""Mobjects used to mark and annotate other mobjects."""

__all__ = ["SurroundingRectangle", "BackgroundRectangle", "Cross", "Underline"]


from ..constants import *
from ..mobject.geometry import Line
from ..mobject.geometry import Rectangle
from ..mobject.types.vectorized_mobject import VGroup
from ..mobject.types.vectorized_mobject import VMobject
from ..utils.color import Color, YELLOW, BLACK, RED
from ..utils.config_ops import digest_config


class SurroundingRectangle(Rectangle):
    CONFIG = {
        "color": YELLOW,
        "buff": SMALL_BUFF,
    }

    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs)
        kwargs["width"] = mobject.get_width() + 2 * self.buff
        kwargs["height"] = mobject.get_height() + 2 * self.buff
        Rectangle.__init__(self, **kwargs)
        self.move_to(mobject)


class BackgroundRectangle(SurroundingRectangle):
    CONFIG = {
        "color": BLACK,
        "stroke_width": 0,
        "stroke_opacity": 0,
        "fill_opacity": 0.75,
        "buff": 0,
    }

    def __init__(self, mobject, **kwargs):
        SurroundingRectangle.__init__(self, mobject, **kwargs)
        self.original_fill_opacity = self.fill_opacity

    def pointwise_become_partial(self, mobject, a, b):
        self.set_fill(opacity=b * self.original_fill_opacity)
        return self

    def set_style(
        self,
        stroke_color=None,
        stroke_width=None,
        fill_color=None,
        fill_opacity=None,
        family=True,
    ):
        # Unchangable style, except for fill_opacity
        VMobject.set_style(
            self,
            stroke_color=BLACK,
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=fill_opacity,
        )
        return self

    def get_fill_color(self):
        return Color(self.color)


class Cross(VGroup):
    CONFIG = {
        "stroke_color": RED,
        "stroke_width": 6,
    }

    def __init__(self, mobject, **kwargs):
        VGroup.__init__(
            self,
            Line(UP + LEFT, DOWN + RIGHT),
            Line(UP + RIGHT, DOWN + LEFT),
        )
        self.replace(mobject, stretch=True)
        self.set_stroke(self.stroke_color, self.stroke_width)


class Underline(Line):
    CONFIG = {
        "buff": SMALL_BUFF,
    }

    def __init__(self, mobject, **kwargs):
        super().__init__(LEFT, RIGHT, **kwargs)
        self.match_width(mobject)
        self.next_to(mobject, DOWN, buff=self.buff)
