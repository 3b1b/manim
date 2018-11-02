

import numpy as np

from constants import *

from animation.animation import Animation
from mobject.svg.tex_mobject import TextMobject
from mobject.types.vectorized_mobject import VMobject
from mobject.types.vectorized_mobject import VectorizedPoint
from animation.transform import Transform
from utils.bezier import interpolate
from utils.config_ops import digest_config
from utils.paths import counterclockwise_path
from utils.rate_functions import double_smooth
from utils.rate_functions import smooth

import position

# Drawing


class ShowPartial(Animation):
    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.pointwise_become_partial(
            starting_submobject, *self.get_bounds(alpha)
        )

    def get_bounds(self, alpha):
        raise Exception("Not Implemented")


class ShowCreation(ShowPartial):
    CONFIG = {
        "submobject_mode": "one_at_a_time",
    }

    def get_bounds(self, alpha):
        return (0, alpha)


class Uncreate(ShowCreation):
    CONFIG = {
        "rate_func": lambda t: smooth(1 - t),
        "remover": True
    }


class DrawBorderThenFill(Animation):
    CONFIG = {
        "run_time": 2,
        "stroke_width": 2,
        "stroke_color": None,
        "rate_func": double_smooth,
    }

    def __init__(self, vmobject, **kwargs):
        if not isinstance(vmobject, VMobject):
            raise Exception("DrawBorderThenFill only works for VMobjects")
        self.reached_halfway_point_before = False
        Animation.__init__(self, vmobject, **kwargs)

    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.pointwise_become_partial(
            starting_submobject, 0, min(2 * alpha, 1)
        )
        if alpha < 0.5:
            if self.stroke_color:
                color = self.stroke_color
            elif starting_submobject.stroke_width > 0:
                color = starting_submobject.get_stroke_color()
            else:
                color = starting_submobject.get_color()
            submobject.set_stroke(color, width=self.stroke_width)
            submobject.set_fill(opacity=0)
        else:
            if not self.reached_halfway_point_before:
                self.reached_halfway_point_before = True
                submobject.points = np.array(starting_submobject.points)
            width, opacity = [
                interpolate(start, end, 2 * alpha - 1)
                for start, end in [
                    (self.stroke_width, starting_submobject.get_stroke_width()),
                    (0, starting_submobject.get_fill_opacity())
                ]
            ]
            submobject.set_stroke(width=width)
            submobject.set_fill(opacity=opacity)


class Write(DrawBorderThenFill):
    CONFIG = {
        "rate_func": None,
        "submobject_mode": "lagged_start",
    }

    def __init__(self, mob_or_text, **kwargs):
        digest_config(self, kwargs)
        if isinstance(mob_or_text, str):
            mobject = TextMobject(mob_or_text)
        else:
            mobject = mob_or_text

        if IS_LIVE_STREAMING:
            print(position.current)
            mobject.shift(position.current)
            position.current = position.current + 2 * DOWN
            if position.current[1] < -3:
                position.current[1] = 3
                position.current = position.current + 3 * RIGHT

        if "run_time" not in kwargs:
            self.establish_run_time(mobject)
        if "lag_factor" not in kwargs:
            if len(mobject.family_members_with_points()) < 4:
                min_lag_factor = 1
            else:
                min_lag_factor = 2
            self.lag_factor = max(self.run_time - 1, min_lag_factor)
        DrawBorderThenFill.__init__(self, mobject, **kwargs)

    def establish_run_time(self, mobject):
        num_subs = len(mobject.family_members_with_points())
        if num_subs < 15:
            self.run_time = 1
        else:
            self.run_time = 2

# Fading


class FadeOut(Transform):
    CONFIG = {
        "remover": True,
    }

    def __init__(self, mobject, **kwargs):
        target = mobject.copy()
        target.fade(1)
        Transform.__init__(self, mobject, target, **kwargs)

    def clean_up(self, surrounding_scene=None):
        Transform.clean_up(self, surrounding_scene)
        self.update(0)


