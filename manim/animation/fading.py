"""Fading in and out of view."""


__all__ = [
    "FadeOut",
    "FadeIn",
    "FadeInFrom",
    "FadeInFromDown",
    "FadeOutAndShift",
    "FadeOutAndShiftDown",
    "FadeInFromPoint",
    "FadeInFromLarge",
    "VFadeIn",
    "VFadeOut",
    "VFadeInThenOut",
]


from ..animation.animation import Animation
from ..animation.animation import DEFAULT_ANIMATION_LAG_RATIO
from ..animation.transform import Transform
from ..constants import DOWN
from ..mobject.types.vectorized_mobject import VMobject
from ..utils.bezier import interpolate
from ..utils.rate_functions import there_and_back
from .. import logger


DEFAULT_FADE_LAG_RATIO = 0


class FadeOut(Transform):
    """A transform fading out the given mobject.

    Examples
    --------

    .. manim:: PlaneFadeOut

        class PlaneFadeOut(Scene):
            def construct(self):
                sq1 = Square()
                sq2 = Square()
                sq3 = Square()
                sq1.next_to(sq2, LEFT)
                sq3.next_to(sq2, RIGHT)
                circ = Circle()
                circ.next_to(sq2, DOWN)

                self.add(sq1, sq2, sq3, circ)
                self.wait()

                self.play(FadeOut(sq1), FadeOut(sq2), FadeOut(sq3))
                self.wait()

    """

    CONFIG = {
        "remover": True,
        "lag_ratio": DEFAULT_FADE_LAG_RATIO,
    }

    def create_target(self):
        return self.mobject.copy().fade(1)

    def clean_up_from_scene(self, scene=None):
        super().clean_up_from_scene(scene)
        self.interpolate(0)


class FadeIn(Transform):
    CONFIG = {
        "lag_ratio": DEFAULT_FADE_LAG_RATIO,
    }

    def create_target(self):
        return self.mobject

    def create_starting_mobject(self):
        start = super().create_starting_mobject()
        start.fade(1)
        if isinstance(start, VMobject):
            start.set_stroke(width=0)
            start.set_fill(opacity=0)
        return start


class FadeInFrom(Transform):
    CONFIG = {
        "direction": DOWN,
        "lag_ratio": DEFAULT_ANIMATION_LAG_RATIO,
    }

    def __init__(self, mobject, direction=None, **kwargs):
        if direction is not None:
            self.direction = direction
        super().__init__(mobject, **kwargs)

    def create_target(self):
        return self.mobject.copy()

    def begin(self):
        super().begin()
        self.starting_mobject.shift(self.direction)
        self.starting_mobject.fade(1)


class FadeInFromDown(FadeInFrom):
    """
    Identical to FadeInFrom, just with a name that
    communicates the default
    """

    CONFIG = {
        "direction": DOWN,
        "lag_ratio": DEFAULT_ANIMATION_LAG_RATIO,
    }

    def __init__(self, mobject, **kwargs):
        super().__init__(mobject, direction=DOWN, **kwargs)
        logger.warning(
            "FadeInFromDown is deprecated and will eventually disappear. Please use FadeInFrom(<mobject>, direction=DOWN, <other_args>) instead."
        )


class FadeOutAndShift(FadeOut):
    CONFIG = {
        "direction": DOWN,
    }

    def __init__(self, mobject, direction=None, **kwargs):
        if direction is not None:
            self.direction = direction
        super().__init__(mobject, **kwargs)

    def create_target(self):
        target = super().create_target()
        target.shift(self.direction)
        return target


class FadeOutAndShiftDown(FadeOutAndShift):
    """
    Identical to FadeOutAndShift, just with a name that
    communicates the default
    """

    CONFIG = {
        "direction": DOWN,
    }

    def __init__(self, mobject, **kwargs):
        super().__init__(mobject, direction=DOWN, **kwargs)
        logger.warning(
            "FadeOutAndShiftDown is deprecated and will eventually disappear. Please use FadeOutAndShift(<mobject>, direction=DOWN, <other_args>) instead."
        )


class FadeInFromPoint(FadeIn):
    def __init__(self, mobject, point, **kwargs):
        self.point = point
        super().__init__(mobject, **kwargs)

    def create_starting_mobject(self):
        start = super().create_starting_mobject()
        start.scale(0)
        start.move_to(self.point)
        return start


class FadeInFromLarge(FadeIn):
    CONFIG = {
        "scale_factor": 2,
    }

    def __init__(self, mobject, scale_factor=2, **kwargs):
        if scale_factor is not None:
            self.scale_factor = scale_factor
        super().__init__(mobject, **kwargs)

    def create_starting_mobject(self):
        start = super().create_starting_mobject()
        start.scale(self.scale_factor)
        return start


class VFadeIn(Animation):
    """
    VFadeIn and VFadeOut only work for VMobjects,
    """

    CONFIG = {
        "suspend_mobject_updating": False,
    }

    def interpolate_submobject(self, submob, start, alpha):
        submob.set_stroke(opacity=interpolate(0, start.get_stroke_opacity(), alpha))
        submob.set_fill(opacity=interpolate(0, start.get_fill_opacity(), alpha))


class VFadeOut(VFadeIn):
    CONFIG = {"remover": True}

    def interpolate_submobject(self, submob, start, alpha):
        super().interpolate_submobject(submob, start, 1 - alpha)


class VFadeInThenOut(VFadeIn):
    CONFIG = {
        "rate_func": there_and_back,
        "remover": True,
    }
