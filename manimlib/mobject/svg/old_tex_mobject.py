from __future__ import annotations

from functools import reduce
import operator as op
import re

from manimlib.constants import BLACK, DEFAULT_MOBJECT_COLOR
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.mobject.svg.tex_mobject import get_tex_mob_scale_factor
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.tex_file_writing import latex_to_svg

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, List, Dict
    from manimlib.typing import ManimColor


class SingleStringTex(SVGMobject):
    """
    A single LaTeX expression rendered as an SVG-based mobject.

    `SingleStringTex` is a subclass of `SVGMobject` that converts a LaTeX
    expression into SVG geometry and loads the resulting paths as a Manim mobject.
    It supports mathematical and text-mode rendering, custom LaTeX templates,
    SVG styling, expression preprocessing, and optional left-to-right organization
    of the generated submobjects.

    Unlike a class that splits a formula into separately addressable text
    components, `SingleStringTex` primarily represents the supplied expression
    as one rendered LaTeX object.

    Parameters
    ----------
    tex_string : str
        The LaTeX expression to render.

    height : float or None, default=None
        Desired height of the resulting SVG mobject. Passed to `SVGMobject`.
        If None, the object is scaled using `get_tex_mob_scale_factor()` multiplied
        by `font_size`.

    fill_color : ManimColor, default=DEFAULT_MOBJECT_COLOR
        Default fill color applied to the rendered SVG geometry.

    fill_opacity : float, default=1.0
        Opacity of the fill.

    stroke_width : float, default=0
        Width of the stroke used to render the SVG paths.

    svg_default : dict, default={"fill_color": DEFAULT_MOBJECT_COLOR}
        Default SVG styling configuration. A shallow copy is stored on the
        instance and included in its `hash_seed`.

    path_string_config : dict, default={}
        Configuration passed to `SVGMobject` for interpreting SVG path strings.
        A shallow copy is stored on the instance, while the original argument is
        passed to the superclass.

    font_size : int, default=48
        Font-size value used when calculating the default scale if `height` is
        None. The actual LaTeX font setup may also depend on the template.

    alignment : str, default=R"\\centering"
        LaTeX alignment command or prefix inserted before the processed expression
        in the generated TeX file body.

    math_mode : bool, default=True
        If True, wraps the processed expression in an `align*` environment.
        If False, the expression is not wrapped in that environment.

    organize_left_to_right : bool, default=False
        If True, sorts the generated submobjects by their x-coordinate after
        initialization, arranging them from left to right.

    template : str, default=""
        LaTeX template information passed to `latex_to_svg` when generating the
        SVG representation.

    additional_preamble : str, default=""
        Additional LaTeX preamble content passed to `latex_to_svg`.

    **kwargs
        Additional keyword arguments forwarded to `SVGMobject`.

    Attributes
    ----------
    height : float or None
        Class-level default for the desired height. The effective value depends
        on initialization and the behavior of `SVGMobject`.

    tex_string : str
        Original LaTeX expression supplied to the constructor.

    svg_default : dict
        Shallow copy of the SVG default styling configuration.

    path_string_config : dict
        Shallow copy of the SVG path configuration.

    font_size : int
        Font-size value used by the instance.

    alignment : str
        Alignment prefix used when constructing the TeX file body.

    math_mode : bool
        Controls whether the expression is wrapped in an `align*` environment.

    organize_left_to_right : bool
        Determines whether submobjects are sorted by horizontal position.

    template : str
        LaTeX template setting used during SVG generation.

    additional_preamble : str
        Extra LaTeX preamble content used during SVG generation.

    Methods
    -------
    hash_seed
        Property returning a tuple of class and expression configuration values
        used to identify the rendering configuration.

    get_svg_string_by_content(content)
        Converts the supplied LaTeX content into an SVG string using the configured
        template and additional preamble.

    get_tex_file_body(tex_string)
        Prepares the body of the TeX file by processing the expression, optionally
        wrapping it in `align*`, and prepending the alignment command.

    get_modified_expression(tex_string)
        Strips surrounding whitespace and delegates expression preprocessing to
        `modify_special_strings`.

    modify_special_strings(tex)
        Preprocesses special or incomplete LaTeX expressions to make them more
        suitable for rendering. It inserts filler groups for selected incomplete
        commands, handles empty input and leading line breaks, balances braces,
        adjusts mismatched `\\left` and `\\right` delimiters, and handles
        incomplete `array` environments.

    balance_braces(tex)
        Attempts to balance curly braces by inserting missing opening or closing
        braces while ignoring braces immediately preceded by a backslash.

    get_tex()
        Returns the original expression stored in `tex_string`.

    organize_submobjects_left_to_right()
        Sorts the object's submobjects by their x-coordinate and returns the object.

    Notes
    -----
    - SVG generation is performed through `latex_to_svg`, which receives the
      content, template, and additional preamble.
    - The `hash_seed` property includes the class name, SVG styling configuration,
      path configuration, original expression, alignment, math-mode setting,
      template, and additional preamble. It does not include every constructor
      parameter, such as `font_size` or `height`.
    - When `math_mode` is True, the processed expression is wrapped in an
      `align*` environment. The alignment prefix is included in either mode.
    - Expression preprocessing is intended to make certain incomplete or
      malformed fragments more renderable; it does not guarantee that arbitrary
      invalid LaTeX will compile successfully.
    - `balance_braces` is a simple character-based correction. It skips a brace
      when the immediately preceding character is a backslash; it is not a full
      LaTeX parser.
    - When the counts of recognized `\\left` and `\\right` delimiters differ,
      both commands are replaced with `\\big`.
    - If an `array` environment has only one of its matching `\\begin` or
      `\\end` markers, the processed expression is replaced with an empty string.
    - If `organize_left_to_right` is enabled, submobjects are sorted by their
      x-coordinate after the superclass initialization has completed.

    Examples
    --------
    Render a basic mathematical expression:

    >>> expression = SingleStringTex(r"x^2 + y^2 = z^2")
    >>> self.add(expression)

    Render an expression with a specified font size:

    >>> expression = SingleStringTex(
    ...     r"\\frac{a}{b}",
    ...     font_size=60,
    ... )
    >>> self.add(expression)

    Set a specific height:

    >>> expression = SingleStringTex(
    ...     r"\\int_0^1 x^2\\,dx",
    ...     height=2,
    ... )
    >>> self.add(expression)

    Use text mode instead of wrapping the expression in `align*`:

    >>> expression = SingleStringTex(
    ...     r"Hello, World!",
    ...     math_mode=False,
    ... )
    >>> self.add(expression)

    Organize generated submobjects from left to right:

    >>> expression = SingleStringTex(
    ...     r"a+b=c",
    ...     organize_left_to_right=True,
    ... )
    >>> self.add(expression)

    Inspect the original expression:

    >>> expression = SingleStringTex(r"e^{i\\pi}+1=0")
    >>> print(expression.get_tex())
    e^{i\\pi}+1=0

    See Also
    --------
    SVGMobject
    Tex
    TexText
    latex_to_svg
    get_tex_mob_scale_factor
    """

    height: float | None = None

    def __init__(
        self,
        tex_string: str,
        height: float | None = None,
        fill_color: ManimColor = DEFAULT_MOBJECT_COLOR,
        fill_opacity: float = 1.0,
        stroke_width: float = 0,
        svg_default: dict = dict(fill_color=DEFAULT_MOBJECT_COLOR),
        path_string_config: dict = dict(),
        font_size: int = 48,
        alignment: str = R"\centering",
        math_mode: bool = True,
        organize_left_to_right: bool = False,
        template: str = "",
        additional_preamble: str = "",
        **kwargs
    ):
        self.tex_string = tex_string
        self.svg_default = dict(svg_default)
        self.path_string_config = dict(path_string_config)
        self.font_size = font_size
        self.alignment = alignment
        self.math_mode = math_mode
        self.organize_left_to_right = organize_left_to_right
        self.template = template
        self.additional_preamble = additional_preamble

        super().__init__(
            height=height,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            path_string_config=path_string_config,
            **kwargs
        )

        if self.height is None:
            self.scale(get_tex_mob_scale_factor() * self.font_size)
        if self.organize_left_to_right:
            self.organize_submobjects_left_to_right()

    @property
    def hash_seed(self) -> tuple:
        return (
            self.__class__.__name__,
            self.svg_default,
            self.path_string_config,
            self.tex_string,
            self.alignment,
            self.math_mode,
            self.template,
            self.additional_preamble
        )

    def get_svg_string_by_content(self, content: str) -> str:
        return latex_to_svg(content, self.template, self.additional_preamble)

    def get_tex_file_body(self, tex_string: str) -> str:
        new_tex = self.get_modified_expression(tex_string)
        if self.math_mode:
            new_tex = "\\begin{align*}\n" + new_tex + "\n\\end{align*}"
        return self.alignment + "\n" + new_tex

    def get_modified_expression(self, tex_string: str) -> str:
        return self.modify_special_strings(tex_string.strip())

    def modify_special_strings(self, tex: str) -> str:
        tex = tex.strip()
        should_add_filler = reduce(op.or_, [
            # Fraction line needs something to be over
            tex == "\\over",
            tex == "\\overline",
            # Makesure sqrt has overbar
            tex == "\\sqrt",
            tex == "\\sqrt{",
            # Need to add blank subscript or superscript
            tex.endswith("_"),
            tex.endswith("^"),
            tex.endswith("dot"),
        ])
        if should_add_filler:
            filler = "{\\quad}"
            tex += filler

        should_add_double_filler = reduce(op.or_, [
            tex == "\\overset",
            # TODO: these can't be used since they change
            # the latex draw order.
            # tex == "\\frac", # you can use \\over as a alternative 
            # tex == "\\dfrac",
            # tex == "\\binom",
        ])
        if should_add_double_filler:
            filler = "{\\quad}{\\quad}"
            tex += filler

        if tex == "\\substack":
            tex = "\\quad"

        if tex == "":
            tex = "\\quad"

        # To keep files from starting with a line break
        if tex.startswith("\\\\"):
            tex = tex.replace("\\\\", "\\quad\\\\")

        tex = self.balance_braces(tex)

        # Handle imbalanced \left and \right
        num_lefts, num_rights = [
            len([
                s for s in tex.split(substr)[1:]
                if s and s[0] in "(){}[]|.\\"
            ])
            for substr in ("\\left", "\\right")
        ]
        if num_lefts != num_rights:
            tex = tex.replace("\\left", "\\big")
            tex = tex.replace("\\right", "\\big")

        for context in ["array"]:
            begin_in = ("\\begin{%s}" % context) in tex
            end_in = ("\\end{%s}" % context) in tex
            if begin_in ^ end_in:
                # Just turn this into a blank string,
                # which means caller should leave a
                # stray \\begin{...} with other symbols
                tex = ""
        return tex

    def balance_braces(self, tex: str) -> str:
        """
        Makes Tex resiliant to unmatched braces
        """
        num_unclosed_brackets = 0
        for i in range(len(tex)):
            if i > 0 and tex[i - 1] == "\\":
                # So as to not count '\{' type expressions
                continue
            char = tex[i]
            if char == "{":
                num_unclosed_brackets += 1
            elif char == "}":
                if num_unclosed_brackets == 0:
                    tex = "{" + tex
                else:
                    num_unclosed_brackets -= 1
        tex += num_unclosed_brackets * "}"
        return tex

    def get_tex(self) -> str:
        return self.tex_string

    def organize_submobjects_left_to_right(self):
        self.sort(lambda p: p[0])
        return self


