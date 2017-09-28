import numpy as np
import itertools as it
import os
from PIL import Image
from random import random

from helpers import *
from mobject import Mobject
from point_cloud_mobject import PMobject

class ImageMobject(Mobject):
    """
    Automatically filters out black pixels
    """
    CONFIG = {
        "filter_color" : "black",
        "invert" : False,
        # "use_cache" : True,
        "height": 2.0,
        "image_mode" : "RGBA",
        "pixel_array_dtype" : "uint8",
    }
    def __init__(self, filename_or_array, **kwargs):
        digest_config(self, kwargs)
        if isinstance(filename_or_array, str):
            path = get_full_image_path(filename_or_array)
            image = Image.open(path).convert(self.image_mode)
            self.pixel_array = np.array(image)
        else:
            self.pixel_array = np.array(filename_or_array)
        self.change_to_rgba_array()
        Mobject.__init__(self, **kwargs)

    def change_to_rgba_array(self):
        pa = self.pixel_array
        if len(pa.shape) == 2:
            pa = pa.reshape(list(pa.shape) + [1])
        if pa.shape[2] == 1:
            pa = pa.repeat(3, axis = 2)
        if pa.shape[2] == 3:
            alphas = 255*np.ones(
                list(pa.shape[:2])+[1], 
                dtype = self.pixel_array_dtype
            )
            pa = np.append(pa, alphas, axis = 2)
        self.pixel_array = pa

    def highlight(self, color, alpha = None, family = True):
        rgb = color_to_int_rgb(color)
        self.pixel_array[:,:,:3] = rgb
        if alpha is not None:
            self.pixel_array[:,:,3] = int(255*alpha)
        for submob in self.submobjects:
            submob.highlight(color, alpha, family)
        return self

    def init_points(self):
        #Corresponding corners of image are fixed to these
        #Three points
        self.points = np.array([
            UP+LEFT, 
            UP+RIGHT,
            DOWN+LEFT,
        ])
        self.center()
        self.scale_to_fit_height(self.height)
        h, w = self.pixel_array.shape[:2]
        self.stretch_to_fit_width(self.height*w/h)

    def set_opacity(self, alpha):
        self.pixel_array[:,:,3] = int(255*alpha)
        return self

    def fade(self, darkness = 0.5):
        self.set_opacity(1 - darkness)
        return self

    def interpolate_color(self, mobject1, mobject2, alpha):
        assert(mobject1.pixel_array.shape == mobject2.pixel_array.shape)
        self.pixel_array = interpolate(
            mobject1.pixel_array, mobject2.pixel_array, alpha
        ).astype(self.pixel_array_dtype)

    def copy(self):
        return self.deepcopy()


