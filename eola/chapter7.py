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
from eola.footnote2 import TwoDTo1DTransformWithDots

from ka_playgrounds.circuits import Resistor, Source, LongResistor

V_COLOR = YELLOW
W_COLOR = MAROON_B
SUM_COLOR = PINK

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

class TwoDToOneDScene(LinearTransformationScene):
    CONFIG = {
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : SPACE_WIDTH,
            "y_radius" : SPACE_HEIGHT,
            "secondary_line_ratio" : 1
        },
        "t_matrix" : [[2, 0], [1, 0]]
    }
    def setup(self):
        self.number_line = NumberLine()
        self.add(self.number_line)
        LinearTransformationScene.setup(self)

class Introduce2Dto1DLinearTransformations(TwoDToOneDScene):
    def construct(self):
        number_line_words = TextMobject("Number line")
        number_line_words.next_to(self.number_line, UP, buff = MED_BUFF)
        numbers = VMobject(*self.number_line.get_number_mobjects())

        self.remove(self.number_line)
        self.apply_transposed_matrix(self.t_matrix)
        self.play(
            ShowCreation(number_line),
            *[Animation(v) for v in self.i_hat, self.j_hat]
        )
        self.play(*map(Write, [numbers, number_line_words]))
        self.dither()

class Symbolic2To1DTransform(Scene):
    def construct(self):
        func = TexMobject("L(", "\\vec{\\textbf{v}}", ")")
        input_array = Matrix([2, 7])
        input_array.highlight(YELLOW)
        in_arrow = Arrow(LEFT, RIGHT, color = input_array.get_color())
        func[1].highlight(input_array.get_color())
        output_array = Matrix([1.8])
        output_array.highlight(PINK)
        out_arrow = Arrow(LEFT, RIGHT, color = output_array.get_color())
        VMobject(
            input_array, in_arrow, func, out_arrow, output_array
        ).arrange_submobjects(RIGHT, buff = SMALL_BUFF)

        input_brace = Brace(input_array, DOWN)
        input_words = input_brace.get_text("2d input")
        output_brace = Brace(output_array, UP)
        output_words = output_brace.get_text("1d output")
        input_words.highlight(input_array.get_color())
        output_words.highlight(output_array.get_color())

        special_words = TextMobject("Linear", "functions are quite special")
        special_words.highlight_by_tex("Linear", BLUE)
        special_words.to_edge(UP)


        self.add(func, input_array)
        self.play(
            GrowFromCenter(input_brace),
            Write(input_words)
        )
        mover = input_array.copy()
        self.play(
            Transform(mover, Dot().move_to(func)),
            ShowCreation(in_arrow),
            rate_func = rush_into,
            run_time = 0.5
        )
        self.play(
            Transform(mover, output_array),
            ShowCreation(out_arrow),
            rate_func = rush_from,
            run_time = 0.5
        )
        self.play(
            GrowFromCenter(output_brace),
            Write(output_words)
        )
        self.dither()
        self.play(Write(special_words))
        self.dither()

