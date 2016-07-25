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
        words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        words.split()[1].highlight(GREEN)
        words.split()[3].highlight(GREEN)
        author = TextMobject("-Morpheus")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)
        comment = TextMobject("""
            (Surprisingly apt words on the importance 
            of understanding matrix operations visually.)
        """)
        comment.scale(0.7)
        comment.next_to(author, DOWN, buff = 1)

        self.play(FadeIn(words))
        self.dither(3)
        self.play(Write(author, run_time = 3))
        self.dither()
        self.play(Write(comment))
        self.dither()

class Introduction(TeacherStudentsScene):
    def construct(self):
        title = TextMobject(["Matrices as", "Linear transformations"])
        title.to_edge(UP)
        title.highlight(YELLOW)
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
            return (SPACE_WIDTH+SPACE_HEIGHT)*p/np.linalg.norm(p)
        self.play(
            ApplyPointwiseFunction(spread_out, everything),
            ApplyFunction(
                lambda m : m.center().to_edge(UP), 
                linear_transformations
            )
        )

class ThreePerspectives(Scene):
    def construct(self):
        title = TextMobject("Linear transformations")
        title.to_edge(UP)
        title.highlight(YELLOW)
        self.add(title)

        words = VMobject(*map(TextMobject, [
            "1. Geometric perspective",
            "2. Numerical computations",
            "3. Abstract definition"
        ]))
        words.arrange_submobjects(DOWN, buff = 0.5, aligned_edge = LEFT)
        words.to_edge(LEFT, buff = 2)
        for word in words.split():
            self.play(Write(word), run_time = 2)
            self.dither()
        for word in words.split():
            all_else = self.get_mobjects()
            all_else.remove(word)
            all_else_copies = [mob.copy() for mob in all_else]
            self.play(*[ApplyMethod(mob.fade, 0.7) for mob in all_else])
            self.dither()
            self.play(*[Transform(*pair) for pair in zip(all_else, all_else_copies)])

class ShowGridCreation(Scene):
    def construct(self):
        plane = NumberPlane()
        coords = VMobject(*plane.get_coordinate_labels())
        self.play(ShowCreation(plane, run_time = 3))
        self.play(Write(coords, run_time = 3))
        self.dither()

class IntroduceLinearTransformations(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "include_background_plane" : False
    }
    def construct(self):
        self.setup()
        self.dither()
        self.apply_transposed_matrix([[2, 1], [1, 2]])
        self.dither()

        lines_rule = TextMobject("Lines remain lines")
        lines_rule.shift(2*UP).to_edge(LEFT)
        origin_rule = TextMobject("Origin remains fixed")
        origin_rule.shift(2*UP).to_edge(RIGHT)
        arrow = Arrow(origin_rule, ORIGIN)
        dot = Dot(ORIGIN, radius = 0.1, color = RED)

        for rule in lines_rule, origin_rule:
            rule.add_background_rectangle()

        self.play(
            # FadeIn(lines_rule_rect),            
            Write(lines_rule, run_time = 2),
        )
        self.dither()
        self.play(
            # FadeIn(origin_rule_rect),            
            Write(origin_rule, run_time = 2),
            ShowCreation(arrow),
            GrowFromCenter(dot)
        )
        self.dither()

class SimpleLinearTransformationScene(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "transposed_matrix" : [[2, 1], [1, 2]]
    }
    def construct(self):
        self.setup()
        self.dither()
        self.apply_transposed_matrix(self.transposed_matrix)
        self.dither()

class SimpleNonlinearTransformationScene(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "words" : "Not linear: some lines get curved"
    }
    def construct(self):
        self.setup()
        self.dither()
        self.apply_nonlinear_transformation(self.func)
        words = TextMobject(self.words)
        words.to_corner(UP+RIGHT)
        words.highlight(RED)
        words.add_background_rectangle()
        self.play(Write(words))
        self.dither()

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
        new_x = np.sign(x)*SPACE_WIDTH*smooth(abs(x) / SPACE_WIDTH)
        new_y = np.sign(y)*SPACE_HEIGHT*smooth(abs(y) / SPACE_HEIGHT)
        return [new_x, new_y, 0]

class SneakyNonlinearTransformationExplained(SneakyNonlinearTransformation):
    CONFIG = {
        "words" : "Not linear: diagonal lines get curved"
    }
    def setup(self):
        LinearTransformationScene.setup(self)
        diag = Line(
            SPACE_HEIGHT*LEFT+SPACE_HEIGHT*DOWN,
            SPACE_HEIGHT*RIGHT + SPACE_HEIGHT*UP
        )
        diag.insert_n_anchor_points(20)
        diag.change_anchor_mode("smooth")
        diag.highlight(YELLOW)
        self.play(ShowCreation(diag))
        self.add_transformable_mobject(diag)

