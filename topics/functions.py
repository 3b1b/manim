from scipy import integrate

from mobject.vectorized_mobject import VMobject

from helpers import *

class FunctionGraph(VMobject):
    CONFIG = {
        "color" : YELLOW,
        "x_min" : -SPACE_WIDTH,
        "x_max" : SPACE_WIDTH,
        "num_steps" : 20,
    }
    def __init__(self, function, **kwargs):
        self.function = function
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        x_values = np.linspace(self.x_min, self.x_max, self.num_steps)
        y_values = self.function(x_values)
        okay_indices = np.isfinite(y_values)
        x_values = x_values[okay_indices]
        y_values = y_values[okay_indices]
        self.set_anchor_points([
            x*RIGHT + y*UP
            for x, y in zip(x_values, y_values)
        ], mode = "smooth")

    def get_function(self):
        return self.function


class ParametricFunction(VMobject):
    CONFIG = {
        "t_min" : 0,
        "t_max" : 1,
        "num_anchor_points" : 10,
    }
    def __init__(self, function, **kwargs):
        self.function = function
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        t_values = np.linspace(
            self.t_min, self.t_max, self.num_anchor_points
        )
        points = np.array(map(self.function, t_values))
        okay_indices = np.apply_along_axis(np.all, 1, np.isfinite(points))
        points = points[okay_indices]
        self.set_anchor_points(points, mode = "smooth")



        











