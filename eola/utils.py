import numpy as np

from scene import Scene
from mobject.vectorized_mobject import VMobject
from mobject.tex_mobject import TexMobject, TextMobject
from animation.transform import ApplyMatrix, ApplyMethod
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
        self.foreground_mobjects = []
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
            self.add_to_foreground(self.plane)
        if self.show_basis_vectors:
            i_hat = Vector(self.background_plane.num_pair_to_point((1, 0)))
            j_hat = Vector(self.background_plane.num_pair_to_point((0, 1)))
            i_hat.highlight(self.i_hat_color)
            j_hat.highlight(self.j_hat_color)
            self.add_to_foreground(i_hat, j_hat)

    def add_to_background(self, *mobjects):
        for mobject in mobjects:
            if mobject not in self.background_mobjects:
                self.background_mobjects.append(mobject)
                self.add(mobject)
            
    def add_to_foreground(self, *mobjects):
        for mobject in mobjects:
            if mobject not in self.foreground_mobjects:
                self.foreground_mobjects.append(mobject)
                self.add(mobject)

    def apply_matrix(self, matrix, **kwargs):
        self.play(ApplyMatrix(
            matrix,
            VMobject(*self.foreground_mobjects),
            **kwargs
        ))