class FormalVsVisual(Scene):
    def construct(self):
        title = TextMobject("Linearity")
        title.highlight(BLUE)
        title.to_edge(UP)
        line = Line(LEFT, RIGHT).scale(SPACE_WIDTH)
        line.next_to(title, DOWN)
        v_line = Line(line.get_center(), SPACE_HEIGHT*DOWN)

        formal = TextMobject("Formal definition")
        visual = TextMobject("Visual intuition")
        formal.next_to(line, DOWN).shift(SPACE_WIDTH*LEFT/2)
        visual.next_to(line, DOWN).shift(SPACE_WIDTH*RIGHT/2)

        v_tex, w_tex = ["\\vec{\\textbf{%s}}"%c for c in "v", "w"]
        additivity = TexMobject(
            "L(", v_tex, "+", w_tex, ") = ",
            "L(", v_tex, ")+", "L(", w_tex, ")"
        )
        additivity.highlight_by_tex(v_tex, V_COLOR)
        additivity.highlight_by_tex(w_tex, W_COLOR)
        scaling = TexMobject(
            "L(", "c", v_tex, ")=", "c", "L(", v_tex, ")"
        )
        scaling.highlight_by_tex(v_tex, V_COLOR)
        scaling.highlight_by_tex("c", GREEN)

        visual_statement = TextMobject("""
            Line of dots evenly spaced
            dots remains evenly spaced
        """)
        visual_statement.submobject_gradient_highlight(YELLOW, MAROON_B)

        properties = VMobject(additivity, scaling)
        properties.arrange_submobjects(DOWN, buff = MED_BUFF)
        
        for text, mob in (formal, properties), (visual, visual_statement):
            mob.scale(0.75)
            mob.next_to(text, DOWN, buff = MED_BUFF)

        self.add(title)
        self.play(*map(ShowCreation, [line, v_line]))
        for mob in formal, visual, additivity, scaling, visual_statement:
            self.play(Write(mob, run_time = 2))
            self.dither()

class AdditivityProperty(TwoDToOneDScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "sum_before" : True
    }
    def construct(self):
        v = Vector([2, 1], color = V_COLOR)
        w = Vector([-1, 1], color = W_COLOR)

        self.play(ShowCreation(v))
        self.play(ShowCreation(w))
        if self.sum_before:
            sum_vect = self.play_sum(v, w)
        else:
            self.add_vector(v, animate = False)
            self.add_vector(w, animate = False)
        self.apply_transposed_matrix(self.t_matrix)
        if not self.sum_before:
            sum_vect = self.play_sum(v, w)
        self.dither()
        self.write_symbols(sum_vect)

    def play_sum(self, v, w):
        sum_vect = Vector(v.get_end()+w.get_end(), color = SUM_COLOR)
        self.play(w.shift, v.get_end(), path_arc = np.pi/4)
        self.play(ShowCreation(sum_vect))
        for vect in v, w:
            vect.target = vect.copy()
            vect.target.set_fill(opacity = 0)
            vect.target.set_stroke(width = 0)
        sum_vect.target = sum_vect
        self.play(*[
            Transform(mob, mob.target)
            for mob in v, w, sum_vect
        ])
        self.add_vector(sum_vect, animate = False)
        return sum_vect

    def write_symbols(self, sum_vect):
        v_tex, w_tex = ["\\vec{\\textbf{%s}}"%c for c in "v", "w"]
        if self.sum_before:
            tex_mob = TexMobject(
                "L(", v_tex, "+", w_tex, ")"
            )
            tex_mob.next_to(sum_vect, UP)
        else:
            tex_mob = TexMobject(
                "L(", v_tex, ")+L(", w_tex, ")"
            )
            tex_mob.next_to(sum_vect, DOWN)
        tex_mob.highlight_by_tex(v_tex, V_COLOR)
        tex_mob.highlight_by_tex(w_tex, W_COLOR)


        self.play(Write(tex_mob))
        self.dither()

class AdditivityPropertyPart2(AdditivityProperty):
    CONFIG = {
        "sum_before" : False
    }

class ScalingProperty(TwoDToOneDScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "scale_before" : True,
        "scalar" : 2,
    }
    def construct(self):
        v = Vector([-1, 1], color = V_COLOR)

        self.play(ShowCreation(v))
        if self.scale_before:
            scaled_vect = self.show_scaling(v)
        self.add_vector(v, animate = False)
        self.apply_transposed_matrix(self.t_matrix)
        if not self.scale_before:
            scaled_vect = self.show_scaling(v)
        self.dither()
        self.write_symbols(scaled_vect)

    def show_scaling(self, v):
        self.add_vector(v.copy().fade(), animate = False)
        self.play(v.scale, self.scalar)
        return v

    def write_symbols(self, scaled_vect):
        v_tex = "\\vec{\\textbf{v}}"
        if self.scale_before:
            tex_mob = TexMobject(
                "L(", "c", v_tex, ")"
            )
            tex_mob.next_to(scaled_vect, UP)
        else:
            tex_mob = TexMobject(
                "c", "L(", v_tex, ")",
            )
            tex_mob.next_to(scaled_vect, DOWN)
        tex_mob.highlight_by_tex(v_tex, V_COLOR)
        tex_mob.highlight_by_tex("c", GREEN)

        self.play(Write(tex_mob))
        self.dither()

