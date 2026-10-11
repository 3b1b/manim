from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import re
import tempfile
from functools import lru_cache

import manimpango
import pygments
import pygments.formatters
import pygments.lexers

from manimlib.config import manim_config
from manimlib.constants import DEFAULT_PIXEL_WIDTH, FRAME_WIDTH
from manimlib.constants import NORMAL
from manimlib.logger import log
from manimlib.mobject.svg.string_mobject import StringMobject
from manimlib.mobject.svg.svg_mobject import get_svg_content_height
from manimlib.utils.cache import cache_on_disk
from manimlib.utils.color import color_to_hex
from manimlib.utils.color import int_to_hex
from manimlib.utils.simple_functions import hash_string

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable

    from manimlib.mobject.types.vectorized_mobject import VGroup
    from manimlib.typing import ManimColor, Span, Selector


DEFAULT_LINE_SPACING_SCALE = 0.6
# Ensure the canvas is large enough to hold all glyphs.
DEFAULT_CANVAS_WIDTH = 16384
DEFAULT_CANVAS_HEIGHT = 16384


# Temporary handler
class _Alignment:
    VAL_DICT = {
        "LEFT": 0,
        "CENTER": 1,
        "RIGHT": 2
    }

    def __init__(self, s: str):
        self.value = _Alignment.VAL_DICT[s.upper()]


@lru_cache(maxsize=128)
@cache_on_disk
def markup_to_svg(
    markup_str: str,
    justify: bool = False,
    indent: float = 0,
    alignment: str = "CENTER",
    line_width: float | None = None,
) -> str:
    validate_error = manimpango.MarkupUtils.validate(markup_str)
    if validate_error:
        raise ValueError(
            f"Invalid markup string \"{markup_str}\"\n" + \
            f"{validate_error}"
        )

    # `manimpango` is under construction,
    # so the following code is intended to suit its interface
    alignment = _Alignment(alignment)
    if line_width is None:
        pango_width = -1
    else:
        pango_width = line_width / FRAME_WIDTH * DEFAULT_PIXEL_WIDTH

    # Write the result to a temporary svg file, and return it's contents.
    temp_file = Path(tempfile.gettempdir(), hash_string(markup_str)).with_suffix(".svg")
    manimpango.MarkupUtils.text2svg(
        text=markup_str,
        font="",                     # Already handled
        slant="NORMAL",              # Already handled
        weight="NORMAL",             # Already handled
        size=1,                      # Already handled
        _=0,                         # Empty parameter
        disable_liga=False,
        file_name=str(temp_file),
        START_X=0,
        START_Y=0,
        width=DEFAULT_CANVAS_WIDTH,
        height=DEFAULT_CANVAS_HEIGHT,
        justify=justify,
        indent=indent,
        line_spacing=None,           # Already handled
        alignment=alignment,
        pango_width=pango_width
    )
    result = temp_file.read_text()
    os.remove(temp_file)
    return result


@lru_cache(maxsize=1)
def get_text_mob_scale_factor() -> float:
    # Render a reference "0" and calibrate so that font_size_for_unit_height
    # gives a height of 1 manim unit. Compensates for platform DPI differences.
    ref_size = 48
    font_size_for_unit_height = manim_config.text.font_size_for_unit_height
    pango_size = str(round(ref_size * 1024))
    svg_string = markup_to_svg(f'<span font_size="{pango_size}">0</span>')
    svg_height = get_svg_content_height(svg_string)
    return ref_size / (font_size_for_unit_height * svg_height)


