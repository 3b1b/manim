from helpers import *

from mobject import Mobject, CompoundMobject
from image_mobject import ImageMobject

PI_CREATURE_DIR = os.path.join(IMAGE_DIR, "PiCreature")
PI_CREATURE_PART_NAME_TO_DIR = lambda name : os.path.join(PI_CREATURE_DIR, "pi_creature_"+name) + ".png"
PI_CREATURE_SCALE_VAL = 0.5
PI_CREATURE_MOUTH_TO_EYES_DISTANCE = 0.25

class PiCreature(CompoundMobject):
    DEFAULT_COLOR = BLUE
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
        self.straight_mouth = TexMobject("-").scale(0.5)
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

    # def TODO_what_should_I_do_with_this(self):
    #     for part_name, mob in zip(self.part_names, self.split()):
    #         setattr(self, part_name, mob)


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


class Bubble(Mobject):
    DEFAULT_CONFIG = {
        "direction" : LEFT,
        "index_of_tip" : -1,
        "center_point" : ORIGIN,
    }
    def __init__(self, **kwargs):
        Mobject.__init__(self, **kwargs)
        self.center_offset = self.center_point - Mobject.get_center(self)
        if self.direction[0] > 0:
            self.rotate(np.pi, UP)
        self.content = Mobject()

    def get_tip(self):
        return self.points[self.index_of_tip]

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
        "initial_width" : 4,
        "initial_height" : 2,
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
        self.add(
            circle,
            Line(boundary_points[0], tip),
            Line(boundary_points[1], tip)
        )
        self.highlight("white")
        self.rotate(np.pi/2)
        self.points[:,1] *= float(self.initial_height)/self.initial_width

class ThoughtBubble(Bubble):
    DEFAULT_CONFIG = {
        "num_bulges" : 7,
        "initial_inner_radius" : 1.8,
        "initial_width" : 6
    }
    def __init__(self, **kwargs):
        Bubble.__init__(self, **kwargs)
        self.index_of_tip = np.argmin(self.points[:,1])

    def generate_points(self):
        self.add(Circle().scale(0.15).shift(2.5*DOWN+2*LEFT))
        self.add(Circle().scale(0.3).shift(2*DOWN+1.5*LEFT))
        for n in range(self.num_bulges):
            theta = 2*np.pi*n/self.num_bulges
            self.add(Circle().shift((np.cos(theta), np.sin(theta), 0)))
        self.filter_out(lambda p : np.linalg.norm(p) < self.initial_inner_radius)
        self.stretch_to_fit_width(self.initial_width)
        self.highlight("white")
