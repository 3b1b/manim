from manimlib.imports import *

from ka_playgrounds.circuits import Resistor, Source, LongResistor

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject(
            "``On this quiz, I asked you to find the determinant of a",
            "2x3 matrix.",
            "Some of you, to my great amusement, actually tried to do this.''" 
        )
        words.set_width(FRAME_WIDTH - 2)
        words.to_edge(UP)
        words[1].set_color(GREEN)
        author = TextMobject("-(Via mathprofessorquotes.com, no name listed)")
        author.set_color(YELLOW)
        author.scale(0.7)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.wait(2)
        self.play(Write(author, run_time = 3))
        self.wait()

class AnotherFootnote(TeacherStudentsScene):
    def construct(self):
        self.teacher.look(LEFT)
        self.teacher_says(
            "More footnotes!",
            target_mode = "surprised",
            run_time = 1
        )
        self.random_blink(2)

class ColumnsRepresentBasisVectors(Scene):
    def construct(self):
        matrix = Matrix([[3, 1], [4, 1], [5, 9]])
        i_hat_words, j_hat_words = [
            TextMobject("Where $\\hat{\\%smath}$ lands"%char)
            for char in ("i", "j")
        ]
        i_hat_words.set_color(X_COLOR)
        i_hat_words.next_to(ORIGIN, LEFT).to_edge(UP)
        j_hat_words.set_color(Y_COLOR)
        j_hat_words.next_to(ORIGIN, RIGHT).to_edge(UP)
        question = TextMobject("How to interpret?")
        question.next_to(matrix, UP)
        question.set_color(YELLOW)

        self.add(matrix)
        self.play(Write(question, run_time = 2))
        self.wait()
        self.play(FadeOut(question))
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
                    ApplyMethod(m.set_color, words.get_color())
                    for m in matrix.get_mob_matrix()[:,i]
                ]
            )
        self.wait(2)
        self.put_in_thought_bubble()

    def put_in_thought_bubble(self):
        everything = VMobject(*self.get_mobjects())
        randy = Randolph().to_corner()
        bubble = randy.get_bubble()

        self.play(FadeIn(randy))
        self.play(
            ApplyFunction(
                lambda m : bubble.position_mobject_inside(
                    m.set_height(2.5)
                ),
                everything
            ),
            ShowCreation(bubble),
            randy.change_mode, "pondering"
        )
        self.play(Blink(randy))
        self.wait()
        self.play(randy.change_mode, "surprised")
        self.wait()

class Symbolic2To3DTransform(Scene):
    def construct(self):
        func = TexMobject("L(", "\\vec{\\textbf{v}}", ")")
        input_array = Matrix([2, 7])
        input_array.set_color(YELLOW)
        in_arrow = Arrow(LEFT, RIGHT, color = input_array.get_color())
        func[1].set_color(input_array.get_color())
        output_array = Matrix([1, 8, 2])
        output_array.set_color(PINK)
        out_arrow = Arrow(LEFT, RIGHT, color = output_array.get_color())
        VMobject(
            input_array, in_arrow, func, out_arrow, output_array
        ).arrange(RIGHT, buff = SMALL_BUFF)

        input_brace = Brace(input_array, DOWN)
        input_words = input_brace.get_text("2d input")
        output_brace = Brace(output_array, UP)
        output_words = output_brace.get_text("3d output")
        input_words.set_color(input_array.get_color())
        output_words.set_color(output_array.get_color())


        self.add(func, input_array)
        self.play(
            GrowFromCenter(input_brace),
            Write(input_words)
        )
        mover = input_array.copy()
        self.play(
            Transform(mover, Dot().move_to(func)),
            ShowCreation(in_arrow),
            rate_func = rush_into
        )
        self.play(
            Transform(mover, output_array),
            ShowCreation(out_arrow),
            rate_func = rush_from
        )
        self.play(
            GrowFromCenter(output_brace),
            Write(output_words)
        )
        self.wait()

class PlaneStartState(LinearTransformationScene):
    def construct(self):
        self.add_title("Input space")
        labels = self.get_basis_vector_labels()
        self.play(*list(map(Write, labels)))
        self.wait()

