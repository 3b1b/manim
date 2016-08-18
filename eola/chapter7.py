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

V_COLOR = YELLOW
W_COLOR = MAROON_B

def get_projection(stable_vector, vector_to_project):
    dot_product = np.dot(*[
        v.get_end()
        for v in stable_vector, vector_to_project
    ])
    stable_square_norm = stable_vector.get_length()**2
    result = Vector(
        stable_vector.get_end()*dot_product/stable_square_norm,
        color = vector_to_project.get_color()
    )
    result.fade()
    return result

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

        for i in range(3):
            self.play(Write(VMobject(*words[2*i:2*i+1])))
        # self.play(FadeIn(words))
        self.dither(2)

class TraditionalOrdering(RandolphScene):
    def construct(self):
        title = TextMobject("Traditional ordering:")
        title.highlight(YELLOW)
        title.scale(1.2)
        title.to_corner(UP+LEFT)
        topics = VMobject(*map(TextMobject, [
            "Topic 1: Vectors",
            "Topic 2: Dot products",
            "\\vdots",
            "(everything else)",
            "\\vdots",
        ]))
        topics.arrange_submobjects(DOWN, aligned_edge = LEFT, buff = SMALL_BUFF)
        # topics.next_to(title, DOWN+RIGHT)

        self.play(
            Write(title, run_time = 1),
            FadeIn(
                topics, 
                run_time = 3,
                submobject_mode = "lagged_start"
            ),
        )
        self.play(topics[1].highlight, PINK)
        self.dither()

class ThisSeriesOrdering(RandolphScene):
    def construct(self):
        title = TextMobject("Essence of linear algebra")
        title.scale(1.2).highlight(BLUE)
        title.to_corner(UP+LEFT)
        line = Line(SPACE_WIDTH*LEFT, SPACE_WIDTH*RIGHT, color = WHITE)
        line.next_to(title, DOWN, buff = SMALL_BUFF)
        line.to_edge(LEFT, buff = 0)

        chapters = VMobject(*[
            TextMobject("\\small " + text)
            for text in [
                "Chapter 1: Vectors, what even are they?",
                "Chapter 2: Linear combinations, span and bases",
                "Chapter 3: Matrices as linear transformations",
                "Chapter 4: Matrix multiplication as composition",
                "Chapter 5: The determinant",
                "Chapter 6: Inverse matrices, column space and null space",
                "Chapter 7: Dot products and duality",
                "Chapter 8: Cross products via transformations",
                "Chapter 9: Change of basis",
                "Chapter 10: Eigenvectors and eigenvalues",
                "Chapter 11: Abstract vector spaces",
            ]
        ])
        chapters.arrange_submobjects(
            DOWN, buff = SMALL_BUFF, aligned_edge = LEFT
        )
        chapters.scale_to_fit_height(1.5*SPACE_HEIGHT)
        chapters.next_to(line, DOWN, buff = SMALL_BUFF)
        chapters.to_edge(RIGHT)

        self.add(title)
        self.play(ShowCreation(line))
        self.play(
            FadeIn(
                chapters, 
                submobject_mode = "lagged_start",
                run_time = 3
            ),
            self.randy.change_mode, "sassy"
        )
        self.play(chapters[6].highlight, PINK)
        self.dither(2)
        self.dither(2)

