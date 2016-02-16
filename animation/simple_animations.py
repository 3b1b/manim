import numpy as np
import itertools as it

from helpers import *

from mobject import Mobject
from animation import Animation


class Rotating(Animation):
    DEFAULT_CONFIG = {
        "axes"       : [RIGHT, UP],
        "axis"       : None,
        "radians"    : 2*np.pi,
        "run_time"   : 20.0,
        "rate_func"  : None,
        "in_place"   : True,
    }
    def update_mobject(self, alpha):
        axes = [self.axis] if self.axis is not None else self.axes
        families = [
            self.mobject.submobject_family(),
            self.starting_mobject.submobject_family()
        ]
        for mob, start in zip(*families):
            mob.points = np.array(start.points)
        if self.in_place:
            method = self.mobject.rotate_in_place
        else:
            method = self.mobject.rotate           
        method(alpha*self.radians, axes = axes)     


class ShowPartial(Animation):
    def update_mobject(self, alpha):
        pairs = zip(
            self.starting_mobject.submobject_family(),
            self.mobject.submobject_family()
        )
        for start, mob in pairs:
            lower_alpha, upper_alpha = self.get_bounds(alpha)
            lower_index, upper_index = [
                int(a * start.get_num_points())
                for a in lower_alpha, upper_alpha
            ]
            for attr in mob.get_array_attrs():
                full_array = getattr(start, attr)
                partial_array = full_array[lower_index:upper_index]
                setattr(mob, attr, partial_array)

    def get_bounds(self, alpha):
        raise Exception("Not Implemented")


class ShowCreation(ShowPartial):
    def get_bounds(self, alpha):
        return (0, alpha)

class ShowPassingFlash(ShowPartial):
    DEFAULT_CONFIG = {
        "time_width" : 0.1
    }
    def get_bounds(self, alpha):
        alpha *= (1+self.time_width)
        alpha -= self.time_width/2
        lower = max(0, alpha - self.time_width/2)
        upper = min(1, alpha + self.time_width/2)
        return (lower, upper)




class Flash(Animation):
    DEFAULT_CONFIG = {
        "color" : "white",
        "slow_factor" : 0.01,
        "run_time" : 0.1,
        "rate_func" : None,
    }
    def __init__(self, mobject, **kwargs):
        self.intermediate = Mobject(color = self.color)
        self.intermediate.add_points([
            point + (x, y, 0)
            for point in self.mobject.points
            for x in [-1, 1]
            for y in [-1, 1]
        ])
        Animation.__init__(self, mobject, **kwargs)        

    def update_mobject(self, alpha):
        #Makes alpha go from 0 to slow_factor to 0 instead of 0 to 1
        alpha = self.slow_factor * (1.0 - 4 * (alpha - 0.5)**2)
        self.mobject.interpolate(
            self.starting_mobject, 
            self.intermediate, 
            alpha
        )

class Homotopy(Animation):
    def __init__(self, homotopy, mobject, **kwargs):
        """
        Homotopy a function from (x, y, z, t) to (x', y', z')
        """
        digest_config(self, kwargs, locals())
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        self.mobject.points = np.array([
            self.homotopy((x, y, z, alpha))
            for x, y, z in self.starting_mobject.points
        ])

class PhaseFlow(Animation):
    DEFAULT_CONFIG = {
        "virtual_time" : 1
    }
    def __init__(self, function, mobject, **kwargs):
        digest_config(self, kwargs, locals())        
        self.get_nudge_func = lambda alpha_diff : \
            lambda point : point + alpha_diff*function(point)
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        if hasattr(self, "last_alpha"):
            nudge = self.virtual_time*(alpha-self.last_alpha)
            self.mobject.apply_function(
                self.get_nudge_func(nudge)
            )
        self.last_alpha = alpha

### Animation modifiers ###

class ApplyToCenters(Animation):
    def __init__(self, AnimationClass, mobjects, **kwargs):
        centers = [mob.get_center() for mob in mobjects]
        kwargs["mobject"] = Mobject().add_points(centers)
        self.centers_container = AnimationClass(**kwargs)
        kwargs.pop("mobject")
        Animation.__init__(self, Mobject(*mobjects), **kwargs)
        self.name = str(self) + AnimationClass.__name__

    def update_mobject(self, alpha):
        self.centers_container.update_mobject(alpha)
        points = self.centers_container.mobject.points
        mobjects = self.mobject.split()        
        for point, mobject in zip(points, mobjects):
            mobject.center().shift(point)



class DelayByOrder(Animation):
    """
    Modifier of animation.

    Warning: This will not work on all animation types.
    """
    DEFAULT_CONFIG = {
        "max_power" : 5
    }
    def __init__(self, animation, **kwargs):
        digest_locals(self)
        self.num_mobject_points = animation.mobject.get_num_points()        
        kwargs.update(dict([
            (attr, getattr(animation, attr))
            for attr in Animation.DEFAULT_CONFIG
        ]))
        Animation.__init__(self, animation.mobject, **kwargs)
        self.name = str(self) + str(self.animation)

    def update_mobject(self, alpha):
        dim = self.mobject.DIM
        alpha_array = np.array([
            [alpha**power]*dim
            for n in range(self.num_mobject_points)
            for prop in [(n+1.0)/self.num_mobject_points]
            for power in [1+prop*(self.max_power-1)]
        ])
        self.animation.update_mobject(alpha_array)


class Succession(Animation):
    def __init__(self, *animations, **kwargs):
        if "run_time" in kwargs:
            run_time = kwargs.pop("run_time")
        else:
            run_time = sum([anim.run_time for anim in animations])
        self.num_anims = len(animations)
        self.anims = animations
        mobject = animations[0].mobject
        Animation.__init__(self, mobject, run_time = run_time, **kwargs)

    def __str__(self):
        return self.__class__.__name__ + \
               "".join(map(str, self.anims))

    def update(self, alpha):
        scaled_alpha = alpha*self.num_anims
        self.mobject = self.anims
        for index in range(len(self.anims)):
            self.anims[index].update(scaled_alpha - index)


