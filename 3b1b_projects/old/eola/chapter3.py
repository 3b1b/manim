from manimlib.imports import *

def curvy_squish(point):
    x, y, z = point
    return (x+np.cos(y))*RIGHT + (y+np.sin(x))*UP

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject([
            "Unfortunately, no one can be told what the",
            "Matrix",
            "is. You have to",
            "see it for yourself.",
        ])
        words.set_width(FRAME_WIDTH - 2)
        words.to_edge(UP)
        words.split()[1].set_color(GREEN)
        words.split()[3].set_color(BLUE)
        author = TextMobject("-Morpheus")
        author.set_color(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)
        comment = TextMobject("""
            (Surprisingly apt words on the importance 
            of understanding matrix operations visually.)
        """)
        comment.next_to(author, DOWN, buff = 1)

        self.play(FadeIn(words))
        self.wait(3)
        self.play(Write(author, run_time = 3))
        self.wait()
        self.play(Write(comment))
        self.wait()

class Introduction(TeacherStudentsScene):
    def construct(self):
        title = TextMobject(["Matrices as", "Linear transformations"])
        title.to_edge(UP)
        title.set_color(YELLOW)
        linear_transformations = title.split()[1]
        self.add(*title.split())
        self.setup()
        self.teacher_says("""
            Listen up folks, this one is
            particularly important
        """, height = 3)
        self.random_blink(2)
        self.teacher_thinks("", height = 3)
        self.remove(linear_transformations)
        everything = VMobject(*self.get_mobjects())
        def spread_out(p):
            p = p + 2*DOWN
            return (FRAME_X_RADIUS+FRAME_Y_RADIUS)*p/get_norm(p)
        self.play(
            ApplyPointwiseFunction(spread_out, everything),
            ApplyFunction(
                lambda m : m.center().to_edge(UP), 
                linear_transformations
            )
        )

class MatrixVectorMechanicalMultiplication(NumericalMatrixMultiplication):
    CONFIG = {
        "left_matrix" : [[1, -3], [2, 4]],
        "right_matrix" : [[5], [7]]
    }

class PostponeHigherDimensions(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.student_says("What about 3 dimensions?")
        self.random_blink()
        self.teacher_says("All in due time,\\\\ young padawan")
        self.random_blink()

class DescribeTransformation(Scene):
    def construct(self):
        self.add_title()
        self.show_function()

    def add_title(self):
        title = TextMobject(["Linear", "transformation"])
        title.to_edge(UP)
        linear, transformation = title.split()
        brace = Brace(transformation, DOWN)
        function = TextMobject("function").next_to(brace, DOWN)
        function.set_color(YELLOW)

        self.play(Write(title))
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(function),
            ApplyMethod(linear.fade)
        )

    def show_function(self):
        f_of_x = TexMobject("f(x)")
        L_of_v = TexMobject("L(\\vec{\\textbf{v}})")
        nums = [5, 2, -3]
        num_inputs = VMobject(*list(map(TexMobject, list(map(str, nums)))))
        num_outputs = VMobject(*[
            TexMobject(str(num**2))
            for num in nums
        ])
        for mob in num_inputs, num_outputs:
            mob.arrange(DOWN, buff = 1)
        num_inputs.next_to(f_of_x, LEFT, buff = 1)
        num_outputs.next_to(f_of_x, RIGHT, buff = 1)
        f_point = VectorizedPoint(f_of_x.get_center())

        input_vect = Matrix([5, 7])
        input_vect.next_to(L_of_v, LEFT, buff = 1)
        output_vect = Matrix([2, -3])
        output_vect.next_to(L_of_v, RIGHT, buff = 1)

        vector_input_words = TextMobject("Vector input")
        vector_input_words.set_color(MAROON_C)
        vector_input_words.next_to(input_vect, DOWN)
        vector_output_words = TextMobject("Vector output")
        vector_output_words.set_color(BLUE)
        vector_output_words.next_to(output_vect, DOWN)

        self.play(Write(f_of_x, run_time = 1))
        self.play(Write(num_inputs, run_time = 2))
        self.wait()
        for mob in f_point, num_outputs:
            self.play(Transform(
                num_inputs, mob,
                lag_ratio = 0.5
            ))
        self.wait()

        self.play(
            FadeOut(num_inputs),
            Transform(f_of_x, L_of_v)
        )
        self.play(
            Write(input_vect),
            Write(vector_input_words)
        )
        self.wait()
        for mob in f_point, output_vect:
            self.play(Transform(
                input_vect, mob,
                lag_ratio = 0.5
            ))
        self.play(Write(vector_output_words))
        self.wait()

