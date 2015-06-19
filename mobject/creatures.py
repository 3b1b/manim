import numpy as np
import itertools as it
import os

from image_mobject import *
from mobject import *
from simple_mobjects import *


class PiCreature(Mobject):
    DEFAULT_COLOR = "blue"
    def __init__(self, color = DEFAULT_COLOR, **kwargs):
        Mobject.__init__(self, color = color, **kwargs)
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

        parts = []
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
            parts.append(mob)
        self.mouth.center().shift(
            self.left_eye.get_center()/2 + 
            self.right_eye.get_center()/2 -
            (0, mouth_to_eyes_distance, 0)
        )

        for part in parts:
            self.add(part)
        self.parts = parts

    def rewire_part_attributes(self, self_from_parts = False):
        if self_from_parts:
            total_num_points = sum(map(Mobject.get_num_points, self.parts))
            self.points = np.zeros((total_num_points, Mobject.DIM))
            self.rgbs   = np.zeros((total_num_points, Mobject.DIM))
        curr = 0
        for part in self.parts:
            n_points = part.get_num_points()
            if self_from_parts:
                self.points[curr:curr+n_points,:] = part.points
                self.rgbs[curr:curr+n_points,:] = part.rgbs
            else:
                part.points = self.points[curr:curr+n_points,:]
                part.rgbs = self.rgbs[curr:curr+n_points,:]
            curr += n_points


    def highlight(self, color):
        for part in set(self.parts).difference(self.white_parts):
            part.highlight(color)
        self.rewire_part_attributes(self_from_parts = True)
        return self

    def move_to(self, destination):
        bottom = np.array((
            np.mean(self.points[:,0]),
            min(self.points[:,1]),
            0
        ))
        self.shift(destination-bottom)
        return self

    def give_frown(self):
        center = self.mouth.get_center()
        self.mouth.center()
        self.mouth.apply_function(lambda (x, y, z) : (x, -y, z))
        self.mouth.shift(center)
        self.rewire_part_attributes(self_from_parts = True)
        return self

    def give_straight_face(self):
        center = self.mouth.get_center()
        self.mouth.center()
        new_mouth = tex_mobject("-").scale(0.5)
        new_mouth.center().shift(self.mouth.get_center())
        new_mouth.shift(center)
        self.parts[self.parts.index(self.mouth)] = new_mouth
        self.white_parts[self.white_parts.index(self.mouth)] = new_mouth
        self.mouth = new_mouth
        self.rewire_part_attributes(self_from_parts = True)
        return self

    def get_step_intermediate(self, pi_creature):
        vect = pi_creature.get_center() - self.get_center()
        result = deepcopy(self).shift(vect / 2.0)
        result.rewire_part_attributes()
        if vect[0] < 0:
            result.right_leg.wag(-vect/2.0, DOWN)
            result.left_leg.wag(vect/2.0, DOWN)
        else:
            result.left_leg.wag(-vect/2.0, DOWN)
            result.right_leg.wag(vect/2.0, DOWN)
        return result


class Randolph(PiCreature):
    pass #Nothing more than an alternative name

class Mortimer(PiCreature):
    def __init__(self, *args, **kwargs):
        PiCreature.__init__(self, *args, **kwargs)
        self.highlight(DARK_BROWN)
        self.give_straight_face()
        self.rotate(np.pi, UP)
        self.rewire_part_attributes()










