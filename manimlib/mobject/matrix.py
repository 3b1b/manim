from __future__ import annotations

import numpy as np

from manimlib.constants import DOWN, LEFT, RIGHT, ORIGIN
from manimlib.constants import DEG
from manimlib.mobject.numbers import DecimalNumber
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence, Union, Optional
    from manimlib.typing import ManimColor, Vect3, VectNArray, Self

    StringMatrixType = Union[Sequence[Sequence[str]], np.ndarray[int, np.dtype[np.str_]]]
    FloatMatrixType = Union[Sequence[Sequence[float]], VectNArray]
    VMobjectMatrixType = Sequence[Sequence[VMobject]]
    GenericMatrixType = Union[FloatMatrixType, StringMatrixType, VMobjectMatrixType]


class Matrix(VMobject):
    """
    A visual representation of a mathematical matrix using arranged Manim
    mobjects, with square brackets and optional ellipsis entries.

    Each matrix entry is converted into a mobject and positioned in a regular
    grid. The matrix exposes groups for accessing its rows, columns, entries,
    brackets, and ellipses, making it useful for mathematical animations and
    transformations.

    Parameters
    ----------
    matrix : GenericMatrixType
        Two-dimensional iterable containing matrix entries. Entries may be
        existing VMobjects, floating-point or complex numbers, or values that
        can be represented as strings and rendered with Tex.
    v_buff : float, default=0.5
        Vertical spacing added to the maximum entry height when positioning
        consecutive rows.
    h_buff : float, default=0.5
        Horizontal spacing added to the maximum entry width when positioning
        consecutive columns.
    bracket_h_buff : float, default=0.2
        Horizontal distance between the matrix entries and the left and right
        brackets.
    bracket_v_buff : float, default=0.25
        Extra vertical space used when sizing the brackets. If ``height`` is
        specified, twice this value is subtracted from the requested row-group
        height.
    height : float or None, default=None
        Optional target height for the row group, applied before the brackets
        are created. When provided, the rows are resized to
        ``height - 2 * bracket_v_buff``.
    element_config : dict, default={}
        Keyword arguments passed to element-conversion methods. These are used
        when constructing DecimalNumber or Tex entries; existing VMobjects are
        returned directly without applying this configuration.
    element_alignment_corner : Vect3, default=DOWN
        Alignment corner used when positioning each entry in the grid.
    ellipses_row : int or None, default=None
        Optional row index whose entries are replaced visually with vertical
        ellipses. Negative indices are supported when they fall within the
        valid row-index range.
    ellipses_col : int or None, default=None
        Optional column index whose entries are replaced visually with
        horizontal ellipses. Negative indices are supported when they fall
        within the valid column-index range.

    Attributes
    ----------
    mob_matrix : VMobjectMatrixType
        Nested list containing the original entry mobjects arranged by row and
        column. Entries replaced visually by ellipses remain referenced here.
    elements : list of VMobject
        Flat list of entries currently treated as ordinary matrix elements.
        Entries replaced by ellipses are removed from this list.
    columns : VGroup
        Group of column groups. Each column contains the corresponding entry
        mobjects from all rows.
    rows : VGroup
        Group of row groups. Each row contains its entry mobjects.
    brackets : VGroup
        Group containing the left and right bracket components.
    ellipses : list of VMobject
        List of entry mobjects that have been visually replaced by ellipsis
        symbols.

    Methods
    -------
    copy(deep=False)
        Copies the matrix and remaps the ``elements`` and ``ellipses`` lists
        to the corresponding mobjects in the copied family.
    create_mobject_matrix(matrix, v_buff, h_buff, aligned_corner, **element_config)
        Converts the input entries into mobjects and arranges them in a grid.
    element_to_mobject(element, **config)
        Returns an existing VMobject unchanged, converts a float or complex
        number to DecimalNumber, or converts other values to Tex.
    create_brackets(rows, v_buff, h_buff)
        Constructs and positions the left and right matrix brackets.
    get_column(index)
        Returns the column at the specified index. Raises IndexError if the
        index is outside the valid nonnegative range.
    get_row(index)
        Returns the row at the specified index. Raises IndexError if the
        index is outside the valid nonnegative range.
    get_columns()
        Returns the group of column groups.
    get_rows()
        Returns the group of row groups.
    set_column_colors(*colors)
        Applies the supplied colors to columns in order and returns this
        Matrix. Extra colors or columns are ignored when their counts differ.
    add_background_to_entries()
        Adds a background rectangle to every entry returned by get_entries()
        and returns this Matrix.
    swap_entry_for_dots(entry, dots)
        Moves a dots mobject to an entry's position, replaces the entry's
        appearance using become(), removes it from elements if present, and
        records it in ellipses if not already recorded.
    swap_entries_for_ellipses(row_index=None, col_index=None,
                              height_ratio=0.65, width_ratio=0.4)
        Replaces entries in a valid selected row with vertical ellipses and/or
        entries in a valid selected column with horizontal ellipses. Returns
        this Matrix.
    get_mob_matrix()
        Returns the nested list of entry mobjects.
    get_entries()
        Returns a VGroup containing the entries currently listed in elements.
    get_brackets()
        Returns a VGroup containing the bracket components.
    get_ellipses()
        Returns a VGroup containing the entries visually replaced by ellipses.

    Notes
    -----
    - The matrix is laid out using a uniform step based on the maximum width
      and maximum height among all entries. Individual entries with different
      dimensions therefore do not receive independently calculated spacing.
    - The input is expected to be a nonempty, rectangular matrix. The
      implementation accesses the first row and computes maxima over all
      entries; empty matrices or empty rows are not supported reliably.
    - Existing VMobject entries are reused rather than copied. Constructing
      a Matrix can therefore reposition the supplied mobjects.
    - Only float and complex values are converted to DecimalNumber. Integers
      and other values are converted to Tex(str(element)).
    - ``height`` resizes the row group before bracket creation. It does not
      directly set the final height of the complete Matrix, and values too
      small for the bracket buffer may produce undesirable geometry.
    - Brackets are constructed using a Tex array expression, then split into
      left and right components. Their exact appearance depends on the
      available LaTeX environment and font configuration.
    - ``get_row()`` and ``get_column()`` reject negative indices, even though
      ``swap_entries_for_ellipses()`` accepts valid negative indices.
    - Replacing an entry with dots uses ``become()`` on the existing entry
      mobject. Its identity is retained, but its visible geometry is replaced.
      The nested ``mob_matrix``, row groups, and column groups continue to
      reference that mobject.
    - If both row and column ellipses are requested, their intersection entry
      is rotated by ``-45 * DEG`` after the replacements.
    - ``swap_entries_for_ellipses()`` calculates average row height and column
      width from the row and column groups. Degenerate matrices may lead to
      invalid dimensions or divisions.
    - The ``copy()`` override remaps only ``elements`` and ``ellipses`` using
      family membership. Other attributes are handled by the parent copy
      implementation.
    - ``element_config`` uses a mutable default dictionary in the constructor.
      Avoid mutating it in place to prevent shared-default side effects.

    Examples
    --------
    Create a matrix from numbers and strings::

        matrix = Matrix([
            [1, 2],
            [3, 4],
        ])

        self.add(matrix)

    Access a row or column::

        first_row = matrix.get_row(0)
        second_column = matrix.get_column(1)

    Color columns independently::

        matrix.set_column_colors(RED, BLUE)

    Add vertical and horizontal ellipses::

        matrix = Matrix(
            [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9],
            ],
            ellipses_row=1,
            ellipses_col=1,
        )

    Retrieve entries, brackets, and ellipses::

        entries = matrix.get_entries()
        brackets = matrix.get_brackets()
        ellipses = matrix.get_ellipses()

    See Also
    --------
    VMobject
    VGroup
    DecimalNumber
    Tex
    GenericMatrixType
    """

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
        self.elements = [elem for row in self.mob_matrix for elem in row]
        self.columns = VGroup(*(
            VGroup(*(row[i] for row in self.mob_matrix))
            for i in range(n_cols)
        ))
        self.rows = VGroup(*(VGroup(*row) for row in self.mob_matrix))
        if height is not None:
            self.rows.set_height(height - 2 * bracket_v_buff)
        self.brackets = self.create_brackets(self.rows, bracket_v_buff, bracket_h_buff)
        self.ellipses = []

        # Add elements and brackets
        self.add(*self.elements)
        self.add(*self.brackets)
        self.center()

        # Potentially add ellipses
        self.swap_entries_for_ellipses(
            ellipses_row,
            ellipses_col,
        )

        # Draw fills together
        self.draw_fills_together_if_disjoint()

    def copy(self, deep: bool = False):
        result = super().copy(deep)
        self_family = self.get_family()
        copy_family = result.get_family()
        for attr in ["elements", "ellipses"]:
            setattr(result, attr, [
                copy_family[self_family.index(mob)]
                for mob in getattr(self, attr)
            ])
        return result

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

    def create_brackets(self, rows, v_buff: float, h_buff: float) -> VGroup:
        brackets = Tex("".join((
            R"\left[\begin{array}{c}",
            *len(rows) * [R"\quad \\"],
            R"\end{array}\right]",
        )))
        brackets.set_height(rows.get_height() + v_buff)
        l_bracket = brackets[:len(brackets) // 2]
        r_bracket = brackets[len(brackets) // 2:]
        l_bracket.next_to(rows, LEFT, h_buff)
        r_bracket.next_to(rows, RIGHT, h_buff)
        return VGroup(l_bracket, r_bracket)

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

    def swap_entry_for_dots(self, entry, dots):
        dots.move_to(entry)
        entry.become(dots)
        if entry in self.elements:
            self.elements.remove(entry)
        if entry not in self.ellipses:
            self.ellipses.append(entry)

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

        if use_vdots:
            for column in cols:
                # Add vdots
                dots = Tex(R"\vdots")
                dots.set_height(vdots_height)
                self.swap_entry_for_dots(column[row_index], dots)
        if use_hdots:
            for row in rows:
                # Add hdots
                dots = Tex(R"\hdots")
                dots.set_width(hdots_width)
                self.swap_entry_for_dots(row[col_index], dots)
        if use_vdots and use_hdots:
            rows[row_index][col_index].rotate(-45 * DEG)
        return self

    def get_mob_matrix(self) -> VMobjectMatrixType:
        return self.mob_matrix

    def get_entries(self) -> VGroup:
        return VGroup(*self.elements)

    def get_brackets(self) -> VGroup:
        return VGroup(*self.brackets)

    def get_ellipses(self) -> VGroup:
        return VGroup(*self.ellipses)


class DecimalMatrix(Matrix):
    """
    A specialized Matrix that renders every entry as a DecimalNumber.

    DecimalMatrix extends Matrix to display numerical matrix entries with
    configurable decimal precision and formatting. Unlike the base Matrix,
    which converts entries according to their types, DecimalMatrix overrides
    element_to_mobject() so every entry is passed to DecimalNumber.

    Parameters
    ----------
    matrix : FloatMatrixType
        Two-dimensional iterable of floating-point values used to construct
        the matrix. The original input is stored in ``float_matrix``.
    num_decimal_places : int, default=2
        Number of decimal places displayed by each DecimalNumber, unless
        overridden through ``decimal_config``.
    decimal_config : dict, default={}
        Additional keyword arguments passed to each DecimalNumber. These
        arguments are combined with ``num_decimal_places``; if this dictionary
        contains a ``num_decimal_places`` key, its value overrides the
        explicit ``num_decimal_places`` argument.
    **config
        Additional keyword arguments forwarded to the parent Matrix
        constructor, such as spacing, bracket buffers, target height,
        alignment, and ellipsis indices.

    Attributes
    ----------
    float_matrix : FloatMatrixType
        Reference to the input matrix supplied during initialization.
    mob_matrix : VMobjectMatrixType
        Nested list of DecimalNumber mobjects created for the matrix entries.
    elements : list of VMobject
        Flat list of matrix entry mobjects, inherited from Matrix.
    rows : VGroup
        Group of matrix rows, inherited from Matrix.
    columns : VGroup
        Group of matrix columns, inherited from Matrix.
    brackets : VGroup
        Group containing the matrix's left and right brackets, inherited
        from Matrix.
    ellipses : list of VMobject
        Entry mobjects visually replaced by ellipses, inherited from Matrix.

    Methods
    -------
    element_to_mobject(element, **decimal_config)
        Constructs and returns a DecimalNumber for the supplied element using
        the provided decimal formatting configuration.

    Notes
    -----
    - All entries are passed to DecimalNumber, regardless of their original
      type. The input should therefore contain values supported by
      DecimalNumber.
    - The matrix layout, bracket construction, row and column access,
      coloring, copying, and ellipsis behavior are inherited from Matrix.
    - ``float_matrix`` stores the original input reference; it is not a
      defensive copy.
    - The ``decimal_config`` dictionary is expanded into a new dictionary
      together with ``num_decimal_places`` before being passed to Matrix.
      A ``num_decimal_places`` key inside ``decimal_config`` takes precedence
      over the separate argument.
    - The default ``decimal_config`` is a mutable dictionary. Avoid modifying
      it in place to prevent shared-default side effects.
    - The ``FloatMatrixType`` annotation indicates the expected input type,
      but runtime validation is not performed explicitly by this class.

    Examples
    --------
    Create a matrix with two decimal places::

        matrix = DecimalMatrix([
            [1.234, 5.678],
            [9.876, 2.345],
        ])

        self.add(matrix)

    Specify a different precision::

        matrix = DecimalMatrix(
            [
                [1.23456, 5.67891],
                [9.87654, 2.34567],
            ],
            num_decimal_places=3,
        )

    Pass additional DecimalNumber configuration::

        matrix = DecimalMatrix(
            [
                [1.25, 2.5],
                [3.75, 4.0],
            ],
            num_decimal_places=1,
            decimal_config={"include_sign": True},
        )

    See Also
    --------
    Matrix
    DecimalNumber
    FloatMatrixType
    """

    def __init__(
        self,
        matrix: FloatMatrixType,
        num_decimal_places: int = 2,
        decimal_config: dict = dict(),
        **config
    ):
        self.float_matrix = matrix
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
    """
    A specialized DecimalMatrix configured to display matrix entries as integers.

    IntegerMatrix inherits from DecimalMatrix and sets the default number of
    decimal places to zero. It retains DecimalMatrix's entry conversion and
    formatting behavior, along with Matrix's layout, brackets, row and column
    access, and other matrix operations.

    Parameters
    ----------
    matrix : FloatMatrixType
        Two-dimensional iterable of numerical values used to construct the
        matrix. The original input is stored in ``float_matrix`` by the parent
        DecimalMatrix constructor.
    num_decimal_places : int, default=0
        Number of decimal places displayed by each DecimalNumber. Although the
        default is zero, callers can explicitly request a different precision.
    decimal_config : dict, default={}
        Additional keyword arguments passed to DecimalNumber through
        DecimalMatrix. If this dictionary contains ``num_decimal_places``, that
        value overrides the separate ``num_decimal_places`` argument.
    **config
        Additional keyword arguments forwarded through DecimalMatrix to Matrix,
        including matrix spacing, bracket buffers, target height, alignment,
        and ellipsis options.

    Attributes
    ----------
    float_matrix : FloatMatrixType
        Reference to the original input matrix, inherited from DecimalMatrix.
    mob_matrix : VMobjectMatrixType
        Nested list of DecimalNumber mobjects representing the matrix entries.
    elements : list of VMobject
        Flat list of ordinary matrix entry mobjects, inherited from Matrix.
    rows : VGroup
        Group containing the matrix's rows.
    columns : VGroup
        Group containing the matrix's columns.
    brackets : VGroup
        Group containing the left and right matrix brackets.
    ellipses : list of VMobject
        Entry mobjects visually replaced by ellipsis symbols.

    Notes
    -----
    - IntegerMatrix does not convert entries to Python integers. It uses
      DecimalNumber with zero decimal places by default, so the displayed
      representation is integer-like while the underlying numerical values
      remain those supplied to DecimalNumber.
    - The caller can override ``num_decimal_places`` and display decimal places
      if desired; zero decimal places is a default, not an enforced restriction.
    - All entry formatting behavior is inherited from DecimalMatrix, and
      matrix layout and manipulation behavior are inherited from Matrix.
    - No explicit validation of the input matrix is performed in this class.
    - The ``decimal_config`` default is a mutable dictionary. Avoid modifying
      it in place to prevent shared-default side effects.

    Examples
    --------
    Create a matrix displayed with zero decimal places::

        matrix = IntegerMatrix([
            [1, 2],
            [3, 4],
        ])

        self.add(matrix)

    Display values rounded to two decimal places instead::

        matrix = IntegerMatrix(
            [
                [1.234, 5.678],
                [9.876, 2.345],
            ],
            num_decimal_places=2,
        )

    Pass additional formatting options::

        matrix = IntegerMatrix(
            [
                [1, 2],
                [3, 4],
            ],
            decimal_config={"include_sign": True},
        )

    See Also
    --------
    Matrix
    DecimalMatrix
    DecimalNumber
    """

    def __init__(
        self,
        matrix: FloatMatrixType,
        num_decimal_places: int = 0,
        decimal_config: dict = dict(),
        **config
    ):
        super().__init__(matrix, num_decimal_places, decimal_config, **config)


class TexMatrix(Matrix):
    """
    A specialized Matrix for rendering matrix entries as LaTeX expressions.

    TexMatrix extends Matrix by passing a shared configuration dictionary to
    the base class's element-construction process. Since Matrix converts
    non-VMobject, non-numeric entries to Tex, string entries are rendered as
    LaTeX expressions. Existing VMobjects are still reused, and float or
    complex entries are still converted to DecimalNumber by the inherited
    element_to_mobject() implementation.

    Parameters
    ----------
    matrix : StringMatrixType
        Two-dimensional iterable containing string expressions intended for
        LaTeX rendering.
    tex_config : dict, default={}
        Keyword arguments forwarded to Tex through Matrix's element-conversion
        process. Examples include text styling or other configuration accepted
        by Tex.
    **config
        Additional keyword arguments forwarded to the parent Matrix constructor,
        including spacing, bracket buffers, target height, element alignment,
        and ellipsis options.

    Attributes
    ----------
    mob_matrix : VMobjectMatrixType
        Nested list of entry mobjects created by Matrix.
    elements : list of VMobject
        Flat list of ordinary matrix entries.
    rows : VGroup
        Group containing the matrix's rows.
    columns : VGroup
        Group containing the matrix's columns.
    brackets : VGroup
        Group containing the left and right matrix brackets.
    ellipses : list of VMobject
        Entry mobjects visually replaced by ellipsis symbols.

    Methods
    -------
    All methods are inherited from Matrix, including row and column access,
    entry retrieval, column coloring, background rectangles, copying, and
    ellipsis replacement.

    Notes
    -----
    - TexMatrix does not override element_to_mobject(). Consequently, it does
      not force every entry to be a Tex object: existing VMobjects are returned
      unchanged, while float and complex values are converted to DecimalNumber.
      Other values are converted to Tex using their string representation.
    - ``tex_config`` is passed as ``element_config`` to Matrix. It affects
      entries constructed by Tex, but is not applied to existing VMobjects or
      DecimalNumber entries.
    - Matrix layout, bracket generation, and entry spacing are inherited from
      Matrix.
    - The input should be a nonempty, rectangular matrix supported by the
      parent Matrix implementation.
    - The ``tex_config`` default is a mutable dictionary. Avoid modifying it
      in place to prevent shared-default side effects.
    - LaTeX expressions must be supported by the active Tex compilation setup.

    Examples
    --------
    Create a matrix containing LaTeX expressions::

        matrix = TexMatrix([
            [r"x^2", r"y^2"],
            [r"\sin(\theta)", r"\cos(\theta)"],
        ])

        self.add(matrix)

    Configure the rendered entries::

        matrix = TexMatrix(
            [
                [r"\alpha", r"\beta"],
                [r"\gamma", r"\delta"],
            ],
            tex_config={"color": BLUE},
        )

    Customize the spacing using inherited Matrix parameters::

        matrix = TexMatrix(
            [
                [r"a", r"b"],
                [r"c", r"d"],
            ],
            h_buff=0.8,
            v_buff=0.6,
        )

    See Also
    --------
    Matrix
    DecimalMatrix
    IntegerMatrix
    Tex
    StringMatrixType
    """

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
    """
    Constructs a visual matrix from an existing group of mobjects.

    MobjectMatrix extends Matrix to arrange the elements of a VGroup into a
    rectangular grid. Instead of converting entries into text or numerical
    mobjects, it returns each supplied VMobject unchanged, preserving its
    existing geometry and styling.

    The number of rows and columns can be specified explicitly or inferred
    from the number of mobjects in the input group.

    Parameters
    ----------
    group : VGroup
        Group containing the mobjects to arrange into a matrix. The elements
        are read in their existing order, row by row.
    n_rows : int or None, default=None
        Number of rows in the resulting matrix. If omitted, it is inferred
        from the number of mobjects and ``n_cols``. If both dimensions are
        omitted, the integer square root of the number of mobjects is used.
    n_cols : int or None, default=None
        Number of columns in the resulting matrix. If omitted, it is inferred
        by integer division of the number of mobjects by ``n_rows``.
    height : float, default=4.0
        Target height passed to the parent Matrix constructor. The parent
        uses this value to resize its row group before creating brackets.
    element_alignment_corner : Vect3, default=ORIGIN
        Alignment corner used when positioning the mobjects in the matrix grid.
    **config
        Additional keyword arguments forwarded to Matrix, such as horizontal
        and vertical spacing, bracket buffers, and ellipsis indices.
        The ``height`` and ``element_alignment_corner`` values supplied
        explicitly to MobjectMatrix override corresponding entries in this
        dictionary.

    Attributes
    ----------
    mob_matrix : VMobjectMatrixType
        Nested list of the supplied mobjects arranged into rows and columns.
    elements : list of VMobject
        Flat list of the matrix entries, inherited from Matrix.
    rows : VGroup
        Group containing the row groups.
    columns : VGroup
        Group containing the column groups.
    brackets : VGroup
        Group containing the left and right matrix brackets.
    ellipses : list of VMobject
        Entry mobjects visually replaced by ellipsis symbols.

    Methods
    -------
    element_to_mobject(element, **config)
        Returns the supplied element unchanged. No conversion or additional
        configuration is applied to individual entries.

    Notes
    -----
    - The input group must contain at least ``n_rows * n_cols`` entries.
      Otherwise, the constructor raises an Exception.
    - If both dimensions are omitted, ``n_rows`` is estimated using
      ``int(np.sqrt(n_mobs))`` and ``n_cols`` is then inferred by integer
      division. This does not guarantee that all entries are used or that
      the resulting dimensions form a square matrix.
    - If only ``n_cols`` is supplied, ``n_rows`` is inferred using integer
      division. If only ``n_rows`` is supplied, ``n_cols`` is inferred
      similarly. Inferred dimensions may leave some input entries unused.
    - Explicit dimensions should be positive integers. Zero dimensions can
      cause division errors, and invalid or negative dimensions are not
      explicitly validated.
    - The constructor uses the first ``n_rows * n_cols`` elements of the
      input group in row-major order. Extra elements are not included in
      the resulting matrix.
    - The original mobjects are reused rather than copied. The parent Matrix
      constructor positions these objects, so their positions may change.
    - The ``height`` parameter is forwarded to Matrix. It controls the row
      group's target height before bracket creation rather than directly
      setting the final height of the complete matrix.
    - Matrix's inherited entry-conversion logic is bypassed because this
      class overrides element_to_mobject().
    - The input should be a VGroup whose elements are compatible with the
      VMobject operations used by Matrix.

    Examples
    --------
    Arrange four mobjects into a 2-by-2 matrix::

        group = VGroup(
            Circle(),
            Square(),
            Triangle(),
            Dot(),
        )

        matrix = MobjectMatrix(group, n_rows=2, n_cols=2)
        self.add(matrix)

    Specify only the number of columns::

        matrix = MobjectMatrix(
            group,
            n_cols=2,
        )

    Customize the matrix height and spacing::

        matrix = MobjectMatrix(
            group,
            n_rows=2,
            n_cols=2,
            height=3.0,
            h_buff=0.8,
            v_buff=0.6,
        )

    See Also
    --------
    Matrix
    VGroup
    VMobject
    """

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
