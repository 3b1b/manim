from helpers import *

from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.tex_mobject import TexMobject, TextMobject
from topics.geometry import Circle, Line


PI_CREATURE_DIR = os.path.join(IMAGE_DIR, "PiCreature")
PI_CREATURE_SCALE_VAL = 0.5
PI_CREATURE_MOUTH_TO_EYES_DISTANCE = 0.25

def part_name_to_directory(name):
    return os.path.join(PI_CREATURE_DIR, "pi_creature_"+name) + ".png"

class PiCreature(Mobject):
    DEFAULT_CONFIG = {
        "color" : BLUE_E
    }
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
        Mobject.__init__(self, **kwargs)
        for part_name in self.PART_NAMES:
            mob = ImageMobject(
                part_name_to_directory(part_name),
                should_center = False
            )
            if part_name not in self.WHITE_PART_NAMES:
                mob.highlight(self.color)
            setattr(self, part_name, mob)
        self.eyes = Mobject(self.left_eye, self.right_eye)
        self.legs = Mobject(self.left_leg, self.right_leg)
        mouth_center = self.get_mouth_center()
        self.mouth.center()
        self.smile = self.mouth
        self.frown = self.mouth.copy().rotate(np.pi, RIGHT)
        self.straight_mouth = TexMobject("-").scale(0.7)
        for mouth in self.smile, self.frown, self.straight_mouth:
            mouth.sort_points(lambda p : p[0])
            mouth.highlight(self.color) ##to blend into background
            mouth.shift(mouth_center)
        self.digest_mobject_attrs()
        self.give_smile()
        self.add(self.mouth)
        self.scale(PI_CREATURE_SCALE_VAL)


    def get_parts(self):
        return [getattr(self, pn) for pn in self.PART_NAMES]

    def get_white_parts(self):
        return [
            getattr(self, pn) 
            for pn in self.WHITE_PART_NAMES+self.MOUTH_NAMES
        ]

    def get_mouth_center(self):
        result = self.body.get_center()
        result[0] = self.eyes.get_center()[0]
        return result
        # left_center  = self.left_eye.get_center()
        # right_center = self.right_eye.get_center()
        # l_to_r = right_center-left_center
        # eyes_to_mouth = rotate_vector(l_to_r, -np.pi/2, OUT)
        # eyes_to_mouth /= np.linalg.norm(eyes_to_mouth)
        # return left_center/2 + right_center/2 + \
        #        PI_CREATURE_MOUTH_TO_EYES_DISTANCE*eyes_to_mouth

    def highlight(self, color, condition = None):
        for part in set(self.get_parts()).difference(self.get_white_parts()):
            part.highlight(color, condition)
        return self

    def move_to(self, destination):
        self.shift(destination-self.get_bottom())
        return self

    def change_mouth_to(self, mouth_name):
        #TODO, This is poorly implemented
        self.mouth = getattr(self, mouth_name) 
        self.sub_mobjects = list_update(
            self.sub_mobjects, 
            self.get_parts()
        )
        self.mouth.highlight(WHITE)
        return self

    def give_smile(self):
        return self.change_mouth_to("smile")

    def give_frown(self):
        return self.change_mouth_to("frown")

    def give_straight_face(self):
        return self.change_mouth_to("straight_mouth")

    def get_eye_center(self):
        return self.eyes.get_center()

    def make_mean(self):
        eye_x, eye_y = self.get_eye_center()[:2]
        def should_delete((x, y, z)):
            return y - eye_y > 0.3*abs(x - eye_x)
        self.eyes.highlight("black", should_delete)
        self.give_straight_face()
        return self

    def make_sad(self):
        eye_x, eye_y = self.get_eye_center()[:2]
        eye_y += 0.15
        def should_delete((x, y, z)):
            return y - eye_y > -0.3*abs(x - eye_x)
        self.eyey.highlight("black", should_delete)
        self.give_frown()
        return self

    def get_step_intermediate(self, pi_creature):
        vect = pi_creature.get_center() - self.get_center()
        result = self.copy().shift(vect / 2.0)
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
        bottom = self.eyes.get_bottom()
        self.eyes.apply_function(
            lambda (x, y, z) : (x, bottom[1], z)
        )
        return self

    def shift_eyes(self):
        for eye in self.left_eye, self.right_eye:
            eye.rotate_in_place(np.pi, UP)
        return self

    def to_symbol(self):
        Mobject.__init__(
            self,
            *list(set(self.get_parts()).difference(self.get_white_parts()))
        )


