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
from eola.chapter8 import get_vect_tex, CrossProductRightHandRule
from eola.chapter8 import U_COLOR, V_COLOR, W_COLOR, P_COLOR


class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject(
            "From [Grothendieck], I have also learned not",
            "to take glory in the ", 
            "difficulty of a proof:", 
            "difficulty means we have not understood.",
            "The idea is to be able to ",
            "paint a landscape",
            "in which the proof is obvious.",
            arg_separator = " "
        )
        words.highlight_by_tex("difficulty of a proof:", RED)
        words.highlight_by_tex("paint a landscape", GREEN)
        words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        author = TextMobject("-Pierre Deligne")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.dither(4)
        self.play(Write(author, run_time = 3))
        self.dither()

class BruteForceVerification(Scene):
    def construct(self):
        v = Matrix(["v_1", "v_2", "v_3"])
        w = Matrix(["w_1", "w_2", "w_3"])
        v1, v2, v3 = v.get_entries()
        w1, w2, w3 = w.get_entries()
        v.highlight(V_COLOR)
        w.highlight(W_COLOR)
        def get_term(e1, e2, e3, e4):
            group = Group(
                e1.copy(), e2.copy(), 
                TexMobject("-"),
                e3.copy(), e4.copy(),
            )
            group.arrange_submobjects()
            return group
        cross = Matrix(list(it.starmap(get_term, [
            (v2, w3, v3, w2),
            (v3, w1, v1, w3),
            (v2, w3, v3, w2),
        ])))
        cross_product = Group(
            v.copy(), TexMobject("\\times"), w.copy(),
            TexMobject("="), cross.copy()
        )
        cross_product.arrange_submobjects()
        cross_product.scale(0.75)

        formula_word = TextMobject("Numerical formula")
        computation_words = TextMobject("""
            Facts you could (painfully)
            verify computationally
        """)
        computation_words.scale(0.75)
        h_line = Line(LEFT, RIGHT).scale(SPACE_WIDTH)
        v_line = Line(UP, DOWN).scale(SPACE_HEIGHT)
        computation_words.to_edge(UP, buff = MED_BUFF/2)
        h_line.next_to(computation_words, DOWN)
        formula_word.next_to(h_line, UP, buff = MED_BUFF)
        computation_words.shift(SPACE_WIDTH*RIGHT/2)
        formula_word.shift(SPACE_WIDTH*LEFT/2)

        cross_product.next_to(formula_word, DOWN, buff = LARGE_BUFF)

        self.add(formula_word, computation_words)
        self.play(
            ShowCreation(h_line),
            ShowCreation(v_line),
            Write(cross_product)
        )

        v_tex, w_tex = get_vect_tex(*"vw")
        v_dot, w_dot = [
            TexMobject(
                tex, "\\cdot", 
                "(", v_tex, "\\times", w_tex, ")",
                "= 0"
            )
            for tex in v_tex, w_tex
        ]
        theta_def = TexMobject(
            "\\theta", 
            "= \\cos^{-1} \\big(", v_tex, "\\cdot", w_tex, "/",
            "(||", v_tex, "||", "\\cdot", "||", w_tex, "||)", "\\big)"
        )

        length_check = TexMobject(
            "||", "(", v_tex, "\\times", w_tex, ")", "|| = ",
            "(||", v_tex, "||)",
            "(||", w_tex, "||)",
            "\\sin(", "\\theta", ")"
        )
        last_point = h_line.get_center()+SPACE_WIDTH*RIGHT/2
        max_width = SPACE_WIDTH-1
        for mob in v_dot, w_dot, theta_def, length_check:
            mob.highlight_by_tex(v_tex, V_COLOR)
            mob.highlight_by_tex(w_tex, W_COLOR)
            mob.highlight_by_tex("\\theta", GREEN)
            mob.next_to(last_point, DOWN, buff = MED_BUFF)
            if mob.get_width() > max_width:
                mob.scale_to_fit_width(max_width)
            last_point = mob
            self.play(FadeIn(mob))
        self.dither()

class ButWeCanDoBetter(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("But we can do \\\\ better than that")
        self.change_student_modes(*["happy"]*3)
        self.random_blink(3)

class Prerequisites(Scene):
    def construct(self):
        title = TextMobject("Prerequisites")
        title.to_edge(UP)
        title.highlight(YELLOW)

        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.scale_to_fit_width(SPACE_WIDTH - 1)
        left_rect, right_rect = [
            rect.copy().shift(DOWN/2).to_edge(edge)
            for edge in LEFT, RIGHT
        ]
        chapter5 = TextMobject("""
            \\centering 
            Chapter 5 
            Determinants
        """)
        chapter7 = TextMobject("""
            \\centering
            Chapter 7: 
            Dot products and duality
        """)

        self.add(title)
        for chapter, rect in (chapter5, left_rect), (chapter7, right_rect):
            if chapter.get_width() > rect.get_width():
                chapter.scale_to_fit_width(rect.get_width())
            chapter.next_to(rect, UP)
            self.play(
                Write(chapter5), 
                ShowCreation(left_rect)
            )
        self.play(
            Write(chapter7),
            ShowCreation(right_rect)
        )
        self.dither()

class DualityReview(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("Quick", "duality", "review")
        words[1].gradient_highlight(BLUE, YELLOW)
        self.teacher_says(words, pi_creature_target_mode = "surprised")
        self.change_student_modes("pondering")
        self.random_blink(2)

class DotProductToTransformSymbol(Scene):
    CONFIG = {
        "vect_coords" : [4, 1]
    }
    def construct(self):
        matrix = Matrix([self.vect_coords])
        vector = Matrix(self.vect_coords)
        matrix.highlight_columns(X_COLOR, Y_COLOR)
        vector.highlight_columns(YELLOW)
        _input = Matrix(["x", "y"])
        _input.get_entries().gradient_highlight(X_COLOR, Y_COLOR)
        left_input, right_input = [_input.copy() for x in range(2)]
        dot, equals = map(TexMobject, ["\\cdot", "="])
        equation = Group(
            vector, dot, left_input, equals,
            matrix, right_input
        )
        equation.arrange_submobjects()
        left_brace = Brace(Group(vector, left_input))
        right_brace = Brace(matrix, UP)
        left_words = left_brace.get_text("Dot product")
        right_words = right_brace.get_text("Transform")
        right_words.scale_to_fit_width(right_brace.get_width())

        self.play(*map(FadeIn, (matrix, right_input)))
        self.play(
            GrowFromCenter(right_brace),
            Write(right_words, run_time = 1)
        )
        self.dither()
        self.play(
            Write(equals),
            Write(dot),
            Transform(matrix.copy(), vector),
            Transform(right_input.copy(), left_input)
        )
        self.play(
            GrowFromCenter(left_brace),
            Write(left_words, run_time = 1)
        )
        self.dither()


























