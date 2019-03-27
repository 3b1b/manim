import numpy as np

from manimlib.constants import *
from manimlib.mobject.numbers import DecimalNumber
from manimlib.mobject.numbers import Integer
from manimlib.mobject.shape_matchers import BackgroundRectangle
from manimlib.mobject.svg.tex_mobject import TexMobject
from manimlib.mobject.svg.tex_mobject import TextMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject

VECTOR_LABEL_SCALE_FACTOR = 0.8


def matrix_to_tex_string(matrix):
    matrix = np.array(matrix).astype("str")
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
    label = Matrix(vect, add_background_rectangles_to_entries=True)
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
        "v_buff": 0.8,
        "h_buff": 1.3,
        "bracket_h_buff": MED_SMALL_BUFF,
        "bracket_v_buff": MED_SMALL_BUFF,
        "add_background_rectangles_to_entries": False,
        "include_background_rectangle": False,
        "element_to_mobject": TexMobject,
        "element_to_mobject_config": {},
        "element_alignment_corner": DR,
    }

    def __init__(self, matrix, **kwargs):
        """
        Matrix can either either include numbres, tex_strings,
        or mobjects
        """
        VMobject.__init__(self, **kwargs)
        matrix = np.array(matrix, ndmin=1)
        mob_matrix = self.matrix_to_mob_matrix(matrix)
        self.organize_mob_matrix(mob_matrix)
        self.elements = VGroup(*mob_matrix.flatten())
        self.add(self.elements)
        self.add_brackets()
        self.center()
        self.mob_matrix = mob_matrix
        if self.add_background_rectangles_to_entries:
            for mob in self.elements:
                mob.add_background_rectangle()
        if self.include_background_rectangle:
            self.add_background_rectangle()

    def matrix_to_mob_matrix(self, matrix):
        return np.vectorize(self.element_to_mobject)(
            matrix, **self.element_to_mobject_config
        )

    def organize_mob_matrix(self, matrix):
        for i, row in enumerate(matrix):
            for j, elem in enumerate(row):
                mob = matrix[i][j]
                mob.move_to(
                    i * self.v_buff * DOWN + j * self.h_buff * RIGHT,
                    self.element_alignment_corner
                )
        return self

    def add_brackets(self):
        bracket_pair = TexMobject("\\big[", "\\big]")
        bracket_pair.scale(2)
        bracket_pair.stretch_to_fit_height(
            self.get_height() + 2 * self.bracket_v_buff
        )
        l_bracket, r_bracket = bracket_pair.split()
        l_bracket.next_to(self, LEFT, self.bracket_h_buff)
        r_bracket.next_to(self, RIGHT, self.bracket_h_buff)
        self.add(l_bracket, r_bracket)
        self.brackets = VGroup(l_bracket, r_bracket)
        return self

    def get_columns(self):
        return VGroup(*[
            VGroup(*self.mob_matrix[:, i])
            for i in range(self.mob_matrix.shape[1])
        ])

    def set_column_colors(self, *colors):
        columns = self.get_columns()
        for color, column in zip(colors, columns):
            column.set_color(color)
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


class DecimalMatrix(Matrix):
    CONFIG = {
        "element_to_mobject": DecimalNumber,
        "element_to_mobject_config": {"num_decimal_places": 1}
    }


class IntegerMatrix(Matrix):
    CONFIG = {
        "element_to_mobject": Integer,
    }


class MobjectMatrix(Matrix):
    CONFIG = {
        "element_to_mobject": lambda m: m,
    }


def get_det_text(matrix, determinant=None, background_rect=False, initial_scale_factor=2):
    parens = TexMobject("(", ")")
    parens.scale(initial_scale_factor)
    parens.stretch_to_fit_height(matrix.get_height())
    l_paren, r_paren = parens.split()
    l_paren.next_to(matrix, LEFT, buff=0.1)
    r_paren.next_to(matrix, RIGHT, buff=0.1)
    det = TextMobject("det")
    det.scale(initial_scale_factor)
    det.next_to(l_paren, LEFT, buff=0.1)
    if background_rect:
        det.add_background_rectangle()
    det_text = VGroup(det, l_paren, r_paren)
    if determinant is not None:
        eq = TexMobject("=")
        eq.next_to(r_paren, RIGHT, buff=0.1)
        result = TexMobject(str(determinant))
        result.next_to(eq, RIGHT, buff=0.2)
        det_text.add(eq, result)
    return det_text