class Randolph(PiCreature):
    pass #Nothing more than an alternative name

class Mortimer(PiCreature):
    DEFAULT_CONFIG = {
        "color" : DARK_BROWN
    }
    def __init__(self, **kwargs):
        PiCreature.__init__(self, **kwargs)
        # self.highlight(DARK_BROWN)
        self.give_straight_face()
        self.rotate(np.pi, UP)


class Mathematician(PiCreature):
    DEFAULT_CONFIG = {
        "color" : GREY,
    }
    def __init__(self, **kwargs):
        PiCreature.__init__(self, **kwargs)
        self.give_straight_face()


class Bubble(Mobject):
    DEFAULT_CONFIG = {
        "direction" : LEFT,
        "center_point" : ORIGIN,
    }
    def __init__(self, **kwargs):
        Mobject.__init__(self, **kwargs)
        self.center_offset = self.center_point - Mobject.get_center(self)
        if self.direction[0] > 0:
            self.rotate(np.pi, UP)
        self.content = Mobject()

    def get_tip(self):
        raise Exception("Not implemented")

    def get_bubble_center(self):
        return self.get_center()+self.center_offset

    def move_tip_to(self, point):
        self.shift(point - self.get_tip())
        return self

    def flip(self):
        self.direction = -np.array(self.direction)
        self.rotate(np.pi, UP)
        return self

    def pin_to(self, mobject):
        mob_center = mobject.get_center()
        if (mob_center[0] > 0) != (self.direction[0] > 0):
            self.flip()
        boundary_point = mobject.get_boundary_point(UP-self.direction)
        vector_from_center = 1.5*(boundary_point-mob_center)
        self.move_tip_to(mob_center+vector_from_center)
        return self

    def add_content(self, mobject):
        scaled_width = 0.75*self.get_width()
        if mobject.get_width() > scaled_width:
            mobject.scale(scaled_width / mobject.get_width())
        mobject.shift(self.get_bubble_center())
        self.content = mobject
        return self

    def write(self, text):
        self.add_content(TextMobject(text))
        return self

    def clear(self):
        self.content = Mobject()
        return self

class SpeechBubble(Bubble):
    DEFAULT_CONFIG = {
        "initial_width"  : 6,
        "initial_height" : 4,
    }

    def generate_points(self):
        complex_power = 0.9
        radius = self.initial_width/2
        circle = Circle(radius = radius)
        circle.scale(1.0/radius)
        circle.apply_complex_function(lambda z : z**complex_power)
        circle.scale(radius)
        boundary_point_as_complex = radius*complex(-1)**complex_power
        boundary_points = [
            [
                boundary_point_as_complex.real,
                unit*boundary_point_as_complex.imag,
                0
            ]
            for unit in -1, 1
        ]
        tip = radius*(1.5*LEFT+UP)
        self.little_line = Line(boundary_points[0], tip)
        self.circle = circle
        self.add(
            circle,
            self.little_line,
            Line(boundary_points[1], tip)
        )
        self.highlight("white")
        self.rotate(np.pi/2)
        self.stretch_to_fit_height(self.initial_height)

    def get_tip(self):
        return self.little_line.points[-1]

    def get_bubble_center(self):
        return self.circle.get_center()

class ThoughtBubble(Bubble):
    DEFAULT_CONFIG = {
        "num_bulges"           : 7,
        "initial_inner_radius" : 1.8,
        "initial_width"        : 6,
    }
    def __init__(self, **kwargs):
        Bubble.__init__(self, **kwargs)

    def get_tip(self):
        return self.small_circle.get_bottom()

    def generate_points(self):
        self.small_circle = Circle().scale(0.15)
        self.small_circle.shift(2.5*DOWN+2*LEFT)
        self.add(self.small_circle)
        self.add(Circle().scale(0.3).shift(2*DOWN+1.5*LEFT))
        for n in range(self.num_bulges):
            theta = 2*np.pi*n/self.num_bulges
            self.add(Circle().shift((np.cos(theta), np.sin(theta), 0)))
        self.filter_out(lambda p : np.linalg.norm(p) < self.initial_inner_radius)
        self.stretch_to_fit_width(self.initial_width)
        self.highlight("white")
