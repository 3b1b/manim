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

import typing

import numpy as np

from .. import logger
from ..animation.animation import Animation
from ..animation.transform import Transform
from ..constants import DOWN
from ..mobject.types.vectorized_mobject import VMobject
from ..utils.bezier import interpolate
from ..utils.rate_functions import there_and_back

if typing.TYPE_CHECKING:
    from ..mobject.mobject import Mobject
    from ..scene.scene import Scene

DEFAULT_FADE_LAG_RATIO: float = 0


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
        self,
        vmobject: VMobject,
        remover: bool = True,
        lag_ratio: float = DEFAULT_FADE_LAG_RATIO,
        **kwargs
    ) -> None:
        super().__init__(vmobject, remover=remover, lag_ratio=lag_ratio, **kwargs)

    def create_target(self) -> "Mobject":
        return self.mobject.copy().fade(1)

    def clean_up_from_scene(self, scene: "Scene" = None) -> None:
        super().clean_up_from_scene(scene)
        self.interpolate(0)


class FadeIn(Transform):
    def __init__(
        self, vmobject: VMobject, lag_ratio: float = DEFAULT_FADE_LAG_RATIO, **kwargs
    ) -> None:
        super().__init__(vmobject, lag_ratio=lag_ratio, **kwargs)

    def create_target(self) -> "Mobject":
        return self.mobject

    def create_starting_mobject(self) -> "Mobject":
        start = super().create_starting_mobject()
        start.fade(1)
        if isinstance(start, VMobject):
            start.set_stroke(width=0)
            start.set_fill(opacity=0)
        return start


class FadeInFrom(Transform):
    def __init__(
        self, mobject: "Mobject", direction: np.ndarray = DOWN, **kwargs
    ) -> None:
        self.direction = direction
        super().__init__(mobject, **kwargs)

    def create_target(self) -> "Mobject":
        return self.mobject.copy()

    def begin(self) -> None:
        super().begin()
        self.starting_mobject.shift(self.direction)
        self.starting_mobject.fade(1)


class FadeInFromDown(FadeInFrom):
    """
    Identical to FadeInFrom, just with a name that
    communicates the default
    """

    def __init__(
        self, mobject: "Mobject", direction: np.ndarray = DOWN, **kwargs
    ) -> None:
        super().__init__(mobject, direction=direction, **kwargs)
        logger.warning(
            "FadeInFromDown is deprecated and will eventually disappear. Please use FadeInFrom(<mobject>, direction=DOWN, <other_args>) instead."
        )


class FadeOutAndShift(FadeOut):
    def __init__(
        self, mobject: "Mobject", direction: np.ndarray = DOWN, **kwargs
    ) -> None:
        self.direction = direction
        super().__init__(mobject, **kwargs)

    def create_target(self) -> "Mobject":
        target = super().create_target()
        target.shift(self.direction)
        return target


class FadeOutAndShiftDown(FadeOutAndShift):
    """
    Identical to FadeOutAndShift, just with a name that
    communicates the default
    """

    def __init__(
        self, mobject: "Mobject", direction: np.ndarray = DOWN, **kwargs
    ) -> None:
        super().__init__(mobject, direction=direction, **kwargs)
        logger.warning(
            "FadeOutAndShiftDown is deprecated and will eventually disappear. Please use FadeOutAndShift(<mobject>, direction=DOWN, <other_args>) instead."
        )


class FadeInFromPoint(FadeIn):
    def __init__(
        self, mobject: "Mobject", point: typing.Union[Mobject,np.ndarray], **kwargs
    ) -> None:
        self.point = point
        super().__init__(mobject, **kwargs)

    def create_starting_mobject(self) -> "Mobject":
        start = super().create_starting_mobject()
        start.scale(0)
        start.move_to(self.point)
        return start


class FadeInFromLarge(FadeIn):
    def __init__(self, mobject: "Mobject", scale_factor: float = 2, **kwargs) -> None:
        self.scale_factor = scale_factor
        super().__init__(mobject, **kwargs)

    def create_starting_mobject(self) -> "Mobject":
        start = super().create_starting_mobject()
        start.scale(self.scale_factor)
        return start


class VFadeIn(Animation):
    """
    VFadeIn and VFadeOut only work for VMobjects,
    """

    def __init__(
        self, mobject: "Mobject", suspend_mobject_updating: bool = False, **kwargs
    ) -> None:
        super().__init__(
            mobject, suspend_mobject_updating=suspend_mobject_updating, **kwargs
        )

    def interpolate_submobject(
        self, submobject: "Mobject", starting_sumobject: "Mobject", alpha: float
    ) -> None:
        submobject.set_stroke(
            opacity=interpolate(0, starting_sumobject.get_stroke_opacity(), alpha)
        )
        submobject.set_fill(
            opacity=interpolate(0, starting_sumobject.get_fill_opacity(), alpha)
        )


class VFadeOut(VFadeIn):
    def __init__(self, mobject: "Mobject", remover: bool = True, **kwargs) -> None:
        super().__init__(mobject, remover=remover, **kwargs)

    def interpolate_submobject(
        self, submobject: "Mobject", starting_sumobject: "Mobject", alpha: float
    ) -> None:
        super().interpolate_submobject(submobject, starting_sumobject, 1 - alpha)


class VFadeInThenOut(VFadeIn):
    def __init__(
        self,
        mobject: "Mobject",
        remover: bool = True,
        rate_func: typing.Callable[[float, float], float] = there_and_back,
        **kwargs
    ):
        super().__init__(mobject, remover=remover, rate_func=rate_func, **kwargs)
