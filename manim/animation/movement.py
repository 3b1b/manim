"""Animations related to movement."""

__all__ = [
    "Homotopy",
    "SmoothedVectorizedHomotopy",
    "ComplexHomotopy",
    "PhaseFlow",
    "MoveAlongPath",
]


import typing

import numpy as np

from ..animation.animation import Animation
from ..utils.rate_functions import linear

if typing.TYPE_CHECKING:
    from ..mobject.mobject import Mobject


class Homotopy(Animation):
    def __init__(
        self,
        homotopy: typing.Callable[
            [float, float, float, float], typing.Tuple[float, float, float]
        ],
        mobject: "Mobject",
        run_time: typing.Optional[float] = 3,
        apply_function_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None,
        **kwargs
    ) -> None:
        """
        Homotopy is a function from
        (x, y, z, t) to (x', y', z')
        """
        self.homotopy = homotopy
        self.apply_function_kwargs = (
            apply_function_kwargs if apply_function_kwargs is not None else {}
        )
        super().__init__(mobject, run_time=run_time, **kwargs)

    def function_at_time_t(self, t: float) -> typing.Tuple[float, float, float]:
        return lambda p: self.homotopy(*p, t)

    def interpolate_submobject(
        self, submobject: "Mobject", starting_sumobject: "Mobject", alpha: float
    ) -> None:
        submobject.points = starting_sumobject.points
        submobject.apply_function(
            self.function_at_time_t(alpha), **self.apply_function_kwargs
        )


class SmoothedVectorizedHomotopy(Homotopy):
    def interpolate_submobject(
        self, submobject: "Mobject", starting_sumobject: "Mobject", alpha: float
    ) -> None:
        Homotopy.interpolate_submobject(self, submobject, starting_sumobject, alpha)
        submobject.make_smooth()


class ComplexHomotopy(Homotopy):
    def __init__(
        self,
        complex_homotopy: typing.Callable[[complex], float],
        mobject: "Mobject",
        **kwargs
    ) -> None:
        """
        Complex Hootopy a function Cx[0, 1] to C
        """

        def homotopy(
            x: float, y: float, z: float, t: float
        ) -> typing.Tuple[float, float, float]:
            c = complex_homotopy(complex(x, y), t)
            return (c.real, c.imag, z)

        Homotopy.__init__(self, homotopy, mobject, **kwargs)


class PhaseFlow(Animation):
    def __init__(
        self,
        function: typing.Callable[[np.ndarray], np.ndarray],
        mobject: "Mobject",
        virtual_time: typing.Optional[float] = 1,
        suspend_mobject_updating: typing.Optional[bool] = False,
        rate_func: typing.Optional[
            typing.Callable[
                [typing.Union[np.ndarray, float]], typing.Union[np.ndarray, float]
            ]
        ] = linear,
        **kwargs
    ) -> None:
        self.virtual_time = virtual_time
        self.function = function
        super().__init__(
            mobject,
            suspend_mobject_updating=suspend_mobject_updating,
            rate_func=rate_func,
            **kwargs
        )

    def interpolate_mobject(self, alpha: float) -> None:
        if hasattr(self, "last_alpha"):
            dt = self.virtual_time * (alpha - self.last_alpha)
            self.mobject.apply_function(lambda p: p + dt * self.function(p))
        self.last_alpha = alpha


class MoveAlongPath(Animation):
    def __init__(
        self,
        mobject: "Mobject",
        path: np.ndarray,
        suspend_mobject_updating: typing.Optional[bool] = False,
        **kwargs
    ) -> None:
        self.path = path
        super().__init__(
            mobject, suspend_mobject_updating=suspend_mobject_updating, **kwargs
        )

    def interpolate_mobject(self, alpha: float) -> None:
        point = self.path.point_from_proportion(alpha)
        self.mobject.move_to(point)
