from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import VMobject

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.number_line import *
from topics.combinatorics import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from mobject.vectorized_mobject import *

from eola.utils import *

import random


class Physicist(PiCreature):
    CONFIG = {
        "color" : PINK,
    }

class ComputerScientist(PiCreature):
    CONFIG = {
        "color" : PURPLE_E,
        "flip_at_start" : True,
    }    

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject(
            "``The introduction of numbers as \\\\ coordinates is an act of violence.''",
        )
        words.to_edge(UP)    
        for mob in words.submobjects[27:27+11]:
            mob.highlight(GREEN)
        author = TextMobject("-Hermann Weyl")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.dither(1)
        self.play(Write(author, run_time = 4))
        self.dither()

class IntroVector(Scene):
    def construct(self):
        plane = NumberPlane()
        labels = plane.get_coordinate_labels()
        vector = Vector(RIGHT+2*UP, color = YELLOW)
        coordinates = vector_coordinate_label(vector)

        self.play(ShowCreation(
            plane, 
            submobject_mode = "lagged_start",
            run_time = 3
        ))
        self.play(ShowCreation(
            vector,
            submobject_mode = "one_at_a_time"
        ))
        self.play(Write(VMobject(*labels)), Write(coordinates))
        self.dither()


class DifferentConceptions(Scene):
    def construct(self):
        physy = Physicist()
        mathy = Mathematician(mode = "pondering")        
        compy = ComputerScientist()
        people = [physy, compy, mathy]
        physy.name = TextMobject("Physics student").to_corner(DOWN+LEFT)
        compy.name = TextMobject("CS student").to_corner(DOWN+RIGHT)
        mathy.name = TextMobject("Mathematician").to_edge(DOWN)
        names = VMobject(physy.name, mathy.name, compy.name)
        names.arrange_submobjects(RIGHT, buff = 1)
        names.to_corner(DOWN+LEFT)
        for pi in people:
            pi.next_to(pi.name, UP)
            self.add(pi)

        for pi in people:
            self.play(Write(pi.name), run_time = 1)
        self.preview_conceptions(people)
        self.physics_conception(people)
        self.cs_conception(people)
        self.handle_mathy(people)


    def preview_conceptions(self, people):
        arrow = Vector(2*RIGHT+ UP)
        array = matrix_to_mobject([[2], [1]])
        tex = TextMobject("""
            Set $V$ with operations \\\\
            $a : V \\times V \\to V$ and \\\\
            $s : \\mathds{R} \\times V \\to V$ such that...
        """)
        physy, compy, mathy = people
        physy.bubble = physy.get_bubble("speech")
        compy.bubble = compy.get_bubble("speech")
        mathy.bubble = mathy.get_bubble(width = 4)

        for pi, sym in zip(people, [arrow, array, tex]):
            pi.bubble.set_fill(BLACK, opacity = 1.0)
            pi.bubble.add_content(sym)
            self.play(FadeIn(pi.bubble))
            self.dither()
        for pi in people:
            self.remove(pi.bubble)


    def physics_conception(self, people):
        pass

    def cs_conception(self, people):
        pass

    def handle_mathy(self, people):
        pass






















