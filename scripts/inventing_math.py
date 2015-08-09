#!/usr/bin/env python

import numpy as np
import itertools as it
from copy import deepcopy
import sys
import operator as op
from random import sample


from animation import *
from mobject import *
from constants import *
from region import *
from scene import Scene, RearrangeEquation
from script_wrapper import command_line_create_scene

from inventing_math_images import *

MOVIE_PREFIX = "inventing_math/"
DIVERGENT_SUM_TEXT = [
    "1", 
    "+2", 
    "+4", 
    "+8", 
    "+\\cdots",
    "+2^n",
    "+\\cdots", 
    "= -1",
]

CONVERGENT_SUM_TEXT = [
    "\\frac{1}{2}",
    "+\\frac{1}{4}",
    "+\\frac{1}{8}",
    "+\\frac{1}{16}",
    "+\\cdots",
    "+\\frac{1}{2^n}",
    "+\\cdots",
    "=1",
]

CONVERGENT_SUM_TERMS = [
    "\\frac{1}{2}",
    "\\frac{1}{4}",
    "\\frac{1}{8}",
    "\\frac{1}{16}",
]

PARTIAL_CONVERGENT_SUMS_TEXT = [
    "\\frac{1}{2}",
    "", "", ",\\quad",
    "\\frac{1}{2} + \\frac{1}{4}",
    "=", "\\frac{3}{4}", ",\\quad",
    "\\frac{1}{2} + \\frac{1}{4} + \\frac{1}{8}",
    "=", "\\frac{7}{8}", ",\\quad",
    "\\frac{1}{2} + \\frac{1}{4} + \\frac{1}{8} + \\frac{1}{16}",
    "=", "\\frac{15}{16}", ",\\dots"
]

def partial_sum(n):
    return sum([1.0/2**(k+1) for k in range(n)])

ALT_PARTIAL_SUM_TEXT = reduce(op.add, [
    [str(partial_sum(n)), "&=", "+".join(CONVERGENT_SUM_TERMS[:n])+"\\\\"]
    for n in range(1, len(CONVERGENT_SUM_TERMS)+1)
])+ [
    "\\vdots", "&", "\\\\",
    "1.0", "&=", "+".join(CONVERGENT_SUM_TERMS)+"+\\cdots+\\frac{1}{2^n}+\\cdots"
]


NUM_WRITTEN_TERMS = 4
INTERVAL_RADIUS = 5
NUM_INTERVAL_TICKS = 16


def divergent_sum():
    return tex_mobject(DIVERGENT_SUM_TEXT, size = "\\large").scale(2)

def convergent_sum():
    return tex_mobject(CONVERGENT_SUM_TEXT, size = "\\large").scale(2)

def underbrace(left, right):
    result = tex_mobject("\\underbrace{%s}"%(14*"\\quad"))
    result.stretch_to_fit_width(right[0]-left[0])
    result.shift(left - result.points[0])
    return result

def zero_to_one_interval():
    interval = NumberLine(
        radius = INTERVAL_RADIUS,
        interval_size = 2.0*INTERVAL_RADIUS/NUM_INTERVAL_TICKS
    )
    interval.elongate_tick_at(-INTERVAL_RADIUS, 4)
    interval.elongate_tick_at(INTERVAL_RADIUS, 4)
    zero = tex_mobject("0").shift(INTERVAL_RADIUS*LEFT+DOWN)
    one = tex_mobject("1").shift(INTERVAL_RADIUS*RIGHT+DOWN)
    return CompoundMobject(interval, zero, one)

def draw_you(with_bubble = False):
    result = PiCreature()
    result.give_straight_face().highlight("grey")
    result.to_corner(LEFT+DOWN)
    result.rewire_part_attributes()
    if with_bubble:
        bubble = ThoughtBubble()
        bubble.stretch_to_fit_width(12)
        bubble.pin_to(result)
        return result, bubble
    return result

def get_room_colors():
    return list(Color("yellow").range_to("red", 4))

def power_of_divisor(n, d):
    result = 0
    while n%d == 0:
        result += 1
        n /= d
    return result

class FlipThroughNumbers(Animation):
    def __init__(self, function = lambda x : x, 
                 start = 0, end = 10, 
                 start_center = ORIGIN,
                 end_center = ORIGIN,
                 **kwargs):
        self.function = function
        self.start = start
        self.end = end
        self.start_center = start_center
        self.end_center = end_center
        self.current_number = function(start)
        mobject = tex_mobject(str(self.current_number)).shift(start_center)
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        new_number = self.function(
            self.start + int(alpha *(self.end-self.start))
        )
        if new_number != self.current_number:
            self.current_number = new_number
            self.mobject = tex_mobject(str(new_number)).shift(self.start_center)
        if not all(self.start_center == self.end_center):
            self.mobject.center().shift(
                (1-alpha)*self.start_center + alpha*self.end_center
            )


######################################

class IntroduceDivergentSum(Scene):
    def construct(self):
        equation = divergent_sum().split()
        sum_value = None
        brace = underbrace(
            equation[0].get_border_point(DOWN+LEFT),
            equation[1].get_border_point(DOWN+RIGHT)
        ).shift(0.2*DOWN)
        min_x_coord = min(equation[0].points[:,0])
        for x in range(NUM_WRITTEN_TERMS):
            self.add(equation[x])
            if x == 0:
                self.dither(0.75)
                continue
            brace.stretch_to_fit_width(
                max(equation[x].points[:,0]) - min_x_coord
            )
            brace.to_edge(LEFT, buff = SPACE_WIDTH+min_x_coord)
            if sum_value:
                self.remove(sum_value)
            sum_value = tex_mobject(str(2**(x+1) - 1))
            sum_value.shift(brace.get_center() + 0.5*DOWN)
            self.add(brace, sum_value)
            self.dither(0.75)
        self.remove(sum_value)
        ellipses = CompoundMobject(
            *[equation[NUM_WRITTEN_TERMS + i] for i in range(3)]
        )
        end_brace = deepcopy(brace).stretch_to_fit_width(
            max(ellipses.points[:,0])-min_x_coord
        ).to_edge(LEFT, buff = SPACE_WIDTH+min_x_coord)
        kwargs = {"run_time" : 5.0, "alpha_func" : rush_into}        
        flip_through = FlipThroughNumbers(
            lambda x : 2**(x+1)-1,
            start = NUM_WRITTEN_TERMS-1,
            end = 50,
            start_center = brace.get_center() + 0.5*DOWN,
            end_center = end_brace.get_center() + 0.5*DOWN,
            **kwargs
        )
        self.add(ellipses)
        self.animate(
            Transform(brace, end_brace, **kwargs),
            flip_through,
        )
        self.clear()
        self.add(*equation)
        self.dither()