class OldTex(SingleStringTex):
    """
    A LaTeX expression split into independently accessible and styleable parts.

    `OldTex` is a subclass of `SingleStringTex` that extends single-expression
    LaTeX rendering with substring-based grouping, part selection, coloring,
    indexing, slicing, and ordering operations.

    It accepts multiple LaTeX strings, optionally separates specified substrings
    into individual parts, joins the resulting pieces into one complete expression,
    and reorganizes the rendered SVG submobjects so that individual parts can be
    accessed and manipulated.

    Parameters
    ----------
    *tex_strings : str
        One or more LaTeX strings that form the complete expression. Each string
        can be split into smaller pieces according to `isolate` and
        `tex_to_color_map`.

    arg_separator : str, default=""
        String inserted between the processed pieces when constructing the full
        LaTeX expression.

    isolate : List[str], default=[]
        Substrings that should be separated into individual pieces during
        preprocessing. Isolated pieces can subsequently be selected and styled
        independently.

    tex_to_color_map : Dict[str, ManimColor], default={}
        Mapping from LaTeX substrings to colors. Each key is included in the
        isolation patterns, and the corresponding color is applied to matching
        parts after the expression has been broken into submobjects.

    **kwargs
        Additional keyword arguments forwarded to `SingleStringTex`, including
        rendering configuration such as `font_size`, `height`, `math_mode`,
        `alignment`, and SVG styling options.

    Attributes
    ----------
    tex_strings : Iterable[str]
        Processed pieces of the original LaTeX strings after applying substring
        isolation. These pieces are joined using `arg_separator` to construct
        the full expression.

    Methods
    -------
    break_up_tex_strings(tex_strings, substrings_to_isolate=[])
        Splits each input string around the specified substrings. Uses escaped
        regular-expression patterns to match the requested substrings literally,
        discards empty pieces, and returns the resulting pieces as a list.

    break_up_by_substrings(tex_strings)
        Reorganizes the existing submobjects into groups corresponding to the
        supplied LaTeX pieces. Each nonempty piece is represented by a
        `SingleStringTex` object containing the appropriate existing submobjects.

    get_parts_by_tex(tex, substring=True, case_sensitive=True)
        Returns a `VGroup` containing direct submobjects that are instances of
        `SingleStringTex` and whose stored LaTeX expression matches the requested
        text according to the selected matching options.

    get_part_by_tex(tex, **kwargs)
        Returns the first part matching the specified LaTeX text, or None if no
        matching part is found.

    set_color_by_tex(tex, color, **kwargs)
        Applies a color to every part returned by `get_parts_by_tex` and returns
        the current object.

    set_color_by_tex_to_color_map(tex_to_color_map, **kwargs)
        Applies the specified color to each substring in a mapping by calling
        `set_color_by_tex` for every mapping entry. Returns the current object.

    index_of_part(part, start=0)
        Returns the index of a specified direct submobject using the list
        `index` method, starting the search at the requested index.

    index_of_part_by_tex(tex, start=0, **kwargs)
        Finds a part by its LaTeX text and returns its index, optionally starting
        the index search at `start`.

    slice_by_tex(start_tex=None, stop_tex=None, **kwargs)
        Returns a slice of the direct submobjects beginning at the part matching
        `start_tex` and ending immediately before the part matching `stop_tex`.
        If `start_tex` is None, slicing begins at index zero. If `stop_tex` is
        None, slicing continues to the end.

    sort_alphabetically()
        Sorts the direct submobjects in place using each submobject's stored
        LaTeX expression, as returned by `get_tex`. Returns None.

    set_bstroke(color=BLACK, width=4)
        Applies a background stroke using the supplied color and width, then
        returns the current object.

    Notes
    -----
    - During initialization, the isolation patterns combine `isolate` entries
      with the keys of `tex_to_color_map`.
    - The strings are processed before being joined into `full_string`, which
      is passed to `SingleStringTex`.
    - After rendering, `break_up_by_substrings` reorganizes the existing
      submobjects into groups associated with the processed pieces.
    - When `break_up_by_substrings` receives exactly one piece, it copies the
      current object and sets that copy as the only submobject. Otherwise, it
      creates a `SingleStringTex` for each nonempty piece and assigns slices of
      the existing submobjects to those groups.
    - `get_parts_by_tex` searches only the direct submobjects of the current
      object. It does not recursively search all descendants.
    - With `substring=True`, a match occurs when the requested `tex` is contained
      in a part's stored expression. With `substring=False`, the expressions must
      be equal.
    - With `case_sensitive=False`, matching is performed after converting both
      strings to lowercase.
    - `index_of_part_by_tex` assumes that `get_part_by_tex` finds a matching part.
      If no part is found, passing the resulting None to `index_of_part` will
      raise an error.
    - `slice_by_tex` uses the index of the first matching part for each boundary.
      The stop boundary is exclusive, following normal Python slicing behavior.
    - `sort_alphabetically` changes the order of direct submobjects and does not
      regenerate the original LaTeX expression.
    - `set_bstroke` uses `set_stroke` with `background=True`, which creates a
      background stroke rather than an ordinary foreground outline.
    - The constructor uses mutable default arguments for `isolate` and
      `tex_to_color_map`. Avoid mutating these defaults directly; explicitly
      provide fresh lists and dictionaries when needed.

    Examples
    --------
    Create a basic expression:

    >>> equation = OldTex(r"x^2 + y^2 = z^2")
    >>> self.add(equation)

    Isolate selected substrings:

    >>> equation = OldTex(
    ...     r"x^2 + y^2 = z^2",
    ...     isolate=["x", "y", "z"],
    ... )
    >>> self.add(equation)

    Assign colors to selected LaTeX substrings:

    >>> equation = OldTex(
    ...     r"a + b = c",
    ...     tex_to_color_map={
    ...         "a": RED,
    ...         "b": GREEN,
    ...         "c": BLUE,
    ...     },
    ... )
    >>> self.add(equation)

    Retrieve every part containing a substring:

    >>> equation = OldTex(
    ...     r"x + x^2 + y",
    ...     isolate=["x", "y"],
    ... )
    >>> x_parts = equation.get_parts_by_tex("x")
    >>> self.add(x_parts)

    Retrieve the first matching part:

    >>> part = equation.get_part_by_tex("y")

    Color a selected substring:

    >>> equation.set_color_by_tex("x", YELLOW)

    Get the index of a part:

    >>> part = equation.get_part_by_tex("x")
    >>> index = equation.index_of_part(part)

    Slice the expression between two parts:

    >>> equation = OldTex(
    ...     r"a + b + c + d",
    ...     isolate=["a", "b", "c", "d"],
    ... )
    >>> middle_parts = equation.slice_by_tex("b", "d")
    >>> self.add(middle_parts)

    Apply a background stroke:

    >>> equation.set_bstroke(color=BLACK, width=4)

    See Also
    --------
    SingleStringTex
    SVGMobject
    VGroup
    Tex
    TexText
    """

    def __init__(
        self,
        *tex_strings: str,
        arg_separator: str = "",
        isolate: List[str] = [],
        tex_to_color_map: Dict[str, ManimColor] = {},
        **kwargs
    ):
        self.tex_strings = self.break_up_tex_strings(
            tex_strings,
            substrings_to_isolate=[*isolate, *tex_to_color_map.keys()]
        )
        full_string = arg_separator.join(self.tex_strings)

        super().__init__(full_string, **kwargs)
        self.break_up_by_substrings(self.tex_strings)
        self.set_color_by_tex_to_color_map(tex_to_color_map)

        if self.organize_left_to_right:
            self.organize_submobjects_left_to_right()

    def break_up_tex_strings(self, tex_strings: Iterable[str], substrings_to_isolate: List[str] = []) -> Iterable[str]:
        # Separate out any strings specified in the isolate
        # or tex_to_color_map lists.
        if len(substrings_to_isolate) == 0:
            return tex_strings
        patterns = (
            "({})".format(re.escape(ss))
            for ss in substrings_to_isolate
        )
        pattern = "|".join(patterns)
        pieces = []
        for s in tex_strings:
            if pattern:
                pieces.extend(re.split(pattern, s))
            else:
                pieces.append(s)
        return list(filter(lambda s: s, pieces))

    def break_up_by_substrings(self, tex_strings: Iterable[str]):
        """
        Reorganize existing submojects one layer
        deeper based on the structure of tex_strings (as a list
        of tex_strings)
        """
        if len(list(tex_strings)) == 1:
            submob = self.copy()
            self.set_submobjects([submob])
            return self
        new_submobjects = []
        curr_index = 0
        for tex_string in tex_strings:
            tex_string = tex_string.strip()
            if len(tex_string) == 0:
                continue
            sub_tex_mob = SingleStringTex(tex_string, math_mode=self.math_mode)
            num_submobs = len(sub_tex_mob)
            if num_submobs == 0:
                continue
            new_index = curr_index + num_submobs
            sub_tex_mob.set_submobjects(self.submobjects[curr_index:new_index])
            new_submobjects.append(sub_tex_mob)
            curr_index = new_index
        self.set_submobjects(new_submobjects)
        return self

    def get_parts_by_tex(
        self,
        tex: str,
        substring: bool = True,
        case_sensitive: bool = True
    ) -> VGroup:
        def test(tex1, tex2):
            if not case_sensitive:
                tex1 = tex1.lower()
                tex2 = tex2.lower()
            if substring:
                return tex1 in tex2
            else:
                return tex1 == tex2

        return VGroup(*filter(
            lambda m: isinstance(m, SingleStringTex) and test(tex, m.get_tex()),
            self.submobjects
        ))

    def get_part_by_tex(self, tex: str, **kwargs) -> SingleStringTex | None:
        all_parts = self.get_parts_by_tex(tex, **kwargs)
        return all_parts[0] if all_parts else None

    def set_color_by_tex(self, tex: str, color: ManimColor, **kwargs):
        self.get_parts_by_tex(tex, **kwargs).set_color(color)
        return self

    def set_color_by_tex_to_color_map(
        self,
        tex_to_color_map: dict[str, ManimColor],
        **kwargs
    ):
        for tex, color in list(tex_to_color_map.items()):
            self.set_color_by_tex(tex, color, **kwargs)
        return self

    def index_of_part(self, part: SingleStringTex, start: int = 0) -> int:
        return self.submobjects.index(part, start)

    def index_of_part_by_tex(self, tex: str, start: int = 0, **kwargs) -> int:
        part = self.get_part_by_tex(tex, **kwargs)
        return self.index_of_part(part, start)

    def slice_by_tex(
        self,
        start_tex: str | None = None,
        stop_tex: str | None = None,
        **kwargs
    ) -> VGroup:
        if start_tex is None:
            start_index = 0
        else:
            start_index = self.index_of_part_by_tex(start_tex, **kwargs)

        if stop_tex is None:
            return self[start_index:]
        else:
            stop_index = self.index_of_part_by_tex(stop_tex, start=start_index, **kwargs)
            return self[start_index:stop_index]

    def sort_alphabetically(self) -> None:
        self.submobjects.sort(key=lambda m: m.get_tex())

    def set_bstroke(self, color: ManimColor = BLACK, width: float = 4):
        self.set_stroke(color, width, background=True)
        return self