class FadeIn(Transform):
    def __init__(self, mobject, **kwargs):
        target = mobject.copy()
        Transform.__init__(self, mobject, target, **kwargs)
        self.starting_mobject.fade(1)
        if isinstance(self.starting_mobject, VMobject):
            self.starting_mobject.set_stroke(width=0)
            self.starting_mobject.set_fill(opacity=0)


class FadeInAndShiftFromDirection(Transform):
    CONFIG = {
        "direction": DOWN,
    }

    def __init__(self, mobject, direction=None, **kwargs):
        digest_config(self, kwargs)
        target = mobject.copy()
        if direction is None:
            direction = self.direction
        mobject.shift(direction)
        mobject.fade(1)
        Transform.__init__(self, mobject, target, **kwargs)


class FadeInFrom(FadeInAndShiftFromDirection):
    """
    Alternate name for FadeInAndShiftFromDirection
    """


class FadeInFromDown(FadeInAndShiftFromDirection):
    """
    Essential a more convenient form of FadeInAndShiftFromDirection
    """
    CONFIG = {
        "direction": DOWN,
    }


class FadeOutAndShift(FadeOut):
    CONFIG = {
        "direction": DOWN,
    }

    def __init__(self, mobject, direction=None, **kwargs):
        FadeOut.__init__(self, mobject, **kwargs)
        if direction is None:
            direction = self.direction
        self.target_mobject.shift(direction)


class FadeOutAndShiftDown(FadeOutAndShift):
    CONFIG = {
        "direction": DOWN,
    }


class FadeInFromLarge(Transform):
    def __init__(self, mobject, scale_factor=2, **kwargs):
        target = mobject.copy()
        mobject.scale(scale_factor)
        mobject.fade(1)
        Transform.__init__(self, mobject, target, **kwargs)


class VFadeIn(Animation):
    """
    VFadeIn and VFadeOut only work for VMobjects, but they can be applied
    to mobjects while they are being animated in some other way (e.g. shifting
    then) in a way that does not work with FadeIn and FadeOut
    """
    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.set_stroke(
            opacity=interpolate(0, starting_submobject.get_stroke_opacity(), alpha)
        )
        submobject.set_fill(
            opacity=interpolate(0, starting_submobject.get_fill_opacity(), alpha)
        )


class VFadeOut(VFadeIn):
    CONFIG = {
        "remover": True
    }

    def update_submobject(self, submobject, starting_submobject, alpha):
        VFadeIn.update_submobject(
            self, submobject, starting_submobject, 1 - alpha
        )


# Growing


class GrowFromPoint(Transform):
    CONFIG = {
        "point_color": None,
    }

    def __init__(self, mobject, point, **kwargs):
        digest_config(self, kwargs)
        target = mobject.copy()
        point_mob = VectorizedPoint(point)
        if self.point_color:
            point_mob.set_color(self.point_color)
        mobject.replace(point_mob)
        mobject.set_color(point_mob.get_color())
        Transform.__init__(self, mobject, target, **kwargs)


class GrowFromCenter(GrowFromPoint):
    def __init__(self, mobject, **kwargs):
        GrowFromPoint.__init__(self, mobject, mobject.get_center(), **kwargs)


class GrowFromEdge(GrowFromPoint):
    def __init__(self, mobject, edge, **kwargs):
        GrowFromPoint.__init__(
            self, mobject, mobject.get_critical_point(edge), **kwargs
        )


class GrowArrow(GrowFromPoint):
    def __init__(self, arrow, **kwargs):
        GrowFromPoint.__init__(self, arrow, arrow.get_start(), **kwargs)


class SpinInFromNothing(GrowFromCenter):
    CONFIG = {
        "path_func": counterclockwise_path()
    }


class ShrinkToCenter(Transform):
    def __init__(self, mobject, **kwargs):
        Transform.__init__(
            self, mobject, mobject.get_point_mobject(), **kwargs
        )
