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
        self.update_mobject(self.rate_func(alpha))

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

    def update_mobject(self, alpha):
        #Typically ipmlemented by subclass
        pass

    def is_remover(self):
        return self.remover

    def clean_up(self):
        self.update(1)

















