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
                 image, 
                 filter_color = "black", 
                 invert = True,
                 *args, **kwargs):
        #TODO, Make sure you always convert to RGB
        self.filter_rgb = 255 * np.array(Color(filter_color).get_rgb()).astype('uint8')
        if isinstance(image, str):
            self.name = to_cammel_case(
                os.path.split(image)[-1].split(".")[0]
            )
            possible_paths = [
                image,
                os.path.join(IMAGE_DIR, image),
                os.path.join(IMAGE_DIR, image + ".jpg"),
                os.path.join(IMAGE_DIR, image + ".png"),
            ]
            found = False
            for path in possible_paths:
                if os.path.exists(path):
                    image = Image.open(path).convert('RGB')
                    found = True
            if not found:
                raise IOError("File not Found")
        if invert:
            image = invert_image(image)
        self.image_array = np.array(image)
        Mobject2D.__init__(self, *args, **kwargs)
                
    def generate_points(self):
        height, width = self.image_array.shape[:2]
        #Flatten array, and find indices where rgb is not filter_rgb
        array = self.image_array.reshape((height * width, 3))
        ones = np.ones(height * width, dtype = 'bool')
        for i in range(3):
            ones *= (array[:,i] != self.filter_rgb[i])
        indices = np.arange(height * width, dtype = 'int')[ones]
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
    images = tex_to_image(expression, size, template_tex_file)
    if isinstance(images, list):
        #TODO, is checking listiness really the best here?
        result = CompoundMobject(*map(ImageMobject, images))
    else:
        result = ImageMobject(images)
    return result.highlight("white").center()