class ClearlyNonsense(Scene):
    def construct(self):
        number_line = NumberLine().add_numbers()
        div_sum = divergent_sum()
        this_way = text_mobject("Sum goes this way...")
        this_way.to_edge(LEFT).shift(RIGHT*(SPACE_WIDTH+1) + DOWN)
        how_here = text_mobject("How does it end up here?")
        how_here.shift(1.5*UP+LEFT)
        neg_1_arrow = Arrow(
            (-1, 0.3, 0), 
            tail=how_here.get_center()+0.5*DOWN
        )
        right_arrow = Arrow(
            (SPACE_WIDTH-0.5)*RIGHT + DOWN, 
            tail = (max(this_way.points[:,0]), -1, 0)
        )
        how_here.highlight("red")
        neg_1_arrow.highlight("red")
        this_way.highlight("yellow")
        right_arrow.highlight("yellow")

        self.animate(Transform(
            div_sum, 
            deepcopy(div_sum).scale(0.5).shift(3*UP)
        ))
        self.animate(ShowCreation(number_line))
        self.dither()
        self.add(how_here)
        self.animate(ShowCreation(neg_1_arrow))
        self.dither()
        self.add(this_way)
        self.animate(ShowCreation(right_arrow))
        self.dither()

class OutlineOfVideo(Scene):
    def construct(self):
        conv_sum = convergent_sum().scale(0.5)
        div_sum = divergent_sum().scale(0.5)
        overbrace = underbrace(
            conv_sum.get_left(),
            conv_sum.get_right()
        ).rotate(np.pi, RIGHT).shift(0.75*UP*conv_sum.get_height())
        dots = conv_sum.split()[-2].highlight("green")
        dots.sort_points()
        arrow = Arrow(
            dots.get_bottom(),
            direction = UP+LEFT
        )
        u_brace = underbrace(div_sum.get_left(), div_sum.get_right())
        u_brace.shift(1.5*div_sum.get_bottom())
        for mob in conv_sum, overbrace, arrow, dots:
            mob.shift(2*UP)
        for mob in div_sum, u_brace:
            mob.shift(DOWN)
        texts = [
            text_mobject(words).highlight("yellow")
            for words in [
                "1. Discover this",
                "2. Clarify what this means",
                "3. Discover this",
                ["4. Invent ", "\\textbf{new math}"]
            ]
        ]
        last_one_split = texts[-1].split()
        last_one_split[1].highlight("skyblue")
        texts[-1] = CompoundMobject(*last_one_split)
        texts[0].shift(overbrace.get_top()+texts[0].get_height()*UP)
        texts[1].shift(sum([
            arrow.get_border_point(DOWN+RIGHT),
            texts[1].get_height()*DOWN
        ]))
        texts[2].shift(u_brace.get_bottom()+texts[3].get_height()*DOWN)
        texts[3].to_edge(DOWN)

        groups = [
            [texts[0], overbrace, conv_sum],
            [texts[1], arrow, dots],
            [texts[2], u_brace, div_sum],
            [texts[3]]
        ]
        for group in groups:
            self.animate(*[
                DelayByOrder(FadeIn(element))
                for element in group
            ])
            self.dither()

# # class ReasonsForMakingVideo(Scene):
# #     def construct(self):
# #         text = text_mobject([
# #             """
# #             \\begin{itemize}
# #             \\item Understand what ``$
# #             """,
# #             "".join(DIVERGENT_SUM_TEXT),
# #             """
# #             $'' is saying.
# #             """,
# #             """
# #             \\item Nonsense-Driven Construction
# #             \\end{itemize}
# #             """
# #         ], size = "\\Small")
# #         text.scale(1.5).to_edge(LEFT).shift(UP).highlight("white")
# #         text.highlight("green", lambda (x, y, z) : x < -SPACE_WIDTH + 1)
# #         line_one_first, equation, line_one_last, line_two = text.split()
# #         line_two.shift(2*DOWN)
# #         div_sum = divergent_sum().scale(0.5).shift(3*UP)

# #         self.add(div_sum)
# #         self.animate(
# #             ApplyMethod(div_sum.replace, equation),
# #             FadeIn(line_one_first),
# #             FadeIn(line_one_last)
# #         )
# #         self.dither()
# #         self.add(line_two)
# #         self.dither()

# class DiscoverAndDefine(Scene):
#     def construct(self):
#         sum_mob = tex_mobject("\\sum_{n = 1}^\\infty a_n")
#         discover = text_mobject("What does it feel like to discover these?")
#         define = text_mobject([
#             "What does it feel like to", 
#             "\\emph{define} ",
#             "them?"
#         ])
#         sum_mob.shift(2*UP)
#         define.shift(2*DOWN)
#         define_parts = define.split()
#         define_parts[1].highlight("skyblue")

#         self.add(sum_mob)
#         self.animate(FadeIn(discover))
#         self.dither()
#         self.animate(FadeIn(CompoundMobject(*define_parts)))
#         self.dither()

class YouAsMathematician(Scene):
    def construct(self):
        you, bubble = draw_you(with_bubble = True)
        explanation = text_mobject(
            "You as a (questionably accurate portrayal of a) mathematician.",
            size = "\\small"
        ).shift([2, you.get_center()[1], 0])
        arrow = Arrow(you.get_center(), direction = LEFT)
        arrow.nudge(you.get_width())
        for mob in arrow, explanation:
            mob.highlight("yellow")
        equation = convergent_sum()
        bubble.add_content(equation)
        equation.shift(0.5*RIGHT)
        bubble.clear()
        dot_pair = [
            Dot(density = 3*DEFAULT_POINT_DENSITY_1D).shift(x+UP)
            for x in LEFT, RIGHT
        ]
        self.add(you, explanation)
        self.animate(
            ShowCreation(arrow),
            BlinkPiCreature(you)
        )
        self.dither()
        self.animate(ShowCreation(bubble))
        self.animate(ShowCreation(equation, run_time = 2.0))
        self.dither()
        self.animate(
            BlinkPiCreature(you),
            FadeOut(explanation),
            FadeOut(arrow)
        )
        self.animate(Transform(equation, CompoundMobject(*dot_pair)))
        self.remove(equation)
        self.add(*dot_pair)
        two_arrows = [
            Arrow(x, direction = x).shift(UP).nudge()
            for x in LEFT, RIGHT
        ]
        self.animate(*[ShowCreation(a) for a in two_arrows])
        self.animate(BlinkPiCreature(you))
        self.remove(*dot_pair+two_arrows)
        everything = CompoundMobject(*self.mobjects)
        self.clear()
        self.animate(
            ApplyPointwiseFunction(
                everything, 
                lambda p : 3*SPACE_WIDTH*p/np.linalg.norm(p)
            ),
            *[
                Transform(dot, deepcopy(dot).shift(DOWN).scale(3)) 
                for dot in dot_pair
            ],
            run_time = 2.0
        )
        self.dither()


