import numpy as np
import itertools as it

from helpers import *

import warnings
from mobject import Mobject, Group
from mobject.vectorized_mobject import VMobject
from mobject.tex_mobject import TextMobject
from animation import Animation
from transform import Transform

class LaggedStart(Animation):
    CONFIG = {
        "run_time" : 2,
        "lag_ratio" : 0.5,
    }
    def __init__(self, AnimationClass, mobject, arg_creator = None, **kwargs):
        digest_config(self, kwargs)
        for key in "rate_func", "run_time", "lag_ratio":
            if key in kwargs:
                kwargs.pop(key)
        if arg_creator is None:
            arg_creator = lambda mobject : (mobject,)
        self.subanimations = [
            AnimationClass(
                *arg_creator(submob),
                run_time = self.run_time,
                rate_func = squish_rate_func(
                    self.rate_func, beta, beta + self.lag_ratio
                ),
                **kwargs
            )
            for submob, beta in zip(
                mobject, 
                np.linspace(0, 1-self.lag_ratio, len(mobject))
            )
        ]
        Animation.__init__(self, mobject, **kwargs)

    def update(self, alpha):
        for anim in self.subanimations:
            anim.update(alpha)
        return self

    def clean_up(self, *args, **kwargs):
        for anim in self.subanimations:
            anim.clean_up(*args, **kwargs)