class AnotherLinearTransformation(SimpleLinearTransformationScene):
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
        p.highlight(YELLOW)
        es.highlight(GREEN)
        text.add_background_rectangle()
        text.shift(-text.get_bottom())
        self.play(Write(text))
        self.dither()

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
            for x in np.arange(-int(SPACE_WIDTH)+0.5, int(SPACE_WIDTH)+0.5)
            for y in np.arange(-int(SPACE_HEIGHT)+0.5, int(SPACE_HEIGHT)+0.5)
        ])
        vectors.submobject_gradient_highlight(PINK, YELLOW)
        dots = self.get_dots(vectors)

        self.dither()
        self.play(ShowCreation(dots))
        self.dither()
        self.play(Transform(dots, vectors))
        self.dither()
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
            self.dither()
            self.add(vector.copy().highlight(DARK_GREY))
        else:
            for vector in vectors.split():
                self.add_vector(vector, animate = False)
        self.apply_transposed_matrix([[3, 0], [1, 2]])
        self.dither()
        dots = self.get_dots(vectors)
        self.play(Transform(vectors, dots))
        self.dither()

    def get_dots(self, vectors):
        return VMobject(*[
            Dot(v.get_end(), color = v.get_color())
            for v in vectors.split()
        ])

# class MoveAroundJustOneVector(MoveAroundAllVectors):
#     CONFIG = {
#         "focus_on_one_vector" : True,
#     }

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

        self.dither()
        self.play(Transform(vectors, dots))
        self.dither()
        self.play(Transform(vectors, vectors_copy))
        self.dither()

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
        self.dither()
        self.play(Transform(
            vectors, vectors_copy, 
            submobject_mode = "all_at_once"
        ))
        self.dither()

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

class FollowIHatJHat(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False
    }
    def construct(self):
        self.setup()
        i_hat = self.add_vector([1, 0], color = X_COLOR)
        i_label = self.label_vector(i_hat, "\\hat{\\imath}")
        j_hat = self.add_vector([0, 1], color = Y_COLOR)
        j_label = self.label_vector(j_hat, "\\hat{\\jmath}")

        self.dither()
        self.play(*map(FadeOut, [i_label, j_label]))
        self.apply_transposed_matrix([[-1, 1], [-2, -1]])
        self.dither()

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
        self.dither()
        self.apply_transposed_matrix(self.transposed_matrix)
        self.dither()
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
        coords.scale(VECTOR_LABEL_SCALE_VAL)
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
            submobject_mode = "all_at_once"
        ))
        self.remove(pre_def)
        self.add_foreground_mobject(v_def)
        self.dither()
        self.show_linear_combination()
        self.remove(coords)

    def show_linear_combination(self, clean_up = True):
        i_hat_copy, j_hat_copy = [m.copy() for m in self.i_hat, self.j_hat]
        self.play(ApplyFunction(
            lambda m : m.scale(self.v_coords[0]).fade(0.3),
            i_hat_copy
        ))
        self.play(ApplyFunction(
            lambda m : m.scale(self.v_coords[1]).fade(0.3),
            j_hat_copy
        ))
        self.play(ApplyMethod(j_hat_copy.shift, i_hat_copy.get_end()))
        self.dither(2)
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
        v.highlight(YELLOW)
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)
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
        v.highlight(YELLOW)
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)
        rule.scale(0.85)
        rule.next_to(self.v_def, DOWN, buff = 0.2)
        rule.to_edge(LEFT)
        rule.add_background_rectangle()

        self.play(Write(rule, run_time = 2))
        self.dither()
        self.linear_map_rule = rule


    def show_basis_vector_coords(self):
        i_coords = matrix_to_mobject(self.transposed_matrix[0])
        j_coords = matrix_to_mobject(self.transposed_matrix[1])
        i_coords.highlight(X_COLOR)
        j_coords.highlight(Y_COLOR)
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
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)
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
        self.dither()
        self.play(Write(j_coords, run_time = 1))
        self.dither()
        self.play(Write(calculation))
        self.dither()
        self.play(Write(result))
        self.dither()

