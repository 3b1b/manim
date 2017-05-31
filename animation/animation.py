from PIL import Image
from colour import Color
import numpy as np
import warnings
import time
import os
import progressbar
import inspect
from copy import deepcopy

from helpers import *
from mobject import Mobject

class Animation(object):
    CONFIG = {
        "run_time" : DEFAULT_ANIMATION_RUN_TIME,
        "rate_func" : smooth,
        "name" : None,
        #Does this animation add or remove a mobject form the screen
        "remover" : False, 
        #Options are lagged_start, smoothed_lagged_start,
        #one_at_a_time, all_at_once
        "submobject_mode" : "all_at_once",
        "lag_factor" : 2,
    }
    def __init__(self, mobject, **kwargs):
        mobject = instantiate(mobject)
        assert(isinstance(mobject, Mobject))
        digest_config(self, kwargs, locals())
        self.starting_mobject = self.mobject.copy()
        if self.rate_func is None:
            self.rate_func = (lambda x : x)
        if self.name is None:
            self.name = self.__class__.__name__ + str(self.mobject)
        self.all_families_zipped = self.get_all_families_zipped()
        self.update(0)

    def update_config(self, **kwargs):
        digest_config(self, kwargs)
        if "rate_func" in kwargs and kwargs["rate_func"] is None:
            self.rate_func = (lambda x : x)
        return self

    def __str__(self):
        return self.name

    def copy(self):
        return deepcopy(self)

    def update(self, alpha):
        if alpha < 0:
            alpha = 0.0
        if alpha > 1:
            alpha = 1.0
        self.update_mobject(self.rate_func(alpha))

    def update_mobject(self, alpha):
        families = self.all_families_zipped
        for i, mobs in enumerate(families):
            sub_alpha = self.get_sub_alpha(alpha, i, len(families))
            self.update_submobject(*list(mobs) + [sub_alpha])
        return self

    def update_submobject(self, submobject, starting_sumobject, alpha):
        #Typically ipmlemented by subclass
        pass

    def get_all_mobjects(self):
        """
        Ordering must match the ording of arguments to update_submobject
        """ 
        return self.mobject, self.starting_mobject

    def get_all_families_zipped(self):
        return zip(*map(
            Mobject.family_members_with_points,
            self.get_all_mobjects()
        ))

    def get_sub_alpha(self, alpha, index, num_submobjects):
        if self.submobject_mode in ["lagged_start", "smoothed_lagged_start"]:
            prop = float(index)/num_submobjects
            if self.submobject_mode is "smoothed_lagged_start":
                prop = smooth(prop)
            lf = self.lag_factor
            return np.clip(lf*alpha - (lf-1)*prop, 0, 1)
        elif self.submobject_mode == "one_at_a_time":
            lower = float(index)/num_submobjects
            upper = float(index+1)/num_submobjects
            return np.clip((alpha-lower)/(upper-lower), 0, 1)
        elif self.submobject_mode == "all_at_once":
            return alpha
        raise Exception("Invalid submobject mode")

    def filter_out(self, *filter_functions):
        self.filter_functions += filter_functions
        return self

    def set_run_time(self, time):
        self.run_time = time
        return self

    def get_run_time(self):
        return self.run_time

    def set_rate_func(self, rate_func):
        if rate_func is None:
            rate_func = lambda x : x
        self.rate_func = rate_func
        return self

    def get_rate_func(self):
        return self.rate_func

    def set_name(self, name):
        self.name = name
        return self

    def is_remover(self):
        return self.remover

    def clean_up(self, surrounding_scene = None):
        self.update(1)
        if surrounding_scene is not None:
            if self.is_remover():
                surrounding_scene.remove(self.mobject)
            else:
                surrounding_scene.add(self.mobject)
        return self


def sync_animation_run_times_and_rate_funcs(*animations, **kwargs):
    for animation in animations:
        animation.update_config(**kwargs)
    max_run_time = max([a.run_time for a in animations])
    for animation in animations:
        if animation.run_time != max_run_time:
            new_rate_func = squish_rate_func(
                animation.get_rate_func(),
                0, float(animation.run_time)/max_run_time
            )
            animation.set_rate_func(new_rate_func)
            animation.set_run_time(max_run_time)












