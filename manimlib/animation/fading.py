from manimlib.animation.animation import Animation
from manimlib.animation.transform import Transform
from manimlib.constants import *
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.bezier import interpolate
from manimlib.utils.config_ops import digest_config


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
