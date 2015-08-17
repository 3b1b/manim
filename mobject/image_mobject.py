import numpy as np
import itertools as it
import os
from PIL import Image
from random import random

from tex_utils import *
from mobject import *

class ImageMobject(Mobject2D):
    """
    Automatically filters out black pixels
    """
#    SHOULD_BUFF_POINTS = False
    def __init__(self, 
                 image_file, 
                 filter_color = "black", 
                 invert = True,
                 *args, **kwargs):
        Mobject2D.__init__(self, *args, **kwargs)
        self.filter_rgb = 255 * np.array(Color(filter_color).get_rgb()).astype('uint8')
        self.name = to_cammel_case(
            os.path.split(image_file)[-1].split(".")[0]
        )
        possible_paths = [
            image_file,
            os.path.join(IMAGE_DIR, image_file),
            os.path.join(IMAGE_DIR, image_file + ".jpg"),
            os.path.join(IMAGE_DIR, image_file + ".png"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                self.generate_points_from_file(path, invert)
                return
        raise IOError("File not Found")
                
    def generate_points_from_file(self, path, invert):
        #Hash should be unique to (path, invert) pair
        dtype = 'float'
        unique_hash = str(hash(path+str(invert)))
        cached_points, cached_rgbs = [
            os.path.join(IMAGE_MOBJECT_DIR, unique_hash)+extension
            for extension in ".points", ".rgbs"
        ]
        if os.path.exists(cached_points) and os.path.exists(cached_rgbs):
            self.points = np.fromfile(cached_points, dtype = dtype)
            self.rgbs = np.fromfile(cached_rgbs, dtype = dtype)
            n_points = self.points.size/self.DIM
            self.points = self.points.reshape(n_points, self.DIM)
            self.rgbs = self.rgbs.reshape(n_points, 3)
        else:
            image = Image.open(path).convert('RGB')
            if invert:
                image = invert_image(image)
            self.generate_points_from_image_array(np.array(image))
            self.points.astype(dtype).tofile(cached_points)
            self.rgbs.astype(dtype).tofile(cached_rgbs)

    def generate_points_from_image_array(self, image_array):
        height, width = image_array.shape[:2]
        #Flatten array, and find indices where rgb is not filter_rgb
        array = image_array.reshape((height * width, 3))
        bools = array == self.filter_rgb
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

    def should_buffer_points(self):
        # potentially changed in subclasses
        return False

class Face(ImageMobject):
    def __init__(self, mode = "simple", *args, **kwargs):
        """
        Mode can be "simple", "talking", "straight"
        """
        ImageMobject.__init__(self, mode + "_face", *args, **kwargs)
        self.scale(0.5)
        self.center()

class VideoIcon(ImageMobject):
    def __init__(self, *args, **kwargs):
        ImageMobject.__init__(self, "video_icon", *args, **kwargs)
        self.scale(0.3)
        self.center()

def text_mobject(text, size = None):
    size = size or "\\Large" #TODO, auto-adjust?
    return tex_mobject(text, size, TEMPLATE_TEXT_FILE)

def tex_mobject(expression, 
                size = None, 
                template_tex_file = TEMPLATE_TEX_FILE):
    if size == None:
        if len("".join(expression)) < MAX_LEN_FOR_HUGE_TEX_FONT:
            size = "\\Huge"
        else:
            size = "\\large"
        #Todo, make this more sophisticated.
    image_files = tex_to_image(expression, size, template_tex_file)
    if isinstance(image_files, list):
        #TODO, is checking listiness really the best here?
        result = CompoundMobject(*map(ImageMobject, image_files))
    else:
        result = ImageMobject(image_files)
    return result.highlight("white").center()





