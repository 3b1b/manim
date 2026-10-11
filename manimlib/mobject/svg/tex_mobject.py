from __future__ import annotations

import re
from pathlib import Path

from functools import lru_cache

from manimlib.config import manim_config
from manimlib.mobject.svg.string_mobject import StringMobject
from manimlib.mobject.svg.svg_mobject import get_svg_content_height
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.color import color_to_hex
from manimlib.utils.color import hex_to_int
from manimlib.utils.tex_file_writing import latex_to_svg
from manimlib.utils.tex import num_tex_symbols
from manimlib.logger import log

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.typing import ManimColor, Span, Selector, Self


@lru_cache(maxsize=1)
def get_tex_mob_scale_factor() -> float:
    # Render a reference "0" and calibrate so that font_size_for_unit_height
    # gives a height of 1 manim unit. Compensates for platform dvisvgm differences.
    font_size_for_unit_height = manim_config.tex.font_size_for_unit_height
    svg_string = latex_to_svg("0", show_message_during_execution=False)
    svg_height = get_svg_content_height(svg_string)
    return 1.0 / (font_size_for_unit_height * svg_height)


class Tex(StringMobject):
    """
    Create a vector-based mathematical text object by compiling LaTeX into SVG.

    `Tex` extends :class:`StringMobject` and provides LaTeX-specific functionality,
    including LaTeX compilation, command parsing, substring selection, color mapping,
    and conversion of selected numeric substrings into changeable decimal objects.

    The generated SVG is parsed into vector objects, allowing individual mathematical
    symbols, commands, and selected substrings to be accessed, colored, and animated
    using ManimGL's mobject functionality.

    Parameters
    ----------
    *tex_strings
        One or more strings containing LaTeX expressions. When multiple strings are
        supplied, they are joined with spaces to create a single LaTeX expression.
        Each original string is also added to the isolation selectors so its
        corresponding parts can be selected individually.

    font_size : int, default=48
        Font-size scaling parameter. The generated object is scaled using
        `get_tex_mob_scale_factor() * font_size`. The resulting value is stored in
        `self.font_size`.

    alignment : str, default=r"\\centering"
        LaTeX alignment command inserted before the expression inside the configured
        LaTeX environment. Pass an empty string to omit the alignment command.

    template : str, default=""
        Template configuration forwarded to `latex_to_svg()` for compiling the
        expression. Its exact interpretation depends on the LaTeX compilation
        implementation.

    additional_preamble : str, default=""
        Additional LaTeX preamble content forwarded to `latex_to_svg()`. This can
        be used to provide extra LaTeX definitions or packages supported by the
        compilation setup.

    tex_to_color_map : dict, default={}
        Mapping of LaTeX selectors to colors. Each matching substring is configured
        for coloring through the inherited substring-selection functionality.
        When both `t2c` and `tex_to_color_map` are provided, entries from
        `tex_to_color_map` take precedence for duplicate keys.

    t2c : dict, default={}
        Short alias for a LaTeX-selector-to-color mapping. Its entries are combined
        with `tex_to_color_map`.

    isolate : Selector, default=[]
        Selectors identifying substrings that should be isolated in the resulting
        object. If multiple `tex_strings` are provided, each of them is automatically
        added to the isolation selectors. A string, compiled regular expression, or
        tuple is wrapped in a list when necessary.

    use_labelled_svg : bool, default=True
        Determines whether the SVG-generation process uses labelled SVG output.
        Forwarded to the parent `StringMobject` implementation.

    **kwargs
        Additional configuration forwarded to `StringMobject`.

    Attributes
    ----------
    tex_environment : str
        LaTeX environment surrounding the expression. Defaults to `"align*"`.

    tex_string : str
        Combined LaTeX expression supplied to the object. Leading and trailing
        whitespace is removed. If the resulting expression is empty, it is replaced
        with a LaTeX line-break command.

    alignment : str
        Alignment command used when constructing the LaTeX content.

    template : str
        LaTeX template configuration used during SVG compilation.

    additional_preamble : str
        Additional LaTeX preamble content used during compilation.

    tex_to_color_map : dict
        Combined selector-to-color mapping used to configure the object's colors.

    font_size : int
        Font-size parameter stored after the initial scaling operation. Subsequent
        scaling operations update this value through `_handle_scale_side_effects()`.

    Methods
    -------
    get_svg_string_by_content(content)
        Compile the supplied LaTeX content into an SVG string using the configured
        template and additional preamble.

    _handle_scale_side_effects(scale_factor)
        Update `font_size` when the object is scaled, provided the attribute already
        exists. Return the object itself.

    get_command_matches(string)
        Parse LaTeX commands and groups of opening and closing braces into regular
        expression matches. Adjacent opening or closing braces are handled in groups.
        Raises `ValueError` if the braces are unbalanced.

    get_command_flag(match_obj)
        Return `1` for an opening-brace match, `-1` for a closing-brace match, and
        `0` for a LaTeX command or any other match handled by the parser.

    replace_for_content(match_obj)
        Return the matched text unchanged. Used when preserving the original content
        during processing.

    replace_for_matching(match_obj)
        Preserve LaTeX commands but remove brace matches. This provides a
        representation suitable for matching content while ignoring braces.

    get_attr_dict_from_command_pair(open_command, close_command)
        Return an empty dictionary when the opening command contains at least two
        characters, otherwise return `None`. This supports interpretation of paired
        brace commands during content processing.

    get_configured_items()
        Return a list of `(span, {})` pairs for every span matching every selector
        in `tex_to_color_map`. The spans are obtained through
        `find_spans_by_selector()`.

    get_color_command(rgb_hex)
        Convert a hexadecimal RGB color string into a LaTeX color command using
        the RGB color model.

    get_command_string(attr_dict, is_end, label_hex)
        Return an empty string if `label_hex` is `None`. Otherwise, return the
        closing brace sequence when `is_end` is true, or an opening group followed
        by a LaTeX color command when it is false.

    get_content_prefix_and_suffix(is_labelled)
        Build the prefix and suffix inserted around the LaTeX expression. For
        unlabelled content, the prefix includes the object's base color. If an
        alignment command is configured, it is included in the prefix. If
        `tex_environment` is nonempty, matching begin and end environment commands
        are included.

    get_parts_by_tex(selector)
        Return a `VGroup` containing parts selected by the supplied LaTeX selector.
        This is an alias for `select_parts()`.

    get_part_by_tex(selector, index=0)
        Return the selected part at the specified index. This is an alias for
        `select_part()`.

    set_color_by_tex(selector, color)
        Set the color of parts matching a LaTeX selector. This delegates to
        `set_parts_color()`.

    set_color_by_tex_to_color_map(color_map)
        Apply a mapping of LaTeX selectors to colors. This delegates to
        `set_parts_color_by_dict()`.

    get_tex()
        Return the stored expression through `get_string()`.

    substr_to_path_count(substr)
        Return the estimated number of LaTeX symbols in `substr`. If the total
        number of submobjects differs from the estimated symbol count of the full
        expression, log a warning.

    get_symbol_substrings()
        Extract symbol-like substrings from `self.string`. The pattern recognizes
        alphabetic LaTeX commands beginning with a backslash and most individual
        non-whitespace characters, excluding selected LaTeX syntax characters
        such as braces, underscores, carets, dollar signs, backslashes, and
        ampersands.

    make_number_changeable(value, index=0, replace_all=False, **config)
        Replace a selected numeric substring with a `DecimalNumber` mobject while
        preserving its position and visual style.

        Parameters
        ----------
        value : float, int, or str
            Numeric value represented in the LaTeX expression. Its string
            representation is used to locate matching parts.
        index : int, default=0
            Index of the matching occurrence to replace when `replace_all` is false.
        replace_all : bool, default=False
            If true, replace every matching occurrence and return a `VGroup`
            containing the generated decimal mobjects.
        **config
            Additional keyword arguments forwarded to `DecimalNumber`. If
            `num_decimal_places` is omitted, it is inferred from the number of
            digits after the decimal point in `str(value)`.

        If the requested substring cannot be found, or the requested occurrence
        does not exist, a warning is logged and an empty `VMobject` is returned.

        For each selected part, the method creates a `DecimalNumber`, positions it
        to replace the original part, copies its visual style, removes extra
        submobjects belonging to the selected part when necessary, and replaces
        the corresponding submobject with the decimal object.

        The stored string is also updated by replacing one occurrence of the
        numeric substring with `\\decimalmob`. This placeholder allows
        `substr_to_path_count()` to account for the replacement.

    Examples
    --------
    Create a basic mathematical expression:

    >>> from manimlib import *
    >>> expression = Tex(r"x^2 + y^2 = z^2")
    >>> self.add(expression)

    Create an expression from multiple strings. The supplied strings are
    automatically added to the isolation selectors:

    >>> expression = Tex(r"x^2", "+", r"y^2", "=", r"z^2")
    >>> self.add(expression)

    Color a selected LaTeX substring:

    >>> expression = Tex(r"x^2 + y^2 = z^2")
    >>> expression.set_color_by_tex("x", RED)
    >>> expression.set_color_by_tex("y", BLUE)

    Use the color-map shorthand:

    >>> expression = Tex(
    ...     r"x^2 + y^2 = z^2",
    ...     t2c={"x": RED, "y": BLUE, "z": GREEN},
    ... )

    Retrieve selected parts:

    >>> expression = Tex(r"x^2 + y^2 = z^2")
    >>> x_parts = expression.get_parts_by_tex("x")
    >>> x_part = expression.get_part_by_tex("x")

    Make a numeric substring changeable:

    >>> expression = Tex(r"x = 2.50")
    >>> number = expression.make_number_changeable("2.50")
    >>> self.add(expression)

    The returned decimal mobject can subsequently be animated or updated using
    the supported `DecimalNumber` interface.

    Replace every occurrence of a number:

    >>> expression = Tex(r"2 + 2 = 4")
    >>> numbers = expression.make_number_changeable(
    ...     2,
    ...     replace_all=True,
    ... )

    Notes
    -----
    - LaTeX must be valid for the configured compilation environment.
    - Substring selection depends on the isolation and matching behavior inherited
      from `StringMobject`.
    - A selector may match multiple spans. Use `get_parts_by_tex()` when all
      matches are required, or `get_part_by_tex()` to retrieve a specific match.
    - The `t2c` and `tex_to_color_map` dictionaries are merged with
      `tex_to_color_map` taking precedence when keys overlap.
    - The `font_size` attribute is assigned after the initial scale operation so
      the initial scaling does not modify the stored font-size parameter through
      `_handle_scale_side_effects()`.
    - When replacing numbers, the selected substring must correspond to a part
      that can be replaced within the existing submobject structure.
    """

    tex_environment: str = "align*"

    def __init__(
        self,
        *tex_strings: str,
        font_size: int = 48,
        alignment: str = R"\centering",
        template: str = "",
        additional_preamble: str = "",
        tex_to_color_map: dict = dict(),
        t2c: dict = dict(),
        isolate: Selector = [],
        use_labelled_svg: bool = True,
        **kwargs
    ):
        # Combine multi-string arg, but mark them to isolate
        if len(tex_strings) > 1:
            if isinstance(isolate, (str, re.Pattern, tuple)):
                isolate = [isolate]
            isolate = [*isolate, *tex_strings]

        tex_string = (" ".join(tex_strings)).strip()

        # Prevent from passing an empty string.
        if not tex_string.strip():
            tex_string = R"\\"

        self.tex_string = tex_string
        self.alignment = alignment
        self.template = template
        self.additional_preamble = additional_preamble
        self.tex_to_color_map = dict(**t2c, **tex_to_color_map)

        super().__init__(
            tex_string,
            use_labelled_svg=use_labelled_svg,
            isolate=isolate,
            **kwargs
        )

        self.set_color_by_tex_to_color_map(self.tex_to_color_map)
        self.scale(get_tex_mob_scale_factor() * font_size)

        self.font_size = font_size  # Important for this to go after the scale call

    def get_svg_string_by_content(self, content: str) -> str:
        return latex_to_svg(content, self.template, self.additional_preamble, short_tex=self.tex_string)

    def _handle_scale_side_effects(self, scale_factor: float) -> Self:
        if hasattr(self, "font_size"):
            self.font_size *= scale_factor
        return self

    # Parsing

    @staticmethod
    def get_command_matches(string: str) -> list[re.Match]:
        # Lump together adjacent brace pairs
        pattern = re.compile(r"""
            (?P<command>\\(?:[a-zA-Z]+|.))
            |(?P<open>{+)
            |(?P<close>}+)
        """, flags=re.X | re.S)
        result = []
        open_stack = []
        for match_obj in pattern.finditer(string):
            if match_obj.group("open"):
                open_stack.append((match_obj.span(), len(result)))
            elif match_obj.group("close"):
                close_start, close_end = match_obj.span()
                while True:
                    if not open_stack:
                        raise ValueError("Missing '{' inserted")
                    (open_start, open_end), index = open_stack.pop()
                    n = min(open_end - open_start, close_end - close_start)
                    result.insert(index, pattern.fullmatch(
                        string, pos=open_end - n, endpos=open_end
                    ))
                    result.append(pattern.fullmatch(
                        string, pos=close_start, endpos=close_start + n
                    ))
                    close_start += n
                    if close_start < close_end:
                        continue
                    open_end -= n
                    if open_start < open_end:
                        open_stack.append(((open_start, open_end), index))
                    break
            else:
                result.append(match_obj)
        if open_stack:
            raise ValueError("Missing '}' inserted")
        return result

    @staticmethod
    def get_command_flag(match_obj: re.Match) -> int:
        if match_obj.group("open"):
            return 1
        if match_obj.group("close"):
            return -1
        return 0

    @staticmethod
    def replace_for_content(match_obj: re.Match) -> str:
        return match_obj.group()

    @staticmethod
    def replace_for_matching(match_obj: re.Match) -> str:
        if match_obj.group("command"):
            return match_obj.group()
        return ""

    @staticmethod
    def get_attr_dict_from_command_pair(
        open_command: re.Match, close_command: re.Match
    ) -> dict[str, str] | None:
        if len(open_command.group()) >= 2:
            return {}
        return None

    def get_configured_items(self) -> list[tuple[Span, dict[str, str]]]:
        return [
            (span, {})
            for selector in self.tex_to_color_map
            for span in self.find_spans_by_selector(selector)
        ]

    @staticmethod
    def get_color_command(rgb_hex: str) -> str:
        rgb = hex_to_int(rgb_hex)
        rg, b = divmod(rgb, 256)
        r, g = divmod(rg, 256)
        return f"\\color[RGB]{{{r}, {g}, {b}}}"

    @staticmethod
    def get_command_string(
        attr_dict: dict[str, str], is_end: bool, label_hex: str | None
    ) -> str:
        if label_hex is None:
            return ""
        if is_end:
            return "}}"
        return "{{" + Tex.get_color_command(label_hex)

    def get_content_prefix_and_suffix(
        self, is_labelled: bool
    ) -> tuple[str, str]:
        prefix_lines = []
        suffix_lines = []
        if not is_labelled:
            prefix_lines.append(self.get_color_command(
                color_to_hex(self.base_color)
            ))
        if self.alignment:
            prefix_lines.append(self.alignment)
        if self.tex_environment:
            prefix_lines.append(f"\\begin{{{self.tex_environment}}}")
            suffix_lines.append(f"\\end{{{self.tex_environment}}}")
        return (
            "".join([line + "\n" for line in prefix_lines]),
            "".join(["\n" + line for line in suffix_lines])
        )

    # Method alias

    def get_parts_by_tex(self, selector: Selector) -> VGroup:
        return self.select_parts(selector)

    def get_part_by_tex(self, selector: Selector, index: int = 0) -> VMobject:
        return self.select_part(selector, index)

    def set_color_by_tex(self, selector: Selector, color: ManimColor):
        return self.set_parts_color(selector, color)

    def set_color_by_tex_to_color_map(
        self, color_map: dict[Selector, ManimColor]
    ):
        return self.set_parts_color_by_dict(color_map)

    def get_tex(self) -> str:
        return self.get_string()

    # Specific to Tex
    def substr_to_path_count(self, substr: str) -> int:
        tex = self.get_tex()
        if len(self) != num_tex_symbols(tex):
            log.warning(f"Estimated size of {tex} does not match true size")
        return num_tex_symbols(substr)

    def get_symbol_substrings(self):
        pattern = "|".join((
            # Tex commands
            r"\\[a-zA-Z]+",
            # And most single characters, with these exceptions
            r"[^\^\{\}\s\_\$\\\&]",
        ))
        return re.findall(pattern, self.string)

    def make_number_changeable(
        self,
        value: float | int | str,
        index: int = 0,
        replace_all: bool = False,
        **config,
    ) -> VMobject:
        substr = str(value)
        parts = self.select_parts(substr)
        if len(parts) == 0:
            log.warning(f"{value} not found in Tex.make_number_changeable call")
            return VMobject()
        if index > len(parts) - 1:
            log.warning(f"Requested {index}th occurance of {value}, but only {len(parts)} exist")
            return VMobject()
        if not replace_all:
            parts = [parts[index]]

        from manimlib.mobject.numbers import DecimalNumber

        decimal_mobs = []
        for part in parts:
            if "num_decimal_places" not in config:
                ndp = len(substr.split(".")[1]) if "." in substr else 0
                config["num_decimal_places"] = ndp
            decimal_mob = DecimalNumber(float(value), **config)
            decimal_mob.replace(part)
            decimal_mob.match_style(part)
            if len(part) > 1:
                self.remove(*part[1:])
            self.replace_submobject(self.submobjects.index(part[0]), decimal_mob)
            decimal_mobs.append(decimal_mob)

            # Replace substr with something that looks like a tex command. This
            # is to ensure Tex.substr_to_path_count counts it correctly.
            self.string = self.string.replace(substr, R"\decimalmob", 1)

        if replace_all:
            return VGroup(*decimal_mobs)
        return decimal_mobs[index]