class WhyConfuseWithTerminology(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.student_says("Why confuse us with \\\\ redundant terminology?")
        other_students = [self.get_students()[i] for i in (0, 2)]
        self.play(*[
            ApplyMethod(student.change_mode, "confused")
            for student in other_students
        ])
        self.random_blink()
        self.wait()
        statement = TextMobject([
            "The word",
            "``transformation''",
            "suggests \\\\ that you think using",
            "movement",
        ])
        statement.split()[1].set_color(BLUE)
        statement.split()[-1].set_color(YELLOW)
        self.teacher_says(statement, width = 10)
        self.play(*[
            ApplyMethod(student.change_mode, "happy")
            for student in other_students
        ])
        self.random_blink()
        self.wait()

class ThinkinfOfFunctionsAsGraphs(VectorScene):
    def construct(self):
        axes = self.add_axes()
        graph = FunctionGraph(lambda x : x**2, x_min = -2, x_max = 2)
        name = TexMobject("f(x) = x^2")
        name.next_to(graph, RIGHT).to_edge(UP)
        point = Dot(graph.point_from_proportion(0.8))
        point_label = TexMobject("(2, f(2))")
        point_label.next_to(point.get_center(), DOWN+RIGHT, buff = 0.1)

        self.play(ShowCreation(graph))
        self.play(Write(name, run_time = 1))
        self.play(
            ShowCreation(point),
            Write(point_label),
            run_time = 1
        )
        self.wait()

        def collapse_func(p):
            return np.dot(p, [RIGHT, RIGHT, OUT]) + (FRAME_Y_RADIUS+1)*DOWN
        self.play(
            ApplyPointwiseFunction(collapse_func, axes),
            ApplyPointwiseFunction(collapse_func, graph),
            ApplyMethod(point.shift, 10*DOWN),
            ApplyMethod(point_label.shift, 10*DOWN),
            ApplyPointwiseFunction(collapse_func, name),
            run_time = 2
        )
        self.clear()
        words = TextMobject(["Instead think about", "\\emph{movement}"])
        words.split()[-1].set_color(YELLOW)
        self.play(Write(words))
        self.wait()

class TransformJustOneVector(VectorScene):
    def construct(self):
        self.lock_in_faded_grid()
        v1_coords = [-3, 1]
        t_matrix = [[0, -1], [2, -1]]
        v1 = Vector(v1_coords)
        v2 = Vector(
            np.dot(np.array(t_matrix).transpose(), v1_coords),
            color = PINK
        )
        for v, word in (v1, "Input"), (v2, "Output"):
            v.label = TextMobject("%s vector"%word)
            v.label.next_to(v.get_end(), UP)
            v.label.set_color(v.get_color())
            self.play(ShowCreation(v))
            self.play(Write(v.label))
        self.wait()
        self.remove(v2)
        self.play(
            Transform(
                v1.copy(), v2, 
                path_arc = -np.pi/2, run_time = 3
            ),
            ApplyMethod(v1.fade)
        )
        self.wait()

class TransformManyVectors(LinearTransformationScene):
    CONFIG = {
        "transposed_matrix" : [[2, 1], [1, 2]],
        "use_dots" : False,
    }
    def construct(self):
        self.lock_in_faded_grid()
        vectors = VMobject(*[
            Vector([x, y])
            for x in np.arange(-int(FRAME_X_RADIUS)+0.5, int(FRAME_X_RADIUS)+0.5)
            for y in np.arange(-int(FRAME_Y_RADIUS)+0.5, int(FRAME_Y_RADIUS)+0.5)
        ])
        vectors.set_submobject_colors_by_gradient(PINK, YELLOW)
        t_matrix = self.transposed_matrix
        transformed_vectors = VMobject(*[
            Vector(
                np.dot(np.array(t_matrix).transpose(), v.get_end()[:2]),
                color = v.get_color()
            )
            for v in vectors.split()
        ])

        self.play(ShowCreation(vectors, lag_ratio = 0.5))
        self.wait()
        if self.use_dots:
            self.play(Transform(
                vectors, self.vectors_to_dots(vectors),
                run_time = 3,
                lag_ratio = 0.5
            ))
            transformed_vectors = self.vectors_to_dots(transformed_vectors)
            self.wait()
        self.play(Transform(
            vectors, transformed_vectors,
            run_time = 3,
            path_arc = -np.pi/2
        ))
        self.wait()
        if self.use_dots:
            self.play(Transform(
                vectors, self.dots_to_vectors(vectors),
                run_time = 2,
                lag_ratio = 0.5
            ))
            self.wait()

    def vectors_to_dots(self, vectors):
        return VMobject(*[
            Dot(v.get_end(), color = v.get_color())
            for v in vectors.split()
        ])

    def dots_to_vectors(self, dots):
        return VMobject(*[
            Vector(dot.get_center(), color = dot.get_color())
            for dot in dots.split()
        ])

class TransformManyVectorsAsPoints(TransformManyVectors):
    CONFIG = {
        "use_dots" : True
    }

class TransformInfiniteGrid(LinearTransformationScene):
    CONFIG = {
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_WIDTH,
            "y_radius" : FRAME_HEIGHT,
        },
        "show_basis_vectors" : False
    }
    def construct(self):
        self.setup()
        self.play(ShowCreation(
            self.plane, run_time = 3, lag_ratio = 0.5
        ))
        self.wait()
        self.apply_transposed_matrix([[2, 1], [1, 2]])
        self.wait()

class TransformInfiniteGridWithBackground(TransformInfiniteGrid):
    CONFIG = {
        "include_background_plane" : True,
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_WIDTH,
            "y_radius" : FRAME_HEIGHT,
            "secondary_line_ratio" : 0
        },

    }

class ApplyComplexFunction(LinearTransformationScene):
    CONFIG = {
        "function" : lambda z : 0.5*z**2,
        "show_basis_vectors" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_X_RADIUS,
            "y_radius" : FRAME_Y_RADIUS,
            "secondary_line_ratio" : 0
        },
    }
    def construct(self):
        self.setup()
        self.plane.prepare_for_nonlinear_transform(100)
        self.wait()
        self.play(ApplyMethod(
            self.plane.apply_complex_function, self.function,
            run_time = 5,
            path_arc = np.pi/2
        ))
        self.wait()

class ExponentialTransformation(ApplyComplexFunction):
    CONFIG = {
        "function" : np.exp,
    }

class CrazyTransformation(ApplyComplexFunction):
    CONFIG = {
        "function" : lambda z : np.sin(z)**2 + np.sinh(z)
    }    

class LookToWordLinear(Scene):
    def construct(self):
        title = TextMobject(["Linear ", "transformations"])
        title.to_edge(UP)
        faded_title = title.copy().fade()
        linear, transformation = title.split()
        faded_linear, faded_transformation = faded_title.split()
        linear_brace = Brace(linear, DOWN)
        transformation_brace = Brace(transformation, DOWN)
        function = TextMobject("function")
        function.set_color(YELLOW)
        function.next_to(transformation_brace, DOWN)
        new_sub_word = TextMobject("What does this mean?")
        new_sub_word.set_color(BLUE)
        new_sub_word.next_to(linear_brace, DOWN)

        self.add(
            faded_linear, transformation, 
            transformation_brace, function
        )
        self.wait()
        self.play(
            Transform(faded_linear, linear),
            Transform(transformation, faded_transformation),
            Transform(transformation_brace, linear_brace),
            Transform(function, new_sub_word),
            lag_ratio = 0.5
        )
        self.wait()

class IntroduceLinearTransformations(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
    }
    def construct(self):
        self.setup()
        self.wait()
        self.apply_transposed_matrix([[2, 1], [1, 2]])
        self.wait()

        lines_rule = TextMobject("Lines remain lines")
        lines_rule.shift(2*UP).to_edge(LEFT)
        origin_rule = TextMobject("Origin remains fixed")
        origin_rule.shift(2*UP).to_edge(RIGHT)
        arrow = Arrow(origin_rule, ORIGIN)
        dot = Dot(ORIGIN, radius = 0.1, color = RED)

        for rule in lines_rule, origin_rule:
            rule.add_background_rectangle()

        self.play(
            Write(lines_rule, run_time = 2),
        )
        self.wait()
        self.play(
            Write(origin_rule, run_time = 2),
            ShowCreation(arrow),
            GrowFromCenter(dot)
        )
        self.wait()

class ToThePedants(Scene):
    def construct(self):
        words = TextMobject([
            "To the pedants:\\\\",
        """
            Yeah yeah, I know that's not the formal definition
            for linear transformations, as seen in textbooks,
            but I'm building visual intuition here, and what 
            I've said is equivalent to the formal definition
            (which I'll get to later in the series).
        """])
        words.split()[0].set_color(RED)
        words.to_edge(UP)
        self.add(words)
        self.wait()

class SimpleLinearTransformationScene(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "transposed_matrix" : [[2, 1], [1, 2]]
    }
    def construct(self):
        self.setup()
        self.wait()
        self.apply_transposed_matrix(self.transposed_matrix)
        self.wait()

class SimpleNonlinearTransformationScene(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "words" : "Not linear: some lines get curved"
    }
    def construct(self):
        self.setup()
        self.wait()
        self.apply_nonlinear_transformation(self.func)
        words = TextMobject(self.words)
        words.to_corner(UP+RIGHT)
        words.set_color(RED)
        words.add_background_rectangle()
        self.play(Write(words))
        self.wait()

    def func(self, point):
        return curvy_squish(point)

