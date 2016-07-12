import numpy as np

from scene import Scene
from mobject.vectorized_mobject import VMobject
from mobject.tex_mobject import TexMobject, TextMobject
from animation.transform import ApplyPointwiseFunction, Transform
from topics.number_line import NumberPlane
from topics.geometry import Vector


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
        },
        "background_plane_kwargs" : {},
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
            color = GREY,
            secondary_color = DARK_GREY,
            **self.background_plane_kwargs
        )

        if self.show_coordinates:
            self.background_plane.add_coordinates()
        if self.include_background_plane:                
            self.add_to_background(self.background_plane)
        if self.include_foreground_plane:
            self.plane = NumberPlane(**self.foreground_plane_kwargs)
            self.add_to_transformable(self.plane)
        if self.show_basis_vectors:
            self.add_vector((1, 0), self.i_hat_color)
            self.add_vector((0, 1), self.j_hat_color)

    def add_to_background(self, *mobjects):
        for mobject in mobjects:
            if mobject not in self.background_mobjects:
                self.background_mobjects.append(mobject)
                self.add(mobject)
            
    def add_to_transformable(self, *mobjects):
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








