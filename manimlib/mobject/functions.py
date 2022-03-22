from __future__ import annotations

from typing import Callable, Sequence

from isosurfaces import plot_isoline

from manimlib.constants import *
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config


class ParametricCurve(VMobject):
    CONFIG = {
        "t_range": [0, 1, 0.1],
        "epsilon": 1e-8,
        # TODO, automatically figure out discontinuities
        "discontinuities": [],
        "use_smoothing": True,
    }

    def __init__(
        self,
        t_func: Callable[[float], np.ndarray],
        t_range: Sequence[float] | None = None,
        **kwargs
    ):
        digest_config(self, kwargs)
        if t_range is not None:
            self.t_range[:len(t_range)] = t_range
        # To be backward compatible with all the scenes specifying t_min, t_max, step_size
        self.t_range = [
            kwargs.get("t_min", self.t_range[0]),
            kwargs.get("t_max", self.t_range[1]),
            kwargs.get("step_size", self.t_range[2]),
        ]
        self.t_func = t_func
        VMobject.__init__(self, **kwargs)

    def get_point_from_function(self, t: float) -> np.ndarray:
        return self.t_func(t)

    def init_points(self):
        t_min, t_max, step = self.t_range

        jumps = np.array(self.discontinuities)
        jumps = jumps[(jumps > t_min) & (jumps < t_max)]
        boundary_times = [t_min, t_max, *(jumps - self.epsilon), *(jumps + self.epsilon)]
        boundary_times.sort()
        for t1, t2 in zip(boundary_times[0::2], boundary_times[1::2]):
            t_range = [*np.arange(t1, t2, step), t2]
            points = np.array([self.t_func(t) for t in t_range])
            self.start_new_path(points[0])
            self.add_points_as_corners(points[1:])
        if self.use_smoothing:
            self.make_approximately_smooth()
        if not self.has_points():
            self.set_points([self.t_func(t_min)])
        return self

    def get_t_func(self):
        return self.t_func

    def get_function(self):
        if hasattr(self, "underlying_function"):
            return self.underlying_function
        if hasattr(self, "function"):
            return self.function

    def get_x_range(self):
        if hasattr(self, "x_range"):
            return self.x_range

class FunctionGraph(ParametricCurve):
    CONFIG = {
        "color": YELLOW,
        "x_range": [-8, 8, 0.25],
    }

    def __init__(
        self,
        function: Callable[[float], float],
        x_range: Sequence[float] | None = None,
        **kwargs
    ):
        digest_config(self, kwargs)
        self.function = function

        if x_range is not None:
            self.x_range[:len(x_range)] = x_range

        def parametric_function(t):
            return [t, function(t), 0]

        super().__init__(parametric_function, self.x_range, **kwargs)


class ImplicitFunction(VMobject):
    CONFIG = {
        "x_range": [-FRAME_X_RADIUS, FRAME_X_RADIUS],
        "y_range": [-FRAME_Y_RADIUS, FRAME_Y_RADIUS],
        "min_depth": 5,
        "max_quads": 1500,
        "use_smoothing": True
    }

    def __init__(
        self,
        func: Callable[[float, float], float],
        **kwargs
    ):
        digest_config(self, kwargs)
        self.function = func
        super().__init__(**kwargs)

    def init_points(self):
        p_min, p_max = (
            np.array([self.x_range[0], self.y_range[0]]),
            np.array([self.x_range[1], self.y_range[1]]),
        )
        curves = plot_isoline(
            fn=lambda u: self.function(u[0], u[1]),
            pmin=p_min,
            pmax=p_max,
            min_depth=self.min_depth,
            max_quads=self.max_quads,
        )  # returns a list of lists of 2D points
        curves = [
            np.pad(curve, [(0, 0), (0, 1)]) for curve in curves if curve != []
        ]  # add z coord as 0
        for curve in curves:
            self.start_new_path(curve[0])
            self.add_points_as_corners(curve[1:])
        if self.use_smoothing:
            self.make_smooth()
        return self