class DotsGettingCloser(Scene):
    def construct(self):
        dots = [
            Dot(radius = 3*Dot.DEFAULT_RADIUS).shift(3*x)
            for x in LEFT, RIGHT
        ]
        self.add(*dots)
        self.dither()
        for x in range(10):
            distance = min(dots[1].points[:,0])-max(dots[0].points[:,0])
            self.animate(ApplyMethod(dots[0].shift, 0.5*distance*RIGHT))


class ZoomInOnInterval(Scene):
    def construct(self):
        number_line = NumberLine(density = 10*DEFAULT_POINT_DENSITY_1D)
        number_line.add_numbers()
        interval = zero_to_one_interval().split()

        new_line = deepcopy(number_line)
        new_line.highlight("black", lambda (x,y,z) : x < 0 or x > 1 or y < -0.2)
        # height = new_line.get_height()
        new_line.scale(2*INTERVAL_RADIUS)
        new_line.shift(INTERVAL_RADIUS*LEFT)
        # new_line.stretch_to_fit_height(height)

        self.add(number_line)
        self.dither()
        self.animate(Transform(number_line, new_line))
        self.clear()
        squish = lambda p : (p[0], 0, 0)
        self.animate(
            ApplyMethod(new_line.apply_function, squish),
            ApplyMethod(
                interval[0].apply_function, squish,
                alpha_func = lambda t : 1-t
            ),
            *[FadeIn(interval[x]) for x in [1, 2]]
        )
        self.clear()
        self.add(*interval)
        self.dither()

class DanceDotOnInterval(Scene):
    def construct(self, mode):
        num_written_terms = NUM_WRITTEN_TERMS
        prop = 0.5
        sum_terms = [
            "\\frac{1}{2}", 
            "\\frac{1}{4}",
            "\\frac{1}{8}",
            "\\frac{1}{16}",
        ]
        num_height = 1.3*DOWN
        interval = zero_to_one_interval()
        dots = [
            Dot(radius = 3*Dot.DEFAULT_RADIUS).shift(INTERVAL_RADIUS*x+UP)
            for x in LEFT, RIGHT
        ]
        color_range = Color("green").range_to("yellow", num_written_terms)
        conv_sum = tex_mobject(sum_terms, size = "\\large").split()

        self.add(interval)
        self.animate(*[
            ApplyMethod(dot.shift, DOWN)
            for dot in dots
        ])
        self.dither()
        for count in range(num_written_terms):
            shift_val = 2*RIGHT*INTERVAL_RADIUS*(1-prop)*(prop**count)
            start = dots[0].get_center()
            line = Line(start, start + shift_val*RIGHT)
            line.highlight(color_range.next())
            self.animate(
                ApplyMethod(dots[0].shift, shift_val),
                ShowCreation(line)
            )
            num = conv_sum[count]
            num.shift(RIGHT*(line.get_center()[0]-num.get_center()[0]))
            num.shift(num_height)
            arrow = Mobject()
            if num.get_width() > line.get_length():
                num.center().shift(3*DOWN+2*(count-2)*RIGHT)
                arrow = Arrow(
                    line.get_center()+2*DOWN,
                    tail = num.get_center()+0.5*num.get_height()*UP
                )
            self.animate(
                ApplyMethod(line.shift, 2*DOWN),
                FadeIn(num),
                FadeIn(arrow),
            )
        self.dither()
        self.write_partial_sums()
        self.dither()

    def write_partial_sums(self):
        partial_sums = tex_mobject(PARTIAL_CONVERGENT_SUMS_TEXT, size = "\\small")
        partial_sums.scale(1.5).to_edge(UP)
        partial_sum_parts = partial_sums.split()
        partial_sum_parts[0].highlight("yellow")

        for x in range(0, len(partial_sum_parts), 4):
            partial_sum_parts[x+2].highlight("yellow")
            self.animate(*[
                FadeIn(partial_sum_parts[y])
                for y in range(x, x+4)
            ])
        self.dither(2)

class OrganizePartialSums(Scene):
    def construct(self):
        partial_sums = tex_mobject(PARTIAL_CONVERGENT_SUMS_TEXT, size = "\\small")
        partial_sums.scale(1.5).to_edge(UP)
        partial_sum_parts = partial_sums.split()
        for x in [0] + range(2, len(partial_sum_parts), 4):
            partial_sum_parts[x].highlight("yellow")
        pure_sums = [
            partial_sum_parts[x] 
            for x in range(0, len(partial_sum_parts), 4)
        ]
        new_pure_sums = deepcopy(pure_sums)
        for pure_sum, count in zip(new_pure_sums, it.count(3, -1.2)):
            pure_sum.center().scale(1/1.25).highlight("white")
            pure_sum.to_edge(LEFT).shift(2*RIGHT+count*UP)

        self.add(*partial_sum_parts)
        self.dither()
        self.animate(*[
            CounterclockwiseTransform(*pair, counterclockwise=False)
            for pair in zip(pure_sums, new_pure_sums)
        ]+[
            FadeOut(mob)
            for mob in partial_sum_parts
            if mob not in pure_sums
        ])
        self.dither()
        down_arrow = tex_mobject("\\downarrow")
        down_arrow.to_edge(LEFT).shift(2*RIGHT+2*DOWN)
        infinite_sum = tex_mobject("".join(CONVERGENT_SUM_TEXT[:-1]), size = "\\samll")
        infinite_sum.scale(1.5/1.25)
        infinite_sum.to_corner(DOWN+LEFT).shift(2*RIGHT)
        self.animate(FadeIn(CompoundMobject(down_arrow, infinite_sum)))

        self.dither()

class SeeNumbersApproachOne(Scene):
    def construct(self):
        interval = zero_to_one_interval()
        arrow = Arrow(INTERVAL_RADIUS*RIGHT, tail=ORIGIN).nudge()
        arrow.shift(DOWN).highlight("yellow")
        num_dots = 6
        colors = Color("green").range_to("yellow", num_dots)
        dots = CompoundMobject(*[
            Dot(
                density = 2*DEFAULT_POINT_DENSITY_1D
            ).scale(1+1.0/2.0**x).shift(
                INTERVAL_RADIUS*RIGHT +\
                (INTERVAL_RADIUS/2.0**x)*LEFT
            ).highlight(colors.next())
            for x in range(num_dots)
        ])

        self.add(interval)
        self.animate(
            ShowCreation(arrow),
            ShowCreation(dots),
            run_time = 2.0
        )
        self.dither()

