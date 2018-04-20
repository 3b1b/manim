from __future__ import absolute_import

import itertools as it
import numpy as np
import random

from constants import *

from mobject.types.vectorized_mobject import VGroup

from mobject.frame import ScreenRectangle
from mobject.svg.drawings import SpeechBubble
from mobject.svg.drawings import ThoughtBubble

from animation.transform import ApplyMethod
from animation.transform import ReplacementTransform
from animation.transform import Transform
from for_3b1b_videos.pi_creature import PiCreature
from for_3b1b_videos.pi_creature import Mortimer
from for_3b1b_videos.pi_creature import Randolph
from for_3b1b_videos.pi_creature_animations import Blink
from for_3b1b_videos.pi_creature_animations import PiCreatureBubbleIntroduction
from for_3b1b_videos.pi_creature_animations import RemovePiCreatureBubble
from scene.scene import Scene
from utils.rate_functions import squish_rate_func
from utils.rate_functions import there_and_back


class PiCreatureScene(Scene):
    CONFIG = {
        "total_wait_time": 0,
        "seconds_to_blink": 3,
        "pi_creatures_start_on_screen": True,
        "default_pi_creature_kwargs": {
            "color": GREY_BROWN,
            "flip_at_start": True,
        },
        "default_pi_creature_start_corner": DOWN + LEFT,
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
        pi_creature = PiCreature(**self.default_pi_creature_kwargs)
        pi_creature.to_corner(self.default_pi_creature_start_corner)
        return pi_creature

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
            lambda pi: pi in mobjects,
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
        on_screen_mobjects = self.camera.extract_mobject_family_members(
            self.get_mobjects()
        )

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
                bubble_class=bubble_class,
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
                bubble_class=bubble_class,
                bubble_kwargs=bubble_kwargs,
                target_mode=target_mode,
                **kwargs
            ))
        anims += [
            RemovePiCreatureBubble(pi, **bubble_removal_kwargs)
            for pi in pi_creatures_with_bubbles
        ]
        anims += added_anims

        self.play(*anims, **kwargs)

    def pi_creature_says(self, *args, **kwargs):
        self.introduce_bubble(
            *args,
            bubble_class=SpeechBubble,
            **kwargs
        )

    def pi_creature_thinks(self, *args, **kwargs):
        self.introduce_bubble(
            *args,
            bubble_class=ThoughtBubble,
            **kwargs
        )

    def say(self, *content, **kwargs):
        self.pi_creature_says(
            self.get_primary_pi_creature(), *content, **kwargs)

    def think(self, *content, **kwargs):
        self.pi_creature_thinks(
            self.get_primary_pi_creature(), *content, **kwargs)

    def compile_play_args_to_animation_list(self, *args):
        """
        Add animations so that all pi creatures look at the
        first mobject being animated with each .play call
        """
        animations = Scene.compile_play_args_to_animation_list(self, *args)
        if not self.any_pi_creatures_on_screen():
            return animations

        non_pi_creature_anims = filter(
            lambda anim: anim.mobject not in self.get_pi_creatures(),
            animations
        )
        if len(non_pi_creature_anims) == 0:
            return animations
        first_anim = non_pi_creature_anims[0]
        # Look at ending state
        first_anim.update(1)
        point_of_interest = first_anim.mobject.get_center()
        first_anim.update(0)

        for pi_creature in self.get_pi_creatures():
            if pi_creature not in self.get_mobjects():
                continue
            if pi_creature in first_anim.mobject.submobject_family():
                continue
            anims_with_pi_creature = filter(
                lambda anim: pi_creature in anim.mobject.submobject_family(),
                animations
            )
            for anim in anims_with_pi_creature:
                if isinstance(anim, Transform):
                    index = anim.mobject.submobject_family().index(pi_creature)
                    target_family = anim.target_mobject.submobject_family()
                    target = target_family[index]
                    if isinstance(target, PiCreature):
                        target.look_at(point_of_interest)
            if not anims_with_pi_creature:
                animations.append(
                    ApplyMethod(pi_creature.look_at, point_of_interest)
                )
        return animations

    def blink(self):
        self.play(Blink(random.choice(self.get_on_screen_pi_creatures())))

    def joint_blink(self, pi_creatures=None, shuffle=True, **kwargs):
        if pi_creatures is None:
            pi_creatures = self.get_on_screen_pi_creatures()
        creatures_list = list(pi_creatures)
        if shuffle:
            random.shuffle(creatures_list)

        def get_rate_func(pi):
            index = creatures_list.index(pi)
            proportion = float(index) / len(creatures_list)
            start_time = 0.8 * proportion
            return squish_rate_func(
                there_and_back,
                start_time, start_time + 0.2
            )

        self.play(*[
            Blink(pi, rate_func=get_rate_func(pi), **kwargs)
            for pi in creatures_list
        ])
        return self

    def wait(self, time=1, blink=True):
        while time >= 1:
            time_to_blink = self.total_wait_time % self.seconds_to_blink == 0
            if blink and self.any_pi_creatures_on_screen() and time_to_blink:
                self.blink()
                self.num_plays -= 1  # This shouldn't count as an animation
            else:
                self.non_blink_wait()
            time -= 1
            self.total_wait_time += 1
        if time > 0:
            self.non_blink_wait(time)
        return self

    def non_blink_wait(self, time=1):
        Scene.wait(self, time)
        return self

    def change_mode(self, mode):
        self.play(self.get_primary_pi_creature().change_mode, mode)

    def look_at(self, thing_to_look_at, pi_creatures=None):
        if pi_creatures is None:
            pi_creatures = self.get_pi_creatures()
        self.play(*it.chain(*[
            [pi.look_at, thing_to_look_at]
            for pi in pi_creatures
        ]))