class OneMustViewThroughTransformations(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            Only with transformations
            can we truly understand
        """)
        self.change_student_modes(
            "pondering",
            "plain",
            "raise_right_hand"
        )
        self.random_blink(2)
        self.teacher_says("""
            First, the 
            standard view...
        """)
        self.random_blink(2)

class ShowNumericalDotProduct(Scene):
    CONFIG = {
        "v1" : [2, 7, 1],
        "v2" : [8, 2, 8],
    }
    def construct(self):
        v1 = Matrix(self.v1)
        v2 = Matrix(self.v2)
        inter_array_dot = TexMobject("\\cdot").scale(1.5)
        dot_product = VMobject(v1, inter_array_dot, v2)
        dot_product.arrange_submobjects(RIGHT)
        dot_product.to_edge(LEFT)
        pairs = zip(v1.get_entries(), v2.get_entries())

        for pair, color in zip(pairs, [X_COLOR, Y_COLOR, Z_COLOR, PINK]):
            VMobject(*pair).highlight(color)

        dot = TexMobject("\\cdot")
        products = VMobject(*[
            VMobject(
                p1.copy(), dot.copy(), p2.copy()
            ).arrange_submobjects(RIGHT, buff = SMALL_BUFF)
            for p1, p2 in pairs
        ])
        products.arrange_submobjects(DOWN, buff = LARGE_BUFF)
        products.next_to(dot_product, RIGHT, buff = LARGE_BUFF)


        products.target = products.copy()
        plusses = ["+"]*(len(self.v1)-1)
        symbols = VMobject(*map(TexMobject, ["="] + plusses))
        final_sum = VMobject(*it.chain(*zip(
            symbols, products.target
        )))
        final_sum.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
        final_sum.next_to(dot_product, RIGHT)


        self.play(
            Write(v1),
            Write(v2),
            FadeIn(inter_array_dot)
        )
        self.dither()
        
        self.dither()
        self.play(Transform(
            VMobject(*it.starmap(VMobject, pairs)).copy(),
            products,
            path_arc = -np.pi/2,
            run_time = 2 
        ))
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(products)
        self.dither()

        self.play(
            Write(symbols),
            Transform(products, products.target, path_arc = np.pi/2)
        )
        self.dither()

class TwoDDotProductExample(ShowNumericalDotProduct):
    CONFIG = {
        "v1" : [1, 2],
        "v2" : [3, 4],
    }

class FourDDotProductExample(ShowNumericalDotProduct):
    CONFIG = {
        "v1" : [6, 2, 8, 3],
        "v2" : [1, 8, 5, 3],
    }

class GeometricInterpretation(VectorScene):
    CONFIG = {
        "v_coords" : [4, 1],
        "w_coords" : [2, -1],
        "v_color" : V_COLOR,
        "w_color" : W_COLOR,
        "project_onto_v" : True,
    }
    def construct(self):
        self.lock_in_faded_grid()
        self.add_symbols()
        self.add_vectors()
        self.line()
        self.project()
        self.show_lengths()
        self.handle_possible_negative()


    def add_symbols(self):
        v = matrix_to_mobject(self.v_coords).highlight(self.v_color)
        w = matrix_to_mobject(self.w_coords).highlight(self.w_color)
        v.add_background_rectangle()
        w.add_background_rectangle()
        dot = TexMobject("\\cdot")
        eq = VMobject(v, dot, w)
        eq.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
        eq.to_corner(UP+LEFT)
        self.play(Write(eq), run_time = 1)
        for array, char in zip([v, w], ["v", "w"]):
            brace = Brace(array, DOWN)
            label = brace.get_text("$\\vec{\\textbf{%s}}$"%char)
            label.highlight(array.get_color())
            self.play(
                GrowFromCenter(brace),
                Write(label),
                run_time = 1
            )
        self.dot_product = eq


    def add_vectors(self):
        self.v = Vector(self.v_coords, color = self.v_color)
        self.w = Vector(self.w_coords, color = self.w_color)
        self.play(ShowCreation(self.v))
        self.play(ShowCreation(self.w))
        for vect, char, direction in zip(
            [self.v, self.w], ["v", "w"], [DOWN+RIGHT, DOWN]
            ):
            label = TexMobject("\\vec{\\textbf{%s}}"%char)
            label.next_to(vect.get_end(), direction)
            label.highlight(vect.get_color())
            self.play(Write(label, run_time = 1))
        self.stable_vect = self.v if self.project_onto_v else self.w
        self.proj_vect = self.w if self.project_onto_v else self.v

    def line(self):
        line = Line(LEFT, RIGHT).scale(SPACE_WIDTH)
        line.rotate(self.stable_vect.get_angle())
        self.play(ShowCreation(line), Animation(self.stable_vect))
        self.dither()

    def project(self):
        dot_product = np.dot(self.v.get_end(), self.w.get_end())
        v_norm, w_norm = [
            np.linalg.norm(vect.get_end())
            for vect in self.v, self.w
        ]
        projected = Vector(
            self.stable_vect.get_end()*dot_product/(
                self.stable_vect.get_length()**2
            ),
            color = self.proj_vect.get_color()
        )
        projection_line = Line(
            self.proj_vect.get_end(), projected.get_end(),
            color = GREY
        )

        self.play(ShowCreation(projection_line))
        self.add(self.proj_vect.copy().fade())
        self.play(Transform(self.proj_vect, projected))
        self.dither()

    def show_lengths(self):
        stable_char = "v" if self.project_onto_v else "w"
        proj_char = "w" if self.project_onto_v else "v"
        product = TextMobject(
            "=", 
            "(",
            "Length of projected $\\vec{\\textbf{%s}}$"%proj_char,
            ")",
            "(",
            "Length of $\\vec{\\textbf{%s}}$"%stable_char,
            ")",
            separate_list_arg_with_spaces = False
        )
        product.scale(0.9)
        product.next_to(self.dot_product, RIGHT)
        proj_words = product[2]
        proj_words.highlight(self.proj_vect.get_color())
        stable_words = product[5]
        stable_words.highlight(self.stable_vect.get_color())
        product.remove(proj_words, stable_words)
        for words in stable_words, proj_words:
            words.add_to_back(BackgroundRectangle(words))
            words.start = words.copy()

        proj_brace, stable_brace = braces = [
            Brace(Line(ORIGIN, vect.get_length()*RIGHT*sgn), UP)
            for vect in self.proj_vect, self.stable_vect
            for sgn in [np.sign(np.dot(vect.get_end(), self.stable_vect.get_end()))]
        ]
        proj_brace.put_at_tip(proj_words.start)
        proj_brace.words = proj_words.start
        stable_brace.put_at_tip(stable_words.start)
        stable_brace.words = stable_words.start
        for brace in braces:
            brace.rotate(self.stable_vect.get_angle())
            brace.words.rotate(self.stable_vect.get_angle())

        self.play(
            GrowFromCenter(proj_brace),
            Write(proj_words.start, run_time = 2)
        )
        self.dither()
        self.play(
            Transform(proj_words.start, proj_words),
            FadeOut(proj_brace)
        )
        self.play(
            GrowFromCenter(stable_brace),
            Write(stable_words.start, run_time = 2),
            Animation(self.stable_vect)
        )
        self.dither()
        self.play(
            Transform(stable_words.start, stable_words),
            Write(product)
        )
        self.dither()

        product.add(stable_words.start, proj_words.start)
        self.product = product

    def handle_possible_negative(self):
        if np.dot(self.w.get_end(), self.v.get_end()) > 0:
            return
        neg = TexMobject("-").highlight(RED)
        neg.next_to(self.product[0], RIGHT)
        words = TextMobject("Should be negative")
        words.highlight(RED)
        words.next_to(
            VMobject(*self.product[2:]), 
            DOWN, 
            buff = LARGE_BUFF,
            aligned_edge = LEFT
        )
        words.add_background_rectangle()
        arrow = Arrow(words.get_left(), neg, color = RED)

        self.play(
            Write(neg),
            ShowCreation(arrow),
            VMobject(*self.product[1:]).next_to, neg,
            Write(words)
        )
        self.dither()

class GeometricInterpretationNegative(GeometricInterpretation):
    CONFIG = {
        "v_coords" : [3, 1],
        "w_coords" : [-1, -2],
        "v_color" : YELLOW,
        "w_color" : MAROON_B,
    }

class ShowQualitativeDotProductValues(VectorScene):
    def construct(self):
        self.lock_in_faded_grid()
        v_sym, dot, w_sym, comp, zero = ineq = TexMobject(
            "\\vec{\\textbf{v}}",
            "\\cdot",
            "\\vec{\\textbf{w}}",
            ">",
            "0",
        )
        ineq.to_edge(UP)
        ineq.add_background_rectangle()
        comp.highlight(GREEN)
        equals = TexMobject("=").highlight(PINK).move_to(comp)
        less_than = TexMobject("<").highlight(RED).move_to(comp)
        v_sym.highlight(V_COLOR)
        w_sym.highlight(W_COLOR)
        words = map(TextMobject, [
            "Similar directions",
            "Perpendicular",
            "Opposing directions"
        ])
        for word, sym in zip(words, [comp, equals, less_than]):
            word.add_background_rectangle()
            word.next_to(sym, DOWN, aligned_edge = LEFT, buff = MED_BUFF)
            word.highlight(sym.get_color())

        v = Vector([1.5, 1.5], color = V_COLOR)
        w = Vector([2, 2], color = W_COLOR)
        w.rotate(-np.pi/6)
        shadow = Vector(
            v.get_end()*np.dot(v.get_end(), w.get_end())/(v.get_length()**2),
            color = MAROON_E,
            preserve_tip_size_when_scaling = False
        )
        shadow_opposite = shadow.copy().scale(-1)
        line = Line(LEFT, RIGHT, color = WHITE)
        line.scale(SPACE_WIDTH)
        line.rotate(v.get_angle())
        proj_line = Line(w.get_end(), shadow.get_end(), color = GREY)


        word = words[0]

        self.add(ineq)
        for mob in v, w, line, proj_line:
            self.play(
                ShowCreation(mob),
                Animation(v)
            )
        self.play(Transform(w.copy(), shadow))
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(shadow)
        self.play(FadeOut(proj_line))

        self.play(Write(word, run_time = 1))
        self.dither()
        self.play(
            Rotate(w, -np.pi/3),
            shadow.scale, 0
        )
        self.play(
            Transform(comp, equals),
            Transform(word, words[1])
        )
        self.dither()
        self.play(
            Rotate(w, -np.pi/3),
            Transform(shadow, shadow_opposite)
        )
        self.play(
            Transform(comp, less_than),
            Transform(word, words[2])
        )
        self.dither()

class AskAboutSymmetry(TeacherStudentsScene):
    def construct(self):
        v, w = "\\vec{\\textbf{v}}", "\\vec{\\textbf{w}}",
        question = TexMobject(
            "\\text{Why does }",
            v, "\\cdot", w, "=", w, "\\cdot", v,
            "\\text{?}"
        )
        VMobject(question[1], question[7]).highlight(V_COLOR)
        VMobject(question[3], question[5]).highlight(W_COLOR)
        self.student_says(
            question,
            pi_creature_target_mode = "raise_left_hand"
        )
        self.change_student_modes("confused")
        self.play(self.get_teacher().change_mode, "pondering")
        self.play(self.get_teacher().look, RIGHT)
        self.play(self.get_teacher().look, LEFT)
        self.random_blink()

class GeometricInterpretationSwapVectors(GeometricInterpretation):
    CONFIG = {
        "project_onto_v" : False,
    }

class SymmetricVAndW(VectorScene):
    def construct(self):
        self.lock_in_faded_grid()
        v = Vector([3, 1], color = V_COLOR)
        w = Vector([1, 3], color = W_COLOR)
        for vect, char in zip([v, w], ["v", "w"]):
            vect.label = TexMobject("\\vec{\\textbf{%s}}"%char)
            vect.label.highlight(vect.get_color())
            vect.label.next_to(vect.get_end(), DOWN+RIGHT)
        for v1, v2 in (v, w), (w, v):
            v1.proj = get_projection(v2, v1)
            v1.proj_line = Line(
                v1.get_end(), v1.proj.get_end(), color = GREY
            )
        line_of_symmetry = DashedLine(SPACE_WIDTH*LEFT, SPACE_WIDTH*RIGHT)
        line_of_symmetry.rotate(np.mean([v.get_angle(), w.get_angle()]))
        line_of_symmetry_words = TextMobject("Line of symmetry")
        line_of_symmetry_words.add_background_rectangle()
        line_of_symmetry_words.next_to(ORIGIN, UP+RIGHT)
        line_of_symmetry_words.rotate(line_of_symmetry.get_angle())

        for vect in v, w:
            self.play(ShowCreation(vect))
            self.play(Write(vect.label, run_time = 1))
        self.dither()
        angle = (v.get_angle()-w.get_angle())/2
        self.play(
            Rotate(w, angle), 
            Rotate(v, -angle),
            rate_func = there_and_back,
            run_time = 2
        )
        self.dither()
        self.play(ShowCreation(line_of_symmetry))
        self.play(Write(line_of_symmetry_words))
        self.dither()
        self.play(Transform(line_of_symmetry_words, line_of_symmetry))
        for vect in v, w:
            self.play(ShowCreation(vect.proj_line))
            vect_copy = vect.copy()
            self.play(Transform(vect_copy, vect.proj))
            self.remove(vect_copy)
            self.add(vect.proj)
            self.dither()

        self.show_doubling(v, w)

    def show_doubling(self, v, w):
        scalar = 2
        new_v = v.copy().scale(scalar)
        new_v.label = VMobject(TexMobject(str(scalar)), v.label.copy())
        new_v.label.arrange_submobjects()
        new_v.label.highlight(new_v.get_color())
        new_v.label.next_to(new_v.get_end(), DOWN+RIGHT)
        new_v.proj = v.proj.copy().scale(scalar)
        new_v.proj.fade()
        new_v.proj_line = Line(
            new_v.get_end(), new_v.proj.get_end(),
            color = GREY
        )

        v_tex, w_tex = ["\\vec{\\textbf{%s}}"%c for c in "v", "w"]
        equation = TexMobject(
            "(", "2", v_tex, ")", "\\cdot", w_tex,
            "=",
            "2(", v_tex, "\\cdot", w_tex, ")"
        )
        equation.highlight_by_tex(v_tex, V_COLOR)
        equation.highlight_by_tex(w_tex, W_COLOR)
        equation.next_to(ORIGIN, DOWN).to_edge(RIGHT)

        words = TextMobject("Symmetry is broken")
        words.next_to(ORIGIN, LEFT)
        words.to_edge(UP)

        v.save_state()
        v.proj.save_state()
        self.play(Transform(*[
            VMobject(mob, mob.proj, mob.proj_line, mob.label)
            for mob in v, new_v
        ]), run_time = 2)
        self.play(Write(words))
        self.dither()

        two_v_parts = equation[1:3]
        equation.remove(*two_v_parts)
        self.play(
            Write(equation),
            Transform(new_v.label.copy(), VMobject(*two_v_parts))
        )
        self.dither()

        for vect in v, v.proj:
            self.play(
                vect.restore,
                rate_func = there_and_back,
                run_time = 2
            )
            self.dither()

class LurkingQuestion(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("That's the standard intro")
        self.dither()
        self.student_says(
            """
            Wait, why are the
            two views connected?
            """,
            pi_creature_target_mode = "confused"
        )
        self.change_student_modes(
            "raise_right_hand", "confused", "raise_left_hand"
        )
        self.random_blink(5)
        answer = TextMobject("""
            The most satisfactory
            answer comes from""",
            "duality"
        )
        answer.highlight_by_tex("duality", PINK)
        self.teacher_says(answer)
        self.random_blink(2)
        self.teacher_thinks("")
        everything = VMobject(*self.get_mobjects())
        self.play(ApplyPointwiseFunction(
            lambda p : 10*(p+2*DOWN)/np.linalg.norm(p+2*DOWN),
            everything
        ))

class Introduce2Dto1DLinearTransformations(LinearTransformationScene):
    def construct(self):
        pass


























