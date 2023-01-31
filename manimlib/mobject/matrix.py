from __future__ import annotations

import itertools as it

import numpy as np

from manimlib.constants import DEFAULT_MOBJECT_TO_MOBJECT_BUFFER
from manimlib.constants import DOWN, LEFT, RIGHT, UP
from manimlib.constants import WHITE
from manimlib.mobject.numbers import DecimalNumber
from manimlib.mobject.numbers import Integer
from manimlib.mobject.shape_matchers import BackgroundRectangle
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.svg.tex_mobject import TexText
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence, Self
    import numpy.typing as npt
    from manimlib.mobject.mobject import Mobject
    from manimlib.typing import ManimColor, Vect3


VECTOR_LABEL_SCALE_FACTOR = 0.8


def matrix_to_tex_string(matrix: npt.ArrayLike) -> str:
    matrix = np.array(matrix).astype("str")
    if matrix.ndim == 1:
        matrix = matrix.reshape((matrix.size, 1))
    n_rows, n_cols = matrix.shape
    prefix = R"\left[ \begin{array}{%s}" % ("c" * n_cols)
    suffix = R"\end{array} \right]"
    rows = [
        " & ".join(row)
        for row in matrix
    ]
    return prefix + R" \\ ".join(rows) + suffix


def matrix_to_mobject(matrix: npt.ArrayLike) -> Tex:
    return Tex(matrix_to_tex_string(matrix))


def vector_coordinate_label(
    vector_mob: VMobject,
    integer_labels: bool = True,
    n_dim: int = 2,
    color: ManimColor = WHITE
) -> Matrix:
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
    def __init__(
        self,
        matrix: Sequence[Sequence[str | float | VMobject]],
        v_buff: float = 0.8,
        h_buff: float = 1.3,
        bracket_h_buff: float = 0.2,
        bracket_v_buff: float = 0.25,
        add_background_rectangles_to_entries: bool = False,
        include_background_rectangle: bool = False,
        element_alignment_corner: Vect3 = DOWN,
        **kwargs
    ):
        """
        Matrix can either include numbers, tex_strings,
        or mobjects
        """
        super().__init__()

        mob_matrix = self.matrix_to_mob_matrix(matrix, **kwargs)
        self.mob_matrix = mob_matrix

        self.organize_mob_matrix(mob_matrix, v_buff, h_buff, element_alignment_corner)
        self.elements = VGroup(*it.chain(*mob_matrix))
        self.add(self.elements)
        self.add_brackets(bracket_v_buff, bracket_h_buff)
        self.center()
        if add_background_rectangles_to_entries:
            for mob in self.elements:
                mob.add_background_rectangle()
        if include_background_rectangle:
            self.add_background_rectangle()


    def element_to_mobject(self, element: str | float | VMobject, **config) -> VMobject:
        if isinstance(element, VMobject):
            return element
        return Tex(str(element), **config)

    def matrix_to_mob_matrix(
        self,
        matrix: Sequence[Sequence[str | float | VMobject]],
        **config
    ) -> list[list[VMobject]]:
        return [
            [
                self.element_to_mobject(item, **config)
                for item in row
            ]
            for row in matrix
        ]

    def organize_mob_matrix(
        self,
        matrix: list[list[VMobject]],
        v_buff: float,
        h_buff: float,
        aligned_corner: Vect3,
    ) -> Self:
        for i, row in enumerate(matrix):
            for j, elem in enumerate(row):
                mob = matrix[i][j]
                mob.move_to(
                    i * v_buff * DOWN + j * h_buff * RIGHT,
                    aligned_corner
                )
        return self

    def add_brackets(self, v_buff: float, h_buff: float) -> Self:
        height = len(self.mob_matrix)
        brackets = Tex("".join((
            R"\left[\begin{array}{c}",
            *height * [R"\quad \\"],
            R"\end{array}\right]",
        )))
        brackets.set_height(self.get_height() + v_buff)
        l_bracket = brackets[:len(brackets) // 2]
        r_bracket = brackets[len(brackets) // 2:]
        l_bracket.next_to(self, LEFT, h_buff)
        r_bracket.next_to(self, RIGHT, h_buff)
        brackets.set_submobjects([l_bracket, r_bracket])
        self.brackets = brackets
        self.add(*brackets)
        return self

    def get_columns(self) -> VGroup:
        return VGroup(*[
            VGroup(*[row[i] for row in self.mob_matrix])
            for i in range(len(self.mob_matrix[0]))
        ])

    def get_rows(self) -> VGroup:
        return VGroup(*[
            VGroup(*row)
            for row in self.mob_matrix
        ])

    def set_column_colors(self, *colors: ManimColor) -> Self:
        columns = self.get_columns()
        for color, column in zip(colors, columns):
            column.set_color(color)
        return self

    def add_background_to_entries(self) -> Self:
        for mob in self.get_entries():
            mob.add_background_rectangle()
        return self

    def get_mob_matrix(self) -> list[list[Mobject]]:
        return self.mob_matrix

    def get_entries(self) -> VGroup:
        return self.elements

    def get_brackets(self) -> VGroup:
        return self.brackets


class DecimalMatrix(Matrix):
    def element_to_mobject(self, element: float, num_decimal_places: int = 1, **config) -> DecimalNumber:
        return DecimalNumber(element, num_decimal_places=num_decimal_places, **config)


class IntegerMatrix(Matrix):
    def __init__(
        self,
        matrix: npt.ArrayLike,
        element_alignment_corner: Vect3 = UP,
        **kwargs
    ):
        super().__init__(matrix, element_alignment_corner=element_alignment_corner, **kwargs)

    def element_to_mobject(self, element: int, **config) -> Integer:
        return Integer(element, **config)


class MobjectMatrix(Matrix):
    def element_to_mobject(self, element: VMobject, **config) -> VMobject:
        return element


def get_det_text(
    matrix: Matrix,
    determinant: int | str | None = None,
    background_rect: bool = False,
    initial_scale_factor: int = 2
) -> VGroup:
    parens = Tex("()")
    parens.scale(initial_scale_factor)
    parens.stretch_to_fit_height(matrix.get_height())
    l_paren, r_paren = parens.split()
    l_paren.next_to(matrix, LEFT, buff=0.1)
    r_paren.next_to(matrix, RIGHT, buff=0.1)
    det = TexText("det")
    det.scale(initial_scale_factor)
    det.next_to(l_paren, LEFT, buff=0.1)
    if background_rect:
        det.add_background_rectangle()
    det_text = VGroup(det, l_paren, r_paren)
    if determinant is not None:
        eq = Tex("=")
        eq.next_to(r_paren, RIGHT, buff=0.1)
        result = Tex(str(determinant))
        result.next_to(eq, RIGHT, buff=0.2)
        det_text.add(eq, result)
    return det_text
