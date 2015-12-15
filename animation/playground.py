import numpy as np

from animation import Animation
from transform import Transform
from mobject import Mobject1D

from helpers import *

class VibratingString(Animation):
    DEFAULT_CONFIG = {
        "num_periods" : 1,
        "overtones" : 4,
        "amplitude" : 0.5,
        "radius" : SPACE_WIDTH/2,
        "center" : ORIGIN,
        "color" : "white",
        "run_time" : 3.0,
        "alpha_func" : None
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        def func(x, t):
            return sum([
                (self.amplitude/((k+1)**2.5))*np.sin(2*mult*t)*np.sin(k*mult*x)
                for k in range(self.overtones)
                for mult in [(self.num_periods+k)*np.pi]
            ])
        self.func = func
        Animation.__init__(self, Mobject1D(color = self.color), **kwargs)

    def update_mobject(self, alpha):
        self.mobject.init_points()
        epsilon = self.mobject.epsilon
        self.mobject.add_points([
            [x*self.radius, self.func(x, alpha*self.run_time)+y, 0]
            for x in np.arange(-1, 1, epsilon/self.radius)
            for y in epsilon*np.arange(3)
        ])
        self.mobject.shift(self.center)


class TurnInsideOut(Transform):
    DEFAULT_CONFIG = {
        "interpolation_function" : path_along_arc(np.pi/2)
    }
    def __init__(self, mobject, **kwargs):
        mobject.sort_points(np.linalg.norm)
        mob_copy = mobject.copy()
        mob_copy.sort_points(lambda p : -np.linalg.norm(p))
        Transform.__init__(self, mobject, mob_copy, **kwargs)


