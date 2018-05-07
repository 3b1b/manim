from constants import *

from svg_mobject import SVGMobject
from svg_mobject import VMobjectFromSVGPathstring
from utils.config_ops import digest_config
from utils.strings import split_string_list_to_isolate_substring
from mobject.types.vectorized_mobject import VGroup
from mobject.types.vectorized_mobject import VectorizedPoint

import operator as op

# TODO list
# - Make sure if "color" is passed into TexMobject, it behaves as expected

TEX_MOB_SCALE_FACTOR = 0.05


class TexSymbol(VMobjectFromSVGPathstring):
    def pointwise_become_partial(self, mobject, a, b):
        # TODO, this assumes a = 0
        if b < 0.5:
            b = 2 * b
            added_width = 1
            opacity = 0
        else:
            added_width = 2 - 2 * b
            opacity = 2 * b - 1
            b = 1
        VMobjectFromSVGPathstring.pointwise_become_partial(
            self, mobject, 0, b
        )
        self.set_stroke(width=added_width + mobject.get_stroke_width())
        self.set_fill(opacity=opacity)


class SingleStringTexMobject(SVGMobject):
    CONFIG = {
        "template_tex_file": TEMPLATE_TEX_FILE,
        "stroke_width": 0,
        "fill_opacity": 1.0,
        "should_center": True,
        "height": None,
        "organize_left_to_right": False,
        "propagate_style_to_family": True,
        "alignment": "",
    }

    def __init__(self, tex_string, **kwargs):
        digest_config(self, kwargs)
        assert(isinstance(tex_string, str))
        self.tex_string = tex_string
        file_name = tex_to_svg_file(
            self.get_modified_expression(tex_string),
            self.template_tex_file
        )
        SVGMobject.__init__(self, file_name=file_name, **kwargs)
        if self.height is None:
            self.scale(TEX_MOB_SCALE_FACTOR)
        if self.organize_left_to_right:
            self.organize_submobjects_left_to_right()

    def get_modified_expression(self, tex_string):
        result = self.alignment + " " + tex_string
        result = result.strip()
        result = self.modify_special_strings(result)
        return result

    def modify_special_strings(self, tex):
        tex = self.remove_stray_braces(tex)
        if tex in ["\\over", "\\overline"]:
            # fraction line needs something to be over
            tex += "\\,"
        if tex == "\\sqrt":
            tex += "{\\quad}"
        if tex == "\\substack":
            tex = ""
        for t1, t2 in ("\\left", "\\right"), ("\\right", "\\left"):
            should_replace = reduce(op.and_, [
                t1 in tex,
                t2 not in tex,
                len(tex) > len(t1) and tex[len(t1)] in "()[]<>|.\\"
            ])
            if should_replace:
                tex = tex.replace(t1, "\\big")
        if tex == "":
            tex = "\\quad"
        return tex

    def remove_stray_braces(self, tex):
        """
        Makes TexMobject resiliant to unmatched { at start
        """
        num_lefts, num_rights = [
            tex.count(char)
            for char in "{}"
        ]
        if num_rights > num_lefts:
            backwards = tex[::-1].replace("}", "", num_rights - num_lefts)
            tex = backwards[::-1]
        elif num_lefts > num_rights:
            tex = tex.replace("{", "", num_lefts - num_rights)
        return tex

    def get_tex_string(self):
        return self.tex_string

    def path_string_to_mobject(self, path_string):
        # Overwrite superclass default to use
        # specialized path_string mobject
        return TexSymbol(path_string)

    def organize_submobjects_left_to_right(self):
        self.sort_submobjects(lambda p: p[0])
        return self


