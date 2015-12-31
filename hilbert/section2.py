from mobject import Mobject, Point, Mobject1D
from mobject.tex_mobject import \
    TexMobject, TextMobject, Brace
from mobject.image_mobject import \
    ImageMobject, MobjectFromRegion

from scene import Scene

from animation import Animation
from animation.transform import \
    Transform, CounterclockwiseTransform, ApplyMethod,\
    GrowFromCenter, ClockwiseTransform, ApplyPointwiseFunction, \
    ShrinkToCenter
from animation.simple_animations import \
    ShowCreation, ShimmerIn, FadeOut, FadeIn
from animation.meta_animations import \
    DelayByOrder, TransformAnimations
from animation.playground import Vibrate

from topics.geometry import \
    Line, Dot, Arrow, Grid, Square, Point
from topics.characters import \
    ThoughtBubble, SpeechBubble, Mathematician
from topics.number_line import UnitInterval, NumberLine
from topics.three_dimensions import Stars

from region import region_from_polygon_vertices, Region

import displayer as disp

from hilbert.curves import \
    TransformOverIncreasingOrders, FlowSnake, HilbertCurve, \
    SnakeCurve, PeanoCurve
from hilbert.section1 import get_mathy_and_bubble

from scipy.spatial.distance import cdist

from helpers import *


def get_time_line():
    length = 5.2*SPACE_WIDTH
    year_range = 400
    time_line = NumberLine(
        numerical_radius = year_range/2,
        unit_length_to_spatial_width = length/year_range,
        tick_frequency = 10,
        leftmost_tick = 1720,
        number_at_center = 1870,
        numbers_with_elongated_ticks = range(1700, 2100, 100)
    )
    time_line.sort_points(lambda p : p[0])        
    time_line.gradient_highlight(
        PeanoCurve.DEFAULT_CONFIG["start_color"], 
        PeanoCurve.DEFAULT_CONFIG["end_color"]
    )
    time_line.add_numbers(
        2020, *range(1800, 2050, 50)
    )
    return time_line


class SectionTwo(Scene):
    def construct(self):
        self.add(TextMobject("Section 2: Filling space"))
        self.dither()

class HilbertCurveIsPerfect(Scene):
    def construct(self):
        curve = HilbertCurve(order = 6)
        curve.highlight(WHITE)
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
        bubble.sort_points(lambda p : np.dot(p, UP+RIGHT))

        self.add(mathy)
        self.dither()
        self.play(ApplyMethod(
            mathy.blink, 
            alpha_func = squish_alpha_func(there_and_back)
        ))
        self.dither()
        self.play(ShowCreation(bubble))
        self.dither()
        self.play(
            ApplyMethod(mathy.shift, 3*(DOWN+LEFT)),
            ApplyPointwiseFunction(
                lambda p : 15*p/np.linalg.norm(p),
                bubble
            ),
            run_time = 3
        )

class TimeLineAboutSpaceFilling(Scene):
    def construct(self):
        curve = PeanoCurve(order = 5)
        curve.stretch_to_fit_width(2*SPACE_WIDTH)
        curve.stretch_to_fit_height(2*SPACE_HEIGHT)
        curve_start = curve.copy()
        curve_start.apply_over_attr_arrays(
            lambda arr : arr[:200]
        )
        time_line = get_time_line()
        time_line.shift(-time_line.number_to_point(2000))

        self.add(time_line)
        self.play(ApplyMethod(
            time_line.shift,
            -time_line.number_to_point(1900),
            run_time = 3
        ))
        brace = Brace(
            Mobject(
                Point(time_line.number_to_point(1865)),
                Point(time_line.number_to_point(1888)),
            ),
            UP
        )
        words = TextMobject("""
            Cantor drives himself (and the \\\\
            mathematical community at large) \\\\
            crazy with research on infinity.
        """)
        words.next_to(brace, UP)
        self.play(
            GrowFromCenter(brace),
            ShimmerIn(words)
        )
        self.dither()
        self.play(
            Transform(time_line, curve_start),
            FadeOut(brace),
            FadeOut(words)
        )
        self.play(ShowCreation(
            curve, 
            run_time = 5,
            alpha_func = None
        ))
        self.dither()



