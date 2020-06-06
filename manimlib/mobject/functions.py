from manimlib.constants import *
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.space_ops import get_norm


class ParametricCurve(VMobject):
    CONFIG = {
        "t_min": 0,
        "t_max": 1,
        "step_size": 0.2,
        "min_samples": 8,
        "dt": 1e-8,
        # TODO, automatically figure out discontinuities
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

    def init_points(self):
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
            # Get an initial sample of points
            t_range = list(np.linspace(t1, t2, self.min_samples + 1))
            samples = [self.function(t) for t in t_range]

            # Take more samples based on the distances between them
            norms = [get_norm(p2 - p1) for p1, p2 in zip(samples, samples[1:])]
            full_t_range = [t1]
            for s1, s2, norm in zip(t_range, t_range[1:], norms):
                n_inserts = int(norm / self.step_size)
                full_t_range += list(np.linspace(s1, s2, n_inserts + 1)[1:])

            points = np.array([self.function(t) for t in full_t_range])
            valid_indices = np.isfinite(points).all(1)
            points = points[valid_indices]
            if len(points) > 0:
                self.start_new_path(points[0])
                self.add_points_as_corners(points[1:])
        self.make_smooth()
        return self


class FunctionGraph(ParametricCurve):
    CONFIG = {
        "color": YELLOW,
        "x_min": -FRAME_X_RADIUS,
        "x_max": FRAME_X_RADIUS,
    }

    def __init__(self, function, **kwargs):
        digest_config(self, kwargs)
        self.parametric_function = \
            lambda t: np.array([t, function(t), 0])
        ParametricCurve.__init__(
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
