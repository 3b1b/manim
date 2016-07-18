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
from mobject.vectorized_mobject import *

from eola.matrix import *
from eola.two_d_space import *

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject("""
            Mathematics requires a small dose, not of genius, \\\\
            but of an imaginative freedom which, in a larger \\\\
            dose, would be insanity.
        """)
        words.to_edge(UP)    
        for mob in words.submobjects[49:49+18]:
            mob.highlight(GREEN)
        words.show()
        author = TextMobject("-Angus K. Rodgers")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.dither(3)
        self.play(Write(author, run_time = 3))
        self.dither()


class CoordinatesWereFamiliar(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.student_says("I know this already")
        self.random_blink()
        self.teacher_says("Ah, but there is a subtlety")
        self.random_blink()
        self.dither()


class CoordinatesAsScalars(VectorScene):
    def construct(self):
        self.axes = self.add_axes()
        vector = self.add_vector([3, -2])
        array, x_line, y_line = self.vector_to_coords(vector)
        self.add(array)
        self.dither()
        new_array = self.general_idea_of_scalars(array)
        self.scale_basis_vectors(new_array)
        self.show_symbolic_sum(new_array, vector)

    def general_idea_of_scalars(self, array):
        starting_mobjects = self.get_mobjects()

        title = TextMobject("Think of each coordinate as a scalar")
        title.to_edge(UP)

        x, y = array.get_mob_matrix().flatten()
        new_x = x.copy().scale(2).highlight(X_COLOR)
        new_x.move_to(3*LEFT+2*UP)
        new_y = y.copy().scale(2).highlight(Y_COLOR)
        new_y.move_to(3*RIGHT+2*UP)

        i_hat, j_hat = self.get_basis_vectors()
        new_i_hat = Vector(3*i_hat.get_end(), color = X_COLOR)
        new_j_hat = Vector(-2*j_hat.get_end(), color = Y_COLOR)
        VMobject(i_hat, new_i_hat).shift(3*LEFT)
        VMobject(j_hat, new_j_hat).shift(3*RIGHT)

        new_array = Matrix([new_x.copy(), new_y.copy()])
        new_array.replace(array)
        new_array.shift(0.5*DOWN)

        self.remove(*starting_mobjects)
        self.play(
            Transform(x, new_x),
            Transform(y, new_y),
            Write(title),
        )
        self.play(FadeIn(i_hat), FadeIn(j_hat))
        self.dither()
        self.play(
            Transform(i_hat, new_i_hat),
            Transform(j_hat, new_j_hat)
        )
        self.dither()
        starting_mobjects.remove(array)
        self.play(
            Transform(
                VMobject(x, y),
                VMobject(*new_array.get_mob_matrix().flatten())
            ),
            FadeOut(i_hat),
            FadeOut(j_hat),
            Write(new_array.get_brackets()),
            FadeIn(VMobject(*starting_mobjects)),
            FadeOut(title)
        )
        self.remove(x, y)
        self.add(new_array)
        return new_array

    def scale_basis_vectors(self, new_array):
        self.play(ApplyMethod(self.axes.highlight, GREY))
        i_hat, j_hat = self.get_basis_vectors()
        for mob in i_hat, j_hat:
            mob.set_stroke(width = 6)
        self.add_vector(i_hat)
        i_hat_label = self.label_vector(
            i_hat, "\\hat{\\imath}", 
            color = X_COLOR, 
            label_scale_val = 1
        )
        self.add_vector(j_hat)
        j_hat_label = self.label_vector(
            j_hat, "\\hat{\\jmath}", 
            color = Y_COLOR, 
            label_scale_val = 1
        )

        x, y = new_array.get_mob_matrix().flatten()
        for coord, v, label, factor, shift_right in [
            (x, i_hat, i_hat_label, 3, False), 
            (y, j_hat, j_hat_label, -2, True)
            ]:
            faded_v = v.copy().fade(0.5)
            scaled_v = Vector(factor*v.get_end(), color = v.get_color())

            scaled_label = VMobject(coord.copy(), label.copy())
            scaled_label.arrange_submobjects(RIGHT, buff = 0.1)
            scaled_label.move_to(label, DOWN+RIGHT)
            scaled_label.shift(scaled_v.get_center()-v.get_center())
            coord_copy = coord.copy()
            self.play(
                Transform(v.copy(), faded_v),
                Transform(v, scaled_v),
                Transform(VMobject(coord_copy, label), scaled_label),
            )
            self.dither()
            if shift_right:
                group = VMobject(v, coord_copy, label)
                self.play(ApplyMethod(group.shift, 3*RIGHT))
        self.dither()


    def show_symbolic_sum(self, new_array, vector):
        new_mob = TexMobject([
            "3\\hat{\\imath}", "+", "(-2)\\hat{\\jmath}"
        ])
        new_mob.shift(vector.get_end()-new_mob.get_corner(UP+LEFT))
        i_hat, plus, j_hat = new_mob.split()
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)

        self.play(Transform(new_array, new_mob))
        self.dither()
        





















