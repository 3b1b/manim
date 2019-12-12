#!/usr/bin/env python


import numpy as np
import itertools as it
from copy import deepcopy
import sys

from manimlib.imports import *
from script_wrapper import command_line_create_scene
from .generate_logo import LogoGeneration

POEM_LINES = """Fixed poorly in notation with that two,
you shine so loud that you deserve a name.
Late though we are to make a change, it's true,
We can extol you 'til you have pi's fame.
One might object, ``Conventions matter not!
Great formulae cast truths transcending names.''
I've noticed, though, how language molds my thoughts;
the natural terms make heart and head the same.
So lose the two inside your autograph,
then guide our thoughts without your ``better'' half.
Wonders math imparts become so neat
when phrased with you, and pi remains off-screen.
Sine and exp both cycle to your beat.
Jive with Fourier, and forms are clean.
``Wait! Area of circles'', pi would say,
``sticks oddly to one half when tau's preferred.''
More to you then!  For write it in this way,
then links to triangles can be inferred.
Nix pi, then all within geometry
shines clean and clear, as if by poetry.""".split("\n")

DIGIT_TO_WORD = {
    '0' : "Zero",
    '1' : "One",
    '2' : "Two",
    '3' : "Three",
    '4' : "Four",
    '5' : "Five",
    '6' : "Six",
    '7' : "Seven",
    '8' : "Eight",
    '9' : "Nine",
}

FORMULAE = [
    "e^{x + \\tau i} = e^{x}",
    "&\\Leftrightarrow",
    "e^{x + 2\\pi i} = e^{x} \\\\",
    "A = \\frac{1}{2} \\tau r^2",
    "&\\Leftrightarrow",
    "A = \\pi r^2 \\\\",
    "n! \\sim \\sqrt{\\tau n}\\left(\\frac{n}{e}\\right)^n",
    "&\\Leftrightarrow",
    "n! \\sim \\sqrt{2\\pi n}\\left(\\frac{n}{e}\\right)^n \\\\",
    # "\\sum_{n = 0}^\\infty \\frac{(-1)^n}{2n+1} = \\frac{\\tau}{8}",
    # "&\\Leftrightarrow",
    # "\\sum_{n = 0}^\\infty \\frac{(-1)^n}{2n+1} = \\frac{\\pi}{4} \\\\",
]

DIGITS = list(map(str, list("62831853071795864769")))
DIGITS[1] = "." + DIGITS[1] #2->.2

BUFF = 1.0

MOVIE_PREFIX = "tau_poem/"

class Welcome(LogoGeneration):
    def construct(self):
        text = "Happy $\\tau$ Day, from 3Blue1Brown!"
        self.add(TextMobject(text).to_edge(UP))
        LogoGeneration.construct(self)

class HappyTauDayWords(Scene):
    def construct(self):
        words = TextMobject("Happy Tau Day Everybody!").scale(2)
        tau = TauCreature().move_to(2*LEFT + UP)
        pi = PiCreature().move_to(2*RIGHT + 3*DOWN)
        pi.set_color("red")
        self.add(words, tau, pi)
        self.wait()
        self.play(BlinkPiCreature(tau))
        self.play(BlinkPiCreature(pi))

