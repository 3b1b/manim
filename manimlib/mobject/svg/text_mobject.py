import itertools as it
import os
import re
import typing
import xml.sax.saxutils as saxutils
from contextlib import contextmanager
from pathlib import Path

import pygments
import pygments.formatters
import pygments.lexers

import manimglpango
from manimlib.logger import log
from manimlib.constants import *
from manimlib.mobject.geometry import Dot
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.utils.iterables import adjacent_pairs
from manimlib.utils.tex_file_writing import tex_hash
from manimlib.utils.config_ops import digest_config
from manimlib.utils.directories import get_downloads_dir
from manimlib.utils.directories import get_text_dir


TEXT_MOB_SCALE_FACTOR = 0.0076
DEFAULT_LINE_SPACING_SCALE = 0.6


class Text(SVGMobject):
    CONFIG = {
        # Mobject
        "svg_default": {
            "color": WHITE,
            "opacity": 1.0,
            "stroke_width": 0,
        },
        "height": None,
        # Text
        "font_size": 48,
        "lsh": None,
        "justify": False,
        "indent": 0,
        "alignment": "LEFT",
        "line_width": -1,  # No auto wrapping if set to -1
        "font": "",
        "gradient": None,
        "slant": NORMAL,
        "weight": NORMAL,
        "t2c": {},
        "t2f": {},
        "t2g": {},
        "t2s": {},
        "t2w": {},
        "disable_ligatures": True,
        "escape_chars": True,
        "apply_space_chars": True,
    }

    def __init__(self, text, **kwargs):
        self.full2short(kwargs)
        digest_config(self, kwargs)
        validate_error = manimglpango.validate(text)
        if validate_error:
            raise ValueError(validate_error)
        self.text = text
        super.__init__(**kwargs)

        self.scale(self.font_size / 48)  # TODO
        if self.gradient:
            self.set_color_by_gradient(*self.gradient)
        # anti-aliasing
        if self.height is None:
            self.scale(TEXT_MOB_SCALE_FACTOR)

    @property
    def hash_seed(self):
        return (
            self.__class__.__name__,
            self.svg_default,
            self.path_string_config,
            self.text,
            #self.font_size,
            self.lsh,
            self.justify,
            self.indent,
            self.alignment,
            self.line_width,
            self.font,
            self.slant,
            self.weight,
            self.t2c,
            self.t2f,
            self.t2s,
            self.t2w,
            self.disable_ligatures,
            self.escape_chars,
            self.apply_space_chars
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

        global_params = {}
        lsh = self.lsh or DEFAULT_LINE_SPACING_SCALE
        global_params["line_height"] = 0.6 * lsh + 0.64
        if self.font:
            global_params["font_family"] = self.font
        #global_params["font_size"] = self.font_size * 1024
        global_params["font_style"] = self.slant
        global_params["font_weight"] = self.weight
        if self.disable_ligatures:
            global_params["font_features"] = "liga=0,dlig=0,clig=0,hlig=0"
        text_span_to_params_map = {
            (0, len(self.text)): global_params
        }

        for t2x_dict, key in (
            (self.t2c, "color"),
            (self.t2f, "font_family"),
            (self.t2s, "font_style"),
            (self.t2w, "font_weight")
        ):
            for word_or_text_span, value in t2x_dict.items():
                for text_span in self.find_indexes(word_or_text_span):
                    if text_span not in text_span_to_params_map:
                        text_span_to_params_map[text_span] = {}
                    text_span_to_params_map[text_span][key] = value

        indices, _, flags, param_dicts = zip(*sorted([
            (*text_span[::(1, -1)[flag]], flag, param_dict)
            for text_span, param_dict in text_span_to_params_map.items()
            for flag in range(2)
        ]))
        tag_pieces = [
            (f"<span {self.get_attr_list_str(param_dict)}>", "</span>")[flag]
            for flag, param_dict in zip(flags, param_dicts)
        ]
        tag_pieces.insert(0, "")
        string_pieces = [
            self.text[slice(*piece_span)]
            for piece_span in list(adjacent_pairs(indices))[:-1]
        ]
        if self.escape_chars:
            string_pieces = list(map(saxutils.escape, string_pieces))
        return "".join(it.chain(*zip(tag_pieces, string_pieces)))

    def find_indexes(self, word_or_text_span):
        if isinstance(word_or_text_span, tuple):
            return [word_or_text_span]

        return [
            match_obj.span()
            for match_obj in re.finditer(re.escape(word_or_text_span), self.text)
        ]

    @staticmethod
    def get_attr_list_str(param_dict):
        return " ".join([
            f"{key}='{value}'"
            for key, value in param_dict.items()
        ])

    def markup_to_svg(self, markup_str, file_name):
        width = DEFAULT_PIXEL_WIDTH
        height = DEFAULT_PIXEL_HEIGHT
        justify = self.justify
        indent = self.indent
        alignment = ["LEFT", "CENTER", "RIGHT"].index(self.alignment.upper())
        line_width = self.line_width * 1024

        return manimglpango.markup_to_svg(
            markup_str,
            file_name,
            width,
            height,
            justify=justify,
            indent=indent,
            alignment=alignment,
            line_width=line_width
        )

    def generate_mobject(self):
        super().generate_mobject()

        # Remove empty paths
        submobjects = list(filter(lambda submob: submob.has_points(), self))

        # Apply space characters
        if self.apply_space_chars:
            for char_index, char in enumerate(self.text):
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


class MarkupText(Text):
    CONFIG = {
        "escape_chars": False,
        "apply_space_chars": False,
    }


class Code(Text):
    CONFIG = {
        "font": "Consolas",
        "font_size": 24,
        "lsh": 1.0,  # TODO
        "language": "python",
        # Visit https://pygments.org/demo/ to have a preview of more styles.
        "code_style": "monokai"
    }

    def __init__(self, code, **kwargs):
        digest_config(self, kwargs)
        self.code = code
        lexer = pygments.lexers.get_lexer_by_name(self.language)
        formatter = pygments.formatters.PangoMarkupFormatter(style=self.code_style)
        markup_code = pygments.highlight(code, lexer, formatter)
        super().__init__(markup_code, **kwargs)


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
        assert manimglpango.register_font(str(file_path))
        yield
    finally:
        manimglpango.unregister_font(str(file_path))
