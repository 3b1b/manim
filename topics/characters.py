from helpers import *

from mobject import Mobject
from mobject.svg_mobject import SVGMobject
from mobject.vectorized_mobject import VMobject
from mobject.tex_mobject import TextMobject

from animation.transform import Transform, ApplyMethod, FadeOut, FadeIn
from animation.simple_animations import Write
from scene import Scene


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
        "corner_scale_factor" : 0.75,
        "flip_at_start" : False,
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
        if self.flip_at_start:
            self.flip()

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
        self.mouth.set_fill(BLACK, opacity = 1)
        self.body.set_fill(self.color, opacity = 1)
        self.pupils.set_fill(BLACK, opacity = 1)
        self.eyes.set_fill(WHITE, opacity = 1)
        return self


    def highlight(self, color):
        self.body.set_fill(color)
        return self

    def move_to(self, destination):
        self.shift(destination-self.get_bottom())
        return self

    def change_mode(self, mode):
        curr_center = self.get_center()
        curr_height = self.get_height()
        looking_direction = None
        looking_direction = self.get_looking_direction()
        should_be_flipped = self.is_flipped()
        self.__init__(mode)
        self.scale_to_fit_height(curr_height)
        self.shift(curr_center)
        self.look(looking_direction)
        if should_be_flipped ^ self.is_flipped():
            self.flip()
        return self

    def look(self, direction):
        x, y = direction[:2]        
        for pupil, eye in zip(self.pupils.split(), self.eyes.split()):
            pupil.move_to(eye, side_to_align = direction)
            #Some hacky nudging is required here
            if y > 0 and x != 0: # Look up and to a side
                nudge_size = pupil.get_height()/4.
                if x > 0: 
                    nudge = nudge_size*(DOWN+LEFT)
                else:
                    nudge = nudge_size*(DOWN+RIGHT)
                pupil.shift(nudge)
            elif y < 0:
                nudge_size = pupil.get_height()/8.
                pupil.shift(nudge_size*UP)
        return self

    def get_looking_direction(self):
        return np.sign(np.round(
            self.pupils.get_center() - self.eyes.get_center(),
            decimals = 1
        ))

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

    def to_corner(self, vect = None):
        if vect is not None:
            SVGMobject.to_corner(self, vect)
        else:
            self.scale(self.corner_scale_factor)
            self.to_corner(DOWN+LEFT)
        return self

    def get_bubble(self, bubble_type = "thought", **kwargs):
        if bubble_type == "thought":
            bubble = ThoughtBubble(**kwargs)
        elif bubble_type == "speech":
            bubble = SpeechBubble(**kwargs)
        else:
            raise Exception("%s is an invalid bubble type"%bubble_type)
        bubble.pin_to(self)
        return bubble


class Randolph(PiCreature):
    pass #Nothing more than an alternative name

class Mortimer(PiCreature):
    CONFIG = {
        "color" : GREY_BROWN,
        "flip_at_start" : True,
    }
    

class Mathematician(PiCreature):
    CONFIG = {
        "color" : GREY,
    }

class Blink(ApplyMethod):
    CONFIG = {
        "rate_func" : squish_rate_func(there_and_back)
    }
    def __init__(self, pi_creature, **kwargs):
        ApplyMethod.__init__(self, pi_creature.blink, **kwargs)