class MarkupText(StringMobject):
    """
    Create a vector-based text object using Pango markup.

    `MarkupText` extends :class:`StringMobject` and renders styled text by converting
    Pango-compatible markup into SVG. Unlike `Tex`, which uses LaTeX, this class
    supports text formatting through markup tags and span attributes.

    It supports font families, font sizes, bold and italic styling, underlining,
    strikethrough, superscripts, subscripts, text alignment, justification, line
    spacing, and selector-based styling. The resulting SVG is converted into
    vector submobjects, allowing individual text portions to be selected, colored,
    and animated.

    Markup syntax and supported attributes are based on the Pango markup format:
    https://docs.gtk.org/Pango/pango_markup.html

    Class Attributes
    ----------------
    MARKUP_TAGS : dict[str, dict[str, str]]
        Maps supported shorthand markup tags to their corresponding Pango span
        attributes.

        Supported tags include:

        - ``b``: bold text.
        - ``big``: larger font size.
        - ``i``: italic text.
        - ``s``: strikethrough.
        - ``sub``: subscript positioning and scaling.
        - ``sup``: superscript positioning and scaling.
        - ``small``: smaller font size.
        - ``tt``: monospace font family.
        - ``u``: single underline.

    MARKUP_ENTITY_DICT : dict[str, str]
        Maps special characters to their markup entity representations.

        Supported mappings include:

        - ``<`` to ``&lt;``
        - ``>`` to ``&gt;``
        - ``&`` to ``&amp;``
        - ``"`` to ``&quot;``
        - ``'`` to ``&apos;``

    Parameters
    ----------
    text : str
        The text content to render. It may contain supported Pango markup tags,
        such as ``<b>bold</b>`` or ``<span foreground='red'>red text</span>``.

    font_size : int, default=48
        Font-size parameter used to construct the global Pango attributes. The
        value is multiplied by 1024 when converted into the markup ``font_size``
        attribute.

    height : float or None, default=None
        Optional height passed to the parent `StringMobject` constructor. When
        `None`, the resulting object is scaled using `get_text_mob_scale_factor()`.
        When explicitly supplied, this additional scaling step is skipped.

    justify : bool, default=False
        Whether to justify the rendered text. Forwarded to `markup_to_svg()`.

    indent : float, default=0
        Indentation setting forwarded to `markup_to_svg()`.

    alignment : str, default=""
        Text alignment configuration. If empty, the value is taken from
        `manim_config.text.alignment`.

    line_width : float or None, default=None
        Optional line-width constraint forwarded to `markup_to_svg()`. Its effect
        depends on the underlying markup-to-SVG implementation.

    font : str, default=""
        Font family used for the global text styling. If empty, the default font
        is taken from `manim_config.text.font`.

    slant : str, default=NORMAL
        Global font-style setting.

    weight : str, default=NORMAL
        Global font-weight setting.

    gradient : Iterable[ManimColor] or None, default=None
        Optional sequence of colors used to apply a gradient to the completed
        object through `set_color_by_gradient()`.

    line_spacing_height : float or None, default=None
        Line-spacing parameter. Takes precedence over `lsh` when truthy.
        The resolved value is stored in `self.lsh`.

    text2color : dict, default={}
        Mapping from text selectors to foreground colors. Takes precedence over
        `t2c` when nonempty.

    text2font : dict, default={}
        Mapping from text selectors to font-family values. Takes precedence over
        `t2f` when nonempty.

    text2gradient : dict, default={}
        Mapping from text selectors to gradient configurations. Stored through
        the `t2g` alias. The constructor warns that gradients supplied through
        this mapping cannot currently be parsed from SVG; use
        `set_color_by_gradient()` to apply gradients directly.

    text2slant : dict, default={}
        Mapping from text selectors to font-style values. Takes precedence over
        `t2s` when nonempty.

    text2weight : dict, default={}
        Mapping from text selectors to font-weight values. Takes precedence over
        `t2w` when nonempty.

    lsh : float or None, default=None
        Short alias for `line_spacing_height`. It is used only when
        `line_spacing_height` is falsy.

    t2c : dict, default={}
        Short alias for `text2color`. Used when `text2color` is falsy.

    t2f : dict, default={}
        Short alias for `text2font`. Used when `text2font` is falsy.

    t2g : dict, default={}
        Short alias for `text2gradient`. Used when `text2gradient` is falsy.

    t2s : dict, default={}
        Short alias for `text2slant`. Used when `text2slant` is falsy.

    t2w : dict, default={}
        Short alias for `text2weight`. Used when `text2weight` is falsy.

    global_config : dict, default={}
        Additional global Pango attributes. These are merged into the global
        attribute dictionary after the standard attributes have been constructed,
        allowing supplied entries to override the corresponding defaults.

    local_configs : dict, default={}
        Mapping from text selectors to dictionaries of local Pango attributes.
        Each matching span is configured using its associated attribute dictionary.

    disable_ligatures : bool, default=True
        Whether to disable common ligature features. When true, the generated
        global attributes include ``font_features="liga=0,dlig=0,clig=0,hlig=0"``.

    isolate : Selector, default=re.compile(r"\w+", re.U)
        Selectors used to isolate portions of the text for individual access.
        By default, word-like sequences are selected using a Unicode-aware regular
        expression.

    **kwargs
        Additional keyword arguments forwarded to `StringMobject`.

    Attributes
    ----------
    text : str
        Original text supplied to the constructor.

    content : str
        Markup content most recently passed to `get_svg_string_by_content()`.

    font_size : int
        Configured global font-size parameter.

    justify : bool
        Whether text justification is enabled.

    indent : float
        Text indentation setting.

    alignment : str
        Effective text alignment setting.

    line_width : float or None
        Optional text line-width constraint.

    font : str
        Effective global font family.

    slant : str
        Global font-style setting.

    weight : str
        Global font-weight setting.

    lsh : float or None
        Effective line-spacing configuration.

    t2c, t2f, t2g, t2s, t2w : dict
        Effective selector-based configuration mappings for color, font family,
        gradient, slant, and weight, respectively.

    global_config : dict
        Additional global Pango attributes.

    local_configs : dict
        Selector-specific local Pango attribute dictionaries.

    disable_ligatures : bool
        Whether ligatures are disabled.

    isolate : Selector
        Selectors used to isolate text portions.

    Methods
    -------
    get_svg_string_by_content(content)
        Store the supplied content in `self.content` and convert it into SVG by
        calling `markup_to_svg()` with the object's justification, indentation,
        alignment, and line-width settings.

    escape_markup_char(substr)
        Static method. Convert a special character to its markup entity
        representation if it appears in `MARKUP_ENTITY_DICT`. Return other
        substrings unchanged.

    unescape_markup_char(substr)
        Static method. Convert a recognized markup entity back to its corresponding
        character. Return unrecognized substrings unchanged.

    get_command_matches(string)
        Static method. Find markup tags, passthrough constructs, entities, and
        selected special characters using a compiled regular expression.

        Recognized patterns include opening and closing tags, self-closing tags,
        quoted tag attributes, processing instructions, comments, CDATA sections,
        document type declarations, markup entities, and selected individual
        characters.

        The method returns the list of regular-expression match objects.

    get_command_flag(match_obj)
        Static method. Return a flag describing the matched markup tag:

        - ``1`` for an opening tag that is not self-closing.
        - ``-1`` for a closing tag.
        - ``0`` for self-closing tags and non-tag matches.

    replace_for_content(match_obj)
        Static method. Remove markup tags from the content representation and
        escape selected special characters. Other matches, including entities and
        passthrough constructs, are returned unchanged.

    replace_for_matching(match_obj)
        Static method. Convert markup content into a representation suitable for
        text matching:

        - Remove markup tags and passthrough constructs.
        - Decode numeric character references in decimal or hexadecimal notation.
        - Decode recognized named entities using `MARKUP_ENTITY_DICT`.
        - Preserve other matched characters.

    get_attr_dict_from_command_pair(open_command, close_command)
        Static method. Extract the attributes associated with a markup tag.

        For a ``span`` opening tag, parse its quoted attributes into a dictionary
        mapping attribute names to values. For recognized shorthand tags, return
        the predefined attribute mapping from `MARKUP_TAGS`. Unknown tag names
        return an empty dictionary.

    get_configured_items()
        Return the configured text spans as `(span, attributes)` pairs.

        The method collects selector matches from the color, font-family, slant,
        and weight mappings, translating them to the corresponding Pango attributes:

        - ``t2c`` becomes ``foreground``.
        - ``t2f`` becomes ``font_family``.
        - ``t2s`` becomes ``font_style``.
        - ``t2w`` becomes ``font_weight``.

        It also includes spans matched by `local_configs`, preserving each
        selector's associated attribute dictionary.

    get_command_string(attr_dict, is_end, label_hex)
        Static method. Convert an attribute dictionary into a markup span string.

        If `is_end` is true, return a closing ``</span>`` tag.

        Otherwise, create an opening ``<span ...>`` tag. When `label_hex` is not
        `None`, set the foreground attribute to that label color and copy eligible
        attributes from `attr_dict`. Background and several decoration-color
        attributes are set to black in this case, while existing foreground-color
        attributes and color aliases are excluded from the copied attributes.

        When `label_hex` is `None`, copy the supplied attribute dictionary directly.
        Attribute values are serialized using single-quoted strings.

    get_content_prefix_and_suffix(is_labelled)
        Build the opening and closing markup strings that wrap the generated text.

        The global attributes include the object's base color, font family, font
        style, font weight, and font size. The font size is multiplied by 1024 and
        rounded to an integer string.

        The method checks the installed Pango version. For Pango versions earlier
        than 1.50, configured line spacing produces a warning because the
        ``line_height`` attribute is unsupported. For version 1.50 or later, the
        method calculates the line-height attribute from `lsh`, falling back to
        `DEFAULT_LINE_SPACING_SCALE` when `lsh` is falsy.

        If `disable_ligatures` is true, the global attributes also disable the
        configured ligature features. Finally, `global_config` is merged into the
        attribute dictionary, allowing custom attributes to override defaults.

        Return a tuple containing the generated opening and closing markup strings.
        Labelled content uses a black label color through `int_to_hex(0)`.

    get_parts_by_text(selector)
        Return a `VGroup` containing the text parts matching the supplied selector.
        This delegates to the inherited `select_parts()` method.

    get_part_by_text(selector, **kwargs)
        Return a selected text part using the inherited `select_part()` method.
        Additional keyword arguments are forwarded to that method.

    set_color_by_text(selector, color)
        Set the color of parts matching the supplied text selector by delegating
        to `set_parts_color()`.

    set_color_by_text_to_color_map(color_map)
        Apply a mapping from text selectors to colors through
        `set_parts_color_by_dict()`.

    get_text()
        Return the stored text representation through `get_string()`.

    Examples
    --------
    Create a basic text object:

    >>> from manimlib import *
    >>> text = MarkupText("Hello, World!")
    >>> self.add(text)

    Apply bold and italic markup:

    >>> text = MarkupText("<b>Bold</b> and <i>italic</i> text")
    >>> self.add(text)

    Use span attributes for foreground colors:

    >>> text = MarkupText(
    ...     "<span foreground='red'>Red</span> "
    ...     "<span foreground='blue'>Blue</span>"
    ... )
    >>> self.add(text)

    Configure text styling using selector mappings:

    >>> text = MarkupText(
    ...     "Make math easier to read",
    ...     t2c={"math": RED, "read": BLUE},
    ...     t2w={"easier": "bold"},
    ... )
    >>> self.add(text)

    Select and color a substring after construction:

    >>> text = MarkupText("Hello, Manim!")
    >>> text.set_color_by_text("Manim", YELLOW)
    >>> selected = text.get_parts_by_text("Hello")

    Apply a gradient to the complete object:

    >>> text = MarkupText("Gradient text")
    >>> text.set_color_by_gradient(RED, BLUE)
    >>> self.add(text)

    Notes
    -----
    - Markup is interpreted by Pango rather than by the LaTeX compiler.
    - Only the tags and attributes supported by the installed Pango version and
      the markup-to-SVG implementation can be expected to work.
    - Selector-based configuration depends on the matching and span-isolation
      behavior inherited from `StringMobject`.
    - `text2gradient` and `t2g` are stored as configuration mappings, but this
      implementation warns that gradients cannot currently be parsed from SVG.
      Apply gradients using `set_color_by_gradient()` instead.
    - The default isolation pattern selects Unicode word-like sequences.
    - The default `disable_ligatures=True` setting helps keep rendered text parts
      more individually addressable by disabling several ligature features.
    """

    # See https://docs.gtk.org/Pango/pango_markup.html
    MARKUP_TAGS = {
        "b": {"font_weight": "bold"},
        "big": {"font_size": "larger"},
        "i": {"font_style": "italic"},
        "s": {"strikethrough": "true"},
        "sub": {"baseline_shift": "subscript", "font_scale": "subscript"},
        "sup": {"baseline_shift": "superscript", "font_scale": "superscript"},
        "small": {"font_size": "smaller"},
        "tt": {"font_family": "monospace"},
        "u": {"underline": "single"},
    }
    MARKUP_ENTITY_DICT = {
        "<": "&lt;",
        ">": "&gt;",
        "&": "&amp;",
        "\"": "&quot;",
        "'": "&apos;"
    }

    def __init__(
        self,
        text: str,
        font_size: int = 48,
        height: float | None = None,
        justify: bool = False,
        indent: float = 0,
        alignment: str = "",
        line_width: float | None = None,
        font: str = "",
        slant: str = NORMAL,
        weight: str = NORMAL,
        gradient: Iterable[ManimColor] | None = None,
        line_spacing_height: float | None = None,
        text2color: dict = {},
        text2font: dict = {},
        text2gradient: dict = {},
        text2slant: dict = {},
        text2weight: dict = {},
        # For convenience, one can use shortened names
        lsh: float | None = None,  # Overrides line_spacing_height
        t2c: dict = {},  # Overrides text2color if nonempty
        t2f: dict = {},  # Overrides text2font if nonempty
        t2g: dict = {},  # Overrides text2gradient if nonempty
        t2s: dict = {},  # Overrides text2slant if nonempty
        t2w: dict = {},  # Overrides text2weight if nonempty
        global_config: dict = {},
        local_configs: dict = {},
        disable_ligatures: bool = True,
        isolate: Selector = re.compile(r"\w+", re.U),
        **kwargs
    ):
        text_config = manim_config.text
        self.text = text
        self.font_size = font_size
        self.justify = justify
        self.indent = indent
        self.alignment = alignment or text_config.alignment
        self.line_width = line_width
        self.font = font or text_config.font
        self.slant = slant
        self.weight = weight

        self.lsh = line_spacing_height or lsh
        self.t2c = text2color or t2c
        self.t2f = text2font or t2f
        self.t2g = text2gradient or t2g
        self.t2s = text2slant or t2s
        self.t2w = text2weight or t2w

        self.global_config = global_config
        self.local_configs = local_configs
        self.disable_ligatures = disable_ligatures
        self.isolate = isolate

        super().__init__(text, height=height, **kwargs)

        if self.t2g:
            log.warning("""
                Manim currently cannot parse gradient from svg.
                Please set gradient via `set_color_by_gradient`.
            """)
        if gradient:
            self.set_color_by_gradient(*gradient)
        if self.t2c:
            self.set_color_by_text_to_color_map(self.t2c)
        if height is None:
            self.scale(get_text_mob_scale_factor())

    def get_svg_string_by_content(self, content: str) -> str:
        self.content = content
        return markup_to_svg(
            content,
            justify=self.justify,
            indent=self.indent,
            alignment=self.alignment,
            line_width=self.line_width
        )

    # Toolkits

    @staticmethod
    def escape_markup_char(substr: str) -> str:
        return MarkupText.MARKUP_ENTITY_DICT.get(substr, substr)

    @staticmethod
    def unescape_markup_char(substr: str) -> str:
        return {
            v: k
            for k, v in MarkupText.MARKUP_ENTITY_DICT.items()
        }.get(substr, substr)

    # Parsing

    @staticmethod
    def get_command_matches(string: str) -> list[re.Match]:
        pattern = re.compile(r"""
            (?P<tag>
                <
                (?P<close_slash>/)?
                (?P<tag_name>\w+)\s*
                (?P<attr_list>(?:\w+\s*\=\s*(?P<quot>["']).*?(?P=quot)\s*)*)
                (?P<elision_slash>/)?
                >
            )
            |(?P<passthrough>
                <\?.*?\?>|<!--.*?-->|<!\[CDATA\[.*?\]\]>|<!DOCTYPE.*?>
            )
            |(?P<entity>&(?P<unicode>\#(?P<hex>x)?)?(?P<content>.*?);)
            |(?P<char>[>"'])
        """, flags=re.X | re.S)
        return list(pattern.finditer(string))

    @staticmethod
    def get_command_flag(match_obj: re.Match) -> int:
        if match_obj.group("tag"):
            if match_obj.group("close_slash"):
                return -1
            if not match_obj.group("elision_slash"):
                return 1
        return 0

    @staticmethod
    def replace_for_content(match_obj: re.Match) -> str:
        if match_obj.group("tag"):
            return ""
        if match_obj.group("char"):
            return MarkupText.escape_markup_char(match_obj.group("char"))
        return match_obj.group()

    @staticmethod
    def replace_for_matching(match_obj: re.Match) -> str:
        if match_obj.group("tag") or match_obj.group("passthrough"):
            return ""
        if match_obj.group("entity"):
            if match_obj.group("unicode"):
                base = 10
                if match_obj.group("hex"):
                    base = 16
                return chr(int(match_obj.group("content"), base))
            return MarkupText.unescape_markup_char(match_obj.group("entity"))
        return match_obj.group()

    @staticmethod
    def get_attr_dict_from_command_pair(
        open_command: re.Match, close_command: re.Match
    ) -> dict[str, str] | None:
        pattern = r"""
            (?P<attr_name>\w+)
            \s*\=\s*
            (?P<quot>["'])(?P<attr_val>.*?)(?P=quot)
        """
        tag_name = open_command.group("tag_name")
        if tag_name == "span":
            return {
                match_obj.group("attr_name"): match_obj.group("attr_val")
                for match_obj in re.finditer(
                    pattern, open_command.group("attr_list"), re.S | re.X
                )
            }
        return MarkupText.MARKUP_TAGS.get(tag_name, {})

    def get_configured_items(self) -> list[tuple[Span, dict[str, str]]]:
        return [
            *(
                (span, {key: val})
                for t2x_dict, key in (
                    (self.t2c, "foreground"),
                    (self.t2f, "font_family"),
                    (self.t2s, "font_style"),
                    (self.t2w, "font_weight")
                )
                for selector, val in t2x_dict.items()
                for span in self.find_spans_by_selector(selector)
            ),
            *(
                (span, local_config)
                for selector, local_config in self.local_configs.items()
                for span in self.find_spans_by_selector(selector)
            )
        ]

    @staticmethod
    def get_command_string(
        attr_dict: dict[str, str], is_end: bool, label_hex: str | None
    ) -> str:
        if is_end:
            return "</span>"

        if label_hex is not None:
            converted_attr_dict = {"foreground": label_hex}
            for key, val in attr_dict.items():
                if key in (
                    "background", "bgcolor",
                    "underline_color", "overline_color", "strikethrough_color"
                ):
                    converted_attr_dict[key] = "black"
                elif key not in ("foreground", "fgcolor", "color"):
                    converted_attr_dict[key] = val
        else:
            converted_attr_dict = attr_dict.copy()
        attrs_str = " ".join([
            f"{key}='{val}'"
            for key, val in converted_attr_dict.items()
        ])
        return f"<span {attrs_str}>"

    def get_content_prefix_and_suffix(
        self, is_labelled: bool
    ) -> tuple[str, str]:
        global_attr_dict = {
            "foreground": color_to_hex(self.base_color),
            "font_family": self.font,
            "font_style": self.slant,
            "font_weight": self.weight,
            "font_size": str(round(self.font_size * 1024)),
        }
        # `line_height` attribute is supported since Pango 1.50.
        pango_version = manimpango.pango_version()
        if tuple(map(int, pango_version.split("."))) < (1, 50):
            if self.lsh is not None:
                log.warning(
                    "Pango version %s found (< 1.50), "
                    "unable to set `line_height` attribute",
                    pango_version
                )
        else:
            line_spacing_scale = self.lsh or DEFAULT_LINE_SPACING_SCALE
            global_attr_dict["line_height"] = str(
                ((line_spacing_scale) + 1) * 0.6
            )
        if self.disable_ligatures:
            global_attr_dict["font_features"] = "liga=0,dlig=0,clig=0,hlig=0"

        global_attr_dict.update(self.global_config)
        return tuple(
            self.get_command_string(
                global_attr_dict,
                is_end=is_end,
                label_hex=int_to_hex(0) if is_labelled else None
            )
            for is_end in (False, True)
        )

    # Method alias

    def get_parts_by_text(self, selector: Selector) -> VGroup:
        return self.select_parts(selector)

    def get_part_by_text(self, selector: Selector, **kwargs) -> VGroup:
        return self.select_part(selector, **kwargs)

    def set_color_by_text(self, selector: Selector, color: ManimColor):
        return self.set_parts_color(selector, color)

    def set_color_by_text_to_color_map(
        self, color_map: dict[Selector, ManimColor]
    ):
        return self.set_parts_color_by_dict(color_map)

    def get_text(self) -> str:
        return self.get_string()