class MovingOrigin(SimpleNonlinearTransformationScene):
    CONFIG = {
        "words" : "Not linear: Origin moves"
    }
    def setup(self):
        LinearTransformationScene.setup(self)
        dot = Dot(ORIGIN, color = RED)
        self.add_transformable_mobject(dot)

    def func(self, point):
        matrix_transform = self.get_matrix_transformation([[2, 0], [1, 1]])
        return matrix_transform(point) + 2*UP+3*LEFT

class SneakyNonlinearTransformation(SimpleNonlinearTransformationScene):
    CONFIG = {
        "words" : "\\dots"
    }
    def func(self, point):
        x, y, z = point
        new_x = np.sign(x)*FRAME_X_RADIUS*smooth(abs(x) / FRAME_X_RADIUS)
        new_y = np.sign(y)*FRAME_Y_RADIUS*smooth(abs(y) / FRAME_Y_RADIUS)
        return [new_x, new_y, 0]

class SneakyNonlinearTransformationExplained(SneakyNonlinearTransformation):
    CONFIG = {
        "words" : "Not linear: diagonal lines get curved"
    }
    def setup(self):
        LinearTransformationScene.setup(self)
        diag = Line(
            FRAME_Y_RADIUS*LEFT+FRAME_Y_RADIUS*DOWN,
            FRAME_Y_RADIUS*RIGHT + FRAME_Y_RADIUS*UP
        )
        diag.insert_n_curves(20)
        diag.make_smooth()
        diag.set_color(YELLOW)
        self.play(ShowCreation(diag))
        self.add_transformable_mobject(diag)

class GridLinesRemainParallel(SimpleLinearTransformationScene):
    CONFIG = {
        "transposed_matrix" : [
            [3, 0],
            [1, 2]
        ]
    }
    def construct(self):
        SimpleLinearTransformationScene.construct(self)
        text = TextMobject([
            "Grid lines remain",
            "parallel",
            "and",
            "evenly spaced",
        ])
        glr, p, a, es = text.split()
        p.set_color(YELLOW)
        es.set_color(GREEN)
        text.add_background_rectangle()
        text.shift(-text.get_bottom())
        self.play(Write(text))
        self.wait()

class Rotation(SimpleLinearTransformationScene):
    CONFIG = {
        "angle" : np.pi/3,
    }
    def construct(self):
        self.transposed_matrix = [
            [np.cos(self.angle), np.sin(self.angle)], 
            [-np.sin(self.angle), np.cos(self.angle)]
        ]
        SimpleLinearTransformationScene.construct(self)

class YetAnotherLinearTransformation(SimpleLinearTransformationScene):
    CONFIG = {
        "transposed_matrix" : [
            [-1, 1],
            [3, 2],
        ]
    }
    def construct(self):
        SimpleLinearTransformationScene.construct(self)
        words = TextMobject("""
            How would you describe 
            one of these numerically?
            """
        )
        words.add_background_rectangle()
        words.to_edge(UP)
        words.set_color(GREEN)
        formula = TexMobject([
            matrix_to_tex_string(["x_\\text{in}", "y_\\text{in}"]),
            "\\rightarrow ???? \\rightarrow",
            matrix_to_tex_string(["x_\\text{out}", "y_{\\text{out}}"])
        ])
        formula.add_background_rectangle()

        self.play(Write(words))
        self.wait()
        self.play(
            ApplyMethod(self.plane.fade, 0.7),
            ApplyMethod(self.background_plane.fade, 0.7),
            Write(formula, run_time = 2),
            Animation(words)
        )
        self.wait()

class FollowIHatJHat(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False
    }
    def construct(self):
        self.setup()
        i_hat = self.add_vector([1, 0], color = X_COLOR)
        i_label = self.label_vector(
            i_hat, "\\hat{\\imath}", 
            color = X_COLOR,
            label_scale_factor = 1
        )
        j_hat = self.add_vector([0, 1], color = Y_COLOR)
        j_label = self.label_vector(
            j_hat, "\\hat{\\jmath}", 
            color = Y_COLOR,
            label_scale_factor = 1
        )

        self.wait()
        self.play(*list(map(FadeOut, [i_label, j_label])))
        self.apply_transposed_matrix([[-1, 1], [-2, -1]])
        self.wait()

class TrackBasisVectorsExample(LinearTransformationScene):
    CONFIG = {
        "transposed_matrix" : [[1, -2], [3, 0]],
        "v_coords" : [-1, 2],
        "v_coord_strings" : ["-1", "2"],
        "result_coords_string" : """
            =
            \\left[ \\begin{array}{c}
                -1(1) + 2(3) \\\\
                -1(-2) + 2(0)
            \\end{arary}\\right] 
            = 
            \\left[ \\begin{array}{c}
                5 \\\\
                2
            \\end{arary}\\right] 
        """
    }
    def construct(self):
        self.setup()
        self.label_bases()
        self.introduce_vector()
        self.wait()
        self.apply_transposed_matrix(self.transposed_matrix)
        self.wait()
        self.show_linear_combination(clean_up = False)
        self.write_linear_map_rule()
        self.show_basis_vector_coords()

    def label_bases(self):
        triplets = [
            (self.i_hat, "\\hat{\\imath}", X_COLOR),
            (self.j_hat, "\\hat{\\jmath}", Y_COLOR),
        ]
        label_mobs = []
        for vect, label, color in triplets:
            label_mobs.append(self.add_transformable_label(
                vect, label, "\\text{Transformed } " + label,
                color = color,
                direction = "right",
            ))
        self.i_label, self.j_label = label_mobs

    def introduce_vector(self):
        v = self.add_vector(self.v_coords)
        coords = Matrix(self.v_coords)
        coords.scale(VECTOR_LABEL_SCALE_FACTOR)
        coords.next_to(v.get_end(), np.sign(self.v_coords[0])*RIGHT)

        self.play(Write(coords, run_time = 1))
        v_def = self.get_v_definition()
        pre_def = VMobject(
            VectorizedPoint(coords.get_center()),
            VMobject(*[
                mob.copy()
                for mob in coords.get_mob_matrix().flatten()
            ])
        )
        self.play(Transform(
            pre_def, v_def, 
            run_time = 2, 
            lag_ratio = 0
        ))
        self.remove(pre_def)
        self.add_foreground_mobject(v_def)
        self.wait()
        self.show_linear_combination()
        self.remove(coords)

    def show_linear_combination(self, clean_up = True):
        i_hat_copy, j_hat_copy = [m.copy() for m in (self.i_hat, self.j_hat)]
        self.play(ApplyFunction(
            lambda m : m.scale(self.v_coords[0]).fade(0.3),
            i_hat_copy
        ))
        self.play(ApplyFunction(
            lambda m : m.scale(self.v_coords[1]).fade(0.3),
            j_hat_copy
        ))
        self.play(ApplyMethod(j_hat_copy.shift, i_hat_copy.get_end()))
        self.wait(2)
        if clean_up:
            self.play(FadeOut(i_hat_copy), FadeOut(j_hat_copy))


    def get_v_definition(self):
        v_def = TexMobject([
            "\\vec{\\textbf{v}}",
            " = %s"%self.v_coord_strings[0],
            "\\hat{\\imath}",
            "+%s"%self.v_coord_strings[1],
            "\\hat{\\jmath}",
        ])
        v, equals_neg_1, i_hat, plus_2, j_hat = v_def.split()
        v.set_color(YELLOW)
        i_hat.set_color(X_COLOR)
        j_hat.set_color(Y_COLOR)
        v_def.add_background_rectangle()
        v_def.to_corner(UP + LEFT)
        self.v_def = v_def
        return v_def

    def write_linear_map_rule(self):
        rule = TexMobject([
            "\\text{Transformed } \\vec{\\textbf{v}}",
            " = %s"%self.v_coord_strings[0],
            "(\\text{Transformed }\\hat{\\imath})",
            "+%s"%self.v_coord_strings[1],
            "(\\text{Transformed } \\hat{\\jmath})",
        ])
        v, equals_neg_1, i_hat, plus_2, j_hat = rule.split()
        v.set_color(YELLOW)
        i_hat.set_color(X_COLOR)
        j_hat.set_color(Y_COLOR)
        rule.scale(0.85)
        rule.next_to(self.v_def, DOWN, buff = 0.2)
        rule.to_edge(LEFT)
        rule.add_background_rectangle()

        self.play(Write(rule, run_time = 2))
        self.wait()
        self.linear_map_rule = rule


    def show_basis_vector_coords(self):
        i_coords = matrix_to_mobject(self.transposed_matrix[0])
        j_coords = matrix_to_mobject(self.transposed_matrix[1])
        i_coords.set_color(X_COLOR)
        j_coords.set_color(Y_COLOR)
        for coords in i_coords, j_coords:
            coords.add_background_rectangle()
            coords.scale(0.7)
        i_coords.next_to(self.i_hat.get_end(), RIGHT)
        j_coords.next_to(self.j_hat.get_end(), RIGHT)

        calculation = TexMobject([
            " = %s"%self.v_coord_strings[0],
            matrix_to_tex_string(self.transposed_matrix[0]),
            "+%s"%self.v_coord_strings[1],
            matrix_to_tex_string(self.transposed_matrix[1]),
        ])
        equals_neg_1, i_hat, plus_2, j_hat = calculation.split()
        i_hat.set_color(X_COLOR)
        j_hat.set_color(Y_COLOR)
        calculation.scale(0.8)
        calculation.next_to(self.linear_map_rule, DOWN)
        calculation.to_edge(LEFT)
        calculation.add_background_rectangle()

        result = TexMobject(self.result_coords_string)
        result.scale(0.8)
        result.add_background_rectangle()
        result.next_to(calculation, DOWN)
        result.to_edge(LEFT)

        self.play(Write(i_coords, run_time = 1))
        self.wait()
        self.play(Write(j_coords, run_time = 1))
        self.wait()
        self.play(Write(calculation))
        self.wait()
        self.play(Write(result))
        self.wait()