class Succession(Animation):
    CONFIG = {
        "rate_func" : None,
    }
    def __init__(self, *args, **kwargs):
        """
        Each arg will either be an animation, or an animation class 
        followed by its arguments (and potentially a dict for 
        configuration).
        For example, 
        Succession(
            ShowCreation(circle),
            Transform, circle, square,
            Transform, circle, triangle,
            ApplyMethod, circle.shift, 2*UP, {"run_time" : 2},
        )
        """
        animations = []
        state = {
            "animations" : animations,
            "curr_class" : None,
            "curr_class_args" : [],
            "curr_class_config" : {},
        }
        def invoke_curr_class(state):
            if state["curr_class"] is None:
                return
            anim = state["curr_class"](
                *state["curr_class_args"], 
                **state["curr_class_config"]
            )
            state["animations"].append(anim)
            anim.update(1)
            state["curr_class"] = None
            state["curr_class_args"] = []
            state["curr_class_config"] = {}

        for arg in args:
            if isinstance(arg, Animation):
                animations.append(arg)
                arg.update(1)
                invoke_curr_class(state)
            elif isinstance(arg, type) and issubclass(arg, Animation):
                invoke_curr_class(state)
                state["curr_class"] = arg
            elif isinstance(arg, dict):
                state["curr_class_config"] = arg
            else:
                state["curr_class_args"].append(arg)
        invoke_curr_class(state)
        for anim in animations:
            anim.update(0)

        animations = filter (lambda x : not(x.empty), animations)

        self.run_times = [anim.run_time for anim in animations]
        if "run_time" in kwargs:
            run_time = kwargs.pop("run_time")
            warnings.warn("Succession doesn't currently support explicit run_time.")
        run_time = sum(self.run_times)
        self.num_anims = len(animations)
        if self.num_anims == 0:
            self.empty = True
        self.animations = animations
        #Have to keep track of this run_time, because Scene.play
        #might very well mess with it.
        self.original_run_time = run_time

        # critical_alphas[i] is the start alpha of self.animations[i]
        # critical_alphas[i + 1] is the end alpha of self.animations[i]
        critical_times = np.concatenate(([0], np.cumsum(self.run_times)))
        self.critical_alphas = map (lambda x : np.true_divide(x, run_time), critical_times) if self.num_anims > 0 else [0.0]

        # self.scene_mobjects_at_time[i] is the scene's mobjects at start of self.animations[i]
        # self.scene_mobjects_at_time[i + 1] is the scene mobjects at end of self.animations[i]
        self.scene_mobjects_at_time = [None for i in range(self.num_anims + 1)]
        self.scene_mobjects_at_time[0] = Group()
        for i in range(self.num_anims):
            self.scene_mobjects_at_time[i + 1] = self.scene_mobjects_at_time[i].copy()
            self.animations[i].clean_up(self.scene_mobjects_at_time[i + 1])

        self.current_alpha = 0
        self.current_anim_index = 0 # If self.num_anims == 0, this is an invalid index, but so it goes
        if self.num_anims > 0:
            self.mobject = self.scene_mobjects_at_time[0]
            self.mobject.add(self.animations[0].mobject)
        else:
            self.mobject = Group()

        Animation.__init__(self, self.mobject, run_time = run_time, **kwargs)

    # Beware: This does NOT take care of calling update(0) on the subanimation.
    # This was important to avoid a pernicious possibility in which subanimations were called
    # with update twice, which could in turn call a sub-Succession with update four times,
    # continuing exponentially.
    def jump_to_start_of_anim(self, index):
        if index != self.current_anim_index:
            self.mobject.remove(*self.mobject.submobjects) # Should probably have a cleaner "remove_all" method...
            self.mobject.add(*self.scene_mobjects_at_time[index].submobjects)
            self.mobject.add(self.animations[index].mobject)

        for i in range(index):
            self.animations[i].update(1)

        self.current_anim_index = index
        self.current_alpha = self.critical_alphas[index]

    def update_mobject(self, alpha):
        if self.num_anims == 0:
            # This probably doesn't matter for anything, but just in case,
            # we want it in the future, we set current_alpha even in this case
            self.current_alpha = alpha
            return

        gt_alpha_iter = it.ifilter(
            lambda i : self.critical_alphas[i+1] >= alpha, 
            range(self.num_anims)
        )
        i = next(gt_alpha_iter, None)
        if i == None:
            # In this case, we assume what is happening is that alpha is 1.0, 
            # but that rounding error is causing us to overshoot the end of
            # self.critical_alphas (which is also 1.0)
            if not abs(alpha - 1) < 0.001:
                warnings.warn(
                    "Rounding error not near alpha=1 in Succession.update_mobject," + \
                    "instead alpha = %f"%alpha
                )
                print self.critical_alphas, alpha
            i = self.num_anims - 1

        # At this point, we should have self.critical_alphas[i] <= alpha <= self.critical_alphas[i +1]

        self.jump_to_start_of_anim(i)
        sub_alpha = inverse_interpolate(
            self.critical_alphas[i], 
            self.critical_alphas[i + 1], 
            alpha
        )
        self.animations[i].update(sub_alpha)
        self.current_alpha = alpha

    def clean_up(self, *args, **kwargs):
        # We clean up as though we've played ALL animations, even if
        # clean_up is called in middle of things
        for anim in self.animations:
            anim.clean_up(*args, **kwargs)

class AnimationGroup(Animation):
    CONFIG = {
        "rate_func" : None
    }
    def __init__(self, *sub_anims, **kwargs):
        sub_anims = filter (lambda x : not(x.empty), sub_anims)
        digest_config(self, locals())
        self.update_config(**kwargs) # Handles propagation to self.sub_anims

        if len(sub_anims) == 0:
            self.empty = True
            self.run_time = 0
        else:
            self.run_time = max([a.run_time for a in sub_anims])
        everything = Mobject(*[a.mobject for a in sub_anims])
        Animation.__init__(self, everything, **kwargs)

    def update(self, alpha):
        for anim in self.sub_anims:
            anim.update(alpha * self.run_time / anim.run_time)

    def clean_up(self, *args, **kwargs):
        for anim in self.sub_anims:
            anim.clean_up(*args, **kwargs)

    def update_config(self, **kwargs):
        Animation.update_config(self, **kwargs)
        
        # If AnimationGroup is called with any configuration,
        # it is propagated to the sub_animations
        for anim in self.sub_anims:
            anim.update_config(**kwargs)

class EmptyAnimation(Animation):
    CONFIG = {
        "run_time" : 0,
        "empty" : True
    }

    def __init__(self, *args, **kwargs):
        return Animation.__init__(self, Group(), *args, **kwargs)
