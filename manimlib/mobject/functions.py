from manimlib.constants import *
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.space_ops import get_norm


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
        # TODO, this seems like a mess.
        t_min, t_max, step = self.t_range
        epsilon = self.epsilon

        discontinuities = filter(
            lambda t: t_min <= t <= t_max,
            self.discontinuities
        )
        discontinuities = np.array(list(discontinuities))
        boundary_times = [
            t_min, t_max,
            *(discontinuities - epsilon),
            *(discontinuities + epsilon),
        ]
        boundary_times.sort()
        for t1, t2 in zip(boundary_times[0::2], boundary_times[1::2]):
            # Get an initial sample of points
            t_range = list(np.linspace(t1, t2, self.min_samples + 1))
            samples = np.array([self.t_func(t) for t in t_range])

            # Take more samples based on the distances between them
            norms = [get_norm(p2 - p1) for p1, p2 in zip(samples, samples[1:])]
            full_t_range = [t1]
            for s1, s2, norm in zip(t_range, t_range[1:], norms):
                n_inserts = int(norm / step)
                full_t_range += list(np.linspace(s1, s2, n_inserts + 1)[1:])

            points = np.array([self.t_func(t) for t in full_t_range])
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
        "x_range": [-8, 8, 0.5],
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