class Bubble(SVGMobject):
    CONFIG = {
        "direction" : LEFT,
        "center_point" : ORIGIN,
        "content_scale_factor" : 0.75,
        "height" : 5,
        "width"  : 8,
        "file_name" : None,
        "propogate_style_to_family" : True,
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
        #TODO, find a better way
        return self.get_corner(DOWN+self.direction)-0.6*self.direction

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
        boundary_point = mobject.get_critical_point(UP-self.direction)
        vector_from_center = 1.0*(boundary_point-mob_center)
        self.move_tip_to(mob_center+vector_from_center)
        return self

    def position_mobject_inside(self, mobject):
        scaled_width = self.content_scale_factor*self.get_width()
        if mobject.get_width() > scaled_width:
            mobject.scale_to_fit_width(scaled_width)
        mobject.shift(
            self.get_bubble_center() - mobject.get_center()
        )
        return mobject

    def add_content(self, mobject):
        self.position_mobject_inside(mobject)
        self.content = mobject
        return self.content

    def write(self, text):
        self.add_content(TextMobject(text))
        return self

    def clear(self):
        self.add_content(VMobject())
        return self

class SpeechBubble(Bubble):
    CONFIG = {
        "file_name" : "Bubbles_speech.svg",
        "height" : 4
    }

class ThoughtBubble(Bubble):
    CONFIG = {
        "file_name" : "Bubbles_thought.svg",
    }

    def __init__(self, **kwargs):
        Bubble.__init__(self, **kwargs)
        self.submobjects.sort(
            lambda m1, m2 : int((m1.get_bottom()-m2.get_bottom())[1])
        )

    def make_green_screen(self):
        self.submobjects[-1].set_fill(GREEN_SCREEN, opacity = 1)
        return self


class TeacherStudentsScene(Scene):
    def setup(self):
        self.teacher = Mortimer()
        self.teacher.to_corner(DOWN + RIGHT)
        self.teacher.look(DOWN+LEFT)
        self.students = VMobject(*[
            Randolph(color = c)
            for c in BLUE_D, BLUE_C, BLUE_E
        ])
        self.students.arrange_submobjects(RIGHT)
        self.students.scale(0.8)
        self.students.to_corner(DOWN+LEFT)

        for pi_creature in self.get_everyone():
            pi_creature.bubble = None
        self.add(*self.get_everyone())

    def get_teacher(self):
        return self.teacher

    def get_students(self):
        return self.students.split()

    def get_everyone(self):
        return [self.get_teacher()] + self.get_students()

    def get_bubble_intro_animation(self, content, bubble_type,
                                   pi_creature,
                                   **bubble_kwargs):
        bubble = pi_creature.get_bubble(bubble_type, **bubble_kwargs)
        bubble.add_content(content)
        if pi_creature.bubble:
            content_intro_anims = [
                Transform(pi_creature.bubble, bubble),
                Transform(pi_creature.bubble.content, bubble.content)
            ]
        else:
            content_intro_anims = [
                FadeIn(bubble),
                Write(content),
            ]
            pi_creature.bubble = bubble 
        return content_intro_anims

    def introduce_bubble(self, content, bubble_type, pi_creature,
                         pi_creature_target_mode = None,
                         added_anims = [],
                         **bubble_kwargs):
        if isinstance(content, str):
            content = TextMobject(content)     
        content_intro_anims = self.get_bubble_intro_animation(
            content, bubble_type, pi_creature, **bubble_kwargs
        )

        if not pi_creature_target_mode:
            if bubble_type is "speech":
                pi_creature_target_mode = "speaking"
            else:
                pi_creature_target_mode = "pondering"

        for p in self.get_everyone():
            if p.bubble and p is not pi_creature:
                added_anims += [
                    FadeOut(p.bubble),
                    FadeOut(p.bubble.content)
                ]
                p.bubble = None
                added_anims.append(ApplyMethod(p.change_mode, "plain"))

        anims = added_anims + content_intro_anims + [
            ApplyMethod(
                pi_creature.change_mode, 
                pi_creature_target_mode,
            ),
        ]
        self.play(*anims)
        return pi_creature.bubble

    def teacher_says(self, content, **kwargs):
        return self.introduce_bubble(
            content, "speech", self.get_teacher(), **kwargs
        )

    def student_says(self, content, student_index = 1, **kwargs):
        student = self.get_students()[student_index]
        return self.introduce_bubble(content, "speech", student, **kwargs)

    def teacher_thinks(self, content, **kwargs):
        return self.introduce_bubble(
            content, "thought", self.get_teacher(), **kwargs
        )

    def student_thinks(self, content, student_index = 1, **kwargs):
        student = self.get_students()[student_index]
        return self.introduce_bubble(content, "thought", student, **kwargs)

    def random_blink(self, num_times = 1):
        for x in range(num_times):
            pi_creature = random.choice(self.get_everyone())
            self.play(Blink(pi_creature))
            self.dither()













