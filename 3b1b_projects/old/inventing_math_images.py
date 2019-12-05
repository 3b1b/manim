#!/usr/bin/env python


import numpy as np
import itertools as it
from copy import deepcopy
import sys

from manimlib.imports import *
from script_wrapper import command_line_create_scene
from .inventing_math import divergent_sum, draw_you



class SimpleText(Scene):
    args_list = [
         ("Build the foundation of what we know",),
         ("What would that feel like?",),
         ("Arbitrary decisions hinder generality",),
         ("Section 1: Discovering and Defining Infinite Sums",),
         ("Section 2: Seeking Generality",),
         ("Section 3: Redefining Distance",),
         ("``Approach''?",),
         ("Rigor would dictate you ignore these",),
         ("dist($A$, $B$) = dist($A+x$, $B+x$) \\quad for all $x$",),
         ("How does a useful distance function differ from a random function?",),
         ("Pause now, if you like, and see if you can invent your own distance function from this.",),
         ("$p$-adic metrics \\\\ ($p$ is any prime number)",),
         ("This is not meant to match the history of discoveries",),
    ]
    @staticmethod
    def args_to_string(text):
        return initials([c for c in text if c in string.letters + " "])

    def construct(self, text):
        self.add(TextMobject(text))


class SimpleTex(Scene):
    args_list = [
        (
            "\\frac{9}{10}+\\frac{9}{100}+\\frac{9}{1000}+\\cdots = 1",
            "SumOf9s"
        ),
        (
            "0 < p < 1",
            "PBetween0And1"
        ),
    ]
    @staticmethod
    def args_to_string(expression, words):
        return words

    def construct(self, expression, words):
        self.add(TexMobject(expression))


class OneMinusOnePoem(Scene):
    def construct(self):
        verse1 = TextMobject("""
            \\begin{flushleft}
            When one takes one from one  \\\\
            plus one from one plus one \\\\
            and on and on but ends  \\\\
            anon then starts again, \\\\
            then some sums sum to one, \\\\
            to zero other ones. \\\\
            One wonders who'd have won \\\\
            had stopping not been done; \\\\
            had he summed every bit \\\\
            until the infinite. \\\\
            \\end{flushleft}
        """).scale(0.5).to_corner(UP+LEFT)
        verse2 = TextMobject("""
            \\begin{flushleft}
            Lest you should think that such \\\\
            less well-known sums are much \\\\
            ado about nonsense \\\\
            I do give these two cents: \\\\
            The universe has got \\\\
            an answer which is not \\\\
            what most would first surmise, \\\\
            it is a compromise, \\\\
            and though it seems a laugh \\\\
            the universe gives ``half''. \\\\
            \\end{flushleft}
        """).scale(0.5).to_corner(DOWN+LEFT)
        equation = TexMobject(
            "1-1+1-1+\\cdots = \\frac{1}{2}"
        )
        self.add(verse1, verse2, equation)
        
class DivergentSum(Scene):
    def construct(self):
        self.add(divergent_sum().scale(0.75))


class PowersOfTwoSmall(Scene):
    def construct(self):
        you, bubble = draw_you(with_bubble=True)
        bubble.write(
            "Is there any way in which apparently \
            large powers of two can be considered small?"
        )
        self.add(you, bubble, bubble.content)


class FinalSlide(Scene):
    def construct(self):
        self.add(TextMobject("""
            \\begin{flushleft}
            Needless to say, what I said here only scratches the 
            surface of the tip of the iceberg of the p-adic metric.  
            What is this new form of number I referred to?
            Why were distances in the 2-adic metric all powers of 
            $\\frac{1}{2}$ and not some other base?
            Why does it only work for prime numbers? \\\\
            \\quad \\\\
            I highly encourage anyone who has not seen p-adic numbers
            to look them up and learn more, but even more edifying than
            looking them up will be to explore this idea for yourself directly.
            What properties make a distance function useful, and why?
            What do I mean by ``useful''?  Useful for what purpose?
            Can you find infinite sums or sequences which feel like
            they should converge in the 2-adic metric, but don't converge 
            to a rational number? Go on!  Search!  Invent!
            \\end{flushleft}
        """, size = "\\small"))




