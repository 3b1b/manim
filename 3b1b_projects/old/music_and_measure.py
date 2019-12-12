#!/usr/bin/env python


import numpy as np
import itertools as it
from copy import deepcopy
import sys
from fractions import Fraction, gcd

from manimlib.imports import *
from .inventing_math import Underbrace

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
    return TexMobject("\\frac{%d}{%d}"%(n, d))

def continued_fraction(int_list):
    if len(int_list) == 1:
        return int_list[0]
    return int_list[0] + Fraction(1, continued_fraction(int_list[1:]))

def zero_to_one_interval():
    interval = NumberLine(
        radius = INTERVAL_RADIUS,
        interval_size = 2.0*INTERVAL_RADIUS/NUM_INTERVAL_TICKS
    )
    interval.elongate_tick_at(-INTERVAL_RADIUS, TICK_STRETCH_FACTOR)
    interval.elongate_tick_at(INTERVAL_RADIUS, TICK_STRETCH_FACTOR)
    interval.add(TexMobject("0").shift(INTERVAL_RADIUS*LEFT+DOWN))
    interval.add(TexMobject("1").shift(INTERVAL_RADIUS*RIGHT+DOWN))
    return interval

class LeftParen(Mobject):
    def generate_points(self):
        self.add(TexMobject("("))
        self.center()    

    def get_center(self):
        return Mobject.get_center(self) + 0.04*LEFT

class RightParen(Mobject):
    def generate_points(self):
        self.add(TexMobject(")"))
        self.center()

    def get_center(self):
        return Mobject.get_center(self) + 0.04*RIGHT


class OpenInterval(Mobject):
    def __init__(self, center_point = ORIGIN, width = 2, **kwargs):
        digest_config(self, kwargs, locals())
        left = LeftParen().shift(LEFT*width/2)
        right = RightParen().shift(RIGHT*width/2)
        Mobject.__init__(self, left, right, **kwargs)
         # scale_factor = width / 2.0
        # self.stretch(scale_factor, 0)
        # self.stretch(0.5+0.5*scale_factor, 1)
        self.shift(center_point)