class Text(MarkupText):
    """
    Create a vector-based text object from plain text.

    `Text` is a subclass of :class:`MarkupText` that provides a simplified interface
    for rendering ordinary text while retaining the font configuration, text
    styling, substring selection, SVG conversion, and vector-mobject functionality
    of its parent class.

    Unlike `MarkupText`, which recognizes markup tags and entities as formatting
    instructions, `Text` overrides the parsing methods so that characters such as
    angle brackets, ampersands, and quotation marks are treated as literal text.
    These special characters are escaped when constructing markup content.

    The class also provides backward-compatible defaults for substring isolation
    and configures path-string processing to use a simple quadratic approximation.

    Parameters
    ----------
    text : str
        The plain text to render. Special markup characters are escaped during
        content processing so they can be displayed as text rather than interpreted
        as markup syntax.

    isolate : Selector, default=(re.compile(r"\w+", re.U), re.compile(r"\S+", re.U))
        Selectors used to isolate portions of the text for individual access.
        The default contains two Unicode-aware regular expressions:

        - ``\\w+`` matches sequences of word characters.
        - ``\\S+`` matches sequences of non-whitespace characters.

        Both selectors are provided for backward compatibility.

    use_labelled_svg : bool, default=True
        Whether to use labelled SVG output. Forwarded to `MarkupText` and its
        parent implementation.

    path_string_config : dict, default={"use_simple_quadratic_approx": True}
        Configuration dictionary for path-string processing. By default, simple
        quadratic approximation is enabled. Forwarded to the parent constructor
        through `kwargs`.

    **kwargs
        Additional keyword arguments forwarded to `MarkupText`. These can configure
        properties such as font size, font family, slant, weight, alignment,
        line spacing, gradients, and selector-based text styling.

    Inheritance
    -----------
    `Text` inherits the rendering and styling functionality of `MarkupText`,
    including:

    - Font configuration and text layout.
    - Conversion of text content into SVG.
    - Global and selector-specific text styling.
    - Text-part selection and coloring.
    - Gradient application.
    - Line-spacing and ligature configuration.

    The main distinction is its handling of special characters during parsing.

    Methods
    -------
    __init__(text, isolate=..., use_labelled_svg=True,
             path_string_config=..., **kwargs)
        Initialize the text object.

        Forward `text`, `isolate`, `use_labelled_svg`, and `path_string_config`
        to the `MarkupText` constructor. All additional keyword arguments are
        forwarded unchanged.

    get_command_matches(string)
        Static method. Find occurrences of the special characters ``<``, ``>``,
        ``&``, double quotation marks, and single quotation marks.

        Unlike the parent implementation, this method does not identify markup
        tags, entities, comments, or other markup constructs. It treats only
        the specified characters as special characters requiring processing.

        Return a list of regular-expression match objects.

    get_command_flag(match_obj)
        Static method. Return ``0`` for every match. No opening or closing markup
        tag structure is interpreted by this method.

    replace_for_content(match_obj)
        Static method. Escape the matched special character using
        `Text.escape_markup_char()`. This allows the character to be included
        safely in markup content while preserving its intended visible meaning.

    replace_for_matching(match_obj)
        Static method. Return the matched character unchanged. This ensures that
        special characters remain part of the text representation used for
        substring matching.

    Examples
    --------
    Create a basic text object:

    >>> from manimlib import *
    >>> text = Text("Hello, World!")
    >>> self.add(text)

    Configure font properties:

    >>> text = Text(
    ...     "Plain text",
    ...     font_size=48,
    ...     font="sans-serif",
    ...     weight="bold",
    ... )
    >>> self.add(text)

    Color selected words:

    >>> text = Text("Red text and blue text")
    >>> text.set_color_by_text("Red", RED)
    >>> text.set_color_by_text("blue", BLUE)

    Select individual text portions:

    >>> text = Text("Hello Manim")
    >>> words = text.get_parts_by_text("Hello")
    >>> word = text.get_part_by_text("Manim")

    Display characters that would otherwise be interpreted as markup:

    >>> text = Text("a < b & c > d")
    >>> self.add(text)

    Notes
    -----
    - `Text` is intended for ordinary text rather than markup-based formatting.
      Use `MarkupText` when you need inline tags such as ``<b>`` or ``<i>``.
    - Special characters are escaped during content processing, but remain
      unchanged during matching so selectors can refer to the original text.
    - The default isolation selectors preserve the behavior expected by older
      code that relies on both word-level and non-whitespace substring matching.
    - `path_string_config` enables simple quadratic approximation by default;
      its exact effect depends on the path-string processing implementation.
    """

    def __init__(
        self,
        text: str,
        # For backward compatibility
        isolate: Selector = (re.compile(r"\w+", re.U), re.compile(r"\S+", re.U)),
        use_labelled_svg: bool = True,
        path_string_config: dict = dict(
            use_simple_quadratic_approx=True,
        ),
        **kwargs
    ):
        super().__init__(
            text,
            isolate=isolate,
            use_labelled_svg=use_labelled_svg,
            path_string_config=path_string_config,
            **kwargs
        )

    @staticmethod
    def get_command_matches(string: str) -> list[re.Match]:
        pattern = re.compile(r"""[<>&"']""")
        return list(pattern.finditer(string))

    @staticmethod
    def get_command_flag(match_obj: re.Match) -> int:
        return 0

    @staticmethod
    def replace_for_content(match_obj: re.Match) -> str:
        return Text.escape_markup_char(match_obj.group())

    @staticmethod
    def replace_for_matching(match_obj: re.Match) -> str:
        return match_obj.group()


