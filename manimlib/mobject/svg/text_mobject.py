import os
import re
import typing
import xml.sax.saxutils as saxutils
from contextlib import contextmanager
from pathlib import Path

import pygments
import pygments.formatters
import pygments.lexers
import manimpango
from manimpango import MarkupUtils

from manimlib.logger import log
from manimlib.constants import *
from manimlib.mobject.geometry import Dot
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.utils.customization import get_customization
from manimlib.utils.tex_file_writing import tex_hash
from manimlib.utils.config_ops import digest_config
from manimlib.utils.directories import get_downloads_dir
from manimlib.utils.directories import get_text_dir


TEXT_MOB_SCALE_FACTOR = 0.0076
DEFAULT_LINE_SPACING_SCALE = 0.6


class _TextParser(object):
    # See https://docs.gtk.org/Pango/pango_markup.html
    # A tag containing two aliases will cause warning,
    # so only use the first key of each group of aliases.
    SPAN_ATTR_KEY_ALIAS_LIST = (
        ("font", "font_desc"),
        ("font_family", "face"),
        ("font_size", "size"),
        ("font_style", "style"),
        ("font_weight", "weight"),
        ("font_variant", "variant"),
        ("font_stretch", "stretch"),
        ("font_features",),
        ("foreground", "fgcolor", "color"),
        ("background", "bgcolor"),
        ("alpha", "fgalpha"),
        ("background_alpha", "bgalpha"),
        ("underline",),
        ("underline_color",),
        ("overline",),
        ("overline_color",),
        ("rise",),
        ("baseline_shift",),
        ("font_scale",),
        ("strikethrough",),
        ("strikethrough_color",),
        ("fallback",),
        ("lang",),
        ("letter_spacing",),
        ("gravity",),
        ("gravity_hint",),
        ("show",),
        ("insert_hyphens",),
        ("allow_breaks",),
        ("line_height",),
        ("text_transform",),
        ("segment",),
    )
    SPAN_ATTR_KEY_CONVERSION = {
        key: key_alias_list[0]
        for key_alias_list in SPAN_ATTR_KEY_ALIAS_LIST
        for key in key_alias_list
    }

    TAG_TO_ATTR_DICT = {
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

    def __init__(self, text: str = "", is_markup: bool = True):
        self.text = text
        self.is_markup = is_markup
        self.global_attrs = {}
        self.local_attrs = {(0, len(self.text)): {}}
        self.tag_strings = set()
        if is_markup:
            self.parse_markup()

    def parse_markup(self) -> None:
        tag_pattern = r"""<(/?)(\w+)\s*((\w+\s*\=\s*('[^']*'|"[^"]*")\s*)*)>"""
        attr_pattern = r"""(\w+)\s*\=\s*(?:(?:'([^']*)')|(?:"([^"]*)"))"""
        start_match_obj_stack = []
        match_obj_pairs = []
        for match_obj in re.finditer(tag_pattern, self.text):
            if not match_obj.group(1):
                start_match_obj_stack.append(match_obj)
            else:
                match_obj_pairs.append((start_match_obj_stack.pop(), match_obj))
            self.tag_strings.add(match_obj.group())
        assert not start_match_obj_stack, "Unclosed tag(s) detected"

        for start_match_obj, end_match_obj in match_obj_pairs:
            tag_name = start_match_obj.group(2)
            assert tag_name == end_match_obj.group(2), "Unmatched tag names"
            assert not end_match_obj.group(3), "Attributes shan't exist in ending tags"
            if tag_name == "span":
                attr_dict = {
                    match.group(1): match.group(2) or match.group(3)
                    for match in re.finditer(attr_pattern, start_match_obj.group(3))
                }
            elif tag_name in _TextParser.TAG_TO_ATTR_DICT.keys():
                assert not start_match_obj.group(3), f"Attributes shan't exist in tag '{tag_name}'"
                attr_dict = _TextParser.TAG_TO_ATTR_DICT[tag_name]
            else:
                raise AssertionError(f"Unknown tag: '{tag_name}'")

            text_span = (start_match_obj.end(), end_match_obj.start())
            self.update_local_attrs(text_span, attr_dict)

    @staticmethod
    def convert_key_alias(key: str) -> str:
        return _TextParser.SPAN_ATTR_KEY_CONVERSION[key]

    @staticmethod
    def update_attr_dict(attr_dict: dict[str, str], key: str, value: typing.Any) -> None:
        converted_key = _TextParser.convert_key_alias(key)
        attr_dict[converted_key] = str(value)

    def update_global_attr(self, key: str, value: typing.Any) -> None:
        _TextParser.update_attr_dict(self.global_attrs, key, value)

    def update_global_attrs(self, attr_dict: dict[str, typing.Any]) -> None:
        for key, value in attr_dict.items():
            self.update_global_attr(key, value)

    def update_local_attr(self, span: tuple[int, int], key: str, value: typing.Any) -> None:
        if span[0] >= span[1]:
            log.warning(f"Span {span} doesn't match any part of the string")
            return

        if span in self.local_attrs.keys():
            _TextParser.update_attr_dict(self.local_attrs[span], key, value)
            return

        span_triplets = []
        for sp, attr_dict in self.local_attrs.items():
            if sp[1] <= span[0] or span[1] <= sp[0]:
                continue
            span_to_become = (max(sp[0], span[0]), min(sp[1], span[1]))
            spans_to_add = []
            if sp[0] < span[0]:
                spans_to_add.append((sp[0], span[0]))
            if span[1] < sp[1]:
                spans_to_add.append((span[1], sp[1]))
            span_triplets.append((sp, span_to_become, spans_to_add))
        for span_to_remove, span_to_become, spans_to_add in span_triplets:
            attr_dict = self.local_attrs.pop(span_to_remove)
            for span_to_add in spans_to_add:
                self.local_attrs[span_to_add] = attr_dict.copy()
            self.local_attrs[span_to_become] = attr_dict
            _TextParser.update_attr_dict(self.local_attrs[span_to_become], key, value)

    def update_local_attrs(self, text_span: tuple[int, int], attr_dict: dict[str, typing.Any]) -> None:
        for key, value in attr_dict.items():
            self.update_local_attr(text_span, key, value)

    def remove_tags(self, string: str) -> str:
        for tag_string in self.tag_strings:
            string = string.replace(tag_string, "")
        return string

    def get_text_pieces(self) -> list[tuple[str, dict[str, str]]]:
        result = []
        for span in sorted(self.local_attrs.keys()):
            text_piece = self.remove_tags(self.text[slice(*span)])
            if not text_piece:
                continue
            if not self.is_markup:
                text_piece = saxutils.escape(text_piece)
            attr_dict = self.global_attrs.copy()
            attr_dict.update(self.local_attrs[span])
            result.append((text_piece, attr_dict))
        return result

    def get_markup_str_with_attrs(self):
        return "".join([
            f"<span {_TextParser.get_attr_dict_str(attr_dict)}>{text_piece}</span>"
            for text_piece, attr_dict in self.get_text_pieces()
        ])

    @staticmethod
    def get_attr_dict_str(attr_dict: dict[str, str]):
        return " ".join([
            f"{key}='{value}'"
            for key, value in attr_dict.items()
        ])


# Temporary handler
class _Alignment:
    VAL_LIST = ["LEFT", "CENTER", "RIGHT"]
    def __init__(self, s):
        self.value = _Alignment.VAL_LIST.index(s.upper())


class Text(SVGMobject):
    CONFIG = {
        # Mobject
        "stroke_width": 0,
        "svg_default": {
            "color": WHITE,
        },
        "height": None,
        # Text
        "is_markup": False,
        "font_size": 48,
        "lsh": None,
        "justify": False,
        "indent": 0,
        "alignment": "LEFT",
        "line_width_factor": None,
        "font": "",
        "disable_ligatures": True,
        "apply_space_chars": True,
        "slant": NORMAL,
        "weight": NORMAL,
        "gradient": None,
        "t2c": {},
        "t2f": {},
        "t2g": {},
        "t2s": {},
        "t2w": {},
        "global_config": {},
        "local_configs": {},
    }

    def __init__(self, text, **kwargs):
        self.full2short(kwargs)
        digest_config(self, kwargs)
        validate_error = MarkupUtils.validate(text)
        if validate_error:
            raise ValueError(validate_error)
        self.text = text
        self.parser = _TextParser(text, is_markup=self.is_markup)
        super().__init__(**kwargs)

        if self.gradient:
            self.set_color_by_gradient(*self.gradient)
        if self.height is None:
            self.scale(TEXT_MOB_SCALE_FACTOR)

    @property
    def hash_seed(self):
        return (
            self.__class__.__name__,
            self.svg_default,
            self.path_string_config,
            self.text,
            self.is_markup,
            self.font_size,
            self.lsh,
            self.justify,
            self.indent,
            self.alignment,
            self.line_width_factor,
            self.font,
            self.disable_ligatures,
            self.apply_space_chars,
            self.slant,
            self.weight,
            self.t2c,
            self.t2f,
            self.t2s,
            self.t2w,
            self.global_config,
            self.local_configs
        )

    def get_file_path(self):
        full_markup = self.get_full_markup_str()
        svg_file = os.path.join(
            get_text_dir(), tex_hash(full_markup) + ".svg"
        )
        if not os.path.exists(svg_file):
            self.markup_to_svg(full_markup, svg_file)
        return svg_file

    def get_full_markup_str(self):
        if self.t2g:
            log.warning(
                "Manim currently cannot parse gradient from svg. "
                "Please set gradient via `set_color_by_gradient`.",
            )

        config_style_dict = self.generate_config_style_dict()
        global_attr_dict = {
            "line_height": ((self.lsh or DEFAULT_LINE_SPACING_SCALE) + 1) * 0.6,
            "font_family": self.font or get_customization()["style"]["font"],
            "font_size": self.font_size * 1024,
            "font_style": self.slant,
            "font_weight": self.weight,
            # TODO, it seems this doesn't work
            "font_features": "liga=0,dlig=0,clig=0,hlig=0" if self.disable_ligatures else None,
            "foreground": config_style_dict.get("fill", None),
            "alpha": config_style_dict.get("fill-opacity", None)
        }
        global_attr_dict = {
            k: v
            for k, v in global_attr_dict.items()
            if v is not None
        }
        global_attr_dict.update(self.global_config)
        self.parser.update_global_attrs(global_attr_dict)

        local_attr_items = [
            (word_or_text_span, {key: value})
            for t2x_dict, key in (
                (self.t2c, "foreground"),
                (self.t2f, "font_family"),
                (self.t2s, "font_style"),
                (self.t2w, "font_weight")
            )
            for word_or_text_span, value in t2x_dict.items()
        ]
        local_attr_items.extend(self.local_configs.items())
        for word_or_text_span, local_config in local_attr_items:
            for text_span in self.find_indexes(word_or_text_span):
                self.parser.update_local_attrs(text_span, local_config)

        return self.parser.get_markup_str_with_attrs()

    def find_indexes(self, word_or_text_span):
        if isinstance(word_or_text_span, tuple):
            return [word_or_text_span]

        return [
            match_obj.span()
            for match_obj in re.finditer(re.escape(word_or_text_span), self.text)
        ]

    def markup_to_svg(self, markup_str, file_name):
        # `manimpango` is under construction,
        # so the following code is intended to suit its interface
        alignment = _Alignment(self.alignment)
        if self.line_width_factor is None:
            pango_width = -1
        else:
            pango_width = self.line_width_factor * DEFAULT_PIXEL_WIDTH

        return MarkupUtils.text2svg(
            text=markup_str,
            font="",                     # Already handled
            slant="NORMAL",              # Already handled
            weight="NORMAL",             # Already handled
            size=1,                      # Already handled
            _=0,                         # Empty parameter
            disable_liga=False,          # Already handled
            file_name=file_name,
            START_X=0,
            START_Y=0,
            width=DEFAULT_PIXEL_WIDTH,
            height=DEFAULT_PIXEL_HEIGHT,
            justify=self.justify,
            indent=self.indent,
            line_spacing=None,           # Already handled
            alignment=alignment,
            pango_width=pango_width
        )

    def generate_mobject(self):
        super().generate_mobject()

        # Remove empty paths
        submobjects = list(filter(lambda submob: submob.has_points(), self))

        # Apply space characters
        if self.apply_space_chars:
            content_str = self.parser.remove_tags(self.text)
            if self.is_markup:
                content_str = saxutils.unescape(content_str)
            for char_index, char in enumerate(content_str):
                if not re.match(r"\s", char):
                    continue
                space = Dot(radius=0, fill_opacity=0, stroke_opacity=0)
                space.move_to(submobjects[max(char_index - 1, 0)].get_center())
                submobjects.insert(char_index, space)
        self.set_submobjects(submobjects)

    def full2short(self, config):
        conversion_dict = {
            "line_spacing_height": "lsh",
            "text2color": "t2c",
            "text2font": "t2f",
            "text2gradient": "t2g",
            "text2slant": "t2s",
            "text2weight": "t2w"
        }
        for kwargs in [config, self.CONFIG]:
            for long_name, short_name in conversion_dict.items():
                if long_name in kwargs:
                    kwargs[short_name] = kwargs.pop(long_name)

    def get_parts_by_text(self, word):
        if self.is_markup:
            log.warning(
                "Slicing MarkupText via `get_parts_by_text`, "
                "the result could be unexpected."
            )
        elif not self.apply_space_chars:
            log.warning(
                "Slicing Text without applying spaces via `get_parts_by_text`, "
                "the result could be unexpected."
            )
        return VGroup(*(
            self[i:j]
            for i, j in self.find_indexes(word)
        ))

    def get_part_by_text(self, word):
        parts = self.get_parts_by_text(word)
        if len(parts) > 0:
            return parts[0]


class MarkupText(Text):
    CONFIG = {
        "is_markup": True,
        "apply_space_chars": False,
    }


class Code(MarkupText):
    CONFIG = {
        "font": "Consolas",
        "font_size": 24,
        "lsh": 1.0,
        "language": "python",
        # Visit https://pygments.org/demo/ to have a preview of more styles.
        "code_style": "monokai",
    }

    def __init__(self, code, **kwargs):
        digest_config(self, kwargs)
        self.code = code
        lexer = pygments.lexers.get_lexer_by_name(self.language)
        formatter = pygments.formatters.PangoMarkupFormatter(style=self.code_style)
        markup = pygments.highlight(code, lexer, formatter)
        markup = markup.replace("<tt>", f"<span font_family='{self.font}'>")
        markup = markup.replace("</tt>", "</span>")
        super().__init__(markup, **kwargs)


@contextmanager
def register_font(font_file: typing.Union[str, Path]):
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

    input_folder = Path(get_downloads_dir()).parent.resolve()
    possible_paths = [
        Path(font_file),
        input_folder / font_file,
    ]
    for path in possible_paths:
        path = path.resolve()
        if path.exists():
            file_path = path
            break
    else:
        error = f"Can't find {font_file}." f"Tried these : {possible_paths}"
        raise FileNotFoundError(error)

    try:
        assert manimpango.register_font(str(file_path))
        yield
    finally:
        manimpango.unregister_font(str(file_path))
