from scipy import integrate

from mobject import Mobject, Mobject1D, Mobject

from helpers import *

class FunctionGraph(Mobject1D):
    CONFIG = {
        "color" : BLUE,
        "x_min" : -10,
        "x_max" : 10,
        "spatial_radius" : SPACE_WIDTH,
    }
    def __init__(self, function, **kwargs):
        self.function = function
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        numerical_radius = (self.x_max - self.x_min)/2
        numerical_center = (self.x_max + self.x_min)/2
        ratio = numerical_radius / self.spatial_radius
        epsilon = self.epsilon * ratio
        self.add_points([
            np.array([(x-numerical_center)/ratio, self.function(x), 0])
            for x in np.arange(self.x_min, self.x_max, self.epsilon)
        ])


class ParametricFunction(Mobject1D):
    CONFIG = {
        "start" : 0,
        "end"   : 1,
    }
    def __init__(self, function, **kwargs):
        self.function = function
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        integral = integrate.quad(
            lambda t : np.linalg.norm(self.function(t)),
            self.start, self.end
        )
        length = np.linalg.norm(integral)
        epsilon = self.epsilon / length        
        t_range = np.arange(self.start, self.end, epsilon)
        self.add_points([self.function(t) for t in t_range])


class Axes(Mobject):
    def __init__(self, **kwargs):
        x_axis = NumberLine(**kwargs)
        y_axis = NumberLine(**kwargs).rotate(np.pi/2, OUT)
        Mobject.__init__(self, x_axis, y_axis)


        