class WatchManyVectorsMove(TransformManyVectors):
    def construct(self):
        self.setup()
        vectors = VMobject(*[
            Vector([x, y])
            for x in np.arange(-int(FRAME_X_RADIUS)+0.5, int(FRAME_X_RADIUS)+0.5)
            for y in np.arange(-int(FRAME_Y_RADIUS)+0.5, int(FRAME_Y_RADIUS)+0.5)
        ])
        vectors.set_submobject_colors_by_gradient(PINK, YELLOW)
        dots = self.vectors_to_dots(vectors)        
        self.play(ShowCreation(dots, lag_ratio = 0.5))
        self.play(Transform(
            dots, vectors, 
            lag_ratio = 0.5,
            run_time = 2
        ))
        self.remove(dots)
        for v in vectors.split():
            self.add_vector(v, animate = False)
        self.apply_transposed_matrix([[1, -2], [3, 0]])
        self.wait()
        self.play(
            ApplyMethod(self.plane.fade),
            FadeOut(vectors),
            Animation(self.i_hat),
            Animation(self.j_hat),
        )
        self.wait()

class NowWithoutWatching(Scene):
    def construct(self):
        text = TextMobject("Now without watching...")
        text.to_edge(UP)
        randy = Randolph(mode = "pondering")
        self.add(randy)
        self.play(Write(text, run_time = 1))
        self.play(ApplyMethod(randy.blink))
        self.wait(2)

class DeduceResultWithGeneralCoordinates(Scene):
    def construct(self):
        i_hat_to = TexMobject("\\hat{\\imath} \\rightarrow")
        j_hat_to = TexMobject("\\hat{\\jmath} \\rightarrow")
        i_coords = Matrix([1, -2])
        j_coords = Matrix([3, 0])
        i_coords.next_to(i_hat_to, RIGHT, buff = 0.1)
        j_coords.next_to(j_hat_to, RIGHT, buff = 0.1)
        i_group = VMobject(i_hat_to, i_coords)
        j_group = VMobject(j_hat_to, j_coords)
        i_group.set_color(X_COLOR)
        j_group.set_color(Y_COLOR)
        i_group.next_to(ORIGIN, LEFT, buff = 1).to_edge(UP)
        j_group.next_to(ORIGIN, RIGHT, buff = 1).to_edge(UP)

        vect = Matrix(["x", "y"])
        x, y = vect.get_mob_matrix().flatten()
        VMobject(x, y).set_color(YELLOW)
        rto = TexMobject("\\rightarrow")
        equals = TexMobject("=")
        plus = TexMobject("+")
        row1 = TexMobject("1x + 3y")
        row2 = TexMobject("-2x + 0y")
        VMobject(
            row1.split()[0], row2.split()[0], row2.split()[1]
        ).set_color(X_COLOR)
        VMobject(
            row1.split()[1], row1.split()[4], row2.split()[2], row2.split()[5]
        ).set_color(YELLOW)
        VMobject(
            row1.split()[3], row2.split()[4]
        ).set_color(Y_COLOR)
        result = Matrix([row1, row2])
        result.show()
        vect_group = VMobject(
            vect, rto, 
            x.copy(), i_coords.copy(), plus,
            y.copy(), j_coords.copy(), equals,
            result
        )
        vect_group.arrange(RIGHT, buff = 0.1)

        self.add(i_group, j_group)
        for mob in vect_group.split():
            self.play(Write(mob))
        self.wait()

