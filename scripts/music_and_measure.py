#!/usr/bin/env python

import numpy as np
import itertools as it
from copy import deepcopy
import sys
from fractions import Fraction, gcd

from animation import *
from mobject import *
from constants import *
from region import *
from scene import Scene
from script_wrapper import command_line_create_scene

import random

MOVIE_PREFIX = "music_and_measure/"

INTERVAL_RADIUS = 6
NUM_INTERVAL_TICKS = 16
TICK_STRETCH_FACTOR = 4
INTERVAL_COLOR_PALETTE = [
    "yellow",
    "green",
    "skyblue",
    "#AD1457",
    "#6A1B9A",
    "#26C6DA",
    "#FF8F00",
]

def rationals():
    curr = Fraction(1, 2)
    numerator, denominator = 1, 2
    while True:
        yield curr
        if curr.numerator < curr.denominator - 1:
            new_numerator = curr.numerator + 1
            while gcd(new_numerator, curr.denominator) != 1:
                new_numerator += 1
            curr = Fraction(new_numerator, curr.denominator)
        else:
            curr = Fraction(1, curr.denominator + 1)

def fraction_mobject(fraction):
    n, d = fraction.numerator, fraction.denominator
    return tex_mobject("\\frac{%d}{%d}"%(n, d))


def zero_to_one_interval():
    interval = NumberLine(
        radius = INTERVAL_RADIUS,
        interval_size = 2.0*INTERVAL_RADIUS/NUM_INTERVAL_TICKS
    )
    interval.elongate_tick_at(-INTERVAL_RADIUS, TICK_STRETCH_FACTOR)
    interval.elongate_tick_at(INTERVAL_RADIUS, TICK_STRETCH_FACTOR)
    interval.add(tex_mobject("0").shift(INTERVAL_RADIUS*LEFT+DOWN))
    interval.add(tex_mobject("1").shift(INTERVAL_RADIUS*RIGHT+DOWN))
    return interval

class OpenInterval(Mobject):
    def __init__(self, center = ORIGIN, width = 2, **kwargs):
        Mobject.__init__(self, **kwargs)
        self.add(tex_mobject("(").shift(LEFT))
        self.add(tex_mobject(")").shift(RIGHT))
        scale_factor = width / 2.0
        self.stretch(scale_factor, 0)
        self.stretch(0.5+0.5*scale_factor, 1)
        self.shift(center)

class VibratingString(Animation):
    def __init__(self, 
                 num_periods = 1,
                 overtones = 4,
                 amplitude = 0.5,
                 radius = INTERVAL_RADIUS, 
                 center = ORIGIN,
                 color = "white",
                 run_time = 3.0, 
                 alpha_func = None,
                 **kwargs):
        self.radius = radius
        self.center = center
        def func(x, t):
            return sum([
                (amplitude/((k+1)**2))*np.sin(2*mult*t)*np.sin(k*mult*x)
                for k in range(overtones)
                for mult in [(num_periods+k)*np.pi]
            ])
        self.func = func
        kwargs["run_time"] = run_time
        kwargs["alpha_func"] = alpha_func
        Animation.__init__(self, Mobject1D(color = color), **kwargs)

    def update_mobject(self, alpha):
        self.mobject.init_points()
        self.mobject.add_points([
            [x*self.radius, self.func(x, alpha*self.run_time), 0]
            for x in np.arange(-1, 1, self.mobject.epsilon/self.radius)
        ])
        self.mobject.shift(self.center)