class ScalingPropertyPart2(ScalingProperty):
    CONFIG = {
        "scale_before" : False
    }

class ThisTwoDTo1DTransformWithDots(TwoDTo1DTransformWithDots):
    pass

class AlwaysfollowIHatJHat(TeacherStudentsScene):
    def construct(self):
        i_tex, j_tex = ["$\\hat{\\%smath}$"%c for c in "i", "j"]
        words = TextMobject(
            "Always follow", i_tex, "and", j_tex
        )
        words.highlight_by_tex(i_tex, X_COLOR)
        words.highlight_by_tex(j_tex, Y_COLOR)
        self.teacher_says(words)
        students = VMobject(*self.get_students())
        ponderers = VMobject(*[
            pi.copy().change_mode("pondering")
            for pi in students
        ])
        self.play(Transform(
            students, ponderers,
            submobject_mode = "lagged_start",
            run_time = 2
        ))
        self.random_blink(2)

class ShowMatrix(TwoDToOneDScene):
    def construct(self):
        self.apply_transposed_matrix(self.t_matrix)
        self.play(Write(self.number_line.get_numbers()))
        self.show_matrix()

    def show_matrix(self):
        for vect, char in zip([self.i_hat, self.j_hat], ["i", "j"]):
            vect.words = TextMobject(
                "$\\hat\\%smath$ lands on"%char,
                str(int(vect.get_end()[0]))
            )
            direction = UP if vect is self.i_hat else DOWN
            vect.words.next_to(vect.get_end(), direction, buff = LARGE_BUFF)
            vect.words.highlight(vect.get_color())
        matrix = Matrix([[1, 2]])
        matrix_words = TextMobject("Transformation matrix: ")
        matrix_group = VMobject(matrix_words, matrix)
        matrix_group.arrange_submobjects()
        matrix_group.to_edge(UP)
        entries = matrix.get_entries()

        self.play(
            Write(matrix_words), 
            Write(matrix.get_brackets()),
            run_time = 1
        )
        for i, vect in enumerate([self.i_hat, self.j_hat]):
            self.play(
                Write(vect.words, run_time = 1),
                ApplyMethod(vect.shift, 0.5*UP, rate_func = there_and_back)
            )
            self.dither()
            self.play(vect.words[1].copy().move_to, entries[i])
            self.dither()

