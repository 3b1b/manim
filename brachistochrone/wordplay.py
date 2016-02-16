import numpy as np
import itertools as it

from helpers import *

from mobject.tex_mobject import TexMobject, TextMobject, Brace
from mobject import Mobject
from mobject.image_mobject import \
    MobjectFromRegion, ImageMobject, MobjectFromPixelArray
from topics.three_dimensions import Stars

from animation import Animation
from animation.transform import \
    Transform, CounterclockwiseTransform, ApplyPointwiseFunction,\
    FadeIn, FadeOut, GrowFromCenter, ApplyFunction, ApplyMethod, \
    ShimmerIn
from animation.simple_animations import \
    ShowCreation, Homotopy, PhaseFlow, ApplyToCenters, DelayByOrder, \
    ShowPassingFlash
from animation.playground import TurnInsideOut, Vibrate
from topics.geometry import \
    Line, Circle, Square, Grid, Rectangle, Arrow, Dot, Point, \
    Arc, FilledRectangle
from topics.characters import Randolph, Mathematician
from topics.functions import ParametricFunction, FunctionGraph
from topics.number_line import NumberPlane
from region import Region, region_from_polygon_vertices
from scene import Scene


class DisectBrachistochroneWord(Scene):
    def construct(self):
        word = TextMobject(
            ["Bra", "chis", "to", "chrone"]
        )
        original_word = word.copy()
        dots = []
        for part in word.split():
            if dots:
                part.next_to(dots[-1], buff = 0.06)
            dot = TexMobject("\\cdot")
            dot.next_to(part, buff = 0.06)
            dots.append(dot)
        dots = Mobject(*dots[:-1])
        dots.shift(0.1*DOWN)
        Mobject(word, dots).center()
        overbrace1 = Brace(Mobject(*word.split()[:-1]), UP)
        overbrace2 = Brace(word.split()[-1], UP)
        shortest = TextMobject("Shortest")
        shortest.next_to(overbrace1, UP)
        shortest.highlight(YELLOW)
        time = TextMobject("Time")
        time.next_to(overbrace2, UP)
        time.highlight(YELLOW)
        chrono_example = TextMobject("As in ``Chronological''")
        chrono_example.scale(0.5)
        chrono_example.to_edge(RIGHT)
        chrono_example.shift(2*UP)
        chrono_example.highlight(BLUE_D)
        chrono_arrow = Arrow(word.split()[-1], chrono_example)
        chrono_arrow.highlight(BLUE_D)

        pronunciation = TextMobject(["/br", "e", "kist","e","kr$\\bar{o}$n/"])
        pronunciation.split()[1].rotate_in_place(np.pi)
        pronunciation.split()[3].rotate_in_place(np.pi) 
        pronunciation.scale(0.7)
        pronunciation.shift(DOWN)

        latin = TextMobject(list("Latin"))
        greek = TextMobject(list("Greek"))
        for mob in latin, greek:
            mob.to_edge(LEFT)
        question_mark = TextMobject("?").next_to(greek, buff = 0.1)
        stars = Stars().highlight(BLACK)
        stars.scale(0.5).shift(question_mark.get_center())

        self.play(Transform(original_word, word), ShowCreation(dots))
        self.play(ShimmerIn(pronunciation))
        self.dither()
        self.play(
            GrowFromCenter(overbrace1),
            GrowFromCenter(overbrace2)
        )
        self.dither()
        self.play(ShimmerIn(latin))
        self.play(FadeIn(question_mark))
        self.play(Transform(
            latin, greek,
            path_func = counterclockwise_path()
        ))
        self.dither()
        self.play(Transform(question_mark, stars))
        self.remove(stars)
        self.dither()
        self.play(ShimmerIn(shortest))
        self.play(ShimmerIn(time))
        self.dither()
        self.play(
            ShowCreation(chrono_arrow),
            ShimmerIn(chrono_example)
        )
        self.dither()