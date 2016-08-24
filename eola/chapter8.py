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
from eola.chapter5 import get_det_text


V_COLOR = RED
U_COLOR = ORANGE
W_COLOR = MAROON_B

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject(
            "To ask the",
            "right question\\\\",
            "is harder than to answer it." 
        )
        words.to_edge(UP)
        words[1].highlight(BLUE)
        author = TextMobject("-Georg Cantor")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.dither(2)
        self.play(Write(author, run_time = 3))
        self.dither()

class CrossAndDualWords(Scene):
    def construct(self):
        v_tex, u_tex, w_tex = [
            "\\vec{\\textbf{%s}}"%s
            for s in "vuw"
        ]
        vector_word = TextMobject("Vector:")
        transform_word = TextMobject("Dual transform:")

        cross = TexMobject(
            v_tex, "=", u_tex, "\\times", w_tex
        )
        for tex, color in zip([v_tex, u_tex, w_tex], [V_COLOR, U_COLOR, W_COLOR]):
            cross.highlight_by_tex(tex, color)
        input_array_tex = matrix_to_tex_string(["x", "y", "z"])
        func = TexMobject("f\\left(%s\\right) = "%input_array_tex)
        matrix = Matrix(np.array([
            ["x", "y", "z"],
            ["u_1", "u_2", "u_3"],
            ["w_1", "w_2", "w_3"],
        ]).T)
        matrix.highlight_columns(WHITE, U_COLOR, W_COLOR)
        det_text = get_det_text(matrix)
        det_text.add(matrix)
        equals_dot = TexMobject(
            "= %s \\cdot"%input_array_tex, v_tex
        )
        equals_dot.highlight_by_tex(v_tex, V_COLOR)
        transform = Group(func, det_text)
        transform.arrange_submobjects()

        vector_word.next_to(transform_word, UP, buff = LARGE_BUFF, aligned_edge = LEFT)
        cross.next_to(vector_word, buff = MED_BUFF)
        transform.next_to(transform_word, buff = MED_BUFF)
        equals_dot.next_to(det_text, DOWN, aligned_edge = LEFT)

        self.add_mobjects_among(locals().values())
        self.show_frame()













