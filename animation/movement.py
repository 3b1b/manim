from constants import *

from animation.animation import Animation
from utils.config_ops import digest_config


class Homotopy(Animation):
    CONFIG = {
        "run_time": 3,
        "apply_function_kwargs": {},
    }

    def __init__(self, homotopy, mobject, **kwargs):
        """
        Homotopy a function from (x, y, z, t) to (x', y', z')
        """
        def function_at_time_t(t):
            return lambda p: homotopy(p[0], p[1], p[2], t)
        self.function_at_time_t = function_at_time_t
        digest_config(self, kwargs)
        Animation.__init__(self, mobject, **kwargs)

    def update_submobject(self, submob, start, alpha):
        submob.points = start.points
        submob.apply_function(
            self.function_at_time_t(alpha),
            **self.apply_function_kwargs
        )


class SmoothedVectorizedHomotopy(Homotopy):
    def update_submobject(self, submob, start, alpha):
        Homotopy.update_submobject(self, submob, start, alpha)
        submob.make_smooth()


class ComplexHomotopy(Homotopy):
    def __init__(self, complex_homotopy, mobject, **kwargs):
        """
        Complex Hootopy a function Cx[0, 1] to C
        """
        def homotopy(x, y, z, t):
            c = complex_homotopy(complex(x, y), t)
            return (c.real, c.imag, z)
        Homotopy.__init__(self, homotopy, mobject, **kwargs)


class PhaseFlow(Animation):
    CONFIG = {
        "virtual_time": 1,
        "rate_func": None,
    }

    def __init__(self, function, mobject, **kwargs):
        digest_config(self, kwargs, locals())
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        if hasattr(self, "last_alpha"):
            dt = self.virtual_time * (alpha - self.last_alpha)
            self.mobject.apply_function(
                lambda p: p + dt * self.function(p)
            )
        self.last_alpha = alpha


class MoveAlongPath(Animation):
    def __init__(self, mobject, path, **kwargs):
        digest_config(self, kwargs, locals())
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        point = self.path.point_from_proportion(alpha)
        self.mobject.move_to(point)
