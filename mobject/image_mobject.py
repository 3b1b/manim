import numpy as np
import itertools as it
import os
from PIL import Image
from random import random

from helpers import *
from mobject import Mobject
from point_cloud_mobject import PMobject

class ImageMobject(PMobject):
    """
    Automatically filters out black pixels
    """
    CONFIG = {
        "filter_color"    : "black",
        "invert"          : True,
        "use_cache"       : True,
        "stroke_width" : 1,
        "scale_value"     : 1.0,
        "should_center"   : True,
    }
    def __init__(self, image_file, **kwargs):
        digest_locals(self)
        Mobject.__init__(self, **kwargs)
        self.name = to_cammel_case(
            os.path.split(image_file)[-1].split(".")[0]
        )
        possible_paths = [
            image_file,
            os.path.join(IMAGE_DIR, image_file),
            os.path.join(IMAGE_DIR, image_file + ".jpg"),
            os.path.join(IMAGE_DIR, image_file + ".png"),
            os.path.join(IMAGE_DIR, image_file + ".gif"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                self.generate_points_from_file(path)
                self.scale(self.scale_value)
                if self.should_center:
                    self.center()
                return
        raise IOError("File not Found")
                
    def generate_points_from_file(self, path):
        if self.use_cache and self.read_in_cached_attrs(path):
            return
        image = Image.open(path).convert('RGB')
        if self.invert:
            image = invert_image(image)
        self.generate_points_from_image_array(np.array(image))
        self.cache_attrs(path)

    def get_cached_attr_files(self, path, attrs):
        #Hash should be unique to (path, invert) pair
        unique_hash = str(hash(path+str(self.invert)))
        return [
            os.path.join(IMAGE_MOBJECT_DIR, unique_hash)+"."+attr
            for attr in attrs
        ]

    def read_in_cached_attrs(self, path, 
                             attrs = ("points", "rgbs"), 
                             dtype = "float64"):
        cached_attr_files = self.get_cached_attr_files(path, attrs)
        if all(map(os.path.exists, cached_attr_files)):
            for attr, cache_file in zip(attrs, cached_attr_files):
                arr = np.fromfile(cache_file, dtype = dtype)
                arr = arr.reshape(arr.size/self.DIM, self.DIM)
                setattr(self, attr, arr)
            return True
        return False

    def cache_attrs(self, path, 
                    attrs = ("points", "rgbs"),
                    dtype = "float64"):
        cached_attr_files = self.get_cached_attr_files(path, attrs)
        for attr, cache_file in zip(attrs, cached_attr_files): 
            getattr(self, attr).astype(dtype).tofile(cache_file)


    def generate_points_from_image_array(self, image_array):
        height, width = image_array.shape[:2]
        #Flatten array, and find indices where rgb is not filter_rgb
        array = image_array.reshape((height * width, 3))
        filter_rgb = np.array(Color(self.filter_color).get_rgb())
        filter_rgb = 255*filter_rgb.astype('uint8')
        bools = array == filter_rgb
        bools = bools[:,0]*bools[:,1]*bools[:,2]
        indices = np.arange(height * width, dtype = 'int')[~bools]
        rgbs = array[indices, :].astype('float') / 255.0

        points = np.zeros((indices.size, 3), dtype = 'float64')
        points[:,0] =  indices%width - width/2
        points[:,1] = -indices/width + height/2

        height, width = map(float, (height, width))
        if height / width > float(DEFAULT_HEIGHT) / DEFAULT_WIDTH:
            points *= 2 * SPACE_HEIGHT / height
        else:
            points *= 2 * SPACE_WIDTH / width
        self.add_points(points, rgbs = rgbs)
        return self


class MobjectFromPixelArray(ImageMobject):
    def __init__(self, image_array, **kwargs):
        Mobject.__init__(self, **kwargs)
        self.generate_points_from_image_array(image_array)