class OneAndInfiniteSumAreTheSameThing(Scene):
    def construct(self):
        one, equals, inf_sum = tex_mobject([
            "1", "=", "\\sum_{n=1}^\\infty \\frac{1}{2^n}"
        ]).split()
        point = Point(equals.get_center()).highlight("black")

        self.add(one.shift(LEFT))
        self.dither()
        self.add(inf_sum.shift(RIGHT))
        self.dither()
        self.animate(
            ApplyMethod(one.shift, RIGHT),
            ApplyMethod(inf_sum.shift, LEFT),
            CounterclockwiseTransform(point, equals)
        )
        self.dither()


class HowDoYouDefineInfiniteSums(Scene):
    def construct(self):
        you = draw_you().center().rewire_part_attributes()
        text = text_mobject(
            ["How", " do", " you,\\\\", "\\emph{define}"],
            size = "\\Huge"
        ).shift(UP).split()
        text[-1].shift(3*DOWN).highlight("skyblue")
        sum_mob = tex_mobject("\\sum_{n=0}^\\infty{a_n}")
        text[-1].shift(LEFT)
        sum_mob.shift(text[-1].get_center()+2*RIGHT)

        self.add(you)
        self.dither()
        for mob in text[:-1]:
            self.add(mob)
            self.dither(0.1)
        self.animate(BlinkPiCreature(you))
        self.dither()
        self.add(text[-1])
        self.dither()
        self.add(sum_mob)
        self.dither()


class LessAboutNewThoughts(Scene):
    def construct(self):
        words = generating, new, thoughts, to, definitions = text_mobject([
            "Generating", " new", " thoughts", "$\\rightarrow$",
            "useful definitions"
        ], size = "\\large").split()
        gen_cross = tex_mobject("\\hline").highlight("red")
        new_cross = deepcopy(gen_cross)
        for cross, mob in [(gen_cross, generating), (new_cross, new)]:
            cross.replace(mob)
            cross.stretch_to_fit_height(0.03)
        disecting = text_mobject("Disecting").highlight("green")
        disecting.shift(generating.get_center() + 0.6*UP)
        old = text_mobject("old").highlight("green")
        old.shift(new.get_center()+0.6*UP)

        kwargs = {"run_time" : 0.25}
        self.add(*words)
        self.dither()
        self.animate(ShowCreation(gen_cross, **kwargs))
        self.animate(ShowCreation(new_cross, **kwargs))
        self.dither()        
        self.add(disecting)
        self.dither(0.5)
        self.add(old)
        self.dither()

class ListOfPartialSums(Scene):
    def construct(self):
        all_terms = np.array(tex_mobject(
            ALT_PARTIAL_SUM_TEXT,
            size = "\\large"
        ).split())
        numbers, equals, sums = [
            all_terms[range(k, 12, 3)]
            for k in 0, 1, 2
        ]
        dots = all_terms[12]
        one = all_terms[-3]
        last_equal = all_terms[-2]
        infinite_sum = all_terms[-1]

        self.count(
            numbers, 
            mode = "show",
            display_numbers = False, 
            run_time = 1.0
        )
        self.animate(ShowCreation(dots))
        self.dither()
        self.animate(
            FadeIn(CompoundMobject(*equals)),
            *[
                Transform(deepcopy(number), finite_sum)
                for number, finite_sum in zip(numbers, sums)
            ]
        )
        self.dither()
        self.animate(*[
            ApplyMethod(s.highlight, "yellow", alpha_func = there_and_back)
            for s in sums
        ])
        self.dither()
        self.add(one.highlight("green"))
        self.dither()


class ShowDecreasingDistance(Scene):
    args_list = [(1,), (2,)]
    @staticmethod
    def args_to_string(num):
        return str(num)

    def construct(self, num):
        number_line = NumberLine(interval_size = 1).add_numbers()
        vert_line0 = Line(0.5*UP+RIGHT, UP+RIGHT)
        vert_line1 = Line(0.5*UP+2*num*RIGHT, UP+2*num*RIGHT)
        horiz_line = Line(vert_line0.end, vert_line1.end)
        lines = [vert_line0, vert_line1, horiz_line]
        for line in lines:
            line.highlight("green")
        dots = CompoundMobject(*[
            Dot().scale(1.0/(n+1)).shift((1+partial_sum(n))*RIGHT)
            for n in range(10)
        ])

        self.add(dots.split()[0])
        self.add(number_line, *lines)
        self.dither()
        self.animate(
            ApplyMethod(vert_line0.shift, RIGHT),
            Transform(
                horiz_line, 
                Line(vert_line0.end+RIGHT, vert_line1.end).highlight("green")
            ),
            ShowCreation(dots),
            run_time = 2.5
        )
        self.dither()

class CircleZoomInOnOne(Scene):
    def construct(self):
        number_line = NumberLine(interval_size = 1).add_numbers()
        dots = CompoundMobject(*[
            Dot().scale(1.0/(n+1)).shift((1+partial_sum(n))*RIGHT)
            for n in range(10)
        ])
        circle = Circle().shift(2*RIGHT)

        self.add(number_line, dots)
        self.animate(Transform(circle, Point(2*RIGHT)), run_time = 5.0)
        self.dither()

class ZoomInOnOne(Scene):
    def construct(self):
        num_levels = 3
        scale_val = 5
        number_lines = [
            NumberLine(
                interval_size = 1, 
                density = scale_val*DEFAULT_POINT_DENSITY_1D
            ).scale(1.0/scale_val**x)
            for x in range(num_levels)
        ]
        kwargs = {"alpha_func" : None}
        self.animate(*[
            ApplyMethod(number_lines[x].scale, scale_val, **kwargs)
            for x in range(1, num_levels)
        ]+[
            ApplyMethod(number_lines[0].stretch, scale_val, 0, **kwargs),
        ])

        self.repeat(5)