class MatrixVectorMultiplication(LinearTransformationScene):
    CONFIG = {
        "abstract" : False
    }
    def construct(self):
        self.setup()
        matrix = self.build_to_matrix()
        self.label_matrix(matrix)
        vector, formula = self.multiply_by_vector(matrix)
        self.reposition_matrix_and_vector(matrix, vector, formula)

    def build_to_matrix(self):
        self.wait()
        self.apply_transposed_matrix([[3, -2], [2, 1]])
        self.wait()
        i_coords = vector_coordinate_label(self.i_hat)
        j_coords = vector_coordinate_label(self.j_hat)
        if self.abstract:
            new_i_coords = Matrix(["a", "c"])
            new_j_coords = Matrix(["b", "d"])
            new_i_coords.move_to(i_coords)
            new_j_coords.move_to(j_coords)
            i_coords = new_i_coords
            j_coords = new_j_coords
        i_coords.set_color(X_COLOR)
        j_coords.set_color(Y_COLOR)
        i_brackets = i_coords.get_brackets()
        j_brackets = j_coords.get_brackets()
        for coords in i_coords, j_coords:
            rect = BackgroundRectangle(coords)
            coords.rect = rect

        abstract_matrix = np.append(
            i_coords.get_mob_matrix(), 
            j_coords.get_mob_matrix(),
            axis = 1
        )
        concrete_matrix = Matrix(
            copy.deepcopy(abstract_matrix),
            add_background_rectangles_to_entries = True
        )
        concrete_matrix.to_edge(UP)
        if self.abstract:
            m = concrete_matrix.get_mob_matrix()[1, 0]
            m.shift(m.get_height()*DOWN/2)
        matrix_brackets = concrete_matrix.get_brackets()

        self.play(ShowCreation(i_coords.rect), Write(i_coords))
        self.play(ShowCreation(j_coords.rect), Write(j_coords))
        self.wait()
        self.remove(i_coords.rect, j_coords.rect)
        self.play(
            Transform(
                VMobject(*abstract_matrix.flatten()),
                VMobject(*concrete_matrix.get_mob_matrix().flatten()),
            ),
            Transform(i_brackets, matrix_brackets),
            Transform(j_brackets, matrix_brackets),
            run_time = 2,
            lag_ratio = 0
        )
        everything = VMobject(*self.get_mobjects())
        self.play(
            FadeOut(everything),
            Animation(concrete_matrix)
        )
        return concrete_matrix

    def label_matrix(self, matrix):
        title = TextMobject("``2x2 Matrix''")
        title.to_edge(UP+LEFT)
        col_circles = []
        for i, color in enumerate([X_COLOR, Y_COLOR]):
            col = VMobject(*matrix.get_mob_matrix()[:,i])
            col_circle = Circle(color = color)
            col_circle.stretch_to_fit_width(matrix.get_width()/3)
            col_circle.stretch_to_fit_height(matrix.get_height())
            col_circle.move_to(col)
            col_circles.append(col_circle)
        i_circle, j_circle = col_circles
        i_message = TextMobject("Where $\\hat{\\imath}$ lands")
        j_message = TextMobject("Where $\\hat{\\jmath}$ lands")
        i_message.set_color(X_COLOR)
        j_message.set_color(Y_COLOR)
        i_message.next_to(i_circle, DOWN, buff = 2, aligned_edge = RIGHT)
        j_message.next_to(j_circle, DOWN, buff = 2, aligned_edge = LEFT)
        i_arrow = Arrow(i_message, i_circle)
        j_arrow = Arrow(j_message, j_circle)

        self.play(Write(title))
        self.wait()
        self.play(ShowCreation(i_circle))
        self.play(
            Write(i_message, run_time = 1.5),
            ShowCreation(i_arrow),
        )
        self.wait()
        self.play(ShowCreation(j_circle))
        self.play(
            Write(j_message, run_time = 1.5),
            ShowCreation(j_arrow)
        )
        self.wait()
        self.play(*list(map(FadeOut, [
            i_message, i_circle, i_arrow, j_message, j_circle, j_arrow
        ])))


    def multiply_by_vector(self, matrix):
        vector = Matrix(["x", "y"]) if self.abstract else Matrix([5, 7])
        vector.set_height(matrix.get_height())
        vector.next_to(matrix, buff = 2)
        brace = Brace(vector, DOWN)
        words = TextMobject("Any  ol' vector")
        words.next_to(brace, DOWN)

        self.play(
            Write(vector),
            GrowFromCenter(brace),
            Write(words),
            run_time = 1
        )
        self.wait()

        v1, v2 = vector.get_mob_matrix().flatten()
        mob_matrix = matrix.copy().get_mob_matrix()
        col1 = Matrix(mob_matrix[:,0])
        col2 = Matrix(mob_matrix[:,1])
        formula = VMobject(
            v1.copy(), col1, TexMobject("+"), v2.copy(), col2
        )
        formula.arrange(RIGHT, buff = 0.1)
        formula.center()
        formula_start = VMobject(
            v1.copy(), 
            VMobject(*matrix.copy().get_mob_matrix()[:,0]),
            VectorizedPoint(),
            v2.copy(),
            VMobject(*matrix.copy().get_mob_matrix()[:,1]),
        )

        self.play(
            FadeOut(brace),
            FadeOut(words),
            Transform(
                formula_start, formula, 
                run_time = 2,
                lag_ratio = 0
            )
        )
        self.wait()
        self.show_result(formula)
        return vector, formula

    def show_result(self, formula):
        if self.abstract:
            row1 = ["a", "x", "+", "b", "y"]
            row2 = ["c", "x", "+", "d", "y"]
        else:
            row1 = ["3", "(5)", "+", "2", "(7)"]
            row2 = ["-2", "(5)", "+", "1", "(7)"]
        row1 = VMobject(*list(map(TexMobject, row1)))
        row2 = VMobject(*list(map(TexMobject, row2)))
        for row in row1, row2:
            row.arrange(RIGHT, buff = 0.1)
        final_sum = Matrix([row1, row2])
        row1, row2 = final_sum.get_mob_matrix().flatten()
        row1.split()[0].set_color(X_COLOR)
        row2.split()[0].set_color(X_COLOR)
        row1.split()[3].set_color(Y_COLOR)
        row2.split()[3].set_color(Y_COLOR)
        equals = TexMobject("=")
        equals.next_to(formula, RIGHT)
        final_sum.next_to(equals, RIGHT)

        self.play(
            Write(equals, run_time = 1),
            Write(final_sum)
        )
        self.wait()


    def reposition_matrix_and_vector(self, matrix, vector, formula):
        start_state = VMobject(matrix, vector)
        end_state = start_state.copy()
        end_state.arrange(RIGHT, buff = 0.1)
        equals = TexMobject("=")
        equals.next_to(formula, LEFT)
        end_state.next_to(equals, LEFT)
        brace = Brace(formula, DOWN)
        brace_words = TextMobject("Where all the intuition is")
        brace_words.next_to(brace, DOWN)
        brace_words.set_color(YELLOW)

        self.play(
            Transform(
                start_state, end_state, 
                lag_ratio = 0
            ),
            Write(equals, run_time = 1)
        )
        self.wait()
        self.play(
            FadeIn(brace),
            FadeIn(brace_words),
            lag_ratio = 0.5
        )
        self.wait()

class MatrixVectorMultiplicationAbstract(MatrixVectorMultiplication):
    CONFIG = {
        "abstract" : True,
    }