class OutputIn3dWords(Scene):
    def construct(self):
        words = TextMobject("Output in 3d")
        words.scale(1.5)
        self.play(Write(words))
        self.wait()

class OutputIn3d(Scene):
    pass

class ShowSideBySide2dTo3d(Scene):
    pass

class AnimationLaziness(Scene):
    def construct(self):
        self.add(TextMobject("But there is some animation laziness..."))

class DescribeColumnsInSpecificTransformation(Scene):
    def construct(self):
        matrix = Matrix([
            [2, 0],
            [-1, 1],
            [-2, 1],
        ])
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        mob_matrix = matrix.get_mob_matrix()
        i_col, j_col = [VMobject(*mob_matrix[:,i]) for i in (0, 1)]
        for col, char, vect in zip([i_col, j_col], ["i", "j"], [UP, DOWN]):
            color = col[0].get_color()
            col.words = TextMobject("Where $\\hat\\%smath$ lands"%char)
            col.words.next_to(matrix, vect, buff = LARGE_BUFF)
            col.words.set_color(color)
            col.arrow = Arrow(
                col.words.get_edge_center(-vect),
                col.get_edge_center(vect),
                color = color
            )

        self.play(Write(matrix.get_brackets()))
        self.wait()
        for col in i_col, j_col:
            self.play(
                Write(col),            
                ShowCreation(col.arrow),
                Write(col.words, run_time = 1)
            )
            self.wait()

class CountRowsAndColumns(Scene):
    def construct(self):
        matrix = Matrix([
            [2, 0],
            [-1, 1],
            [-2, 1],
        ])
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        rows_brace = Brace(matrix, LEFT)
        rows_words = rows_brace.get_text("3", "rows")
        rows_words.set_color(PINK)
        cols_brace = Brace(matrix, UP)
        cols_words = cols_brace.get_text("2", "columns")
        cols_words.set_color(TEAL)
        title = TexMobject("3", "\\times", "2", "\\text{ matrix}")
        title.to_edge(UP)

        self.add(matrix)
        self.play(
            GrowFromCenter(rows_brace),
            Write(rows_words, run_time = 2)
        )
        self.play(
            GrowFromCenter(cols_brace),
            Write(cols_words, run_time = 2)
        )
        self.wait()
        self.play(
            rows_words[0].copy().move_to, title[0],
            cols_words[0].copy().move_to, title[2],
            Write(VMobject(title[1], title[3]))
        )
        self.wait()

class WriteColumnSpaceDefinition(Scene):
    def construct(self):
        matrix = Matrix([
            [2, 0],
            [-1, 1],
            [-2, 1],
        ])
        matrix.set_column_colors(X_COLOR, Y_COLOR)

        brace = Brace(matrix)
        words = VMobject(
            TextMobject("Span", "of columns"),
            TexMobject("\\Updownarrow"),
            TextMobject("``Column space''")
        )
        words.arrange(DOWN, buff = 0.1)
        words.next_to(brace, DOWN)
        words[0][0].set_color(PINK)
        words[2].set_color(TEAL)
        words[0].add_background_rectangle()
        words[2].add_background_rectangle()
        VMobject(matrix, brace, words).center()

        self.add(matrix)
        self.play(
            GrowFromCenter(brace),
            Write(words, run_time = 2)
        )
        self.wait()

