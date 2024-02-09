from __future__ import annotations

import itertools as it

import numpy as np

from manimlib.constants import DOWN, LEFT, RIGHT, ORIGIN
from manimlib.constants import DEGREES
from manimlib.mobject.numbers import DecimalNumber
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence, Union, Tuple, Optional
    from manimlib.typing import ManimColor, Vect3, VectNArray, Self

    StringMatrixType = Union[Sequence[Sequence[str]], np.ndarray[int, np.dtype[np.str_]]]
    FloatMatrixType = Union[Sequence[Sequence[float]], VectNArray]
    VMobjectMatrixType = Sequence[Sequence[VMobject]]
    GenericMatrixType = Union[FloatMatrixType, StringMatrixType, VMobjectMatrixType]


class Matrix(VMobject):
    def __init__(
        self,
        matrix: GenericMatrixType,
        v_buff: float = 0.5,
        h_buff: float = 0.5,
        bracket_h_buff: float = 0.2,
        bracket_v_buff: float = 0.25,
        height: float | None = None,
        element_config: dict = dict(),
        element_alignment_corner: Vect3 = DOWN,
        ellipses_row: Optional[int] = None,
        ellipses_col: Optional[int] = None,
    ):
        """
        Matrix can either include numbers, tex_strings,
        or mobjects
        """
        super().__init__()

        self.mob_matrix = self.create_mobject_matrix(
            matrix, v_buff, h_buff, element_alignment_corner,
            **element_config
        )
        # Create helpful groups for the elements
        n_cols = len(self.mob_matrix[0])
        self.elements = VGroup(*it.chain(*self.mob_matrix))
        self.columns = VGroup(*(
            VGroup(*(row[i] for row in self.mob_matrix))
            for i in range(n_cols)
        ))
        self.rows = VGroup(*(VGroup(*row) for row in self.mob_matrix))
        self.ellipses = VGroup()

        # Add elements and brackets
        self.elements.center()
        self.add(self.elements)
        if height is not None:
            self.set_height(height - 2 * bracket_v_buff)
        self.add_brackets(bracket_v_buff, bracket_h_buff)
        self.add(self.ellipses)

        # Potentially add ellipses
        self.swap_entries_for_ellipses(
            ellipses_row,
            ellipses_col,
        )

    def create_mobject_matrix(
        self,
        matrix: GenericMatrixType,
        v_buff: float,
        h_buff: float,
        aligned_corner: Vect3,
        **element_config
    ) -> VMobjectMatrixType:
        """
        Creates and organizes the matrix of mobjects
        """
        mob_matrix = [
            [
                self.element_to_mobject(element, **element_config)
                for element in row
            ]
            for row in matrix
        ]
        max_width = max(elem.get_width() for row in mob_matrix for elem in row)
        max_height = max(elem.get_height() for row in mob_matrix for elem in row)
        x_step = (max_width + h_buff) * RIGHT
        y_step = (max_height + v_buff) * DOWN
        for i, row in enumerate(mob_matrix):
            for j, elem in enumerate(row):
                elem.move_to(i * y_step + j * x_step, aligned_corner)
        return mob_matrix

    def element_to_mobject(self, element, **config) -> VMobject:
        if isinstance(element, VMobject):
            return element
        elif isinstance(element, float | complex):
            return DecimalNumber(element, **config)
        else:
            return Tex(str(element), **config)

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
        self.brackets = VGroup(l_bracket, r_bracket)
        self.add(*brackets)
        return self

    def get_column(self, index: int):
        if not 0 <= index < len(self.columns):
            raise IndexError(f"Index {index} out of bound for matrix with {len(self.columns)} columns")
        return self.columns[index]

    def get_row(self, index: int):
        if not 0 <= index < len(self.rows):
            raise IndexError(f"Index {index} out of bound for matrix with {len(self.rows)} rows")
        return self.rows[index]

    def get_columns(self) -> VGroup:
        return self.columns

    def get_rows(self) -> VGroup:
        return self.rows

    def set_column_colors(self, *colors: ManimColor) -> Self:
        columns = self.get_columns()
        for color, column in zip(colors, columns):
            column.set_color(color)
        return self

    def add_background_to_entries(self) -> Self:
        for mob in self.get_entries():
            mob.add_background_rectangle()
        return self

    def swap_entries_for_ellipses(
        self,
        row_index: Optional[int] = None,
        col_index: Optional[int] = None,
        height_ratio: float = 0.65,
        width_ratio: float = 0.4
    ):
        rows = self.get_rows()
        cols = self.get_columns()

        avg_row_height = rows.get_height() / len(rows)
        vdots_height = height_ratio * avg_row_height

        avg_col_width = cols.get_width() / len(cols)
        hdots_width = width_ratio * avg_col_width

        use_vdots = row_index is not None and -len(rows) <= row_index < len(rows)
        use_hdots = col_index is not None and -len(cols) <= col_index < len(cols)

        def swap_entry_for_dots(entry, dots):
            dots.move_to(entry)
            entry.become(dots)
            self.elements.remove(entry)
            self.ellipses.add(entry)

        if use_vdots:
            for column in cols:
                # Add vdots
                dots = Tex(R"\vdots")
                dots.set_height(vdots_height)
                swap_entry_for_dots(column[row_index], dots)
        if use_hdots:
            for row in rows:
                # Add hdots
                dots = Tex(R"\hdots")
                dots.set_width(hdots_width)
                swap_entry_for_dots(row[col_index], dots)
        if use_vdots and use_hdots:
            rows[row_index][col_index].rotate(-45 * DEGREES)
        return self

    def get_mob_matrix(self) -> VMobjectMatrixType:
        return self.mob_matrix

    def get_entries(self) -> VGroup:
        return self.elements

    def get_brackets(self) -> VGroup:
        return self.brackets