class ColumnsToBasisVectors(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[3, 1], [1, 2]]
    }
    def construct(self):
        self.setup()
        vector_coords = [-1, 2]

        vector = self.move_matrix_columns(self.t_matrix, vector_coords)
        self.scale_and_add(vector, vector_coords)
        self.wait(3)

    def move_matrix_columns(self, transposed_matrix, vector_coords = None):
        matrix = np.array(transposed_matrix).transpose()
        matrix_mob = Matrix(matrix)
        matrix_mob.to_corner(UP+LEFT)
        matrix_mob.add_background_to_entries()
        col1 = VMobject(*matrix_mob.get_mob_matrix()[:,0])
        col1.set_color(X_COLOR)
        col2 = VMobject(*matrix_mob.get_mob_matrix()[:,1])
        col2.set_color(Y_COLOR)
        matrix_brackets = matrix_mob.get_brackets()
        matrix_background = BackgroundRectangle(matrix_mob)
        self.add_foreground_mobject(matrix_background, matrix_mob)

        if vector_coords is not None:
            vector = Matrix(vector_coords)
            VMobject(*vector.get_mob_matrix().flatten()).set_color(YELLOW)
            vector.set_height(matrix_mob.get_height())
            vector.next_to(matrix_mob, RIGHT)
            vector_background = BackgroundRectangle(vector)
            self.add_foreground_mobject(vector_background, vector)

        new_i = Vector(matrix[:,0])
        new_j = Vector(matrix[:,1])
        i_label = vector_coordinate_label(new_i).set_color(X_COLOR)
        j_label = vector_coordinate_label(new_j).set_color(Y_COLOR)
        i_coords = VMobject(*i_label.get_mob_matrix().flatten())
        j_coords = VMobject(*j_label.get_mob_matrix().flatten())
        i_brackets = i_label.get_brackets()
        j_brackets = j_label.get_brackets()
        i_label_background = BackgroundRectangle(i_label)
        j_label_background = BackgroundRectangle(j_label)
        i_coords_start = VMobject(
            matrix_background.copy(),
            col1.copy(),
            matrix_brackets.copy()
        )
        i_coords_end = VMobject(
            i_label_background,
            i_coords,
            i_brackets,
        )
        j_coords_start = VMobject(
            matrix_background.copy(),
            col2.copy(),
            matrix_brackets.copy()
        )
        j_coords_end = VMobject(
            j_label_background,
            j_coords,
            j_brackets,
        )

        transform_matrix1 = np.array(matrix)
        transform_matrix1[:,1] = [0, 1]
        transform_matrix2 = np.dot(
            matrix,
            np.linalg.inv(transform_matrix1)
        )

        self.wait()
        self.apply_transposed_matrix(
            transform_matrix1.transpose(),
            added_anims = [Transform(i_coords_start, i_coords_end)],
            path_arc = np.pi/2,
        )
        self.add_foreground_mobject(i_coords_start)
        self.apply_transposed_matrix(
            transform_matrix2.transpose(),
            added_anims = [Transform(j_coords_start, j_coords_end) ],
            path_arc = np.pi/2,
        )
        self.add_foreground_mobject(j_coords_start)
        self.wait()

        self.matrix = VGroup(matrix_background, matrix_mob)
        self.i_coords = i_coords_start
        self.j_coords = j_coords_start

        return vector if vector_coords is not None else None


    def scale_and_add(self, vector, vector_coords):
        i_copy = self.i_hat.copy()
        j_copy = self.j_hat.copy()
        i_target = i_copy.copy().scale(vector_coords[0]).fade(0.3)
        j_target = j_copy.copy().scale(vector_coords[1]).fade(0.3)

        coord1, coord2 = vector.copy().get_mob_matrix().flatten()
        coord1.add_background_rectangle()
        coord2.add_background_rectangle()

        self.play(
            Transform(i_copy, i_target),
            ApplyMethod(coord1.next_to, i_target.get_center(), DOWN)
        )
        self.play(
            Transform(j_copy, j_target),
            ApplyMethod(coord2.next_to, j_target.get_center(), LEFT)
        )
        j_copy.add(coord2)
        self.play(ApplyMethod(j_copy.shift, i_copy.get_end()))
        self.add_vector(j_copy.get_end())
        self.wait()

class Describe90DegreeRotation(LinearTransformationScene):
    CONFIG = {
        "transposed_matrix" : [[0, 1], [-1, 0]],
        "title" : "$90^\\circ$ rotation counterclockwise",
    }
    def construct(self):
        self.setup()
        title = TextMobject(self.title)
        title.shift(DOWN)
        title.add_background_rectangle()
        matrix = Matrix(np.array(self.transposed_matrix).transpose())
        matrix.to_corner(UP+LEFT)
        matrix_background = BackgroundRectangle(matrix)
        col1 = VMobject(*matrix.get_mob_matrix()[:,0])
        col2 = VMobject(*matrix.get_mob_matrix()[:,1])
        col1.set_color(X_COLOR)
        col2.set_color(Y_COLOR)
        self.add_foreground_mobject(matrix_background, matrix.get_brackets())

        self.wait()
        self.apply_transposed_matrix(self.transposed_matrix)
        self.wait()
        self.play(Write(title))
        self.add_foreground_mobject(title)

        for vect, color, col in [(self.i_hat, X_COLOR, col1), (self.j_hat, Y_COLOR, col2)]:
            label = vector_coordinate_label(vect)
            label.set_color(color)
            background = BackgroundRectangle(label)
            coords = VMobject(*label.get_mob_matrix().flatten())
            brackets = label.get_brackets()

            self.play(ShowCreation(background), Write(label))
            self.wait()
            self.play(
                ShowCreation(background, rate_func = lambda t : smooth(1-t)),                
                ApplyMethod(coords.replace, col),
                FadeOut(brackets),
            )
            self.remove(label)
            self.add_foreground_mobject(coords)
            self.wait()
        self.show_vector(matrix)

    def show_vector(self, matrix):
        vector = Matrix(["x", "y"])
        VMobject(*vector.get_mob_matrix().flatten()).set_color(YELLOW)
        vector.set_height(matrix.get_height())
        vector.next_to(matrix, RIGHT)
        v_background = BackgroundRectangle(vector)

        matrix = np.array(self.transposed_matrix).transpose()
        inv = np.linalg.inv(matrix)
        self.apply_transposed_matrix(inv.transpose(), run_time = 0.5)
        self.add_vector([1, 2])
        self.wait()
        self.apply_transposed_matrix(self.transposed_matrix)
        self.play(ShowCreation(v_background), Write(vector))
        self.wait()

class DescribeShear(Describe90DegreeRotation):
    CONFIG = {
        "transposed_matrix" : [[1, 0], [1, 1]],
        "title" : "``Shear''",
    }

class OtherWayAround(Scene):
    def construct(self):
        self.play(Write("What about the other way around?"))
        self.wait(2)

class DeduceTransformationFromMatrix(ColumnsToBasisVectors):
    def construct(self):
        self.setup()
        self.move_matrix_columns([[1, 2], [3, 1]])

class LinearlyDependentColumns(ColumnsToBasisVectors):
    def construct(self):
        self.setup()
        title = TextMobject("Linearly dependent")
        subtitle = TextMobject("columns")
        title.add_background_rectangle()
        subtitle.add_background_rectangle()
        subtitle.next_to(title, DOWN)
        title.add(subtitle)
        title.shift(UP).to_edge(LEFT)
        title.set_color(YELLOW)
        self.add_foreground_mobject(title)
        self.move_matrix_columns([[2, 1], [-2, -1]])

class NextVideo(Scene):
    def construct(self):
        title = TextMobject("Next video: Matrix multiplication as composition")
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()         

