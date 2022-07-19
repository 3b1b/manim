from __future__ import annotations

from manimlib.animation.animation import Animation
from manimlib.constants import ORIGIN, OUT
from manimlib.constants import PI, TAU
from manimlib.utils.rate_functions import linear
from manimlib.utils.rate_functions import smooth

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

    from manimlib.mobject.mobject import Mobject


class Rotating(Animation):
    CONFIG = {
        # "axis": OUT,
        # "radians": TAU,
        "run_time": 5,
        "rate_func": linear,
        "about_point": None,
        "about_edge": None,
        "suspend_mobject_updating": False,
    }

    def __init__(
        self,
        mobject: Mobject,
        angle: float = TAU,
        axis: np.ndarray = OUT,
        **kwargs
    ):
        self.angle = angle
        self.axis = axis
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        for sm1, sm2 in self.get_all_families_zipped():
            sm1.set_points(sm2.get_points())
        self.mobject.rotate(
            alpha * self.angle,
            axis=self.axis,
            about_point=self.about_point,
            about_edge=self.about_edge,
        )


class Rotate(Rotating):
    CONFIG = {
        "run_time": 1,
        "rate_func": smooth,
        "about_edge": ORIGIN,
    }

    def __init__(
        self,
        mobject: Mobject,
        angle: float = PI,
        axis: np.ndarray = OUT,
        **kwargs
    ):
        super().__init__(mobject, angle, axis, **kwargs)