class Code(MarkupText):
    """
    Render syntax-highlighted source code as a vector-based text object.

    `Code` is a subclass of :class:`MarkupText` that uses Pygments to tokenize and
    highlight source code, converts the highlighted output into Pango-compatible
    markup, and renders it through ManimGL's text and SVG pipeline.

    It supports multiple programming languages and Pygments highlighting styles.
    The resulting code is rendered as a `MarkupText` object, allowing it to use
    the inherited text layout, styling, selection, and vector-mobject functionality.

    Parameters
    ----------
    code : str
        The source code to render. Pygments processes this string using the lexer
        selected by `language`, then applies syntax highlighting with the selected
        `code_style`.

    font : str, default="Consolas"
        Font family used to display the code. The default is a monospaced font
        commonly available on Windows. If the font is unavailable on the current
        system, the underlying text-rendering system may substitute another font.

    font_size : int, default=24
        Font-size parameter passed to `MarkupText`.

    lsh : float, default=1.0
        Line-spacing configuration passed to `MarkupText` through its `lsh`
        parameter. It controls the configured line-height behavior when supported
        by the installed Pango version.

    fill_color : ManimColor, default=None
        Fill color forwarded to `MarkupText` through `kwargs`. Its effect depends
        on the underlying mobject and SVG-rendering configuration.

    stroke_color : ManimColor, default=None
        Stroke color forwarded to `MarkupText` through `kwargs`. Its effect depends
        on the underlying mobject and SVG-rendering configuration.

    language : str, default="python"
        Programming-language name recognized by Pygments. It is passed to
        `pygments.lexers.get_lexer_by_name()` to select the appropriate lexer.
        Supported names depend on the installed Pygments version.

    code_style : str, default="monokai"
        Pygments highlighting style used to assign syntax colors and formatting.
        The style name must be recognized by the installed Pygments version.
        Visit https://pygments.org/demo/ to preview available styles.

    **kwargs
        Additional keyword arguments forwarded to `MarkupText`. These can configure
        properties such as alignment, indentation, line width, gradients,
        selector-based styling, and other supported text options.

    Initialization Process
    ----------------------
    1. Retrieve the Pygments lexer corresponding to `language`.
    2. Create a `PangoMarkupFormatter` configured with `code_style`.
    3. Highlight the source code using `pygments.highlight()`.
    4. Remove opening and closing ``tt`` tags from the generated markup.
    5. Pass the resulting markup to `MarkupText`, together with the font,
       font size, line-spacing configuration, stroke color, fill color, and
       additional keyword arguments.

    Removing the ``tt`` tags prevents the formatter's explicit monospace markup
    from overriding the `font` argument supplied to this class.

    Examples
    --------
    Render Python code with the default settings:

    >>> from manimlib import *
    >>> code = Code(
    ...     "def square(x):\\n    return x * x"
    ... )
    >>> self.add(code)

    Specify a different programming language:

    >>> code = Code(
    ...     "function square(x) { return x * x; }",
    ...     language="javascript",
    ... )
    >>> self.add(code)

    Change the highlighting style and font size:

    >>> code = Code(
    ...     "for i in range(5):\\n    print(i)",
    ...     language="python",
    ...     code_style="monokai",
    ...     font_size=28,
    ... )
    >>> self.add(code)

    Customize the font and line spacing:

    >>> code = Code(
    ...     "x = 10\\ny = x ** 2",
    ...     font="DejaVu Sans Mono",
    ...     font_size=24,
    ...     lsh=1.0,
    ... )
    >>> self.add(code)

    Notes
    -----
    - Pygments must be installed and available in the Python environment.
    - The selected language must be recognized by Pygments. An invalid lexer name
      can cause `get_lexer_by_name()` to raise an exception.
    - The selected style must be supported by the installed Pygments version.
    - The requested font should be installed on the system for predictable
      typography. Font availability varies across operating systems.
    - Syntax highlighting is generated by Pygments before the content reaches
      `MarkupText`; it is not performed by ManimGL itself.
    - The generated markup is rendered through the inherited Pango/SVG pipeline,
      so rendering behavior also depends on the installed text-rendering libraries.
    - The class does not add a background panel, line numbers, or a code-window
      frame. Those elements must be created separately if desired.
    """

    def __init__(
        self,
        code: str,
        font: str = "Consolas",
        font_size: int = 24,
        lsh: float = 1.0,
        fill_color: ManimColor = None,
        stroke_color: ManimColor = None,
        language: str = "python",
        # Visit https://pygments.org/demo/ to have a preview of more styles.
        code_style: str = "monokai",
        **kwargs
    ):
        lexer = pygments.lexers.get_lexer_by_name(language)
        formatter = pygments.formatters.PangoMarkupFormatter(
            style=code_style
        )
        markup = pygments.highlight(code, lexer, formatter)
        markup = re.sub(r"</?tt>", "", markup)
        super().__init__(
            markup,
            font=font,
            font_size=font_size,
            lsh=lsh,
            stroke_color=stroke_color,
            fill_color=fill_color,
            **kwargs
        )


@contextmanager
def register_font(font_file: str | Path):
    """Temporarily add a font file to Pango's search path.
    This searches for the font_file at various places. The order it searches it described below.
    1. Absolute path.
    2. Downloads dir.

    Parameters
    ----------
    font_file :
        The font file to add.
    Examples
    --------
    Use ``with register_font(...)`` to add a font file to search
    path.
    .. code-block:: python
        with register_font("path/to/font_file.ttf"):
           a = Text("Hello", font="Custom Font Name")
    Raises
    ------
    FileNotFoundError:
        If the font doesn't exists.
    AttributeError:
        If this method is used on macOS.
    Notes
    -----
    This method of adding font files also works with :class:`CairoText`.
    .. important ::
        This method is available for macOS for ``ManimPango>=v0.2.3``. Using this
        method with previous releases will raise an :class:`AttributeError` on macOS.
    """

    file_path = Path(font_file).resolve()
    if not file_path.exists():
        error = f"Can't find {font_file}."
        raise FileNotFoundError(error)
    try:
        assert manimpango.register_font(str(file_path))
        yield
    finally:
        manimpango.unregister_font(str(file_path))
