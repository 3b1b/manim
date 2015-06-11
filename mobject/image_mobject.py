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

class SpeechBubble(ImageMobject):
    def __init__(self, *args, **kwargs):
        ImageMobject.__init__(self, "speech_bubble", *args, **kwargs)
        self.scale(0.25)

class ThoughtBubble(ImageMobject):
    def __init__(self, *args, **kwargs):
        ImageMobject.__init__(self, "thought_bubble", *args, **kwargs)
        self.scale(0.5)

class SimpleFace(ImageMobject):
    def __init__(self, *args, **kwargs):
        ImageMobject.__init__(self, "simple_face", *args, **kwargs)
        self.scale(0.5)

class VideoIcon(ImageMobject):
    def __init__(self, *args, **kwargs):
        ImageMobject.__init__(self, "video_icon", *args, **kwargs)
        self.scale(0.3)

def text_mobject(text, size = "\\Large"):
    image = tex_to_image(text, size, TEMPLATE_TEXT_FILE)
    assert(not isinstance(image, list))
    return ImageMobject(image).center()

#Purely redundant function to make singulars and plurals sensible
def tex_mobject(expression, size = "\\Huge"):
    return tex_mobjects(expression, size)

def tex_mobjects(expression, size = "\\Huge"):
    images = tex_to_image(expression, size)
    if isinstance(images, list):
        #TODO, is checking listiness really the best here?
        result = [ImageMobject(im) for im in images]
        return CompoundMobject(*result).center().split()
    else:
        return ImageMobject(images).center()





