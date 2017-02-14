from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from scene import Scene
from scene.zoomed_scene import ZoomedScene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from eoc.chapter1 import OpeningQuote, PatreonThanks
from eoc.graph_scene import *


class Chapter3OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            "Using the chain rule is like peeling an onion: ",
            "you have to deal with each layer at a time, and ",
            "if it is too big you will start crying."
        ],
        "author" : "(Anonymous professor)"
    }

class TransitionFromLastVideo(TeacherStudentsScene):
    def construct(self):
        simple_rules = VGroup(*map(TexMobject, [
            "\\frac{d(x^3)}{dx} = 3x^2",
            "\\frac{d(\\sin(x))}{dx} = \\cos(x)",
            "\\frac{d(e^x)}{dx} = e^x",
        ]))

        combination_rules = VGroup(*[
            TexMobject("\\frac{d}{dx}\\left(%s\\right)"%tex)
            for tex in [
                "\\sin(x) + x^2",
                "\\sin(x)(x^2)",
                "\\sin(x^2)",
            ]
        ])
        for rules in simple_rules, combination_rules:
            rules.arrange_submobjects(buff = LARGE_BUFF)
            rules.next_to(self.get_teacher(), UP, buff = MED_LARGE_BUFF)
            rules.to_edge(LEFT)

        series = VideoSeries()
        series.to_edge(UP)
        last_video = series[2]
        last_video.save_state()
        this_video = series[3]
        brace = Brace(last_video)

        #Simple rules
        self.add(series)
        self.play(
            FadeIn(brace),
            last_video.highlight, YELLOW
        )
        for rule in simple_rules:
            self.play(
                Write(rule, run_time = 1),
                self.get_teacher().change_mode, "raise_right_hand",
                *[
                    ApplyMethod(pi.change_mode, "pondering")
                    for pi in self.get_students()
                ]
            )
        self.dither(2)
        self.play(simple_rules.replace, last_video)
        self.play(
            last_video.restore,            
            Animation(simple_rules),
            brace.next_to, this_video, DOWN,
            this_video.highlight, YELLOW
        )

        #Combination rules
        self.play(
            Write(combination_rules),
            *[
                ApplyMethod(pi.change_mode, "confused")
                for pi in self.get_students()
            ]
        )
        self.dither(2)
        for rule in combination_rules:
            interior = VGroup(*rule[5:-1])
            added_anims = []
            if rule is combination_rules[-1]:
                inner_func = VGroup(*rule[-4:-2])
                self.play(inner_func.shift, 0.5*UP)
                added_anims = [
                    inner_func.shift, 0.5*DOWN,
                    inner_func.highlight, YELLOW
                ]
            self.play(
                interior.highlight, YELLOW,
                *added_anims,
                submobject_mode = "lagged_start"
            )
            self.dither()
        self.dither()

        #Address subtraction and division
        subtraction = TexMobject("\\sin(x)", "-", "x^2")
        decomposed_subtraction = TexMobject("\\sin(x)", "+(-1)\\cdot", "x^2")
        pre_division = TexMobject("\\frac{\\sin(x)}{x^2}")
        division = VGroup(
            VGroup(*pre_division[:6]),
            VGroup(*pre_division[6:7]),
            VGroup(*pre_division[7:]),
        )
        pre_decomposed_division = TexMobject("\\sin(x)\\cdot\\frac{1}{x^2}")
        decomposed_division = VGroup(
            VGroup(*pre_decomposed_division[:6]),
            VGroup(*pre_decomposed_division[6:9]),
            VGroup(*pre_decomposed_division[9:]),
        )
        for mob in subtraction, decomposed_subtraction, division, decomposed_division:
            mob.next_to(self.get_teacher(), UP+LEFT)

        top_group = VGroup(series, simple_rules, brace)
        combination_rules.save_state()
        self.play(
            top_group.next_to, SPACE_HEIGHT*UP, UP,
            combination_rules.to_edge, UP,
        )
        pairs = [
            (subtraction, decomposed_subtraction), 
            (division, decomposed_division)
        ]
        for question, answer in pairs:
            self.play(
                Write(question),
                combination_rules.fade, 0.2,
                self.get_students()[2].change_mode, "raise_right_hand",
                self.get_teacher().change_mode, "plain",
            )
            self.dither()
            answer[1].highlight(GREEN)
            self.play(
                Transform(question, answer),
                self.get_teacher().change_mode, "hooray",
                self.get_students()[2].change_mode, "plain",
            )
            self.dither()
            self.play(FadeOut(question))

        #Monstrous expression
        monster = TexMobject(
            "\\Big(",
            "e^{\\sin(x)} \\cdot",
            "\\cos\\big(",
            "\\frac{1}{x^3}",
            " + x^3",
            "\\big)",
            "\\Big)^4"
        )
        monster.next_to(self.get_pi_creatures(), UP)
        parts = [
            VGroup(*monster[3][2:]),
            VGroup(*monster[3][:2]),
            monster[4],
            VGroup(monster[2], monster[5]),
            monster[1],
            VGroup(monster[0], monster[6])
        ]
        modes = [
            "erm", "erm",
            "confused", 
            "sad", "sad",
            "pleading",
        ]
        for part, mode in zip(parts, modes):
            self.play(
                FadeIn(part, submobject_mode = "lagged_start"),
                self.get_teacher().change_mode, "raise_right_hand",
                *[
                    ApplyMethod(pi.change_mode, mode)
                    for pi in self.get_students()
                ]
            )
        self.dither(2)

        #Bring back combinations
        self.play(
            FadeOut(monster),
            combination_rules.restore,
            *[
                ApplyMethod(pi_creature.change_mode, "pondering")
                for pi_creature in self.get_pi_creatures()
            ]
        )
        self.dither(2)



















































