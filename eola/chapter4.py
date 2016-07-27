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
from eola.chapter3 import MatrixVectorMultiplicationAbstract


class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject([
            "It is my experience that proofs involving",
            "matrices",
            "can be shortened by 50\\% if one",
            "throws the matrices out."
        ])
        words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        words.split()[1].highlight(GREEN)
        words.split()[3].highlight(BLUE)
        author = TextMobject("-Emil Artin")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.dither(2)
        self.play(Write(author, run_time = 3))
        self.dither()

class MatrixToBlank(Scene):
    def construct(self):
        matrix = Matrix([[3, 1], [0, 2]])
        arrow = Arrow(LEFT, RIGHT)
        matrix.to_edge(LEFT)
        arrow.next_to(matrix, LEFT)
        matrix.add(arrow)
        self.play(Write(matrix))
        self.dither()

class RecapTime(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.teacher_says("Quick recap time!")
        self.random_blink()
        self.dither()
        student = self.get_students()[0]
        everyone = self.get_mobjects()
        everyone.remove(student)
        everyone = VMobject(*everyone)
        self.play(
            ApplyMethod(everyone.fade, 0.7),
            ApplyMethod(student.change_mode, "confused")
        )
        self.play(Blink(student))
        self.dither()
        self.play(ApplyFunction(
            lambda m : m.change_mode("pondering").look(LEFT),
            student
        ))
        self.play(Blink(student))
        self.dither()

class DeterminedByTwoBasisVectors(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False
    }
    def construct(self):
        self.setup()
        i_hat = self.add_vector([1, 0], color = X_COLOR)
        self.add_transformable_label(
            i_hat, "\\hat{\\imath}", "\\hat{\\imath}", 
            color = X_COLOR
        )
        j_hat = self.add_vector([0, 1], color = Y_COLOR)
        self.add_transformable_label(
            j_hat, "\\hat{\\jmath}", "\\hat{\\jmath}", 
            color = Y_COLOR
        )

        t_matrix = np.array([[2, 2], [-2, 1]])
        matrix = t_matrix.transpose()
        matrix1 = np.array(matrix)
        matrix1[:,1] = [0, 1]
        matrix2 = np.dot(matrix, np.linalg.inv(matrix1))

        self.dither()
        self.apply_transposed_matrix(matrix1.transpose())
        self.apply_transposed_matrix(matrix2.transpose())
        self.dither()

class FollowLinearCombination(LinearTransformationScene):
    def construct(self):
        vect_coords = [-1, 2]
        t_matrix = np.array([[2, 2], [-2, 1]])

        #Draw vectors
        self.setup()
        i_label = self.add_transformable_label(
            self.i_hat, "\\hat{\\imath}", animate = False,
            direction = "right", color = X_COLOR
        )
        j_label = self.add_transformable_label(
            self.j_hat, "\\hat{\\jmath}", animate = False,
            direction = "right", color = Y_COLOR
        )
        vect = self.add_vector(vect_coords)
        vect_array = Matrix(["x", "y"], add_background_rectangles = True)
        v_equals = TexMobject(["\\vec{\\textbf{v}}", "="])
        v_equals.split()[0].highlight(YELLOW)
        v_equals.next_to(vect_array, LEFT)
        vect_array.add(v_equals)
        vect_array.to_edge(UP, buff = 0.2)
        background_rect = BackgroundRectangle(vect_array)
        vect_array.get_entries().highlight(YELLOW)
        self.play(ShowCreation(background_rect), Write(vect_array))
        self.add_foreground_mobject(background_rect, vect_array)

        #Show scaled vectors
        x, y = vect_array.get_entries().split()
        scaled_i_label = VMobject(x.copy(), i_label)
        scaled_j_label = VMobject(y.copy(), j_label)
        scaled_i = self.i_hat.copy().scale(vect_coords[0])
        scaled_j = self.j_hat.copy().scale(vect_coords[1])
        for mob in scaled_i, scaled_j:
            mob.fade(0.3)
        scaled_i_label_target = scaled_i_label.copy()
        scaled_i_label_target.arrange_submobjects(buff = 0.1)
        scaled_i_label_target.next_to(scaled_i, DOWN)
        scaled_j_label_target = scaled_j_label.copy()
        scaled_j_label_target.arrange_submobjects(buff = 0.1)
        scaled_j_label_target.next_to(scaled_j, LEFT)

        self.show_scaled_vectors(vect_array, vect_coords, i_label, j_label)
        self.apply_transposed_matrix(t_matrix)
        self.show_scaled_vectors(vect_array, vect_coords, i_label, j_label)
        self.record_basis_coordinates(vect_array, vect)

    def show_scaled_vectors(self, vect_array, vect_coords, i_label, j_label):
        x, y = vect_array.get_entries().split()
        scaled_i_label = VMobject(x.copy(), i_label.copy())
        scaled_j_label = VMobject(y.copy(), j_label.copy())
        scaled_i = self.i_hat.copy().scale(vect_coords[0])
        scaled_j = self.j_hat.copy().scale(vect_coords[1])
        for mob in scaled_i, scaled_j:
            mob.fade(0.3)
        scaled_i_label_target = scaled_i_label.copy()
        scaled_i_label_target.arrange_submobjects(buff = 0.1)
        scaled_i_label_target.next_to(scaled_i.get_center(), DOWN)
        scaled_j_label_target = scaled_j_label.copy()
        scaled_j_label_target.arrange_submobjects(buff = 0.1)
        scaled_j_label_target.next_to(scaled_j.get_center(), LEFT)

        self.play(
            Transform(self.i_hat.copy(), scaled_i),
            Transform(scaled_i_label, scaled_i_label_target)
        )
        scaled_i = self.get_mobjects_from_last_animation()[0]
        self.play(
            Transform(self.j_hat.copy(), scaled_j),
            Transform(scaled_j_label, scaled_j_label_target)
        )
        scaled_j = self.get_mobjects_from_last_animation()[0]
        self.play(*[
            ApplyMethod(mob.shift, scaled_i.get_end())
            for mob in scaled_j, scaled_j_label
        ])
        self.dither()
        self.play(*map(FadeOut, [
            scaled_i, scaled_j, scaled_i_label, scaled_j_label,
        ]))

    def record_basis_coordinates(self, vect_array, vect):
        i_label = vector_coordinate_label(self.i_hat)
        i_label.highlight(X_COLOR)
        j_label = vector_coordinate_label(self.j_hat)
        j_label.highlight(Y_COLOR)
        for mob in i_label, j_label:
            mob.scale_in_place(0.8)
            background = BackgroundRectangle(mob)
            self.play(ShowCreation(background), Write(mob))

        self.dither()
        x, y = vect_array.get_entries().split()
        pre_formula = VMobject(
            x, i_label, TexMobject("+"),
            y, j_label
        )
        post_formula = pre_formula.copy()
        pre_formula.split()[2].fade(1)
        post_formula.arrange_submobjects(buff = 0.1)
        post_formula.next_to(vect, DOWN)
        background = BackgroundRectangle(post_formula)
        everything = self.get_mobjects()
        everything.remove(vect)
        self.play(*[
            ApplyMethod(m.fade) for m in everything
        ] + [
            ShowCreation(background, run_time = 2, rate_func = squish_rate_func(smooth, 0.5, 1)),
            Transform(pre_formula.copy(), post_formula, run_time = 2),
            ApplyMethod(vect.set_stroke, width = 7)
        ])
        self.dither()

class MatrixVectorMultiplicationCopy(MatrixVectorMultiplicationAbstract):
    pass ## Here just for stage_animations.py purposes

class RecapOver(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.teacher_says("Recap over!")

class TwoSuccessiveTransformations(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.apply_transposed_matrix([[2, 1],[1, 2]])
        self.apply_transposed_matrix([[-1, -0.5],[0, -0.5]])
        self.dither()

class RotationThenShear(LinearTransformationScene):
    CONFIG = {
        "foreground_plane_kwargs" : {
            "x_radius" : SPACE_WIDTH,
            "y_radius" : 2*SPACE_WIDTH,
            "secondary_line_ratio" : 0
        },
    }
    def construct(self):
        self.setup()
        rot_words = TextMobject("$90^\\circ$ rotation counterclockwise")
        shear_words = TextMobject("followed by a shear")
        rot_words.highlight(YELLOW)
        shear_words.highlight(PINK)
        VMobject(rot_words, shear_words).arrange_submobjects(DOWN).to_edge(UP)
        for words in rot_words, shear_words:
            words.add_background_rectangle()

        self.play(Write(rot_words, run_time = 1))
        self.add_foreground_mobject(rot_words)            
        self.apply_transposed_matrix([[0, 1], [-1, 0]])

        self.play(Write(shear_words, run_time = 1))
        self.add_foreground_mobject(shear_words)
        self.apply_transposed_matrix([[1, 0], [1, 1]])
        self.dither()

class IntroduceIdeaOfComposition(RotationThenShear):
    def construct(self):
        self.setup()
        self.show_composition()
        self.track_basis_vectors()

    def show_composition(self):
        words = TextMobject([
            "``Composition''",
            "of a",
            "rotation",
            "and a",
            "shear"
        ])
        words.split()[0].submobject_gradient_highlight(YELLOW, PINK, use_color_range_to = False)
        words.split()[2].highlight(YELLOW)
        words.split()[4].highlight(PINK)
        words.add_background_rectangle()
        words.to_edge(UP)

        self.apply_transposed_matrix([[0, 1], [-1, 0]], run_time = 2)
        self.apply_transposed_matrix([[1, 0], [1, 1]], run_time = 2)
        self.play(Write(words))
        self.dither()

    def track_basis_vectors(self):
        pass























