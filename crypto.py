from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from topics.probability import *
from topics.complex_numbers import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

class AskQuestion(Scene):
    CONFIG = {
        "time_per_char" : 0.06,
    }
    def construct(self):
        strings = [
            "What", "does", "it", "mean   ", "to", 
            "have    ", "a", "Bitcoin?"
        ]
        question = TextMobject(*strings)
        question.highlight_by_tex("have", YELLOW)
        self.dither()
        for word, part in zip(strings, question):
            n_chars = len(word.strip())
            n_spaces = len(word) - n_chars
            self.play(
                LaggedStart(FadeIn, part),
                run_time = self.time_per_char * len(word),
                rate_func = squish_rate_func(smooth, 0, 0.5)
            )
            self.dither(self.time_per_char*n_spaces)
        self.dither(2)



















