class FollowVectorViaCoordinates(TwoDToOneDScene):
    CONFIG = {
        "t_matrix" : [[1, 0], [-2, 0]],
        "v_coords" : [3, 3],
        "written_v_coords" : ["x", "y"],
        "concrete" : False,
    }
    def construct(self):
        v = Vector(self.v_coords)
        array = Matrix(self.v_coords if self.concrete else self.written_v_coords)
        array.get_entries().gradient_highlight(X_COLOR, Y_COLOR)
        array.add_to_back(BackgroundRectangle(array))
        v_label = TexMobject("\\vec{\\textbf{v}}", "=")
        v_label[0].highlight(YELLOW)
        v_label.next_to(v.get_end(), RIGHT)
        v_label.add_background_rectangle()
        array.next_to(v_label, RIGHT)

        bases = self.i_hat, self.j_hat
        basis_labels = self.get_basis_vector_labels(direction = "right")
        scaling_anim_tuples = self.get_scaling_anim_tuples(
            basis_labels, array, [DOWN, RIGHT]
        )

        self.play(*map(Write, basis_labels))
        self.play(
            ShowCreation(v),
            Write(array),
            Write(v_label)
        )
        self.add_foreground_mobject(v_label, array)
        self.add_vector(v, animate = False)
        self.dither()
        to_fade = basis_labels
        for i, anim_tuple in enumerate(scaling_anim_tuples):
            self.play(*anim_tuple)
            movers = self.get_mobjects_from_last_animation()
            to_fade += movers[:-1]
            if i == 1:
                self.play(*[
                    ApplyMethod(m.shift, self.v_coords[0]*RIGHT)
                    for m in movers
                ])
            self.dither()
        self.play(
            *map(FadeOut, to_fade) + [
                vect.restore
                for vect in self.i_hat, self.j_hat
            ]
        )

        self.apply_transposed_matrix(self.t_matrix)
        self.play(Write(self.number_line.get_numbers(), run_time = 1))
        self.play(
            self.i_hat.shift, 0.5*UP,
            self.j_hat.shift, DOWN,
        )
        if self.concrete:
            new_labels = [
                TexMobject("(%d)"%num)
                for num in self.t_matrix[:,0]
            ]
        else:
            new_labels = [
                TexMobject("L(\\hat{\\%smath})"%char)
                for char in "i", "j"
            ]
            
        new_labels[0].highlight(X_COLOR)
        new_labels[1].highlight(Y_COLOR)

        new_labels.append(
            TexMobject("L(\\vec{\\textbf{v}})").highlight(YELLOW)
        )
        for label, vect, direction in zip(new_labels, list(bases) + [v], [UP, DOWN, UP]):
            label.next_to(vect, direction)

        self.play(*map(Write, new_labels))
        self.dither()
        scaling_anim_tuples = self.get_scaling_anim_tuples(
            new_labels, array, [UP, DOWN]
        )
        for i, anim_tuple in enumerate(scaling_anim_tuples):
            self.play(*anim_tuple)
            movers = VMobject(*self.get_mobjects_from_last_animation())
            self.dither()
        self.play(movers.shift, self.i_hat.get_end()[0]*RIGHT)
        self.dither()
        if self.concrete:
            final_label = TexMobject(str(int(v.get_end()[0])))
            final_label.move_to(new_labels[-1])
            final_label.highlight(new_labels[-1].get_color())
            self.play(Transform(new_labels[-1], final_label))
            self.dither()


    def get_scaling_anim_tuples(self, labels, array, directions):
        scaling_anim_tuples = []
        bases = self.i_hat, self.j_hat
        quints = zip(
            bases, self.v_coords, labels, 
            array.get_entries(), directions
        )        
        for basis, scalar, label, entry, direction in quints:
            basis.save_state()
            basis.scaled = basis.copy().scale(scalar)
            basis.scaled.shift(basis.get_start() - basis.scaled.get_start())
            scaled_label = VMobject(entry.copy(), label.copy())
            entry.target, label.target = scaled_label.split()
            entry.target.next_to(label.target, LEFT)
            scaled_label.next_to(
                basis.scaled,
                direction
            )

            scaling_anim_tuples.append((
                ApplyMethod(label.move_to, label.target),
                ApplyMethod(entry.copy().move_to, entry.target),
                Transform(basis, basis.scaled),
            ))
        return scaling_anim_tuples

class FollowVectorViaCoordinatesConcrete(FollowVectorViaCoordinates):
    CONFIG = {
        "v_coords" : [4, 3],
        "concrete" : True
    }