class TexMobject(SingleStringTexMobject):
    CONFIG = {
        "arg_separator": " ",
        "substrings_to_isolate": [],
        "tex_to_color_map": {},
    }

    def __init__(self, *tex_strings, **kwargs):
        digest_config(self, kwargs)
        tex_strings = self.break_up_tex_strings(tex_strings)
        self.tex_strings = tex_strings
        SingleStringTexMobject.__init__(
            self, self.arg_separator.join(tex_strings), **kwargs
        )
        self.break_up_by_substrings()
        self.set_color_by_tex_to_color_map(self.tex_to_color_map)

        if self.organize_left_to_right:
            self.organize_submobjects_left_to_right()

    def break_up_tex_strings(self, tex_strings):
        substrings_to_isolate = op.add(
            self.substrings_to_isolate,
            self.tex_to_color_map.keys()
        )
        split_list = split_string_list_to_isolate_substring(
            tex_strings, *substrings_to_isolate
        )
        split_list = map(str.strip, split_list)
        split_list = filter(lambda s: s != '', split_list)
        return split_list

    def break_up_by_substrings(self):
        """
        Reorganize existing submojects one layer
        deeper based on the structure of tex_strings (as a list
        of tex_strings)
        """
        new_submobjects = []
        curr_index = 0
        for tex_string in self.tex_strings:
            sub_tex_mob = SingleStringTexMobject(tex_string, **self.CONFIG)
            num_submobs = len(sub_tex_mob.submobjects)
            new_index = curr_index + num_submobs
            if num_submobs == 0:
                # For cases like empty tex_strings, we want the corresponing
                # part of the whole TexMobject to be a VectorizedPoint
                # positioned in the right part of the TexMobject
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

        return VGroup(*filter(
            lambda m: test(tex, m.get_tex_string()),
            self.submobjects
        ))

    def get_part_by_tex(self, tex, **kwargs):
        all_parts = self.get_parts_by_tex(tex, **kwargs)
        return all_parts[0] if all_parts else None

    def set_color_by_tex(self, tex, color, **kwargs):
        parts_to_color = self.get_parts_by_tex(tex, **kwargs)
        for part in parts_to_color:
            part.set_color(color)
        return self

    def set_color_by_tex_to_color_map(self, texs_to_color_map, **kwargs):
        for texs, color in texs_to_color_map.items():
            try:
                # If the given key behaves like tex_strings
                texs + ''
                self.set_color_by_tex(texs, color, **kwargs)
            except TypeError:
                # If the given key is a tuple
                for tex in texs:
                    self.set_color_by_tex(tex, color, **kwargs)
        return self

    def index_of_part(self, part):
        split_self = self.split()
        if part not in split_self:
            raise Exception("Trying to get index of part not in TexMobject")
        return split_self.index(part)

    def index_of_part_by_tex(self, tex, **kwargs):
        part = self.get_part_by_tex(tex, **kwargs)
        return self.index_of_part(part)

    def split(self):
        # Many old scenes assume that when you pass in a single string
        # to TexMobject, it indexes across the characters.
        if len(self.submobjects) == 1:
            return self.submobjects[0].split()
        else:
            return super(TexMobject, self).split()


class TextMobject(TexMobject):
    CONFIG = {
        "template_tex_file": TEMPLATE_TEXT_FILE,
        "alignment": "\\centering",
    }


class BulletedList(TextMobject):
    CONFIG = {
        "buff": MED_LARGE_BUFF,
        "dot_scale_factor": 2,
        # Have to include because of handle_multiple_args implementation
        "template_tex_file": TEMPLATE_TEXT_FILE,
        "alignment": "",
    }

    def __init__(self, *items, **kwargs):
        line_separated_items = [s + "\\\\" for s in items]
        TextMobject.__init__(self, *line_separated_items, **kwargs)
        for part in self:
            dot = TexMobject("\\cdot").scale(self.dot_scale_factor)
            dot.next_to(part[0], LEFT, SMALL_BUFF)
            part.add_to_back(dot)
        self.arrange_submobjects(
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


class TexMobjectFromPresetString(TexMobject):

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        TexMobject.__init__(self, self.tex, **kwargs)
        self.set_color(self.color)

##########


def tex_hash(expression, template_tex_file):
    return str(hash(expression + template_tex_file))


def tex_to_svg_file(expression, template_tex_file):
    image_dir = os.path.join(
        TEX_IMAGE_DIR,
        tex_hash(expression, template_tex_file)
    )
    if os.path.exists(image_dir):
        return get_sorted_image_list(image_dir)
    tex_file = generate_tex_file(expression, template_tex_file)
    dvi_file = tex_to_dvi(tex_file)
    return dvi_to_svg(dvi_file)


def generate_tex_file(expression, template_tex_file):
    result = os.path.join(
        TEX_DIR,
        tex_hash(expression, template_tex_file)
    ) + ".tex"
    if not os.path.exists(result):
        print("Writing \"%s\" to %s" % (
            "".join(expression), result
        ))
        with open(template_tex_file, "r") as infile:
            body = infile.read()
            body = body.replace(TEX_TEXT_TO_REPLACE, expression)
        with open(result, "w") as outfile:
            outfile.write(body)
    return result


def get_null():
    if os.name == "nt":
        return "NUL"
    return "/dev/null"


def tex_to_dvi(tex_file):
    result = tex_file.replace(".tex", ".dvi")
    if not os.path.exists(result):
        commands = [
            "latex",
            "-interaction=batchmode",
            "-halt-on-error",
            "-output-directory=" + TEX_DIR,
            tex_file,
            ">",
            get_null()
        ]
        exit_code = os.system(" ".join(commands))
        if exit_code != 0:
            latex_output = ''
            log_file = tex_file.replace(".tex", ".log")
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    latex_output = f.read()
            raise Exception(
                "Latex error converting to dvi. "
                "See log output above or the log file: %s" % log_file)
    return result


def dvi_to_svg(dvi_file, regen_if_exists=False):
    """
    Converts a dvi, which potentially has multiple slides, into a
    directory full of enumerated pngs corresponding with these slides.
    Returns a list of PIL Image objects for these images sorted as they
    where in the dvi
    """
    result = dvi_file.replace(".dvi", ".svg")
    if not os.path.exists(result):
        commands = [
            "dvisvgm",
            dvi_file,
            "-n",
            "-v",
            "0",
            "-o",
            result,
            ">",
            get_null()
        ]
        os.system(" ".join(commands))
    return result
