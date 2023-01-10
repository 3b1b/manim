from __future__ import annotations

from isosurfaces import plot_isoline
import numpy as np

from manimlib.constants import FRAME_X_RADIUS, FRAME_Y_RADIUS
from manimlib.constants import YELLOW
from manimlib.mobject.types.vectorized_mobject import VMobject

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Sequence, Tuple
    from manimlib.typing import ManimColor, Vect3


class ParametricCurve(VMobject):
    def __init__(
        self,
        t_func: Callable[[float], Sequence[float] | Vect3],
        t_range: Tuple[float, float, float] = (0, 1, 0.1),
        epsilon: float = 1e-8,
        # TODO, automatically figure out discontinuities
        discontinuities: Sequence[float] = [],
        use_smoothing: bool = True,
        **kwargs
    ):
        self.t_func = t_func
        self.t_range = t_range
        self.epsilon = epsilon
        self.discontinuities = discontinuities
        self.use_smoothing = use_smoothing
        super().__init__(**kwargs)

    def get_point_from_function(self, t: float) -> Vect3:
        return np.array(self.t_func(t))

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
            self.set_points(np.array([self.t_func(t_min)]))
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
    def __init__(
        self,
        function: Callable[[float], float],
        x_range: Tuple[float, float, float] = (-8, 8, 0.25),
        color: ManimColor = YELLOW,
        **kwargs
    ):
        self.function = function
        self.x_range = x_range

        def parametric_function(t):
            return [t, function(t), 0]

        super().__init__(parametric_function, self.x_range, **kwargs)


class ImplicitFunction(VMobject):
    def __init__(
        self,
        func: Callable[[float, float], float],
        x_range: Tuple[float, float] = (-FRAME_X_RADIUS, FRAME_X_RADIUS),
        y_range: Tuple[float, float] = (-FRAME_Y_RADIUS, FRAME_Y_RADIUS),
        min_depth: int = 5,
        max_quads: int = 1500,
        use_smoothing: bool = True,
        joint_type: str = 'no_joint',
        **kwargs
    ):
        super().__init__(joint_type=joint_type, **kwargs)

        p_min, p_max = (
            np.array([x_range[0], y_range[0]]),
            np.array([x_range[1], y_range[1]]),
        )
        curves = plot_isoline(
            fn=lambda u: func(u[0], u[1]),
            pmin=p_min,
            pmax=p_max,
            min_depth=min_depth,
            max_quads=max_quads,
        )  # returns a list of lists of 2D points
        curves = [
            np.pad(curve, [(0, 0), (0, 1)]) for curve in curves if curve != []
        ]  # add z coord as 0
        for curve in curves:
            self.start_new_path(curve[0])
            self.add_points_as_corners(curve[1:])
        if use_smoothing:
            self.make_smooth()
