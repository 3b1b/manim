import numpy as np
import itertools as it
import os

from image_mobject import *
from mobject import *
from simple_mobjects import *


class PiCreature(CompoundMobject):
    DEFAULT_COLOR = "blue"
    PART_NAMES = [
        'arm', 
        'body', 
        'left_eye', 
        'right_eye',
        'left_leg',
        'right_leg',            
        'mouth', 
    ]
    WHITE_PART_NAMES = ['left_eye', 'right_eye', 'mouth']
    MOUTH_NAMES = ["smile", "frown", "straight_mouth"]

    def __init__(self, **kwargs):
        color = self.DEFAULT_COLOR if "color" not in kwargs else kwargs.pop("color")
        for part_name in self.PART_NAMES:
            mob = ImageMobject(
                PI_CREATURE_PART_NAME_TO_DIR(part_name)
            )
            if part_name not in self.WHITE_PART_NAMES:
                mob.highlight(color)
            mob.scale(PI_CREATURE_SCALE_VAL)
            setattr(self, part_name, mob)
        self.eyes = [self.left_eye, self.right_eye]
        self.legs = [self.left_leg, self.right_leg]
        mouth_center = self.get_mouth_center()
        self.mouth.center()
        self.smile = deepcopy(self.mouth)
        self.frown = deepcopy(self.mouth).rotate(np.pi, RIGHT)
        self.straight_mouth = tex_mobject("-").scale(0.5)
        for mouth_name in ["mouth"] + self.MOUTH_NAMES:
            mouth = getattr(self, mouth_name)
            mouth.sort_points(lambda p : p[0])
            mouth.shift(mouth_center)
        #Ordering matters here, so hidden mouths are behind body
        self.part_names = self.MOUTH_NAMES + self.PART_NAMES
        self.white_parts = self.MOUTH_NAMES + self.WHITE_PART_NAMES
        CompoundMobject.__init__(
            self,
            *self.get_parts(),
            **kwargs
        )

    def sync_parts(self):
        CompoundMobject.__init__(self, *self.get_parts())
        return self

    def TODO_what_should_I_do_with_this(self):
        for part_name, mob in zip(self.part_names, self.split()):
            setattr(self, part_name, mob)


    def get_parts(self):
        return [getattr(self, pn) for pn in self.part_names]

    def get_white_parts(self):
        return [getattr(self, pn) for pn in self.white_parts]

    def get_mouth_center(self):
        left_center  = self.left_eye.get_center()
        right_center = self.right_eye.get_center()
        l_to_r = right_center-left_center
        eyes_to_mouth = rotate_vector(l_to_r, -np.pi/2, OUT)
        eyes_to_mouth /= np.linalg.norm(eyes_to_mouth)
        return left_center/2 + right_center/2 + \
               PI_CREATURE_MOUTH_TO_EYES_DISTANCE*eyes_to_mouth

    def highlight(self, color, condition = None):
        for part in set(self.get_parts()).difference(self.get_white_parts()):
            part.highlight(color, condition)
        return self.sync_parts()

    def move_to(self, destination):
        self.shift(destination-self.get_bottom())
        return self.sync_parts()

    def change_mouth_to(self, mouth_name):
        self.mouth = getattr(self, mouth_name)
        return self.sync_parts()

    def give_smile(self):
        return self.change_mouth_to("smile")

    def give_frown(self):
        return self.change_mouth_to("frown")

    def give_straight_face(self):
        return self.change_mouth_to("straight_mouth")

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
        return self.sync_parts()

    def make_sad(self):
        eye_x, eye_y = self.get_eye_center()[:2]
        eye_y += 0.15
        def should_delete((x, y, z)):
            return y - eye_y > -0.3*abs(x - eye_x)
        for eye in self.left_eye, self.right_eye:
            eye.highlight("black", should_delete)
        self.give_frown()
        return self.sync_parts()

    def get_step_intermediate(self, pi_creature):
        vect = pi_creature.get_center() - self.get_center()
        result = deepcopy(self).shift(vect / 2.0)
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
        return result.sync_parts()

    def blink(self):
        for eye in self.left_eye, self.right_eye:
            bottom = eye.get_bottom()
            eye.apply_function(
                lambda (x, y, z) : (x, bottom[1], z)
            )
        return self.sync_parts()

    def shift_eyes(self):
        for eye in self.left_eye, self.right_eye:
            eye.rotate_in_place(np.pi, UP)
        return self.sync_parts()

    def to_symbol(self):
        CompoundMobject.__init__(
            self,
            *list(set(self.get_parts()).difference(self.get_white_parts()))
        )


class Randolph(PiCreature):
    pass #Nothing more than an alternative name

class Mortimer(PiCreature):
    DEFAULT_COLOR = DARK_BROWN
    def __init__(self, *args, **kwargs):
        PiCreature.__init__(self, *args, **kwargs)
        # self.highlight(DARK_BROWN)
        self.give_straight_face()
        self.rotate(np.pi, UP)