class NotPixelatedSpace(Scene):
    def construct(self):
        grid = Grid(64, 64)
        space_region = Region()
        space_mobject = MobjectFromRegion(space_region, DARK_GREY)
        curve = PeanoCurve(order = 5).replace(space_mobject)
        line = Line(5*LEFT, 5*RIGHT)
        line.gradient_highlight(curve.start_color, curve.end_color)
        for mob in grid, space_mobject:
            mob.sort_points(np.linalg.norm)
        infinitely = TextMobject("Infinitely")
        detailed = TextMobject("detailed")
        extending = TextMobject("extending")
        detailed.next_to(infinitely, RIGHT)
        extending.next_to(infinitely, RIGHT)
        Mobject(extending, infinitely, detailed).center()
        arrows = Mobject(*[
            Arrow(2*p, 4*p)
            for theta in np.arange(np.pi/6, 2*np.pi, np.pi/3)
            for p in [rotate_vector(RIGHT, theta)]
        ])

        self.add(grid)
        self.dither()
        self.play(Transform(grid, space_mobject, run_time = 5))
        self.remove(grid)
        self.highlight_region(space_region, DARK_GREY)
        self.dither()
        self.add(infinitely, detailed)
        self.dither()
        self.play(DelayByOrder(Transform(detailed, extending)))
        self.play(ShowCreation(arrows))
        self.dither()
        self.clear()
        self.highlight_region(space_region, DARK_GREY)
        self.play(ShowCreation(line))
        self.play(Transform(line, curve, run_time = 5))



class HistoryOfDiscover(Scene):
    def construct(self):
        time_line = get_time_line()
        time_line.shift(-time_line.number_to_point(1900))
        hilbert_curve = HilbertCurve(order = 3)
        peano_curve = PeanoCurve(order = 2)
        for curve in hilbert_curve, peano_curve:
            curve.scale(0.5)
        hilbert_curve.to_corner(DOWN+RIGHT)
        peano_curve.to_corner(UP+LEFT)
        squares = Mobject(*[
            Square(side_length=3, color=WHITE).replace(curve)
            for curve in hilbert_curve, peano_curve
        ])


        self.add(time_line)
        self.dither()
        for year, curve, vect, text in [
            (1890, peano_curve, UP, "Peano Curve"), 
            (1891, hilbert_curve, DOWN, "Hilbert Curve"),
            ]:
            point = time_line.number_to_point(year)
            point[1] = 0.2
            arrow = Arrow(point+2*vect, point, buff = 0.1)
            arrow.gradient_highlight(curve.start_color, curve.end_color)
            year_mob = TexMobject(str(year))
            year_mob.next_to(arrow, vect)
            words = TextMobject(text)
            words.next_to(year_mob, vect)

            self.play(
                ShowCreation(arrow), 
                ShimmerIn(year_mob),
                ShimmerIn(words)
            )
            self.play(ShowCreation(curve))
            self.dither()
        self.play(ShowCreation(squares))
        self.dither()
        self.play(ApplyMethod(
            Mobject(*self.mobjects).shift, 20*(DOWN+RIGHT)
        ))



class DefinitionOfCurve(Scene):
    def construct(self):
        start_words = TextMobject([
            "``", "Space Filling", "Curve ''",
        ]).to_edge(TOP, buff = 0.25)
        quote, space_filling, curve_quote = start_words.copy().split()
        curve_quote.shift(
            space_filling.get_left()-\
            curve_quote.get_left()
        )
        space_filling = Point(space_filling.get_center())                
        end_words = Mobject(*[
            quote, space_filling, curve_quote
        ]).center().to_edge(TOP, buff = 0.25)
        space_filling_fractal = TextMobject("""
            ``Space Filling Fractal''
        """).to_edge(UP)
        curve = HilbertCurve(order = 2).shift(DOWN)
        fine_curve = HilbertCurve(order = 8)
        fine_curve.replace(curve)
        dots = Mobject(*[
            Dot(
                curve.points[n*curve.get_num_points()/15],
                color = YELLOW_C
            )
            for n in range(1, 15)
            if n not in [4, 11]
        ])

        start_words.shift(2*(UP+LEFT))
        self.play(
            ApplyMethod(start_words.shift, 2*(DOWN+RIGHT))
        )
        self.dither()
        self.play(Transform(start_words, end_words))
        self.dither()
        self.play(ShowCreation(curve))
        self.dither()
        self.play(ShowCreation(
            dots, 
            run_time = 3,
        ))
        self.dither()
        self.clear()
        self.play(ShowCreation(fine_curve, run_time = 5))
        self.dither()
        self.play(ShimmerIn(space_filling_fractal))
        self.dither()


class PseudoHilbertCurvesDontFillSpace(Scene):
    def construct(self):
        curve = HilbertCurve(order = 1)
        grid = Grid(2, 2, point_thickness=1)
        self.add(grid, curve)
        for order in range(2, 6):
            self.dither()
            new_grid = Grid(2**order, 2**order, point_thickness=1)
            self.play(
                ShowCreation(new_grid),
                Animation(curve)          
            )
            self.remove(grid)
            grid = new_grid
            self.play(Transform(
                curve, HilbertCurve(order = order)
            ))


        square = Square(side_length = 6, color = WHITE)
        square.corner = Mobject1D()
        square.corner.add_line(3*DOWN, ORIGIN)
        square.corner.add_line(ORIGIN, 3*RIGHT)
        square.digest_mobject_attrs()
        square.scale(2**(-5))
        square.corner.highlight(
            Color(rgb = curve.rgbs[curve.get_num_points()/3])
        )
        square.shift(
            grid.get_corner(UP+LEFT)-\
            square.get_corner(UP+LEFT)
        )


        self.dither()
        self.play(
            FadeOut(grid), 
            FadeOut(curve),
            FadeIn(square)
        )
        self.play(
            ApplyMethod(square.replace, grid)
        )
        self.dither()


