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
            "\\small Calvin:",
            "You know, I don't think math is a science, I think it's a religion.",
            "\\\\Hobbes:",
            "A religion?",
            "\\\\Calvin:" ,
            "Yeah. All these equations are like miracles."
            "You take two numbers and when you add them, "
            "they magically become one NEW number!"
        )
        words.scale_to_fit_width(2*SPACE_WIDTH - 1)
        words.to_edge(UP)
        words[0].highlight(YELLOW)
        words[2].highlight("#fd9c2b")
        words[4].highlight(YELLOW)

        self.play(FadeIn(words))
        self.dither(2)

class TraditionalOrdering(RandolphScene):
    def construct(self):
        title = TextMobject("Traditional ordering:")
        title.highlight(YELLOW).to_edge(UP)
        topics = VMobject(*map(TextMobject, [
            "Topic 1: Vectors",
            "Topic 2: Dot product",
            "\\vdots",
            "(everything else)",
            "\\vdots",
        ]))
        topics.arrange_submobjects(DOWN)
        topics.next_to(title, DOWN)

        self.play(
            Write(title),
            FadeIn(topics, submobject_mode = "lagged_start")
        )
        self.play(topics[1].highlight, PINK)
        self.dither()

class ThisSeriesOrdering(RandolphScene):
    def construct(self):
        pass