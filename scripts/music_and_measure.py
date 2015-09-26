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
from inventing_math import underbrace

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

class Piano(ImageMobject):
    SHOULD_BUFF_POINTS = False
    def __init__(self, **kwargs):
        ImageMobject.__init__(self, "piano_keyboard", invert = False)
        jump = self.get_width()/24        
        self.scale(0.5).center()
        self.half_note_jump = self.get_width()/24
        self.ivory_jump = self.get_width()/14

    def split(self):
        left = self.get_left()[0]
        keys = []
        for count in range(14):
            key = Mobject(color = "white")
            x0 = left + count*self.ivory_jump
            x1 = x0 + self.ivory_jump
            key.add_points(
                self.points[
                    (self.points[:,0] > x0)*(self.points[:,0] < x1)
                ]
            )
            keys.append(key)
        return keys


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
                (amplitude/((k+1)**2.5))*np.sin(2*mult*t)*np.sin(k*mult*x)
                for k in range(overtones)
                for mult in [(num_periods+k)*np.pi]
            ])
        self.func = func
        kwargs["run_time"] = run_time
        kwargs["alpha_func"] = alpha_func
        Animation.__init__(self, Mobject1D(color = color), **kwargs)

    def update_mobject(self, alpha):
        self.mobject.init_points()
        epsilon = self.mobject.epsilon
        self.mobject.add_points([
            [x*self.radius, self.func(x, alpha*self.run_time)+y, 0]
            for x in np.arange(-1, 1, epsilon/self.radius)
            for y in epsilon*np.arange(3)
        ])
        self.mobject.shift(self.center)


class IntervalScene(Scene):
    def construct(self):
        self.interval = UnitInterval()
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
        width *= self.interval.unit_length_to_spacial_width
        center_point = self.interval.number_to_point(num)
        open_interval = OpenInterval(center_point, width)
        if color:
            open_interval.highlight(color)
        interval_line = Line(open_interval.get_left(), open_interval.get_right())
        interval_line.scale_in_place(0.9)#Silliness
        interval_line.do_in_place(interval_line.sort_points, np.linalg.norm)
        interval_line.highlight("yellow")
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
        self.play(ShowCreation(arrow_to_int))
        self.add(integration)
        self.dither()
        self.play(ShowCreation(arrow_to_prob))
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
        self.play(DelayByOrder(Transform(all_mobs, line)))
        self.clear()
        self.play(VibratingString(alpha_func = smooth))
        self.clear()
        self.add(line)
        self.dither()


