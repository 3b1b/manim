from manimlib.constants import *
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config


class ParametricCurve(VMobject):
    CONFIG = {
        "t_range": [0, 1, 0.1],
        "min_samples": 10,
        "epsilon": 1e-8,
        # TODO, automatically figure out discontinuities
        "discontinuities": [],
    }

    def __init__(self, t_func, t_range=None, **kwargs):
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

    def get_point_from_function(self, t):
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
        self.make_smooth(true_smooth=False)
        return self


class FunctionGraph(ParametricCurve):
    CONFIG = {
        "color": YELLOW,
        "x_range": [-8, 8, 0.25],
    }

    def __init__(self, function, x_range=None, **kwargs):
        digest_config(self, kwargs)
        self.function = function

        if x_range is not None:
            self.x_range[:len(x_range)] = x_range

        def parametric_function(t):
            return [t, function(t), 0]

        super().__init__(parametric_function, self.x_range, **kwargs)

    def get_function(self):
        return self.function

    def get_point_from_function(self, x):
        return self.t_func(x)
