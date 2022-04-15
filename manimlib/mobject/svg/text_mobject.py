from __future__ import annotations

from contextlib import contextmanager
import itertools as it
import os
from pathlib import Path
import re

from manimpango import MarkupUtils
import pygments
import pygments.formatters
import pygments.lexers

from manimlib.constants import BLACK
from manimlib.constants import DEFAULT_PIXEL_HEIGHT, DEFAULT_PIXEL_WIDTH
from manimlib.constants import NORMAL
from manimlib.logger import log
from manimlib.mobject.svg.labelled_string import LabelledString
from manimlib.utils.config_ops import digest_config
from manimlib.utils.customization import get_customization
from manimlib.utils.directories import get_downloads_dir
from manimlib.utils.directories import get_text_dir
from manimlib.utils.iterables import remove_list_redundancies
from manimlib.utils.tex_file_writing import tex_hash

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from colour import Color
    from typing import Union

    from manimlib.mobject.types.vectorized_mobject import VMobject
    from manimlib.mobject.types.vectorized_mobject import VGroup

    ManimColor = Union[str, Color]
    Span = tuple[int, int]


TEXT_MOB_SCALE_FACTOR = 0.0076
DEFAULT_LINE_SPACING_SCALE = 0.6


# See https://docs.gtk.org/Pango/pango_markup.html
# A tag containing two aliases will cause warning,
# so only use the first key of each group of aliases.
MARKUP_KEY_ALIAS_LIST = (
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
MARKUP_COLOR_KEYS = (
    "foreground",
    "background",
    "underline_color",
    "overline_color",
    "strikethrough_color"
)
MARKUP_TAG_CONVERSION_DICT = {
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
    }

    def __init__(self, text: str, **kwargs):
        self.full2short(kwargs)
        digest_config(self, kwargs)

        if not self.font:
            self.font = get_customization()["style"]["font"]
        if self.is_markup:
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
            self.base_color,
            self.isolate,
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
            self.local_configs
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

    def pre_parse(self) -> None:
        super().pre_parse()
        self.tag_items_from_markup = self.get_tag_items_from_markup()
        self.global_dict_from_config = self.get_global_dict_from_config()
        self.local_dicts_from_markup = self.get_local_dicts_from_markup()
        self.local_dicts_from_config = self.get_local_dicts_from_config()
        self.predefined_attr_dicts = self.get_predefined_attr_dicts()

    # Toolkits

    @staticmethod
    def get_attr_dict_str(attr_dict: dict[str, str]) -> str:
        return " ".join([
            f"{key}='{val}'"
            for key, val in attr_dict.items()
        ])

    @staticmethod
    def merge_attr_dicts(
        attr_dict_items: list[tuple[Span, dict[str, str]]]
    ) -> list[tuple[Span, dict[str, str]]]:
        index_seq = [0]
        attr_dict_list = [{}]
        for span, attr_dict in attr_dict_items:
            if span[0] >= span[1]:
                continue
            region_indices = [
                MarkupText.find_region_index(index_seq, index)
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
            for key, val in attr_dict.items():
                if not key:
                    continue
                for mid_dict in attr_dict_list[slice(*region_indices)]:
                    mid_dict[key] = val
        return list(zip(
            MarkupText.get_neighbouring_pairs(index_seq), attr_dict_list[:-1]
        ))

    def find_substr_or_span(
        self, substr_or_span: str | tuple[int | None, int | None]
    ) -> list[Span]:
        if isinstance(substr_or_span, str):
            return self.find_substr(substr_or_span)

        span = tuple([
            (
                min(index, self.string_len)
                if index >= 0
                else max(index + self.string_len, 0)
            )
            if index is not None else default_index
            for index, default_index in zip(substr_or_span, self.full_span)
        ])
        if span[0] >= span[1]:
            return []
        return [span]

    # Pre-parsing

    def get_tag_items_from_markup(
        self
    ) -> list[tuple[Span, Span, dict[str, str]]]:
        if not self.is_markup:
            return []

        tag_pattern = r"""<(/?)(\w+)\s*((?:\w+\s*\=\s*(['"]).*?\4\s*)*)>"""
        attr_pattern = r"""(\w+)\s*\=\s*(['"])(.*?)\2"""
        begin_match_obj_stack = []
        match_obj_pairs = []
        for match_obj in self.finditer(tag_pattern):
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
                attr_dict = {
                    match.group(1): match.group(3)
                    for match in re.finditer(
                        attr_pattern, begin_match_obj.group(3)
                    )
                }
            elif tag_name in MARKUP_TAG_CONVERSION_DICT.keys():
                if begin_match_obj.group(3):
                    raise ValueError(
                        f"Attributes shan't exist in tag '{tag_name}'"
                    )
                attr_dict = MARKUP_TAG_CONVERSION_DICT[tag_name].copy()
            else:
                raise ValueError(f"Unknown tag: '{tag_name}'")

            result.append(
                (begin_match_obj.span(), end_match_obj.span(), attr_dict)
            )
        return result

    def get_global_dict_from_config(self) -> dict[str, str]:
        result = {
            "line_height": str((
                (self.lsh or DEFAULT_LINE_SPACING_SCALE) + 1
            ) * 0.6),
            "font_family": self.font,
            "font_size": str(self.font_size * 1024),
            "font_style": self.slant,
            "font_weight": self.weight
        }
        result.update(self.global_config)
        return result

    def get_local_dicts_from_markup(
        self
    ) -> list[Span, dict[str, str]]:
        return sorted([
            ((begin_tag_span[0], end_tag_span[1]), attr_dict)
            for begin_tag_span, end_tag_span, attr_dict
            in self.tag_items_from_markup
        ])

    def get_local_dicts_from_config(
        self
    ) -> list[Span, dict[str, str]]:
        return [
            (span, {key: val})
            for t2x_dict, key in (
                (self.t2c, "foreground"),
                (self.t2f, "font_family"),
                (self.t2s, "font_style"),
                (self.t2w, "font_weight")
            )
            for substr_or_span, val in t2x_dict.items()
            for span in self.find_substr_or_span(substr_or_span)
        ] + [
            (span, local_config)
            for substr_or_span, local_config in self.local_configs.items()
            for span in self.find_substr_or_span(substr_or_span)
        ]

    def get_predefined_attr_dicts(self) -> list[Span, dict[str, str]]:
        attr_dict_items = [
            (self.full_span, self.global_dict_from_config),
            *self.local_dicts_from_markup,
            *self.local_dicts_from_config
        ]
        key_conversion_dict = {
            key: key_alias_list[0]
            for key_alias_list in MARKUP_KEY_ALIAS_LIST
            for key in key_alias_list
        }
        return [
            (span, {
                key_conversion_dict[key.lower()]: val
                for key, val in attr_dict.items()
            })
            for span, attr_dict in attr_dict_items
        ]

    # Parsing

    def get_command_repl_items(self) -> list[tuple[Span, str]]:
        result = [
            (tag_span, "")
            for begin_tag, end_tag, _ in self.tag_items_from_markup
            for tag_span in (begin_tag, end_tag)
        ]
        if not self.is_markup:
            result += [
                (span, escaped)
                for char, escaped in (
                    ("&", "&amp;"),
                    (">", "&gt;"),
                    ("<", "&lt;")
                )
                for span in self.find_substr(char)
            ]
        return result

    def get_extra_entity_spans(self) -> list[Span]:
        if not self.is_markup:
            return []
        return self.find_spans(r"&.*?;")

    def get_extra_ignored_spans(self) -> list[int]:
        return []

    def get_internal_specified_spans(self) -> list[Span]:
        return []

    def get_external_specified_spans(self) -> list[Span]:
        return [span for span, _ in self.local_dicts_from_config]

    def get_label_span_list(self) -> list[Span]:
        breakup_indices = remove_list_redundancies(list(it.chain(*it.chain(
            self.find_spans(r"\s+"),
            self.find_spans(r"\b"),
            self.specified_spans
        ))))
        breakup_indices = sorted(filter(
            self.is_splittable_index, breakup_indices
        ))
        return list(filter(
            lambda span: self.get_substr(span).strip(),
            self.get_neighbouring_pairs(breakup_indices)
        ))

    def get_content(self, use_plain_file: bool) -> str:
        filtered_attr_dicts = list(filter(
            lambda item: all([
                self.is_splittable_index(index)
                for index in item[0]
            ]),
            self.predefined_attr_dicts
        ))
        if use_plain_file:
            attr_dict_items = [
                (self.full_span, {
                    "foreground": self.int_to_hex(self.base_color_int)
                }),
                *filtered_attr_dicts,
                *[
                    (span, {})
                    for span in self.label_span_list
                ]
            ]
        else:
            attr_dict_items = [
                (self.full_span, {"foreground": BLACK}),
                *[
                    (span, {
                        key: BLACK if key in MARKUP_COLOR_KEYS else val
                        for key, val in attr_dict.items()
                    })
                    for span, attr_dict in filtered_attr_dicts
                ],
                *[
                    (span, {"foreground": self.int_to_hex(label + 1)})
                    for label, span in enumerate(self.label_span_list)
                ]
            ]
        inserted_string_pairs = [
            (span, (
                f"<span {self.get_attr_dict_str(attr_dict)}>",
                "</span>"
            ))
            for span, attr_dict in self.merge_attr_dicts(attr_dict_items)
        ]
        span_repl_dict = self.generate_span_repl_dict(
            inserted_string_pairs, self.command_repl_items
        )
        return self.get_replaced_substr(self.full_span, span_repl_dict)

    # Method alias

    def get_parts_by_text(self, text: str, **kwargs) -> VGroup:
        return self.get_parts_by_string(text, **kwargs)

    def get_part_by_text(self, text: str, **kwargs) -> VMobject:
        return self.get_part_by_string(text, **kwargs)

    def set_color_by_text(self, text: str, color: ManimColor, **kwargs):
        return self.set_color_by_string(text, color, **kwargs)

    def set_color_by_text_to_color_map(
        self, text_to_color_map: dict[str, ManimColor], **kwargs
    ):
        return self.set_color_by_string_to_color_map(
            text_to_color_map, **kwargs
        )

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