class MatrixInTheWild(Scene):
    def construct(self):
        randy = Randolph(color = PINK)
        randy.look(LEFT)
        randy.to_corner()
        matrix = Matrix([
            [3, 1],
            [4, 1],
            [5, 9],
        ])
        matrix.next_to(randy, RIGHT, buff = LARGE_BUFF, aligned_edge = DOWN)
        bubble = randy.get_bubble(height = 4)
        bubble.make_green_screen()
        VMobject(randy, bubble, matrix).to_corner(UP+LEFT, buff = MED_SMALL_BUFF)

        self.add(randy)
        self.play(Write(matrix))
        self.play(randy.look, RIGHT, run_time = 0.5)
        self.play(randy.change_mode, "sassy")
        self.play(Blink(randy))
        self.play(
            ShowCreation(bubble),
            randy.change_mode, "pondering"
        )
        # self.play(matrix.set_column_colors, X_COLOR, Y_COLOR)
        self.wait()
        for x in range(3):
            self.play(Blink(randy))
            self.wait(2)
        new_matrix = Matrix([[3, 1, 4], [1, 5, 9]])
        new_matrix.move_to(matrix, aligned_edge = UP+LEFT)
        self.play(
            Transform(matrix, new_matrix),
            FadeOut(bubble)
        )
        self.remove(matrix)
        matrix = new_matrix
        self.add(matrix)
        self.play(randy.look, DOWN+RIGHT, run_time = 0.5)
        self.play(randy.change_mode, "confused")
        self.wait()
        self.play(Blink(randy))
        self.wait()

        top_brace = Brace(matrix, UP)
        top_words = top_brace.get_text("3 basis vectors")
        top_words.set_submobject_colors_by_gradient(GREEN, RED, BLUE)
        side_brace = Brace(matrix, RIGHT)
        side_words = side_brace.get_text("""
            2 coordinates for
            each landing spots
        """)
        side_words.set_color(YELLOW)

        self.play(
            GrowFromCenter(top_brace),
            Write(top_words),
            matrix.set_column_colors, X_COLOR, Y_COLOR, Z_COLOR
        )
        self.play(randy.change_mode, "happy")
        self.play(
            GrowFromCenter(side_brace),
            Write(side_words, run_time = 2)
        )
        self.play(Blink(randy))
        self.wait()

class ThreeDToTwoDInput(Scene):
    pass

class ThreeDToTwoDInputWords(Scene):
    def construct(self):
        words = TextMobject("3d input")
        words.scale(2)
        self.play(Write(words))
        self.wait()

class ThreeDToTwoDOutput(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "foreground_plane_kwargs" : {
            "color" : GREY,
            "x_radius" : FRAME_X_RADIUS,
            "y_radius" : FRAME_Y_RADIUS,
            "secondary_line_ratio" : 0
        },
    }
    def construct(self):
        title = TextMobject("Output in 2d")
        title.to_edge(UP, buff = SMALL_BUFF)
        subwords = TextMobject("""
            (only showing basis vectors,
            full 3d grid would be a mess)
        """)
        subwords.scale(0.75)
        subwords.next_to(title, DOWN)
        for words in title, subwords:
            words.add_background_rectangle()

        self.add(title)
        i, j, k = it.starmap(self.add_vector, [
            ([3, 1], X_COLOR),
            ([1, 2], Y_COLOR),
            ([-2, -2], Z_COLOR)
        ])
        pairs = [
            (i, "L(\\hat\\imath)"),
            (j, "L(\\hat\\jmath)"),
            (k, "L(\\hat k)")
        ]
        for v, tex in pairs:
            self.label_vector(v, tex)
        self.play(Write(subwords))
        self.wait()

class ThreeDToTwoDSideBySide(Scene):
    pass

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

class TwoDTo1DTransform(LinearTransformationScene):
    CONFIG = {
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_X_RADIUS,
            "y_radius" : FRAME_Y_RADIUS,
            "secondary_line_ratio" : 1
        },
        "t_matrix" : [[1, 0], [2, 0]],
    }
    def construct(self):
        line = NumberLine()
        plane_words = TextMobject("2d space")
        plane_words.next_to(self.j_hat, UP, buff = MED_SMALL_BUFF)
        plane_words.add_background_rectangle()
        line_words = TextMobject("1d space (number line)")
        line_words.next_to(line, UP)


        self.play(Write(plane_words))
        self.wait()
        self.remove(plane_words)
        mobjects = self.get_mobjects()
        self.play(
            *list(map(FadeOut, mobjects)) + [ShowCreation(line)]
        )
        self.play(Write(line_words))
        self.wait()
        self.remove(line_words)
        self.play(*list(map(FadeIn, mobjects)))
        self.apply_transposed_matrix(self.t_matrix)
        self.play(Write(VMobject(*line.get_number_mobjects())))
        self.wait()
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
        matrix_group.arrange(buff = MED_SMALL_BUFF)
        matrix_group.to_edge(UP)
        entries = matrix.get_entries()

        self.play(Write(matrix_words), Write(matrix.get_brackets()))
        for i, vect in enumerate([self.i_hat, self.j_hat]):
            self.play(vect.rotate, np.pi/12, rate_func = wiggle)
            self.play(Write(vect.words))
            self.wait()
            self.play(vect.words[1].copy().move_to, entries[i])
            self.wait()

