from __future__ import annotations

from typing import Callable, Sequence

from manimlib.animation.animation import Animation
from manimlib.utils.rate_functions import linear

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from manimlib.mobject.mobject import Mobject


class Homotopy(Animation):
    CONFIG = {
        "run_time": 3,
        "apply_function_kwargs": {},
    }

    def __init__(
        self,
        homotopy: Callable[[float, float, float, float], Sequence[float]],
        mobject: Mobject,
        **kwargs
    ):
        """
        Homotopy is a function from
        (x, y, z, t) to (x', y', z')
        """
        self.homotopy = homotopy
        super().__init__(mobject, **kwargs)

    def function_at_time_t(
        self,
        t: float
    ) -> Callable[[np.ndarray], Sequence[float]]:
        return lambda p: self.homotopy(*p, t)

    def interpolate_submobject(
        self,
        submob: Mobject,
        start: Mobject,
        alpha: float
    ) -> None:
        submob.match_points(start)
        submob.apply_function(
            self.function_at_time_t(alpha),
            **self.apply_function_kwargs
        )


class SmoothedVectorizedHomotopy(Homotopy):
    CONFIG = {
        "apply_function_kwargs": {"make_smooth": True},
    }


class ComplexHomotopy(Homotopy):
    def __init__(
        self,
        complex_homotopy: Callable[[complex, float], Sequence[float]],
        mobject: Mobject,
        **kwargs
    ):
        """
        Given a function form (z, t) -> w, where z and w
        are complex numbers and t is time, this animates
        the state over time
        """
        def homotopy(x, y, z, t):
            c = complex_homotopy(complex(x, y), t)
            return (c.real, c.imag, z)
        super().__init__(homotopy, mobject, **kwargs)


class PhaseFlow(Animation):
    CONFIG = {
        "virtual_time": 1,
        "rate_func": linear,
        "suspend_mobject_updating": False,
    }

    def __init__(
        self,
        function: Callable[[np.ndarray], np.ndarray],
        mobject: Mobject,
        **kwargs
    ):
        self.function = function
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        if hasattr(self, "last_alpha"):
            dt = self.virtual_time * (alpha - self.last_alpha)
            self.mobject.apply_function(
                lambda p: p + dt * self.function(p)
            )
        self.last_alpha = alpha


class MoveAlongPath(Animation):
    CONFIG = {
        "suspend_mobject_updating": False,
    }

    def __init__(self, mobject: Mobject, path: Mobject, **kwargs):
        self.path = path
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        point = self.path.point_from_proportion(alpha)
        self.mobject.move_to(point)