class FinalSlide(Scene):
    def construct(self):
        text = TextMobject("""
            \\footnotesize 
            Technically, the definition of ``linear'' is as follows: 
            A transformation L is linear if it satisfies these
            two properties:

            \\begin{align*}
                L(\\vec{\\textbf{v}} + \\vec{\\textbf{w}}) 
                &= L(\\vec{\\textbf{v}}) + L(\\vec{\\textbf{w}})
                & & \\text{``Additivity''} \\\\
                L(c\\vec{\\textbf{v}}) &= c L(\\vec{\\textbf{v}})
                & & \\text{``Scaling''}
            \\end{align*}

            I'll talk about these properties later on, but I'm a big 
            believer in first understanding things visually.  
            Once you do, it becomes much more intuitive why these 
            two properties make sense.  So for now, you can 
            feel fine thinking of linear transformations as those 
            which keep grid lines parallel and evenly spaced 
            (and which fix the origin in place), since this visual 
            definition is actually equivalent to the two properties 
            above.
        """, enforce_new_line_structure = False)
        text.set_height(FRAME_HEIGHT - 2)
        text.to_edge(UP)
        self.add(text)
        self.wait()

### Old scenes

class RotateIHat(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False
    }
    def construct(self):
        self.setup()
        i_hat, j_hat = self.get_basis_vectors()
        i_label, j_label = self.get_basis_vector_labels()
        self.add_vector(i_hat)
        self.play(Write(i_label, run_time = 1))
        self.wait()
        self.play(FadeOut(i_label))
        self.apply_transposed_matrix([[0, 1], [-1, 0]])
        self.wait()
        self.play(Write(j_label, run_time = 1))
        self.wait()

class TransformationsAreFunctions(Scene):
    def construct(self):
        title = TextMobject([
            """Linear transformations are a
            special kind of""",
            "function"
        ])
        title_start, function = title.split()
        function.set_color(YELLOW)
        title.to_edge(UP)

        equation = TexMobject([
            "L",
            "(",
            "\\vec{\\textbf{v}}",
            ") = ",
            "\\vec{\\textbf{w}}",
        ])
        L, lp, _input, equals, _output = equation.split()
        L.set_color(YELLOW)
        _input.set_color(MAROON_C)
        _output.set_color(BLUE)
        equation.scale(2)
        equation.next_to(title, DOWN, buff = 1)

        starting_vector = TextMobject("Starting vector")
        starting_vector.shift(DOWN+3*LEFT)
        starting_vector.set_color(MAROON_C)
        ending_vector = TextMobject("The vector where it lands")
        ending_vector.shift(DOWN).to_edge(RIGHT)
        ending_vector.set_color(BLUE)

        func_arrow = Arrow(function.get_bottom(), L.get_top(), color = YELLOW)
        start_arrow = Arrow(starting_vector.get_top(), _input.get_bottom(), color = MAROON_C)
        ending_arrow = Arrow(ending_vector, _output, color = BLUE)


        self.add(title)
        self.play(
            Write(equation),
            ShowCreation(func_arrow)
        )
        for v, a in [(starting_vector, start_arrow), (ending_vector, ending_arrow)]:
            self.play(Write(v), ShowCreation(a), run_time = 1)
        self.wait()

class UsedToThinkinfOfFunctionsAsGraphs(VectorScene):
    def construct(self):
        self.show_graph()
        self.show_inputs_and_output()

    def show_graph(self):
        axes = self.add_axes()
        graph = FunctionGraph(lambda x : x**2, x_min = -2, x_max = 2)
        name = TexMobject("f(x) = x^2")
        name.next_to(graph, RIGHT).to_edge(UP)
        point = Dot(graph.point_from_proportion(0.8))
        point_label = TexMobject("(x, x^2)")
        point_label.next_to(point, DOWN+RIGHT, buff = 0.1)

        self.play(ShowCreation(graph))
        self.play(Write(name, run_time = 1))
        self.play(
            ShowCreation(point),
            Write(point_label),
            run_time = 1
        )
        self.wait()

        def collapse_func(p):
            return np.dot(p, [RIGHT, RIGHT, OUT]) + (FRAME_Y_RADIUS+1)*DOWN
        self.play(
            ApplyPointwiseFunction(
                collapse_func, axes, 
                lag_ratio = 0,
            ),
            ApplyPointwiseFunction(collapse_func, graph),
            ApplyMethod(point.shift, 10*DOWN),
            ApplyMethod(point_label.shift, 10*DOWN),
            ApplyFunction(lambda m : m.center().to_edge(UP), name),
            run_time = 1
        )
        self.clear()
        self.add(name)
        self.wait()

    def show_inputs_and_output(self):
        numbers = list(range(-3, 4))
        inputs = VMobject(*list(map(TexMobject, list(map(str, numbers)))))
        inputs.arrange(DOWN, buff = 0.5, aligned_edge = RIGHT)
        arrows = VMobject(*[
            Arrow(LEFT, RIGHT).next_to(mob)
            for mob in inputs.split()
        ])
        outputs = VMobject(*[
            TexMobject(str(num**2)).next_to(arrow)
            for num, arrow in zip(numbers, arrows.split())
        ])
        everyone = VMobject(inputs, arrows, outputs)
        everyone.center().to_edge(UP, buff = 1.5)

        self.play(Write(inputs, run_time = 1))
        self.wait()
        self.play(
            Transform(inputs.copy(), outputs),
            ShowCreation(arrows)
        )
        self.wait()

class TryingToVisualizeFourDimensions(Scene):
    def construct(self):
        randy = Randolph().to_corner()
        bubble = randy.get_bubble()
        formula = TexMobject("""
            L\\left(\\left[
                \\begin{array}{c}
                    x \\\\
                    y
                \\end{array}
            \\right]\\right) = 
            \\left[
                \\begin{array}{c}
                    2x + y \\\\
                    x + 2y
                \\end{array}
            \\right]
        """)
        formula.next_to(randy, RIGHT)
        formula.split()[3].set_color(X_COLOR)
        formula.split()[4].set_color(Y_COLOR)
        VMobject(*formula.split()[9:9+4]).set_color(MAROON_C)
        VMobject(*formula.split()[13:13+4]).set_color(BLUE)
        thought = TextMobject("""
            Do I imagine plotting 
            $(x, y, 2x+y, x+2y)$???
        """)
        thought.split()[-17].set_color(X_COLOR)
        thought.split()[-15].set_color(Y_COLOR)
        VMobject(*thought.split()[-13:-13+4]).set_color(MAROON_C)
        VMobject(*thought.split()[-8:-8+4]).set_color(BLUE)

        bubble.position_mobject_inside(thought)
        thought.shift(0.2*UP)

        self.add(randy)

        self.play(
            ApplyMethod(randy.look, DOWN+RIGHT),
            Write(formula)
        )
        self.play(
            ApplyMethod(randy.change_mode, "pondering"),
            ShowCreation(bubble),
            Write(thought)
        )
        self.play(Blink(randy))
        self.wait()
        self.remove(thought)
        bubble.make_green_screen()
        self.wait()
        self.play(Blink(randy))
        self.play(ApplyMethod(randy.change_mode, "confused"))
        self.wait()
        self.play(Blink(randy))
        self.wait()

