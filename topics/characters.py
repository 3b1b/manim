from helpers import *

from mobject import Mobject
from mobject.svg_mobject import SVGMobject
from mobject.vectorized_mobject import VMobject, VGroup
from mobject.tex_mobject import TextMobject, TexMobject

from topics.objects import Bubble, ThoughtBubble, SpeechBubble

from animation import Animation
from animation.transform import Transform, ApplyMethod, \
    FadeOut, FadeIn, ApplyPointwiseFunction
from animation.simple_animations import Write
from scene import Scene


PI_CREATURE_DIR = os.path.join(IMAGE_DIR, "PiCreature")
PI_CREATURE_SCALE_FACTOR = 0.5

LEFT_EYE_INDEX    = 0
RIGHT_EYE_INDEX   = 1
LEFT_PUPIL_INDEX  = 2
RIGHT_PUPIL_INDEX = 3
BODY_INDEX        = 4
MOUTH_INDEX       = 5


class PiCreature(SVGMobject):
    CONFIG = {
        "color" : BLUE_E,
        "stroke_width" : 0,
        "fill_opacity" : 1.0,
        "initial_scale_factor" : 0.01,
        "corner_scale_factor" : 0.75,
        "flip_at_start" : False,
        "is_looking_direction_purposeful" : False,
        "start_corner" : None,
    }
    def __init__(self, mode = "plain", **kwargs):
        self.parts_named = False
        svg_file = os.path.join(
            PI_CREATURE_DIR, 
            "PiCreatures_%s.svg"%mode
        )
        digest_config(self, kwargs, locals())
        SVGMobject.__init__(self, file_name = svg_file, **kwargs)
        self.init_colors()
        if self.flip_at_start:
            self.flip()
        if self.start_corner is not None:
            self.to_corner(self.start_corner)

    def name_parts(self):
        self.mouth = self.submobjects[MOUTH_INDEX]
        self.body = self.submobjects[BODY_INDEX]
        self.pupils = VGroup(*[
            self.submobjects[LEFT_PUPIL_INDEX],
            self.submobjects[RIGHT_PUPIL_INDEX]
        ])
        self.eyes = VGroup(*[
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

    def change_mode(self, mode):
        curr_eye_center = self.eyes.get_center()
        curr_height = self.get_height()
        should_be_flipped = self.is_flipped()
        should_look = hasattr(self, "purposeful_looking_direction")
        if should_look:
            looking_direction = self.purposeful_looking_direction
        self.__init__(mode)
        self.scale_to_fit_height(curr_height)
        self.shift(curr_eye_center - self.eyes.get_center())
        if should_be_flipped ^ self.is_flipped():
            self.flip()
        if should_look:
            self.look(looking_direction)
        return self

    def look(self, direction):
        direction = direction/np.linalg.norm(direction)
        self.purposeful_looking_direction = direction
        for pupil, eye in zip(self.pupils.split(), self.eyes.split()):
            pupil_radius = pupil.get_width()/2.
            eye_radius = eye.get_width()/2.
            pupil.move_to(eye)
            if direction[1] < 0:
                pupil.shift(pupil_radius*DOWN/3)
            pupil.shift(direction*(eye_radius-pupil_radius))
            bottom_diff = eye.get_bottom()[1] - pupil.get_bottom()[1]
            if bottom_diff > 0:
                pupil.shift(bottom_diff*UP)
            #TODO, how to handle looking up...
            # top_diff = eye.get_top()[1]-pupil.get_top()[1]
            # if top_diff < 0:
            #     pupil.shift(top_diff*UP)
        return self

    def look_at(self, point_or_mobject):
        if isinstance(point_or_mobject, Mobject):
            point = point_or_mobject.get_center()
        else:
            point = point_or_mobject
        self.look(point - self.eyes.get_center())
        return self


    def get_looking_direction(self):
        return np.sign(np.round(
            self.pupils.get_center() - self.eyes.get_center(),
            decimals = 2
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

    def to_corner(self, vect = None, **kwargs):
        if vect is not None:
            SVGMobject.to_corner(self, vect, **kwargs)
        else:
            self.scale(self.corner_scale_factor)
            self.to_corner(DOWN+LEFT, **kwargs)
        return self

    def get_bubble(self, bubble_type = "thought", **kwargs):
        #TODO, change bubble_type arg to have type Bubble
        if bubble_type == "thought":
            bubble = ThoughtBubble(**kwargs)
        elif bubble_type == "speech":
            bubble = SpeechBubble(**kwargs)
        else:
            raise Exception("%s is an invalid bubble type"%bubble_type)
        bubble.pin_to(self)
        return bubble

    def make_eye_contact(self, pi_creature):
        self.look_at(pi_creature.eyes)
        pi_creature.look_at(self.eyes)
        return self

    def shrug(self):
        self.change_mode("shruggie")
        top_mouth_point, bottom_mouth_point = [
            self.mouth.points[np.argmax(self.mouth.points[:,1])],
            self.mouth.points[np.argmin(self.mouth.points[:,1])]
        ]
        self.look(top_mouth_point - bottom_mouth_point)
        return self
            


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

class BabyPiCreature(PiCreature):
    CONFIG = {
        "scale_factor" : 0.5,
        "eye_scale_factor" : 1.2,
        "pupil_scale_factor" : 1.3
    }
    def __init__(self, *args, **kwargs):
        PiCreature.__init__(self, *args, **kwargs)
        self.scale(self.scale_factor)
        self.shift(LEFT)
        self.to_edge(DOWN, buff = LARGE_BUFF)
        eyes = VGroup(self.eyes, self.pupils)
        eyes_bottom = eyes.get_bottom()
        eyes.scale(self.eye_scale_factor)
        eyes.move_to(eyes_bottom, aligned_edge = DOWN)
        looking_direction = self.get_looking_direction()
        for pupil in self.pupils:
            pupil.scale_in_place(self.pupil_scale_factor)
        self.look(looking_direction)
        


class Blink(ApplyMethod):
    CONFIG = {
        "rate_func" : squish_rate_func(there_and_back)
    }
    def __init__(self, pi_creature, **kwargs):
        ApplyMethod.__init__(self, pi_creature.blink, **kwargs)



class PiCreatureScene(Scene):
    CONFIG = {
        "total_dither_time" : 0
    }
    def setup(self):
        self.pi_creature = self.get_pi_creature()
        self.add(self.pi_creature)

    def get_pi_creature(self):
        return Randolph().to_corner()

    def play(self, *args, **kwargs):
        if self.pi_creature not in self.get_mobjects():
            Scene.play(self, *args, **kwargs)
            return

        if inspect.ismethod(args[0]):
            mobject_of_interest = args[0].im_self
        elif isinstance(args[0], Transform):
            if args[0].mobject is self.pi_creature:
                mobject_of_interest = self.pi_creature
            else:
                mobject_of_interest = args[0].ending_mobject
        elif isinstance(args[0], Animation):
            mobject_of_interest = args[0].mobject
        else:
            raise Exception("Invalid play args")

        if mobject_of_interest is self.pi_creature:
            new_anims = []
        else:
            new_anims = [self.pi_creature.look_at, mobject_of_interest]
        Scene.play(self, *list(args) + new_anims, **kwargs)

    def dither(self, time = 1, blink = True):
        while time > 0:
            if blink and self.total_dither_time%2 == 1:
                self.play(Blink(self.pi_creature))
            else:
                Scene.dither(self, time)
            time -= 1
            self.total_dither_time += 1
        return self

    def change_mode(self, mode):
        self.play(self.pi_creature.change_mode, mode)


class TeacherStudentsScene(Scene):
    def setup(self):
        self.teacher = Mortimer()
        self.teacher.to_corner(DOWN + RIGHT)
        self.teacher.look(DOWN+LEFT)
        self.students = VGroup(*[
            Randolph(color = c)
            for c in BLUE_D, BLUE_C, BLUE_E
        ])
        self.students.arrange_submobjects(RIGHT)
        self.students.scale(0.8)
        self.students.to_corner(DOWN+LEFT)
        self.teacher.look_at(self.students[-1].eyes)
        for student in self.students:
            student.look_at(self.teacher.eyes)

        for pi_creature in self.get_everyone():
            pi_creature.bubble = None
        self.add(*self.get_everyone())

    def get_teacher(self):
        return self.teacher

    def get_students(self):
        return self.students

    def get_everyone(self):
        return [self.get_teacher()] + list(self.get_students())

    def get_bubble_intro_animation(self, content, bubble_type,
                                   pi_creature,
                                   **bubble_kwargs):
        bubble = pi_creature.get_bubble(bubble_type, **bubble_kwargs)
        bubble.add_content(content)
        bubble.resize_to_content()
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
                         target_mode = None,
                         added_anims = [],
                         **bubble_kwargs):
        if all(map(lambda s : isinstance(s, str), content)):
            content = TextMobject(*content)
        elif len(content) == 1 and isinstance(content[0], Mobject):
            content = content[0]
        else:
            raise Exception("Invalid content type")
        content_intro_anims = self.get_bubble_intro_animation(
            content, bubble_type, pi_creature, **bubble_kwargs
        )

        if not target_mode:
            if bubble_type is "speech":
                target_mode = "speaking"
            else:
                target_mode = "pondering"

        for p in self.get_everyone():
            if (p.bubble is not None) and (p is not pi_creature):
                added_anims += [
                    FadeOut(p.bubble),
                    FadeOut(p.bubble.content)
                ]
                p.bubble = None
                added_anims.append(ApplyMethod(p.change_mode, "plain"))

        anims = added_anims + content_intro_anims + [
            ApplyMethod(
                pi_creature.change_mode, 
                target_mode,
            ),
        ]
        self.play(*anims)
        return pi_creature.bubble

    def teacher_says(self, *content, **kwargs):
        return self.introduce_bubble(
            content, "speech", self.get_teacher(), **kwargs
        )

    def student_says(self, *content, **kwargs):
        if "target_mode" not in kwargs:
            target_mode = random.choice([
                "raise_right_hand", 
                "raise_left_hand", 
            ])
            kwargs["target_mode"] = target_mode
        student = self.get_students()[kwargs.get("student_index", 1)]
        return self.introduce_bubble(content, "speech", student, **kwargs)

    def teacher_thinks(self, *content, **kwargs):
        return self.introduce_bubble(
            content, "thought", self.get_teacher(), **kwargs
        )

    def student_thinks(self, *content, **kwargs):
        student = self.get_students()[kwargs.get("student_index", 1)]
        return self.introduce_bubble(content, "thought", student, **kwargs)

    def random_blink(self, num_times = 1):
        for x in range(num_times):
            pi_creature = random.choice(self.get_everyone())
            self.play(Blink(pi_creature))
            self.dither()

    def change_student_modes(self, *modes, **kwargs):
        added_anims = kwargs.get("added_anims", [])
        pairs = zip(self.get_students(), modes)
        start = VGroup(*[s for s, m in pairs])
        target = VGroup(*[s.copy().change_mode(m) for s, m in pairs])
        self.play(
            Transform(
                start, target, 
                submobject_mode = "lagged_start",
                run_time = 2
            ),
            *added_anims
        )


    def zoom_in_on_thought_bubble(self, bubble = None, radius = SPACE_HEIGHT+SPACE_WIDTH):
        if bubble is None:
            for pi in self.get_everyone():
                if hasattr(pi, "bubble") and isinstance(pi.bubble, ThoughtBubble):
                    bubble = pi.bubble
                    break
            if bubble is None:
                raise Exception("No pi creatures have a thought bubble")
        vect = -bubble.get_bubble_center()
        def func(point):
            centered = point+vect
            return radius*centered/np.linalg.norm(centered)
        self.play(*[
            ApplyPointwiseFunction(func, mob)
            for mob in self.get_mobjects()
        ])













