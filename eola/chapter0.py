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

from eola.utils import *

EXAMPLE_TRANFORM = [[0, 1], [-1, 1]]
TRANFORMED_VECTOR = [[1], [2]]

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject(
            """
            ``There is hardly any theory which is more elementary 
            than linear algebra, in spite of the fact that generations 
            of professors and textbook writers have obscured its 
            simplicity by preposterous calculations with matrices.''
            """, 
            organize_left_to_right = False
        )
        words.scale_to_fit_width(2*(SPACE_WIDTH-1))
        words.to_edge(UP)        
        for mob in words.submobjects[48:49+13]:
            mob.highlight(GREEN)
        words.show()
        author = TextMobject("-Hermann Weyl")
        author.highlight(YELLOW)
        author.next_to(words, DOWN)

        self.play(Write(words))
        self.dither()
        self.play(FadeIn(author))
        self.dither()


class AboutLinearAlgebra(Scene):
    def construct(self):
        self.show_dependencies()
        self.linalg_is_confusing()
        self.ask_questions()

    def show_dependencies(self):
        linalg = TextMobject("Linear Algebra")
        subjects = map(TextMobject, [
            "Computer science",
            "Physics",
            "Electrical engineering",
            "Mechanical engineering",
            "Statistics",
            "\\vdots"
        ])
        prev = subjects[0]
        for subject in subjects[1:]:
            subject.next_to(prev, DOWN, aligned_edge = LEFT)
            prev = subject
        all_subs = VMobject(*subjects)
        linalg.to_edge(LEFT)
        all_subs.next_to(linalg, RIGHT, buff = 2)
        arrows = VMobject(*[
            Arrow(linalg, sub)
            for sub in subjects
        ])

        self.play(Write(linalg, run_time = 1))
        self.dither()
        self.play(
            ShowCreation(arrows, submobject_mode = "lagged_start"),
            FadeIn(all_subs),
            run_time = 2
        )
        self.dither()
        self.linalg = linalg

    def linalg_is_confusing(self):
        linalg = self.linalg
        all_else = list(self.mobjects)
        all_else.remove(linalg)
        randy = Randolph()
        randy.to_corner()
        bubble = randy.get_bubble(width = 10)
        new_linalg = bubble.position_mobject_inside(linalg.copy())

        self.play(*map(FadeOut, all_else))
        self.remove(*all_else)
        self.play(
            Transform(linalg, new_linalg),
            Write(bubble),
            FadeIn(randy)
        )
        self.play(ApplyMethod(randy.change_mode, "confused"))
        self.dither()
        self.play(Blink(randy))
        self.play(FadeOut(linalg))
        self.remove(linalg)

        self.randy, self.bubble = randy, bubble

    def ask_questions(self):
        randy, bubble = self.randy, self.bubble
        matrix_multiplication = TexMobject("""
            \\left[
                \\begin{array}{cc}
                    a & b \\\\
                    c & d
                \\end{array}
            \\right]
            \\left[
                \\begin{array}{cc}
                    e & f \\\\
                    g & h
                \\end{array}
            \\right]
            = 
            \\left[
                \\begin{array}{cc}
                    ae + bg & af + bh \\\\
                    ce + dg & cf + dh
                \\end{array}
            \\right]
        """)

        cross = TexMobject("\\vec{v} \\times \\vec{w}")
        left_right_arrow = DoubleArrow(Point(LEFT), Point(RIGHT))
        det = TextMobject("Det")
        q_mark = TextMobject("?")
        left_right_arrow.next_to(cross)
        det.next_to(left_right_arrow)
        q_mark.next_to(left_right_arrow, UP)
        cross_question = VMobject(cross, left_right_arrow, q_mark, det)
        cross_question.get_center = lambda : left_right_arrow.get_center()

        eigen_q = TextMobject("Eigen?")

        for mob in matrix_multiplication, cross_question, eigen_q:
            bubble.position_mobject_inside(mob)
            self.play(FadeIn(mob))
            if randy.mode is not "pondering":
                self.play(ApplyMethod(randy.change_mode, "pondering"))
                self.dither()
            else:
                self.dither(2)
            self.remove(mob)



