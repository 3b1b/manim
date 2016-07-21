from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import VMobject

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.number_line import *
from topics.numerals import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from mobject.vectorized_mobject import *

from eola.matrix import *
from eola.two_d_space import *

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject([
            "Unfortunately, no one can be told what the",
            "Matrix",
            "is. You have to",
            "see it for yourself.",
        ])
        words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        words.split()[1].highlight(GREEN)
        words.split()[3].highlight(GREEN)
        author = TextMobject("-Morpheus")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)
        comment = TextMobject("""
            (Surprisingly apt words on the importance 
            of understanding matrix operations visually.)
        """)
        comment.scale(0.7)
        comment.next_to(author, DOWN, buff = 1)

        self.play(FadeIn(words))
        self.dither(3)
        self.play(Write(author, run_time = 3))
        self.dither()
        self.play(Write(comment))
        self.dither()


class Introduction(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Matrices as linear transformations")
        title.to_edge(UP)
        title.highlight(YELLOW)
        self.add(title)
        self.setup()
        self.teacher_says("""
            Listen up folks, this one is
            particularly important
        """, height = 3)
        self.random_blink(2)
        self.teacher_says("We'll start by just watching", height = 3)
        self.random_blink()
        self.teacher_thinks(VMobject())
        everything = VMobject(*self.get_mobjects())
        def spread_out(p):
            p = p + 3*DOWN
            return (SPACE_WIDTH+SPACE_HEIGHT)*p/np.linalg.norm(p)
        self.play(ApplyPointwiseFunction(spread_out, everything))


class ShowGridCreation(Scene):
    def construct(self):
        plane = NumberPlane()
        coords = plane.get_coordinate_labels()
        self.play(ShowCreation(plane))
        self.play(Write(coords, run_time = 5))
        self.dither()

class SimpleLinearTransformationScene(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False
    }
    def construct(self):
        self.setup()




