class TrackBasisVectorsExampleGenerally(TrackBasisVectorsExample):
    CONFIG = {
        "v_coord_strings" : ["x", "y"],
        "result_coords_string" : """
            =
            \\left[ \\begin{array}{c}
                1x + 3y \\\\
                -2x + 0y
            \\end{arary}\\right] 
        """
    }

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
        self.dither()
        self.apply_transposed_matrix([[3, -2], [2, 1]])
        self.dither()
        i_coords = vector_coordinate_label(self.i_hat)
        j_coords = vector_coordinate_label(self.j_hat)
        if self.abstract:
            new_i_coords = Matrix(["a", "c"])
            new_j_coords = Matrix(["b", "d"])
            new_i_coords.scale(0.7).move_to(i_coords)
            new_j_coords.scale(0.7).move_to(j_coords)
            i_coords = new_i_coords
            j_coords = new_j_coords
        i_coords.highlight(X_COLOR)
        j_coords.highlight(Y_COLOR)
        i_brackets = i_coords.get_brackets()
        j_brackets = j_coords.get_brackets()
        for coords in i_coords, j_coords:
            rect = Rectangle(
                color = BLACK,
                stroke_width = 0,
                fill_opacity = 0.75
            )
            rect.replace(coords, stretch = True)
            coords.rect = rect

        abstract_matrix = np.append(
            i_coords.get_mob_matrix(), 
            j_coords.get_mob_matrix(),
            axis = 1
        )
        concrete_matrix = Matrix(
            copy.deepcopy(abstract_matrix),
            add_background_rectangles = True
        )
        concrete_matrix.to_edge(UP)
        matrix_brackets = concrete_matrix.get_brackets()

        self.play(FadeIn(i_coords.rect), Write(i_coords))
        self.play(FadeIn(j_coords.rect), Write(j_coords))
        self.dither()
        self.remove(i_coords.rect, j_coords.rect)
        self.play(
            Transform(
                VMobject(*abstract_matrix.flatten()),
                VMobject(*concrete_matrix.get_mob_matrix().flatten()),
            ),
            Transform(i_brackets, matrix_brackets),
            Transform(j_brackets, matrix_brackets),
            run_time = 2,
            submobject_mode = "all_at_once"
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
        i_message.highlight(X_COLOR)
        j_message.highlight(Y_COLOR)
        i_message.next_to(i_circle, DOWN, buff = 2, aligned_edge = RIGHT)
        j_message.next_to(j_circle, DOWN, buff = 2, aligned_edge = LEFT)
        i_arrow = Arrow(i_message, i_circle)
        j_arrow = Arrow(j_message, j_circle)

        self.play(Write(title))
        self.dither()
        self.play(ShowCreation(i_circle))
        self.play(
            Write(i_message, run_time = 1.5),
            ShowCreation(i_arrow),
        )
        self.dither()
        self.play(ShowCreation(j_circle))
        self.play(
            Write(j_message, run_time = 1.5),
            ShowCreation(j_arrow)
        )
        self.dither()
        self.play(*map(FadeOut, [
            i_message, i_circle, i_arrow, j_message, j_circle, j_arrow
        ]))


    def multiply_by_vector(self, matrix):
        vector = Matrix(["x", "y"]) if self.abstract else Matrix([5, 7])
        vector.scale_to_fit_height(matrix.get_height())
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
        self.dither()

        v1, v2 = vector.get_mob_matrix().flatten()
        mob_matrix = matrix.copy().get_mob_matrix()
        col1 = Matrix(mob_matrix[:,0])
        col2 = Matrix(mob_matrix[:,1])
        formula = VMobject(
            v1.copy(), col1, TexMobject("+"), v2.copy(), col2
        )
        formula.arrange_submobjects(RIGHT, buff = 0.1)
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
                submobject_mode = "all_at_once"
            )
        )
        self.dither()
        self.show_result(formula)
        return vector, formula

    def show_result(self, formula):
        if self.abstract:
            row1 = ["a", "x", "+", "b", "y"]
            row2 = ["c", "x", "+", "d", "y"]
        else:
            row1 = ["3", "(5)", "+", "2", "(7)"]
            row2 = ["-2", "(5)", "+", "1", "(7)"]
        row1 = VMobject(*map(TexMobject, row1))
        row2 = VMobject(*map(TexMobject, row2))
        for row in row1, row2:
            row.arrange_submobjects(RIGHT, buff = 0.1)
            row.scale(0.7)
        final_sum = Matrix([row1, row2])
        row1, row2 = final_sum.get_mob_matrix().flatten()
        row1.split()[0].highlight(X_COLOR)
        row2.split()[0].highlight(X_COLOR)
        row1.split()[3].highlight(Y_COLOR)
        row2.split()[3].highlight(Y_COLOR)
        equals = TexMobject("=")
        equals.next_to(formula, RIGHT)
        final_sum.next_to(equals, RIGHT)

        self.play(
            Write(equals, run_time = 1),
            Write(final_sum)
        )
        self.dither()

    def reposition_matrix_and_vector(self, matrix, vector, formula):
        start_state = VMobject(matrix, vector)
        end_state = start_state.copy()
        end_state.arrange_submobjects(RIGHT, buff = 0.1)
        equals = TexMobject("=")
        equals.next_to(formula, LEFT)
        end_state.next_to(equals, LEFT)

        self.play(
            Transform(
                start_state, end_state, 
                submobject_mode = "all_at_once"
            ),
            Write(equals, run_time = 1)
        )
        self.dither()

