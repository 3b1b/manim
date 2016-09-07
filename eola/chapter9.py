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

V_COLOR = YELLOW


class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject(
            "\\centering ``Mathematics is the art of giving the \\\\",
            "same name ",
            "to ",
            "different things",
            ".''",
            arg_separator = " "
        )
        words.highlight_by_tex("same name ", BLUE)
        words.highlight_by_tex("different things", MAROON_B)
        # words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        author = TextMobject("-Henri Poincar\\'e.")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.dither(2)
        self.play(Write(author, run_time = 3))
        self.dither(2)

class LinearCombinationScene(LinearTransformationScene):
    CONFIG = {
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : SPACE_WIDTH,
            "y_radius" : SPACE_HEIGHT,
            "secondary_line_ratio" : 1
        },
    }
    def show_linear_combination(self, numerical_coords,
                                basis_vectors,
                                coord_mobs = None,
                                show_sum_vect = False,
                                sum_vect_color = V_COLOR,
                                ):
        for basis, scalar in zip(basis_vectors, numerical_coords):
            if not hasattr(basis, "label"):
                basis.label = VectorizedPoint()
                direction = np.round(basis.get_end().rotate(np.pi/2))
                basis.label.next_to(basis.get_center(), direction)
            basis.save_state()
            basis.label.save_state()
            basis.target = basis.copy().scale(scalar)
            basis.label.target = basis.label.copy()
            basis.label.target.shift(
                basis.target.get_center() - basis.get_center()
            )
        if coord_mobs is None:
            coord_mobs = map(TexMobject, map(str, numerical_coords))
            VGroup(*coord_mobs).set_fill(opacity = 0)
            for coord, basis in zip(coord_mobs, basis_vectors):
                coord.next_to(basis.label, LEFT)
        for coord, basis in zip(coord_mobs, basis_vectors):
            coord.target = coord.copy()
            coord.target.next_to(basis.label.target, LEFT)
            coord.target.set_fill(basis.get_color(), opacity = 1)
            self.play(*map(MoveToTarget, [
                coord, basis, basis.label
            ]))
            self.dither()
        self.play(*[
            ApplyMethod(m.shift, basis_vectors[0].get_end())
            for m in self.get_mobjects_from_last_animation()
        ])
        if show_sum_vect:
            sum_vect = Vector(
                basis_vectors[1].get_end(),
                color = sum_vect_color
            )
            self.play(ShowCreation(sum_vect))
        self.dither(2)
        self.play(*it.chain(
            [basis.restore for basis in basis_vectors],
            [basis.label.restore for basis in basis_vectors],
            [FadeOut(coord) for coord in coord_mobs],
            [FadeOut(sum_vect) for x in [1] if show_sum_vect],
        ))



class RemindOfCoordinates(LinearCombinationScene):
    CONFIG = {
        "vector_coords" : [3, 2]
    }
    def construct(self):
        self.remove(self.i_hat, self.j_hat)

        v = self.add_vector(self.vector_coords, color = V_COLOR)
        coords = self.write_vector_coordinates(v)
        self.show_standard_coord_meaning(*coords.get_entries().copy())
        self.show_abstract_scalar_idea(*coords.get_entries().copy())
        self.scale_basis_vectors(*coords.get_entries().copy())



    def show_standard_coord_meaning(self, x_coord, y_coord):
        x, y = self.vector_coords
        x_line = Line(ORIGIN, x*RIGHT, color = GREEN)
        y_line = Line(ORIGIN, y*UP, color = RED)
        y_line.shift(x_line.get_end())
        for line, coord, direction in (x_line, x_coord, DOWN), (y_line, y_coord, LEFT):
            self.play(
                coord.highlight, line.get_color(),
                coord.next_to, line.get_center(), direction,
                ShowCreation(line),                
            )
            self.dither()
        self.dither()
        self.play(*map(FadeOut, [x_coord, y_coord, x_line, y_line]))


    def show_abstract_scalar_idea(self, x_coord, y_coord):
        x_shift, y_shift = 4*LEFT, 4*RIGHT
        to_save = x_coord, y_coord, self.i_hat, self.j_hat
        for mob in to_save:
            mob.save_state()
        everything = VGroup(*self.get_mobjects())

        x, y = self.vector_coords  
        scaled_i = self.i_hat.copy().scale(x)
        scaled_j = self.j_hat.copy().scale(y)
        VGroup(self.i_hat, scaled_i).shift(x_shift)
        VGroup(self.j_hat, scaled_j).shift(y_shift)

        self.play(
            FadeOut(everything),
            x_coord.scale_in_place, 1.5,
            x_coord.move_to, x_shift + 3*UP,
            y_coord.scale_in_place, 1.5,
            y_coord.move_to, y_shift + 3*UP,
        )
        self.play(*map(FadeIn, [self.i_hat, self.j_hat]))
        self.dither()
        self.play(Transform(self.i_hat, scaled_i))
        self.play(Transform(self.j_hat, scaled_j))
        self.dither()
        self.play(
            FadeIn(everything),
            *[mob.restore for mob in to_save]
        )
        self.dither()

    def scale_basis_vectors(self, x_coord, y_coord):
        self.i_hat.label = self.get_vector_label(
            self.i_hat, "\\hat{\\imath}", "right"
        )
        self.j_hat.label = self.get_vector_label(
            self.j_hat, "\\hat{\\jmath}", "left"
        )
        self.play(*map(Write, [self.i_hat.label, self.j_hat.label]))
        self.show_linear_combination(
            self.vector_coords, 
            basis_vectors = [self.i_hat, self.j_hat],
            coord_mobs = [x_coord, y_coord]
        )






