class ForgetAboutGraphs(Scene):
    def construct(self):
        self.play(Write("You must unlearn graphs"))
        self.wait()

class ThinkAboutFunctionAsMovingVector(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "leave_ghost_vectors" : True,
    }
    def construct(self):
        self.setup()
        vector = self.add_vector([2, 1])
        label = self.add_transformable_label(vector, "v")
        self.wait()
        self.apply_transposed_matrix([[1, 1], [-3, 1]])
        self.wait()

class PrepareForFormalDefinition(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.teacher_says("Get ready for a formal definition!")
        self.wait(3)
        bubble = self.student_thinks("")
        bubble.make_green_screen()
        self.wait(3)

class AdditivityProperty(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "give_title" : True,
        "transposed_matrix" : [[2, 0], [1, 1]],
        "nonlinear_transformation" : None,
        "vector_v" : [2, 1],
        "vector_w" : [1, -2],
        "proclaim_sum" : True,
    }
    def construct(self):
        self.setup()
        added_anims = []
        if self.give_title:
            title = TextMobject("""
                First fundamental property of 
                linear transformations
            """)
            title.to_edge(UP)
            title.set_color(YELLOW)
            title.add_background_rectangle()
            self.play(Write(title))
            added_anims.append(Animation(title))
        self.wait()
        self.play(ApplyMethod(self.plane.fade), *added_anims)

        v, w = self.draw_all_vectors()
        self.apply_transformation(added_anims)
        self.show_final_sum(v, w)

    def draw_all_vectors(self):
        v = self.add_vector(self.vector_v, color = MAROON_C)
        v_label = self.add_transformable_label(v, "v")
        w = self.add_vector(self.vector_w, color = GREEN)
        w_label = self.add_transformable_label(w, "w")
        new_w = w.copy().fade(0.4)
        self.play(ApplyMethod(new_w.shift, v.get_end()))
        sum_vect = self.add_vector(new_w.get_end(), color = PINK)
        sum_label = self.add_transformable_label(
            sum_vect, 
            "%s + %s"%(v_label.expression, w_label.expression),
            rotate = True
        )
        self.play(FadeOut(new_w))
        return v, w

    def apply_transformation(self, added_anims):
        if self.nonlinear_transformation:
            self.apply_nonlinear_transformation(self.nonlinear_transformation)
        else:
            self.apply_transposed_matrix(
                self.transposed_matrix,
                added_anims = added_anims
            )
        self.wait()

    def show_final_sum(self, v, w):
        new_w = w.copy()
        self.play(ApplyMethod(new_w.shift, v.get_end()))
        self.wait()
        if self.proclaim_sum:
            text = TextMobject("It's still their sum!")
            text.add_background_rectangle()
            text.move_to(new_w.get_end(), aligned_edge = -new_w.get_end())
            text.shift_onto_screen()
            self.play(Write(text))
            self.wait()

class NonlinearLacksAdditivity(AdditivityProperty):
    CONFIG = {
        "give_title" : False,
        "nonlinear_transformation" : curvy_squish,
        "vector_v" : [3, 2],
        "vector_w" : [2, -3],
        "proclaim_sum" : False,
    }

class SecondAdditivityExample(AdditivityProperty):
    CONFIG = {
        "give_title" : False,
        "transposed_matrix" : [[1, -1], [2, 1]],
        "vector_v" : [-2, 2],
        "vector_w" : [3, 0],
        "proclaim_sum" : False,
    }

class ShowGridCreation(Scene):
    def construct(self):
        plane = NumberPlane()
        coords = VMobject(*plane.get_coordinate_labels())
        self.play(ShowCreation(plane, run_time = 3))
        self.play(Write(coords, run_time = 3))
        self.wait()

class MoveAroundAllVectors(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "focus_on_one_vector" : False,
        "include_background_plane" : False,
    }
    def construct(self):
        self.setup()
        vectors = VMobject(*[
            Vector([x, y])
            for x in np.arange(-int(FRAME_X_RADIUS)+0.5, int(FRAME_X_RADIUS)+0.5)
            for y in np.arange(-int(FRAME_Y_RADIUS)+0.5, int(FRAME_Y_RADIUS)+0.5)
        ])
        vectors.set_submobject_colors_by_gradient(PINK, YELLOW)
        dots = self.get_dots(vectors)

        self.wait()
        self.play(ShowCreation(dots))
        self.wait()
        self.play(Transform(dots, vectors))
        self.wait()
        self.remove(dots)
        if self.focus_on_one_vector:
            vector = vectors.split()[43]#yeah, great coding Grant
            self.remove(vectors)
            self.add_vector(vector)
            self.play(*[
                FadeOut(v) 
                for v in vectors.split()
                if v is not vector
            ])
            self.wait()
            self.add(vector.copy().set_color(DARK_GREY))
        else:
            for vector in vectors.split():
                self.add_vector(vector, animate = False)
        self.apply_transposed_matrix([[3, 0], [1, 2]])
        self.wait()
        dots = self.get_dots(vectors)
        self.play(Transform(vectors, dots))
        self.wait()

    def get_dots(self, vectors):
        return VMobject(*[
            Dot(v.get_end(), color = v.get_color())
            for v in vectors.split()
        ])

class ReasonForThinkingAboutArrows(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False
    }
    def construct(self):
        self.setup()
        self.plane.fade()
        v_color = MAROON_C
        w_color = BLUE

        v = self.add_vector([3, 1], color = v_color)
        w = self.add_vector([1, -2], color = w_color)
        vectors = VMobject(v, w)

        self.to_and_from_dots(vectors)
        self.scale_and_add(vectors)
        self.apply_transposed_matrix([[1, 1], [-1, 0]])
        self.scale_and_add(vectors)

    def to_and_from_dots(self, vectors):
        vectors_copy = vectors.copy()
        dots = VMobject(*[
            Dot(v.get_end(), color = v.get_color())
            for v in vectors.split()
        ])

        self.wait()
        self.play(Transform(vectors, dots))
        self.wait()
        self.play(Transform(vectors, vectors_copy))
        self.wait()

    def scale_and_add(self, vectors):
        vectors_copy = vectors.copy()
        v, w, = vectors.split()
        scaled_v = Vector(0.5*v.get_end(), color = v.get_color())
        scaled_w = Vector(1.5*w.get_end(), color = w.get_color())
        shifted_w = scaled_w.copy().shift(scaled_v.get_end())
        sum_vect = Vector(shifted_w.get_end(), color = PINK)

        self.play(
            ApplyMethod(v.scale, 0.5),
            ApplyMethod(w.scale, 1.5),
        )
        self.play(ApplyMethod(w.shift, v.get_end()))
        self.add_vector(sum_vect)
        self.wait()
        self.play(Transform(
            vectors, vectors_copy, 
            lag_ratio = 0
        ))
        self.wait()

class LinearTransformationWithOneVector(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
    }
    def construct(self):
        self.setup()
        v = self.add_vector([3, 1])
        self.vector_to_coords(v) 
        self.apply_transposed_matrix([[-1, 1], [-2, -1]])
        self.vector_to_coords(v)























