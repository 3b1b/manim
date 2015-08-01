#!/usr/bin/env python

import numpy as np
import itertools as it
from copy import deepcopy
import sys


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
    "+8", "+\\cdots",
    "+2^n",
    "+\\cdots", 
    "= -1",
]

CONVERGENT_SUM_TEXT = [
    "\\frac{1}{2}",
    "+\\frac{1}{4}",
    "+\\frac{1}{8}",
    "+\\frac{1}{16}",
    "+\\cdots+",
    "\\frac{1}{2^n}",
    "+\\cdots",
    "=1",
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
        interval = zero_to_one_interval()
        dots = [
            Dot(radius = 3*Dot.DEFAULT_RADIUS).shift(INTERVAL_RADIUS*x+UP)
            for x in LEFT, RIGHT
        ]
        color_range = Color("green").range_to("grey", NUM_WRITTEN_TERMS)
        conv_sum = convergent_sum().split()

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
            num = conv_sum[count]
            num.shift(RIGHT*(line.get_center()[0]-num.get_center()[0]))
            if num.get_width() > line.get_length():
                num.stretch_to_fit_width(line.get_length())
            num.shift(3*DOWN)
            self.animate(
                ApplyMethod(line.shift, 2*DOWN),
                FadeIn(num)
            )
            self.dither()
        self.animate(FadeIn(conv_sum[NUM_WRITTEN_TERMS]))







if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)