class DecimalMatrix(Matrix):
    def __init__(
        self,
        matrix: FloatMatrixType,
        num_decimal_places: int = 2,
        decimal_config: dict = dict(),
        **config
    ):
        super().__init__(
            matrix,
            element_config=dict(
                num_decimal_places=num_decimal_places,
                **decimal_config
            ),
            **config
        )

    def element_to_mobject(self, element, **decimal_config) -> DecimalNumber:
        return DecimalNumber(element, **decimal_config)


class IntegerMatrix(DecimalMatrix):
    def __init__(
        self,
        matrix: FloatMatrixType,
        num_decimal_places: int = 0,
        decimal_config: dict = dict(),
        **config
    ):
        super().__init__(matrix, num_decimal_places, decimal_config, **config)



class TexMatrix(Matrix):
    def __init__(
        self,
        matrix: StringMatrixType,
        tex_config: dict = dict(),
        **config,
    ):
        super().__init__(
            matrix,
            element_config=tex_config,
            **config
        )



class MobjectMatrix(Matrix):
    def __init__(
        self,
        group: VGroup,
        n_rows: int | None = None,
        n_cols: int | None = None,
        height: float = 4.0,
        element_alignment_corner=ORIGIN,
        **config,
    ):
        # Have fallback defaults of n_rows and n_cols
        n_mobs = len(group)
        if n_rows is None:
            n_rows = int(np.sqrt(n_mobs)) if n_cols is None else n_mobs // n_cols
        if n_cols is None:
            n_cols = n_mobs // n_rows

        if len(group) < n_rows * n_cols:
            raise Exception("Input to MobjectMatrix must have at least n_rows * n_cols entries")

        mob_matrix = [
            [group[n * n_cols + k] for k in range(n_cols)]
            for n in range(n_rows)
        ]
        config.update(
            height=height,
            element_alignment_corner=element_alignment_corner,
        )
        super().__init__(mob_matrix,  **config)

    def element_to_mobject(self, element: VMobject, **config) -> VMobject:
        return element
