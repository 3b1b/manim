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
    DEFAULT_CONFIG = {
        "run_time" : DEFAULT_ANIMATION_RUN_TIME,
        "alpha_func" : smooth,
        "name" : None,
    }
    def __init__(self, mobject, **kwargs):
        mobject = instantiate(mobject)
        assert(isinstance(mobject, Mobject))
        digest_config(self, kwargs, locals())
        self.starting_mobject = self.mobject.copy()
        if self.alpha_func is None:
            self.alpha_func = (lambda x : x)
        if self.name is None:
            self.name = self.__class__.__name__ + str(self.mobject)
        self.update(0)

    def __str__(self):
        return self.name

    def copy(self):
        return deepcopy(self)

    def update(self, alpha):
        if alpha < 0:
            alpha = 0.0
        if alpha > 1:
            alpha = 1.0
        self.update_mobject(self.alpha_func(alpha))

    def filter_out(self, *filter_functions):
        self.filter_functions += filter_functions
        return self

    def restrict_height(self, height):
        self.restricted_height = min(height, SPACE_HEIGHT)
        return self

    def restrict_width(self, width):
        self.restricted_width = min(width, SPACE_WIDTH)   
        return self

    def shift(self, vector):
        self.spatial_center += vector
        return self

    def set_run_time(self, time):
        self.run_time = time
        return self

    def set_alpha_func(self, alpha_func):
        if alpha_func is None:
            alpha_func = lambda x : x
        self.alpha_func = alpha_func
        return self

    def set_name(self, name):
        self.name = name
        return self

    def update_mobject(self, alpha):
        #Typically ipmlemented by subclass
        pass

    def clean_up(self):
        self.update(1)

