class Piano(ImageMobject):
    CONFIG = {
        "stroke_width" : 1,
        "invert" : False, 
        "scale_factorue" : 0.5
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        ImageMobject.__init__(self, "piano_keyboard")
        jump = self.get_width()/24        
        self.center()
        self.half_note_jump = self.get_width()/24
        self.ivory_jump = self.get_width()/14

    def split(self):
        left = self.get_left()[0]
        keys = []
        for count in range(14):
            key = Mobject(
                color = "white",
                stroke_width = 1
            )
            x0 = left + count*self.ivory_jump
            x1 = x0 + self.ivory_jump
            key.add_points(
                self.points[
                    (self.points[:,0] > x0)*(self.points[:,0] < x1)
                ]
            )
            keys.append(key)
        return keys


class Vibrate(Animation):
    CONFIG = {
        "num_periods" : 1,
        "overtones" : 4,
        "amplitude" : 0.5,
        "radius" : INTERVAL_RADIUS,
        "center" : ORIGIN,
        "color" : "white",
        "run_time" : 3.0,
        "rate_func" : None
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        def func(x, t):
            return sum([
                (self.amplitude/((k+1)**2.5))*np.sin(2*mult*t)*np.sin(k*mult*x)
                for k in range(self.overtones)
                for mult in [(self.num_periods+k)*np.pi]
            ])
        self.func = func
        Animation.__init__(self, Mobject1D(color = self.color), **kwargs)

    def interpolate_mobject(self, alpha):
        self.mobject.reset_points()
        epsilon = self.mobject.epsilon
        self.mobject.add_points([
            [x*self.radius, self.func(x, alpha*self.run_time)+y, 0]
            for x in np.arange(-1, 1, epsilon/self.radius)
            for y in epsilon*np.arange(3)
        ])
        self.mobject.shift(self.center)


class IntervalScene(NumberLineScene):
    def construct(self):
        self.number_line = UnitInterval()
        self.displayed_numbers = [0, 1]
        self.number_mobs = self.number_line.get_number_mobjects(*self.displayed_numbers)
        self.add(self.number_line, *self.number_mobs)

    def show_all_fractions(self, 
                           num_fractions = 27, 
                           pause_time = 1.0,
                           remove_as_you_go = True):
        shrink = not remove_as_you_go
        for fraction, count in zip(rationals(), list(range(num_fractions))):
            frac_mob, tick  = self.add_fraction(fraction, shrink)
            self.wait(pause_time)
            if remove_as_you_go:
                self.remove(frac_mob, tick)

    def add_fraction(self, fraction, shrink = False):
        point = self.number_line.number_to_point(fraction)
        tick_rad = self.number_line.tick_size*TICK_STRETCH_FACTOR        
        frac_mob = fraction_mobject(fraction)
        if shrink:
            scale_factor = 2.0/fraction.denominator
            frac_mob.scale(scale_factor)
            tick_rad *= scale_factor
        frac_mob.shift(point + frac_mob.get_height()*UP)
        tick = Line(point + DOWN*tick_rad, point + UP*tick_rad)
        tick.set_color("yellow")
        self.add(frac_mob, tick)
        return frac_mob, tick

    def add_fraction_ticks(self, num_fractions = 1000, run_time = 0):
        long_tick_size = self.number_line.tick_size*TICK_STRETCH_FACTOR
        all_ticks = []
        for frac, count in zip(rationals(), list(range(num_fractions))):
            point = self.number_line.number_to_point(frac)
            tick_rad = 2.0*long_tick_size/frac.denominator
            tick = Line(point+tick_rad*DOWN, point+tick_rad*UP)
            tick.set_color("yellow")
            all_ticks.append(tick)
        all_ticks = Mobject(*all_ticks)
        if run_time > 0:
            self.play(ShowCreation(all_ticks))
        else:
            self.add(all_ticks)
        return all_ticks


    def cover_fractions(self, 
                        epsilon = 0.3, 
                        num_fractions = 10,
                        run_time_per_interval = 0.5):
        intervals = []
        lines = []
        num_intervals = 0
        all_rationals = rationals()
        count = 0
        while True:
            fraction = next(all_rationals)
            count += 1
            if num_intervals >= num_fractions:
                break
            if fraction < self.number_line.left_num or fraction > self.number_line.right_num:
                continue
            num_intervals += 1
            interval, line = self.add_open_interval(
                fraction,
                epsilon / min(2**count, 2**30),
                run_time = run_time_per_interval
            )
            intervals.append(interval)
            lines.append(line)
        return intervals, lines

    def add_open_interval(self, num, width, color = None, run_time = 0):
        spatial_width = width*self.number_line.unit_length_to_spatial_width
        center_point = self.number_line.number_to_point(num)
        open_interval = OpenInterval(center_point, spatial_width)
        color = color or "yellow"
        interval_line = Line(
            center_point+spatial_width*LEFT/2,
            center_point+spatial_width*RIGHT/2
        )
        interval_line.do_in_place(interval_line.sort_points, get_norm)
        interval_line.set_color(color)
        if run_time > 0:
            squished_interval = deepcopy(open_interval).stretch_to_fit_width(0)
            self.play(
                Transform(squished_interval, open_interval),
                ShowCreation(interval_line),
                run_time = run_time
            )
            self.remove(squished_interval)
        self.add(open_interval, interval_line)
        return open_interval, interval_line


class TwoChallenges(Scene):
    def construct(self):
        two_challenges = TextMobject("Two Challenges", size = "\\Huge").to_edge(UP)
        one, two = list(map(TextMobject, ["1.", "2."]))
        one.shift(UP).to_edge(LEFT)
        two.shift(DOWN).to_edge(LEFT)
        notes = ImageMobject("musical_notes").scale(0.3)
        notes.next_to(one)
        notes.set_color("blue")
        measure = TextMobject("Measure Theory").next_to(two)
        probability = TextMobject("Probability")
        probability.next_to(measure).shift(DOWN+RIGHT)
        integration = TexMobject("\\int")
        integration.next_to(measure).shift(UP+RIGHT)
        arrow_to_prob = Arrow(measure, probability)
        arrow_to_int = Arrow(measure, integration)
        for arrow in arrow_to_prob, arrow_to_int:
            arrow.set_color("yellow")


        self.add(two_challenges)
        self.wait()
        self.add(one, notes)
        self.wait()
        self.add(two, measure)
        self.wait()
        self.play(ShowCreation(arrow_to_int))
        self.add(integration)
        self.wait()
        self.play(ShowCreation(arrow_to_prob))
        self.add(probability)
        self.wait()

class MeasureTheoryToHarmony(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        self.cover_fractions()
        self.wait()
        all_mobs = Mobject(*self.mobjects)
        all_mobs.sort_points()
        self.clear()
        radius = self.interval.radius
        line = Line(radius*LEFT, radius*RIGHT).set_color("white")
        self.play(DelayByOrder(Transform(all_mobs, line)))
        self.clear()
        self.play(Vibrate(rate_func = smooth))
        self.clear()
        self.add(line)
        self.wait()


class ChallengeOne(Scene):
    def construct(self):
        title = TextMobject("Challenge #1").to_edge(UP)
        start_color = Color("blue")
        colors = start_color.range_to("white", 6)
        self.bottom_vibration = Vibrate(
            num_periods = 1, run_time = 3.0, 
            center = DOWN, color = start_color
        )
        top_vibrations = [
            Vibrate(
                num_periods = freq, run_time = 3.0,
                center = 2*UP, color = next(colors)
            )
            for freq in [1, 2, 5.0/3, 4.0/3, 2]
        ]
        freq_220 = TextMobject("220 Hz")
        freq_r220 = TextMobject("$r\\times$220 Hz")
        freq_330 = TextMobject("1.5$\\times$220 Hz")
        freq_sqrt2 = TextMobject("$\\sqrt{2}\\times$220 Hz")
        freq_220.shift(1.5*DOWN)
        for freq in freq_r220, freq_330, freq_sqrt2:
            freq.shift(1.5*UP)
        r_constraint = TexMobject("(1<r<2)", size = "\\large")

        self.add(title)
        self.wait()
        self.vibrate(1)
        self.add(freq_220)
        self.vibrate(1)
        self.add(r_constraint)
        self.vibrate(1)
        self.add(freq_r220)
        self.vibrate(2, top_vibrations[1])
        self.remove(freq_r220, r_constraint)
        self.add(freq_330)
        self.vibrate(2, top_vibrations[2])
        self.remove(freq_330)
        self.add(freq_sqrt2)
        self.vibrate(1, top_vibrations[3])
        self.remove(freq_sqrt2)
        self.continuously_vary_frequency(top_vibrations[0], top_vibrations[4])

    def vibrate(self, num_repeats, *top_vibrations):
        anims = [self.bottom_vibration] + list(top_vibrations)
        for count in range(num_repeats):
            self.play(*anims)
        self.remove(*[a.mobject for a in anims])

    def continuously_vary_frequency(self, top_vib_1, top_vib_2):
        number_line = NumberLine(interval_size = 1).add_numbers()

        one, two = 2*number_line.interval_size*RIGHT, 4*number_line.interval_size*RIGHT
        arrow1 = Arrow(one+UP, one)
        arrow2 = Arrow(two+UP, two)
        r1 = TexMobject("r").next_to(arrow1, UP)
        r2 = TexMobject("r").next_to(arrow2, UP)
        kwargs = {
            "run_time" : 5.0,
            "rate_func" : there_and_back
        }
        run_time = 3.0
        vibrations = [self.bottom_vibration, top_vib_1, top_vib_2]

        self.add(number_line, r1, arrow1)
        self.play(bottom_vibration, top_vib_1)
        for vib in vibrations:
            vib.set_run_time(kwargs["run_time"])
        self.play(
            self.bottom_vibration,
            Transform(arrow1, arrow2, **kwargs),
            Transform(r1, r2, **kwargs),
            TransformAnimations(top_vib_1, top_vib_2, **kwargs)
        )
        for vib in vibrations:
            vib.set_run_time(3.0)
        self.play(bottom_vibration, top_vib_1)

class JustByAnalyzingTheNumber(Scene):
    def construct(self):
        nums = [
            1.5,
            np.sqrt(2),
            2**(5/12.),
            4/3.,
            1.2020569031595942,
        ]
        last = None
        r_equals = TexMobject("r=").shift(2*LEFT)
        self.add(r_equals)
        for num in nums:
            mob = TexMobject(str(num)).next_to(r_equals)
            mob.set_color()
            mob.sort_points()
            if last:
                self.play(DelayByOrder(Transform(last, mob, run_time = 0.5)))
                self.remove(last)
                self.add(mob)
            else:
                self.add(mob)
            self.wait()
            last = mob

class QuestionAndAnswer(Scene):
    def construct(self):
        Q = TextMobject("Q:").shift(UP).to_edge(LEFT)
        A = TextMobject("A:").shift(DOWN).to_edge(LEFT)
        string1 = Vibrate(center = 3*UP, color = "blue")
        string2 = Vibrate(num_periods = 2, center = 3.5*UP, color = "green")
        twotwenty = TexMobject("220").scale(0.25).next_to(string1.mobject, LEFT)
        r220 = TexMobject("r\\times220").scale(0.25).next_to(string2.mobject, LEFT)
        question = TextMobject(
            "For what values of $r$ will the frequencies 220~Hz and \
            $r\\times$220~Hz sound nice together?"
        ).next_to(Q)
        answer = TextMobject([
            "When $r$ is", 
            "sufficiently close to",
            "a rational number"
        ], size = "\\small").scale(1.5)
        answer.next_to(A)
        correction1 = TextMobject(
            "with sufficiently low denominator",
            size = "\\small"
        ).scale(1.5)
        correction1.set_color("yellow")
        correction1.next_to(A).shift(2*answer.get_height()*DOWN)
        answer = answer.split()
        answer[1].set_color("green")
        temp_answer_end = deepcopy(answer[-1]).next_to(answer[0], buff = 0.2)

        self.add(Q, A, question, twotwenty, r220)
        self.play(string1, string2)
        self.add(answer[0], temp_answer_end)
        self.play(string1, string2)
        self.play(ShimmerIn(correction1), string1, string2)
        self.play(string1, string2, run_time = 3.0)
        self.play(
            Transform(Point(answer[1].get_left()), answer[1]),
            Transform(temp_answer_end, answer[2]),
            string1, string2
        )
        self.play(string1, string2, run_time = 3.0)

class PlaySimpleRatio(Scene):
    args_list = [
        (Fraction(3, 2), "green"),
        (Fraction(4, 3), "purple"),
        (Fraction(8, 5), "skyblue"),
        (Fraction(211, 198), "orange"),
        (Fraction(1093, 826), "red"),
        ((np.exp(np.pi)-np.pi)/15, "#7e008e")
    ]
    @staticmethod
    def args_to_string(fraction, color):
        return str(fraction).replace("/", "_to_")

    def construct(self, fraction, color):
        string1 = Vibrate(
            num_periods = 1, run_time = 5.0, 
            center = DOWN, color = "blue"
        )
        string2 = Vibrate(
            num_periods = fraction, run_time = 5.0,
            center = 2*UP, color = color
        )
        if isinstance(fraction, Fraction):
            mob = fraction_mobject(fraction).shift(0.5*UP)
        else:
            mob = TexMobject("\\frac{e^\\pi - \\pi}{15} \\approx \\frac{4}{3}")
            mob.shift(0.5*UP)
        self.add(mob)
        self.play(string1, string2)

class LongSine(Mobject1D):
    def generate_points(self):
        self.add_points([
            (x, np.sin(2*np.pi*x), 0)
            for x in np.arange(0, 100, self.epsilon/10)
        ])

class DecomposeMusicalNote(Scene):
    def construct(self):
        line = Line(FRAME_Y_RADIUS*DOWN, FRAME_Y_RADIUS*UP)
        sine = LongSine()
        kwargs = {
            "run_time" : 4.0,
            "rate_func" : None
        }
        words = TextMobject("Imagine 220 per second...")
        words.shift(2*UP)

        self.add(line)
        self.play(ApplyMethod(sine.shift, 4*LEFT, **kwargs))
        self.add(words)
        kwargs["rate_func"] = rush_into
        self.play(ApplyMethod(sine.shift, 80*LEFT, **kwargs))
        kwargs["rate_func"] = None
        kwargs["run_time"] = 1.0
        sine.to_edge(LEFT, buff = 0)
        for x in range(5):
            self.play(ApplyMethod(sine.shift, 85*LEFT, **kwargs))

class DecomposeTwoFrequencies(Scene):
    def construct(self):
        line = Line(FRAME_Y_RADIUS*DOWN, FRAME_Y_RADIUS*UP)
        sine1 = LongSine().shift(2*UP).set_color("yellow")
        sine2 = LongSine().shift(DOWN).set_color("lightgreen")
        sine1.stretch(2.0/3, 0)
        comp = Mobject(sine1, sine2)

        self.add(line)
        self.play(ApplyMethod(
            comp.shift, 15*LEFT,
            run_time = 7.5,
            rate_func=linear
        ))


class MostRationalsSoundBad(Scene):
    def construct(self):
        self.add(TextMobject("Most rational numbers sound bad!"))

class FlashOnXProximity(Animation):
    def __init__(self, mobject, x_val, *close_mobjects, **kwargs):
        self.x_val = x_val
        self.close_mobjects = close_mobjects
        Animation.__init__(self, mobject, **kwargs)

    def interpolate_mobject(self, alpha):
        for mob in self.close_mobjects:
            if np.min(np.abs(mob.points[:,0] - self.x_val)) < 0.1:
                self.mobject.set_color()
                return
        self.mobject.to_original_color()

class PatternInFrequencies(Scene):
    args_list = [
        (3, 2, "green"),
        (4, 3, "purple"),
        (8, 5, "skyblue"),
        (35, 43, "red"),
    ]
    @staticmethod
    def args_to_string(num1, num2, color):
        return "%d_to_%d"%(num1, num2)

    def construct(self, num1, num2, color):
        big_line = Line(FRAME_Y_RADIUS*UP, FRAME_Y_RADIUS*DOWN)
        big_line.set_color("white").shift(2*LEFT)
        line_template = Line(UP, DOWN)
        line_template.shift(2*UP+2*LEFT)
        setup_width = FRAME_WIDTH
        num_top_lines = int(setup_width)
        num_bot_lines = int(setup_width*num1/num2)
        top_lines = Mobject(*[
            deepcopy(line_template).shift(k*(float(num1)/num2)*RIGHT)
            for k in range(num_top_lines)
        ])
        line_template.shift(4*DOWN)
        bottom_lines = Mobject(*[
            deepcopy(line_template).shift(k*RIGHT)
            for k in range(num_bot_lines)
        ])
        bottom_lines.set_color("blue")
        top_lines.set_color(color)
        kwargs = {
            "run_time" : 10,
            "rate_func" : None
        }

        self.add(big_line)
        self.add(TexMobject("%d:%d"%(num1, num2)))
        fracs = (
            1.0/(num_top_lines-1), 
            1.0/(num_bot_lines-1)
        )
        anims = [
            ApplyMethod(mob.shift, setup_width*LEFT, **kwargs)
            for mob in (top_lines, bottom_lines)
        ]
        anim_mobs = [anim.mobject for anim in anims]
        self.play(
            FlashOnXProximity(big_line, -2, *anim_mobs, **kwargs),
            *anims
        )


class CompareFractionComplexity(Scene):
    def construct(self):
        fractions = []
        for num, den in [(4, 3), (1093,826)]:
            top = TexMobject("%d \\over"%num)
            bottom = TexMobject(str(den)).next_to(top, DOWN, buff = 0.3)
            fractions.append(Mobject(top, bottom))
        frac0 = fractions[0].shift(3*LEFT).split()
        frac1 = fractions[1].shift(3*RIGHT).split()
        arrow1 = Arrow(UP, ORIGIN).next_to(frac0[0], UP)
        arrow2 = Arrow(UP, ORIGIN).next_to(frac1[0], UP)
        simple = TextMobject("Simple").next_to(arrow1, UP)
        simple.set_color("green")
        complicated = TextMobject("Complicated").next_to(arrow2, UP)
        complicated.set_color("red")
        indicates = TextMobject("Indicates complexity").shift(2*DOWN)
        arrow3 = Arrow(indicates.get_top(), frac0[1])
        arrow4 = Arrow(indicates.get_top(), frac1[1])

        self.add(*frac0 + frac1)
        self.wait()
        self.add(simple, complicated)
        self.play(*[
            ShowCreation(arrow)
            for arrow in (arrow1, arrow2)
        ])
        self.wait()
        self.play(*[
            DelayByOrder(ApplyMethod(frac[1].set_color, "yellow"))
            for frac in (frac0, frac1)
        ])
        self.play(
            FadeIn(indicates),
            ShowCreation(arrow3),
            ShowCreation(arrow4)
        )
        self.wait()
        
class IrrationalGang(Scene):
    def construct(self):
        randy = Randolph()
        randy.mouth.set_color(randy.DEFAULT_COLOR)
        randy.sync_parts()
        sqrt13 = TexMobject("\\sqrt{13}").shift(2*LEFT)
        sqrt13.set_color("green")
        zeta3 = TexMobject("\\zeta(3)").shift(2*RIGHT)
        zeta3.set_color("grey")
        eyes = Mobject(*randy.eyes)
        eyes.scale(0.5)
        sqrt13.add(eyes.next_to(sqrt13, UP, buff = 0).shift(0.25*RIGHT))
        eyes.scale(0.5)
        zeta3.add(eyes.next_to(zeta3, UP, buff = 0).shift(0.3*LEFT+0.08*DOWN))
        speech_bubble = SpeechBubble()
        speech_bubble.pin_to(randy)
        speech_bubble.write("We want to play too!")

        self.add(randy, sqrt13, zeta3, speech_bubble, speech_bubble.content)
        self.play(BlinkPiCreature(randy))


class ConstructPiano(Scene):
    def construct(self):
        piano = Piano()
        keys = piano.split()
        anims = []
        askew = deepcopy(keys[-1])
        keys[-1].rotate_in_place(np.pi/5)
        for key in keys:
            key.stroke_width = 1
            key_copy = deepcopy(key).to_corner(DOWN+LEFT)
            key_copy.scale_in_place(0.25)
            key_copy.shift(1.8*random.random()*FRAME_X_RADIUS*RIGHT)
            key_copy.shift(1.8*random.random()*FRAME_Y_RADIUS*UP)
            key_copy.rotate(2*np.pi*random.random())
            anims.append(Transform(key_copy, key))
        self.play(*anims, run_time = 3.0)
        self.wait()
        self.play(Transform(anims[-1].mobject, askew))
        self.wait()


class PianoTuning(Scene):
    def construct(self):
        piano = self.piano = Piano()
        jump = piano.half_note_jump
        semicircle = Circle().filter_out(lambda p : p[1] < 0)
        semicircle.scale(jump/semicircle.get_width())
        semicircles = Mobject(*[
            deepcopy(semicircle).shift(jump*k*RIGHT)
            for k in range(23)
        ])
        semicircles.set_color("white")
        semicircles.next_to(piano, UP, buff = 0)
        semicircles.shift(0.05*RIGHT)
        semicircles.sort_points(lambda p : p[0])
        first_jump = semicircles.split()[0]
        twelfth_root = TexMobject("2^{\\left(\\frac{1}{12}\\right)}")
        twelfth_root.scale(0.75).next_to(first_jump, UP, buff = 1.5)
        line = Line(twelfth_root, first_jump).set_color("grey")
        self.keys = piano.split()
        self.semicircles = semicircles.split()

        self.add(piano)
        self.wait()
        self.play(ShowCreation(first_jump))
        self.play(
            ShowCreation(line),
            FadeIn(twelfth_root)
        )
        self.wait()
        self.play(ShowCreation(semicircles, rate_func=linear))
        self.wait()

        self.show_interval(5, 7)
        self.show_interval(4, 5)

    def show_interval(self, interval, half_steps):
        whole_notes_to_base = 5
        half_notes_to_base = 9

        self.clear()
        self.add(self.piano)
        colors = list(Color("blue").range_to("yellow", 7))
        low = self.keys[whole_notes_to_base]
        high = self.keys[whole_notes_to_base + interval - 1]
        u_brace = Underbrace(low.get_bottom(), high.get_bottom())
        u_brace.set_color("yellow")
        ratio = TexMobject("2^{\\left(\\frac{%d}{12}\\right)}"%half_steps)
        ratio.next_to(u_brace, DOWN, buff = 0.2)
        semicircles = self.semicircles[half_notes_to_base:half_notes_to_base+half_steps]
        product = TexMobject(
            ["\\left(2^{\\left(\\frac{1}{12}\\right)}\\right)"]*half_steps,
            size = "\\small"
        ).next_to(self.piano, UP, buff = 1.0)
        approximate_form = TexMobject("\\approx"+str(2**(float(half_steps)/12)))
        approximate_form.scale(0.75)
        approximate_form.next_to(ratio)
        if interval == 5:
            num_den = (3, 2)
        elif interval == 4:
            num_den = (4, 3)
        should_be = TextMobject("Should be $\\frac{%d}{%d}$"%num_den)
        should_be.next_to(u_brace, DOWN)

        self.play(ApplyMethod(low.set_color, colors[0]))
        self.play(
            ApplyMethod(high.set_color, colors[interval]),
            Transform(Point(u_brace.get_left()), u_brace),
        )
        self.wait()
        self.play(ShimmerIn(should_be))
        self.wait()
        self.remove(should_be)
        terms = product.split()
        for term, semicircle in zip(terms, semicircles):
            self.add(term, semicircle)
            self.wait(0.25)
        self.wait()
        product.sort_points(lambda p : p[1])
        self.play(DelayByOrder(Transform(product, ratio)))
        self.wait()
        self.play(ShimmerIn(approximate_form))
        self.wait()

class PowersOfTwelfthRoot(Scene):
    def construct(self):
        max_height = FRAME_Y_RADIUS-0.5
        min_height = -max_height
        num_terms = 11
        mob_list = []
        fraction_map = {
            1 : Fraction(16, 15),
            2 : Fraction(9, 8),
            3 : Fraction(6, 5),
            4 : Fraction(5, 4),
            5 : Fraction(4, 3),
            7 : Fraction(3, 2),
            8 : Fraction(8, 5),
            9 : Fraction(5, 3),
            10 : Fraction(16, 9),
        }
        approx = TexMobject("\\approx").scale(0.5)
        curr_height = max_height*UP
        spacing = UP*(max_height-min_height)/(len(fraction_map)-1.0)
        for i in range(1, num_terms+1):
            if i not in fraction_map:
                continue
            term = TexMobject("2^{\\left(\\frac{%d}{12}\\right)}"%i)
            term.shift(curr_height)
            curr_height -= spacing
            term.shift(4*LEFT)
            value = 2**(i/12.0)
            approx_form = TexMobject(str(value)[:10])
            approx_copy = deepcopy(approx).next_to(term)
            approx_form.scale(0.5).next_to(approx_copy)
            words = TextMobject("is close to")
            words.scale(approx_form.get_height()/words.get_height())
            words.next_to(approx_form)
            frac = fraction_map[i]
            frac_mob = TexMobject("%d/%d"%(frac.numerator, frac.denominator))
            frac_mob.scale(0.5).next_to(words)
            percent_error = abs(100*((value - frac) / frac))
            error_string = TextMobject([
                "with", str(percent_error)[:4] + "\\%", "error"
            ])
            error_string = error_string.split()
            error_string[1].set_color()
            error_string = Mobject(*error_string)
            error_string.scale(approx_form.get_height()/error_string.get_height())
            error_string.next_to(frac_mob)

            mob_list.append(Mobject(*[
                term, approx_copy, approx_form, words, frac_mob, error_string
            ]))
        self.play(ShimmerIn(Mobject(*mob_list), run_time = 3.0))

class InterestingQuestion(Scene):
    def construct(self):
        words = TextMobject("Interesting Question:", size = "\\Huge")
        words.scale(2.0)
        self.add(words)


class SupposeThereIsASavant(Scene):
    def construct(self):
        words = "Suppose there is a musical savant " + \
                "who finds pleasure in all pairs of " + \
                "notes whose frequencies have a rational ratio"
        words = words.split(" ")
        word_mobs = TextMobject(words).split()
        word_mobs[4].set_color()
        word_mobs[5].set_color()
        for word, word_mob in zip(words, word_mobs):
            self.add(word_mob)
            self.wait(0.1*len(word))

class AllValuesBetween1And2(NumberLineScene):
    def construct(self):
        NumberLineScene.construct(self)
        irrational = 1.2020569031595942        
        cont_frac = [1, 4, 1, 18, 1, 1, 1, 4, 1, 9, 9, 2, 1, 1, 1, 2]        
        one, two, irr = list(map(
            self.number_line.number_to_point, 
            [1, 2, irrational]
        ))
        top_arrow = Arrow(one+UP, one)
        bot_arrow = Arrow(irr+2*DOWN, irr)
        r = TexMobject("r").next_to(top_arrow, UP)
        irr_mob = TexMobject(str(irrational)+"\\dots").next_to(bot_arrow, DOWN)

        approximations = [
            continued_fraction(cont_frac[:k])
            for k in range(1, len(cont_frac))[:8]
        ]

        kwargs = {
            "run_time" : 3.0,
            "rate_func" : there_and_back
        }
        self.play(*[
            ApplyMethod(mob.shift, RIGHT, **kwargs)
            for mob in (r, top_arrow)
        ])
        self.wait() 
        self.remove(r, top_arrow)
        self.play(
            ShimmerIn(irr_mob),
            ShowCreation(bot_arrow)
        )
        self.wait()
        self.add(irr_mob, bot_arrow)

        frac_mob = Point(top_arrow.get_top())
        max_num_zooms = 4
        num_zooms = 0
        for approx in approximations:
            point = self.number_line.number_to_point(approx)
            new_arrow = Arrow(point+UP, point)
            mob = fraction_mobject(approx).next_to(new_arrow, UP)
            self.play(
                Transform(top_arrow, new_arrow),
                Transform(frac_mob, mob),
                run_time = 0.5
            )
            self.wait(0.5)
            points = list(map(self.number_line.number_to_point, [approx, irrational]))
            distance = get_norm(points[1]-points[0])
            if distance < 0.3*FRAME_X_RADIUS and num_zooms < max_num_zooms:
                num_zooms += 1
                new_distance = 0.75*FRAME_X_RADIUS
                self.zoom_in_on(irrational, new_distance/distance)
                for mob in irr_mob, bot_arrow:
                    mob.shift(mob.get_center()[0]*LEFT)
            self.wait(0.5)


class ChallengeTwo(Scene):
    def construct(self):
        self.add(TextMobject("Challenge #2"))

class CoveringSetsWithOpenIntervals(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        dots = Mobject(*[
            Dot().shift(self.number_line.number_to_point(num)+UP)
            for num in set([0.2, 0.25, 0.45, 0.6, 0.65])
        ])
        theorems = [
            TextMobject(words).shift(UP)
            for words in [
                "Heine-Borel Theorem",
                "Lebesgue's Number Lemma",
                "Vitali Covering Lemma",
                "Besicovitch Covering Theorem",
                "$\\vdots$"
            ]
        ]

        self.add(dots)
        self.play(DelayByOrder(ApplyMethod(dots.shift, DOWN, run_time = 2)))
        self.wait()
        for center in 0.225, 0.475, 0.625:
            self.add_open_interval(center, 0.1, run_time = 1.0)
        self.wait()
        for x in range(2*len(theorems)):
            self.play(*[
                ApplyMethod(th.shift, UP, rate_func=linear)
                for th in theorems[:x+1]
            ])

class DefineOpenInterval(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        open_interval, line = self.add_open_interval(0.5, 0.75, run_time = 1.0)
        left, right = open_interval.get_left(), open_interval.get_right()
        a, less_than1, x, less_than2, b = \
            TexMobject(["a", "<", "x", "<", "b"]).shift(UP).split()
        left_arrow = Arrow(a.get_corner(DOWN+LEFT), left)
        right_arrow = Arrow(b.get_corner(DOWN+RIGHT), right)

        self.play(*[ShimmerIn(mob) for mob in (a, less_than1, x)])
        self.play(ShowCreation(left_arrow))
        self.wait()
        self.play(*[ShimmerIn(mob) for mob in (less_than2, b)])
        self.play(ShowCreation(right_arrow))
        self.wait()


class ShowAllFractions(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        self.show_all_fractions(
            num_fractions = 100,
            remove_as_you_go = False, 
            pause_time = 0.3
        )
        self.wait()
        self.play(*[
            CounterclockwiseTransform(mob, Point(mob.get_center()))
            for mob in self.mobjects
            if isinstance(mob, ImageMobject)
        ])
        self.wait()

class NaiveFractionCover(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        self.add_fraction_ticks(100)
        self.add_fraction_ticks(run_time = 5.0)
        last_interval = None
        centers = np.arange(0, 1.1, .1)
        random.shuffle(centers)
        for num, count in zip(centers, it.count()):
            if count == 0:
                kwargs = {
                    "run_time" : 1.0,
                    "rate_func" : rush_into
                }
            elif count == 10:
                kwargs = {
                    "run_time" : 1.0,
                    "rate_func" : rush_from
                }
            else:
                kwargs = {
                    "run_time" : 0.25,
                    "rate_func" : None
                }
            open_interval, line = self.add_open_interval(num, 0.1)
            open_interval.shift(UP)
            self.remove(line)
            anims = [ApplyMethod(open_interval.shift, DOWN, **kwargs)]
            last_interval = open_interval
            self.play(*anims)
        self.wait()

class CoverFractionsWithWholeInterval(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        self.add_fraction_ticks()
        self.wait()
        self.add_open_interval(0.5, 1, color = "red", run_time = 2.0)
        self.wait()

class SumOfIntervalsMustBeLessThan1(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        self.add_fraction_ticks()
        anims = []
        last_plus = Point((FRAME_X_RADIUS-0.5)*LEFT+2*UP)        
        for num in np.arange(0, 1.1, .1):
            open_interval, line = self.add_open_interval(num, 0.1)
            self.remove(line)
            int_copy = deepcopy(open_interval)
            int_copy.scale(0.6).next_to(last_plus, buff = 0.1)
            last_plus = TexMobject("+").scale(0.3)
            last_plus.next_to(int_copy, buff = 0.1)
            anims.append(Transform(open_interval, int_copy))
            if num < 1.0:
                anims.append(FadeIn(last_plus))
        less_than1 = TexMobject("<1").scale(0.5)
        less_than1.next_to(int_copy)
        dots = TexMobject("\\dots").replace(int_copy)
        words = TextMobject("Use infinitely many intervals")
        words.shift(UP)

        self.wait()
        self.play(*anims)
        self.play(ShimmerIn(less_than1))
        self.wait()
        self.play(Transform(anims[-1].mobject, dots))
        self.play(ShimmerIn(words))
        self.wait()

class RationalsAreDense(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        words = TextMobject(["Rationals are", "\\emph{dense}", "in the reals"])
        words.shift(2*UP)
        words = words.split()
        words[1].set_color()

        self.add(words[0])
        self.play(ShimmerIn(words[1]))
        self.add(words[2])
        self.wait()
        ticks = self.add_fraction_ticks(run_time = 5.0)
        self.wait()
        for center, width in [(0.5, 0.1), (0.2, 0.05), (0.7, 0.01)]:
            oi, line = self.add_open_interval(center, width, run_time = 1)
            self.remove(line)
        self.wait()
        for compound in oi, ticks:
            self.remove(compound)
            self.add(*compound.split())
        self.zoom_in_on(0.7, 100)
        self.play(ShowCreation(ticks, run_time = 2.0))
        self.wait()


class SurelyItsImpossible(Scene):
    def construct(self):
        self.add(TextMobject("Surely it's impossible!"))

class HowCanYouNotCoverEntireInterval(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        small_words = TextMobject("""
            In case you are wondering, it is indeed true 
            that if you cover all real numbers between 0 
            and 1 with a set of open intervals, the sum 
            of the lengths of those intervals must be at 
            least 1. While intuitive, this is not actually 
            as obvious as it might seem, just try to prove 
            it for yourself!
        """)
        small_words.scale(0.5).to_corner(UP+RIGHT)        
        big_words = TextMobject("""
            Covering all numbers from 0 to 1 \\emph{will}
            force the sum of the lengths of your intervals
            to be at least 1.
        """)
        big_words.next_to(self.number_line, DOWN, buff = 0.5)

        ticks = self.add_fraction_ticks()
        left  = self.number_line.number_to_point(0)
        right = self.number_line.number_to_point(1)
        full_line = Line(left, right)
        full_line.set_color("red")
        # dot = Dot().shift(left).set_color("red")
        # point = Point(left).set_color("red")
        intervals = []
        for num in np.arange(0, 1.1, .1):
            open_interval, line = self.add_open_interval(num, 0.1)
            self.remove(line)
            intervals.append(open_interval)
        self.wait()
        self.remove(ticks)
        self.play(*[
            Transform(tick, full_line)
            for tick in ticks.split()
        ])
        self.play(ShimmerIn(big_words))
        self.wait()
        # self.play(DelayByOrder(FadeToColor(full_line, "red")))
        self.play(ShimmerIn(small_words))
        self.wait()

class PauseNow(Scene):
    def construct(self):
        top_words = TextMobject("Try for yourself!").scale(2).shift(3*UP)
        bot_words = TextMobject("""
            If you've never seen this before, you will get 
            the most out of the solution and the intuitions
            I illustrate only after pulling out a pencil and
            paper and taking a wack at it yourself.
        """).next_to(top_words, DOWN, buff = 0.5)
        self.add(top_words, bot_words)

class StepsToSolution(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        self.spacing = 0.7
        steps = list(map(TextMobject, [
            "Enumerate all rationals in (0, 1)",
            "Assign one interval to each rational",
            "Choose sum of the form $\\mathlarger{\\sum}_{n=1}^\\infty a_n = 1$",
            "Pick any $\\epsilon$ such that $0 < \\epsilon < 1$",
            "Stretch the $n$th interval to have length $\\epsilon/2^n$",
        ]))
        for step in steps:
            step.shift(DOWN)
        for step in steps[2:]:
            step.shift(DOWN)
        for step, count in zip(steps, it.count()):
            self.add(step)
            self.wait()
            if count == 0:
                self.enumerate_rationals()
            elif count == 1:
                self.assign_intervals_to_rationals()
            elif count == 2:
                self.add_terms()
            elif count == 3:
                self.multiply_by_epsilon()
            elif count == 4:
                self.stretch_intervals()
            self.remove(step)

    def enumerate_rationals(self):
        ticks = self.add_fraction_ticks(run_time = 2.0)
        anims = []
        commas = Mobject()
        denom_to_mobs = {}
        for frac, count in zip(rationals(), list(range(1,28))):
            mob, tick = self.add_fraction(frac, shrink = True)
            self.wait(0.1)
            self.remove(tick)
            if frac.denominator not in denom_to_mobs:
                denom_to_mobs[frac.denominator] = []
            denom_to_mobs[frac.denominator].append(mob)
            mob_copy = deepcopy(mob).center()
            mob_copy.shift((2.4-mob_copy.get_bottom()[1])*UP)
            mob_copy.shift((-FRAME_X_RADIUS+self.spacing*count)*RIGHT)
            comma = TextMobject(",").next_to(mob_copy, buff = 0.1, aligned_edge = DOWN)
            anims.append(Transform(mob, mob_copy))
            commas.add(comma)
        anims.append(ShimmerIn(commas))
        new_ticks = []
        for tick, count in zip(ticks.split(), it.count(1)):
            tick_copy = deepcopy(tick).center().shift(1.6*UP)
            tick_copy.shift((-FRAME_X_RADIUS+self.spacing*count)*RIGHT)
            new_ticks.append(tick_copy)
        new_ticks = Mobject(*new_ticks)
        anims.append(DelayByOrder(Transform(ticks, new_ticks)))
        self.wait()
        self.play(*anims)
        self.wait()
        for denom in range(2, 10):
            for mob in denom_to_mobs[denom]:
                mob.set_color("green")
            self.wait()
            for mob in denom_to_mobs[denom]:
                mob.to_original_color()
        self.ticks = ticks.split()[:20]

    def assign_intervals_to_rationals(self):
        anims = []
        for tick in self.ticks:
            interval = OpenInterval(tick.get_center(), self.spacing)
            interval.scale_in_place(0.5)
            squished = deepcopy(interval).stretch_to_fit_width(0)
            anims.append(Transform(squished, interval))
        self.play(*anims)
        self.show_frame()
        self.wait()
        to_remove = [self.number_line] + self.number_mobs
        self.play(*[
            ApplyMethod(mob.shift, FRAME_WIDTH*RIGHT)
            for mob in to_remove
        ])
        self.remove(*to_remove)
        self.wait()

        self.intervals = [a.mobject for a in anims]
        kwargs = {
            "run_time" : 2.0,
            "rate_func" : there_and_back
        }
        self.play(*[
            ApplyMethod(mob.scale_in_place, 0.5*random.random(), **kwargs)
            for mob in self.intervals
        ])
        self.wait()

    def add_terms(self):
        self.ones = []
        scale_factor = 0.6
        plus = None
        for count in range(1, 10):
            frac_bottom = TexMobject("\\over %d"%(2**count))
            frac_bottom.scale(scale_factor)
            one = TexMobject("1").scale(scale_factor)
            one.next_to(frac_bottom, UP, buff = 0.1)
            compound = Mobject(frac_bottom, one)
            if plus:
                compound.next_to(plus)
            else:
                compound.to_edge(LEFT)
            plus = TexMobject("+").scale(scale_factor)
            plus.next_to(compound)
            frac_bottom, one = compound.split()
            self.ones.append(one)
            self.add(frac_bottom, one, plus)
            self.wait(0.2)
        dots = TexMobject("\\dots").scale(scale_factor).next_to(plus)
        arrow = Arrow(ORIGIN, RIGHT).next_to(dots)
        one = TexMobject("1").next_to(arrow)
        self.ones.append(one)
        self.play(*[ShowCreation(mob) for mob in (dots, arrow, one)])
        self.wait()

    def multiply_by_epsilon(self):
        self.play(*[
            CounterclockwiseTransform(
                one,
                TexMobject("\\epsilon").replace(one)
            )
            for one in self.ones
        ])
        self.wait()

    def stretch_intervals(self):
        for interval, count in zip(self.intervals, it.count(1)):
            self.play(
                ApplyMethod(interval.scale_in_place, 1.0/(count**2)),
                run_time = 1.0/count
            )
        self.wait()


class OurSumCanBeArbitrarilySmall(Scene):
    def construct(self):
        step_size = 0.01
        epsilon = TexMobject("\\epsilon")
        equals = TexMobject("=").next_to(epsilon)
        self.add(epsilon, equals)
        for num in np.arange(1, 0, -step_size):
            parts = list(map(TexMobject, str(num)))
            parts[0].next_to(equals)
            for i in range(1, len(parts)):
                parts[i].next_to(parts[i-1], buff = 0.1, aligned_edge = DOWN)
            self.add(*parts)
            self.wait(0.05)
            self.remove(*parts)
        self.wait()
        self.clear()
        words = TextMobject([
            "Not only can the sum be $< 1$,\\\\",
            "it can be \\emph{arbitrarily small} !"
        ]).split()
        self.add(words[0])
        self.wait()
        self.play(ShimmerIn(words[1].set_color()))
        self.wait()

class ProofDoesNotEqualIntuition(Scene):
    def construct(self):
        self.add(TextMobject("Proof $\\ne$ Intuition"))

class StillFeelsCounterintuitive(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        ticks = self.add_fraction_ticks(run_time = 1.0)
        epsilon, equals, num = list(map(TexMobject, ["\\epsilon", "=", "0.3"]))
        epsilon.shift(2*UP)
        equals.next_to(epsilon)
        num.next_to(equals)
        self.add(epsilon, equals, num)
        self.cover_fractions()
        self.remove(ticks)
        self.add(*ticks.split())
        self.zoom_in_on(np.sqrt(2)/2, 100)
        self.play(ShowCreation(ticks))
        self.wait()

class VisualIntuition(Scene):
    def construct(self):
        self.add(TextMobject("Visual Intuition:"))

class SideNote(Scene):
    def construct(self):
        self.add(TextMobject("(Brief Sidenote)"))

class TroubleDrawingSmallInterval(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        interval, line = self.add_open_interval(0.5, 0.5)
        big = Mobject(interval, line)
        small_int, small_line = self.add_open_interval(0.5, 0.01)
        small = Mobject(small_int, line.scale_in_place(0.01/0.5))
        shrunk = deepcopy(big).scale_in_place(0.01/0.5)
        self.clear()
        IntervalScene.construct(self)
        words = TextMobject("This tiny stretch")
        words.shift(2*UP+2*LEFT)
        arrow = Arrow(words, line)

        for target in shrunk, small:
            mob = deepcopy(big)
            self.play(Transform(
                mob, target,
                run_time = 2.0
            ))
            self.wait()
            self.play(Transform(mob, big))
            self.wait()
            self.remove(mob)
        self.play(Transform(big, small))
        self.play(ShimmerIn(words), ShowCreation(arrow))
        self.play(Transform(
            line, deepcopy(line).scale(10).shift(DOWN),
            run_time = 2.0,
            rate_func = there_and_back
        ))
        self.wait()

class WhatDoesItLookLikeToBeOutside(Scene):
    def construct(self):
        self.add(TextMobject(
            "What does it look like for a number to be outside a dense set of intervals?"
        ))

class ZoomInOnSqrt2Over2(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        epsilon, equals, num = list(map(TexMobject, ["\\epsilon", "=", "0.3"]))
        equals.next_to(epsilon)
        num.next_to(equals)
        self.add(Mobject(epsilon, equals, num).center().shift(2*UP))
        intervals, lines = self.cover_fractions()
        self.remove(*lines)
        irr = TexMobject("\\frac{\\sqrt{2}}{2}")
        point = self.number_line.number_to_point(np.sqrt(2)/2)
        arrow = Arrow(point+UP, point)
        irr.next_to(arrow, UP)
        self.play(ShimmerIn(irr), ShowCreation(arrow))
        for count in range(4):
            self.remove(*intervals)
            self.remove(*lines)
            self.zoom_in_on(np.sqrt(2)/2, 20)
            for mob in irr, arrow:
                mob.shift(mob.get_center()[0]*LEFT)
            intervals, lines = self.cover_fractions()

class NotCoveredMeansCacophonous(Scene):
    def construct(self):
        statement1 = TextMobject("$\\frac{\\sqrt{2}}{2}$ is not covered")
        implies = TexMobject("\\Rightarrow")
        statement2 = TextMobject("Rationals which are close to $\\frac{\\sqrt{2}}{2}$ must have large denominators")
        statement1.to_edge(LEFT)
        implies.next_to(statement1)
        statement2.next_to(implies)
        implies.sort_points()

        self.add(statement1)
        self.wait()
        self.play(ShowCreation(implies))
        self.play(ShimmerIn(statement2))
        self.wait()

class ShiftSetupByOne(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        new_interval = UnitInterval(
            number_at_center = 1.5,
            leftmost_tick = 1,
            numbers_with_elongated_ticks = [1, 2],
        )
        new_interval.add_numbers(1, 2)
        side_shift_val = self.number_line.number_to_point(1)
        side_shift_val -= new_interval.number_to_point(1)
        new_interval.shift(side_shift_val)
        self.add(new_interval)
        self.number_line.add_numbers(0)
        self.remove(*self.number_mobs)
        epsilon_mob = TexMobject("\\epsilon = 0.01").to_edge(UP)
        self.add(epsilon_mob)
        fraction_ticks = self.add_fraction_ticks()
        self.remove(fraction_ticks)
        intervals, lines = self.cover_fractions(
            epsilon = 0.01,
            num_fractions = 150,
            run_time_per_interval = 0,
        )
        self.remove(*intervals+lines)        
        for interval, frac in zip(intervals, rationals()):
            interval.scale_in_place(2.0/frac.denominator)


        for interval in intervals[:10]:
            squished = deepcopy(interval).stretch_to_fit_width(0)
            self.play(Transform(squished, interval), run_time = 0.2)
            self.remove(squished)
            self.add(interval)
        for interval in intervals[10:50]:
            self.add(interval)
            self.wait(0.1)
        for interval in intervals[50:]:
            self.add(interval)
        self.wait()
        mobs_shifts = [
            (intervals, UP),
            ([self.number_line, new_interval], side_shift_val*LEFT),
            (intervals, DOWN)
        ]
        for mobs, shift_val in mobs_shifts:
            self.play(*[
                ApplyMethod(mob.shift, shift_val)
                for mob in mobs
            ])
        self.number_line = new_interval
        self.wait()
        words = TextMobject(
            "Almost all the covered numbers are harmonious!",
            size = "\\small"
        ).shift(2*UP)
        self.play(ShimmerIn(words))
        self.wait()
        for num in [7, 5]:
            point = self.number_line.number_to_point(2**(num/12.))
            arrow = Arrow(point+DOWN, point)
            mob = TexMobject(
                "2^{\\left(\\frac{%d}{12}\\right)}"%num
            ).next_to(arrow, DOWN)
            self.play(ShimmerIn(mob), ShowCreation(arrow))
            self.wait()
            self.remove(mob, arrow)
        self.remove(words)
        words = TextMobject(
            "Cacophonous covered numbers:",
            size = "\\small"
        )
        words.shift(2*UP)
        answer1 = TextMobject("Complicated rationals,", size = "\\small")
        answer2 = TextMobject(
            "real numbers \\emph{very very very} close to them",
            size = "\\small"
        )
        compound = Mobject(answer1, answer2.next_to(answer1))
        compound.next_to(words, DOWN)
        answer1, answer2 = compound.split()

        self.add(words)
        self.wait()
        self.remove(*intervals)
        self.add(answer1)
        self.play(ShowCreation(fraction_ticks, run_time = 5.0))
        self.add(answer2)
        self.wait()
        self.remove(words, answer1, answer2)
        words = TextMobject([
            "To a", "savant,", "harmonious numbers could be ",
            "\\emph{precisely}", "those 1\\% covered by the intervals"
        ]).shift(2*UP)
        words = words.split()
        words[1].set_color()
        words[3].set_color()
        self.add(*words)
        self.play(ShowCreation(
            Mobject(*intervals),
            run_time = 5.0
        ))
        self.wait()

class FinalEquivalence(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        ticks = self.add_fraction_ticks()
        intervals, lines = self.cover_fractions(
            epsilon = 0.01,
            num_fractions = 150,
            run_time_per_interval = 0,
        )
        for interval, frac in zip(intervals, rationals()):
            interval.scale_in_place(2.0/frac.denominator)
        self.remove(*intervals+lines)
        intervals = Mobject(*intervals)
        arrow = TexMobject("\\Leftrightarrow")
        top_words = TextMobject("Harmonious numbers are rare,")
        bot_words = TextMobject("even for the savant")
        bot_words.set_color().next_to(top_words, DOWN)
        words = Mobject(top_words, bot_words)
        words.next_to(arrow)

        self.play(
            ShowCreation(ticks),
            Transform(
                deepcopy(intervals).stretch_to_fit_height(0),
                intervals
            )
        )
        everything = Mobject(*self.mobjects)
        self.clear()
        self.play(Transform(
            everything,
            deepcopy(everything).scale(0.5).to_edge(LEFT)
        ))
        self.add(arrow)
        self.play(ShimmerIn(words))
        self.wait()





if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)


