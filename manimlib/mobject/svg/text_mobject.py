from __future__ import annotations

import os
import re
import itertools as it
import xml.sax.saxutils as saxutils
from pathlib import Path
from contextlib import contextmanager
import typing
from typing import Iterable, Sequence, Union

import pygments
import pygments.formatters
import pygments.lexers

from manimpango import MarkupUtils

from manimlib.logger import log
from manimlib.constants import *
from manimlib.mobject.svg.mtex_mobject import LabelledString
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.customization import get_customization
from manimlib.utils.tex_file_writing import tex_hash
from manimlib.utils.config_ops import digest_config
from manimlib.utils.directories import get_downloads_dir
from manimlib.utils.directories import get_text_dir
from manimlib.utils.iterables import remove_list_redundancies


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.mobject.types.vectorized_mobject import VMobject
    ManimColor = Union[str, colour.Color, Sequence[float]]
    Span = tuple[int, int]

TEXT_MOB_SCALE_FACTOR = 0.0076
DEFAULT_LINE_SPACING_SCALE = 0.6


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
COLOR_RELATED_KEYS = (
    "foreground",
     "background",
     "underline_color",
     "overline_color",
     "strikethrough_color"
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


# Temporary handler
class _Alignment:
    VAL_DICT = {
        "LEFT": 0,
        "CENTER": 1,
        "RIGHT": 2
    }

    def __init__(self, s: str):
        self.value = _Alignment.VAL_DICT[s.upper()]


class MarkupText(LabelledString):
    CONFIG = {
        "is_markup": True,
        "font_size": 48,
        "lsh": None,
        "justify": False,
        "indent": 0,
        "alignment": "LEFT",
        "line_width_factor": None,
        "font": "",
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
        "isolate": [],
    }

    def __init__(self, text: str, **kwargs):
        self.full2short(kwargs)
        digest_config(self, kwargs)
        validate_error = MarkupUtils.validate(text)
        if validate_error:
            raise ValueError(validate_error)

        self.text = text
        super().__init__(text, **kwargs)

        if self.t2g:
            log.warning(
                "Manim currently cannot parse gradient from svg. "
                "Please set gradient via `set_color_by_gradient`.",
            )
        if self.gradient:
            self.set_color_by_gradient(*self.gradient)
        if self.height is None:
            self.scale(TEXT_MOB_SCALE_FACTOR)

    @property
    def hash_seed(self) -> tuple:
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
            self.slant,
            self.weight,
            self.t2c,
            self.t2f,
            self.t2s,
            self.t2w,
            self.global_config,
            self.local_configs,
            self.isolate
        )

    def full2short(self, config: dict) -> None:
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

    def get_file_path_by_content(self, content: str) -> str:
        svg_file = os.path.join(
            get_text_dir(), tex_hash(content) + ".svg"
        )
        if not os.path.exists(svg_file):
            self.markup_to_svg(content, svg_file)
        return svg_file

    def markup_to_svg(self, markup_str: str, file_name: str) -> str:
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
            disable_liga=False,
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

    # Toolkits

    @staticmethod
    def get_attr_dict_str(attr_dict: dict[str, str]) -> str:
        return " ".join([
            f"{key}='{value}'"
            for key, value in attr_dict.items()
        ])

    @staticmethod
    def get_begin_tag_str(attr_dict: dict[str, str]) -> str:
        return f"<span {MarkupText.get_attr_dict_str(attr_dict)}>"

    @staticmethod
    def get_end_tag_str() -> str:
        return "</span>"

    @staticmethod
    def convert_attr_key(key: str) -> str:
        return SPAN_ATTR_KEY_CONVERSION[key.lower()]

    @staticmethod
    def convert_attr_val(val: typing.Any) -> str:
        return str(val).lower()

    @staticmethod
    def merge_attr_items(
        attr_items: list[Span, str, str]
    ) -> list[tuple[Span, dict[str, str]]]:
        index_seq = [0]
        attr_dict_list = [{}]
        for span, key, value in attr_items:
            if span[0] >= span[1]:
                continue
            region_indices = [
                MarkupText.find_region_index(index, index_seq)
                for index in span
            ]
            for flag in (1, 0):
                if index_seq[region_indices[flag]] == span[flag]:
                    continue
                region_index = region_indices[flag]
                index_seq.insert(region_index + 1, span[flag])
                attr_dict_list.insert(
                    region_index + 1, attr_dict_list[region_index].copy()
                )
                region_indices[flag] += 1
                if flag == 0:
                    region_indices[1] += 1
            for attr_dict in attr_dict_list[slice(*region_indices)]:
                attr_dict[key] = value
        return list(zip(
            MarkupText.get_neighbouring_pairs(index_seq), attr_dict_list[:-1]
        ))

    # Parser

    @property
    def tag_items_from_markup(
        self
    ) -> list[tuple[Span, Span, dict[str, str]]]:
        if not self.is_markup:
            return []

        tag_pattern = r"""<(/?)(\w+)\s*((\w+\s*\=\s*('.*?'|".*?")\s*)*)>"""
        attr_pattern = r"""(\w+)\s*\=\s*(?:(?:'(.*?)')|(?:"(.*?)"))"""
        begin_match_obj_stack = []
        match_obj_pairs = []
        for match_obj in re.finditer(tag_pattern, self.string):
            if not match_obj.group(1):
                begin_match_obj_stack.append(match_obj)
            else:
                match_obj_pairs.append(
                    (begin_match_obj_stack.pop(), match_obj)
                )
        if begin_match_obj_stack:
            raise ValueError("Unclosed tag(s) detected")

        result = []
        for begin_match_obj, end_match_obj in match_obj_pairs:
            tag_name = begin_match_obj.group(2)
            if tag_name != end_match_obj.group(2):
                raise ValueError("Unmatched tag names")
            if end_match_obj.group(3):
                raise ValueError("Attributes shan't exist in ending tags")
            if tag_name == "span":
                attr_dict = dict([
                    (
                        MarkupText.convert_attr_key(match.group(1)),
                        MarkupText.convert_attr_val(
                            match.group(2) or match.group(3)
                        )
                    )
                    for match in re.finditer(
                        attr_pattern, begin_match_obj.group(3)
                    )
                ])
            elif tag_name in TAG_TO_ATTR_DICT.keys():
                if begin_match_obj.group(3):
                    raise ValueError(
                        f"Attributes shan't exist in tag '{tag_name}'"
                    )
                attr_dict = TAG_TO_ATTR_DICT[tag_name].copy()
            else:
                raise ValueError(f"Unknown tag: '{tag_name}'")

            result.append(
                (begin_match_obj.span(), end_match_obj.span(), attr_dict)
            )
        return result

    @property
    def global_attr_items_from_config(self) -> list[str, str]:
        global_attr_dict = {
            "line_height": (
                (self.lsh or DEFAULT_LINE_SPACING_SCALE) + 1
            ) * 0.6,
            "font_family": self.font or get_customization()["style"]["font"],
            "font_size": self.font_size * 1024,
            "font_style": self.slant,
            "font_weight": self.weight
        }
        global_attr_dict = {
            k: v
            for k, v in global_attr_dict.items()
            if v is not None
        }
        result = list(it.chain(
            global_attr_dict.items(),
            self.global_config.items()
        ))
        return [
            (
                self.convert_attr_key(key),
                self.convert_attr_val(val)
            )
            for key, val in result
        ]

    @property
    def local_attr_items_from_config(self) -> list[tuple[Span, str, str]]:
        result = [
            (text_span, key, val)
            for t2x_dict, key in (
                (self.t2c, "foreground"),
                (self.t2f, "font_family"),
                (self.t2s, "font_style"),
                (self.t2w, "font_weight")
            )
            for word_or_span, val in t2x_dict.items()
            for text_span in self.find_spans(word_or_span)
        ] + [
            (text_span, key, val)
            for word_or_span, local_config in self.local_configs.items()
            for text_span in self.find_spans(word_or_span)
            for key, val in local_config.items()
        ]
        return [
            (
                text_span,
                self.convert_attr_key(key),
                self.convert_attr_val(val)
            )
            for text_span, key, val in result
        ]

    def find_spans(self, word_or_span: str | Span) -> list[Span]:
        if isinstance(word_or_span, tuple):
            return [word_or_span]

        return [
            match_obj.span()
            for match_obj in re.finditer(re.escape(word_or_span), self.string)
        ]

    @property
    def skipped_spans(self) -> list[Span]:
        return [
            match_obj.span()
            for match_obj in re.finditer(r"\s+", self.string)
        ]

    @property
    def label_span_list(self) -> list[Span]:
        breakup_indices = [
            index
            for pattern in [
                r"\s+",
                r"\b",
                *[
                    re.escape(substr)
                    for substr in self.get_substrs_to_isolate(self.isolate)
                ]
            ]
            for match_obj in re.finditer(pattern, self.string)
            for index in match_obj.span()
        ]
        breakup_indices = sorted(filter(
            lambda index: not any([
                span[0] < index < span[1]
                for span, _ in self.command_repl_items
            ]),
            remove_list_redundancies([
                *self.full_span, *breakup_indices
            ])
        ))
        return list(filter(
            lambda span: self.string[slice(*span)].strip(),
            self.get_neighbouring_pairs(breakup_indices)
        ))

    @property
    def predefined_items(self) -> list[Span, str, str]:
        return list(it.chain(
            [
                (self.full_span, key, val)
                for key, val in self.global_attr_items_from_config
            ],
            sorted([
                ((begin_tag_span[0], end_tag_span[1]), key, val)
                for begin_tag_span, end_tag_span, attr_dict
                in self.tag_items_from_markup
                for key, val in attr_dict.items()
            ]),
            self.local_attr_items_from_config
        ))

    def get_inserted_string_pairs(
        self, use_label: bool
    ) -> list[tuple[Span, tuple[str, str]]]:
        attr_items = self.predefined_items
        if use_label:
            attr_items = [
                (span, key, WHITE if key in COLOR_RELATED_KEYS else val)
                for span, key, val in attr_items
            ] + [
                (span, "foreground", "#{:06x}".format(label))
                for label, span in enumerate(self.label_span_list)
            ]
        return [
            (span, (
                self.get_begin_tag_str(attr_dict),
                self.get_end_tag_str()
            ))
            for span, attr_dict in self.merge_attr_items(attr_items)
        ]

    @property
    def inserted_string_pairs(self) -> list[tuple[Span, tuple[str, str]]]:
        return self.get_inserted_string_pairs(use_label=True)

    @property
    def command_repl_items(self) -> list[tuple[Span, str]]:
        return [
            (tag_span, "")
            for begin_tag, end_tag, _ in self.tag_items_from_markup
            for tag_span in (begin_tag, end_tag)
        ]

    @property
    def has_predefined_colors(self) -> bool:
        return any([
            key in COLOR_RELATED_KEYS
            for _, key, _ in self.predefined_items
        ])

    @property
    def plain_string(self) -> str:
        return "".join([
            self.get_begin_tag_str({"foreground": self.base_color}),
            self.replace_str_by_spans(
                self.string, self.get_span_replacement_dict(
                    self.get_inserted_string_pairs(use_label=False),
                    self.command_repl_items
                )
            ),
            self.get_end_tag_str()
        ])

    def handle_submob_string(self, substr: str, string_span: Span) -> str:
        if self.is_markup:
            substr = saxutils.unescape(substr)
        return substr

    # Method alias

    def get_parts_by_text(self, substr: str) -> VGroup:
        return self.get_parts_by_string(substr)

    def get_part_by_text(self, substr: str, index: int = 0) -> VMobject:
        return self.get_part_by_string(substr, index)

    def set_color_by_text(self, substr: str, color: ManimColor):
        return self.set_color_by_string(substr, color)

    def set_color_by_text_to_color_map(
        self, text_to_color_map: dict[str, ManimColor]
    ):
        return self.set_color_by_string_to_color_map(text_to_color_map)

    def indices_of_part_by_text(
        self, substr: str, index: int = 0
    ) -> list[int]:
        return self.indices_of_part_by_string(substr, index)

    def get_text(self) -> str:
        return self.get_string()


class Text(MarkupText):
    CONFIG = {
        "is_markup": False,
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

    def __init__(self, code: str, **kwargs):
        digest_config(self, kwargs)
        self.code = code
        lexer = pygments.lexers.get_lexer_by_name(self.language)
        formatter = pygments.formatters.PangoMarkupFormatter(
            style=self.code_style
        )
        markup = pygments.highlight(code, lexer, formatter)
        markup = re.sub(r"</?tt>", "", markup)
        super().__init__(markup, **kwargs)


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
