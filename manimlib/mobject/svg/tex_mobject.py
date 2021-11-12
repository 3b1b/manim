from functools import reduce
import hashlib
import operator as op
import re
from types import MethodType

from manimlib.constants import *
from manimlib.mobject.geometry import Line
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.config_ops import digest_config
from manimlib.utils.tex_file_writing import tex_to_svg_file
from manimlib.utils.tex_file_writing import get_tex_config
from manimlib.utils.tex_file_writing import display_during_execution


SCALE_FACTOR_PER_FONT_POINT = 0.001


tex_hash_to_mob_map = {}


class SVGTex(SVGMobject):
    CONFIG = {
        "height": None,
        # The hierachy structure is needed for the `break_up_by_substrings` method
        "unpack_groups": False,
        "path_string_config": {
            "should_subdivide_sharp_curves": True,
            "should_remove_null_curves": True,
        }
    }

    def __init__(self, tex_obj, **kwargs):
        self.tex_obj = tex_obj
        full_tex = self.get_tex_file_body()
        filename = tex_to_svg_file(full_tex)
        super().__init__(filename, **kwargs)
        self.break_up_by_substrings()
        self.init_colors()

    def get_mobjects_from(self, element):
        result = super().get_mobjects_from(element)
        if len(result) == 0:
            return result
        result[0].fill_color = None
        try:
            fill_color = element.getAttribute("fill")
            if fill_color:
                result[0].fill_color = fill_color
        except:
            pass
        return result

    def get_tex_file_body(self):
        new_tex = self.get_modified_expression()
        if self.tex_obj.math_mode:
            new_tex = "\\begin{align*}\n" + new_tex + "\n\\end{align*}"

        new_tex = self.tex_obj.alignment + "\n" + new_tex

        tex_config = get_tex_config()
        return tex_config["tex_body"].replace(
            tex_config["text_to_replace"],
            new_tex
        )

    def get_modified_expression(self):
        tex_components = []
        to_isolate = self.tex_obj.substrings_to_isolate
        for tex_substring in self.tex_obj.tex_substrings:
            if tex_substring not in to_isolate:
                tex_components.append(tex_substring)
            else:
                color_index = to_isolate.index(tex_substring)
                tex_components.append("".join([
                    "{\\color[RGB]{",
                    str(self.get_nth_color_tuple(color_index))[1:-1],
                    "}",
                    tex_substring,
                    "}"
                ]))
        return self.tex_obj.arg_separator.join(tex_components)

    def break_up_by_substrings(self):
        """
        Reorganize existing submojects one layer
        deeper based on the structure of tex_substrings (as a list
        of tex_substrings)
        """
        if len(self.tex_obj.tex_substrings) == 1:
            submob = self.copy()
            self.set_submobjects([submob])
            return self
        new_submobjects = []
        new_submobject_components = []
        for part in self.submobjects:
            if part.fill_color is not None:
                if new_submobject_components:
                    new_submobjects.append(VGroup(*new_submobject_components))
                    new_submobject_components = []
                new_submobjects.append(part)
            else:
                new_submobject_components.append(part)
        if new_submobject_components:
            new_submobjects.append(VGroup(*new_submobject_components))

        for submob, tex_substring in zip(new_submobjects, self.tex_obj.tex_substrings):
            fill_color = submob.fill_color
            if fill_color is not None:
                submob_tex_string = self.tex_obj.substrings_to_isolate[int(fill_color[1:], 16) - 1]
            else:
                submob_tex_string = tex_substring
            submob.tex_string = submob_tex_string
            # Prevent methods and classes using `get_tex()` from breaking.
            submob.get_tex = MethodType(lambda sm: sm.tex_string, submob)
        self.set_submobjects(new_submobjects)

        return self

    @staticmethod
    def get_nth_color_tuple(n):  ## TODO: Refactor
        # Get a unique color different from black,
        # or the svg file will not include the color information.
        return (
            (n + 1) // 256 // 256,
            (n + 1) // 256 % 256,
            (n + 1) % 256
        )


