#!/usr/bin/env python

import numpy as np
import itertools as it
from copy import deepcopy
import sys
import operator as op
from random import sample

from manimlib.imports import *
from script_wrapper import command_line_create_scene
from functools import reduce

# from inventing_math_images import *

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
    return TexMobject(DIVERGENT_SUM_TEXT, size = "\\large").scale(2)

def convergent_sum():
    return TexMobject(CONVERGENT_SUM_TEXT, size = "\\large").scale(2)

def Underbrace(left, right):
    result = TexMobject("\\Underbrace{%s}"%(14*"\\quad"))
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
    zero = TexMobject("0").shift(INTERVAL_RADIUS*LEFT+DOWN)
    one = TexMobject("1").shift(INTERVAL_RADIUS*RIGHT+DOWN)
    return Mobject(interval, zero, one)

def draw_you(with_bubble = False):
    result = PiCreature()
    result.give_straight_face().set_color("grey")
    result.to_corner(LEFT+DOWN)
    result.rewire_part_attributes()
    if with_bubble:
        bubble = ThoughtBubble()
        bubble.stretch_to_fit_width(11)
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
        mobject = TexMobject(str(self.current_number)).shift(start_center)
        Animation.__init__(self, mobject, **kwargs)

    def interpolate_mobject(self, alpha):
        new_number = self.function(
            self.start + int(alpha *(self.end-self.start))
        )
        if new_number != self.current_number:
            self.current_number = new_number
            self.mobject = TexMobject(str(new_number)).shift(self.start_center)
        if not all(self.start_center == self.end_center):
            self.mobject.center().shift(
                (1-alpha)*self.start_center + alpha*self.end_center
            )


######################################

class IntroduceDivergentSum(Scene):
    def construct(self):
        equation = divergent_sum().split()
        sum_value = None
        brace = Underbrace(
            equation[0].get_boundary_point(DOWN+LEFT),
            equation[1].get_boundary_point(DOWN+RIGHT)
        ).shift(0.2*DOWN)
        min_x_coord = min(equation[0].points[:,0])
        for x in range(NUM_WRITTEN_TERMS):
            self.add(equation[x])
            if x == 0:
                self.wait(0.75)
                continue
            brace.stretch_to_fit_width(
                max(equation[x].points[:,0]) - min_x_coord
            )
            brace.to_edge(LEFT, buff = FRAME_X_RADIUS+min_x_coord)
            if sum_value:
                self.remove(sum_value)
            sum_value = TexMobject(str(2**(x+1) - 1))
            sum_value.shift(brace.get_center() + 0.5*DOWN)
            self.add(brace, sum_value)
            self.wait(0.75)
        self.remove(sum_value)
        ellipses = Mobject(
            *[equation[NUM_WRITTEN_TERMS + i] for i in range(3)]
        )
        end_brace = deepcopy(brace).stretch_to_fit_width(
            max(ellipses.points[:,0])-min_x_coord
        ).to_edge(LEFT, buff = FRAME_X_RADIUS+min_x_coord)
        kwargs = {"run_time" : 5.0, "rate_func" : rush_into}        
        flip_through = FlipThroughNumbers(
            lambda x : 2**(x+1)-1,
            start = NUM_WRITTEN_TERMS-1,
            end = 50,
            start_center = brace.get_center() + 0.5*DOWN,
            end_center = end_brace.get_center() + 0.5*DOWN,
            **kwargs
        )
        self.add(ellipses)
        self.play(
            Transform(brace, end_brace, **kwargs),
            flip_through,
        )
        self.clear()
        self.add(*equation)
        self.wait()

class ClearlyNonsense(Scene):
    def construct(self):
        number_line = NumberLine().add_numbers()
        div_sum = divergent_sum()
        this_way = TextMobject("Sum goes this way...")
        this_way.to_edge(LEFT).shift(RIGHT*(FRAME_X_RADIUS+1) + DOWN)
        how_here = TextMobject("How does it end up here?")
        how_here.shift(1.5*UP+LEFT)
        neg_1_arrow = Arrow(
            (-1, 0.3, 0), 
            tail=how_here.get_center()+0.5*DOWN
        )
        right_arrow = Arrow(
            (FRAME_X_RADIUS-0.5)*RIGHT + DOWN, 
            tail = (max(this_way.points[:,0]), -1, 0)
        )
        how_here.set_color("red")
        neg_1_arrow.set_color("red")
        this_way.set_color("yellow")
        right_arrow.set_color("yellow")

        self.play(Transform(
            div_sum, 
            deepcopy(div_sum).scale(0.5).shift(3*UP)
        ))
        self.play(ShowCreation(number_line))
        self.wait()
        self.add(how_here)
        self.play(ShowCreation(neg_1_arrow))
        self.wait()
        self.add(this_way)
        self.play(ShowCreation(right_arrow))
        self.wait()

