import numpy as np

from manimlib.animation.animation import Animation
from manimlib.animation.transform import Transform
from manimlib.animation.composition import Succession
from manimlib.animation.composition import LaggedStart
from manimlib.constants import *
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.bezier import interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.paths import counterclockwise_path
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
        # Intialize with no animations, but add them
        # in the begin method
        Succession.__init__(self, **kwargs)
        self.mobject = vmobject

    def check_validity_of_input(self, vmobject):
        if not isinstance(vmobject, VMobject):
            raise Exception("DrawBorderThenFill only works for VMobjects")

    def begin(self):
        vmobject = self.mobject
        self.original_vmobject = vmobject.copy()
        self.animations = [
            self.get_draw_border_animation(vmobject),
            self.get_fill_animation(vmobject),
        ]
        super().begin()

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


class Write(LaggedStart):
    CONFIG = {
        # To be figured out in
        # set_default_config_from_lengths
        "run_time": None,
        "lag_ratio": None,
        "draw_border_then_fill_config": {}
    }

    def __init__(self, tex_mobject, **kwargs):
        digest_config(self, kwargs)
        letters = VGroup(*tex_mobject.family_members_with_points())
        self.tex_mobject = tex_mobject
        self.set_default_config_from_length(len(letters))
        subanims = [
            DrawBorderThenFill(
                letter,
                **self.draw_border_then_fill_config,
            )
            for letter in letters
        ]
        LaggedStart.__init__(self, *subanims, **kwargs)
        self.mobject = tex_mobject

    def set_default_config_from_length(self, length):
        if self.run_time is None:
            if length < 15:
                self.run_time = 1
            else:
                self.run_time = 2
        if self.lag_ratio is None:
            self.lag_ratio = min(4.0 / length, 0.2)

    # def get_all_mobjects(self):
    #     # self.mobject here, which is what usually would
    #     # be returned, will be a different Group of all
    #     # letters
    #     return self.tex_mobject

    # def update_mobjects(self, dt):
    #     self.tex_mobject.update(dt)

    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)
        scene.remove(self.mobject)
        scene.add(self.tex_mobject)


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