class TeacherStudentsScene(PiCreatureScene):
    CONFIG = {
        "student_colors": [BLUE_D, BLUE_E, BLUE_C],
        "student_scale_factor": 0.8,
        "seconds_to_blink": 2,
        "screen_height": 3,
    }

    def setup(self):
        PiCreatureScene.setup(self)
        self.screen = ScreenRectangle(height=self.screen_height)
        self.screen.to_corner(UP + LEFT)
        self.hold_up_spot = self.teacher.get_corner(UP + LEFT) + MED_LARGE_BUFF * UP

    def create_pi_creatures(self):
        self.teacher = Mortimer(color = self.default_pi_creature_kwargs["color"])
        self.teacher.to_corner(DOWN + RIGHT)
        self.teacher.look(DOWN + LEFT)
        self.students = VGroup(*[
            Randolph(color=c)
            for c in self.student_colors
        ])
        self.students.arrange_submobjects(RIGHT)
        self.students.scale(self.student_scale_factor)
        self.students.to_corner(DOWN + LEFT)
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

    def change_all_student_modes(self, mode, **kwargs):
        self.change_student_modes(*[mode] * len(self.students), **kwargs)

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
            submobject_mode=submobject_mode,
            run_time=2
        )

    def zoom_in_on_thought_bubble(self, bubble=None, radius=FRAME_Y_RADIUS + FRAME_X_RADIUS):
        if bubble is None:
            for pi in self.get_pi_creatures():
                if hasattr(pi, "bubble") and isinstance(pi.bubble, ThoughtBubble):
                    bubble = pi.bubble
                    break
            if bubble is None:
                raise Exception("No pi creatures have a thought bubble")
        vect = -bubble.get_bubble_center()

        def func(point):
            centered = point + vect
            return radius * centered / np.linalg.norm(centered)
        self.play(*[
            ApplyPointwiseFunction(func, mob)
            for mob in self.get_mobjects()
        ])

    def teacher_holds_up(self, mobject, target_mode="raise_right_hand", **kwargs):
        mobject.move_to(self.hold_up_spot, DOWN)
        mobject.shift_onto_screen()
        mobject_copy = mobject.copy()
        mobject_copy.shift(DOWN)
        mobject_copy.fade(1)
        self.play(
            ReplacementTransform(mobject_copy, mobject),
            self.teacher.change, target_mode,
        )
