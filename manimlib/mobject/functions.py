from manimlib.constants import *
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config


class ParametricFunction(VMobject):
    CONFIG = {
        "t_min": 0,
        "t_max": 1,
        "num_anchor_points": 100,
    }

    def __init__(self, function, **kwargs):
        self.function = function
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        n_points = 3 * self.num_anchor_points - 2
        self.points = np.zeros((n_points, self.dim))
        self.points[:, 0] = np.linspace(
            self.t_min, self.t_max, n_points
        )
        # VMobject.apply_function takes care of preserving
        # desirable tangent line properties at anchor points
        self.apply_function(lambda p: self.function(p[0]))


class FunctionGraph(ParametricFunction):
    CONFIG = {
        "color": YELLOW,
        "x_min": -FRAME_X_RADIUS,
        "x_max": FRAME_X_RADIUS,
    }

    def __init__(self, function, **kwargs):
        digest_config(self, kwargs)

        def parametric_function(t):
            return t * RIGHT + function(t) * UP
        ParametricFunction.__init__(
            self,
            parametric_function,
            t_min=self.x_min,
            t_max=self.x_max,
            **kwargs
        )
        self.function = function

    def get_function(self):
        return self.function
