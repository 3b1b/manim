from helpers import *

from mobject import Mobject
from mobject.svg_mobject import SVGMobject
from mobject.vectorized_mobject import VMobject, VGroup
from mobject.tex_mobject import TextMobject, TexMobject

from topics.objects import Bubble, ThoughtBubble, SpeechBubble

from animation import Animation
from animation.transform import *
from animation.simple_animations import Write, ShowCreation, AnimationGroup
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
        "stroke_color" : BLACK,
        "fill_opacity" : 1.0,
        "propogate_style_to_family" : True,
        "height" : 3,
        "corner_scale_factor" : 0.75,
        "flip_at_start" : False,
        "is_looking_direction_purposeful" : False,
        "start_corner" : None,
        #Range of proportions along body where arms are
        "right_arm_range" : [0.55, 0.7],
        "left_arm_range" : [.34, .462],
    }
    def __init__(self, mode = "plain", **kwargs):
        self.parts_named = False
        try:
            svg_file = os.path.join(
                PI_CREATURE_DIR, 
                "PiCreatures_%s.svg"%mode
            )
            SVGMobject.__init__(self, file_name = svg_file, **kwargs)
        except:
            warnings.warn("No PiCreature design with mode %s"%mode)
            svg_file = os.path.join(
                PI_CREATURE_DIR, 
                "PiCreatures_plain.svg"
            )
            SVGMobject.__init__(self, file_name = svg_file, **kwargs)

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
        self.eye_parts = VGroup(self.eyes, self.pupils)
        self.parts_named = True

    def init_colors(self):
        SVGMobject.init_colors(self)
        if not self.parts_named:
            self.name_parts()
        self.mouth.set_fill(BLACK, opacity = 1)
        self.body.set_fill(self.color, opacity = 1)
        self.pupils.set_fill(BLACK, opacity = 1)
        self.eyes.set_fill(WHITE, opacity = 1)
        return self

    def copy(self):
        copy_mobject = SVGMobject.copy(self)
        copy_mobject.name_parts()
        return copy_mobject

    def highlight(self, color):
        self.body.set_fill(color)
        return self

    def change_mode(self, mode):
        new_self = self.__class__(
            mode = mode,
            color = self.color
        )
        new_self.scale_to_fit_height(self.get_height())
        if self.is_flipped() ^ new_self.is_flipped():
            new_self.flip()
        new_self.shift(self.eyes.get_center() - new_self.eyes.get_center())
        if hasattr(self, "purposeful_looking_direction"):
            new_self.look(self.purposeful_looking_direction)
        Transform(self, new_self).update(1)
        return self

    def look(self, direction):
        norm = np.linalg.norm(direction)
        if norm == 0:
            return
        direction /= norm
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

    def change(self, new_mode, look_at_arg = None):
        self.change_mode(new_mode)
        if look_at_arg is not None:
            self.look_at(look_at_arg)
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
        eye_parts = self.eye_parts
        eye_bottom_y = eye_parts.get_bottom()[1]
        eye_parts.apply_function(
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

    def get_bubble(self, *content, **kwargs):
        bubble_class = kwargs.get("bubble_class", ThoughtBubble)
        bubble = bubble_class(**kwargs)
        if len(content) > 0:
            if isinstance(content[0], str):
                content_mob = TextMobject(*content)
            else:
                content_mob = content[0]
            bubble.add_content(content_mob)
            if "height" not in kwargs and "width" not in kwargs:
                bubble.resize_to_content()
        bubble.pin_to(self)
        self.bubble = bubble
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

    def get_arm_copies(self):
        body = self.body
        return VGroup(*[
            body.copy().pointwise_become_partial(body, *alpha_range)
            for alpha_range in self.right_arm_range, self.left_arm_range
        ])
            
def get_all_pi_creature_modes():
    result = []
    prefix = "PiCreatures_"
    suffix = ".svg"
    for file in os.listdir(PI_CREATURE_DIR):
        if file.startswith(prefix) and file.endswith(suffix):
            result.append(
                file[len(prefix):-len(suffix)]
            )
    return result

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

class Eyes(VMobject):
    CONFIG = {
        "height" : 0.3,
        "thing_looked_at" : None,
        "mode" : "plain",
    }
    def __init__(self, mobject, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.mobject = mobject
        self.submobjects = self.get_eyes().submobjects

    def get_eyes(self, mode = None, thing_to_look_at = None):
        mode = mode or self.mode
        if thing_to_look_at is None:
            thing_to_look_at = self.thing_looked_at

        pi = Randolph(mode = mode)
        eyes = VGroup(pi.eyes, pi.pupils)
        eyes.scale_to_fit_height(self.height)
        if self.submobjects:
            eyes.move_to(self, DOWN)
        else:
            eyes.move_to(self.mobject.get_top(), DOWN)
        if thing_to_look_at is not None:
            pi.look_at(thing_to_look_at)
        return eyes

    def change_mode_anim(self, mode, **kwargs):
        self.mode = mode
        return Transform(self, self.get_eyes(mode = mode), **kwargs)

    def look_at_anim(self, point_or_mobject, **kwargs):
        self.thing_looked_at = point_or_mobject
        return Transform(
            self, self.get_eyes(thing_to_look_at = point_or_mobject), 
            **kwargs
        )

    def blink_anim(self, **kwargs):
        target = self.copy()
        bottom_y = self.get_bottom()[1]
        for submob in target:
            submob.apply_function(
                lambda p : [p[0], bottom_y, p[2]]
            )
        if "rate_func" not in kwargs:
            kwargs["rate_func"] = squish_rate_func(there_and_back)
        return Transform(self, target, **kwargs)

#######################

class PiCreatureBubbleIntroduction(AnimationGroup):
    CONFIG = {
        "target_mode" : "speaking",
        "bubble_class" : SpeechBubble,
        "change_mode_kwargs" : {},
        "bubble_creation_class" : ShowCreation,
        "bubble_creation_kwargs" : {},
        "bubble_kwargs" : {},
        "content_introduction_class" : Write,
        "content_introduction_kwargs" : {},
        "look_at_arg" : None,
    }
    def __init__(self, pi_creature, *content, **kwargs):
        digest_config(self, kwargs)
        bubble = pi_creature.get_bubble(
            *content,
            bubble_class = self.bubble_class,
            **self.bubble_kwargs
        )

        pi_creature.generate_target()
        pi_creature.target.change_mode(self.target_mode)
        if self.look_at_arg is not None:
            pi_creature.target.look_at(self.look_at_arg)

        change_mode = MoveToTarget(pi_creature, **self.change_mode_kwargs)
        bubble_creation = self.bubble_creation_class(
            bubble, **self.bubble_creation_kwargs
        )
        content_introduction = self.content_introduction_class(
            bubble.content, **self.content_introduction_kwargs
        )
        AnimationGroup.__init__(
            self, change_mode, bubble_creation, content_introduction,
            **kwargs
        )

class PiCreatureSays(PiCreatureBubbleIntroduction):
    CONFIG = {
        "target_mode" : "speaking",
        "bubble_class" : SpeechBubble,
    }

class RemovePiCreatureBubble(AnimationGroup):
    CONFIG = {
        "target_mode" : "plain",
        "look_at_arg" : None,
        "remover" : True,
    }
    def __init__(self, pi_creature, **kwargs):
        assert hasattr(pi_creature, "bubble")
        digest_config(self, kwargs, locals())

        pi_creature.generate_target()
        pi_creature.target.change_mode(self.target_mode)
        if self.look_at_arg is not None:
            pi_creature.target.look_at(self.look_at_arg)

        AnimationGroup.__init__(
            self,
            MoveToTarget(pi_creature),
            FadeOut(pi_creature.bubble),
            FadeOut(pi_creature.bubble.content),
        )

    def clean_up(self, surrounding_scene = None):
        AnimationGroup.clean_up(self, surrounding_scene)
        self.pi_creature.bubble = None
        if surrounding_scene is not None:
            surrounding_scene.add(self.pi_creature)

###########

class PiCreatureScene(Scene):
    CONFIG = {
        "total_dither_time" : 0,
        "seconds_to_blink" : 3,
        "pi_creatures_start_on_screen" : True,
    }
    def setup(self):
        self.pi_creatures = VGroup(*self.create_pi_creatures())
        self.pi_creature = self.get_primary_pi_creature()
        if self.pi_creatures_start_on_screen:
            self.add(*self.pi_creatures)

    def create_pi_creatures(self):
        """ 
        Likely updated for subclasses 
        """
        return VGroup(self.create_pi_creature())

    def create_pi_creature(self):
        return Mortimer().to_corner(DOWN+RIGHT)

    def get_pi_creatures(self):
        return self.pi_creatures

    def get_primary_pi_creature(self):
        return self.pi_creatures[0]

    def any_pi_creatures_on_screen(self):
        mobjects = self.get_mobjects()
        return any([pi in mobjects for pi in self.get_pi_creatures()])

    def get_on_screen_pi_creatures(self):
        mobjects = self.get_mobjects()
        return VGroup(*filter(
            lambda pi : pi in mobjects,
            self.get_pi_creatures()
        ))

    def introduce_bubble(self, *args, **kwargs):
        if isinstance(args[0], PiCreature):
            pi_creature = args[0]
            content = args[1:]
        else:
            pi_creature = self.get_primary_pi_creature()
            content = args

        bubble_class = kwargs.pop("bubble_class", SpeechBubble)
        target_mode = kwargs.pop(
            "target_mode", 
            "thinking" if bubble_class is ThoughtBubble else "speaking"
        )
        bubble_kwargs = kwargs.pop("bubble_kwargs", {})
        bubble_removal_kwargs = kwargs.pop("bubble_removal_kwargs", {})
        added_anims = kwargs.pop("added_anims", [])

        anims = []
        on_screen_mobjects = self.get_mobjects()
        def has_bubble(pi):
            return hasattr(pi, "bubble") and \
                   pi.bubble is not None and \
                   pi.bubble in on_screen_mobjects

        pi_creatures_with_bubbles = filter(has_bubble, self.get_pi_creatures())
        if pi_creature in pi_creatures_with_bubbles:
            pi_creatures_with_bubbles.remove(pi_creature)
            old_bubble = pi_creature.bubble
            bubble = pi_creature.get_bubble(
                *content,
                bubble_class = bubble_class,
                **bubble_kwargs
            )
            anims += [
                ReplacementTransform(old_bubble, bubble),
                ReplacementTransform(old_bubble.content, bubble.content),
                pi_creature.change_mode, target_mode
            ]
        else:
            anims.append(PiCreatureBubbleIntroduction(
                pi_creature,
                *content,
                bubble_class = bubble_class,
                bubble_kwargs = bubble_kwargs,
                target_mode = target_mode,
                **kwargs
            ))
        anims += [
            RemovePiCreatureBubble(pi, **bubble_removal_kwargs)
            for pi in pi_creatures_with_bubbles
        ]
        anims += added_anims

        self.play(*anims)

    def pi_creature_says(self, *args, **kwargs):
        self.introduce_bubble(
            *args,
            bubble_class = SpeechBubble,
            **kwargs
        )

    def pi_creature_thinks(self, *args, **kwargs):
        self.introduce_bubble(
            *args,
            bubble_class = ThoughtBubble,
            **kwargs
        )

    def say(self, *content, **kwargs):
        self.pi_creature_says(self.get_primary_pi_creature(), *content, **kwargs)

    def think(self, *content, **kwargs):
        self.pi_creature_thinks(self.get_primary_pi_creature(), *content, **kwargs)

    def compile_play_args_to_animation_list(self, *args):
        """
        Add animations so that all pi creatures look at the 
        first mobject being animated with each .play call
        """
        animations = Scene.compile_play_args_to_animation_list(self, *args)
        if not self.any_pi_creatures_on_screen():
            return animations

        non_pi_creature_anims = filter(
            lambda anim : anim.mobject not in self.get_pi_creatures(),
            animations
        )
        if len(non_pi_creature_anims) == 0:
            return animations
        first_anim = non_pi_creature_anims[0]
        #Look at ending state
        first_anim.update(1)
        point_of_interest = first_anim.mobject.get_center()
        first_anim.update(0)

        for pi_creature in self.get_pi_creatures():
            if pi_creature not in self.get_mobjects():
                continue
            if pi_creature in first_anim.mobject.submobject_family():
                continue
            anims_with_pi_creature = filter(
                lambda anim : pi_creature in anim.mobject.submobject_family(),
                animations
            )
            if anims_with_pi_creature:
                for anim in anims_with_pi_creature:
                    if isinstance(anim, Transform):
                        index = anim.mobject.submobject_family().index(pi_creature)
                        target_family = anim.target_mobject.submobject_family()
                        target = target_family[index]
                        if isinstance(target, PiCreature):
                            target.look_at(point_of_interest)
                continue
            animations.append(
                ApplyMethod(pi_creature.look_at, point_of_interest)
            )
        return animations

    def blink(self):
        self.play(Blink(random.choice(self.get_on_screen_pi_creatures())))

    def joint_blink(self, pi_creatures = None, shuffle = True, **kwargs):
        if pi_creatures is None:
            pi_creatures = self.get_on_screen_pi_creatures()
        creatures_list = list(pi_creatures)
        if shuffle:
            random.shuffle(creatures_list)

        def get_rate_func(pi):
            index = creatures_list.index(pi)
            proportion = float(index)/len(creatures_list)
            start_time = 0.8*proportion
            return squish_rate_func(
                there_and_back,
                start_time, start_time + 0.2
            )

        self.play(*[
            Blink(pi, rate_func = get_rate_func(pi), **kwargs)
            for pi in creatures_list
        ])
        return self

    def dither(self, time = 1, blink = True):
        while time >= 1:
            time_to_blink = self.total_dither_time%self.seconds_to_blink == 0
            if blink and self.any_pi_creatures_on_screen() and time_to_blink:
                self.blink()
            else:
                self.non_blink_dither()
            time -= 1
            self.total_dither_time += 1
        if time > 0:
            self.non_blink_dither(time)
        return self

    def non_blink_dither(self, time = 1):
        Scene.dither(self, time)
        return self

    def change_mode(self, mode):
        self.play(self.get_primary_pi_creature().change_mode, mode)

    def look_at(self, thing_to_look_at, pi_creatures = None):
        if pi_creatures is None:
            pi_creatures = self.get_pi_creatures()
        self.play(*it.chain(*[
            [pi.look_at, thing_to_look_at]
            for pi in pi_creatures
        ]))

class TeacherStudentsScene(PiCreatureScene):
    CONFIG = {
        "student_colors" : [BLUE_D, BLUE_E, BLUE_C],
        "student_scale_factor" : 0.8,
        "seconds_to_blink" : 2,
    }
    def create_pi_creatures(self):
        self.teacher = Mortimer()
        self.teacher.to_corner(DOWN + RIGHT)
        self.teacher.look(DOWN+LEFT)
        self.students = VGroup(*[
            Randolph(color = c)
            for c in self.student_colors
        ])
        self.students.arrange_submobjects(RIGHT)
        self.students.scale(self.student_scale_factor)
        self.students.to_corner(DOWN+LEFT)
        self.teacher.look_at(self.students[-1].eyes)
        for student in self.students:
            student.look_at(self.teacher.eyes)

        return [self.teacher] + list(self.students)

    def get_teacher(self):
        return self.teacher

    def get_students(self):
        return self.students

    def teacher_says(self, *content, **kwargs):
        return self.pi_creature_says(
            self.get_teacher(), *content, **kwargs
        )

    def student_says(self, *content, **kwargs):
        if "target_mode" not in kwargs:
            target_mode = random.choice([
                "raise_right_hand", 
                "raise_left_hand", 
            ])
            kwargs["target_mode"] = target_mode
        student = self.get_students()[kwargs.get("student_index", 1)]
        return self.pi_creature_says(
            student, *content, **kwargs
        )

    def teacher_thinks(self, *content, **kwargs):
        return self.pi_creature_thinks(
            self.get_teacher(), *content, **kwargs
        )

    def student_thinks(self, *content, **kwargs):
        student = self.get_students()[kwargs.get("student_index", 1)]
        return self.pi_creature_thinks(student, *content, **kwargs)

    def change_student_modes(self, *modes, **kwargs):
        added_anims = kwargs.pop("added_anims", [])
        self.play(
            self.get_student_changes(*modes, **kwargs),
            *added_anims
        )

    def get_student_changes(self, *modes, **kwargs):
        pairs = zip(self.get_students(), modes)
        pairs = [(s, m) for s, m in pairs if m is not None]
        start = VGroup(*[s for s, m in pairs])
        target = VGroup(*[s.copy().change_mode(m) for s, m in pairs])
        if "look_at_arg" in kwargs:
            for pi in target:
                pi.look_at(kwargs["look_at_arg"])
        submobject_mode = kwargs.get("submobject_mode", "lagged_start")
        return Transform(
            start, target, 
            submobject_mode = submobject_mode,
            run_time = 2
        )

    def zoom_in_on_thought_bubble(self, bubble = None, radius = SPACE_HEIGHT+SPACE_WIDTH):
        if bubble is None:
            for pi in self.get_pi_creatures():
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