class ChallengeOne(Scene):
    def construct(self):
        title = text_mobject("Challenge #1").to_edge(UP)
        start_color = Color("blue")
        colors = start_color.range_to("white", 6)
        self.bottom_vibration = VibratingString(
            num_periods = 1, run_time = 3.0, 
            center = DOWN, color = start_color
        )
        top_vibrations = [
            VibratingString(
                num_periods = freq, run_time = 3.0,
                center = 2*UP, color = colors.next()
            )
            for freq in [1, 2, 5.0/3, 4.0/3, 2]
        ]
        freq_220 = text_mobject("220 Hz")
        freq_r220 = text_mobject("$r\\times$220 Hz")
        freq_330 = text_mobject("1.5$\\times$220 Hz")
        freq_sqrt2 = text_mobject("$\\sqrt{2}\\times$220 Hz")
        freq_220.shift(1.5*DOWN)
        for freq in freq_r220, freq_330, freq_sqrt2:
            freq.shift(1.5*UP)
        r_constraint = tex_mobject("(1<r<2)", size = "\\large")

        self.add(title)
        self.dither()
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
        r1 = tex_mobject("r").next_to(arrow1, UP)
        r2 = tex_mobject("r").next_to(arrow2, UP)
        kwargs = {
            "run_time" : 5.0,
            "alpha_func" : there_and_back
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

class QuestionAndAnswer(Scene):
    def construct(self):
        Q = text_mobject("Q:").shift(UP).to_edge(LEFT)
        A = text_mobject("A:").shift(DOWN).to_edge(LEFT)
        string1 = VibratingString(center = 3*UP, color = "blue")
        string2 = VibratingString(num_periods = 2, center = 3.5*UP, color = "green")
        twotwenty = tex_mobject("220").scale(0.25).next_to(string1.mobject, LEFT)
        r220 = tex_mobject("r\\times220").scale(0.25).next_to(string2.mobject, LEFT)
        question = text_mobject(
            "For what values of $r$ will the frequencies 220~Hz and \
            $r\\times$220~Hz sound nice together?"
        ).next_to(Q)
        answer = text_mobject([
            "When $r$ is", 
            "sufficiently close to",
            "a rational number"
        ], size = "\\small").scale(1.5)
        answer.next_to(A)
        correction1 = text_mobject(
            "with sufficiently low denominator",
            size = "\\small"
        ).scale(1.5)
        correction1.highlight("yellow")
        correction1.next_to(A).shift(2*answer.get_height()*DOWN)
        answer = answer.split()
        answer[1].highlight("green")
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
    ]
    @staticmethod
    def args_to_string(fraction, color):
        return str(fraction).replace("/", "_to_")

    def construct(self, fraction, color):
        string1 = VibratingString(
            num_periods = 1, run_time = 5.0, 
            center = DOWN, color = "blue"
        )
        string2 = VibratingString(
            num_periods = fraction, run_time = 5.0,
            center = 2*UP, color = color
        )
        self.add(fraction_mobject(fraction).shift(0.5*UP))
        self.play(string1, string2)

