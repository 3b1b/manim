import numpy as np

from manimlib.animation.animation import Animation
from manimlib.animation.transform import Transform
from manimlib.animation.composition import Succession
from manimlib.constants import *
from manimlib.mobject.svg.tex_mobject import TextMobject
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.bezier import interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.paths import counterclockwise_path
from manimlib.utils.rate_functions import double_smooth
from manimlib.utils.rate_functions import linear
from manimlib.utils.rate_functions import smooth

# Drawing


class ShowPartial(Animation):
    """
    Abstract class for ShowCreation and ShowPassingFlash
    """

    def interpolate_submobject(self, submob, start_submob, alpha):
        submob.pointwise_become_partial(
            start_submob, *self.get_bounds(alpha)
        )

    def get_bounds(self, alpha):
        raise Exception("Not Implemented")


class ShowCreation(ShowPartial):
    CONFIG = {
        "lag_ratio": 1,
    }

    def get_bounds(self, alpha):
        return (0, alpha)


class Uncreate(ShowCreation):
    CONFIG = {
        "rate_func": lambda t: smooth(1 - t),
        "remover": True
    }


class DrawBorderThenFill(Succession):
    CONFIG = {
        "run_time": 2,
        "stroke_width": 2,
        "stroke_color": None,
        "draw_border_animation_config": {},
        "fill_animation_config": {},
    }

    def __init__(self, vmobject, **kwargs):
        self.check_validity_of_input(vmobject)
        self.vmobject = vmobject
        self.original_vmobject = vmobject.copy()
        digest_config(self, kwargs)
        Succession.__init__(
            self,
            self.get_draw_border_animation(vmobject),
            self.get_fill_animation(vmobject),
            **kwargs,
        )

    def check_validity_of_input(self, vmobject):
        if not isinstance(vmobject, VMobject):
            raise Exception("DrawBorderThenFill only works for VMobjects")

    def get_draw_border_animation(self, vmobject):
        vmobject.set_stroke(
            color=self.get_stroke_color(vmobject),
            width=self.stroke_width
        )
        vmobject.set_fill(opacity=0)
        return ShowCreation(
            vmobject,
            **self.draw_border_animation_config
        )

    def get_stroke_color(self, vmobject):
        if self.stroke_color:
            return self.stroke_color
        elif vmobject.get_stroke_width() > 0:
            return vmobject.get_stroke_color()
        return vmobject.get_color()

    def get_fill_animation(self, vmobject):
        return Transform(
            vmobject,
            self.original_vmobject,
            **self.fill_animation_config,
        )

    def update_mobjects(self, dt):
        super().update_mobjects(dt)
        self.original_vmobject.update(dt)


class Write(DrawBorderThenFill):
    CONFIG = {
        "rate_func": linear,
        "lag_ratio": 0.5,
    }

    def __init__(self, mob_or_text, **kwargs):
        digest_config(self, kwargs)
        if isinstance(mob_or_text, str):
            mobject = TextMobject(mob_or_text)
        else:
            mobject = mob_or_text

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


class ShowIncreasingSubsets(Animation):
    def __init__(self, group, **kwargs):
        self.all_submobs = group.submobjects
        Animation.__init__(self, group, **kwargs)

    def interpolate_mobject(self, alpha):
        n_submobs = len(self.all_submobs)
        index = int(alpha * n_submobs)
        self.mobject.submobjects = self.all_submobs[:index]

# Fading


class FadeOut(Transform):
    CONFIG = {
        "remover": True,
    }

    def __init__(self, mobject, **kwargs):
        target = mobject.copy()
        target.fade(1)
        Transform.__init__(self, mobject, target, **kwargs)

    def clean_up_from_scene(self, scene=None):
        Transform.clean_up_from_scene(self, scene)
        self.interpolate(0)


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

    def interpolate_submobject(self, submobject, starting_submobject, alpha):
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

    def interpolate_submobject(self, submobject, starting_submobject, alpha):
        VFadeIn.interpolate_submobject(
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
        mobject.scale(0)
        mobject.move_to(point)
        if self.point_color:
            mobject.set_color(self.point_color)
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