class IntervalScene(Scene):
    def construct(self):
        self.interval = zero_to_one_interval()
        self.add(self.interval)

    def show_all_fractions(self, 
                           num_fractions = 27, 
                           pause_time = 1.0,
                           remove_as_you_go = True):
        shrink = not remove_as_you_go
        for fraction, count in zip(rationals(), range(num_fractions)):
            frac_mob, tick  = self.add_fraction(fraction, shrink)
            self.dither(pause_time)
            if remove_as_you_go:
                self.remove(frac_mob, tick)

    def add_fraction(self, fraction, shrink = False):
        point = self.num_to_point(fraction)
        tick_rad = self.interval.tick_size*TICK_STRETCH_FACTOR        
        frac_mob = fraction_mobject(fraction)
        if shrink:
            scale_factor = 2.0/fraction.denominator
            frac_mob.scale(scale_factor)
            tick_rad *= scale_factor
        frac_mob.shift(point + frac_mob.get_height()*UP)
        tick = Line(point + DOWN*tick_rad, point + UP*tick_rad)
        tick.highlight("yellow")
        self.add(frac_mob, tick)
        return frac_mob, tick

    def cover_fractions(self, 
                        epsilon = 0.3, 
                        num_fractions = 9, 
                        run_time_per_interval = 0.5):
        for fraction, count in zip(rationals(), range(num_fractions)):
            self.add_open_interval(
                fraction,
                epsilon / 2**(count+1),
                run_time = run_time_per_interval
            )

    def add_open_interval(self, num, width, color = None, run_time = 0):
        width *= 2*self.interval.radius
        center_point = self.num_to_point(num)
        open_interval = OpenInterval(center_point, width)
        if color:
            open_interval.highlight(color)
        interval_line = Line(open_interval.get_left(), open_interval.get_right())
        interval_line.scale_in_place(0.9)#Silliness
        interval_line.do_in_place(interval_line.sort_points, np.linalg.norm)
        interval_line.highlight("yellow")
        if run_time > 0:
            squished_interval = deepcopy(open_interval).stretch_to_fit_width(0)
            self.animate(
                Transform(squished_interval, open_interval),
                ShowCreation(interval_line),
                run_time = run_time
            )
            self.remove(squished_interval)
        self.add(open_interval, interval_line)
        return open_interval, interval_line

    def num_to_point(self, num):
        assert(num <= 1 and num >= 0)
        radius = self.interval.radius
        return (num*2*radius - radius)*RIGHT


class TwoChallenges(Scene):
    def construct(self):
        two_challenges = text_mobject("Two Challenges", size = "\\Huge").to_edge(UP)
        one, two = map(text_mobject, ["1.", "2."])
        one.shift(UP).to_edge(LEFT)
        two.shift(DOWN).to_edge(LEFT)
        notes = ImageMobject("musical_notes").scale(0.3)
        notes.next_to(one)
        notes.highlight("blue")
        measure = text_mobject("Measure Theory").next_to(two)
        probability = text_mobject("Probability")
        probability.next_to(measure).shift(DOWN+RIGHT)
        integration = tex_mobject("\\int")
        integration.next_to(measure).shift(UP+RIGHT)
        arrow_to_prob = Arrow(measure, probability)
        arrow_to_int = Arrow(measure, integration)
        for arrow in arrow_to_prob, arrow_to_int:
            arrow.highlight("yellow")


        self.add(two_challenges)
        self.dither()
        self.add(one, notes)
        self.dither()
        self.add(two, measure)
        self.dither()
        self.animate(ShowCreation(arrow_to_int))
        self.add(integration)
        self.dither()
        self.animate(ShowCreation(arrow_to_prob))
        self.add(probability)
        self.dither()

class MeasureTheoryToHarmony(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        self.cover_fractions()
        self.dither()
        all_mobs = CompoundMobject(*self.mobjects)
        all_mobs.sort_points()
        self.clear()
        radius = self.interval.radius
        line = Line(radius*LEFT, radius*RIGHT).highlight("white")
        self.animate(DelayByOrder(Transform(all_mobs, line)))
        self.clear()
        self.animate(VibratingString(alpha_func = smooth))
        self.clear()
        self.add(line)
        self.dither()


class ChallengeOne(Scene):
    def construct(self):
        title = text_mobject("Challenge #1").to_edge(UP)
        bottom_vibration = VibratingString(
            num_periods = 1, run_time = 1.0, 
            center = DOWN, color = "blue"
        )
        top_vibration = VibratingString(
            num_periods = 2, run_time = 1.0,
            center = 2*UP, color = "lightgreen"
        )
        freq_num1 = text_mobject("220 Hz")
        freq_num2 = text_mobject("$r\\times$220 Hz")
        freq_num1.shift(1.5*DOWN)
        freq_num2.shift(1.5*UP)
        r_constraint = tex_mobject("1<r<2")
        # self.add(title, freq_num1, freq_num2, r_constraint)
        self.animate(top_vibration, bottom_vibration)



class SampleIntervalScene(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        self.cover_fractions()
        self.dither()


class ShowAllFractions(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        self.show_all_fractions(remove_as_you_go = False, pause_time = 0.3)


if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)


