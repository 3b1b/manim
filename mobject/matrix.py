from __future__ import absolute_import

import numpy as np

from mobject.mobject import Mobject
from mobject.svg.tex_mobject import TexMobject
from mobject.types.vectorized_mobject import VGroup
from mobject.types.vectorized_mobject import VMobject
from mobject.shape_matchers import BackgroundRectangle

from constants import *

VECTOR_LABEL_SCALE_FACTOR = 0.8


def matrix_to_tex_string(matrix):
    matrix = np.array(matrix).astype("string")
    if matrix.ndim == 1:
        matrix = matrix.reshape((matrix.size, 1))
    n_rows, n_cols = matrix.shape
    prefix = "\\left[ \\begin{array}{%s}" % ("c" * n_cols)
    suffix = "\\end{array} \\right]"
    rows = [
        " & ".join(row)
        for row in matrix
    ]
    return prefix + " \\\\ ".join(rows) + suffix


def matrix_to_mobject(matrix):
    return TexMobject(matrix_to_tex_string(matrix))


def vector_coordinate_label(vector_mob, integer_labels=True,
                            n_dim=2, color=WHITE):
    vect = np.array(vector_mob.get_end())
    if integer_labels:
        vect = np.round(vect).astype(int)
    vect = vect[:n_dim]
    vect = vect.reshape((n_dim, 1))
    label = Matrix(vect, add_background_rectangles=True)
    label.scale(VECTOR_LABEL_SCALE_FACTOR)

    shift_dir = np.array(vector_mob.get_end())
    if shift_dir[0] >= 0:  # Pointing right
        shift_dir -= label.get_left() + DEFAULT_MOBJECT_TO_MOBJECT_BUFFER * LEFT
    else:  # Pointing left
        shift_dir -= label.get_right() + DEFAULT_MOBJECT_TO_MOBJECT_BUFFER * RIGHT
    label.shift(shift_dir)
    label.set_color(color)
    label.rect = BackgroundRectangle(label)
    label.add_to_back(label.rect)
    return label


class Matrix(VMobject):
    CONFIG = {
        "v_buff": 0.5,
        "h_buff": 1,
        "add_background_rectangles": False
    }

    def __init__(self, matrix, **kwargs):
        """
        Matrix can either either include numbres, tex_strings,
        or mobjects
        """
        VMobject.__init__(self, **kwargs)
        matrix = np.array(matrix)
        if matrix.ndim == 1:
            matrix = matrix.reshape((matrix.size, 1))
        if not isinstance(matrix[0][0], Mobject):
            matrix = matrix.astype("string")
            matrix = self.string_matrix_to_mob_matrix(matrix)
        self.organize_mob_matrix(matrix)
        self.add(*matrix.flatten())
        self.add_brackets()
        self.center()
        self.mob_matrix = matrix
        if self.add_background_rectangles:
            for mob in matrix.flatten():
                mob.add_background_rectangle()

    def string_matrix_to_mob_matrix(self, matrix):
        return np.array([
            map(TexMobject, row)
            for row in matrix
        ]).reshape(matrix.shape)

    def organize_mob_matrix(self, matrix):
        for i, row in enumerate(matrix):
            for j, elem in enumerate(row):
                mob = matrix[i][j]
                if i == 0 and j == 0:
                    continue
                elif i == 0:
                    mob.next_to(matrix[i][j - 1], RIGHT, self.h_buff)
                else:
                    mob.next_to(matrix[i - 1][j], DOWN, self.v_buff)
        return self

    def add_brackets(self):
        bracket_pair = TexMobject("\\big[ \\big]")
        bracket_pair.scale(2)
        bracket_pair.stretch_to_fit_height(self.get_height() + 0.5)
        l_bracket, r_bracket = bracket_pair.split()
        l_bracket.next_to(self, LEFT)
        r_bracket.next_to(self, RIGHT)
        self.add(l_bracket, r_bracket)
        self.brackets = VGroup(l_bracket, r_bracket)
        return self

    def set_color_columns(self, *colors):
        for i, color in enumerate(colors):
            VGroup(*self.mob_matrix[:, i]).set_color(color)
        return self

    def add_background_to_entries(self):
        for mob in self.get_entries():
            mob.add_background_rectangle()
        return self

    def get_mob_matrix(self):
        return self.mob_matrix

    def get_entries(self):
        return VGroup(*self.get_mob_matrix().flatten())

    def get_brackets(self):
        return self.brackets
