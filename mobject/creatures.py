import numpy as np
import itertools as it
import os

from image_mobject import *
from mobject import *
from simple_mobjects import *


class PiCreature(Mobject):
    DEFAULT_COLOR = "blue"
    def __init__(self, **kwargs):
        Mobject.__init__(self, **kwargs)
        color = self.DEFAULT_COLOR
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
        self.eyes = [self.left_eye, self.right_eye]
        self.legs = [self.left_leg, self.right_leg]
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
        return self

    def reload_from_parts(self):
       self.rewire_part_attributes(self_from_parts = True)

    def highlight(self, color, condition = None):
        self.rewire_part_attributes()
        if condition is not None:
            Mobject.highlight(self, color, condition)
            return self
        for part in set(self.parts).difference(self.white_parts):
            part.highlight(color)
        self.reload_from_parts()
        return self

    def move_to(self, destination):
        bottom = np.array((
            np.mean(self.points[:,0]),
            min(self.points[:,1]),
            0
        ))
        self.shift(destination-bottom)
        self.rewire_part_attributes()
        return self

    def give_frown(self):
        center = self.mouth.get_center()
        self.mouth.center()
        self.mouth.apply_function(lambda (x, y, z) : (x, -y, z))
        self.mouth.shift(center)
        self.reload_from_parts()
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
        self.reload_from_parts()
        return self

    def get_eye_center(self):
        return center_of_mass([
            self.left_eye.get_center(), 
            self.right_eye.get_center()
        ]) + 0.04*RIGHT + 0.02*UP

    def make_mean(self):
        eye_x, eye_y = self.get_eye_center()[:2]
        def should_delete((x, y, z)):
            return y - eye_y > 0.3*abs(x - eye_x)
        for eye in self.left_eye, self.right_eye:
            eye.highlight("black", should_delete)
        self.give_straight_face()
        return self

    def make_sad(self):
        eye_x, eye_y = self.get_eye_center()[:2]
        eye_y += 0.15
        def should_delete((x, y, z)):
            return y - eye_y > -0.3*abs(x - eye_x)
        for eye in self.left_eye, self.right_eye:
            eye.highlight("black", should_delete)
        self.give_frown()
        self.reload_from_parts()
        return self

    def get_step_intermediate(self, pi_creature):
        vect = pi_creature.get_center() - self.get_center()
        result = deepcopy(self).shift(vect / 2.0)
        result.rewire_part_attributes()
        left_forward = vect[0] > 0
        if self.right_leg.get_center()[0] < self.left_leg.get_center()[0]:
            #For Mortimer's case
            left_forward = not left_forward
        if left_forward:
            result.left_leg.wag(vect/2.0, DOWN)
            result.right_leg.wag(-vect/2.0, DOWN)
        else:
            result.right_leg.wag(vect/2.0, DOWN)
            result.left_leg.wag(-vect/2.0, DOWN)
        return result

    def blink(self):
        for eye in self.left_eye, self.right_eye:
            bottom = min(eye.points[:,1])
            eye.apply_function(
                lambda (x, y, z) : (x, bottom, z)
            )
        self.reload_from_parts()
        return self

    def shift_eyes(self):
        for eye in self.left_eye, self.right_eye:
            center = eye.get_center()
            eye.center()
            eye.rotate(np.pi, UP)
            eye.shift(center)
        self.reload_from_parts()
        return self

    def to_symbol(self):
        for white_part in self.white_parts:
            self.parts.remove(white_part)
        self.reload_from_parts()
        return self


class Randolph(PiCreature):
    pass #Nothing more than an alternative name

class Mortimer(PiCreature):
    DEFAULT_COLOR = DARK_BROWN
    def __init__(self, *args, **kwargs):
        PiCreature.__init__(self, *args, **kwargs)
        # self.highlight(DARK_BROWN)
        self.give_straight_face()
        self.rotate(np.pi, UP)
        self.rewire_part_attributes()

class TauCreature(PiCreature):
    def __init__(self, **kwargs):
        leg_shift_val = 0.25
        leg_wag_val = 0.2
        PiCreature.__init__(self, **kwargs)
        self.parts.remove(self.right_leg)
        self.left_leg.shift(leg_shift_val*RIGHT)
        self.left_leg.wag(leg_wag_val*RIGHT, DOWN)
        self.leg = self.left_leg
        self.reload_from_parts()










