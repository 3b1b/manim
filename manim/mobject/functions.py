"""Mobjects representing function graphs."""

__all__ = ["ParametricFunction", "FunctionGraph"]


from .. import config
from ..constants import *
from ..mobject.types.vectorized_mobject import VMobject
from ..utils.color import YELLOW

import math


class ParametricFunction(VMobject):
    """A parametric curve.

    Examples
    --------

    .. manim:: PlotParametricFunction
        :save_last_frame:

        class PlotParametricFunction(Scene):
            def func(self, t):
                return np.array((np.sin(2 * t), np.sin(3 * t), 0))

            def construct(self):
                func = ParametricFunction(self.func, t_max = TAU, fill_opacity=0).set_color(RED)
                self.add(func.scale(3))

    .. manim:: ThreeDParametricSpring
        :save_last_frame:

        class ThreeDParametricSpring(ThreeDScene):
            def construct(self):
                curve1 = ParametricFunction(
                    lambda u: np.array([
                        1.2 * np.cos(u),
                        1.2 * np.sin(u),
                        u * 0.05
                    ]), color=RED, t_min=-3 * TAU, t_max=5 * TAU,
                ).set_shade_in_3d(True)
                axes = ThreeDAxes()
                self.add(axes, curve1)
                self.set_camera_orientation(phi=80 * DEGREES, theta=-60 * DEGREES)
                self.wait()
    """

    def __init__(
        self,
        function=None,
        t_min=0,
        t_max=1,
        step_size=0.01,
        dt=1e-8,
        discontinuities=None,
        **kwargs
    ):
        self.function = function
        self.t_min = t_min
        self.t_max = t_max
        self.step_size = step_size
        self.dt = dt
        self.discontinuities = [] if discontinuities is None else discontinuities
        VMobject.__init__(self, **kwargs)

    def get_function(self):
        return self.function

    def get_point_from_function(self, t):
        return self.function(t)

    def get_step_size(self, t=None):
        if self.step_size == "auto":
            """
            for x between -1 to 1, return 0.01
            else, return log10(x) (rounded)
            e.g.: 10.5 -> 0.1 ; 1040 -> 10
            """
            if t == 0:
                scale = 0
            else:
                scale = math.log10(abs(t))
                if scale < 0:
                    scale = 0

                scale = math.floor(scale)

            scale -= 2
            return math.pow(10, scale)
        else:
            return self.step_size

    def generate_points(self):
        t_min, t_max = self.t_min, self.t_max
        dt = self.dt

        discontinuities = filter(lambda t: t_min <= t <= t_max, self.discontinuities)
        discontinuities = np.array(list(discontinuities))
        boundary_times = [
            self.t_min,
            self.t_max,
            *(discontinuities - dt),
            *(discontinuities + dt),
        ]
        boundary_times.sort()
        for t1, t2 in zip(boundary_times[0::2], boundary_times[1::2]):
            t_range = list(np.arange(t1, t2, self.get_step_size(t1)))
            if t_range[-1] != t2:
                t_range.append(t2)
            points = np.array([self.function(t) for t in t_range])
            valid_indices = np.apply_along_axis(np.all, 1, np.isfinite(points))
            points = points[valid_indices]
            if len(points) > 0:
                self.start_new_path(points[0])
                self.add_points_as_corners(points[1:])
        self.make_smooth()
        return self


class FunctionGraph(ParametricFunction):
    def __init__(self, function, x_min=None, x_max=None, color=YELLOW, **kwargs):
        if x_min is None:
            x_min = -config["frame_x_radius"]
        if x_max is None:
            x_max = config["frame_x_radius"]
        self.x_min = x_min
        self.x_max = x_max
        self.parametric_function = lambda t: np.array([t, function(t), 0])
        ParametricFunction.__init__(
            self,
            self.parametric_function,
            t_min=self.x_min,
            t_max=self.x_max,
            color=color,
            **kwargs
        )
        self.function = function

    def get_function(self):
        return self.function

    def get_point_from_function(self, x):
        return self.parametric_function(x)
