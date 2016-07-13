import numpy as np

from scene import Scene
from mobject import Mobject
from mobject.vectorized_mobject import VMobject
from mobject.tex_mobject import TexMobject, TextMobject
from animation.transform import ApplyPointwiseFunction, Transform, \
    ApplyMethod, FadeOut
from animation.simple_animations import ShowCreation
from topics.number_line import NumberPlane
from topics.geometry import Vector, Line, Circle


from helpers import *

def matrix_to_tex_string(matrix):
    matrix = np.array(matrix).astype("string")
    n_rows, n_cols = matrix.shape
    prefix = "\\left[ \\begin{array}{%s}"%("c"*n_cols)
    suffix = "\\end{array} \\right]"
    rows = [
        " & ".join(row)
        for row in matrix
    ]
    return prefix + " \\\\ ".join(rows) + suffix


def matrix_to_mobject(matrix):
    return TexMobject(matrix_to_tex_string(matrix))

class LinearTransformationScene(Scene):
    CONFIG = {
        "include_background_plane" : True,
        "include_foreground_plane" : True,
        "foreground_plane_kwargs" : {
            "x_radius" : 2*SPACE_WIDTH,
            "y_radius" : 2*SPACE_HEIGHT,
            "secondary_line_ratio" : 0
        },
        "background_plane_kwargs" : {
            "color" : GREY,
            "secondary_color" : DARK_GREY,
            "axes_color" : GREY,
        },
        "show_coordinates" : False,
        "show_basis_vectors" : True,
        "i_hat_color" : GREEN_B,
        "j_hat_color" : RED,
    }
    def setup(self):
        self.background_mobjects = []
        self.transformable_mobject = []
        self.moving_vectors = []

        self.background_plane = NumberPlane(
            **self.background_plane_kwargs
        )

        if self.show_coordinates:
            self.background_plane.add_coordinates()
        if self.include_background_plane:                
            self.add_background_mobject(self.background_plane)
        if self.include_foreground_plane:
            self.plane = NumberPlane(**self.foreground_plane_kwargs)
            self.add_transformable_mobject(self.plane)
        if self.show_basis_vectors:
            self.add_vector((1, 0), self.i_hat_color)
            self.add_vector((0, 1), self.j_hat_color)

    def add_background_mobject(self, *mobjects):
        for mobject in mobjects:
            if mobject not in self.background_mobjects:
                self.background_mobjects.append(mobject)
                self.add(mobject)
            
    def add_transformable_mobject(self, *mobjects):
        for mobject in mobjects:
            if mobject not in self.transformable_mobject:
                self.transformable_mobject.append(mobject)
                self.add(mobject)

    def add_vector(self, coords, color = YELLOW):
        vector = Vector(self.background_plane.num_pair_to_point(coords))
        vector.highlight(color)
        self.moving_vectors.append(vector)
        return vector

    def apply_matrix(self, matrix, **kwargs):
        matrix = np.array(matrix)
        if matrix.shape == (2, 2):
            new_matrix = np.identity(3)
            new_matrix[:2, :2] = matrix
            matrix = new_matrix
        elif matrix.shape != (3, 3):
            raise "Matrix has bad dimensions"
        transpose = np.transpose(matrix)

        def func(point):
            return np.dot(point, transpose)

        new_vectors = [
            Vector(func(v.get_end()), color = v.get_stroke_color())
            for v in self.moving_vectors
        ]
        self.play(
            ApplyPointwiseFunction(
                func,
                VMobject(*self.transformable_mobject),
                **kwargs
            ),
            Transform(
                VMobject(*self.moving_vectors),
                VMobject(*new_vectors), 
                **kwargs
            )
        )

class Matrix(VMobject):
    CONFIG = {
        "v_buff" : 0.5,
        "h_buff" : 1,
    }
    def __init__(self, matrix, **kwargs):
        """
        Matrix can either either include numbres, tex_strings, 
        or mobjects
        """
        VMobject.__init__(self, **kwargs)
        matrix = np.array(matrix)
        assert(matrix.ndim == 2)
        if not isinstance(matrix[0][0], Mobject):
            matrix = matrix.astype("string")
            matrix = self.string_matrix_to_mob_matrix(matrix)
        self.organize_mob_matrix(matrix)
        self.add(*matrix.flatten())
        self.add_brackets()
        self.center()
        self.mob_matrix = matrix

    def string_matrix_to_mob_matrix(self, matrix):
        return np.array([
            map(TexMobject, row)
            for row in matrix
        ])

    def organize_mob_matrix(self, matrix):
        for i, row in enumerate(matrix):
            for j, elem in enumerate(row):
                mob = matrix[i][j]
                if i == 0 and j == 0:
                    continue
                elif i == 0:
                    mob.next_to(matrix[i][j-1], RIGHT, self.h_buff)
                else:
                    mob.next_to(matrix[i-1][j], DOWN, self.v_buff)
        return self

    def get_mob_matrix(self):
        return self.mob_matrix

    def add_brackets(self):
        bracket_pair = TexMobject("\\big[ \\big]")
        bracket_pair.scale(2)
        bracket_pair.stretch_to_fit_height(self.get_height() + 0.5)
        l_bracket, r_bracket = bracket_pair.split()
        l_bracket.next_to(self, LEFT)
        r_bracket.next_to(self, RIGHT)
        self.add(l_bracket, r_bracket)
        return self


