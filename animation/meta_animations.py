import numpy as np
import itertools as it

from helpers import *
from animation import Animation
from transform import Transform


class DelayByOrder(Animation):
    """
    Modifier of animation.

    Warning: This will not work on all animation types, but 
    when it does, it will be pretty cool
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
        self.name = self.__class__.__name__ + str(self.animation)

    def update_mobject(self, alpha):
        dim = self.mobject.DIM
        alpha_array = np.array([
            [alpha**power]*dim
            for n in range(self.num_mobject_points)
            for prop in [(n+1.0)/self.num_mobject_points]
            for power in [1+prop*(self.max_power-1)]
        ])
        self.animation.update_mobject(alpha_array)



class TransformAnimations(Transform):
    DEFAULT_CONFIG = {
        "alpha_func" : squish_alpha_func(smooth)
    }
    def __init__(self, start_anim, end_anim, **kwargs):
        if "run_time" in kwargs:
            self.run_time = kwargs.pop("run_time")
        else:
            self.run_time = max(start_anim.run_time, end_anim.run_time)
        for anim in start_anim, end_anim:
            anim.set_run_time(self.run_time)
            
        if start_anim.starting_mobject.get_num_points() != end_anim.starting_mobject.get_num_points():
            Mobject.align_data(start_anim.starting_mobject, end_anim.starting_mobject)
            for anim in start_anim, end_anim:
                if hasattr(anim, "ending_mobject"):
                    Mobject.align_data(anim.starting_mobject, anim.ending_mobject)

        Transform.__init__(self, start_anim.mobject, end_anim.mobject, **kwargs)
        #Rewire starting and ending mobjects
        start_anim.mobject = self.starting_mobject
        end_anim.mobject = self.ending_mobject

    def update(self, alpha):
        self.start_anim.update(alpha)
        self.end_anim.update(alpha)
        Transform.update(self, alpha)


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



       
