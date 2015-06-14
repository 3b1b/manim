import numpy as np
import itertools as it
import os

from image_mobject import *
from mobject import *
from simple_mobjects import *


class PiCreature(CompoundMobject):
    DEFAULT_COLOR = "blue"
    def __init__(self, color = DEFAULT_COLOR, **kwargs):
        scale_val = 0.5
        mouth_to_eyes_distance = 0.25
        part_names = [
            'arm', 
            'body', 
            'left_eye', 
            'right_eye',             
            'left_leg',
            'right_leg',            
            'mouth', 
        ]
        white_part_names = ['left_eye', 'right_eye', 'mouth']
        directory = os.path.join(IMAGE_DIR, "PiCreature")

        self.parts = []
        self.white_parts = []
        for part_name in part_names:
            path = os.path.join(directory, "pi_creature_"+part_name)
            path += ".png"
            mob = ImageMobject(path)
            mob.scale(scale_val)
            if part_name in white_part_names:
                self.white_parts.append(mob)
            else:
                mob.highlight(color)
            setattr(self, part_name, mob)
            self.parts.append(mob)
        self.mouth.center().shift(
            self.left_eye.get_center()/2 + 
            self.right_eye.get_center()/2 -
            (0, mouth_to_eyes_distance, 0)
        )
        self.reload_parts()

    def reload_parts(self):
        CompoundMobject.__init__(self, *self.parts)
        return self

    def highlight(self, color):
        for part in set(self.parts).difference(self.white_parts):
            part.highlight(color)
        return self.reload_parts()

    def give_frown(self):
        center = self.mouth.get_center()
        self.mouth.center()
        self.mouth.apply_function(lambda (x, y, z) : (x, -y, z))
        self.mouth.shift(center)
        return self.reload_parts()

    def give_straight_face(self):
        center = self.mouth.get_center()
        self.mouth.center()
        new_mouth = tex_mobject("-").scale(0.5)
        new_mouth.center().shift(self.mouth.get_center())
        new_mouth.shift(center)
        self.parts[self.parts.index(self.mouth)] = new_mouth
        self.white_parts[self.white_parts.index(self.mouth)] = new_mouth
        self.mouth = new_mouth
        return self.reload_parts()

class Randolph(PiCreature):
    pass #Nothing more than an alternative name

class Mortimer(PiCreature):
    def __init__(self, *args, **kwargs):
        PiCreature.__init__(self, *args, **kwargs)
        self.highlight(DARK_BROWN)
        self.give_straight_face()






