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

    def __init__(
        self, vmobject, remover=True, lag_ratio=DEFAULT_FADE_LAG_RATIO, **kwargs
    ):
        super().__init__(vmobject, remover=remover, lag_ratio=lag_ratio, **kwargs)

    def create_target(self):
        return self.mobject.copy().fade(1)

    def clean_up_from_scene(self, scene=None):
        super().clean_up_from_scene(scene)
        self.interpolate(0)


class FadeIn(Transform):
    def __init__(self, vmobject, lag_ratio=DEFAULT_FADE_LAG_RATIO, **kwargs):
        super().__init__(vmobject, lag_ratio=lag_ratio, **kwargs)

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
    def __init__(self, mobject, direction=DOWN, **kwargs):
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

    def __init__(self, mobject, direction=DOWN, **kwargs):
        super().__init__(mobject, direction=direction, **kwargs)
        logger.warning(
            "FadeInFromDown is deprecated and will eventually disappear. Please use FadeInFrom(<mobject>, direction=DOWN, <other_args>) instead."
        )


class FadeOutAndShift(FadeOut):
    def __init__(self, mobject, direction=DOWN, **kwargs):
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

    def __init__(self, mobject, direction=DOWN, **kwargs):
        super().__init__(mobject, direction=direction, **kwargs)
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
    def __init__(self, mobject, scale_factor=2, **kwargs):
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

    def __init__(self, mobject, suspend_mobject_updating=False, **kwargs):
        super().__init__(
            mobject, suspend_mobject_updating=suspend_mobject_updating, **kwargs
        )

    def interpolate_submobject(self, submob, start, alpha):
        submob.set_stroke(opacity=interpolate(0, start.get_stroke_opacity(), alpha))
        submob.set_fill(opacity=interpolate(0, start.get_fill_opacity(), alpha))


class VFadeOut(VFadeIn):
    def __init__(self, mobject, remover=True, **kwargs):
        super().__init__(mobject, remover=remover, **kwargs)

    def interpolate_submobject(self, submob, start, alpha):
        super().interpolate_submobject(submob, start, 1 - alpha)


class VFadeInThenOut(VFadeIn):
    def __init__(self, mobject, remover=True, rate_func=there_and_back, **kwargs):
        super().__init__(mobject, remover=remover, rate_func=rate_func, **kwargs)
