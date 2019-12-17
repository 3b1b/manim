from manimlib.imports import *
from old_projects.eola.footnote2 import TwoDTo1DTransformWithDots


V_COLOR = YELLOW
W_COLOR = MAROON_B
SUM_COLOR = PINK


def get_projection(vector_to_project, stable_vector):
    v1, v2 = stable_vector, vector_to_project
    return v1*np.dot(v1, v2)/(get_norm(v1)**2)

def get_vect_mob_projection(vector_to_project, stable_vector):
    return Vector(
        get_projection(
            vector_to_project.get_end(),            
            stable_vector.get_end()
        ),
        color = vector_to_project.get_color()
    ).fade()

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
            "they magically become one NEW number! "
            "No one can say how it happens. "
            "You either believe it or you don't.",
        )
        words.set_width(FRAME_WIDTH - 1)
        words.to_edge(UP)
        words[0].set_color(YELLOW)
        words[2].set_color("#fd9c2b")
        words[4].set_color(YELLOW)

        for i in range(3):
            speaker, quote = words[2*i:2*i+2]
            self.play(FadeIn(speaker, run_time = 0.5))
            rt = max(1, len(quote.split())/18)
            self.play(Write(
                quote, 
                run_time = rt,
            ))
        self.wait(2)

class TraditionalOrdering(RandolphScene):
    def construct(self):
        title = TextMobject("Traditional ordering:")
        title.set_color(YELLOW)
        title.scale(1.2)
        title.to_corner(UP+LEFT)
        topics = VMobject(*list(map(TextMobject, [
            "Topic 1: Vectors",
            "Topic 2: Dot products",
            "\\vdots",
            "(everything else)",
            "\\vdots",
        ])))
        topics.arrange(DOWN, aligned_edge = LEFT, buff = SMALL_BUFF)
        # topics.next_to(title, DOWN+RIGHT)

        self.play(
            Write(title, run_time = 1),
            FadeIn(
                topics, 
                run_time = 3,
                lag_ratio = 0.5
            ),
        )
        self.play(topics[1].set_color, PINK)
        self.wait()

class ThisSeriesOrdering(RandolphScene):
    def construct(self):
        title = TextMobject("Essence of linear algebra")
        self.randy.rotate(np.pi, UP)
        title.scale(1.2).set_color(BLUE)
        title.to_corner(UP+LEFT)
        line = Line(FRAME_X_RADIUS*LEFT, FRAME_X_RADIUS*RIGHT, color = WHITE)
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
        chapters.arrange(
            DOWN, buff = SMALL_BUFF, aligned_edge = LEFT
        )
        chapters.set_height(1.5*FRAME_Y_RADIUS)
        chapters.next_to(line, DOWN, buff = SMALL_BUFF)
        chapters.to_edge(RIGHT)

        self.add(title)
        self.play(
            ShowCreation(line),
        )
        self.play(
            FadeIn(
                chapters, 
                lag_ratio = 0.5,
                run_time = 3
            ),
            self.randy.change_mode, "sassy"
        )
        self.play(self.randy.look, UP+LEFT)
        self.play(chapters[6].set_color, PINK)
        self.wait(6)

class OneMustViewThroughTransformations(TeacherStudentsScene):
    def construct(self):
        words = TextMobject(
            "Only with" , "transformations",
            "\n can we truly understand",
        )
        words.set_color_by_tex("transformations", BLUE)
        self.teacher_says(words)
        self.change_student_modes(
            "pondering",
            "plain",
            "raise_right_hand"
        )
        self.random_blink(2)
        words = TextMobject(
            "First, the ",
            "standard view...",
            arg_separator = "\n"
        )
        self.teacher_says(words)
        self.random_blink(2)

class ShowNumericalDotProduct(Scene):
    CONFIG = {
        "v1" : [2, 7, 1],
        "v2" : [8, 2, 8],
        "write_dot_product_words" : True,
    }
    def construct(self):
        v1 = Matrix(self.v1)
        v2 = Matrix(self.v2)
        inter_array_dot = TexMobject("\\cdot").scale(1.5)
        dot_product = VGroup(v1, inter_array_dot, v2)
        dot_product.arrange(RIGHT, buff = MED_SMALL_BUFF/2)
        dot_product.to_edge(LEFT)
        pairs = list(zip(v1.get_entries(), v2.get_entries()))

        for pair, color in zip(pairs, [X_COLOR, Y_COLOR, Z_COLOR, PINK]):
            VGroup(*pair).set_color(color)

        dot = TexMobject("\\cdot")
        products = VGroup(*[
            VGroup(
                p1.copy(), dot.copy(), p2.copy()
            ).arrange(RIGHT, buff = SMALL_BUFF)
            for p1, p2 in pairs
        ])
        products.arrange(DOWN, buff = LARGE_BUFF)
        products.next_to(dot_product, RIGHT, buff = LARGE_BUFF)


        products.target = products.copy()
        plusses = ["+"]*(len(self.v1)-1)
        symbols = VGroup(*list(map(TexMobject, ["="] + plusses)))
        final_sum = VGroup(*it.chain(*list(zip(
            symbols, products.target
        ))))
        final_sum.arrange(RIGHT, buff = SMALL_BUFF)
        final_sum.next_to(dot_product, RIGHT)

        title = TextMobject("Two vectors of the same dimension")
        title.to_edge(UP)

        arrow = Arrow(DOWN, UP).next_to(inter_array_dot, DOWN)
        dot_product_words = TextMobject("Dot product")
        dot_product_words.set_color(YELLOW)
        dot_product_words.next_to(arrow, DOWN)
        dot_product_words.shift_onto_screen()

        self.play(
            Write(v1),
            Write(v2),
            FadeIn(inter_array_dot),
            FadeIn(title)
        )
        self.wait()
        if self.write_dot_product_words:
            self.play(
                inter_array_dot.set_color, YELLOW,
                ShowCreation(arrow),
                Write(dot_product_words, run_time = 2)
            )
            self.wait()
        self.play(Transform(
            VGroup(*it.starmap(Group, pairs)).copy(),
            products,
            path_arc = -np.pi/2,
            run_time = 2 
        ))
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(products)
        self.wait()

        self.play(
            Write(symbols),
            Transform(products, products.target, path_arc = np.pi/2)
        )
        self.wait()

class TwoDDotProductExample(ShowNumericalDotProduct):
    CONFIG = {
        "v1" : [1, 2],
        "v2" : [3, 4],
    }

