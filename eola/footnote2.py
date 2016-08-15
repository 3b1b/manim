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
            "``On this quiz, I asked you to find the determinant of a",
            "2x3 matrix.",
            "Some of you, to my great amusement, actually tried to do this.''" 
        )
        words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        words[1].highlight(GREEN)
        author = TextMobject("-(Via mathprofessorquotes.com, no name listed)")
        author.highlight(YELLOW)
        author.scale(0.7)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.dither(2)
        self.play(Write(author, run_time = 3))
        self.dither()

class AnotherFootnote(TeacherStudentsScene):
    def construct(self):
        self.teacher.look(LEFT)
        self.teacher_says(
            "More footnotes!",
            pi_creature_target_mode = "surprised",
            run_time = 1
        )
        self.random_blink(2)

class ColumnsRepresentBasisVectors(Scene):
    def construct(self):
        matrix = Matrix([[3, 1], [4, 1], [5, 9]])
        i_hat_words, j_hat_words = [
            TextMobject("Where $\\hat{\\%smath}$ lands"%char)
            for char in "i", "j"
        ]
        i_hat_words.highlight(X_COLOR)
        i_hat_words.next_to(ORIGIN, LEFT).to_edge(UP)
        j_hat_words.highlight(Y_COLOR)
        j_hat_words.next_to(ORIGIN, RIGHT).to_edge(UP)

        self.add(matrix)
        self.dither()
        for i, words in enumerate([i_hat_words, j_hat_words]):
            arrow = Arrow(
                words.get_bottom(),
                matrix.get_mob_matrix()[0,i].get_top(),
                color = words.get_color()
            )
            self.play(
                Write(words, run_time = 1),
                ShowCreation(arrow),
                *[
                    ApplyMethod(m.highlight, words.get_color())
                    for m in matrix.get_mob_matrix()[:,i]
                ]
            )
        self.dither()











