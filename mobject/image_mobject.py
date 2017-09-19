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
    }
    def __init__(self, filename_or_array, **kwargs):
        if isinstance(filename_or_array, str):
            path = get_full_image_path(filename_or_array)
            image = Image.open(path).convert("RGB")
            self.pixel_array = np.array(image)
        else:
            self.pixel_array = np.array(filename_or_array)
        Mobject.__init__(self, **kwargs)


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







