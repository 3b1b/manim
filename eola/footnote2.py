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

from ka_playgrounds.circuits import Resistor, Source, LongResistor

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject(
            "On this quiz, I asked you to find the determinant of a",
            "2x3 matrix.",
            "Some of you, to my great amusement, actually tried to do this." 
        )
        words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        words[1].highlight(GREEN)
        author = TextMobject("-(Linear algebra professor whose name I could not track down)")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.dither(2)
        self.play(Write(author, run_time = 3))
        self.dither()