class NumericalMatrixMultiplication(Scene):
    CONFIG = {
        "left_matrix" : [[1, 2], [3, 4]],
        "right_matrix" : [[5, 6], [7, 8]]
    }
    def construct(self):
        left_string_matrix, right_string_matrix = [
            np.array(matrix).astype("string")
            for matrix in self.left_matrix, self.right_matrix
        ]
        if right_string_matrix.shape[0] != left_string_matrix.shape[1]:
            raise Exception("Incompatible shapes for matrix multiplication")

        left = Matrix(left_string_matrix)
        right = Matrix(right_string_matrix)
        result = self.get_result_matrix(
            left_string_matrix, right_string_matrix
        )

        self.organize_matrices(left, right, result)
        # self.add_lines(left, right)
        self.animate_product(left, right, result)


    def get_result_matrix(self, left, right):
        (m, k), n = left.shape, right.shape[1]
        mob_matrix = np.array([VMobject()]).repeat(m*n).reshape((m, n))
        for a in range(m):
            for b in range(n):
                parts = [
                    prefix + "(%s)(%s)"%(left[a][c], right[c][b])
                    for c in range(k)
                    for prefix in ["" if c == 0 else "+"]
                ]
                mob_matrix[a][b] = TexMobject(parts, next_to_buff = 0.1)
        return Matrix(mob_matrix)

    def add_lines(self, left, right):
        line_kwargs = {
            "color" : BLUE,
            "stroke_width" : 2,
        }
        left_rows = [
            VMobject(*row) for row in left.get_mob_matrix()
        ]
        h_lines = VMobject()
        for row in left_rows[:-1]:
            h_line = Line(row.get_left(), row.get_right(), **line_kwargs)
            h_line.next_to(row, DOWN, buff = left.v_buff/2.)
            h_lines.add(h_line)

        right_cols = [
            VMobject(*col) for col in np.transpose(right.get_mob_matrix())
        ]
        v_lines = VMobject()
        for col in right_cols[:-1]:
            v_line = Line(col.get_top(), col.get_bottom(), **line_kwargs)
            v_line.next_to(col, RIGHT, buff = right.h_buff/2.)
            v_lines.add(v_line)

        self.play(ShowCreation(h_lines))
        self.play(ShowCreation(v_lines))
        self.dither()
        self.show_frame()

    def organize_matrices(self, left, right, result):
        equals = TexMobject("=")
        everything = VMobject(left, right, equals, result)
        everything.arrange_submobjects()
        everything.scale_to_fit_width(2*SPACE_WIDTH-1)
        self.add(everything)


    def animate_product(self, left, right, result):
        l_matrix = left.get_mob_matrix()
        r_matrix = right.get_mob_matrix()
        result_matrix = result.get_mob_matrix()
        circle = Circle(
            radius = l_matrix[0][0].get_height(),
            color = GREEN
        )
        circles = VMobject(*[
            entry.get_point_mobject()
            for entry in l_matrix[0][0], r_matrix[0][0]
        ])
        (m, k), n = l_matrix.shape, r_matrix.shape[1]
        for mob in result_matrix.flatten():
            mob.highlight(BLACK)
        lagging_anims = []
        for a in range(m):
            for b in range(n):
                for c in range(k):
                    l_matrix[a][c].highlight(YELLOW)
                    r_matrix[c][b].highlight(YELLOW)
                for c in range(k):
                    start_parts = VMobject(
                        l_matrix[a][c].copy(),
                        r_matrix[c][b].copy()
                    )
                    result_entry = result_matrix[a][b].split()[c]

                    new_circles = VMobject(*[
                        circle.copy().shift(part.get_center())
                        for part in start_parts.split()
                    ])
                    self.play(Transform(circles, new_circles))
                    self.play(
                        Transform(
                            start_parts, 
                            result_entry.copy().highlight(YELLOW), 
                            path_arc = -np.pi/2
                        ),
                        *lagging_anims
                    )
                    result_entry.highlight(YELLOW)
                    self.remove(start_parts)
                    lagging_anims = [
                        ApplyMethod(result_entry.highlight, WHITE)
                    ]

                for c in range(k):
                    l_matrix[a][c].highlight(WHITE)
                    r_matrix[c][b].highlight(WHITE)
        self.play(FadeOut(circles), *lagging_anims)
        self.dither()