class OldTexText(OldTex):
    """
    A text-oriented variant of `OldTex` for rendering LaTeX expressions without
    mathematical mode enabled by default.

    `OldTexText` is a subclass of `OldTex` that preserves its substring isolation,
    part selection, coloring, indexing, and slicing functionality while providing
    a default configuration suited to text rendering.

    It forwards the supplied text strings and keyword arguments to `OldTex`,
    explicitly passing the selected `math_mode` and `arg_separator` values.

    Parameters
    ----------
    *tex_strings : str
        One or more LaTeX strings that form the expression to render. These are
        passed directly to the `OldTex` constructor.

    math_mode : bool, default=False
        Determines whether the expression is wrapped in an `align*` environment
        by the inherited `SingleStringTex` rendering logic. Defaults to False,
        unlike the default mathematical mode used by `SingleStringTex`.

    arg_separator : str, default=""
        String inserted between the processed text pieces when constructing the
        complete expression. The default is an empty string.

    **kwargs
        Additional keyword arguments forwarded to `OldTex`. These can include
        options for isolating substrings, mapping substrings to colors, setting
        font size, controlling SVG styling, and configuring LaTeX rendering.

    Notes
    -----
    - `OldTexText` does not implement its own rendering or substring-processing
      methods. It inherits these behaviors from `OldTex` and its parent classes.
    - The only constructor-specific defaults are `math_mode=False` and
      `arg_separator=""`.
    - Setting `math_mode=False` prevents the inherited rendering logic from
      automatically wrapping the processed expression in an `align*` environment.
      The expression is still processed using the configured alignment prefix.
    - Substring isolation and color mapping work through the inherited `OldTex`
      implementation.
    - An explicit `math_mode` argument overrides the default False value.
    - The class name indicates text-oriented usage, but the supplied strings must
      still be valid for the selected LaTeX template and rendering configuration.

    Examples
    --------
    Render a simple text expression:

    >>> text = OldTexText(r"Hello, World!")
    >>> self.add(text)

    Render multiple text pieces:

    >>> text = OldTexText("Hello, ", "Manim!")
    >>> self.add(text)

    Isolate and color selected substrings:

    >>> text = OldTexText(
    ...     r"Hello, World!",
    ...     isolate=["Hello", "World"],
    ...     tex_to_color_map={
    ...         "Hello": BLUE,
    ...         "World": YELLOW,
    ...     },
    ... )
    >>> self.add(text)

    Specify a separator between input strings:

    >>> text = OldTexText(
    ...     "First",
    ...     "Second",
    ...     arg_separator=" ",
    ... )
    >>> self.add(text)

    Enable mathematical mode explicitly:

    >>> text = OldTexText(
    ...     r"x^2 + y^2",
    ...     math_mode=True,
    ... )
    >>> self.add(text)

    See Also
    --------
    OldTex
    SingleStringTex
    TexText
    """

    def __init__(
        self,
        *tex_strings: str,
        math_mode: bool = False,
        arg_separator: str = "",
        **kwargs
    ):
        super().__init__(
            *tex_strings,
            math_mode=math_mode,
            arg_separator=arg_separator,
            **kwargs
        )