class Tex(VMobject):
    CONFIG = {
        "fill_opacity": 1.0,
        "stroke_width": 0,
        "should_center": True,
        "font_size": 48,
        "height": None,
        "organize_left_to_right": False,
        "alignment": "\\centering",
        "math_mode": True,
        "arg_separator": "",
        "isolate": [],
        "tex_to_color_map": {},
    }

    def __init__(self, *tex_strings, **kwargs):
        super().__init__(**kwargs)
        self.substrings_to_isolate = [*self.isolate, *self.tex_to_color_map.keys()]
        self.tex_substrings = self.break_up_tex_strings(tex_strings)
        tex_string = self.arg_separator.join(tex_strings)
        self.tex_string = tex_string

        hash_val = self.tex2hash()
        if hash_val not in tex_hash_to_mob_map:  ## TODO
            with display_during_execution(f" Writing \"{tex_string}\""):
                svg_mob = SVGTex(self)
                tex_hash_to_mob_map[hash_val] = svg_mob
        self.add(*(
            sm.copy()
            for sm in tex_hash_to_mob_map[hash_val]
        ))
        self.init_colors()
        self.set_color_by_tex_to_color_map(self.tex_to_color_map, substring=False)

        if self.height is None:
            self.scale(SCALE_FACTOR_PER_FONT_POINT * self.font_size)
        if self.organize_left_to_right:
            self.organize_submobjects_left_to_right()

    def tex2hash(self):
        id_str = self.tex_string + str(self.substrings_to_isolate)
        hasher = hashlib.sha256()
        hasher.update(id_str.encode())
        return hasher.hexdigest()[:16]

    def break_up_tex_strings(self, tex_strings):
        # Separate out any strings specified in the isolate
        # or tex_to_color_map lists.
        if len(self.substrings_to_isolate) == 0:
            return tex_strings
        patterns = (
            "({})".format(re.escape(ss))
            for ss in self.substrings_to_isolate
        )
        pattern = "|".join(patterns)
        pieces = []
        for s in tex_strings:
            if pattern:
                pieces.extend(re.split(pattern, s))
            else:
                pieces.append(s)
        return list(filter(lambda s: s, pieces))


    def organize_submobjects_left_to_right(self):
        self.sort(lambda p: p[0])
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

        return VGroup(*[
            mob for mob in self.submobjects if test(tex, mob.get_tex())
        ])

    def get_part_by_tex(self, tex, **kwargs):
        all_parts = self.get_parts_by_tex(tex, **kwargs)
        return all_parts[0] if all_parts else None

    def set_color_by_tex(self, tex, color, **kwargs):
        self.get_parts_by_tex(tex, **kwargs).set_color(color)
        return self

    def set_color_by_tex_to_color_map(self, tex_to_color_map, **kwargs):
        for tex, color in list(tex_to_color_map.items()):
            self.set_color_by_tex(tex, color, **kwargs)
        return self

    def index_of_part(self, part, start=0):
        return self.submobjects.index(part, start)

    def index_of_part_by_tex(self, tex, start=0, **kwargs):
        part = self.get_part_by_tex(tex, **kwargs)
        return self.index_of_part(part, start)

    def slice_by_tex(self, start_tex=None, stop_tex=None, **kwargs):
        if start_tex is None:
            start_index = 0
        else:
            start_index = self.index_of_part_by_tex(start_tex, **kwargs)

        if stop_tex is None:
            return self[start_index:]
        else:
            stop_index = self.index_of_part_by_tex(stop_tex, start=start_index, **kwargs)
            return self[start_index:stop_index]

    def sort_alphabetically(self):
        self.submobjects.sort(key=lambda m: m.get_tex())

    def set_bstroke(self, color=BLACK, width=4):
        self.set_stroke(color, width, background=True)
        return self


class TexText(Tex):
    CONFIG = {
        "math_mode": False,
        "arg_separator": "",
    }


class BulletedList(TexText):
    CONFIG = {
        "buff": MED_LARGE_BUFF,
        "dot_scale_factor": 2,
        "alignment": "",
    }

    def __init__(self, *items, **kwargs):
        line_separated_items = [s + "\\\\" for s in items]
        TexText.__init__(self, *line_separated_items, **kwargs)
        for part in self:
            dot = Tex("\\cdot").scale(self.dot_scale_factor)
            dot.next_to(part[0], LEFT, SMALL_BUFF)
            part.add_to_back(dot)
        self.arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=self.buff
        )

    def fade_all_but(self, index_or_string, opacity=0.5):
        arg = index_or_string
        if isinstance(arg, str):
            part = self.get_part_by_tex(arg)
        elif isinstance(arg, int):
            part = self.submobjects[arg]
        else:
            raise Exception("Expected int or string, got {0}".format(arg))
        for other_part in self.submobjects:
            if other_part is part:
                other_part.set_fill(opacity=1)
            else:
                other_part.set_fill(opacity=opacity)


class TexFromPresetString(Tex):
    CONFIG = {
        # To be filled by subclasses
        "tex": None,
        "color": None,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        Tex.__init__(self, self.tex, **kwargs)
        self.set_color(self.color)


class Title(TexText):
    CONFIG = {
        "scale_factor": 1,
        "include_underline": True,
        "underline_width": FRAME_WIDTH - 2,
        # This will override underline_width
        "match_underline_width_to_text": False,
        "underline_buff": MED_SMALL_BUFF,
    }

    def __init__(self, *text_parts, **kwargs):
        TexText.__init__(self, *text_parts, **kwargs)
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