class DefineInfiniteSum(Scene):
    def construct(self):
        self.put_expression_in_corner()
        self.list_partial_sums()
        self.dither()

    def put_expression_in_corner(self):
        buff = 0.24
        define, infinite_sum = tex_mobject([
            "\\text{\\emph{Define} }",
            "\\sum_{n = 0}^\\infty a_n = X"
        ]).split()
        define.highlight("skyblue")
        expression = CompoundMobject(define, infinite_sum)

        self.add(expression)
        self.dither()
        self.animate(ApplyFunction(
            lambda mob : mob.scale(0.5).to_corner(UP+LEFT, buff = buff),
            expression            
        ))
        bottom = (min(expression.points[:,1]) - buff)*UP
        side   = (max(expression.points[:,0]) + buff)*RIGHT
        lines = [
            Line(SPACE_WIDTH*LEFT+bottom, side+bottom),
            Line(SPACE_HEIGHT*UP+side, side+bottom)
        ]
        self.animate(*[
            ShowCreation(line.highlight("white"))
            for line in lines
        ])
        self.dither()

    def list_partial_sums(self):
        num_terms = 10
        term_strings = reduce(op.add, [
            [
                "s_%d"%n, 
                "&=", 
                "+".join(["a_%d"%k for k in range(n+1)])+"\\\\"
            ]
            for n in range(num_terms)
        ])
        terms = tex_mobject(term_strings, size = "\\large").split()
        number_line = NumberLine()
        ex_point = 2*RIGHT
        ex = tex_mobject("X").shift(ex_point + LEFT + UP)
        arrow = Arrow(ex_point, tail = ex.points[-1]).nudge()

        for term, count in zip(terms, it.count()):
            self.add(term)
            self.dither(0.1)
            if count % 3 == 2:
                self.dither(0.5)
        self.dither()
        esses = np.array(terms)[range(0, len(terms), 3)]
        other_terms = filter(lambda m : m not in esses, terms)
        self.animate(*[
            ApplyMethod(ess.highlight, "yellow")
            for ess in esses
        ])

        def move_s(s, n):
            s.center()
            s.scale(1.0/(n+1))
            s.shift(ex_point-RIGHT*2.0/2**n)
            return s
        self.animate(*[
            FadeOut(term)
            for term in other_terms
        ]+[
            ApplyFunction(lambda s : move_s(s, n), ess)
            for ess, n in zip(esses, it.count())
        ]+[
            FadeIn(number_line), 
            FadeIn(ex), 
            FadeIn(arrow)
        ])

        lines = [
            Line(x+0.25*DOWN, x+0.25*UP).highlight("white")
            for y in [-1, -0.01, 1, 0.01]
            for x in [ex_point+y*RIGHT]
        ]
        self.animate(*[
            Transform(lines[x], lines[x+1], run_time = 3.0)
            for x in 0, 2
        ])


class YouJustInventedSomeMath(Scene):
    def construct(self):
        text = text_mobject([
            "You ", "just ", "invented\\\\", "some ", "math"
        ]).split()
        for mob in text[:3]:
            mob.shift(UP)
        for mob in text[3:]:
            mob.shift(1.3*DOWN)
        you = draw_you().center().rewire_part_attributes()

        self.add(you)
        for mob in text:
            self.add(mob)
            self.dither(0.2)
        self.animate(BlinkPiCreature(you))


class SeekMoreGeneralTruths(Scene):
    def construct(self):
        summands = [
            "\\frac{1}{3^n}",
            "2^n",            
            "\\frac{1}{n^2}",
            "\\frac{(-1)^n}{n}",
            "\\frac{(-1)^n}{(2n)!}",
            "\\frac{2\sqrt{2}}{99^2}\\frac{(4n)!}{(n!)^4} \\cdot \\frac{26390n + 1103}{396^{4k}}",            
        ]
        sums = tex_mobject([
            "&\\sum_{n = 0}^\\infty" + summand + "= ? \\\\"
            for summand in summands
        ], size = "")
        sums.stretch_to_fit_height(2*SPACE_HEIGHT-1)
        sums.shift((SPACE_HEIGHT-0.5-max(sums.points[:,1]))*UP)

        for qsum in sums.split():
            self.add(qsum)
            self.dither(0.5)
        self.dither()

class ChopIntervalInProportions(Scene):
    args_list = [("9", ), ("p", )]
    @staticmethod
    def args_to_string(*args):
        return args[0]

    def construct(self, mode):
        if mode == "9":
            prop = 0.1
            num_terms = 2
            left_terms, right_terms = [
                [
                    tex_mobject("\\frac{%d}{%d}"%(k, (10**(count+1))))
                    for count in range(num_terms)
                ]
                for k in 9, 1
            ]
        if mode == "p":
            num_terms = 3         
            prop = 0.7
            left_terms = map(tex_mobject, ["(1-p)", "p(1-p)"]+[
                "p^%d(1-p)"%(count)
                for count in range(2, num_terms)
            ])
            right_terms = map(tex_mobject, ["p"] + [
                "p^%d"%(count+1)
                for count in range(1, num_terms)
            ])
        interval = zero_to_one_interval()
        left = INTERVAL_RADIUS*LEFT
        right = INTERVAL_RADIUS*RIGHT
        curr = left.astype("float")
        brace_to_replace = None
        term_to_replace = None

        self.add(interval)
        for lt, rt, count in zip(left_terms, right_terms, it.count()):
            last = deepcopy(curr)
            curr += 2*RIGHT*INTERVAL_RADIUS*(1-prop)*(prop**count)
            braces = [
                underbrace(a, b).rotate(np.pi, RIGHT)
                for a, b in [(last, curr), (curr, right)]
            ]
            for term, brace, count2 in zip([lt, rt], braces, it.count()):
                term.scale(0.75)
                term.shift(brace.get_center()+UP)                
                if term.get_width() > brace.get_width():
                    term.shift(UP+RIGHT)
                    term.add(Arrow(
                        brace.get_center()+0.3*UP,
                        tail = term.get_center()+0.5*DOWN
                    ))
                
            if brace_to_replace is not None:
                self.animate(
                    Transform(
                        brace_to_replace.repeat(2), 
                        CompoundMobject(*braces)
                    ),
                    Transform(
                        term_to_replace,
                        CompoundMobject(lt, rt)
                    )
                )
                self.remove(brace_to_replace, term_to_replace)
                self.add(lt, rt, *braces)
            else:
                self.animate(*[
                    FadeIn(mob)
                    for mob in braces + [lt, rt]
                ])
            self.dither()
            brace_to_replace = braces[1]
            term_to_replace = rt             
        self.dither()