class FlashOnXProximity(Animation):
    def __init__(self, mobject, x_val, *close_mobjects, **kwargs):
        self.x_val = x_val
        self.close_mobjects = close_mobjects
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        for mob in self.close_mobjects:
            if np.min(np.abs(mob.points[:,0] - self.x_val)) < 0.1:
                self.mobject.highlight()
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
        big_line = Line(SPACE_HEIGHT*UP, SPACE_HEIGHT*DOWN)
        big_line.highlight("white").shift(2*LEFT)
        line_template = Line(UP, DOWN)
        line_template.shift(2*UP+2*LEFT)
        setup_width = 2*SPACE_WIDTH
        num_top_lines = int(setup_width)
        num_bot_lines = int(setup_width*num1/num2)
        top_lines = CompoundMobject(*[
            deepcopy(line_template).shift(k*(float(num1)/num2)*RIGHT)
            for k in range(num_top_lines)
        ])
        line_template.shift(4*DOWN)
        bottom_lines = CompoundMobject(*[
            deepcopy(line_template).shift(k*RIGHT)
            for k in range(num_bot_lines)
        ])
        bottom_lines.highlight("blue")
        top_lines.highlight(color)
        kwargs = {
            "run_time" : 10,
            "alpha_func" : None
        }

        self.add(big_line)
        self.add(tex_mobject("%d:%d"%(num1, num2)))
        fracs = (
            1.0/(num_top_lines-1), 
            1.0/(num_bot_lines-1)
        )
        anims = [
            ApplyMethod(mob.shift, setup_width*LEFT, **kwargs)
            for mob in top_lines, bottom_lines
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
            top = tex_mobject("%d \\over"%num)
            bottom = tex_mobject(str(den)).next_to(top, DOWN, buff = 0.3)
            fractions.append(CompoundMobject(top, bottom))
        frac0 = fractions[0].shift(3*LEFT).split()
        frac1 = fractions[1].shift(3*RIGHT).split()
        arrow1 = Arrow(UP, ORIGIN).next_to(frac0[0], UP)
        arrow2 = Arrow(UP, ORIGIN).next_to(frac1[0], UP)
        simple = text_mobject("Simple").next_to(arrow1, UP)
        simple.highlight("green")
        complicated = text_mobject("Complicated").next_to(arrow2, UP)
        complicated.highlight("red")
        indicates = text_mobject("Indicates complexity").shift(2*DOWN)
        arrow3 = Arrow(indicates.get_top(), frac0[1])
        arrow4 = Arrow(indicates.get_top(), frac1[1])

        self.add(*frac0 + frac1)
        self.dither()
        self.add(simple, complicated)
        self.play(*[
            ShowCreation(arrow)
            for arrow in arrow1, arrow2
        ])
        self.dither()
        self.play(*[
            DelayByOrder(ApplyMethod(frac[1].highlight, "yellow"))
            for frac in frac0, frac1
        ])
        self.play(
            FadeIn(indicates),
            ShowCreation(arrow3),
            ShowCreation(arrow4)
        )
        self.dither()
        
class IrrationalGang(Scene):
    def construct(self):
        randy = Randolph()
        randy.mouth.highlight(randy.DEFAULT_COLOR)
        randy.sync_parts()
        sqrt13 = tex_mobject("\\sqrt{13}").shift(2*LEFT)
        sqrt13.highlight("green")
        zeta3 = tex_mobject("\\zeta(3)").shift(2*RIGHT)
        zeta3.highlight("grey")
        eyes = CompoundMobject(*randy.eyes)
        eyes.scale(0.5)
        sqrt13.add(eyes.next_to(sqrt13, UP, buff = 0).shift(0.25*RIGHT))
        eyes.scale(0.5)
        zeta3.add(eyes.next_to(zeta3, UP, buff = 0).shift(0.3*LEFT+0.08*DOWN))
        speech_bubble = SpeechBubble()
        speech_bubble.pin_to(randy)
        speech_bubble.write("We want to play too!")

        self.add(randy, sqrt13, zeta3, speech_bubble, speech_bubble.content)
        self.play(BlinkPiCreature(randy))



class PianoTuning(Scene):
    def construct(self):
        piano = self.piano = Piano()
        jump = piano.half_note_jump
        semicircle = Circle().filter_out(lambda p : p[1] < 0)
        semicircle.scale(jump/semicircle.get_width())
        semicircles = CompoundMobject(*[
            deepcopy(semicircle).shift(jump*k*RIGHT)
            for k in range(23)
        ])
        semicircles.highlight("white")
        semicircles.next_to(piano, UP, buff = 0)
        semicircles.shift(0.05*RIGHT)
        semicircles.sort_points(lambda p : p[0])
        first_jump = semicircles.split()[0]
        twelfth_root = tex_mobject("2^{\\left(\\frac{1}{12}\\right)}")
        twelfth_root.scale(0.75).next_to(first_jump, UP, buff = 1.5)
        line = Line(twelfth_root, first_jump).highlight("grey")
        self.keys = piano.split()
        self.semicircles = semicircles.split()

        self.add(piano)
        self.dither()
        self.play(ShowCreation(first_jump))
        self.play(
            ShowCreation(line),
            FadeIn(twelfth_root)
        )
        self.dither()
        self.play(ShowCreation(semicircles, alpha_func = None))
        self.dither()

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
        u_brace = underbrace(low.get_bottom(), high.get_bottom())
        u_brace.highlight("yellow")
        ratio = tex_mobject("2^{\\left(\\frac{%d}{12}\\right)}"%half_steps)
        ratio.next_to(u_brace, DOWN, buff = 0.2)
        semicircles = self.semicircles[half_notes_to_base:half_notes_to_base+half_steps]
        product = tex_mobject(
            ["\\left(2^{\\left(\\frac{1}{12}\\right)}\\right)"]*half_steps,
            size = "\\small"
        ).next_to(self.piano, UP, buff = 1.0)
        approximate_form = tex_mobject("\\approx"+str(2**(float(half_steps)/12)))
        approximate_form.scale(0.75)
        approximate_form.next_to(ratio)

        self.play(ApplyMethod(low.highlight, colors[0]))
        self.play(
            ApplyMethod(high.highlight, colors[interval]),
            Transform(Point(u_brace.get_left()), u_brace),
        )
        terms = product.split()
        for term, semicircle in zip(terms, semicircles):
            self.add(term, semicircle)
            self.dither(0.25)
        self.dither()
        product.sort_points(lambda p : p[1])
        self.play(DelayByOrder(Transform(product, ratio)))
        self.dither()
        self.play(ShimmerIn(approximate_form))
        self.dither()

class PowersOfTwelfthRoot(Scene):
    def construct(self):
        max_height = SPACE_HEIGHT-0.5
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
        approx = tex_mobject("\\approx").scale(0.5)
        curr_height = max_height*UP
        spacing = UP*(max_height-min_height)/(len(fraction_map)-1.0)
        for i in range(1, num_terms+1):
            if i not in fraction_map:
                continue
            term = tex_mobject("2^{\\left(\\frac{%d}{12}\\right)}"%i)
            term.shift(curr_height)
            curr_height -= spacing
            term.shift(4*LEFT)
            value = 2**(i/12.0)
            approx_form = tex_mobject(str(value)[:10])
            approx_copy = deepcopy(approx).next_to(term)
            approx_form.scale(0.5).next_to(approx_copy)
            words = text_mobject("is close to")
            words.scale(approx_form.get_height()/words.get_height())
            words.next_to(approx_form)
            frac = fraction_map[i]
            frac_mob = tex_mobject("%d/%d"%(frac.numerator, frac.denominator))
            frac_mob.scale(0.5).next_to(words)
            percent_error = abs(100*((value - frac) / frac))
            error_string = text_mobject([
                "with", str(percent_error)[:4] + "\\%", "error"
            ])
            error_string = error_string.split()
            error_string[1].highlight()
            error_string = CompoundMobject(*error_string)
            error_string.scale(approx_form.get_height()/error_string.get_height())
            error_string.next_to(frac_mob)

            mob_list.append(CompoundMobject(*[
                term, approx_copy, approx_form, words, frac_mob, error_string
            ]))
        self.play(ShimmerIn(CompoundMobject(*mob_list), run_time = 3.0))


class AllValuesBetween1And2(Scene):
    def construct(self):
        irrational = 1.2020569031595942        
        cont_frac = [1, 4, 1, 18, 1, 1, 1, 4, 1, 9, 9, 2, 1, 1, 1, 2]        
        number_line = NumberLine(interval_size = 1).add_numbers()
        one, two = 2*RIGHT, 4*RIGHT
        top_arrow = Arrow(one+UP, one)
        bot_arrow = Arrow(2*irrational*RIGHT+DOWN, 2*irrational*RIGHT)
        r = tex_mobject("r").next_to(top_arrow, UP)
        irr_mob = tex_mobject(str(irrational)).next_to(bot_arrow, DOWN)

        approximations = [
            continued_fraction(cont_frac[:k])
            for k in range(1, len(cont_frac))
        ]
        approx_mobs = [fraction_mobject(a) for a in approximations]

        self.add(number_line)
        kwargs = {
            "run_time" : 3.0,
            "alpha_func" : there_and_back
        }
        self.play(*[
            ApplyMethod(mob.shift, 2*RIGHT, **kwargs)
            for mob in r, top_arrow
        ])
        self.remove(r, top_arrow)
        self.play(
            ShimmerIn(irr_mob),
            ShowCreation(bot_arrow)
        )
        frac_mob = Point(top_arrow.get_top())
        for approx in approximations:
            point = 2*float(approx)*RIGHT
            new_arrow = Arrow(point+UP, point)
            mob = fraction_mobject(approx).next_to(new_arrow, UP)
            self.play(
                Transform(top_arrow, new_arrow),
                Transform(frac_mob, mob),
                run_time = 0.2
            )
            self.dither(0.5)



class SampleIntervalScene(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        self.cover_fractions()
        self.dither()


class ShowAllFractions(IntervalScene):
    def construct(self):
        IntervalScene.construct(self)
        self.show_all_fractions(
            num_fractions = 100,
            remove_as_you_go = False, 
            pause_time = 0.3
        )


if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)


