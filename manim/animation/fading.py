"""Fading in and out of view.

.. manim:: Example
    :hide_source:

    class Example(Scene):
        def construct(self):
            s1 = Square().set_color(BLUE)
            s2 = Square().set_color(BLUE)
            s3 = Square().set_color(BLUE)
            s4 = Square().set_color(BLUE)
            s5 = Square().set_color(BLUE)
            s6 = Square().set_color(RED)
            s7 = Square().set_color(RED)
            s8 = Square().set_color(RED)
            VGroup(s1, s2, s3, s4).set_x(0).arrange(buff=1.9).shift(UP)
            VGroup(s5, s6, s7, s8).set_x(0).arrange(buff=1.9).shift(2 * DOWN)
            t1 = Text("FadeIn").scale(0.5).next_to(s1, UP)
            t2 = Text("FadeInFromPoint").scale(0.5).next_to(s2, UP)
            t3 = Text("FadeInFrom").scale(0.5).next_to(s3, UP)
            t4 = Text("VFadeIn").scale(0.5).next_to(s4, UP)
            t5 = Text("FadeInFromLarge").scale(0.4).next_to(s5, UP)
            t6 = Text("FadeOut").scale(0.45).next_to(s6, UP)
            t7 = Text("FadeOutAndShift").scale(0.45).next_to(s7, UP)
            t8 = Text("VFadeOut").scale(0.45).next_to(s8, UP)

            objs = [ManimBanner().scale(0.25) for _ in range(1, 9)]
            objs[0].move_to(s1.get_center())
            objs[1].move_to(s2.get_center())
            objs[2].move_to(s3.get_center())
            objs[3].move_to(s4.get_center())
            objs[4].move_to(s5.get_center())
            objs[5].move_to(s6.get_center())
            objs[6].move_to(s7.get_center())
            objs[7].move_to(s8.get_center())
            self.add(s1, s2, s3, s4, s5, s6, s7, s8, t1, t2, t3, t4, t5, t6, t7, t8)
            self.add(*objs)

            self.play(
                FadeIn(objs[0]),
                FadeInFromPoint(objs[1], s2.get_center()),
                FadeInFrom(objs[2], LEFT*0.2),
                VFadeIn(objs[3]),
                FadeInFromLarge(objs[4]),
            )
            self.wait(0.3)
            self.play(
                FadeOut(objs[5]),
                FadeOutAndShift(objs[6], DOWN),
                VFadeOut(objs[7])
            )

"""


__all__ = [
    "FadeOut",
    "FadeIn",
    "FadeInFrom",
    "FadeOutAndShift",
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
    """A transform fading out the given mobject."""

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
            start.set_stroke(opacity=0)
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


class FadeInFromPoint(FadeIn):
    def __init__(
        self, mobject: "Mobject", point: typing.Union["Mobject", np.ndarray], **kwargs
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
        self, submobject: "Mobject", starting_submobject: "Mobject", alpha: float
    ) -> None:
        submobject.set_stroke(
            opacity=interpolate(0, starting_submobject.get_stroke_opacity(), alpha)
        )
        submobject.set_fill(
            opacity=interpolate(0, starting_submobject.get_fill_opacity(), alpha)
        )


class VFadeOut(VFadeIn):
    def __init__(self, mobject: "Mobject", remover: bool = True, **kwargs) -> None:
        super().__init__(mobject, remover=remover, **kwargs)

    def interpolate_submobject(
        self, submobject: "Mobject", starting_submobject: "Mobject", alpha: float
    ) -> None:
        super().interpolate_submobject(submobject, starting_submobject, 1 - alpha)


class VFadeInThenOut(VFadeIn):
    def __init__(
        self,
        mobject: "Mobject",
        remover: bool = True,
        rate_func: typing.Callable[[float, float], float] = there_and_back,
        **kwargs
    ):
        super().__init__(mobject, remover=remover, rate_func=rate_func, **kwargs)
