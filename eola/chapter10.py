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
        words = TextMobject(
            "``Last time, I asked: `What does",
            "mathematics", 
            """ mean to you?', and some people answered: `The 
            manipulation of numbers, the manipulation of structures.' 
            And if I had asked what""",
            "music",
            """means to you, would you have answered: `The 
            manipulation of notes?' '' """, 
            enforce_new_line_structure = False
        )
        words.highlight_by_tex("mathematics", BLUE)
        words.highlight_by_tex("music", BLUE)
        words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        author = TextMobject("-Serge Lang")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(Write(words, run_time = 8))
        self.dither(2)
        self.play(Write(author, run_time = 3))
        self.dither(2)

class NewSceneName(Scene):
    def construct(self):
        pass




































