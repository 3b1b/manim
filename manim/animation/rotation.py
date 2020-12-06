"""Animations related to rotation."""

__all__ = ["Rotating", "Rotate"]

import typing

import numpy as np

from ..animation.animation import Animation
from ..animation.transform import Transform
from ..constants import OUT, PI, TAU
from ..utils.rate_functions import linear

if typing.TYPE_CHECKING:
    from ..mobject.mobject import Mobject


class Rotating(Animation):
    def __init__(
        self,
        mobject: "Mobject",
        axis: typing.Optional[np.ndarray] = OUT,
        radians: typing.Optional[np.ndarray] = TAU,
        about_point: typing.Optional[np.ndarray] = None,
        about_edge: typing.Optional[np.ndarray] = None,
        run_time: typing.Optional[float] = 5,
        rate_func: typing.Callable[
            [typing.Union[np.ndarray, float]], typing.Union[np.ndarray, float]
        ] = linear,
        **kwargs
    ) -> None:
        self.axis = axis
        self.radians = radians
        self.about_point = about_point
        self.about_edge = about_edge
        super().__init__(mobject, run_time=run_time, rate_func=rate_func, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        self.mobject.become(self.starting_mobject)
        self.mobject.rotate(
            alpha * self.radians,
            axis=self.axis,
            about_point=self.about_point,
            about_edge=self.about_edge,
        )


class Rotate(Transform):
    def __init__(
        self,
        mobject: "Mobject",
        angle: typing.Optional[np.ndarray] = PI,
        axis: typing.Optional[np.ndarray] = OUT,
        about_point: typing.Optional[np.ndarray] = None,
        about_edge: typing.Optional[np.ndarray] = None,
        **kwargs
    ) -> None:
        if "path_arc" not in kwargs:
            kwargs["path_arc"] = angle
        if "path_arc_axis" not in kwargs:
            kwargs["path_arc_axis"] = axis
        self.angle = angle
        self.axis = axis
        self.about_edge = about_edge
        self.about_point = about_point
        super().__init__(mobject, **kwargs)

    def create_target(self) -> "Mobject":
        target = self.mobject.copy()
        target.rotate(
            self.angle,
            axis=self.axis,
            about_point=self.about_point,
            about_edge=self.about_edge,
        )
        return target