class TwoDTo1DTransformWithDots(TwoDTo1DTransform):
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
        func = self.get_matrix_transformation(self.t_matrix)
        new_dots = VMobject(*[
            Dot(
                func(dot.get_center()), 
                color = dot.get_color(),
                radius = dot.radius
            )
            for dot in dots
        ])
        words = TextMobject(
            "Line of dots remains evenly spaced"
        )
        words.next_to(line, UP, buff = MED_SMALL_BUFF)

        self.play(Write(dots))
        self.apply_transposed_matrix(
            self.t_matrix,
            added_anims = [Transform(dots, new_dots)]
        )
        self.play(Write(words))
        self.wait()

class NextVideo(Scene):
    def construct(self):
        title = TextMobject("""
            Next video: Dot products and duality
        """)
        title.set_width(FRAME_WIDTH - 2)
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()     

class DotProductPreview(VectorScene):
    CONFIG = {
        "v_coords" : [3, 1],
        "w_coords" : [2, -1],
        "v_color" : YELLOW,
        "w_color" : MAROON_C,

    }
    def construct(self):
        self.lock_in_faded_grid()
        self.add_symbols()
        self.add_vectors()
        self.grow_number_line()
        self.project_w()
        self.show_scaling()


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

    def add_vectors(self):
        self.v = Vector(self.v_coords, color = self.v_color)
        self.w = Vector(self.w_coords, color = self.w_color)
        self.play(ShowCreation(self.v))
        self.play(ShowCreation(self.w))

    def grow_number_line(self):
        line = NumberLine(stroke_width = 2).add_numbers()
        line.rotate(self.v.get_angle())
        self.play(Write(line), Animation(self.v))
        self.play(
            line.set_color, self.v.get_color(), 
            Animation(self.v),
            rate_func = there_and_back
        )
        self.wait()

    def project_w(self):
        dot_product = np.dot(self.v.get_end(), self.w.get_end())
        v_norm, w_norm = [
            get_norm(vect.get_end())
            for vect in (self.v, self.w)
        ]
        projected_w = Vector(
            self.v.get_end()*dot_product/(v_norm**2),
            color = self.w.get_color()
        )
        projection_line = Line(
            self.w.get_end(), projected_w.get_end(),
            color = GREY
        )

        self.play(ShowCreation(projection_line))
        self.add(self.w.copy().fade())
        self.play(Transform(self.w, projected_w))
        self.wait()

    def show_scaling(self):
        dot_product = np.dot(self.v.get_end(), self.w.get_end())
        start_brace, interim_brace, final_brace = braces = [
            Brace(
                Line(ORIGIN, norm*RIGHT), 
                UP
            )
            for norm in (1, self.v.get_length(), dot_product)
        ]
        length_texs = list(it.starmap(TexMobject, [
            ("1",),
            ("\\text{Scale by }", "||\\vec{\\textbf{v}}||",),
            ("\\text{Length of}", "\\text{ scaled projection}",),
        ]))
        length_texs[1][1].set_color(self.v_color)
        length_texs[2][1].set_color(self.w_color)
        for brace, tex_mob in zip(braces, length_texs):
            tex_mob.add_background_rectangle()
            brace.put_at_tip(tex_mob, buff = SMALL_BUFF)
            brace.add(tex_mob)
            brace.rotate(self.v.get_angle())
        new_w = self.w.copy().scale(self.v.get_length())

        self.play(Write(start_brace))
        self.wait()
        self.play(
            Transform(start_brace, interim_brace),
            Transform(self.w, new_w)
        )
        self.wait()
        self.play(
            Transform(start_brace, final_brace)
        )
        self.wait()


















