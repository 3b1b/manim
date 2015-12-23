from mobject import Mobject, Point
from mobject.tex_mobject import \
    TexMobject, TextMobject, Brace
from mobject.image_mobject import \
    ImageMobject, MobjectFromRegion

from scene import Scene

from animation import Animation
from animation.transform import \
    Transform, CounterclockwiseTransform, ApplyMethod,\
    GrowFromCenter, ClockwiseTransform, ApplyPointwiseFunction
from animation.simple_animations import \
    ShowCreation, ShimmerIn, FadeOut, FadeIn
from animation.meta_animations import \
    DelayByOrder, TransformAnimations
from animation.playground import Vibrate

from topics.geometry import \
    Line, Dot, Arrow, Grid, Square, Point
from topics.characters import \
    ThoughtBubble, SpeechBubble, Mathematician
from topics.number_line import UnitInterval
from topics.three_dimensions import Stars

from region import region_from_polygon_vertices

import displayer as disp

from hilbert.curves import \
    TransformOverIncreasingOrders, FlowSnake, HilbertCurve, \
    SnakeCurve

from section1 import get_mathy_and_bubble

from scipy.spatial.distance import cdist

from helpers import *


class SectionTwo(Scene):
    def construct(self):
        self.add(TextMobject("Section 2: Filling space"))
        self.dither()

class HilbertCurveIsPerfect(Scene):
    def construct(self):
        curve = HilbertCurve(order = 6)
        colored_curve = curve.copy()
        colored_curve.thin_out(3)
        lion = ImageMobject("lion", invert = False)
        lion.replace(curve, stretch = True)
        sparce_lion = lion.copy()
        sparce_lion.thin_out(100)
        distance_matrix = cdist(colored_curve.points, sparce_lion.points)
        closest_point_indices = np.apply_along_axis(
            np.argmin, 1, distance_matrix
        )
        colored_curve.rgbs = sparce_lion.rgbs[closest_point_indices]
        line = Line(5*LEFT, 5*RIGHT)
        Mobject.align_data(line, colored_curve)
        line.rgbs = colored_curve.rgbs

        self.add(lion)
        self.play(ShowCreation(curve, run_time = 3))
        self.play(
            FadeOut(lion),
            Transform(curve, colored_curve),
            run_time = 3
        )
        self.dither()
        self.play(Transform(curve, line, run_time = 5))
        self.dither()


class AskMathematicianFriend(Scene):
    def construct(self):
        mathy, bubble = get_mathy_and_bubble()

