class GeometricSum(RearrangeEquation):
    def construct(self):
        start_terms = "(1-p) + p (1-p) + p^2 (1-p) + p^3 (1-p) + \\cdots = 1"
        end_terms = "1 + p + p^2 + p^3 + \\cdots = \\frac{1}{(1-p)}"
        index_map = {
            0 : 0,
            # 0 : -1, #(1-p)
            1 : 1,  #+
            2 : 2,  #p
            # 3 : -1, #(1-p)
            4 : 3,  #+
            5 : 4,  #p^2
            # 6 : -1, #(1-p)
            7 : 5,  #+
            8 : 6,  #p^3
            # 9 : -1, #(1-p)
            10: 7,  #+
            11: 8,  #\\cdots
            12: 9,  #=
            13: 10, #1
        }
        def start_transform(mob):
            return mob.scale(1.3).shift(2*UP)
        def end_transform(mob):
            return mob.scale(1.3).shift(DOWN)

        RearrangeEquation.construct(
            self, 
            start_terms.split(" "), end_terms.split(" "), 
            index_map, size = "\\large", 
            path = counterclockwise_path,
            start_transform = start_transform,
            end_transform = end_transform,
            leave_start_terms = True,
            transform_kwargs = {"run_time" : 2.0}
        )

class PointNineRepeating(RearrangeEquation):
    def construct(self):
        start_terms = [
            "\\frac{9}{10}",
            "+",
            "\\frac{9}{100}",
            "+",
            "\\frac{9}{1000}",
            "+",
            "\\cdots=1",
        ]
        end_terms = "0 . 9 9 9 \\cdots=1".split(" ")
        index_map = {
            0 : 2,
            2 : 3,
            4 : 4,
            6 : 5,
        }
        for term in tex_mobject(start_terms).split():
            self.add(term)
            self.dither(0.5)
        self.clear()
        RearrangeEquation.construct(
            self,
            start_terms,
            end_terms,
            index_map,
            path = straight_path
        )


class PlugNumbersIntoRightside(Scene):
    def construct(self):
        scale_factor = 1.5
        lhs, rhs = tex_mobject(
            ["1 + p + p^2 + p^3 + \\cdots = ", "\\frac{1}{1-p}"],
            size = "\\large"
        ).scale(scale_factor).split()
        rhs = tex_mobject(
            ["1 \\over 1 - ", "p"], 
            size = "\\large"
        ).replace(rhs).split()
        num_strings = [
            "0.5", "3", "\pi", "(-1)", "3.7", "2",
            "0.2", "27", "i"
        ] 
        nums = [
            tex_mobject(num_string, size="\\large")
            for num_string in num_strings
        ]
        for num, num_string in zip(nums, num_strings):
            num.scale(scale_factor)
            num.shift(rhs[1].get_center())
            num.shift(0.1*RIGHT + 0.08*UP)
            num.highlight("green")
            if num_string == "(-1)":
                num.shift(0.3*RIGHT)
        right_words = text_mobject(
            "This side makes sense for almost any value of $p$,"
        ).shift(2*UP)
        left_words = text_mobject(
            "even if it seems like this side will not."
        ).shift(2*DOWN)
        right_words.add(Arrow(
            rhs[0].get_center(),
            tail = right_words.get_center()+DOWN+RIGHT
        ).nudge(0.5))
        left_words.add(Arrow(
            lhs.get_center() + 0.3*DOWN,
            tail = left_words.get_center() + 0.3*UP
        ))
        right_words.highlight("green")
        left_words.highlight("yellow")


        self.add(lhs, *rhs)
        self.dither()
        self.animate(FadeIn(right_words))
        curr = rhs[1]
        for num, count in zip(nums, it.count()):
            self.animate(CounterclockwiseTransform(curr, num))
            self.dither()
            if count == 2:
                self.animate(FadeIn(left_words))


class PlugInNegativeOne(RearrangeEquation):
    def construct(self):
        num_written_terms = 4
        start_terms = reduce(op.add, [
            ["(-", "1", ")^%d"%n, "+"]
            for n in range(num_written_terms)
        ]) + ["\\cdots=", "\\frac{1}{1-(-1)}"]
        end_terms = "1 - 1 + 1 - 1 + \\cdots= \\frac{1}{2}".split(" ")
        index_map = dict([
            (4*n + 1, 2*n)
            for n in range(num_written_terms)
        ]+[
            (4*n + 3, 2*n + 1)
            for n in range(num_written_terms)
        ])
        index_map[-2] = -2
        index_map[-1] = -1
        RearrangeEquation.construct(
            self,
            start_terms,
            end_terms,
            index_map,
            path = straight_path,
            start_transform = lambda m : m.shift(2*UP),
            leave_start_terms = True,
        )

class PlugInTwo(RearrangeEquation):
    def construct(self):
        num_written_terms = 4
        start_terms = reduce(op.add, [
            ["2", "^%d"%n, "+"]
            for n in range(num_written_terms)
        ]) + ["\\cdots=", "\\frac{1}{1-2}"]
        end_terms = "1 + 2 + 4 + 8 + \\cdots= -1".split(" ")
        index_map = dict([
            (3*n, 2*n)
            for n in range(num_written_terms)
        ]+[
            (3*n + 2, 2*n + 1)
            for n in range(num_written_terms)
        ])
        index_map[-2] = -2
        index_map[-1] = -1
        RearrangeEquation.construct(
            self,
            start_terms,
            end_terms,
            index_map,
            size = "\\Huge",
            path = straight_path,
            start_transform = lambda m : m.shift(2*UP),
            leave_start_terms = True,
        )

class ListPartialDivergentSums(Scene):
    args_list = [
        (
            lambda n : "1" if n%2 == 0 else "(-1)",
            lambda n : "1" if n%2 == 0 else "0"
        ),
        (
            lambda n : "2^%d"%n if n > 1 else ("1" if n==0 else "2"),
            lambda n : str(2**(n+1)-1)
        )
    ]
    @staticmethod
    def args_to_string(*args):
        if args[0](1) == "(-1)":
            return "Negative1"
        else:
            return args[0](1)
    def construct(self, term_func, partial_sum_func):
        num_lines = 8
        rhss = [
            partial_sum_func(n) 
            for n in range(num_lines)
        ]
        lhss = [
            "&=" + \
            "+".join([term_func(k) for k in range(n+1)]) + \
            "\\\\"
            for n in range(num_lines)
        ]
        terms = tex_mobject(
            list(it.chain.from_iterable(zip(rhss, lhss))) + ["\\vdots&", ""],
            size = "\\large"
        ).shift(RIGHT).split()
        words = text_mobject("These numbers don't \\\\ approach anything")
        words.to_edge(LEFT)
        arrow = Arrow(3*DOWN+2*LEFT, direction = DOWN, length = 6)

        for x in range(0, len(terms), 2):
            self.animate(FadeIn(terms[x]), FadeIn(terms[x+1]))
        self.animate(FadeIn(words), ShowCreation(arrow))
        for x in range(0, len(terms), 2):
            self.animate(
                ApplyMethod(terms[x].highlight, "green"),
                run_time = 0.1
            )
        self.dither()


