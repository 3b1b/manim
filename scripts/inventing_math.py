#!/usr/bin/env python

import numpy as np
import itertools as it
from copy import deepcopy
import sys
import operator as op


from animation import *
from mobject import *
from constants import *
from region import *
from scene import Scene
from script_wrapper import command_line_create_scene

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

def underbrace():
    return tex_mobject("\\underbrace{%s}"%(8*"\\quad"))

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

def draw_you():
    result = PiCreature()
    result.give_straight_face().highlight("grey")
    result.to_corner(LEFT+DOWN)
    result.rewire_part_attributes()
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
        brace = underbrace().shift(0.75*DOWN)
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
            end = 40,
            start_center = brace.get_center() + 0.5*DOWN,
            end_center = end_brace.get_center() + 0.5*DOWN,
            **kwargs
        )
        self.add(ellipses)
        self.animate(
            Transform(brace, end_brace, **kwargs),
            flip_through,
        )
        kwargs = {"run_time" : 0.5, "alpha_func" : rush_from}
        self.clear()
        self.add(CompoundMobject(*equation[:-1]))
        self.animate(
            Transform(
                flip_through.mobject,
                equation[-1],
                **kwargs
            ),
            FadeOut(brace, **kwargs),
        )
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

class ReasonsForMakingVideo(Scene):
    def construct(self):
        text = text_mobject([
            """
            \\begin{itemize}
            \\item Understand what ``$
            """,
            "".join(DIVERGENT_SUM_TEXT),
            """
            $'' is saying.
            """,
            """
            \\item Nonsense-Driven Construction
            \\end{itemize}
            """
        ], size = "\\Small")
        text.scale(1.5).to_edge(LEFT).shift(UP).highlight("white")
        text.highlight("green", lambda (x, y, z) : x < -SPACE_WIDTH + 1)
        line_one_first, equation, line_one_last, line_two = text.split()
        line_two.shift(2*DOWN)
        div_sum = divergent_sum().scale(0.5).shift(3*UP)

        self.add(div_sum)
        self.animate(
            ApplyMethod(div_sum.replace, equation),
            FadeIn(line_one_first),
            FadeIn(line_one_last)
        )
        self.dither()
        self.add(line_two)
        self.dither()

class DiscoverAndDefine(Scene):
    def construct(self):
        sum_mob = tex_mobject("\\sum_{n = 1}^\\infty a_n")
        discover = text_mobject("What does it feel like to discover these?")
        define = text_mobject([
            "What does it feel like to", 
            "\\emph{define} ",
            "them?"
        ])
        sum_mob.shift(2*UP)
        define.shift(2*DOWN)
        define_parts = define.split()
        define_parts[1].highlight("skyblue")

        self.add(sum_mob)
        self.animate(FadeIn(discover))
        self.dither()
        self.animate(FadeIn(CompoundMobject(*define_parts)))
        self.dither()

class YouAsMathematician(Scene):
    def construct(self):
        you = draw_you()
        explanation = text_mobject(
            "You as a (questionably accurate portrayal of a) mathematician.",
            size = "\\small"
        ).shift([2, you.get_center()[1], 0])
        arrow = Arrow(you.get_center(), direction = LEFT)
        arrow.nudge(you.get_width())
        for mob in arrow, explanation:
            mob.highlight("yellow")
        bubble = ThoughtBubble()
        bubble.stretch_to_fit_width(10)
        bubble.pin_to(you)
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
            ApplyFunction(
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
    def construct(self):
        num_height = 1.3*DOWN
        interval = zero_to_one_interval()
        dots = [
            Dot(radius = 3*Dot.DEFAULT_RADIUS).shift(INTERVAL_RADIUS*x+UP)
            for x in LEFT, RIGHT
        ]
        color_range = Color("green").range_to("yellow", NUM_WRITTEN_TERMS)
        conv_sum = convergent_sum().split()
        partial_sums = tex_mobject(PARTIAL_CONVERGENT_SUMS_TEXT, size = "\\small")
        partial_sums.scale(1.5).to_edge(UP)
        partial_sum_parts = partial_sums.split()

        self.add(interval)
        self.animate(*[
            ApplyMethod(dot.shift, DOWN)
            for dot in dots
        ])
        self.dither()
        for count in range(NUM_WRITTEN_TERMS):
            shift_val = RIGHT*INTERVAL_RADIUS/(2.0**count)
            start = dots[0].get_center()
            line = Line(start, start + shift_val*RIGHT)
            line.highlight(color_range.next())
            self.animate(
                ApplyMethod(dots[0].shift, shift_val),
                ShowCreation(line)
            )
            num = conv_sum[count].scale(0.75)
            num.shift(RIGHT*(line.get_center()[0]-num.get_center()[0]))
            if num.get_width() > line.get_length():
                num.stretch_to_fit_width(line.get_length())
            num.shift(num_height)
            self.animate(
                ApplyMethod(line.shift, 2*DOWN),
                FadeIn(num)
            )
            self.dither()
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
            SemiCircleTransform(*pair, counterclockwise=False)
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
        gen_cross = ImageMobject("cross").highlight("red")
        new_cross = deepcopy(gen_cross)
        for cross, mob in [(gen_cross, generating), (new_cross, new)]:
            cross.replace(mob, stretch = True)
        disecting = text_mobject("Disecting")
        disecting.shift(generating.get_center() + 0.7*UP)
        old = text_mobject("old")
        old.shift(new.get_center()+0.7*DOWN)

        kwargs = {"run_time" : 0.25}
        self.add(*words)
        self.dither()
        self.animate(ShowCreation(gen_cross, **kwargs))
        self.animate(ShowCreation(new_cross, **kwargs))
        self.dither()        
        self.add(disecting)
        self.dither(0.25)
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
        vert_line0 = Line(0.5*UP, UP)
        vert_line1 = Line(0.5*UP+num*RIGHT, UP+num*RIGHT)
        horiz_line = Line(UP, UP+num*RIGHT)
        lines = [vert_line0, vert_line1, horiz_line]
        for line in lines:
            line.highlight("green")

        self.add(number_line, *lines)
        self.dither()
        self.animate(
            ApplyMethod(vert_line0.shift, RIGHT),
            Transform(
                horiz_line, 
                Line(vert_line0.end+RIGHT, vert_line1.end).highlight("green")
            ),
            run_time = 2.5
        )
        self.dither()

























if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)