class HilbertCurveIsLimit(Scene):
    def construct(self):
        mathy, bubble = get_mathy_and_bubble()
        bubble.write(
            "A Hilbert curve is the \\\\ limit of all these \\dots"
        )

        self.add(mathy, bubble)
        self.play(ShimmerIn(bubble.content))
        self.dither()


class DefiningCurves(Scene):
    def construct(self):
        words = TextMobject(
            ["One does not simply define the limit \\\\ \
            of a sequence of","curves","\\dots"]
        )
        top_words = TextMobject([
            "curves", "are functions"
        ]).to_edge(UP)
        curves1 = words.split()[1]
        curves2 = top_words.split()[0]
        words.ingest_sub_mobjects()
        number = TexMobject("0.27")
        pair = TexMobject("(0.53, 0.02)")
        pair.next_to(number, buff = 2)
        arrow = Arrow(number, pair)
        Mobject(number, arrow, pair).center().shift(UP)
        number_line = UnitInterval()
        number_line.stretch_to_fit_width(5)
        number_line.to_edge(LEFT).shift(DOWN)
        grid = Grid(4, 4).scale(0.4)
        grid.next_to(number_line, buff = 2)
        low_arrow = Arrow(number_line, grid)

        self.play(ShimmerIn(words))
        self.dither()
        self.play(
            FadeOut(words),
            ApplyMethod(curves1.replace, curves2),
            ShimmerIn(top_words.split()[1])
        )
        self.dither()
        self.play(FadeIn(number))
        self.play(ShowCreation(arrow))
        self.play(FadeIn(pair))
        self.dither()
        self.play(ShowCreation(number_line))
        self.play(ShowCreation(low_arrow))
        self.play(ShowCreation(grid))
        self.dither()


class PseudoHilbertCurveAsFunctionExample(Scene):
    args_list = [(2,), (3,)]

    # For subclasses to turn args in the above  
    # list into stings which can be appended to the name
    @staticmethod
    def args_to_string(order):
        return "Order%d"%order
        
    @staticmethod
    def string_to_args(order_str):
        return int(order_str)


    def construct(self, order):
        if order == 2:
            result_tex = "(0.125, 0.75)"
        elif order == 3:
            result_tex = "(0.0758,  0.6875)"

        phc, arg, result = TexMobject([
            "\\text{PHC}_%d"%order, 
            "(0.3)", 
            "= %s"%result_tex
        ]).to_edge(UP).split()
        function = TextMobject("Function", size = "\\normal")
        function.shift(phc.get_center()+DOWN+2*LEFT)
        function_arrow = Arrow(function, phc)

        line = Line(5*LEFT, 5*RIGHT)
        curve = HilbertCurve(order = order)
        line.match_colors(curve)
        grid = Grid(2**order, 2**order)
        grid.fade()
        for mob in curve, grid:
            mob.scale(0.7)
        index = int(0.3*line.get_num_points())
        dot1 = Dot(line.points[index])
        arrow1 = Arrow(arg, dot1, buff = 0.1)
        dot2 = Dot(curve.points[index])
        arrow2 = Arrow(result.get_bottom(), dot2, buff = 0.1)

        self.add(phc)
        self.play(
            ShimmerIn(function),
            ShowCreation(function_arrow)
        )
        self.dither()
        self.remove(function_arrow, function)
        self.play(ShowCreation(line))
        self.dither()
        self.play(
            ShimmerIn(arg),
            ShowCreation(arrow1),
            ShowCreation(dot1)
        )
        self.dither()
        self.remove(arrow1)
        self.play(
            FadeIn(grid),            
            Transform(line, curve),
            Transform(dot1, dot2),
            run_time = 2
        )
        self.dither()
        self.play(
            ShimmerIn(result),
            ShowCreation(arrow2)
        )
        self.dither()



class ContinuityRequired(Scene):
    def construct(self):
        words = TextMobject([
            "A function must be",
            "\\emph{continuous}", 
            "if it is to represent a curve."
        ])
        words.split()[1].highlight(YELLOW_C)
        self.add(words)
        self.dither()




class FormalDefinitionOfContinuity(Scene):
    def construct(self):
        self.play(ShimmerIn(TextMobject(" ".join([
            "$f : A \\to B$  is continuous if: \\\\ \n\n", 
            "$\\forall x \\in A$,",
            "$\\forall \\epsilon > 0$,",
            "$\\exists \\delta > 0$ such that",
            "$|f(y) - f(x)| < \\epsilon$",
            "for all $y \\in A$  satisfying $|x-y|<\\delta$.",
        ]))))
        self.dither()