class TwoDOneDMatrixMultiplication(Scene):
    def construct(self):
        matrix = Matrix([[1, -2]])
        matrix.label = "Transform"
        vector = Matrix([4, 3])
        vector.label = "Vector"
        matrix.next_to(vector, LEFT, buff = 0.2)
        for m, vect in zip([matrix, vector], [UP, DOWN]):
            x, y = m.get_entries()
            x.highlight(X_COLOR)
            y.highlight(Y_COLOR)
            m.brace = Brace(m, vect)
            m.label = m.brace.get_text(m.label)
        matrix.label.highlight(BLUE)
        vector.label.highlight(YELLOW)

        starter_pairs = zip(vector.get_entries(), matrix.get_entries())
        pairs = [
            VMobject(
                e1.copy(), TexMobject("\\cdot"), e2.copy()
            ).arrange_submobjects()
            for e1, e2 in starter_pairs
        ]
        symbols = map(TexMobject, ["=", "+"])
        equation = VMobject(*it.chain(*zip(symbols, pairs)))
        equation.arrange_submobjects()
        equation.next_to(vector, RIGHT)

        for m in vector, matrix:
            self.play(Write(m))
            self.play(
                GrowFromCenter(m.brace),
                Write(m.label),
                run_time = 1
            )
            self.dither()
        self.play(Write(VMobject(*symbols)))
        for starter_pair, pair in zip(starter_pairs, pairs):
            self.play(Transform(
                VMobject(*starter_pair).copy(), 
                pair, 
                path_arc = -np.pi/2
            ))
        self.dither()

class AssociationBetweenMatricesAndVectors(Scene):
    def construct(self):
        matrices_words = TextMobject("$1\\times 2$ matrices")
        matrices_words.highlight(BLUE)
        vectors_words = TextMobject("2d vectors")
        vectors_words.highlight(YELLOW)
        arrow = DoubleArrow(LEFT, RIGHT, color = WHITE)
        VMobject(
            matrices_words, arrow, vectors_words
        ).arrange_submobjects(buff = MED_BUFF)

        matrices = VMobject(Matrix([[2, 7]]), Matrix([[1, -2]]))
        vectors = VMobject(Matrix([2, 7]), Matrix([1, -2]))
        for m in list(matrices) + list(vectors):
            x, y = m.get_entries()
            x.highlight(X_COLOR)
            y.highlight(Y_COLOR)
        matrices[0].next_to(matrices_words, UP, buff = MED_BUFF)
        matrices[1].next_to(matrices_words, DOWN, buff = MED_BUFF)
        vectors[0].next_to(vectors_words, UP, buff = MED_BUFF)
        vectors[1].next_to(vectors_words, DOWN, buff = MED_BUFF)

        self.play(*map(Write, [matrices_words, vectors_words]))
        self.play(ShowCreation(arrow))
        self.dither()
        self.play(FadeIn(vectors))
        vectors.save_state()
        self.dither()
        self.play(Transform(
            vectors, matrices, 
            path_arc = np.pi/2,
            submobject_mode = "lagged_start",
            run_time = 2,
        ))
        self.dither()
        self.play(
            vectors.restore, 
            path_arc = -np.pi/2,
            submobject_mode = "lagged_start",
            run_time = 2
        )
        self.dither()

class WhatAboutTheGeometricView(TeacherStudentsScene):
    def construct(self):
        self.student_says("""
            What does this association
            mean geometrically? 
            """, 
            pi_creature_target_mode = "raise_right_hand"
        )
        self.change_student_modes("pondering", "raise_right_hand", "pondering")
        self.random_blink(2)

class AnExampleWillClarify(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("An example will clarify...")
        self.change_student_modes(*["happy"]*3)
        self.random_blink(3)

class ImagineYouDontKnowThis(Scene):
    def construct(self):
        words = TextMobject("Imagine you don't know this")
        words.highlight(RED)
        words.scale(1.5)
        self.play(Write(words))
        self.dither()

class ProjectOntoUnitVectorNumberline(VectorScene):
    def construct(self):
        self.lock_in_faded_grid()
        u_hat = Vector([1, 0], color = PINK)
        u_hat.rotate(np.pil/6)
        number_line = NumberLine()
        numbers = number_line.get_numbers()
        VMobject(number_line, numbers).rotate(u_hat.get_angle())
























