from helpers import *

from mobject import Mobject
from mobject.svg_mobject import SVGMobject
from mobject.vectorized_mobject import VMobject
from mobject.tex_mobject import TextMobject


PI_CREATURE_DIR = os.path.join(IMAGE_DIR, "PiCreature")
PI_CREATURE_SCALE_VAL = 0.5

MOUTH_INDEX       = 5
BODY_INDEX        = 4
RIGHT_PUPIL_INDEX = 3
LEFT_PUPIL_INDEX  = 2
RIGHT_EYE_INDEX   = 1
LEFT_EYE_INDEX    = 0


class PiCreature(SVGMobject):
    CONFIG = {
        "color" : BLUE_E,
        "stroke_width" : 0,
        "fill_opacity" : 1.0,
        "initial_scale_val" : 0.01,
    }
    def __init__(self, mode = "plain", **kwargs):
        self.parts_named = False
        svg_file = os.path.join(
            PI_CREATURE_DIR, 
            "PiCreatures_%s.svg"%mode
        )
        digest_config(self, kwargs, locals())
        SVGMobject.__init__(self, svg_file, **kwargs)
        self.init_colors()

    def name_parts(self):
        self.mouth = self.submobjects[MOUTH_INDEX]
        self.body = self.submobjects[BODY_INDEX]
        self.pupils = VMobject(*[
            self.submobjects[LEFT_PUPIL_INDEX],
            self.submobjects[RIGHT_PUPIL_INDEX]
        ])
        self.eyes = VMobject(*[
            self.submobjects[LEFT_EYE_INDEX],
            self.submobjects[RIGHT_EYE_INDEX]
        ])
        self.submobjects = []
        self.add(self.body, self.mouth, self.eyes, self.pupils)
        self.parts_named = True

    def init_colors(self):
        self.set_stroke(color = BLACK, width = self.stroke_width)
        if not self.parts_named:
            self.name_parts()
        self.mouth.set_fill(BLACK)
        self.body.set_fill(self.color)
        self.pupils.set_fill(BLACK)
        self.eyes.set_fill(WHITE)


    def highlight(self, color):
        self.body.set_fill(color)
        return self

    def move_to(self, destination):
        self.shift(destination-self.get_bottom())
        return self

    def change_mode(self, mode):
        curr_center = self.get_center()
        curr_height = self.get_height()
        flip = self.is_flipped()
        self.__class__.__init__(self, mode)
        self.scale_to_fit_height(curr_height)
        self.shift(curr_center)
        if flip:
            self.flip()
        return self

    def look_left(self):
        self.change_mode(self.mode + "_looking_left")
        return self

    def is_flipped(self):
        return self.eyes.submobjects[0].get_center()[0] > \
               self.eyes.submobjects[1].get_center()[0]

    def blink(self):
        eye_bottom_y = self.eyes.get_bottom()[1]
        for mob in self.eyes, self.pupils:
            mob.apply_function(
                lambda p : [p[0], eye_bottom_y, p[2]]
            )
        return self


class Randolph(PiCreature):
    pass #Nothing more than an alternative name

class Mortimer(PiCreature):
    CONFIG = {
        "color" : "#be2612"
    }
    def __init__(self, *args, **kwargs):
        PiCreature.__init__(self, *args, **kwargs)
        self.flip()


class Mathematician(PiCreature):
    CONFIG = {
        "color" : GREY,
    }

class Bubble(SVGMobject):
    CONFIG = {
        "direction" : LEFT,
        "center_point" : ORIGIN,
        "content_scale_factor" : 0.75, 
        "height" : 4,
        "width"  : 6,
        "file_name" : None,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs, locals())
        if self.file_name is None:
            raise Exception("Must invoke Bubble subclass")
        svg_file = os.path.join(
            IMAGE_DIR, self.file_name
        )
        SVGMobject.__init__(self, svg_file, **kwargs)
        self.center()
        self.stretch_to_fit_height(self.height)
        self.stretch_to_fit_width(self.width)
        if self.direction[0] > 0:
            Mobject.flip(self)
        self.content = Mobject()

    def get_tip(self):
        return self.get_corner(DOWN+self.direction)

    def get_bubble_center(self):
        return self.get_center() + self.get_height()*UP/8.0

    def move_tip_to(self, point):
        self.shift(point - self.get_tip())
        return self

    def flip(self):
        Mobject.flip(self)        
        self.direction = -np.array(self.direction)
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
        if self.content in self.submobjects:
            self.submobjects.remove(self.content)
        scaled_width = self.content_scale_factor*self.get_width()
        if mobject.get_width() > scaled_width:
            mobject.scale(scaled_width / mobject.get_width())
        mobject.shift(self.get_bubble_center())
        self.content = mobject
        self.add(self.content)
        return self

    def write(self, text):
        self.add_content(TextMobject(text))
        return self

    def clear(self):
        self.add_content(Mobject())
        return self

class SpeechBubble(Bubble):
    CONFIG = {
        "file_name" : "Bubbles_speech.svg",
    }

class ThoughtBubble(Bubble):
    CONFIG = {
        "file_name" : "Bubbles_thought.svg",
    }