class OutlineOfVideo(Scene):
    def construct(self):
        conv_sum = convergent_sum().scale(0.5)
        div_sum = divergent_sum().scale(0.5)
        overbrace = Underbrace(
            conv_sum.get_left(),
            conv_sum.get_right()
        ).rotate(np.pi, RIGHT).shift(0.75*UP*conv_sum.get_height())
        dots = conv_sum.split()[-2].set_color("green")
        dots.sort_points()
        arrow = Arrow(
            dots.get_bottom(),
            direction = UP+LEFT
        )
        u_brace = Underbrace(div_sum.get_left(), div_sum.get_right())
        u_brace.shift(1.5*div_sum.get_bottom())
        for mob in conv_sum, overbrace, arrow, dots:
            mob.shift(2*UP)
        for mob in div_sum, u_brace:
            mob.shift(DOWN)
        texts = [
            TextMobject(words).set_color("yellow")
            for words in [
                "1. Discover this",
                "2. Clarify what this means",
                "3. Discover this",
                ["4. Invent ", "\\textbf{new math}"]
            ]
        ]
        last_one_split = texts[-1].split()
        last_one_split[1].set_color("skyblue")
        texts[-1] = Mobject(*last_one_split)
        texts[0].shift(overbrace.get_top()+texts[0].get_height()*UP)
        texts[1].shift(sum([
            arrow.get_boundary_point(DOWN+RIGHT),
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
            self.play(*[
                DelayByOrder(FadeIn(element))
                for element in group
            ])
            self.wait()

# # class ReasonsForMakingVideo(Scene):
# #     def construct(self):
# #         text = TextMobject([
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
# #         text.scale(1.5).to_edge(LEFT).shift(UP).set_color("white")
# #         text.set_color("green", lambda (x, y, z) : x < -FRAME_X_RADIUS + 1)
# #         line_one_first, equation, line_one_last, line_two = text.split()
# #         line_two.shift(2*DOWN)
# #         div_sum = divergent_sum().scale(0.5).shift(3*UP)

# #         self.add(div_sum)
# #         self.play(
# #             ApplyMethod(div_sum.replace, equation),
# #             FadeIn(line_one_first),
# #             FadeIn(line_one_last)
# #         )
# #         self.wait()
# #         self.add(line_two)
# #         self.wait()

# class DiscoverAndDefine(Scene):
#     def construct(self):
#         sum_mob = TexMobject("\\sum_{n = 1}^\\infty a_n")
#         discover = TextMobject("What does it feel like to discover these?")
#         define = TextMobject([
#             "What does it feel like to", 
#             "\\emph{define} ",
#             "them?"
#         ])
#         sum_mob.shift(2*UP)
#         define.shift(2*DOWN)
#         define_parts = define.split()
#         define_parts[1].set_color("skyblue")

#         self.add(sum_mob)
#         self.play(FadeIn(discover))
#         self.wait()
#         self.play(FadeIn(Mobject(*define_parts)))
#         self.wait()

class YouAsMathematician(Scene):
    def construct(self):
        you, bubble = draw_you(with_bubble = True)
        explanation = TextMobject(
            "You as a (questionably accurate portrayal of a) mathematician.",
            size = "\\small"
        ).shift([2, you.get_center()[1], 0])
        arrow = Arrow(you.get_center(), direction = LEFT)
        arrow.nudge(you.get_width())
        for mob in arrow, explanation:
            mob.set_color("yellow")
        equation = convergent_sum()
        bubble.add_content(equation)
        equation_parts = equation.split()
        equation.shift(0.5*RIGHT)
        bubble.clear()
        dot_pair = [
            Dot(density = 3*DEFAULT_POINT_DENSITY_1D).shift(x+UP)
            for x in (LEFT, RIGHT)
        ]
        self.add(you, explanation)
        self.play(
            ShowCreation(arrow),
            BlinkPiCreature(you)
        )
        self.wait()
        self.play(ShowCreation(bubble))
        for part in equation_parts:
            self.play(DelayByOrder(FadeIn(part)), run_time = 0.5)
        self.wait()
        self.play(
            BlinkPiCreature(you),
            FadeOut(explanation),
            FadeOut(arrow)
        )
        self.remove(bubble, *equation_parts)
        self.disapproving_friend()
        self.add(bubble, equation)
        self.play(Transform(equation, Mobject(*dot_pair)))
        self.remove(equation)
        self.add(*dot_pair)
        two_arrows = [
            Arrow(x, direction = x).shift(UP).nudge()
            for x in (LEFT, RIGHT)
        ]
        self.play(*[ShowCreation(a) for a in two_arrows])
        self.play(BlinkPiCreature(you))
        self.remove(*dot_pair+two_arrows)
        everything = Mobject(*self.mobjects)
        self.clear()
        self.play(
            ApplyPointwiseFunction(
                lambda p : 3*FRAME_X_RADIUS*p/get_norm(p),                
                everything
            ),
            *[
                Transform(dot, deepcopy(dot).shift(DOWN).scale(3)) 
                for dot in dot_pair
            ],
            run_time = 2.0
        )
        self.wait()

    def disapproving_friend(self):
        friend = Mortimer().to_corner(DOWN+RIGHT)
        bubble = SpeechBubble().pin_to(friend)
        bubble.write("It's simply not rigorous!")
        bubble.content.sort_points(lambda p : np.dot(p, DOWN+RIGHT))

        self.add(friend, bubble)
        self.play(DelayByOrder(FadeIn(bubble.content)))
        self.wait()
        self.remove(friend, bubble, bubble.content)


class DotsGettingCloser(Scene):
    def construct(self):
        dots = [
            Dot(radius = 3*Dot.DEFAULT_RADIUS).shift(3*x)
            for x in (LEFT, RIGHT)
        ]
        self.add(*dots)
        self.wait()
        for x in range(10):
            distance = min(dots[1].points[:,0])-max(dots[0].points[:,0])
            self.play(ApplyMethod(dots[0].shift, 0.5*distance*RIGHT))


class ZoomInOnInterval(Scene):
    def construct(self):
        number_line = NumberLine(density = 10*DEFAULT_POINT_DENSITY_1D)
        number_line.add_numbers()
        interval = zero_to_one_interval().split()

        new_line = deepcopy(number_line)
        new_line.set_color("black", lambda x_y_z1 : x_y_z1[0] < 0 or x_y_z1[0] > 1 or x_y_z1[1] < -0.2)
        # height = new_line.get_height()
        new_line.scale(2*INTERVAL_RADIUS)
        new_line.shift(INTERVAL_RADIUS*LEFT)
        # new_line.stretch_to_fit_height(height)

        self.add(number_line)
        self.wait()
        self.play(Transform(number_line, new_line))
        self.clear()
        squish = lambda p : (p[0], 0, 0)
        self.play(
            ApplyMethod(new_line.apply_function, squish),
            ApplyMethod(
                interval[0].apply_function, squish,
                rate_func = lambda t : 1-t
            ),
            *[FadeIn(interval[x]) for x in [1, 2]]
        )
        self.clear()
        self.add(*interval)
        self.wait()

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
            for x in (LEFT, RIGHT)
        ]
        color_range = Color("green").range_to("yellow", num_written_terms)
        conv_sum = TexMobject(sum_terms, size = "\\large").split()

        self.add(interval)
        self.play(*[
            ApplyMethod(dot.shift, DOWN)
            for dot in dots
        ])
        self.wait()
        for count in range(num_written_terms):
            shift_val = 2*RIGHT*INTERVAL_RADIUS*(1-prop)*(prop**count)
            start = dots[0].get_center()
            line = Line(start, start + shift_val*RIGHT)
            line.set_color(next(color_range))
            self.play(
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
            self.play(
                ApplyMethod(line.shift, 2*DOWN),
                FadeIn(num),
                FadeIn(arrow),
            )
        self.wait()
        self.write_partial_sums()
        self.wait()

    def write_partial_sums(self):
        partial_sums = TexMobject(PARTIAL_CONVERGENT_SUMS_TEXT, size = "\\small")
        partial_sums.scale(1.5).to_edge(UP)
        partial_sum_parts = partial_sums.split()
        partial_sum_parts[0].set_color("yellow")

        for x in range(0, len(partial_sum_parts), 4):
            partial_sum_parts[x+2].set_color("yellow")
            self.play(*[
                FadeIn(partial_sum_parts[y])
                for y in range(x, x+4)
            ])
        self.wait(2)

class OrganizePartialSums(Scene):
    def construct(self):
        partial_sums = TexMobject(PARTIAL_CONVERGENT_SUMS_TEXT, size = "\\small")
        partial_sums.scale(1.5).to_edge(UP)
        partial_sum_parts = partial_sums.split()
        for x in [0] + list(range(2, len(partial_sum_parts), 4)):
            partial_sum_parts[x].set_color("yellow")
        pure_sums = [
            partial_sum_parts[x] 
            for x in range(0, len(partial_sum_parts), 4)
        ]
        new_pure_sums = deepcopy(pure_sums)
        for pure_sum, count in zip(new_pure_sums, it.count(3, -1.2)):
            pure_sum.center().scale(1/1.25).set_color("white")
            pure_sum.to_edge(LEFT).shift(2*RIGHT+count*UP)

        self.add(*partial_sum_parts)
        self.wait()
        self.play(*[
            ClockwiseTransform(*pair)
            for pair in zip(pure_sums, new_pure_sums)
        ]+[
            FadeOut(mob)
            for mob in partial_sum_parts
            if mob not in pure_sums
        ])
        down_arrow = TexMobject("\\downarrow")
        down_arrow.to_edge(LEFT).shift(2*RIGHT+2*DOWN)
        dots = TexMobject("\\vdots")
        dots.shift(down_arrow.get_center()+down_arrow.get_height()*UP)
        infinite_sum = TexMobject("".join(CONVERGENT_SUM_TEXT[:-1]), size = "\\samll")
        infinite_sum.scale(1.5/1.25)
        infinite_sum.to_corner(DOWN+LEFT).shift(2*RIGHT)

        self.play(ShowCreation(dots))
        self.wait()
        self.play(FadeIn(Mobject(down_arrow, infinite_sum)))
        self.wait()

class SeeNumbersApproachOne(Scene):
    def construct(self):
        interval = zero_to_one_interval()
        arrow = Arrow(INTERVAL_RADIUS*RIGHT, tail=ORIGIN).nudge()
        arrow.shift(DOWN).set_color("yellow")
        num_dots = 6
        colors = Color("green").range_to("yellow", num_dots)
        dots = Mobject(*[
            Dot(
                density = 2*DEFAULT_POINT_DENSITY_1D
            ).scale(1+1.0/2.0**x).shift(
                INTERVAL_RADIUS*RIGHT +\
                (INTERVAL_RADIUS/2.0**x)*LEFT
            ).set_color(next(colors))
            for x in range(num_dots)
        ])

        self.add(interval)
        self.play(
            ShowCreation(arrow),
            ShowCreation(dots),
            run_time = 2.0
        )
        self.wait()

class OneAndInfiniteSumAreTheSameThing(Scene):
    def construct(self):
        one, equals, inf_sum = TexMobject([
            "1", "=", "\\sum_{n=1}^\\infty \\frac{1}{2^n}"
        ]).split()
        point = Point(equals.get_center()).set_color("black")

        self.add(one.shift(LEFT))
        self.wait()
        self.add(inf_sum.shift(RIGHT))
        self.wait()
        self.play(
            ApplyMethod(one.shift, RIGHT),
            ApplyMethod(inf_sum.shift, LEFT),
            CounterclockwiseTransform(point, equals)
        )
        self.wait()


class HowDoYouDefineInfiniteSums(Scene):
    def construct(self):
        you = draw_you().center().rewire_part_attributes()
        text = TextMobject(
            ["How", " do", " you,\\\\", "\\emph{define}"],
            size = "\\Huge"
        ).shift(UP).split()
        text[-1].shift(3*DOWN).set_color("skyblue")
        sum_mob = TexMobject("\\sum_{n=0}^\\infty{a_n}")
        text[-1].shift(LEFT)
        sum_mob.shift(text[-1].get_center()+2*RIGHT)

        self.add(you)
        self.wait()
        for mob in text[:-1]:
            self.add(mob)
            self.wait(0.1)
        self.play(BlinkPiCreature(you))
        self.wait()
        self.add(text[-1])
        self.wait()
        self.add(sum_mob)
        self.wait()


class LessAboutNewThoughts(Scene):
    def construct(self):
        words = generating, new, thoughts, to, definitions = TextMobject([
            "Generating", " new", " thoughts", "$\\rightarrow$",
            "useful definitions"
        ], size = "\\large").split()
        gen_cross = TexMobject("\\hline").set_color("red")
        new_cross = deepcopy(gen_cross)
        for cross, mob in [(gen_cross, generating), (new_cross, new)]:
            cross.replace(mob)
            cross.stretch_to_fit_height(0.03)
        disecting = TextMobject("Disecting").set_color("green")
        disecting.shift(generating.get_center() + 0.6*UP)
        old = TextMobject("old").set_color("green")
        old.shift(new.get_center()+0.6*UP)

        kwargs = {"run_time" : 0.25}
        self.add(*words)
        self.wait()
        self.play(ShowCreation(gen_cross, **kwargs))
        self.play(ShowCreation(new_cross, **kwargs))
        self.wait()        
        self.add(disecting)
        self.wait(0.5)
        self.add(old)
        self.wait()

class ListOfPartialSums(Scene):
    def construct(self):
        all_terms = np.array(TexMobject(
            ALT_PARTIAL_SUM_TEXT,
            size = "\\large"
        ).split())
        numbers, equals, sums = [
            all_terms[list(range(k, 12, 3))]
            for k in (0, 1, 2)
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
        self.play(ShowCreation(dots))
        self.wait()
        self.play(
            FadeIn(Mobject(*equals)),
            *[
                Transform(deepcopy(number), finite_sum)
                for number, finite_sum in zip(numbers, sums)
            ]
        )
        self.wait()
        self.play(*[
            ApplyMethod(s.set_color, "yellow", rate_func = there_and_back)
            for s in sums
        ])
        self.wait()
        self.add(one.set_color("green"))
        self.wait()


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
            line.set_color("green")
        dots = Mobject(*[
            Dot().scale(1.0/(n+1)).shift((1+partial_sum(n))*RIGHT)
            for n in range(10)
        ])

        self.add(dots.split()[0])
        self.add(number_line, *lines)
        self.wait()
        self.play(
            ApplyMethod(vert_line0.shift, RIGHT),
            Transform(
                horiz_line, 
                Line(vert_line0.end+RIGHT, vert_line1.end).set_color("green")
            ),
            ShowCreation(dots),
            run_time = 2.5
        )
        self.wait()

class CircleZoomInOnOne(Scene):
    def construct(self):
        number_line = NumberLine(interval_size = 1).add_numbers()
        dots = Mobject(*[
            Dot().scale(1.0/(n+1)).shift((1+partial_sum(n))*RIGHT)
            for n in range(10)
        ])
        circle = Circle().shift(2*RIGHT)
        text = TextMobject(
            "All but finitely many dots fall inside even the tiniest circle."
        )
        numbers = [TexMobject("\\frac{1}{%s}"%s) for s in ["100", "1,000,000", "g_{g_{64}}"]]
        for num in numbers + [text]:
            num.shift(2*UP)
            num.sort_points(lambda p : np.dot(p, DOWN+RIGHT))
        curr_num = numbers[0]
        arrow = Arrow(2*RIGHT, direction = 1.5*(DOWN+RIGHT)).nudge()

        self.add(number_line, dots)
        self.play(
            Transform(circle, Point(2*RIGHT).set_color("white")),
            run_time = 5.0
        )

        self.play(*[
            DelayByOrder(FadeIn(mob))
            for mob in (arrow, curr_num)
        ])
        self.wait()
        for num in numbers[1:] + [text]:
            curr_num.points = np.array(list(reversed(curr_num.points)))
            self.play(
                ShowCreation(
                    curr_num, 
                    rate_func = lambda t : smooth(1-t)
                ),
                ShowCreation(num)
            )
            self.remove(curr_num)
            curr_num = num
            self.wait()

class ZoomInOnOne(Scene):
    def construct(self):
        num_iterations = 8
        number_line = NumberLine(interval_size = 1, radius = FRAME_X_RADIUS+2)
        number_line.filter_out(lambda x_y_z2:abs(x_y_z2[1])>0.1)
        nl_with_nums = deepcopy(number_line).add_numbers()
        self.play(ApplyMethod(nl_with_nums.shift, 2*LEFT))
        zero, one, two = [
            TexMobject(str(n)).scale(0.5).shift(0.4*DOWN+2*(-1+n)*RIGHT)
            for n in (0, 1, 2)
        ]
        self.play(
            FadeOut(nl_with_nums),
            *[Animation(mob) for mob in (zero, one, two, number_line)]
        )
        self.remove(nl_with_nums, number_line, zero, two)
        powers_of_10 = [10**(-n) for n in range(num_iterations+1)]
        number_pairs = [(1-epsilon, 1+epsilon) for epsilon in powers_of_10]
        for count in range(num_iterations):
            self.zoom_with_numbers(number_pairs[count], number_pairs[count+1])
            self.clear()
            self.add(one)

    def zoom_with_numbers(self, numbers, next_numbers):
        all_numbers = [TexMobject(str(n_u[0])).scale(0.5).shift(0.4*DOWN+2*n_u[1]*RIGHT) for n_u in zip(numbers+next_numbers, it.cycle([-1, 1]))]

        num_levels = 3
        scale_factor = 10
        number_lines = [
            NumberLine(
                interval_size = 1, 
                density = scale_factor*DEFAULT_POINT_DENSITY_1D
            ).filter_out(
                lambda x_y_z:abs(x_y_z[1])>0.1
            ).scale(1.0/scale_factor**x)
            for x in range(num_levels)
        ]
        kwargs = {"rate_func" : None}
        self.play(*[
            ApplyMethod(number_lines[x].scale, scale_factor, **kwargs)
            for x in range(1, num_levels)
        ]+[
            ApplyMethod(number_lines[0].stretch, scale_factor, 0, **kwargs),
        ]+[
            ApplyMethod(
                all_numbers[i].shift, 
                2*LEFT*(scale_factor-1)*(-1)**i, 
                **kwargs
            )
            for i in (0, 1)
        ]+[
            Transform(Point(0.4*DOWN + u*0.2*RIGHT), num, **kwargs)
            for u, num in zip([-1, 1], all_numbers[2:])
        ])
        self.remove(*all_numbers)


class DefineInfiniteSum(Scene):
    def construct(self):
        self.put_expression_in_corner()
        self.list_partial_sums()
        self.wait()

    def put_expression_in_corner(self):
        buff = 0.24
        define, infinite_sum = TexMobject([
            "\\text{\\emph{Define} }",
            "\\sum_{n = 0}^\\infty a_n = X"
        ]).split()
        define.set_color("skyblue")
        expression = Mobject(define, infinite_sum)

        self.add(expression)
        self.wait()
        self.play(ApplyFunction(
            lambda mob : mob.scale(0.5).to_corner(UP+LEFT, buff = buff),
            expression            
        ))
        bottom = (min(expression.points[:,1]) - buff)*UP
        side   = (max(expression.points[:,0]) + buff)*RIGHT
        lines = [
            Line(FRAME_X_RADIUS*LEFT+bottom, side+bottom),
            Line(FRAME_Y_RADIUS*UP+side, side+bottom)
        ]
        self.play(*[
            ShowCreation(line.set_color("white"))
            for line in lines
        ])
        self.wait()

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
        terms = TexMobject(term_strings, size = "\\large").split()
        number_line = NumberLine()
        ex_point = 2*RIGHT
        ex = TexMobject("X").shift(ex_point + LEFT + UP)
        arrow = Arrow(ex_point, tail = ex.points[-1]).nudge()

        for term, count in zip(terms, it.count()):
            self.add(term)
            self.wait(0.1)
            if count % 3 == 2:
                self.wait(0.5)
        self.wait()
        esses = np.array(terms)[list(range(0, len(terms), 3))]
        other_terms = [m for m in terms if m not in esses]
        self.play(*[
            ApplyMethod(ess.set_color, "yellow")
            for ess in esses
        ])

        def move_s(s, n):
            s.center()
            s.scale(1.0/(n+1))
            s.shift(ex_point-RIGHT*2.0/2**n)
            return s
        self.play(*[
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
            Line(x+0.25*DOWN, x+0.25*UP).set_color("white")
            for y in [-1, -0.01, 1, 0.01]
            for x in [ex_point+y*RIGHT]
        ]
        self.play(*[
            Transform(lines[x], lines[x+1], run_time = 3.0)
            for x in (0, 2)
        ])


class YouJustInventedSomeMath(Scene):
    def construct(self):
        text = TextMobject([
            "You ", "just ", "invented\\\\", "some ", "math"
        ]).split()
        for mob in text[:3]:
            mob.shift(UP)
        for mob in text[3:]:
            mob.shift(1.3*DOWN)
        # you = draw_you().center().rewire_part_attributes()
        # smile = PiCreature().mouth.center().shift(you.mouth.get_center())
        you = PiCreature().set_color("grey")
        you.center().rewire_part_attributes()

        self.add(you)
        for mob in text:
            self.add(mob)
            self.wait(0.2)
        self.play(WaveArm(you))
        self.play(BlinkPiCreature(you))



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
        sums = TexMobject([
            "&\\sum_{n = 0}^\\infty" + summand + "= ? \\\\"
            for summand in summands
        ], size = "")
        sums.stretch_to_fit_height(FRAME_HEIGHT-1)
        sums.shift((FRAME_Y_RADIUS-0.5-max(sums.points[:,1]))*UP)

        for qsum in sums.split():
            qsum.sort_points(lambda p : np.dot(p, DOWN+RIGHT))
            self.play(DelayByOrder(FadeIn(qsum)))
            self.wait(0.5)
        self.wait()

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
                    TexMobject("\\frac{%d}{%d}"%(k, (10**(count+1))))
                    for count in range(num_terms)
                ]
                for k in (9, 1)
            ]
        if mode == "p":
            num_terms = 4         
            prop = 0.7
            left_terms = list(map(TexMobject, ["(1-p)", ["p","(1-p)"]]+[
                ["p^%d"%(count), "(1-p)"]
                for count in range(2, num_terms)
            ]))
            right_terms = list(map(TexMobject, ["p"] + [
                ["p", "^%d"%(count+1)]
                for count in range(1, num_terms)
            ]))
        interval = zero_to_one_interval()
        left = INTERVAL_RADIUS*LEFT
        right = INTERVAL_RADIUS*RIGHT
        left_paren = TexMobject("(")
        right_paren = TexMobject(")").shift(right + 1.1*UP)
        curr = left.astype("float")
        brace_to_replace = None
        term_to_replace = None

        self.add(interval)
        additional_anims = []
        for lt, rt, count in zip(left_terms, right_terms, it.count()):
            last = deepcopy(curr)
            curr += 2*RIGHT*INTERVAL_RADIUS*(1-prop)*(prop**count)
            braces = [
                Underbrace(a, b).rotate(np.pi, RIGHT)
                for a, b in [(last, curr), (curr, right)]
            ]
            for term, brace, count2 in zip([lt, rt], braces, it.count()):
                term.scale(0.75)
                term.shift(brace.get_center()+UP)                
                if term.get_width() > brace.get_width():
                    term.shift(UP+1.5*(count-2)*RIGHT)
                    arrow = Arrow(
                        brace.get_center()+0.3*UP,
                        tail = term.get_center()+0.5*DOWN
                    )
                    arrow.points = np.array(list(reversed(arrow.points)))
                    additional_anims = [ShowCreation(arrow)]
            if brace_to_replace is not None:
                if mode == "p":
                    lt, rt = lt.split(), rt.split()                    
                    if count == 1:
                        new_term_to_replace = deepcopy(term_to_replace)
                        new_term_to_replace.center().shift(last+UP+0.3*LEFT)
                        left_paren.center().shift(last+1.1*UP)
                        self.play(
                            FadeIn(lt[1]),
                            FadeIn(rt[0]),
                            Transform(
                                brace_to_replace.repeat(2),
                                Mobject(*braces)
                            ),
                            FadeIn(left_paren), 
                            FadeIn(right_paren),
                            Transform(term_to_replace, new_term_to_replace),
                            *additional_anims
                        )
                        self.wait()
                        self.play(
                            Transform(
                                term_to_replace,
                                Mobject(lt[0], rt[1])
                            ),
                            FadeOut(left_paren),
                            FadeOut(right_paren)
                        )
                        self.remove(left_paren, right_paren)
                    else:
                        self.play(
                            FadeIn(lt[1]),
                            FadeIn(rt[0]),
                            Transform(
                                brace_to_replace.repeat(2),
                                Mobject(*braces)
                            ),
                            Transform(
                                term_to_replace,
                                Mobject(lt[0], rt[1])
                            ),
                            *additional_anims
                        )
                    self.remove(*lt+rt)
                    lt, rt = Mobject(*lt), Mobject(*rt)
                    self.add(lt, rt)
                else:
                    self.play(
                        Transform(
                            brace_to_replace.repeat(2), 
                            Mobject(*braces)
                        ),
                        Transform(
                            term_to_replace,
                            Mobject(lt, rt)
                        ),
                        *additional_anims
                    )
                self.remove(brace_to_replace, term_to_replace)
                self.add(lt, rt, *braces)
            else:
                self.play(*[
                    FadeIn(mob)
                    for mob in braces + [lt, rt]
                ] + additional_anims)
            self.wait()
            brace_to_replace = braces[1]
            term_to_replace = rt
        if mode == "9":
            split_100 = TexMobject("\\frac{9}{1000}+\\frac{1}{1000}")
            split_100.scale(0.5)
            split_100.shift(right_terms[-1].get_center())
            split_100.to_edge(RIGHT)
            split_100.sort_points()
            right_terms[-1].sort_points()
            self.play(Transform(
                right_terms[-1], split_100
            ))
        self.wait()



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
            path = counterclockwise_path(),
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
        for term in TexMobject(start_terms).split():
            self.add(term)
            self.wait(0.5)
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
        lhs, rhs = TexMobject(
            ["1 + p + p^2 + p^3 + \\cdots = ", "\\frac{1}{1-p}"],
            size = "\\large"
        ).scale(scale_factor).split()
        rhs = TexMobject(
            ["1 \\over 1 - ", "p"], 
            size = "\\large"
        ).replace(rhs).split()
        num_strings = [
            "0.5", "3", "\pi", "(-1)", "3.7", "2",
            "0.2", "27", "i"
        ] 
        nums = [
            TexMobject(num_string, size="\\large")
            for num_string in num_strings
        ]
        for num, num_string in zip(nums, num_strings):
            num.scale(scale_factor)
            num.shift(rhs[1].get_center())
            num.shift(0.1*RIGHT + 0.08*UP)
            num.set_color("green")
            if num_string == "(-1)":
                num.shift(0.3*RIGHT)
        right_words = TextMobject(
            "This side makes sense for almost any value of $p$,"
        ).shift(2*UP)
        left_words = TextMobject(
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
        right_words.set_color("green")
        left_words.set_color("yellow")


        self.add(lhs, *rhs)
        self.wait()
        self.play(FadeIn(right_words))
        curr = rhs[1]
        for num, count in zip(nums, it.count()):
            self.play(CounterclockwiseTransform(curr, num))
            self.wait()
            if count == 2:
                self.play(FadeIn(left_words))


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
        terms = TexMobject(
            list(it.chain.from_iterable(list(zip(rhss, lhss)))) + ["\\vdots&", ""],
            size = "\\large"
        ).shift(RIGHT).split()
        words = TextMobject("These numbers don't \\\\ approach anything")
        words.to_edge(LEFT)
        arrow = Arrow(3*DOWN+2*LEFT, direction = DOWN, length = 6)

        for x in range(0, len(terms), 2):
            self.play(FadeIn(terms[x]), FadeIn(terms[x+1]))
        self.play(FadeIn(words), ShowCreation(arrow))
        for x in range(0, len(terms), 2):
            self.play(
                ApplyMethod(terms[x].set_color, "green"),
                run_time = 0.1
            )
        self.wait()

class NotARobot(Scene):
    def construct(self):
        you = draw_you().center()
        top_words = TextMobject("You are a mathematician,")
        low_words = TextMobject("not a robot.")
        top_words.shift(1.5*UP)
        low_words.shift(1.5*DOWN)
        
        self.add(you)
        self.play(ShimmerIn(top_words))
        self.play(ShimmerIn(low_words))


class SumPowersOfTwoAnimation(Scene):
    def construct(self):
        iterations = 5
        dot = Dot(density = 3*DEFAULT_POINT_DENSITY_1D).scale(1.5)
        dot_width = dot.get_width()*RIGHT
        dot_buff = 0.2*RIGHT
        left = (FRAME_X_RADIUS-1)*LEFT
        right = left + 2*dot_width + dot_buff
        top_brace_left = left+dot_width+dot_buff+0.3*DOWN
        bottom_brace_left = left + 0.3*DOWN
        circle = Circle().scale(dot_width[0]/2).shift(left+dot_width/2)
        curr_dots = deepcopy(dot).shift(left+1.5*dot_width+dot_buff)
        topbrace = Underbrace(top_brace_left, right).rotate(np.pi, RIGHT)
        bottombrace = Underbrace(bottom_brace_left, right)
        colors = Color("yellow").range_to("purple", iterations)
        curr_dots.set_color(next(colors))
        equation = TexMobject(
            "1+2+4+\\cdots+2^n=2^{n+1} - 1",
            size = "\\Huge"
        ).shift(3*UP)
        full_top_sum = TexMobject(["1", "+2", "+4", "+8", "+16"]).split()

        self.add(equation)
        self.wait()
        self.add(circle, curr_dots, topbrace, bottombrace)
        for n in range(1,iterations):
            bottom_num = TexMobject(str(2**n))
            new_bottom_num = TexMobject(str(2**(n+1)))            
            bottom_num.shift(bottombrace.get_center()+0.5*DOWN)

            top_sum = Mobject(*full_top_sum[:n]).center()
            top_sum_end = deepcopy(full_top_sum[n]).center()
            top_sum.shift(topbrace.get_center()+0.5*UP)
            new_top_sum = Mobject(*full_top_sum[:(n+1)]).center()
            self.add(top_sum, bottom_num)

            if n == iterations:
                continue
            new_dot = deepcopy(dot).shift(circle.get_center())
            shift_val = (2**n)*(dot_width+dot_buff)
            right += shift_val
            new_dots = Mobject(new_dot, curr_dots)
            new_dots.set_color(next(colors)).shift(shift_val)
            alt_bottombrace = deepcopy(bottombrace).shift(shift_val)
            alt_bottom_num = deepcopy(bottom_num).shift(shift_val)
            alt_topbrace = deepcopy(alt_bottombrace).rotate(np.pi, RIGHT)
            top_sum_end.shift(alt_topbrace.get_center()+0.5*UP)
            new_topbrace = Underbrace(top_brace_left, right).rotate(np.pi, RIGHT)
            new_bottombrace = Underbrace(bottom_brace_left, right)
            new_bottom_num.shift(new_bottombrace.get_center()+0.5*DOWN)
            new_top_sum.shift(new_topbrace.get_center()+0.5*UP)
            for exp, brace in [
                    (top_sum, topbrace),
                    (top_sum_end, alt_topbrace),
                    (new_top_sum, new_topbrace),
                ]:
                if exp.get_width() > brace.get_width():
                    exp.stretch_to_fit_width(brace.get_width())
            new_top_sum = new_top_sum.split()
            new_top_sum_start = Mobject(*new_top_sum[:-1])
            new_top_sum_end = new_top_sum[-1]

            self.wait()            
            self.play(*[
                FadeIn(mob)
                for mob in [
                    new_dots, 
                    alt_topbrace, 
                    alt_bottombrace, 
                    top_sum_end,
                    alt_bottom_num,
                ]
            ])
            self.wait()
            self.play(
                Transform(topbrace, new_topbrace),
                Transform(alt_topbrace, new_topbrace),
                Transform(bottombrace, new_bottombrace),
                Transform(alt_bottombrace, new_bottombrace),
                Transform(bottom_num, new_bottom_num),
                Transform(alt_bottom_num, new_bottom_num),
                Transform(top_sum, new_top_sum_start),
                Transform(top_sum_end, new_top_sum_end)
            )
            self.remove(
                bottom_num, alt_bottom_num, top_sum, 
                top_sum_end, new_top_sum_end,
                alt_topbrace, alt_bottombrace
            )
            curr_dots = Mobject(curr_dots, new_dots)

        
class PretendTheyDoApproachNegativeOne(RearrangeEquation):
    def construct(self):
        num_lines = 6
        da = "\\downarrow"
        columns = [
            TexMobject("\\\\".join([
                n_func(n)
                for n in range(num_lines)
            ]+last_bits), size = "\\Large").to_corner(UP+LEFT)
            for n_func, last_bits in [
               (lambda n : str(2**(n+1)-1), ["\\vdots", da, "-1"]),
               (lambda n : "+1", ["", "", "+1"]),
               (lambda n : "=", ["", "", "="]),
               (lambda n : str(2**(n+1)), ["\\vdots", da, "0"]),
            ]
        ]
        columns[-1].set_color()
        columns[2].shift(0.2*DOWN)
        shift_val = 3*RIGHT
        for column in columns:
            column.shift(shift_val)
            shift_val = shift_val + (column.get_width()+0.2)*RIGHT            
        self.play(ShimmerIn(columns[0]))
        self.wait()
        self.add(columns[1])
        self.wait()
        self.play(
            DelayByOrder(Transform(deepcopy(columns[0]), columns[-1])),
            FadeIn(columns[2])
        )
        self.wait()

class DistanceBetweenRationalNumbers(Scene):
    def construct(self):
        locii = [2*LEFT, 2*RIGHT]
        nums = [
            TexMobject(s).shift(1.3*d)
            for s, d in zip(["\\frac{1}{2}", "3"], locii)
        ]            
        arrows = [
            Arrow(direction, tail = ORIGIN)
            for direction in locii
        ]
        dist = TexMobject("\\frac{5}{2}").scale(0.5).shift(0.5*UP)
        text = TextMobject("How we define distance between rational numbers")
        text.to_edge(UP)
        self.add(text, *nums)
        self.play(*[ShowCreation(arrow) for arrow in arrows])
        self.play(ShimmerIn(dist))
        self.wait()

class NotTheOnlyWayToOrganize(Scene):
    def construct(self):
        self.play(ShowCreation(NumberLine().add_numbers()))
        self.wait()
        words = "Is there any other reasonable way to organize numbers?"
        self.play(FadeIn(TextMobject(words).shift(2*UP)))
        self.wait()

class DistanceIsAFunction(Scene):
    args_list = [
        ("Euclidian",),
        ("Random",),
        ("2adic",),
    ]
    @staticmethod
    def args_to_string(word):
        return word

    def construct(self, mode):
        if mode == "Euclidian":
            dist_text = "dist"
        elif mode == "Random":
            dist_text = "random\\_dist"
        elif mode == "2adic":
            dist_text = "2\\_adic\\_dist"
        dist, r_paren, arg0, comma, arg1, l_paren, equals, result = TextMobject([
            dist_text, "(", "000", ",", "000", ")", "=", "000"
        ]).split()
        point_origin = comma.get_center()+0.2*UP
        if mode == "Random":
            examples = [
                ("2", "3", "7"),
                ("\\frac{1}{2}", "100", "\\frac{4}{5}"),
            ]
            dist.set_color("orange")
            self.add(dist)
            self.wait()
        elif mode == "Euclidian":
            examples = [
                ("1", "5", "4"),
                ("\\frac{1}{2}", "3", "\\frac{5}{2}"),
                ("-3", "3", "6"),
                ("2", "3", "1"),
                ("0", "4", "x"),
                ("1", "5", "x"),
                ("2", "6", "x"),
            ]
        elif mode == "2adic":
            examples = [
                ("2", "0", "\\frac{1}{2}"),
                ("-1", "15", "\\frac{1}{16}"),
                ("3", "7", "\\frac{1}{4}"),
                ("\\frac{3}{2}", "1", "2"),
            ]
            dist.set_color("green")
            self.add(dist)
            self.wait()
        example_mobs = [
            (
                TexMobject(tup[0]).shift(arg0.get_center()),
                TexMobject(tup[1]).shift(arg1.get_center()),
                TexMobject(tup[2]).shift(result.get_center())
            )
            for tup in examples
        ]

        self.add(dist, r_paren, comma, l_paren, equals)
        previous = None
        kwargs = {"run_time" : 0.5}
        for mobs in example_mobs:
            if previous:
                self.play(*[
                    DelayByOrder(Transform(prev, mob, **kwargs))
                    for prev, mob in zip(previous, mobs)[:-1]
                ])
                self.play(DelayByOrder(Transform(
                    previous[-1], mobs[-1], **kwargs
                )))
                self.remove(*previous)
            self.add(*mobs)
            previous = mobs
            self.wait()

class ShiftInvarianceNumberLine(Scene):
    def construct(self):
        number_line = NumberLine().add_numbers()
        topbrace = Underbrace(ORIGIN, 2*RIGHT).rotate(np.pi, RIGHT)
        dist0 = TextMobject(["dist(", "$0$", ",", "$2$",")"])
        dist1 = TextMobject(["dist(", "$2$", ",", "$4$",")"])
        for dist in dist0, dist1:
            dist.shift(topbrace.get_center()+0.3*UP)
        dist1.shift(2*RIGHT)
        footnote = TextMobject("""
            \\begin{flushleft}
            *yeah yeah, I know I'm still drawing them on a line,
            but until a few minutes from now I have no other way
            to draw them
            \\end{flushright}
        """).scale(0.5).to_corner(DOWN+RIGHT)

        self.add(number_line, topbrace, dist0, footnote)
        self.wait()
        self.remove(dist0)
        self.play(
            ApplyMethod(topbrace.shift, 2*RIGHT),
            *[
                Transform(*pair)
                for pair in zip(dist0.split(), dist1.split())
            ]
        )
        self.wait()

class NameShiftInvarianceProperty(Scene):
    def construct(self):
        prop = TextMobject([
            "dist($A$, $B$) = dist(",
            "$A+x$, $B+x$",
            ") \\quad for all $x$"
        ])
        mid_part = prop.split()[1]
        u_brace = Underbrace(
            mid_part.get_boundary_point(DOWN+LEFT),
            mid_part.get_boundary_point(DOWN+RIGHT)
        ).shift(0.3*DOWN)
        label = TextMobject("Shifted values")
        label.shift(u_brace.get_center()+0.5*DOWN)
        name = TextMobject("``Shift Invariance''")
        name.set_color("green").to_edge(UP)
        for mob in u_brace, label:
            mob.set_color("yellow")

        self.add(prop)
        self.play(ShimmerIn(label), ShimmerIn(u_brace))
        self.wait()
        self.play(ShimmerIn(name))
        self.wait()


class TriangleInequality(Scene):
    def construct(self):
        symbols = ["A", "B", "C"]
        locations = [2*(DOWN+LEFT), UP, 4*RIGHT]
        ab, plus, bc, greater_than, ac = TextMobject([
            "dist($A$, $B$)",
            "$+$",
            "dist($B$, $C$)",
            "$>$",
            "dist($A$, $C$)",
        ]).to_edge(UP).split()
        all_dists = [ab, ac, bc]
        ab_line, ac_line, bc_line = all_lines = [
            Line(*pair).scale_in_place(0.8)
            for pair in it.combinations(locations, 2)
        ]
        def put_on_line(mob, line):
            result = deepcopy(mob).center().scale(0.5)
            result.rotate(np.arctan(line.get_slope()))
            result.shift(line.get_center()+0.2*UP)
            return result
        ab_copy, ac_copy, bc_copy = all_copies = [
            put_on_line(dist, line)
            for dist, line in zip(all_dists, all_lines)
        ]
        for symbol, loc in zip(symbols, locations):
            self.add(TexMobject(symbol).shift(loc))
        self.play(ShowCreation(ac_line), FadeIn(ac_copy))
        self.wait()
        self.play(*[
            ShowCreation(line) for line in (ab_line, bc_line)
        ]+[
            FadeIn(dist) for dist in (ab_copy, bc_copy)
        ])
        self.wait()
        self.play(*[
            Transform(*pair)
            for pair in zip(all_copies, all_dists)
        ]+[
            FadeIn(mob)
            for mob in (plus, greater_than)
        ])
        self.wait()

        

class StruggleToFindFrameOfMind(Scene):
    def construct(self):
        you, bubble = draw_you(with_bubble = True)
        questions = TextMobject("???", size = "\\Huge").scale(1.5)
        contents = [
            TexMobject("2, 4, 8, 16, 32, \\dots \\rightarrow 0"),
            TextMobject("dist(0, 2) $<$ dist(0, 64)"),
            NumberLine().sort_points(lambda p : -p[1]).add(
                TextMobject("Not on a line?").shift(UP)
            ),
        ]
        kwargs = {"run_time" : 0.5}
        self.add(you, bubble)
        bubble.add_content(questions)
        for mob in contents:
            curr = bubble.content
            self.remove(curr)
            bubble.add_content(mob)
            for first, second in [(curr, questions), (questions, mob)]:
                copy = deepcopy(first)
                self.play(DelayByOrder(Transform(
                    copy, second, **kwargs
                )))
                self.remove(copy)
            self.add(mob)
            self.wait()


class RoomsAndSubrooms(Scene):
    def construct(self):
        colors = get_room_colors()
        a_set = [3*RIGHT, 3*LEFT]
        b_set = [1.5*UP, 1.5*DOWN]
        c_set = [LEFT, RIGHT]
        rectangle_groups = [
            [Rectangle(7, 12).set_color(colors[0])],
            [
                Rectangle(6, 5).shift(a).set_color(colors[1])
                for a in a_set
            ],
            [
                Rectangle(2, 4).shift(a + b).set_color(colors[2])
                for a in a_set
                for b in b_set
            ],
            [
                Rectangle(1, 1).shift(a+b+c).set_color(colors[3])
                for a in a_set
                for b in b_set
                for c in c_set
            ]
        ]

        for group in rectangle_groups:
            mob = Mobject(*group)
            mob.sort_points(get_norm)
            self.play(ShowCreation(mob))

        self.wait()


class RoomsAndSubroomsWithNumbers(Scene):
    def construct(self):
        zero_local = (FRAME_X_RADIUS-0.5)*LEFT
        zero_one_width = FRAME_X_RADIUS-0.3

        zero, power_mobs = self.draw_numbers(zero_local, zero_one_width)
        self.wait()
        rectangles    = self.draw_first_rectangles(zero_one_width)
        rect_clusters = self.draw_remaining_rectangles(rectangles)
        self.adjust_power_mobs(zero, power_mobs, rect_clusters[-1])
        self.wait()        
        num_mobs = self.draw_remaining_numbers(
            zero, power_mobs, rect_clusters
        )
        self.wait()
        self.add_negative_one(num_mobs)
        self.wait()
        self.show_distances(num_mobs, rect_clusters)


    def draw_numbers(self, zero_local, zero_one_width):
        num_numbers = 5
        zero = TexMobject("0").shift(zero_local)
        self.add(zero)
        nums = []
        for n in range(num_numbers):
            num = TexMobject(str(2**n))
            num.scale(1.0/(n+1))
            num.shift(
                zero_local+\
                RIGHT*zero_one_width/(2.0**n)+\
                LEFT*0.05*n+\
                (0.4*RIGHT if n == 0 else ORIGIN) #Stupid
            )
            self.play(FadeIn(num, run_time = 0.5))
            nums.append(num)
        return zero, nums

    def draw_first_rectangles(self, zero_one_width):
        side_buff = 0.05
        upper_buff = 0.5
        colors = get_room_colors()
        rectangles = []
        for n in range(4):
            rect = Rectangle(
                FRAME_HEIGHT-(n+2)*upper_buff, 
                zero_one_width/(2**n)-0.85*(n+1)*side_buff
            )
            rect.sort_points(get_norm)
            rect.to_edge(LEFT, buff = 0.2).shift(n*side_buff*RIGHT)
            rect.set_color(colors[n])
            rectangles.append(rect)
        for rect in rectangles:
            self.play(ShowCreation(rect))
            self.wait()
        return rectangles

    def draw_remaining_rectangles(self, rectangles):
        clusters = []
        centers = [ORIGIN] + list(map(Mobject.get_center, rectangles))
        shift_vals = [
            2*(c2 - c1)[0]*RIGHT
            for c1, c2 in zip(centers[1:], centers)
        ]
        for rectangle, count in zip(rectangles, it.count(1)):
            cluster = [rectangle]
            for shift_val in shift_vals[:count]:
                cluster += [mob.shift(shift_val) for mob in deepcopy(cluster)]
            clusters.append(cluster)
            for rect in cluster[1:]:
                self.play(FadeIn(rect, run_time = 0.6**(count-1)))
        return clusters

    def adjust_power_mobs(self, zero, power_mobs, small_rects):
        new_zero = deepcopy(zero)
        self.center_in_closest_rect(new_zero, small_rects)
        new_power_mobs = deepcopy(power_mobs)        
        for mob, count in zip(new_power_mobs, it.count(1)):
            self.center_in_closest_rect(mob, small_rects)
        new_power_mobs[-1].shift(DOWN)
        dots = TexMobject("\\vdots")
        dots.scale(0.5).shift(new_zero.get_center()+0.5*DOWN)
        self.play(
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
            self.play(*[
                ApplyFunction(transform, mob)
                for mob in (zero_copy, power_mob_copy)
            ])
            last_left_mob = zero
            for n in range(power+1, 2*power):
                left_mob = num_mobs[n-power]
                shift_val = left_mob.get_center()-last_left_mob.get_center()
                self.play(*[
                    ApplyMethod(mob.shift, shift_val)
                    for mob in (zero_copy, power_mob_copy)
                ])
                num_mobs[n] = TexMobject(str(n))
                num_mobs[n].scale(1.0/(power_of_divisor(n, 2)+1))
                width_ratio = max_width / num_mobs[n].get_width()
                if width_ratio < 1: 
                    num_mobs[n].scale(width_ratio)
                num_mobs[n].shift(power_mob_copy.get_center()+DOWN)
                self.center_in_closest_rect(num_mobs[n], small_rects)
                point = Point(power_mob_copy.get_center())
                self.play(Transform(point, num_mobs[n]))
                self.remove(point)
                self.add(num_mobs[n])
                last_left_mob = left_mob
            self.remove(zero_copy, power_mob_copy)
            self.wait()
        return num_mobs

    @staticmethod
    def center_in_closest_rect(mobject, rectangles):
        center = mobject.get_center()
        diffs = [r.get_center()-center for r in rectangles]
        mobject.shift(diffs[np.argmin(list(map(get_norm, diffs)))])

    def add_negative_one(self, num_mobs):
        neg_one = TexMobject("-1").scale(0.5)
        shift_val = num_mobs[15].get_center()-neg_one.get_center()
        neg_one.shift(UP)
        self.play(ApplyMethod(neg_one.shift, shift_val))

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
            text = TextMobject(
                "Any of these pairs are considered to be a distance " +\
                dist_string +\
                " away from each other"
            ).shift(2*UP)
            self.add(text)
            self.clear_way_for_text(text, cluster)
            self.add(*cluster)          
            pairs = [a_b for a_b in it.combinations(list(range(16)), 2) if (a_b[0]-a_b[1])%(2**count) == 0 and (a_b[0]-a_b[1])%(2**(count+1)) != 0]
            for pair in sample(pairs, min(10, len(pairs))):
                for index in pair:
                    num_mobs[index].set_color("green")
                self.play(*[
                    ApplyMethod(
                        num_mobs[index].rotate_in_place, np.pi/10, 
                        rate_func = wiggle
                    )
                    for index in pair
                ])
                self.wait()
                for index in pair:
                    num_mobs[index].set_color("white")

    @staticmethod
    def clear_way_for_text(text, mobjects):
        right, top, null = np.max(text.points, 0)
        left, bottom, null = np.min(text.points, 0)
        def filter_func(xxx_todo_changeme):
            (x, y, z) = xxx_todo_changeme
            return x>left and x<right and y>bottom and y<top
        for mobject in mobjects:
            mobject.filter_out(filter_func)

class DeduceWhereNegativeOneFalls(Scene):
    def construct(self):
        part0, arg0, part1, part2, arg1, part3 = TextMobject([
            "dist(-1, ", "0000", ") = ", "dist(0, ", "0000", ")"
        ]).scale(1.5).split()
        u_brace = Underbrace(
            part2.get_boundary_point(DOWN+LEFT),
            part3.get_boundary_point(DOWN+RIGHT)
        ).shift(0.3+DOWN)
        
        colors = list(get_room_colors())
        num_labels = len(colors)
        texts = [
            Mobject(parts[0], parts[1].set_color(color))
            for count, color in zip(it.count(), colors)
            for parts in [TextMobject([
                "Represented (heuristically) \\\\ by being in the same \\\\", 
                (count*"sub-")+"room"
            ]).split()]
        ]
        target_text_top = u_brace.get_center()+0.5*DOWN
        for text in texts:
            text.shift(target_text_top - text.get_top())

        self.add(part0, part1, part2, part3, u_brace)
        last_args = [arg0, arg1]
        for n in range(1, 15):
            rest_time = 0.3 + 1.0/(n+1)
            new_args = [
                TextMobject("$%d$"%k).scale(1.5)
                for k in (2**n-1, 2**n)
            ]
            for new_arg, old_arg in zip(new_args, last_args):
                new_arg.shift(old_arg.get_center())
            if last_args != [arg0, arg1]:
                self.play(*[
                    DelayByOrder(Transform(*pair, run_time = 0.5*rest_time))
                    for pair in zip(last_args, new_args)
                ])
            if n-1 < num_labels:
                self.add(texts[n-1])
                if n > 1:
                    self.remove(texts[n-2])
            else:
                self.remove(u_brace, *texts)
            self.remove(*last_args)
            self.add(*new_args)
            self.wait(rest_time)
            last_args = new_args


class OtherRationalNumbers(Scene):
    def construct(self):
        import random
        self.add(TextMobject("Where do other \\\\ rational numbers fall?"))
        pairs = [
            (1, 2),
            (1, 3),
            (4, 9),
            (-7, 13),
            (3, 1001),
        ]
        locii = [
            4*LEFT+2*UP,
            4*RIGHT,
            5*RIGHT+UP,
            4*LEFT+2*DOWN,
            3*DOWN,
        ]
        for pair, locus in zip(pairs, locii):
            fraction = TexMobject("\\frac{%d}{%d}"%pair).shift(locus)
            self.play(ShimmerIn(fraction))
        self.wait()

class PAdicMetric(Scene):
    def construct(self):
        p_str, text = TextMobject(["$p$", "-adic metric"]).shift(2*UP).split()
        primes = [TexMobject(str(p)) for p in [2, 3, 5, 7, 11, 13, 17, 19, 23]]
        p_str.set_color("yellow")
        colors = Color("green").range_to("skyblue", len(primes))
        new_numbers = TextMobject("Completely new types of numbers!")
        new_numbers.set_color("skyblue").shift(2.3*DOWN)
        arrow = Arrow(2*DOWN, tail = 1.7*UP)

        curr = deepcopy(p_str)
        self.add(curr, text)
        self.wait()        
        for prime, count in zip(primes, it.count()):
            prime.scale(1.0).set_color(next(colors))
            prime.shift(center_of_mass([p_str.get_top(), p_str.get_center()]))
            self.play(DelayByOrder(Transform(curr, prime)))
            self.wait()
            if count == 2:
                self.spill(Mobject(curr, text), arrow, new_numbers)
            self.remove(curr)
            curr = prime
        self.play(DelayByOrder(Transform(curr, p_str)))
        self.wait()

    def spill(self, start, arrow, end):
        start.sort_points(lambda p : p[1])
        self.play(
            ShowCreation(
                arrow,
                rate_func = squish_rate_func(smooth, 0.5, 1.0)
            ),
            DelayByOrder(Transform(
                start,
                Point(arrow.points[0]).set_color("white")
            ))
        )
        self.play(ShimmerIn(end))


class FuzzyDiscoveryToNewMath(Scene):
    def construct(self):
        fuzzy = TextMobject("Fuzzy Discovery")
        fuzzy.to_edge(UP).shift(FRAME_X_RADIUS*LEFT/2)
        new_math = TextMobject("New Math")
        new_math.to_edge(UP).shift(FRAME_X_RADIUS*RIGHT/2)
        lines = Mobject(
            Line(DOWN*FRAME_Y_RADIUS, UP*FRAME_Y_RADIUS),
            Line(3*UP+LEFT*FRAME_X_RADIUS, 3*UP+RIGHT*FRAME_X_RADIUS)
        )
        fuzzy_discoveries = [
            TexMobject("a^2 + b^2 = c^2"),
            TexMobject("".join(CONVERGENT_SUM_TEXT)),            
            TexMobject("".join(DIVERGENT_SUM_TEXT)),
            TexMobject("e^{\pi i} = -1"),
        ]
        triangle_lines = [
            Line(ORIGIN, LEFT),
            Line(LEFT, UP),
            Line(UP, ORIGIN),
        ]
        for line, char in zip(triangle_lines, ["a", "c", "b"]):
            line.set_color("blue")
            char_mob = TexMobject(char).scale(0.25)
            line.add(char_mob.shift(line.get_center()))
        triangle = Mobject(*triangle_lines)
        triangle.center().shift(1.5*fuzzy_discoveries[0].get_right())
        how_length = TextMobject("But how is length defined?").scale(0.5)
        how_length.shift(0.75*DOWN)
        fuzzy_discoveries[0].add(triangle, how_length)
        new_maths = [
            TextMobject("""
                Define distance between points $(x_0, y_0)$ and
                $(x_1, y_1)$ as $\\sqrt{(x_1-x_0)^2 + (y_1-y_0)^2}$
            """),
            TextMobject("Define ``approach'' and infinite sums"),
            TextMobject("Discover $2$-adic numbers"),
            TextMobject(
                "Realize exponentiation is doing something much \
                different from repeated multiplication"
            )
        ]
        midpoints = []
        triplets = list(zip(fuzzy_discoveries, new_maths, it.count(2, -1.75)))
        for disc, math, count in triplets:
            math.scale(0.65)
            for mob in disc, math:
                mob.to_edge(LEFT).shift(count*UP)
            math.shift(FRAME_X_RADIUS*RIGHT)
            midpoints.append(count*UP)

        self.add(fuzzy, lines)
        self.play(*list(map(ShimmerIn, fuzzy_discoveries)))
        self.wait()
        self.play(DelayByOrder(Transform(
            deepcopy(fuzzy), new_math
        )))
        self.play(*[
            DelayByOrder(Transform(deepcopy(disc), math))
            for disc, math in zip(fuzzy_discoveries, new_maths)
        ])
        self.wait()


class DiscoveryAndInvention(Scene):
    def construct(self):
        invention, vs, discovery = TextMobject([
            "Invention ", "vs. ", "Discovery"
        ]).split()
        nrd = TextMobject(
            "Non-rigorous truths"
        ).shift(2*UP)
        rt = TextMobject(
            "Rigorous terms"
        ).shift(2*DOWN)
        
        arrows = []
        self.add(discovery, vs, invention)
        self.wait()
        arrow = Arrow(
            nrd.get_bottom(),
            tail = discovery.get_top()
        )
        self.play(
            FadeIn(nrd),
            ShowCreation(arrow)
        )
        arrows.append(arrow)
        self.wait()
        arrow = Arrow(
            invention.get_top(),
            tail = nrd.get_bottom()
        )
        self.play(ShowCreation(arrow))
        arrows.append(arrow)
        self.wait()
        arrow = Arrow(
            rt.get_top(),
            tail = invention.get_bottom()
        )
        self.play(
            FadeIn(rt),
            ShowCreation(arrow)
        )
        arrows.append(arrow)
        self.wait()
        arrow = Arrow(
            discovery.get_bottom(),
            tail = rt.get_top()
        )
        self.play(ShowCreation(arrow))
        self.wait()
        arrows.append(arrow)
        for color in Color("yellow").range_to("red", 4):
            for arrow in arrows:
                self.play(
                    ShowCreation(deepcopy(arrow).set_color(color)),
                    run_time = 0.25
                )




if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)