class SumPowersOfTwoAnimation(Scene):
    def construct(self):
        dot = Dot(density = 3*DEFAULT_POINT_DENSITY_1D).scale(3)
        dot_width = dot.get_width()*RIGHT
        dot_buff = 0.4*RIGHT
        left = (SPACE_WIDTH-1)*LEFT
        right = left + 2*dot_width + dot_buff
        top_brace_left = left+dot_width+dot_buff+0.3*DOWN
        bottom_brace_left = left + 0.3*DOWN
        circle = Circle().scale(dot_width[0]/2).shift(left+dot_width/2)
        curr_dots = deepcopy(dot).shift(left+1.5*dot_width+dot_buff)
        topbrace = underbrace(top_brace_left, right).rotate(np.pi, RIGHT)
        bottombrace = underbrace(bottom_brace_left, right)
        colors = Color("yellow").range_to("purple", 5)
        curr_dots.highlight(colors.next())
        equation = tex_mobject(
            "1+2+4+\\cdots+2^n=2^{n+1}"
        ).shift(3*UP)

        self.add(equation)
        self.dither()
        self.add(circle, curr_dots, topbrace, bottombrace)
        for n in range(1,5):
            top_num = tex_mobject("+".join([
                str(2**k)
                for k in range(n)
            ])).shift(topbrace.get_center()+0.5*UP)
            bottom_num = tex_mobject(str(2**n))
            bottom_num.shift(bottombrace.get_center()+0.5*DOWN)
            self.add(top_num, bottom_num)
            self.dither()
            if n == 4:
                continue
            new_dot = deepcopy(dot).shift(circle.get_center()+2*UP)
            self.animate(ApplyMethod(
                new_dot.shift, 2*DOWN, 
                alpha_func = rush_into
            ))
            self.remove(new_dot)
            shift_val = (2**n)*(dot_width+dot_buff)
            right += shift_val
            new_dots = CompoundMobject(new_dot, curr_dots)
            target = deepcopy(new_dots).shift(shift_val)
            target.highlight(colors.next())
            self.remove(top_num, bottom_num)
            self.animate(
                CounterclockwiseTransform(
                    new_dots, target,
                    alpha_func = rush_from
                ),
                Transform(
                    topbrace, 
                    underbrace(top_brace_left, right).rotate(np.pi, RIGHT)
                ),
                Transform(
                    bottombrace,
                    underbrace(bottom_brace_left, right)
                )
            )
            curr_dots = CompoundMobject(curr_dots, new_dots)


        
class PretendTheyDoApproachNegativeOne(RearrangeEquation):
    def construct(self):
        you, bubble = draw_you(with_bubble = True)
        start_terms = "1 , 3 , 7 , 15 , 31 , \\cdots\\rightarrow -1".split(" ")
        end_terms   = "2 , 4 , 8 , 16 , 32 , \\cdots\\rightarrow 0".split(" ")
        def transform(mob):
            bubble.add_content(mob)
            return mob
        index_map = dict([(a, a) for a in range(len(start_terms))])

        self.add(you, bubble)
        RearrangeEquation.construct(
            self, start_terms, end_terms, index_map, 
            size = "\\Huge", 
            start_transform = transform,
            end_transform = transform
        )


class NotTheOnlyWayToOrganize(Scene):
    def construct(self):
        self.animate(ShowCreation(NumberLine().add_numbers()))
        self.dither()
        words = "Is there any other reasonable way to organize numbers?"
        self.animate(FadeIn(text_mobject(words).shift(2*UP)))
        self.dither()



class RoomsAndSubrooms(Scene):
    def construct(self):
        colors = get_room_colors()
        a_set = [3*RIGHT, 3*LEFT]
        b_set = [1.5*UP, 1.5*DOWN]
        c_set = [LEFT, RIGHT]
        rectangle_groups = [
            [Rectangle(7, 12).highlight(colors[0])],
            [
                Rectangle(6, 5).shift(a).highlight(colors[1])
                for a in a_set
            ],
            [
                Rectangle(2, 4).shift(a + b).highlight(colors[2])
                for a in a_set
                for b in b_set
            ],
            [
                Rectangle(1, 1).shift(a+b+c).highlight(colors[3])
                for a in a_set
                for b in b_set
                for c in c_set
            ]
        ]

        for group in rectangle_groups:
            mob = CompoundMobject(*group)
            mob.sort_points(np.linalg.norm)
            self.animate(ShowCreation(mob))

        self.dither()