class FourDDotProductExample(ShowNumericalDotProduct):
    CONFIG = {
        "v1" : [6, 2, 8, 3],
        "v2" : [1, 8, 5, 3],
        "write_dot_product_words" : False,
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
        v = matrix_to_mobject(self.v_coords).set_color(self.v_color)
        w = matrix_to_mobject(self.w_coords).set_color(self.w_color)
        v.add_background_rectangle()
        w.add_background_rectangle()
        dot = TexMobject("\\cdot")
        eq = VMobject(v, dot, w)
        eq.arrange(RIGHT, buff = SMALL_BUFF)
        eq.to_corner(UP+LEFT)
        self.play(Write(eq), run_time = 1)
        for array, char in zip([v, w], ["v", "w"]):
            brace = Brace(array, DOWN)
            label = brace.get_text("$\\vec{\\textbf{%s}}$"%char)
            label.set_color(array.get_color())
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
            label.set_color(vect.get_color())
            self.play(Write(label, run_time = 1))
        self.stable_vect = self.v if self.project_onto_v else self.w
        self.proj_vect = self.w if self.project_onto_v else self.v

    def line(self):
        line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        line.rotate(self.stable_vect.get_angle())
        self.play(ShowCreation(line), Animation(self.stable_vect))
        self.wait()

    def project(self):
        dot_product = np.dot(self.v.get_end(), self.w.get_end())
        v_norm, w_norm = [
            get_norm(vect.get_end())
            for vect in (self.v, self.w)
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
        self.wait()

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
            arg_separator = ""
        )
        product.scale(0.9)
        product.next_to(self.dot_product, RIGHT)
        proj_words = product[2]
        proj_words.set_color(self.proj_vect.get_color())
        stable_words = product[5]
        stable_words.set_color(self.stable_vect.get_color())
        product.remove(proj_words, stable_words)
        for words in stable_words, proj_words:
            words.add_to_back(BackgroundRectangle(words))
            words.start = words.copy()

        proj_brace, stable_brace = braces = [
            Brace(Line(ORIGIN, vect.get_length()*RIGHT*sgn), UP)
            for vect in (self.proj_vect, self.stable_vect)
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
        self.wait()
        self.play(
            Transform(proj_words.start, proj_words),
            FadeOut(proj_brace)
        )
        self.play(
            GrowFromCenter(stable_brace),
            Write(stable_words.start, run_time = 2),
            Animation(self.stable_vect)
        )
        self.wait()
        self.play(
            Transform(stable_words.start, stable_words),
            Write(product)
        )
        self.wait()

        product.add(stable_words.start, proj_words.start)
        self.product = product

    def handle_possible_negative(self):
        if np.dot(self.w.get_end(), self.v.get_end()) > 0:
            return
        neg = TexMobject("-").set_color(RED)
        neg.next_to(self.product[0], RIGHT)
        words = TextMobject("Should be negative")
        words.set_color(RED)
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
        self.wait()

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
        comp.set_color(GREEN)
        equals = TexMobject("=").set_color(PINK).move_to(comp)
        less_than = TexMobject("<").set_color(RED).move_to(comp)
        v_sym.set_color(V_COLOR)
        w_sym.set_color(W_COLOR)
        words = list(map(TextMobject, [
            "Similar directions",
            "Perpendicular",
            "Opposing directions"
        ]))
        for word, sym in zip(words, [comp, equals, less_than]):
            word.add_background_rectangle()
            word.next_to(sym, DOWN, aligned_edge = LEFT, buff = MED_SMALL_BUFF)
            word.set_color(sym.get_color())

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
        line.scale(FRAME_X_RADIUS)
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
        self.wait()
        self.play(
            Rotate(w, -np.pi/3),
            shadow.scale, 0
        )
        self.play(
            Transform(comp, equals),
            Transform(word, words[1])
        )
        self.wait()
        self.play(
            Rotate(w, -np.pi/3),
            Transform(shadow, shadow_opposite)
        )
        self.play(
            Transform(comp, less_than),
            Transform(word, words[2])
        )
        self.wait()

class AskAboutSymmetry(TeacherStudentsScene):
    def construct(self):
        v, w = "\\vec{\\textbf{v}}", "\\vec{\\textbf{w}}",
        question = TexMobject(
            "\\text{Why does }",
            v, "\\cdot", w, "=", w, "\\cdot", v,
            "\\text{?}"
        )
        VMobject(question[1], question[7]).set_color(V_COLOR)
        VMobject(question[3], question[5]).set_color(W_COLOR)
        self.student_says(
            question,
            target_mode = "raise_left_hand"
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
            vect.label.set_color(vect.get_color())
            vect.label.next_to(vect.get_end(), DOWN+RIGHT)
        for v1, v2 in (v, w), (w, v):
            v1.proj = get_vect_mob_projection(v1, v2)
            v1.proj_line = Line(
                v1.get_end(), v1.proj.get_end(), color = GREY
            )
        line_of_symmetry = DashedLine(FRAME_X_RADIUS*LEFT, FRAME_X_RADIUS*RIGHT)
        line_of_symmetry.rotate(np.mean([v.get_angle(), w.get_angle()]))
        line_of_symmetry_words = TextMobject("Line of symmetry")
        line_of_symmetry_words.add_background_rectangle()
        line_of_symmetry_words.next_to(ORIGIN, UP+LEFT)
        line_of_symmetry_words.rotate(line_of_symmetry.get_angle())

        for vect in v, w:
            self.play(ShowCreation(vect))
            self.play(Write(vect.label, run_time = 1))
        self.wait()
        angle = (v.get_angle()-w.get_angle())/2
        self.play(
            Rotate(w, angle), 
            Rotate(v, -angle),
            rate_func = there_and_back,
            run_time = 2
        )
        self.wait()
        self.play(
            ShowCreation(line_of_symmetry),
            Write(line_of_symmetry_words, run_time = 1)
        )
        self.wait(0.5)
        self.remove(line_of_symmetry_words)
        self.play(*list(map(Uncreate, line_of_symmetry_words)))
        for vect in w, v:
            self.play(ShowCreation(vect.proj_line))
            vect_copy = vect.copy()
            self.play(Transform(vect_copy, vect.proj))
            self.remove(vect_copy)
            self.add(vect.proj)
            self.wait()
        self.play(*list(map(FadeOut,[
            v.proj, v.proj_line, w.proj, w.proj_line
        ])))
        self.show_doubling(v, w)

    def show_doubling(self, v, w):
        scalar = 2
        new_v = v.copy().scale(scalar)
        new_v.label = VMobject(TexMobject("2"), v.label.copy())
        new_v.label.arrange(aligned_edge = DOWN)
        new_v.label.next_to(new_v.get_end(), DOWN+RIGHT)
        new_v.proj = v.proj.copy().scale(scalar)
        new_v.proj.fade()
        new_v.proj_line = Line(
            new_v.get_end(), new_v.proj.get_end(),
            color = GREY
        )

        v_tex, w_tex = ["\\vec{\\textbf{%s}}"%c for c in ("v", "w")]
        equation = TexMobject(
            "(", "2", v_tex, ")", "\\cdot", w_tex,
            "=",
            "2(", v_tex, "\\cdot", w_tex, ")"
        )
        equation.set_color_by_tex(v_tex, V_COLOR)
        equation.set_color_by_tex(w_tex, W_COLOR)
        equation.next_to(ORIGIN, DOWN).to_edge(RIGHT)

        words = TextMobject("Symmetry is broken")
        words.next_to(ORIGIN, LEFT)
        words.to_edge(UP)

        v.save_state()
        v.proj.save_state()
        v.proj_line.save_state()
        self.play(Transform(*[
            VGroup(mob, mob.label)
            for mob in (v, new_v)
        ]), run_time = 2)
        last_mob = self.get_mobjects_from_last_animation()[0] 
        self.remove(last_mob)
        self.add(*last_mob)       
        Transform(
            VGroup(v.proj, v.proj_line),
            VGroup(new_v.proj, new_v.proj_line)
        ).update(1)##Hacky

        self.play(Write(words))
        self.wait()

        two_v_parts = equation[1:3]
        equation.remove(*two_v_parts)

        for full_v, projector, stable in zip([False, True], [w, v], [v, w]):
            self.play(
                Transform(projector.copy(), projector.proj),
                ShowCreation(projector.proj_line)
            )
            self.remove(self.get_mobjects_from_last_animation()[0])
            self.add(projector.proj)
            self.wait()
            if equation not in self.get_mobjects():
                self.play(
                    Write(equation),
                    Transform(new_v.label.copy(), VMobject(*two_v_parts))
                )
                self.wait()
            v_parts = [v]
            if full_v:
                v_parts += [v.proj, v.proj_line]
            self.play(
                *[v_part.restore for v_part in v_parts],
                rate_func = there_and_back,
                run_time = 2
            )
            self.wait()
            self.play(*list(map(FadeOut, [
                projector.proj, projector.proj_line
            ])))

class LurkingQuestion(TeacherStudentsScene):
    def construct(self):
        # self.teacher_says("That's the standard intro")
        # self.wait()
        # self.student_says(
        #     """
        #     Wait, why are the
        #     two views connected?
        #     """,
        #     student_index = 2,
        #     target_mode = "raise_left_hand",
        #     width = 6,
        # )
        self.change_student_modes(
            "raise_right_hand", "confused", "raise_left_hand"
        )
        self.random_blink(5)
        answer = TextMobject("""
            The most satisfactory
            answer comes from""",
            "duality"
        )
        answer[-1].set_color_by_gradient(BLUE, YELLOW)
        self.teacher_says(answer)
        self.random_blink(2)
        self.teacher_thinks("")
        everything = VMobject(*self.get_mobjects())
        self.play(ApplyPointwiseFunction(
            lambda p : 10*(p+2*DOWN)/get_norm(p+2*DOWN),
            everything
        ))

class TwoDToOneDScene(LinearTransformationScene):
    CONFIG = {
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_X_RADIUS,
            "y_radius" : FRAME_Y_RADIUS,
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
        number_line_words.next_to(self.number_line, UP, buff = MED_SMALL_BUFF)
        numbers = VMobject(*self.number_line.get_number_mobjects())

        self.remove(self.number_line)
        self.apply_transposed_matrix(self.t_matrix)
        self.play(
            ShowCreation(number_line),
            *[Animation(v) for v in (self.i_hat, self.j_hat)]
        )
        self.play(*list(map(Write, [numbers, number_line_words])))
        self.wait()

class Symbolic2To1DTransform(Scene):
    def construct(self):
        func = TexMobject("L(", "\\vec{\\textbf{v}}", ")")
        input_array = Matrix([2, 7])
        input_array.set_color(YELLOW)
        in_arrow = Arrow(LEFT, RIGHT, color = input_array.get_color())
        func[1].set_color(input_array.get_color())
        output_array = Matrix([1.8])
        output_array.set_color(PINK)
        out_arrow = Arrow(LEFT, RIGHT, color = output_array.get_color())
        VMobject(
            input_array, in_arrow, func, out_arrow, output_array
        ).arrange(RIGHT, buff = SMALL_BUFF)

        input_brace = Brace(input_array, DOWN)
        input_words = input_brace.get_text("2d input")
        output_brace = Brace(output_array, UP)
        output_words = output_brace.get_text("1d output")
        input_words.set_color(input_array.get_color())
        output_words.set_color(output_array.get_color())

        special_words = TextMobject("Linear", "functions are quite special")
        special_words.set_color_by_tex("Linear", BLUE)
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
        self.wait()
        self.play(Write(special_words))
        self.wait()

class RecommendChapter3(Scene):
    def construct(self):
        title = TextMobject("""
            Definitely watch Chapter 3
            if you haven't already
        """)
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()  

class OkayToIgnoreFormalProperties(Scene):
    def construct(self):
        title = TextMobject("Formal linearity properties")
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        h_line.next_to(title, DOWN)
        v_tex, w_tex = ["\\vec{\\textbf{%s}}"%s for s in ("v", "w")]
        additivity = TexMobject(
            "L(", v_tex, "+", w_tex, ") = ",
            "L(", v_tex, ") + L(", w_tex, ")",
        )
        scaling = TexMobject(
            "L(", "c", v_tex, ") =", "c", "L(", v_tex, ")",
        )
        for tex_mob in additivity, scaling:
            tex_mob.set_color_by_tex(v_tex, V_COLOR)
            tex_mob.set_color_by_tex(w_tex, W_COLOR)
            tex_mob.set_color_by_tex("c", GREEN)
        additivity.next_to(h_line, DOWN, buff = MED_SMALL_BUFF)
        scaling.next_to(additivity, DOWN, buff = MED_SMALL_BUFF)
        words = TextMobject("We'll ignore these")
        words.set_color(RED)
        arrow = Arrow(DOWN, UP, color = RED)
        arrow.next_to(scaling, DOWN)
        words.next_to(arrow, DOWN)

        randy = Randolph().to_corner(DOWN+LEFT)
        morty = Mortimer().to_corner(DOWN+RIGHT)

        self.add(randy, morty, title)
        self.play(ShowCreation(h_line))
        for tex_mob in additivity, scaling:
            self.play(Write(tex_mob, run_time = 2))
        self.play(
            FadeIn(words),
            ShowCreation(arrow),
        )
        self.play(
            randy.look, LEFT,
            morty.look, RIGHT,
        )
        self.wait()

class FormalVsVisual(Scene):
    def construct(self):
        title = TextMobject("Linearity")
        title.set_color(BLUE)
        title.to_edge(UP)
        line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        line.next_to(title, DOWN)
        v_line = Line(line.get_center(), FRAME_Y_RADIUS*DOWN)

        formal = TextMobject("Formal definition")
        visual = TextMobject("Visual intuition")
        formal.next_to(line, DOWN).shift(FRAME_X_RADIUS*LEFT/2)
        visual.next_to(line, DOWN).shift(FRAME_X_RADIUS*RIGHT/2)

        v_tex, w_tex = ["\\vec{\\textbf{%s}}"%c for c in ("v", "w")]
        additivity = TexMobject(
            "L(", v_tex, "+", w_tex, ") = ",
            "L(", v_tex, ")+", "L(", w_tex, ")"
        )
        additivity.set_color_by_tex(v_tex, V_COLOR)
        additivity.set_color_by_tex(w_tex, W_COLOR)
        scaling = TexMobject(
            "L(", "c", v_tex, ")=", "c", "L(", v_tex, ")"
        )
        scaling.set_color_by_tex(v_tex, V_COLOR)
        scaling.set_color_by_tex("c", GREEN)

        visual_statement = TextMobject("""
            Line of dots evenly spaced
            dots remains evenly spaced
        """)
        visual_statement.set_submobject_colors_by_gradient(YELLOW, MAROON_B)

        properties = VMobject(additivity, scaling)
        properties.arrange(DOWN, buff = MED_SMALL_BUFF)
        
        for text, mob in (formal, properties), (visual, visual_statement):
            mob.scale(0.75)
            mob.next_to(text, DOWN, buff = MED_SMALL_BUFF)

        self.add(title)
        self.play(*list(map(ShowCreation, [line, v_line])))
        for mob in formal, visual, additivity, scaling, visual_statement:
            self.play(Write(mob, run_time = 2))
            self.wait()

class AdditivityProperty(TwoDToOneDScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "sum_before" : True
    }
    def construct(self):
        v = Vector([2, 1], color = V_COLOR)
        w = Vector([-1, 1], color = W_COLOR)


        L, sum_tex, r_paren = symbols = self.get_symbols()
        symbols.shift(4*RIGHT+2*UP)
        self.add_foreground_mobject(sum_tex)
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
        symbols.target = symbols.copy().next_to(sum_vect, UP)
        VGroup(L, r_paren).set_color(BLACK)
        self.play(Transform(symbols, symbols.target))
        self.wait()

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
            for mob in (v, w, sum_vect)
        ])
        self.add_vector(sum_vect, animate = False)
        return sum_vect

    def get_symbols(self):
        v_tex, w_tex = ["\\vec{\\textbf{%s}}"%c for c in ("v", "w")]
        if self.sum_before:
            tex_mob = TexMobject(
                "L(", v_tex, "+", w_tex, ")"
            )
            result = VGroup(
                tex_mob[0], 
                VGroup(*tex_mob[1:4]), 
                tex_mob[4]
            )
        else:
            tex_mob = TexMobject(
                "L(", v_tex, ")", "+", "L(", w_tex, ")"
            )
            result = VGroup(
                VectorizedPoint(tex_mob.get_left()),
                tex_mob,
                VectorizedPoint(tex_mob.get_right()),
            )
        tex_mob.set_color_by_tex(v_tex, V_COLOR)
        tex_mob.set_color_by_tex(w_tex, W_COLOR)
        result[1].add_to_back(BackgroundRectangle(result[1]))        
        return result

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
        self.wait()
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
        tex_mob.set_color_by_tex(v_tex, V_COLOR)
        tex_mob.set_color_by_tex("c", GREEN)

        self.play(Write(tex_mob))
        self.wait()

class ScalingPropertyPart2(ScalingProperty):
    CONFIG = {
        "scale_before" : False
    }

class ThisTwoDTo1DTransformWithDots(TwoDTo1DTransformWithDots):
    pass

class NonLinearFailsDotTest(TwoDTo1DTransformWithDots):
    def construct(self):
        line = NumberLine()
        self.add(line, *self.get_mobjects())
        offset = LEFT+DOWN
        vect = 2*RIGHT+UP
        dots = VMobject(*[
             Dot(offset + a*vect, radius = 0.075)
             for a in np.linspace(-2, 3, 18)
        ])
        dots.set_submobject_colors_by_gradient(YELLOW_B, YELLOW_C)
        func = lambda p : (p[0]**2 - p[1]**2)*RIGHT
        new_dots = VMobject(*[
            Dot(
                func(dot.get_center()), 
                color = dot.get_color(),
                radius = dot.radius
            )
            for dot in dots
        ])
        words = TextMobject(
            "Line of dots", "do not", "remain evenly spaced"
        )
        words.set_color_by_tex("do not", RED)
        words.next_to(line, UP, buff = MED_SMALL_BUFF)
        array_tex = matrix_to_tex_string(["x", "y"])
        equation = TexMobject(
            "f", "\\left(%s \\right)"%array_tex, " = x^2 - y^2"
        )
        for part in equation:
            part.add_to_back(BackgroundRectangle(part))
        equation.to_corner(UP+LEFT)
        self.add_foreground_mobject(equation)

        self.play(Write(dots))
        self.apply_nonlinear_transformation(
            func,
            added_anims = [Transform(dots, new_dots)]
        )
        self.play(Write(words))
        self.wait()

class AlwaysfollowIHatJHat(TeacherStudentsScene):
    def construct(self):
        i_tex, j_tex = ["$\\hat{\\%smath}$"%c for c in ("i", "j")]
        words = TextMobject(
            "Always follow", i_tex, "and", j_tex
        )
        words.set_color_by_tex(i_tex, X_COLOR)
        words.set_color_by_tex(j_tex, Y_COLOR)
        self.teacher_says(words)
        students = VMobject(*self.get_students())
        ponderers = VMobject(*[
            pi.copy().change_mode("pondering")
            for pi in students
        ])
        self.play(Transform(
            students, ponderers,
            lag_ratio = 0.5,
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
            vect.words.set_color(vect.get_color())
        matrix = Matrix([[1, 2]])
        matrix_words = TextMobject("Transformation matrix: ")
        matrix_group = VMobject(matrix_words, matrix)
        matrix_group.arrange()
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
            self.wait()
            self.play(vect.words[1].copy().move_to, entries[i])
            self.wait()

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
        array.get_entries().set_color_by_gradient(X_COLOR, Y_COLOR)
        array.add_to_back(BackgroundRectangle(array))
        v_label = TexMobject("\\vec{\\textbf{v}}", "=")
        v_label[0].set_color(YELLOW)
        v_label.next_to(v.get_end(), RIGHT)
        v_label.add_background_rectangle()
        array.next_to(v_label, RIGHT)

        bases = self.i_hat, self.j_hat
        basis_labels = self.get_basis_vector_labels(direction = "right")
        scaling_anim_tuples = self.get_scaling_anim_tuples(
            basis_labels, array, [DOWN, RIGHT]
        )

        self.play(*list(map(Write, basis_labels)))
        self.play(
            ShowCreation(v),
            Write(array),
            Write(v_label)
        )
        self.add_foreground_mobject(v_label, array)
        self.add_vector(v, animate = False)
        self.wait()
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
            self.wait()
        self.play(
            *list(map(FadeOut, to_fade)) + [
                vect.restore
                for vect in (self.i_hat, self.j_hat)
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
                for char in ("i", "j")
            ]
            
        new_labels[0].set_color(X_COLOR)
        new_labels[1].set_color(Y_COLOR)

        new_labels.append(
            TexMobject("L(\\vec{\\textbf{v}})").set_color(YELLOW)
        )
        for label, vect, direction in zip(new_labels, list(bases) + [v], [UP, DOWN, UP]):
            label.next_to(vect, direction)

        self.play(*list(map(Write, new_labels)))
        self.wait()
        scaling_anim_tuples = self.get_scaling_anim_tuples(
            new_labels, array, [UP, DOWN]
        )
        for i, anim_tuple in enumerate(scaling_anim_tuples):
            self.play(*anim_tuple)
            movers = VMobject(*self.get_mobjects_from_last_animation())
            self.wait()
        self.play(movers.shift, self.i_hat.get_end()[0]*RIGHT)
        self.wait()
        if self.concrete:
            final_label = TexMobject(str(int(v.get_end()[0])))
            final_label.move_to(new_labels[-1])
            final_label.set_color(new_labels[-1].get_color())
            self.play(Transform(new_labels[-1], final_label))
            self.wait()


    def get_scaling_anim_tuples(self, labels, array, directions):
        scaling_anim_tuples = []
        bases = self.i_hat, self.j_hat
        quints = list(zip(
            bases, self.v_coords, labels, 
            array.get_entries(), directions
        ))        
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
    CONFIG = {
        "matrix" : [[1, -2]],
        "vector" : [4, 3],
        "order_left_to_right" : False,
    }
    def construct(self):
        matrix = Matrix(self.matrix)
        matrix.label = "Transform"
        vector = Matrix(self.vector)
        vector.label = "Vector"
        matrix.next_to(vector, LEFT, buff = 0.2)
        self.color_matrix_and_vector(matrix, vector)
        for m, vect in zip([matrix, vector], [UP, DOWN]):
            m.brace = Brace(m, vect)
            m.label = m.brace.get_text(m.label)
        matrix.label.set_color(BLUE)
        vector.label.set_color(MAROON_B)

        for m in vector, matrix:
            self.play(Write(m))
            self.play(
                GrowFromCenter(m.brace),
                Write(m.label),
                run_time = 1
            )
            self.wait()
        self.show_product(matrix, vector)

    def show_product(self, matrix, vector):
        starter_pairs = list(zip(vector.get_entries(), matrix.get_entries()))
        pairs = [
            VMobject(
                e1.copy(), TexMobject("\\cdot"), e2.copy()
            ).arrange(
                LEFT if self.order_left_to_right else RIGHT,
            )
            for e1, e2 in starter_pairs
        ]
        symbols = list(map(TexMobject, ["=", "+"]))
        equation = VMobject(*it.chain(*list(zip(symbols, pairs))))
        equation.arrange(align_using_submobjects = True)
        equation.next_to(vector, RIGHT)

        self.play(Write(VMobject(*symbols)))
        for starter_pair, pair in zip(starter_pairs, pairs):
            self.play(Transform(
                VMobject(*starter_pair).copy(), 
                pair, 
                path_arc = -np.pi/2
            ))
        self.wait()

    def color_matrix_and_vector(self, matrix, vector):
        for m in matrix, vector:
            x, y = m.get_entries()
            x.set_color(X_COLOR)
            y.set_color(Y_COLOR)

class AssociationBetweenMatricesAndVectors(Scene):
    CONFIG = {
        "matrices" : [
            [[2, 7]],
            [[1, -2]]
        ]
    }
    def construct(self):
        matrices_words = TextMobject("$1\\times 2$ matrices")
        matrices_words.set_color(BLUE)
        vectors_words = TextMobject("2d vectors")
        vectors_words.set_color(YELLOW)
        arrow = DoubleArrow(LEFT, RIGHT, color = WHITE)
        VGroup(
            matrices_words, arrow, vectors_words
        ).arrange(buff = MED_SMALL_BUFF)

        matrices = VGroup(*list(map(Matrix, self.matrices)))
        vectors = VGroup(*list(map(Matrix, [m[0] for m in self.matrices])))
        for m in list(matrices) + list(vectors):
            x, y = m.get_entries()
            x.set_color(X_COLOR)
            y.set_color(Y_COLOR)
        matrices.words = matrices_words
        vectors.words = vectors_words
        for group in matrices, vectors:
            for m, direction in zip(group, [UP, DOWN]):
                m.next_to(group.words, direction, buff = MED_SMALL_BUFF)

        self.play(*list(map(Write, [matrices_words, vectors_words])))
        self.play(ShowCreation(arrow))
        self.wait()
        self.play(FadeIn(vectors))
        vectors.save_state()
        self.wait()
        self.play(Transform(
            vectors, matrices, 
            path_arc = np.pi/2,
            lag_ratio = 0.5,
            run_time = 2,
        ))
        self.wait()
        self.play(
            vectors.restore, 
            path_arc = -np.pi/2,
            lag_ratio = 0.5,
            run_time = 2
        )
        self.wait()

class WhatAboutTheGeometricView(TeacherStudentsScene):
    def construct(self):
        self.student_says("""
            What does this association
            mean geometrically? 
            """, 
            target_mode = "raise_right_hand"
        )
        self.change_student_modes("pondering", "raise_right_hand", "pondering")
        self.random_blink(2)

class SomeKindOfConnection(Scene):
    CONFIG = {
        "v_coords" : [2, 3]
    }
    def construct(self):
        width = FRAME_X_RADIUS-1
        plane = NumberPlane(x_radius = 4, y_radius = 6)
        squish_plane = plane.copy()
        i_hat = Vector([1, 0], color = X_COLOR)
        j_hat = Vector([0, 1], color = Y_COLOR)
        vect = Vector(self.v_coords, color = YELLOW)
        plane.add(vect, i_hat, j_hat)
        plane.set_width(FRAME_X_RADIUS)
        plane.to_edge(LEFT, buff = 0)
        plane.remove(vect, i_hat, j_hat)

        squish_plane.apply_function(
            lambda p : np.dot(p, [4, 1, 0])*RIGHT
        )
        squish_plane.add(Vector(self.v_coords[1]*RIGHT, color = Y_COLOR))
        squish_plane.add(Vector(self.v_coords[0]*RIGHT, color = X_COLOR))        
        squish_plane.scale(width/(FRAME_WIDTH))
        plane.add(j_hat, i_hat)

        number_line = NumberLine().stretch_to_fit_width(width)
        number_line.to_edge(RIGHT)
        squish_plane.move_to(number_line)

        numbers = number_line.get_numbers(*list(range(-6, 8, 2)))
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        v_line.set_color(GREY)
        v_line.set_stroke(width = 10)

        matrix = Matrix([self.v_coords])
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.next_to(number_line, UP, buff = LARGE_BUFF)
        v_coords = Matrix(self.v_coords)
        v_coords.set_column_colors(YELLOW)
        v_coords.scale(0.75)
        v_coords.next_to(vect.get_end(), RIGHT)
        for array in matrix, v_coords:
            array.add_to_back(BackgroundRectangle(array))


        self.play(*list(map(ShowCreation, [
            plane, number_line, v_line
        ]))+[
            Write(numbers, run_time = 2)
        ])
        self.play(Write(matrix, run_time = 1))
        mover = plane.copy()
        interim = plane.copy().scale(0.8).move_to(number_line)
        for target in interim, squish_plane:
            self.play(
                Transform(mover, target),
                Animation(plane),
                run_time = 1,
            )
        self.wait()
        self.play(ShowCreation(vect))
        self.play(Transform(matrix.copy(), v_coords))
        self.wait()

class AnExampleWillClarify(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("An example will clarify...")
        self.change_student_modes(*["happy"]*3)
        self.random_blink(3)

class ImagineYouDontKnowThis(Scene):
    def construct(self):
        words = TextMobject("Imagine you don't know this")
        words.set_color(RED)
        words.scale(1.5)
        self.play(Write(words))
        self.wait()

class ProjectOntoUnitVectorNumberline(VectorScene):
    CONFIG = {
        "randomize_dots" : True,
        "animate_setup" : True,
        "zoom_factor" : 1,
        "u_hat_color" : YELLOW,
        "tilt_angle" : np.pi/6,
    }
    def setup(self):
        plane = self.add_plane()
        plane.fade()

        u_hat = Vector([1, 0], color = self.u_hat_color)
        u_brace = Brace(u_hat, UP)
        u_hat.rotate(self.tilt_angle)
        u_hat.label = TexMobject("\\hat{\\textbf{u}}")
        u_hat.label.set_color(u_hat.get_color())
        u_hat.label.next_to(u_hat.get_end(), UP+LEFT)
        one = TexMobject("1")
        u_brace.put_at_tip(one)
        u_brace.add(one)
        u_brace.rotate(u_hat.get_angle())
        one.rotate_in_place(-u_hat.get_angle())

        number_line = NumberLine(x_min = -9, x_max = 9)
        numbers = number_line.get_numbers()
        VGroup(number_line, numbers).rotate(u_hat.get_angle())
        if self.animate_setup:
            self.play(
                ShowCreation(number_line),
                Write(numbers),
                run_time = 3 
            )
            self.wait()
            self.play(ShowCreation(u_hat))
            self.play(FadeIn(u_brace))
            self.play(FadeOut(u_brace))
            self.play(Write(u_hat.label))            
            self.wait()
        else:
            self.add(number_line, numbers, u_hat)

        if self.zoom_factor != 1:
            for mob in plane, u_hat:
                mob.target = mob.copy().scale(self.zoom_factor)
            number_line.target = number_line.copy()
            number_line.target.rotate(-u_hat.get_angle())
            number_line.target.stretch(self.zoom_factor, 0)
            numbers.target = number_line.target.get_numbers()
            number_line.target.rotate(u_hat.get_angle())
            numbers.target.rotate(u_hat.get_angle())
            self.play(*[
                Transform(mob, mob.target)
                for mob in self.get_mobjects()
            ])
            self.wait()
        self.number_line, self.numbers, self.u_hat = number_line, numbers, u_hat


    def construct(self):
        vectors = self.get_vectors(randomize = self.randomize_dots)
        dots = self.get_dots(vectors)
        proj_dots = self.get_proj_dots(dots)
        proj_lines = self.get_proj_lines(dots, proj_dots)

        self.wait()
        self.play(FadeIn(vectors, lag_ratio = 0.5))
        self.wait()
        self.play(Transform(vectors, dots))
        self.wait()
        self.play(ShowCreation(proj_lines))
        self.wait()
        self.play(
            self.number_line.set_stroke, None, 2, 
            Transform(vectors, proj_dots),
            Transform(proj_lines, proj_dots),
            Animation(self.u_hat),
            lag_ratio = 0.5,
            run_time = 2
        )
        self.wait()


    def get_vectors(self, num_vectors = 10, randomize = True):
        x_max = FRAME_X_RADIUS - 1
        y_max = FRAME_Y_RADIUS - 1
        x_vals = np.linspace(-x_max, x_max, num_vectors)
        y_vals = np.linspace(y_max, -y_max, num_vectors)
        if randomize:
            random.shuffle(y_vals)
        vectors = VGroup(*[
            Vector(x*RIGHT + y*UP)
            for x, y in zip(x_vals, y_vals)
        ])
        vectors.set_color_by_gradient(PINK, MAROON_B)
        return vectors

    def get_dots(self, vectors):
        return VGroup(*[
            Dot(v.get_end(), color = v.get_color(), radius = 0.075)
            for v in vectors
        ]) 

    def get_proj_dots(self, dots):
        return VGroup(*[
            dot.copy().move_to(get_projection(
                dot.get_center(), self.u_hat.get_end()
            ))
            for dot in dots
        ])

    def get_proj_lines(self, dots, proj_dots):
        return VGroup(*[
            DashedLine(
                d1.get_center(), d2.get_center(), 
                buff = 0, color = d1.get_color(),
                dash_length = 0.15
            )
            for d1, d2 in zip(dots, proj_dots)
        ])

class ProjectionFunctionSymbol(Scene):
    def construct(self):
        v_tex = "\\vec{\\textbf{v}}"
        equation = TexMobject(
            "P(", v_tex, ")=", 
            "\\text{number }", v_tex, "\\text{ lands on}"
        )
        equation.set_color_by_tex(v_tex, YELLOW)
        equation.shift(2*UP)
        words = TextMobject(
            "This projection function is", "linear"
        )
        words.set_color_by_tex("linear", BLUE)
        arrow = Arrow(
            words.get_top(), equation[0].get_bottom(), 
            color = BLUE
        )

        self.add(VGroup(*equation[:3]))
        self.play(Write(VGroup(*equation[3:])))
        self.wait()
        self.play(Write(words), ShowCreation(arrow))
        self.wait()

class ProjectLineOfDots(ProjectOntoUnitVectorNumberline):
    CONFIG = {
        "randomize_dots" : False,
        "animate_setup" : False,
    }

class ProjectSingleVectorOnUHat(ProjectOntoUnitVectorNumberline):
    CONFIG = {
        "animate_setup" : False
    }
    def construct(self):
        v = Vector([-3, 1], color = PINK)
        v.proj = get_vect_mob_projection(v, self.u_hat)
        v.proj_line = DashedLine(v.get_end(), v.proj.get_end())
        v.proj_line.set_color(v.get_color())
        v_tex = "\\vec{\\textbf{v}}"
        u_tex = self.u_hat.label.get_tex_string()
        v.label = TexMobject(v_tex)
        v.label.set_color(v.get_color())
        v.label.next_to(v.get_end(), LEFT)
        dot_product = TexMobject(v_tex, "\\cdot", u_tex)
        dot_product.set_color_by_tex(v_tex, v.get_color())
        dot_product.set_color_by_tex(u_tex, self.u_hat.get_color())
        dot_product.next_to(ORIGIN, UP, buff = MED_SMALL_BUFF)
        dot_product.rotate(self.tilt_angle)
        dot_product.shift(v.proj.get_end())
        dot_product.add_background_rectangle()
        v.label.add_background_rectangle()

        self.play(
            ShowCreation(v),
            Write(v.label),
        )
        self.wait()
        self.play(
            ShowCreation(v.proj_line),
            Transform(v.copy(), v.proj)
        )
        self.wait()
        self.play(
            FadeOut(v),
            FadeOut(v.proj_line),
            FadeOut(v.label),
            Write(dot_product)
        )
        self.wait()

class AskAboutProjectionMatrix(Scene):
    def construct(self):
        matrix = Matrix([["?", "?"]])
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        words = TextMobject("Projection matrix:")
        VMobject(words, matrix).arrange(buff = MED_SMALL_BUFF).shift(UP)
        basis_words = [
            TextMobject("Where", "$\\hat{\\%smath}$"%char, "lands")
            for char in ("i", "j")
        ]
        for b_words, q_mark, direction in zip(basis_words, matrix.get_entries(), [UP, DOWN]):
            b_words.next_to(q_mark, direction, buff = 1.5)
            b_words.arrow = Arrow(b_words, q_mark, color = q_mark.get_color())
            b_words.set_color(q_mark.get_color())

        self.play(
            Write(words), 
            Write(matrix)
        )
        self.wait()
        for b_words in basis_words:
            self.play(
                Write(b_words),
                ShowCreation(b_words.arrow)
            )
        self.wait()

class ProjectBasisVectors(ProjectOntoUnitVectorNumberline):
    CONFIG = {
        "animate_setup" : False,
        "zoom_factor" : 3,
        "u_hat_color" : YELLOW,
        "tilt_angle" : np.pi/5,
    }
    def construct(self):
        basis_vectors = self.get_basis_vectors()
        i_hat, j_hat = basis_vectors
        for vect in basis_vectors:
            vect.scale(self.zoom_factor)
        dots = self.get_dots(basis_vectors)
        proj_dots = self.get_proj_dots(dots)
        proj_lines = self.get_proj_lines(dots, proj_dots)
        for dot in proj_dots:
            dot.scale_in_place(0.1)
        proj_basis = VGroup(*[
            get_vect_mob_projection(vector, self.u_hat)
            for vector in basis_vectors
        ])

        i_tex, j_tex = ["$\\hat{\\%smath}$"%char for char in ("i", "j")]
        question = TextMobject(
            "Where do", i_tex, "and", j_tex, "land?"
        )
        question.set_color_by_tex(i_tex, X_COLOR)
        question.set_color_by_tex(j_tex, Y_COLOR)
        question.add_background_rectangle()
        matrix = Matrix([["u_x", "u_y"]])
        VGroup(question, matrix).arrange(DOWN).to_corner(
            UP+LEFT, buff = MED_SMALL_BUFF/2
        )
        matrix_rect = BackgroundRectangle(matrix)


        i_label = TexMobject(i_tex[1:-1])
        j_label = TexMobject(j_tex[1:-1])
        u_label = TexMobject("\\hat{\\textbf{u}}")
        trips = list(zip(
            (i_label, j_label, u_label), 
            (i_hat, j_hat, self.u_hat),
            (DOWN+RIGHT, UP+LEFT, UP),
        ))
        for label, vect, direction in trips:
            label.set_color(vect.get_color())
            label.scale(1.2)
            label.next_to(vect.get_end(), direction, buff = MED_SMALL_BUFF/2)

        self.play(Write(u_label, run_time = 1))
        self.play(*list(map(ShowCreation, basis_vectors)))
        self.play(*list(map(Write, [i_label, j_label])), run_time = 1)
        self.play(ShowCreation(proj_lines))
        self.play(
            Write(question), 
            ShowCreation(matrix_rect),            
            Write(matrix.get_brackets()),
            run_time = 2,
        )
        to_remove = [proj_lines]
        quads = list(zip(basis_vectors, proj_basis, proj_lines, proj_dots))
        for vect, proj_vect, proj_line, proj_dot in quads:
            self.play(Transform(vect.copy(), proj_vect))
            to_remove += self.get_mobjects_from_last_animation()
        self.wait()
        self.play(*list(map(FadeOut, to_remove)))

        # self.show_u_coords(u_label)
        u_x, u_y = [
            TexMobject("u_%s"%c).set_color(self.u_hat.get_color())
            for c in ("x", "y")
        ]
        matrix_x, matrix_y = matrix.get_entries()
        self.remove(j_hat, j_label)
        self.show_symmetry(i_hat, u_x, matrix_x)
        self.add(j_hat, j_label)
        self.remove(i_hat, i_label)
        self.show_symmetry(j_hat, u_y, matrix_y)

    # def show_u_coords(self, u_label):
    #     coords = Matrix(["u_x", "u_y"])
    #     x, y = coords.get_entries()
    #     x.set_color(X_COLOR)
    #     y.set_color(Y_COLOR)
    #     coords.add_to_back(BackgroundRectangle(coords))
    #     eq = TexMobject("=")
    #     eq.next_to(u_label, RIGHT)
    #     coords.next_to(eq, RIGHT)
    #     self.play(*map(FadeIn, [eq, coords]))
    #     self.wait()
    #     self.u_coords = coords

    def show_symmetry(self, vect, coord, coord_landing_spot):
        starting_mobjects = list(self.get_mobjects())
        line = DashedLine(FRAME_X_RADIUS*LEFT, FRAME_X_RADIUS*RIGHT)
        words = TextMobject("Line of symmetry")
        words.next_to(ORIGIN, UP+LEFT)
        words.shift(LEFT)
        words.add_background_rectangle()
        angle = np.mean([vect.get_angle(), self.u_hat.get_angle()])
        VGroup(line, words).rotate(angle)

        self.play(ShowCreation(line))
        if vect.get_end()[0] > 0.1:#is ihat
            self.play(Write(words, run_time = 1))

        vect.proj = get_vect_mob_projection(vect, self.u_hat)
        self.u_hat.proj = get_vect_mob_projection(self.u_hat, vect)
        for v in vect, self.u_hat:
            v.proj_line = DashedLine(
                v.get_end(), v.proj.get_end(), 
                color = v.get_color()
            )
            v.proj_line.fade()
            v.tick = Line(0.1*DOWN, 0.1*UP, color = WHITE)
            v.tick.rotate(v.proj.get_angle())
            v.tick.shift(v.proj.get_end())
            v.q_mark = TextMobject("?")
            v.q_mark.next_to(v.tick, v.proj.get_end()-v.get_end())

            self.play(ShowCreation(v.proj_line))
            self.play(Transform(v.copy(), v.proj))
            self.remove(*self.get_mobjects_from_last_animation())
            self.add(v.proj)
            self.wait()
        for v in vect, self.u_hat:
            self.play(
                ShowCreation(v.tick),
                Write(v.q_mark)
            )
            self.wait()
        for v in self.u_hat, vect:
            coord_copy = coord.copy().move_to(v.q_mark)
            self.play(Transform(v.q_mark, coord_copy))
            self.wait()
        final_coord = coord_copy.copy()
        self.play(final_coord.move_to, coord_landing_spot)

        added_mobjects = [
            mob
            for mob in self.get_mobjects()
            if mob not in starting_mobjects + [final_coord]
        ]
        self.play(*list(map(FadeOut, added_mobjects)))

class ShowSingleProjection(ProjectBasisVectors):
    CONFIG = {
        "zoom_factor" : 1
    }
    def construct(self):
        vector = Vector([5, - 1], color = MAROON_B)
        proj = get_vect_mob_projection(vector, self.u_hat)
        proj_line = DashedLine(
            vector.get_end(), proj.get_end(), 
            color = vector.get_color()
        )
        coords = Matrix(["x", "y"])
        coords.get_entries().set_color(vector.get_color())
        coords.add_to_back(BackgroundRectangle(coords))
        coords.next_to(vector.get_end(), RIGHT)

        u_label = TexMobject("\\hat{\\textbf{u}}")
        u_label.next_to(self.u_hat.get_end(), UP)
        u_label.add_background_rectangle()
        self.add(u_label)

        self.play(ShowCreation(vector))
        self.play(Write(coords))
        self.wait()
        self.play(ShowCreation(proj_line))
        self.play(
            Transform(vector.copy(), proj),
            Animation(self.u_hat)
        )
        self.wait()

class GeneralTwoDOneDMatrixMultiplication(TwoDOneDMatrixMultiplication):
    CONFIG = {
        "matrix" : [["u_x", "u_y"]],
        "vector" : ["x", "y"],
        "order_left_to_right" : True,
    }
    def construct(self):
        TwoDOneDMatrixMultiplication.construct(self)
        everything = VGroup(*self.get_mobjects())
        to_fade = [m for m in everything if isinstance(m, Brace) or isinstance(m, TextMobject)]

        u = Matrix(self.matrix[0])
        v = Matrix(self.vector)
        self.color_matrix_and_vector(u, v)
        dot_product = VGroup(u, TexMobject("\\cdot"), v)
        dot_product.arrange()
        dot_product.shift(2*RIGHT+DOWN)
        words = VGroup(
            TextMobject("Matrix-vector product"),
            TexMobject("\\Updownarrow"),
            TextMobject("Dot product")
        )
        words[0].set_color(BLUE)
        words[2].set_color(GREEN)
        words.arrange(DOWN)
        words.to_edge(LEFT)



        self.play(
            everything.to_corner, UP+RIGHT,
            *list(map(FadeOut, to_fade))
        )
        self.remove(everything)
        self.add(*everything)
        self.remove(*to_fade)

        self.play(Write(words, run_time = 2))        
        self.play(ShowCreation(dot_product))
        self.show_product(u, v)



    def color_matrix_and_vector(self, matrix, vector):
        colors = [X_COLOR, Y_COLOR]
        for coord, color in zip(matrix.get_entries(), colors):
            coord[0].set_color(YELLOW)
            coord[1].set_color(color)
        vector.get_entries().set_color(MAROON_B)

class UHatIsTransformInDisguise(Scene):
    def construct(self):
        u_tex = "$\\hat{\\textbf{u}}$"
        words = TextMobject(
            u_tex,
            "is secretly a \\\\",
            "transform",
            "in disguise",
        )
        words.set_color_by_tex(u_tex, YELLOW)
        words.set_color_by_tex("transform", BLUE)
        words.scale(2)

        self.play(Write(words))
        self.wait()

class AskAboutNonUnitVectors(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "What about \\\\ non-unit vectors",
            target_mode = "raise_left_hand"
        )
        self.random_blink(2)

class ScaleUpUHat(ProjectOntoUnitVectorNumberline) :
    CONFIG = {
        "animate_setup" : False,
        "u_hat_color" : YELLOW,
        "tilt_angle" : np.pi/6,
        "scalar" : 3,
    }
    def construct(self):
        self.scale_u_hat()
        self.show_matrix()
        self.transform_basis_vectors()
        self.transform_some_vector()

    def scale_u_hat(self):
        self.u_hat.coords = Matrix(["u_x", "u_y"])
        new_u = self.u_hat.copy().scale(self.scalar)
        new_u.coords = Matrix([
            "%du_x"%self.scalar,
            "%du_y"%self.scalar,
        ])
        for v in self.u_hat, new_u:
            v.coords.get_entries().set_color(YELLOW)
            v.coords.add_to_back(BackgroundRectangle(v.coords))
            v.coords.next_to(v.get_end(), UP+LEFT)

        self.play(Write(self.u_hat.coords))
        self.play(
            Transform(self.u_hat, new_u),
            Transform(self.u_hat.coords, new_u.coords)
        )
        self.wait()

    def show_matrix(self):
        matrix = Matrix([list(self.u_hat.coords.get_entries().copy())])
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.add_to_back(BackgroundRectangle(matrix))
        brace = Brace(matrix)
        words = TextMobject(
            "\\centering Associated\\\\", 
            "transformation"
        )
        words.set_color_by_tex("transformation", BLUE)
        words.add_background_rectangle()
        brace.put_at_tip(words)
        VGroup(matrix, brace, words).to_corner(UP+LEFT)

        self.play(Transform(
            self.u_hat.coords, matrix
        ))
        self.play(
            GrowFromCenter(brace),
            Write(words, run_time = 2)
        )
        self.wait()
        self.matrix_words = words

    def transform_basis_vectors(self):
        start_state = list(self.get_mobjects())
        bases = self.get_basis_vectors()
        for b, char in zip(bases, ["x", "y"]):
            b.proj = get_vect_mob_projection(b, self.u_hat)
            b.proj_line = DashedLine(
                b.get_end(), b.proj.get_end(),
                dash_length = 0.05
            )
            b.proj.label = TexMobject("u_%s"%char)
            b.proj.label.set_color(b.get_color())
            b.scaled_proj = b.proj.copy().scale(self.scalar)
            b.scaled_proj.label = TexMobject("3u_%s"%char)
            b.scaled_proj.label.set_color(b.get_color())
            for v, direction in zip([b.proj, b.scaled_proj], [UP, UP+LEFT]):
                v.label.add_background_rectangle()
                v.label.next_to(v.get_end(), direction)

        self.play(*list(map(ShowCreation, bases)))
        for b in bases:
            mover = b.copy()
            self.play(ShowCreation(b.proj_line))
            self.play(Transform(mover, b.proj))
            self.play(Write(b.proj.label))
            self.wait()
            self.play(
                Transform(mover, b.scaled_proj),
                Transform(b.proj.label, b.scaled_proj.label)
            )
            self.wait()
        self.play(*list(map(FadeOut, [
            mob
            for mob in self.get_mobjects()
            if mob not in start_state
        ])))

    def transform_some_vector(self):
        words = TextMobject(
            "\\centering Project\\\\",
            "then scale"
        )
        project, then_scale = words.split()
        words.add_background_rectangle()
        words.move_to(self.matrix_words, aligned_edge = UP)

        v = Vector([3, -1], color = MAROON_B)
        proj = get_vect_mob_projection(v, self.u_hat)
        proj_line = DashedLine(
            v.get_end(), proj.get_end(),
            color = v.get_color()
        )
        mover = v.copy()

        self.play(ShowCreation(v))
        self.play(Transform(self.matrix_words, words))
        self.play(ShowCreation(proj_line))
        self.play(
            Transform(mover, proj),
            project.set_color, YELLOW
        )
        self.wait()
        self.play(
            mover.scale, self.scalar,
            then_scale.set_color, YELLOW
        )
        self.wait()

class NoticeWhatHappenedHere(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            Notice what 
            happened here
        """)
        self.change_student_modes(*["pondering"]*3)
        self.random_blink()

class AbstractNumericAssociation(AssociationBetweenMatricesAndVectors):
    CONFIG = {
        "matrices" : [
            [["u_x", "u_y"]]
        ]
    }

class TwoDOneDTransformationSeparateSpace(Scene):
    CONFIG = {
        "v_coords" : [4, 1]
    }
    def construct(self):
        width = FRAME_X_RADIUS-1
        plane = NumberPlane(x_radius = 6, y_radius = 7)
        squish_plane = plane.copy()
        i_hat = Vector([1, 0], color = X_COLOR)
        j_hat = Vector([0, 1], color = Y_COLOR)
        vect = Vector(self.v_coords, color = YELLOW)
        plane.add(vect, i_hat, j_hat)
        plane.set_width(FRAME_X_RADIUS)
        plane.to_edge(LEFT, buff = 0)
        plane.remove(vect, i_hat, j_hat)

        squish_plane.apply_function(
            lambda p : np.dot(p, [4, 1, 0])*RIGHT
        )
        squish_plane.add(Vector(self.v_coords[0]*RIGHT, color = X_COLOR))
        squish_plane.add(Vector(self.v_coords[1]*RIGHT, color = Y_COLOR))
        squish_plane.scale(width/(FRAME_WIDTH))
        plane.add(i_hat, j_hat)

        number_line = NumberLine().stretch_to_fit_width(width)
        number_line.to_edge(RIGHT)
        squish_plane.move_to(number_line)

        numbers = number_line.get_numbers(*list(range(-6, 8, 2)))
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        v_line.set_color(GREY)
        v_line.set_stroke(width = 10)

        matrix = Matrix([self.v_coords])
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.next_to(number_line, UP, buff = LARGE_BUFF)
        v_coords = Matrix(self.v_coords)
        v_coords.set_column_colors(YELLOW)
        v_coords.scale(0.75)
        v_coords.next_to(vect.get_end(), RIGHT)
        for array in matrix, v_coords:
            array.add_to_back(BackgroundRectangle(array))

        start_words = TextMobject(
            "\\centering Any time you have a \\\\",
            "2d-to-1d linear transform..."
        )
        end_words = TextMobject(
            "\\centering ...it's associated \\\\",
            "with some vector",
        )
        for words in start_words, end_words:
            words.add_background_rectangle()
            words.scale(0.8)
        start_words.next_to(ORIGIN, RIGHT, buff = MED_SMALL_BUFF).to_edge(UP)
        end_words.next_to(ORIGIN, DOWN+LEFT, buff = MED_SMALL_BUFF/2)

        self.play(*list(map(ShowCreation, [
            plane, number_line, v_line
        ]))+[
            Write(numbers, run_time = 2)
        ])
        self.play(Write(start_words, run_time = 2))
        self.play(Write(matrix, run_time = 1))
        mover = plane.copy()
        interim = plane.copy().scale(0.8).move_to(number_line)
        for target in interim, squish_plane:
            self.play(
                Transform(mover, target),
                Animation(plane),
                Animation(start_words),
                run_time = 1,
            )
        self.wait()
        self.play(Transform(start_words.copy(), end_words))
        self.play(ShowCreation(vect))
        self.play(Transform(matrix.copy(), v_coords))
        self.wait()

class IsntThisBeautiful(TeacherStudentsScene):
    def construct(self):
        self.teacher.look(DOWN+LEFT)
        self.teacher_says(
            "Isn't this", "beautiful",
            target_mode = "surprised"
        )
        for student in self.get_students():
            self.play(student.change_mode, "happy")
        self.random_blink()
        duality_words = TextMobject(
            "It's called", "duality"
        )
        duality_words[1].set_color_by_gradient(BLUE, YELLOW)
        self.teacher_says(duality_words)
        self.random_blink()

class RememberGraphDuality(Scene):
    def construct(self):
        words = TextMobject("""
            \\centering
            Some of you may remember an 
            early video I did on graph duality
        """)
        words.to_edge(UP)
        self.play(Write(words))
        self.wait()

class LooseDualityDescription(Scene):
    def construct(self):
        duality = TextMobject("Duality")
        duality.set_color_by_gradient(BLUE, YELLOW)
        arrow = TexMobject("\\Leftrightarrow")
        words = TextMobject("Natural-but-surprising", "correspondence")
        words[1].set_color_by_gradient(BLUE, YELLOW)
        VGroup(duality, arrow, words).arrange(buff = MED_SMALL_BUFF)

        self.add(duality)
        self.play(Write(arrow))
        self.play(Write(words))
        self.wait()

class DualOfAVector(ScaleUpUHat):
    pass #Exact copy

class DualOfATransform(TwoDOneDTransformationSeparateSpace):
    pass #Exact copy

class UnderstandingProjection(ProjectOntoUnitVectorNumberline):
    pass ##Copy

class ShowQualitativeDotProductValuesCopy(ShowQualitativeDotProductValues):
    pass

class TranslateToTheWorldOfTransformations(TwoDOneDMatrixMultiplication):
    CONFIG = {
        "order_left_to_right" : True,
    }
    def construct(self):
        v1, v2 = [
            Matrix(["x_%d"%n, "y_%d"%n])
            for n in (1, 2)
        ]
        v1.set_column_colors(V_COLOR)
        v2.set_column_colors(W_COLOR)
        dot = TexMobject("\\cdot")

        matrix = Matrix([["x_1", "y_1"]])
        matrix.set_column_colors(X_COLOR, Y_COLOR)

        dot_product = VGroup(v1, dot, v2)
        dot_product.arrange(RIGHT)
        matrix.next_to(v2, LEFT)

        brace = Brace(matrix, UP)
        word = TextMobject("Transform")
        word.set_width(brace.get_width())
        brace.put_at_tip(word)
        word.set_color(BLUE)

        self.play(Write(dot_product))
        self.wait()
        self.play(
            dot.set_fill, BLACK, 0,
            Transform(v1, matrix),
        )
        self.play(
            GrowFromCenter(brace),
            Write(word)
        )
        self.wait()
        self.show_product(v1, v2)
        self.wait()

class NumericalAssociationSilliness(GeneralTwoDOneDMatrixMultiplication):
    pass #copy

class YouMustKnowPersonality(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            You should learn a
            vector's personality
        """)
        self.random_blink()
        self.change_student_modes("pondering")
        self.random_blink()
        self.change_student_modes("pondering", "plain", "pondering")
        self.random_blink()

class WhatTheVectorWantsToBe(Scene):
    CONFIG = {
        "v_coords" : [2, 4]
    }
    def construct(self):
        width = FRAME_X_RADIUS-1
        plane = NumberPlane(x_radius = 6, y_radius = 7)
        squish_plane = plane.copy()
        i_hat = Vector([1, 0], color = X_COLOR)
        j_hat = Vector([0, 1], color = Y_COLOR)
        vect = Vector(self.v_coords, color = YELLOW)
        plane.add(vect, i_hat, j_hat)
        plane.set_width(FRAME_X_RADIUS)
        plane.to_edge(LEFT, buff = 0)
        plane.remove(vect, i_hat, j_hat)

        squish_plane.apply_function(
            lambda p : np.dot(p, [4, 1, 0])*RIGHT
        )
        squish_plane.add(Vector(self.v_coords[1]*RIGHT, color = Y_COLOR))
        squish_plane.add(Vector(self.v_coords[0]*RIGHT, color = X_COLOR))        
        squish_plane.scale(width/(FRAME_WIDTH))
        plane.add(j_hat, i_hat)

        number_line = NumberLine().stretch_to_fit_width(width)
        number_line.to_edge(RIGHT)
        squish_plane.move_to(number_line)

        numbers = number_line.get_numbers(*list(range(-6, 8, 2)))
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        v_line.set_color(GREY)
        v_line.set_stroke(width = 10)

        matrix = Matrix([self.v_coords])
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.next_to(number_line, UP, buff = LARGE_BUFF)
        v_coords = Matrix(self.v_coords)
        v_coords.set_column_colors(YELLOW)
        v_coords.scale(0.75)
        v_coords.next_to(vect.get_end(), RIGHT)
        for array in matrix, v_coords:
            array.add_to_back(BackgroundRectangle(array))

        words = TextMobject(
            "What the vector",
            "\\\\ wants",
            "to be"
        )
        words[1].set_color(BLUE)
        words.next_to(matrix, UP, buff = MED_SMALL_BUFF)

        self.add(plane, v_line, number_line, numbers)
        self.play(ShowCreation(vect))
        self.play(Write(v_coords))
        self.wait()
        self.play(
            Transform(v_coords.copy(), matrix),
            Write(words)
        )
        self.play(
            Transform(plane.copy(), squish_plane, run_time = 3),
            *list(map(Animation, [
                words,
                matrix,
                plane,
                vect, 
                v_coords
            ]))
        )
        self.wait()

class NextVideo(Scene):
    def construct(self):
        title = TextMobject("""
            Next video: Cross products in the
            light of linear transformations
        """)
        title.set_height(1.2)
        title.to_edge(UP, buff = MED_SMALL_BUFF/2)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN)
        VGroup(title, rect).show()

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()

















