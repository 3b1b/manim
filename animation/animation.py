from PIL import Image
from colour import Color
import numpy as np
import warnings
import time
import os
import copy
import progressbar
import inspect
from images2gif import writeGif

from helpers import *
from constants import *
from mobject import Mobject, Point

class Animation(object):
    def __init__(self,
                 mobject,
                 run_time = DEFAULT_ANIMATION_RUN_TIME,
                 alpha_func = smooth,
                 name = None):
        if isinstance(mobject, type) and issubclass(mobject, Mobject):
            self.mobject = mobject()
        elif isinstance(mobject, Mobject):
            self.mobject = mobject
        else:
            raise Exception("Invalid mobject parameter, must be \
                             subclass or instance of Mobject")
        self.starting_mobject = copy.deepcopy(self.mobject)
        self.alpha_func = alpha_func or (lambda x : x)
        self.run_time = run_time
        #TODO, Adress the idea of filtering the animation
        self.filter_functions = []
        self.restricted_height = SPACE_HEIGHT
        self.restricted_width  = SPACE_WIDTH
        self.spacial_center = np.zeros(3)
        self.name = name or self.__class__.__name__ + str(self.mobject)
        self.update(0)

    def __str__(self):
        return self.name

    def get_points_and_rgbs(self):
        """
        It is the responsibility of this class to only emit points within
        the space.  Returns np array of points and corresponding np array 
        of rgbs
        """
        #TODO, I don't think this should be necessary.  This should happen 
        #under the individual mobjects.  
        points = self.mobject.points
        rgbs   = self.mobject.rgbs
        #Filters out what is out of bounds.
        admissibles = (abs(points[:,0]) < self.restricted_width) * \
                      (abs(points[:,1]) < self.restricted_height)
        for filter_function in self.filter_functions:
            admissibles *= ~filter_function(points)
        if any(self.spacial_center):
            points += self.spacial_center
            #Filter out points pushed off the edge
            admissibles *= (abs(points[:,0]) < SPACE_WIDTH) * \
                           (abs(points[:,1]) < SPACE_HEIGHT)
        if rgbs.shape[0] < points.shape[0]:
            #TODO, this shouldn't be necessary, find what's happening.
            points = points[:rgbs.shape[0], :]
            admissibles = admissibles[:rgbs.shape[0]]
        return points[admissibles, :], rgbs[admissibles, :]

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
        self.spacial_center += vector
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


