class RoomsAndSubroomsWithNumbers(Scene):
    def construct(self):
        zero_local = (SPACE_WIDTH-0.5)*LEFT
        zero_one_width = SPACE_WIDTH-0.3

        zero, power_mobs = self.draw_numbers(zero_local, zero_one_width)
        self.dither()
        rectangles    = self.draw_first_rectangles(zero_one_width)
        rect_clusters = self.draw_remaining_rectangles(rectangles)
        self.adjust_power_mobs(zero, power_mobs, rect_clusters[-1])
        self.dither()        
        num_mobs = self.draw_remaining_numbers(
            zero, power_mobs, rect_clusters
        )
        self.dither()
        self.add_negative_one(num_mobs)
        self.dither()
        self.show_distances(num_mobs, rect_clusters)


    def draw_numbers(self, zero_local, zero_one_width):
        num_numbers = 5
        zero = tex_mobject("0").shift(zero_local)
        self.add(zero)
        nums = []
        for n in range(num_numbers):
            num = tex_mobject(str(2**n))
            num.scale(1.0/(n+1))
            num.shift(
                zero_local+\
                RIGHT*zero_one_width/(2.0**n)+\
                LEFT*0.05*n+\
                (0.4*RIGHT if n == 0 else ORIGIN) #Stupid
            )
            self.animate(FadeIn(num, run_time = 0.5))
            nums.append(num)
        return zero, nums

    def draw_first_rectangles(self, zero_one_width):
        side_buff = 0.05
        upper_buff = 0.5
        colors = get_room_colors()
        rectangles = []
        for n in range(4):
            rect = Rectangle(
                2*SPACE_HEIGHT-(n+2)*upper_buff, 
                zero_one_width/(2**n)-0.85*(n+1)*side_buff
            )
            rect.sort_points(np.linalg.norm)
            rect.to_edge(LEFT, buff = 0.2).shift(n*side_buff*RIGHT)
            rect.highlight(colors[n])
            rectangles.append(rect)
        for rect in rectangles:
            self.animate(ShowCreation(rect))
            self.dither()
        return rectangles

    def draw_remaining_rectangles(self, rectangles):
        clusters = []
        centers = [ORIGIN] + map(Mobject.get_center, rectangles)
        shift_vals = [
            2*(c2 - c1)[0]*RIGHT
            for c1, c2 in zip(centers[1:], centers)
        ]
        for rectangle, count in zip(rectangles, it.count(1)):
            cluster = [rectangle]
            for shift_val in shift_vals[:count]:
                cluster += map(
                    lambda mob : mob.shift(shift_val),
                    deepcopy(cluster)
                )
            clusters.append(cluster)
            for rect in cluster[1:]:
                self.animate(FadeIn(rect, run_time = 0.6**(count-1)))
        return clusters

    def adjust_power_mobs(self, zero, power_mobs, small_rects):
        new_zero = deepcopy(zero)
        self.center_in_closest_rect(new_zero, small_rects)
        new_power_mobs = deepcopy(power_mobs)        
        for mob, count in zip(new_power_mobs, it.count(1)):
            self.center_in_closest_rect(mob, small_rects)
        new_power_mobs[-1].shift(DOWN)
        dots = tex_mobject("\\vdots")
        dots.scale(0.5).shift(new_zero.get_center()+0.5*DOWN)
        self.animate(
            Transform(zero, new_zero),
            FadeIn(dots),
            *[
                Transform(old, new)
                for old, new in zip(power_mobs, new_power_mobs)
            ]
        )

    def draw_remaining_numbers(self, zero, power_mobs, rect_clusters):
        small_rects = rect_clusters[-1]
        max_width = 0.8*small_rects[0].get_width()
        max_power = 4
        num_mobs = [None]*(2**max_power + 1)
        num_mobs[0] = zero
        powers = [2**k for k in range(max_power+1)]
        for p, index in zip(powers, it.count()):
            num_mobs[p] = power_mobs[index]
        for power, count in zip(powers[1:-1], it.count(1)):
            zero_copy = deepcopy(zero)
            power_mob_copy = deepcopy(num_mobs[power])
            def transform(mob):
                self.center_in_closest_rect(mob, small_rects)
                mob.shift(UP)
                return mob
            self.animate(*[
                ApplyFunction(transform, mob)
                for mob in zero_copy, power_mob_copy
            ])
            last_left_mob = zero
            for n in range(power+1, 2*power):
                left_mob = num_mobs[n-power]
                shift_val = left_mob.get_center()-last_left_mob.get_center()
                self.animate(*[
                    ApplyMethod(mob.shift, shift_val)
                    for mob in zero_copy, power_mob_copy
                ])
                num_mobs[n] = tex_mobject(str(n))
                num_mobs[n].scale(1.0/(power_of_divisor(n, 2)+1))
                width_ratio = max_width / num_mobs[n].get_width()
                if width_ratio < 1: 
                    num_mobs[n].scale(width_ratio)
                num_mobs[n].shift(power_mob_copy.get_center()+DOWN)
                self.center_in_closest_rect(num_mobs[n], small_rects)
                point = Point(power_mob_copy.get_center())
                self.animate(Transform(point, num_mobs[n]))
                self.remove(point)
                self.add(num_mobs[n])
                last_left_mob = left_mob
            self.remove(zero_copy, power_mob_copy)
            self.dither()
        return num_mobs

    @staticmethod
    def center_in_closest_rect(mobject, rectangles):
        center = mobject.get_center()
        diffs = [r.get_center()-center for r in rectangles]
        mobject.shift(diffs[np.argmin(map(np.linalg.norm, diffs))])

    def add_negative_one(self, num_mobs):
        neg_one = tex_mobject("-1").scale(0.5)
        shift_val = num_mobs[15].get_center()-neg_one.get_center()
        neg_one.shift(UP)
        self.animate(ApplyMethod(neg_one.shift, shift_val))

    def show_distances(self, num_mobs, rect_clusters):
        self.remove(*[r for c in rect_clusters for r in c])
        text = None
        for cluster, count in zip(rect_clusters, it.count()):
            if text is not None:
                self.remove(text)
            if count == 0:
                dist_string = "1"
            else:
                dist_string = "$\\frac{1}{%d}$"%(2**count)
            text = text_mobject(
                "Any of these pairs are considered to be a distance " +\
                dist_string +\
                " away from each other"
            ).shift(2*UP)
            self.add(text)
            self.clear_way_for_text(text, cluster)
            self.add(*cluster)          
            pairs = filter(
                lambda (a, b) : (a-b)%(2**count) == 0 and (a-b)%(2**(count+1)) != 0,
                it.combinations(range(16), 2)
            )
            for pair in sample(pairs, min(10, len(pairs))):
                for index in pair:
                    num_mobs[index].highlight("green")
                self.animate(*[
                    ApplyMethod(
                        num_mobs[index].rotate_in_place, np.pi/10, 
                        alpha_func = wiggle
                    )
                    for index in pair
                ])
                self.dither()
                for index in pair:
                    num_mobs[index].highlight("white")

    @staticmethod
    def clear_way_for_text(text, mobjects):
        right, top, null = np.max(text.points, 0)
        left, bottom, null = np.min(text.points, 0)
        def filter_func((x, y, z)):
            return x>left and x<right and y>bottom and y<top
        for mobject in mobjects:
            mobject.filter_out(filter_func)



class DiscoveryAndInvention(Scene):
    def construct(self):
        invention, vs, discovery = text_mobject([
            "Invention ", "vs. ", "Discovery"
        ]).split()
        nrd = text_mobject(
            "Non-rigorous truths"
        ).shift(2*UP)
        rt = text_mobject(
            "Rigorous terms"
        ).shift(2*DOWN)
        
        arrows = []
        self.add(discovery, vs, invention)
        self.dither()
        arrow = Arrow(
            nrd.get_bottom(),
            tail = discovery.get_top()
        )
        self.animate(
            FadeIn(nrd),
            ShowCreation(arrow)
        )
        arrows.append(arrow)
        self.dither()
        arrow = Arrow(
            invention.get_top(),
            tail = nrd.get_bottom()
        )
        self.animate(ShowCreation(arrow))
        arrows.append(arrow)
        self.dither()
        arrow = Arrow(
            rt.get_top(),
            tail = invention.get_bottom()
        )
        self.animate(
            FadeIn(rt),
            ShowCreation(arrow)
        )
        arrows.append(arrow)
        self.dither()
        arrow = Arrow(
            discovery.get_bottom(),
            tail = rt.get_top()
        )
        self.animate(ShowCreation(arrow))
        self.dither()
        arrows.append(arrow)
        for color in Color("yellow").range_to("red", 4):
            for arrow in arrows:
                self.animate(
                    ShowCreation(deepcopy(arrow).highlight(color)),
                    run_time = 0.25
                )










if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)

