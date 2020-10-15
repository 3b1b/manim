"""Mobjects representing text rendered using LaTeX."""

__all__ = [
    "TexSymbol",
    "SingleStringMathTex",
    "MathTex",
    "Tex",
    "BulletedList",
    "MathTexFromPresetString",
    "Title",
    "TexMobject",
    "TextMobject",
]


from functools import reduce
import operator as op

from ... import config, logger
from ...constants import *
from ...mobject.geometry import Line
from ...mobject.svg.svg_mobject import SVGMobject
from ...mobject.svg.svg_mobject import VMobjectFromSVGPathstring
from ...mobject.types.vectorized_mobject import VGroup
from ...mobject.types.vectorized_mobject import VectorizedPoint
from ...utils.config_ops import digest_config
from ...utils.strings import split_string_list_to_isolate_substrings
from ...utils.tex_file_writing import tex_to_svg_file
from ...utils.color import BLACK
from ...utils.tex import TexTemplate

TEX_MOB_SCALE_FACTOR = 0.05


class TexSymbol(VMobjectFromSVGPathstring):
    """Purely a renaming of VMobjectFromSVGPathstring."""

    pass


class SingleStringMathTex(SVGMobject):
    """Elementary building block for rendering text with LaTeX.

    Tests
    -----
    Check that creating a :class:`~.SingleStringMathTex` object works::

        >>> SingleStringMathTex('Test')
        SingleStringMathTex('Test')
    """

    CONFIG = {
        "stroke_width": 0,
        "fill_opacity": 1.0,
        "background_stroke_width": 1,
        "background_stroke_color": BLACK,
        "should_center": True,
        "height": None,
        "organize_left_to_right": False,
        "alignment": "",
        "tex_environment": "align*",
        "tex_template": None,
    }

    def __init__(self, tex_string, **kwargs):
        digest_config(self, kwargs)
        if self.tex_template is None:
            self.tex_template = kwargs.get("tex_template", config["tex_template"])

        assert isinstance(tex_string, str)
        self.tex_string = tex_string
        file_name = tex_to_svg_file(
            self.get_modified_expression(tex_string),
            environment=self.tex_environment,
            tex_template=self.tex_template,
        )
        SVGMobject.__init__(self, file_name=file_name, **kwargs)
        if self.height is None:
            self.scale(TEX_MOB_SCALE_FACTOR)
        if self.organize_left_to_right:
            self.organize_submobjects_left_to_right()

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.tex_string)})"

    def get_modified_expression(self, tex_string):
        result = self.alignment + " " + tex_string
        result = result.strip()
        result = self.modify_special_strings(result)
        return result

    def modify_special_strings(self, tex):
        tex = self.remove_stray_braces(tex)
        should_add_filler = reduce(
            op.or_,
            [
                # Fraction line needs something to be over
                tex == "\\over",
                tex == "\\overline",
                # Makesure sqrt has overbar
                tex == "\\sqrt",
                # Need to add blank subscript or superscript
                tex.endswith("_"),
                tex.endswith("^"),
                tex.endswith("dot"),
            ],
        )
        if should_add_filler:
            filler = "{\\quad}"
            tex += filler

        if tex == "\\substack":
            tex = "\\quad"

        if tex == "":
            tex = "\\quad"

        # To keep files from starting with a line break
        if tex.startswith("\\\\"):
            tex = tex.replace("\\\\", "\\quad\\\\")

        # Handle imbalanced \left and \right
        num_lefts, num_rights = [
            len([s for s in tex.split(substr)[1:] if s and s[0] in "(){}[]|.\\"])
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

    def remove_stray_braces(self, tex):
        """
        Makes MathTex resilient to unmatched { at start
        """
        # "\{" does not count (it's a brace literal), but "\\{" counts (it's a new line and then brace)
        num_lefts = tex.count("{") - tex.count("\\{") + tex.count("\\\\{")
        num_rights = tex.count("}") - tex.count("\\}") + tex.count("\\\\}")
        while num_rights > num_lefts:
            tex = "{" + tex
            num_lefts += 1
        while num_lefts > num_rights:
            tex = tex + "}"
            num_rights += 1
        return tex

    def get_tex_string(self):
        return self.tex_string

    def path_string_to_mobject(self, path_string):
        # Overwrite superclass default to use
        # specialized path_string mobject
        return TexSymbol(path_string)

    def organize_submobjects_left_to_right(self):
        self.sort(lambda p: p[0])
        return self


class MathTex(SingleStringMathTex):
    """A string compiled with LaTeX in math mode.

    Examples
    --------
    .. manim:: Formula
        :save_last_frame:

        class Formula(Scene):
            def construct(self):
                t = MathTex(r"\int_a^b f'(x) dx = f(b)- f(a)")
                self.add(t)

    Tests
    -----
    Check that creating a :class:`~.MathTex` works::

        >>> MathTex('a^2 + b^2 = c^2')
        MathTex('a^2 + b^2 = c^2')

    """

    CONFIG = {
        "arg_separator": " ",
        "substrings_to_isolate": [],
        "tex_to_color_map": {},
        "tex_environment": "align*",
    }

    def __init__(self, *tex_strings, **kwargs):
        digest_config(self, kwargs)
        tex_strings = self.break_up_tex_strings(tex_strings)
        self.tex_strings = tex_strings
        SingleStringMathTex.__init__(
            self, self.arg_separator.join(tex_strings), **kwargs
        )
        config = dict(self.CONFIG)
        config.update(kwargs)
        self.break_up_by_substrings(config)
        self.set_color_by_tex_to_color_map(self.tex_to_color_map)

        if self.organize_left_to_right:
            self.organize_submobjects_left_to_right()

    def break_up_tex_strings(self, tex_strings):
        substrings_to_isolate = op.add(
            self.substrings_to_isolate, list(self.tex_to_color_map.keys())
        )
        split_list = split_string_list_to_isolate_substrings(
            tex_strings, *substrings_to_isolate
        )
        if self.arg_separator == " ":
            split_list = [str(x).strip() for x in split_list]
        # split_list = list(map(str.strip, split_list))
        split_list = [s for s in split_list if s != ""]
        return split_list

    def break_up_by_substrings(self, config):
        """
        Reorganize existing submojects one layer
        deeper based on the structure of tex_strings (as a list
        of tex_strings)
        """
        new_submobjects = []
        curr_index = 0
        for tex_string in self.tex_strings:
            sub_tex_mob = SingleStringMathTex(tex_string, **config)
            num_submobs = len(sub_tex_mob.submobjects)
            new_index = curr_index + num_submobs
            if num_submobs == 0:
                # For cases like empty tex_strings, we want the corresponing
                # part of the whole MathTex to be a VectorizedPoint
                # positioned in the right part of the MathTex
                sub_tex_mob.submobjects = [VectorizedPoint()]
                last_submob_index = min(curr_index, len(self.submobjects) - 1)
                sub_tex_mob.move_to(self.submobjects[last_submob_index], RIGHT)
            else:
                sub_tex_mob.submobjects = self.submobjects[curr_index:new_index]
            new_submobjects.append(sub_tex_mob)
            curr_index = new_index
        self.submobjects = new_submobjects
        return self

    def get_parts_by_tex(self, tex, substring=True, case_sensitive=True):
        def test(tex1, tex2):
            if not case_sensitive:
                tex1 = tex1.lower()
                tex2 = tex2.lower()
            if substring:
                return tex1 in tex2
            else:
                return tex1 == tex2

        return VGroup(*[m for m in self.submobjects if test(tex, m.get_tex_string())])

    def get_part_by_tex(self, tex, **kwargs):
        all_parts = self.get_parts_by_tex(tex, **kwargs)
        return all_parts[0] if all_parts else None

    def set_color_by_tex(self, tex, color, **kwargs):
        parts_to_color = self.get_parts_by_tex(tex, **kwargs)
        for part in parts_to_color:
            part.set_color(color)
        return self

    def set_color_by_tex_to_color_map(self, texs_to_color_map, **kwargs):
        for texs, color in list(texs_to_color_map.items()):
            try:
                # If the given key behaves like tex_strings
                texs + ""
                self.set_color_by_tex(texs, color, **kwargs)
            except TypeError:
                # If the given key is a tuple
                for tex in texs:
                    self.set_color_by_tex(tex, color, **kwargs)
        return self

    def index_of_part(self, part):
        split_self = self.split()
        if part not in split_self:
            raise ValueError("Trying to get index of part not in MathTex")
        return split_self.index(part)

    def index_of_part_by_tex(self, tex, **kwargs):
        part = self.get_part_by_tex(tex, **kwargs)
        return self.index_of_part(part)

    def sort_alphabetically(self):
        self.submobjects.sort(key=lambda m: m.get_tex_string())


class Tex(MathTex):
    r"""A string compiled with LaTeX in normal mode.

    Tests
    -----

    Check whether writing a LaTeX string works::

        >>> Tex('The horse does not eat cucumber salad.')
        Tex('The horse does not eat cucumber salad.')

    """

    CONFIG = {
        "alignment": "\\centering",
        "arg_separator": "",
        "tex_environment": None,
    }


class BulletedList(Tex):
    CONFIG = {
        "buff": MED_LARGE_BUFF,
        "dot_scale_factor": 2,
        # Have to include because of handle_multiple_args implementation
        "alignment": "",
    }

    def __init__(self, *items, **kwargs):
        line_separated_items = [s + "\\\\" for s in items]
        Tex.__init__(self, *line_separated_items, **kwargs)
        for part in self:
            dot = MathTex("\\cdot").scale(self.dot_scale_factor)
            dot.next_to(part[0], LEFT, SMALL_BUFF)
            part.add_to_back(dot)
        self.arrange(DOWN, aligned_edge=LEFT, buff=self.buff)

    def fade_all_but(self, index_or_string, opacity=0.5):
        arg = index_or_string
        if isinstance(arg, str):
            part = self.get_part_by_tex(arg)
        elif isinstance(arg, int):
            part = self.submobjects[arg]
        else:
            raise TypeError("Expected int or string, got {0}".format(arg))
        for other_part in self.submobjects:
            if other_part is part:
                other_part.set_fill(opacity=1)
            else:
                other_part.set_fill(opacity=opacity)


class MathTexFromPresetString(MathTex):
    CONFIG = {
        # To be filled by subclasses
        "tex": None,
        "color": None,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        MathTex.__init__(self, self.tex, **kwargs)
        self.set_color(self.color)


class Title(Tex):
    CONFIG = {
        "scale_factor": 1,
        "include_underline": True,
        # This will override underline_width
        "match_underline_width_to_text": False,
        "underline_buff": MED_SMALL_BUFF,
    }

    def __init__(self, *text_parts, **kwargs):
        Tex.__init__(self, *text_parts, **kwargs)
        self.underline_width = config["frame_width"] - 2
        self.scale(self.scale_factor)
        self.to_edge(UP)
        if self.include_underline:
            underline = Line(LEFT, RIGHT)
            underline.next_to(self, DOWN, buff=self.underline_buff)
            if self.match_underline_width_to_text:
                underline.match_width(self)
            else:
                underline.set_width(self.underline_width)
            self.add(underline)
            self.underline = underline


class TexMobject(MathTex):
    def __init__(self, *tex_strings, **kwargs):
        logger.warning(
            "TexMobject has been deprecated (due to its confusing name) "
            "in favour of MathTex. Please use MathTex instead!"
        )
        MathTex.__init__(self, *tex_strings, **kwargs)


class TextMobject(Tex):
    def __init__(self, *text_parts, **kwargs):
        logger.warning(
            "TextMobject has been deprecated (due to its confusing name) "
            "in favour of Tex. Please use Tex instead!"
        )
        Tex.__init__(self, *text_parts, **kwargs)