class TauPoem(Scene):
    args_list = [(x,) for x in range(len(POEM_LINES))]
    @staticmethod
    def args_to_string(line_num, *ignore):
        return str(line_num)

    def __init__(self, line_num, *args, **kwargs):
        self.line_num = line_num
        self.anim_kwargs = {
            "run_time" : 4.0,
        }
        self.line_num_to_method = {
            0  : self.line0,
            1  : self.line1,
            2  : self.line2,
            3  : self.line3,
            4  : self.line4,
            5  : self.line5,
            6  : self.line6,
            7  : self.line7,
            8  : self.line8,
            9  : self.line9,
            10 : self.line10,
            11 : self.line11,
            12 : self.line12,
            13 : self.line13,
            14 : self.line14,
            15 : self.line15,
            16 : self.line16,
            17 : self.line17,
            18 : self.line18,
            19 : self.line19,
        }
        Scene.__init__(self, *args, **kwargs)

    def construct(self):
        self.add_line_and_number()
        self.line_num_to_method[self.line_num]()
        self.first_word_to_last_digit()

    def add_line_and_number(self):
        self.first_digits, new_digit, last_digits = TexMobject([
            "".join(DIGITS[:self.line_num]),
            DIGITS[self.line_num],
            "".join(DIGITS[(self.line_num+1):]),
        ]).to_edge(UP, buff=0.2).split()
        line_str = POEM_LINES[self.line_num]
        if self.line_num == 0:
            index = line_str.index("ed ")
        elif self.line_num == 10:
            index = line_str.index("ders")
        else:
            index = line_str.index(" ")
        first_word, rest_of_line = TextMobject(
            [line_str[:index], line_str[index:]]
        ).to_edge(UP).shift(BUFF*DOWN).split()
        first_word.shift(0.15*RIGHT) #Stupid
        number_word = TextMobject(DIGIT_TO_WORD[DIGITS[self.line_num][-1]])
        number_word.shift(first_word.get_center())
        number_word.shift(BUFF * UP / 2)

        kwargs = {
            "rate_func" : squish_rate_func(smooth),
        }
        self.add(first_word, rest_of_line, self.first_digits)
        self.first_word  = first_word
        self.number_word = number_word
        self.new_digit   = new_digit

    def first_word_to_last_digit(self):
        if self.line_num == 19:
            shift_val = FRAME_Y_RADIUS*DOWN
            self.new_digit.shift(shift_val)
            self.play(ApplyMethod(
                self.first_digits.shift, shift_val, run_time = 2.0
            ))
            self.wait(2)
        self.play_over_time_range(0, 2,
            Transform(
                deepcopy(self.first_word), self.number_word,
                rate_func = squish_rate_func(smooth)
            )
        )
        self.play_over_time_range(2, 4,
            Transform(
                self.number_word, self.new_digit,
                rate_func = squish_rate_func(smooth)                
            )
        )

    def line0(self):
        two, pi = TexMobject(["2", "\\pi"]).scale(2).split()
        self.add(two, pi)
        two_copy = deepcopy(two).rotate(np.pi/10).set_color("yellow")
        self.play(Transform(
            two, two_copy,
            rate_func = squish_rate_func(
                lambda t : wiggle(t),
                0.4, 0.9,
            ),
            **self.anim_kwargs
        ))

    def line1(self):
        two_pi = TexMobject(["2", "\\pi"]).scale(2)
        tau = TauCreature()
        tau.to_symbol()
        sphere = Mobject()
        sphere.interpolate(
            two_pi, 
            Sphere().set_color("yellow"),
            0.8
        )
        self.add(two_pi)
        self.wait()
        self.play(CounterclockwiseTransform(
            two_pi, sphere,
            rate_func = lambda t : 2*smooth(t/2)
        ))
        self.remove(two_pi)
        self.play(CounterclockwiseTransform(
            sphere, tau,
            rate_func = lambda t : 2*(smooth(t/2+0.5)-0.5)
        ))
        self.remove(sphere)
        self.add(tau)
        self.wait()

    def line2(self):
        tau = TauCreature()
        tau.make_sad()
        tau.mouth.points = np.array(sorted(
            tau.mouth.points, 
            lambda p0, p1 : cmp(p0[0], p1[0])
        ))
        blinked = deepcopy(tau).blink()
        for eye in blinked.eyes:
            eye.set_color("black")
        self.add(*set(tau.parts).difference(tau.white_parts))
        self.play(*[
            Transform(*eyes)
            for eyes in zip(blinked.eyes, tau.eyes)
        ])
        self.play(ShowCreation(tau.mouth))
        self.wait(2)

    def line3(self):
        tau = TauCreature().make_sad()
        pi = PiCreature()
        self.add(*tau.parts)
        self.wait()
        self.play(
            Transform(tau.leg, pi.left_leg),
            ShowCreation(pi.right_leg),
            run_time = 1.0,
        )
        self.play(*[
            Transform(*parts)
            for parts in zip(tau.white_parts, pi.white_parts)
        ])
        self.remove(*tau.parts + pi.parts)
        self.play(BlinkPiCreature(pi))

    def pi_speaking(self, text):
        pi = PiCreature()
        pi.set_color("red").give_straight_face()
        pi.shift(3*DOWN + LEFT)
        bubble = SpeechBubble().speak_from(pi)
        bubble.write(text)
        return pi, bubble

    def line4(self):
        pi, bubble = self.pi_speaking("Conventions matter \\\\ not!")
        self.add(pi)
        self.wait()
        self.play(Transform(
            Point(bubble.tip).set_color("black"),
            bubble
        ))


    def line5(self):
        pi, bubble = self.pi_speaking("""
            Great formulae cast \\\\ 
            truths transcending \\\\
            names.
        """)
        self.add(pi, bubble)

        formulae = TexMobject(FORMULAE, size = "\\small")
        formulae.scale(1.25)
        formulae.to_corner([1, -1, 0])
        self.play(FadeIn(formulae))

    def line6(self):
        bubble = ThoughtBubble()
        self.play(ApplyFunction(
            lambda p : 2 * p /  get_norm(p),
            bubble,
            rate_func = wiggle,
            run_time = 3.0,
        ))

    def line7(self):
        bubble = ThoughtBubble()
        heart = ImageMobject("heart")
        heart.scale(0.5).shift(DOWN).set_color("red")
        for mob in bubble, heart:
            mob.sort_points(get_norm)

        self.add(bubble)
        self.wait()
        self.remove(bubble)
        bubble_copy = deepcopy(bubble)
        self.play(CounterclockwiseTransform(bubble_copy, heart))
        self.wait()
        self.remove(bubble_copy)
        self.play(CounterclockwiseTransform(heart, bubble))
        self.wait()


    def line8(self):
        pi = PiCreature().give_straight_face()
        tau = TauCreature()
        two = ImageMobject("big2").scale(0.5).shift(1.6*LEFT + 0.1*DOWN)

        self.add(two, *pi.parts)
        self.wait()
        self.play(
            Transform(pi.left_leg, tau.leg),
            Transform(
                pi.right_leg, 
                Point(pi.right_leg.points[0,:]).set_color("black")
            ),
            Transform(pi.mouth, tau.mouth),
            CounterclockwiseTransform(
                two, 
                Dot(two.get_center()).set_color("black")
            )
        )

    def line9(self):
        tau = TauCreature()
        pi = PiCreature().set_color("red").give_straight_face()
        pi.scale(0.2).move_to(tau.arm.points[-1,:])
        point = Point(pi.get_center()).set_color("black")
        vanish_local = 3*(LEFT + UP)
        new_pi = deepcopy(pi)
        new_pi.scale(0.01)
        new_pi.rotate(np.pi)
        new_pi.shift(vanish_local)
        Mobject.set_color(new_pi, "black")

        self.add(tau)
        self.wait()
        self.play(Transform(point, pi))
        self.remove(point)
        self.add(pi)
        self.play(WaveArm(tau),Transform(pi, new_pi))

    def line10(self):
        formulae = TexMobject(FORMULAE, "\\small")
        formulae.scale(1.5).to_edge(DOWN)
        self.add(formulae)

    def line11(self):
        formulae = TexMobject(FORMULAE, "\\small")
        formulae.scale(1.5).to_edge(DOWN)
        formulae = formulae.split()
        f_copy = deepcopy(formulae)
        for mob, count in zip(f_copy, it.count()):
            if count%3 == 0:
                mob.to_edge(LEFT).shift(RIGHT*(FRAME_X_RADIUS-1))
            else:
                mob.shift(FRAME_WIDTH*RIGHT)
        self.play(*[
            Transform(*mobs, run_time = 2.0)
            for mobs in zip(formulae, f_copy)
        ])

    def line12(self):
        interval_size = 0.5
        axes_center = FRAME_X_RADIUS*LEFT/2
        grid_center = FRAME_X_RADIUS*RIGHT/2
        radius = FRAME_X_RADIUS / 2.0
        axes = Axes(
            radius = radius,
            interval_size = interval_size
        )
        axes.shift(axes_center)
        def sine_curve(t):
            t += 1
            result = np.array((-np.pi*t, np.sin(np.pi*t), 0))
            result *= interval_size
            result += axes_center
            return result
        sine = ParametricFunction(sine_curve)
        sine_period = Line(
            axes_center,
            axes_center + 2*np.pi*interval_size*RIGHT
        )
        grid = Grid(radius = radius).shift(grid_center)
        circle = Circle().scale(interval_size).shift(grid_center)
        grid.add(TexMobject("e^{ix}").shift(grid_center+UP+RIGHT))
        circle.set_color("white")
        tau_line = Line(
            *[np.pi*interval_size*vect for vect in (LEFT, RIGHT)],
            density = 5*DEFAULT_POINT_DENSITY_1D
        )
        tau_line.set_color("red")
        tau = TexMobject("\\tau")
        tau.shift(tau_line.get_center() + 0.5*UP)

        self.add(axes, grid)
        self.play(
            TransformAnimations(
                ShowCreation(sine),
                ShowCreation(deepcopy(sine).shift(2*np.pi*interval_size*RIGHT)),
                run_time = 2.0,
                rate_func = smooth
            ),
            ShowCreation(circle)
        )
        self.play(
            CounterclockwiseTransform(sine_period, tau_line),
            CounterclockwiseTransform(circle, deepcopy(tau_line)),
            FadeOut(axes),
            FadeOut(grid),
            FadeOut(sine),
            FadeIn(tau),            
        )
        self.wait()


    def line13(self):
        formula = form_start, two_pi, form_end = TexMobject([
            "\\hat{f^{(n)}}(\\xi) = (",
            "2\\pi",
            "i\\xi)^n \\hat{f}(\\xi)"
        ]).shift(DOWN).split()
        tau = TauCreature().center()
        tau.scale(two_pi.get_width()/tau.get_width())
        tau.shift(two_pi.get_center()+0.2*UP)
        tau.rewire_part_attributes()

        self.add(*formula)
        self.wait()
        self.play(CounterclockwiseTransform(two_pi, tau))
        self.remove(two_pi)
        self.play(BlinkPiCreature(tau))
        self.wait()

    def line14(self):
        pi, bubble = self.pi_speaking(
            "Wait! Area \\\\ of circles"
        )
        self.add(pi)
        self.play(
            Transform(Point(bubble.tip).set_color("black"), bubble)
        )

    def line15(self):
        pi, bubble = self.pi_speaking(
            "sticks oddly \\\\ to one half when \\\\ tau's preferred."
        )
        formula = form_start, half, form_end = TexMobject([
            "A = ",
            "\\frac{1}{2}",
            "\\tau r^2"
        ]).split()

        self.add(pi, bubble, *formula)
        self.wait(2)
        self.play(ApplyMethod(half.set_color, "yellow"))

    def line16(self):
        self.add(TexMobject(
            "\\frac{1}{2}\\tau r^2"
        ).scale(2).shift(DOWN))

    def line17(self):
        circle = Dot(
            radius = 1, 
            density = 4*DEFAULT_POINT_DENSITY_1D
        )
        blue_rgb = np.array(Color("blue").get_rgb())
        white_rgb = np.ones(3)
        circle.rgbas = np.array([
            alpha * blue_rgb + (1 - alpha) * white_rgb
            for alpha in np.arange(0, 1, 1.0/len(circle.rgbas))
        ])
        for index in range(circle.points.shape[0]):
            circle.rgbas
        def trianglify(xxx_todo_changeme):
            (x, y, z) = xxx_todo_changeme
            norm = get_norm((x, y, z))
            comp = complex(x, y)*complex(0, 1)
            return (
                norm * np.log(comp).imag,
                -norm,
                0
            )
        tau_r = TexMobject("\\tau r").shift(1.3*DOWN)
        r = TexMobject("r").shift(0.2*RIGHT + 0.7*DOWN)
        lines = [
            Line(DOWN+np.pi*LEFT, DOWN+np.pi*RIGHT),
            Line(ORIGIN, DOWN)
        ]
        for line in lines:
            line.set_color("red")

        self.play(ApplyFunction(trianglify, circle, run_time = 2.0))
        self.add(tau_r, r)
        self.play(*[
            ShowCreation(line, run_time = 1.0)
            for line in lines
        ])
        self.wait()

    def line18(self):
        tau = TauCreature()
        tau.shift_eyes()
        tau.move_to(DOWN)
        pi = PiCreature()
        pi.set_color("red")
        pi.move_to(DOWN + 3*LEFT)
        mad_tau = deepcopy(tau).make_mean()
        mad_tau.arm.wag(0.5*UP, LEFT, 2.0)
        sad_pi  = deepcopy(pi).shift_eyes().make_sad()
        blinked_tau = deepcopy(tau).blink()
        blinked_pi  = deepcopy(pi).blink()

        self.add(*pi.parts + tau.parts)
        self.wait(0.8)
        self.play(*[
            Transform(*eyes, run_time = 0.2, rate_func = rush_into)
            for eyes in [
                (tau.left_eye, blinked_tau.left_eye),
                (tau.right_eye, blinked_tau.right_eye),
            ]
        ])
        self.remove(tau.left_eye, tau.right_eye)
        self.play(*[
            Transform(*eyes, run_time = 0.2, rate_func = rush_from)
            for eyes in [
                (blinked_tau.left_eye, mad_tau.left_eye),
                (blinked_tau.right_eye, mad_tau.right_eye),
            ]
        ])
        self.remove(blinked_tau.left_eye, blinked_tau.right_eye)
        self.add(mad_tau.left_eye, mad_tau.right_eye)
        self.play(
            Transform(tau.arm, mad_tau.arm),
            Transform(tau.mouth, mad_tau.mouth),
            run_time = 0.5
        )
        self.remove(*tau.parts + blinked_tau.parts)
        self.add(*mad_tau.parts)

        self.play(*[
            Transform(*eyes, run_time = 0.2, rate_func = rush_into)
            for eyes in [
                (pi.left_eye, blinked_pi.left_eye),
                (pi.right_eye, blinked_pi.right_eye),
            ]
        ])
        self.remove(pi.left_eye, pi.right_eye)
        self.play(*[
            Transform(*eyes, run_time = 0.2, rate_func = rush_from)
            for eyes in [
                (blinked_pi.left_eye, sad_pi.left_eye),
                (blinked_pi.right_eye, sad_pi.right_eye),
            ]
        ] + [
            Transform(pi.mouth, sad_pi.mouth, run_time = 0.2)
        ])
        self.remove(*blinked_pi.parts + pi.parts + sad_pi.parts)
        self.play(
            WalkPiCreature(sad_pi, DOWN+4*LEFT),
            run_time = 1.0
        )
        self.wait()

    def line19(self):
        pass


if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)