class TexText(Tex):
    """
    Create a LaTeX-based text object using the `Tex` implementation without
    wrapping the content in a LaTeX environment by default.

    `TexText` is a lightweight subclass of :class:`Tex`. It inherits the LaTeX
    compilation, SVG conversion, substring selection, color mapping, scaling,
    and numeric replacement functionality provided by `Tex`.

    The main difference is that `TexText` sets `tex_environment` to an empty
    string. Consequently, the default content-generation process does not add
    a `\\begin{...}` and `\\end{...}` pair around the expression.

    This class is useful for rendering LaTeX text or expressions that should
    not be enclosed in the default `align*` environment used by `Tex`.

    Class Attributes
    ----------------
    tex_environment : str
        LaTeX environment surrounding the expression. Defaults to an empty
        string, disabling automatic environment wrapping in the inherited
        `get_content_prefix_and_suffix()` implementation.

    Parameters
    ----------
    *tex_strings
        One or more strings containing LaTeX content. Multiple strings are
        combined by the inherited `Tex` constructor.

    font_size : int, default=48
        Font-size scaling parameter inherited from `Tex`.

    alignment : str, default=r"\\centering"
        LaTeX alignment command inherited from `Tex`. Set to an empty string
        if no alignment command should be inserted.

    template : str, default=""
        LaTeX template configuration used during compilation.

    additional_preamble : str, default=""
        Additional LaTeX preamble content used during compilation.

    tex_to_color_map : dict, default={}
        Mapping of LaTeX selectors to colors.

    t2c : dict, default={}
        Short alias for the selector-to-color mapping.

    isolate : Selector, default=[]
        Selectors specifying substrings that should be isolated.

    use_labelled_svg : bool, default=True
        Whether to use labelled SVG output.

    **kwargs
        Additional keyword arguments forwarded through the inherited `Tex`
        constructor to `StringMobject`.

    Inherited Functionality
    -----------------------
    `TexText` inherits the methods of `Tex`, including:

    - `get_svg_string_by_content()` for compiling LaTeX content into SVG.
    - `get_parts_by_tex()` and `get_part_by_tex()` for selecting expression parts.
    - `set_color_by_tex()` and `set_color_by_tex_to_color_map()` for coloring
      selected substrings.
    - `get_tex()` for retrieving the stored LaTeX expression.
    - `make_number_changeable()` for replacing selected numeric parts with
      `DecimalNumber` mobjects.
    - LaTeX command parsing and symbol-substring extraction methods.

    Examples
    --------
    Create a text object:

    >>> from manimlib import *
    >>> text = TexText(r"Hello, World!")
    >>> self.add(text)

    Render mathematical text without the default `align*` environment:

    >>> expression = TexText(r"x^2 + y^2 = z^2")
    >>> self.add(expression)

    Color selected substrings:

    >>> expression = TexText(r"a + b = c", t2c={"a": RED, "b": BLUE, "c": GREEN})
    >>> self.add(expression)

    Notes
    -----
    - `TexText` changes only the default `tex_environment`; most of its behavior
      comes from `Tex` and its parent classes.
    - The inherited default alignment command remains `\\centering` unless
      overridden. An empty environment does not automatically disable alignment.
    - LaTeX content must still be valid for the configured compilation setup.
    """

    tex_environment: str = ""
