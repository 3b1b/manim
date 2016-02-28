import numpy as np
import operator as op

from animation import Animation
from transform import Transform
from mobject import Mobject1D, Mobject
from topics.geometry import Line

from helpers import *

class Vibrate(Animation):
    CONFIG = {
        "spatial_period"  : 6,
        "temporal_period" : 1,
        "overtones"       : 4,
        "amplitude"       : 0.5,
        "radius"          : SPACE_WIDTH/2,
        "run_time"        : 3.0,
        "rate_func"      : None
    }
    def __init__(self, mobject = None, **kwargs):
        if mobject is None:
            mobject = Line(3*LEFT, 3*RIGHT)
        Animation.__init__(self, mobject, **kwargs)

    def wave_function(self, x, t):
        return sum([
            reduce(op.mul, [
                self.amplitude/(k**2), #Amplitude
                np.sin(2*np.pi*(k**1.5)*t/self.temporal_period), #Frequency
                np.sin(2*np.pi*k*x/self.spatial_period) #Number of waves
            ])
            for k in range(1, self.overtones+1)
        ])


    def update_mobject(self, alpha):
        time = alpha*self.run_time
        families = map(
            Mobject.submobject_family,
            [self.mobject, self.starting_mobject]
        )
        for mob, start in zip(*families):
            mob.points = np.apply_along_axis(
                lambda (x, y, z) : (x, y + self.wave_function(x, time), z),
                1, start.points
            )


class TurnInsideOut(Transform):
    CONFIG = {
        "path_func" : path_along_arc(np.pi/2)
    }
    def __init__(self, mobject, **kwargs):
        mobject.sort_points(np.linalg.norm)
        mob_copy = mobject.copy()
        mob_copy.sort_points(lambda p : -np.linalg.norm(p))
        Transform.__init__(self, mobject, mob_copy, **kwargs)