class MatrixVectorMultiplicationAbstract(MatrixVectorMultiplication):
    CONFIG = {
        "abstract" : True,
    }


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
        self.dither()
        self.play(FadeOut(i_label))
        self.apply_transposed_matrix([[0, 1], [-1, 0]])
        self.dither()
        self.play(Write(j_label, run_time = 1))
        self.dither()

class TransformationsAreFunctions(Scene):
    def construct(self):
        title = TextMobject([
            """Linear transformations are a
            special kind of""",
            "function"
        ])
        title_start, function = title.split()
        function.highlight(YELLOW)
        title.to_edge(UP)

        equation = TexMobject([
            "L",
            "(",
            "\\vec{\\textbf{v}}",
            ") = ",
            "\\vec{\\textbf{w}}",
        ])
        L, lp, _input, equals, _output = equation.split()
        L.highlight(YELLOW)
        _input.highlight(MAROON_C)
        _output.highlight(BLUE)
        equation.scale(2)
        equation.next_to(title, DOWN, buff = 1)

        starting_vector = TextMobject("Starting vector")
        starting_vector.shift(DOWN+3*LEFT)
        starting_vector.highlight(MAROON_C)
        ending_vector = TextMobject("The vector where it lands")
        ending_vector.shift(DOWN).to_edge(RIGHT)
        ending_vector.highlight(BLUE)

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
        self.dither()

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
        self.dither()

        def collapse_func(p):
            return np.dot(p, [RIGHT, RIGHT, OUT]) + (SPACE_HEIGHT+1)*DOWN
        self.play(
            ApplyPointwiseFunction(
                collapse_func, axes, 
                submobject_mode = "all_at_once",
            ),
            ApplyPointwiseFunction(collapse_func, graph),
            ApplyMethod(point.shift, 10*DOWN),
            ApplyMethod(point_label.shift, 10*DOWN),
            ApplyFunction(lambda m : m.center().to_edge(UP), name),
            run_time = 1
        )
        self.clear()
        self.add(name)
        self.dither()

    def show_inputs_and_output(self):
        numbers = range(-3, 4)
        inputs = VMobject(*map(TexMobject, map(str, numbers)))
        inputs.arrange_submobjects(DOWN, buff = 0.5, aligned_edge = RIGHT)
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
        self.dither()
        self.play(
            Transform(inputs.copy(), outputs),
            ShowCreation(arrows)
        )
        self.dither()

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
        formula.split()[3].highlight(X_COLOR)
        formula.split()[4].highlight(Y_COLOR)
        VMobject(*formula.split()[9:9+4]).highlight(MAROON_C)
        VMobject(*formula.split()[13:13+4]).highlight(BLUE)
        thought = TextMobject("""
            Do I imagine plotting 
            $(x, y, 2x+y, x+2y)$???
        """)
        thought.split()[-17].highlight(X_COLOR)
        thought.split()[-15].highlight(Y_COLOR)
        VMobject(*thought.split()[-13:-13+4]).highlight(MAROON_C)
        VMobject(*thought.split()[-8:-8+4]).highlight(BLUE)

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
        self.dither()
        self.remove(thought)
        bubble.make_green_screen()
        self.dither()
        self.play(Blink(randy))
        self.play(ApplyMethod(randy.change_mode, "confused"))
        self.dither()
        self.play(Blink(randy))
        self.dither()

class ForgetAboutGraphs(Scene):
    def construct(self):
        self.play(Write("You must unlearn graphs"))
        self.dither()

class ThinkAboutFunctionAsMovingVector(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "leave_ghost_vectors" : True,
    }
    def construct(self):
        self.setup()
        vector = self.add_vector([2, 1])
        label = self.add_transformable_label(vector, "v")
        self.dither()
        self.apply_transposed_matrix([[1, 1], [-3, 1]])
        self.dither()

class PrepareForFormalDefinition(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.teacher_says("Get ready for a formal definition!")
        self.dither(3)
        bubble = self.student_thinks("")
        bubble.make_green_screen()
        self.dither(3)

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
            title.highlight(YELLOW)
            title.add_background_rectangle()
            self.play(Write(title))
            added_anims.append(Animation(title))
        self.dither()
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
        self.dither()

    def show_final_sum(self, v, w):
        new_w = w.copy()
        self.play(ApplyMethod(new_w.shift, v.get_end()))
        self.dither()
        if self.proclaim_sum:
            text = TextMobject("It's still their sum!")
            text.add_background_rectangle()
            text.move_to(new_w.get_end(), side_to_align = -new_w.get_end())
            text.shift_onto_screen()
            self.play(Write(text))
            self.dither()

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



























