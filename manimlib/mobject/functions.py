from manimlib.constants import *
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
import math


class ParametricFunction(VMobject):
    CONFIG = {
        "t_min": 0,
        "t_max": 1,
        "step_size": 0.01,  # Use "auto" (lowercase) for automatic step size
        "dt": 1e-8,
        # TODO, be smarter about figuring these out?
        "discontinuities": [],
    }

    def __init__(self, function=None, **kwargs):
        # either get a function from __init__ or from CONFIG
        self.function = function or self.function
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

        discontinuities = filter(
            lambda t: t_min <= t <= t_max,
            self.discontinuities
        )
        discontinuities = np.array(list(discontinuities))
        boundary_times = [
            self.t_min, self.t_max,
            *(discontinuities - dt),
            *(discontinuities + dt),
        ]
        boundary_times.sort()
        for t1, t2 in zip(boundary_times[0::2], boundary_times[1::2]):
            t_range = list(np.arange(t1, t2, self.get_step_size(t1)))
            if t_range[-1] != t2:
                t_range.append(t2)
            points = np.array([self.function(t) for t in t_range])
            valid_indices = np.apply_along_axis(
                np.all, 1, np.isfinite(points)
            )
            points = points[valid_indices]
            if len(points) > 0:
                self.start_new_path(points[0])
                self.add_points_as_corners(points[1:])
        self.make_smooth()
        return self


class FunctionGraph(ParametricFunction):
    CONFIG = {
        "color": YELLOW,
        "x_min": -FRAME_X_RADIUS,
        "x_max": FRAME_X_RADIUS,
    }

    def __init__(self, function, **kwargs):
        digest_config(self, kwargs)
        self.parametric_function = \
            lambda t: np.array([t, function(t), 0])
        ParametricFunction.__init__(
            self,
            self.parametric_function,
            t_min=self.x_min,
            t_max=self.x_max,
            **kwargs
        )
        self.function = function

    def get_function(self):
        return self.function

    def get_point_from_function(self, x):
        return self.parametric_function(x)