class NumericVsGeometric(Scene):
    def construct(self):
        self.setup()
        self.specifics_concepts()
        self.clear_way_for_geometric()
        self.list_geometric_benefits()

    def setup(self):
        numeric = TextMobject("Numeric operations")
        geometric = TextMobject("Geometric intuition")
        for mob in numeric, geometric:
            mob.to_corner(UP+LEFT)
        geometric.shift(SPACE_WIDTH*RIGHT)
        hline = Line(SPACE_WIDTH*LEFT, SPACE_WIDTH*RIGHT)
        hline.next_to(numeric, DOWN)
        hline.to_edge(LEFT, buff = 0)
        vline = Line(SPACE_HEIGHT*UP, SPACE_HEIGHT*DOWN)
        for mob in hline, vline:
            mob.highlight(GREEN)

        self.play(ShowCreation(VMobject(hline, vline)))
        digest_locals(self)

    def specifics_concepts(self):
        matrix_vector_product = TexMobject(" ".join([
            matrix_to_tex_string(EXAMPLE_TRANFORM),
            matrix_to_tex_string(TRANFORMED_VECTOR),
            "&=",
            matrix_to_tex_string([
                ["1 \\cdot 1 + 0 \\cdot 2"], 
                ["1 \\cdot 1 + (-1)\\cdot 2"]
            ]),
            "\\\\ &=",
            matrix_to_tex_string([[1], [-1]]),
        ]))
        matrix_vector_product.scale_to_fit_width(SPACE_WIDTH-0.5)
        matrix_vector_product.next_to(self.vline, LEFT)

        self.play(
            Write(self.numeric),
            FadeIn(matrix_vector_product),
            run_time = 2
        )
        self.dither()
        self.play(Write(self.geometric, run_time = 2))
        ### Paste in linear transformation
        self.dither()
        digest_locals(self)

    def clear_way_for_geometric(self):
        new_line = Line(SPACE_HEIGHT*LEFT, SPACE_HEIGHT*RIGHT)
        new_line.shift((SPACE_HEIGHT+1)*DOWN)
        self.play(
            Transform(self.vline, new_line),
            Transform(self.hline, new_line),
            ApplyMethod(self.numeric.shift, (2*SPACE_HEIGHT+1)*DOWN),
            ApplyMethod(
                self.matrix_vector_product.shift, 
                (2*SPACE_HEIGHT+1)*DOWN
            ),
            ApplyMethod(self.geometric.to_edge, LEFT)
        )

    def list_geometric_benefits(self):
        follow_words = TextMobject("is helpful for \\dots")
        follow_words.next_to(self.geometric)
        #Ugly hack
        diff = follow_words.submobjects[0].get_bottom()[1] - \
             self.geometric.submobjects[0].get_bottom()[1]
        follow_words.shift(diff*DOWN)
        randys = [
            Randolph(mode = "speaking"),
            Randolph(mode = "surprised"),
            Randolph(mode = "pondering")
        ]
        bulb = SVGMobject("light_bulb")
        bulb.scale_to_fit_height(1)
        bulb.highlight(YELLOW)
        thoughts = [
            matrix_to_mobject(EXAMPLE_TRANFORM),
            bulb,
            TextMobject("So therefore...").scale(0.5)
        ]

        self.play(Write(follow_words, run_time = 1.5))
        curr_randy = None
        for randy, thought in zip(randys, thoughts):
            randy.shift(DOWN)
            thought.next_to(randy, UP+RIGHT, buff = 0)
            if curr_randy:
                self.play(
                    Transform(curr_randy, randy),
                    Transform(curr_thought, thought)
                )
            else:
                self.play(
                    FadeIn(randy),
                    Write(thought, run_time = 1)
                )
                curr_randy = randy
                curr_thought = thought
            self.dither(1.5)


class ExampleTransformation(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.apply_matrix(EXAMPLE_TRANFORM)
        self.dither()



class NumericToComputations(Scene):
    def construct(self):
        top = TextMobject("Numeric understanding")
        arrow = Arrow(UP, DOWN)
        bottom = TextMobject("Actual computations")
        top.next_to(arrow, UP)
        bottom.next_to(arrow, DOWN)

        self.add(top)
        self.play(ShowCreation(arrow, submobject_mode = "one_at_a_time"))
        self.play(FadeIn(bottom))
        self.dither()















