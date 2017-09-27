from helpers import *

from vectorized_mobject import VMobject, VGroup, VectorizedPoint
from svg_mobject import SVGMobject, VMobjectFromSVGPathstring
from topics.geometry import BackgroundRectangle

import collections
import sys

TEX_MOB_SCALE_FACTOR = 0.05

class TexSymbol(VMobjectFromSVGPathstring):
    def pointwise_become_partial(self, mobject, a, b):
        #TODO, this assumes a = 0
        if b < 0.5:
            b = 2*b 
            added_width = 1
            opacity = 0
        else:
            added_width = 2 - 2*b
            opacity = 2*b - 1
            b = 1
        VMobjectFromSVGPathstring.pointwise_become_partial(
            self, mobject, 0, b
        )
        self.set_stroke(width = added_width + mobject.get_stroke_width())
        self.set_fill(opacity = opacity)


class TexMobject(SVGMobject):
    CONFIG = {
        "template_tex_file" : TEMPLATE_TEX_FILE,
        "stroke_width"      : 0,
        "fill_opacity"      : 1.0,
        "fill_color"        : WHITE,
        "should_center"     : True,
        "arg_separator"     : " ",
        "height" : None,
        "organize_left_to_right" : False,
        "propogate_style_to_family" : True,
        "alignment" : "",
    }
    def __init__(self, *args, **kwargs):
        digest_config(self, kwargs, locals())
        ##TODO, Eventually remove this
        if len(args) == 1 and isinstance(args[0], list):
            self.args = args[0]
        ##
        assert(all([isinstance(a, str) for a in self.args]))
        self.tex_string = self.get_modified_expression()
        file_name = tex_to_svg_file(
            self.tex_string,
            self.template_tex_file
        )
        SVGMobject.__init__(self, file_name = file_name, **kwargs)
        self.scale(TEX_MOB_SCALE_FACTOR)
        if self.organize_left_to_right:
            self.organize_submobjects_left_to_right()

    def path_string_to_mobject(self, path_string):
        #Overwrite superclass default to use
        #specialized path_string mobject
        return TexSymbol(path_string)

    def generate_points(self):
        SVGMobject.generate_points(self)
        if len(self.args) > 1:
            self.handle_multiple_args()

    def get_modified_expression(self):
        result = self.arg_separator.join(self.args)
        result = " ".join([self.alignment, result])
        result = result.strip()
        result = self.modify_special_strings(result)

        return result

    def modify_special_strings(self, tex):
        tex = self.remove_stray_braces(tex)
        if tex in ["\\over", "\\overline"]:
            #fraction line needs something to be over
            tex += "\\,"
        if tex == "\\sqrt":
            tex += "{\\quad}"
        if tex == "\\substack":
            tex = ""
        for t1, t2 in ("\\left", "\\right"), ("\\right", "\\left"):
            should_replace = reduce(op.and_, [
                t1 in tex,
                t2 not in tex,
                len(tex) > len(t1) and tex[len(t1)] in "()[]|\\"
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

    def handle_multiple_args(self):
        """
        Reorganize existing submojects one layer 
        deeper based on the structure of args (as a list of strings)
        """
        new_submobjects = []
        curr_index = 0
        self.expression_parts = list(self.args)
        for expr in self.args:
            sub_tex_mob = TexMobject(expr, **self.CONFIG)
            sub_tex_mob.tex_string = expr ##Want it unmodified
            num_submobs = len(sub_tex_mob.submobjects)
            new_index = curr_index + num_submobs
            if num_submobs == 0:
                if len(self) > curr_index:
                    last_submob_index = curr_index
                else:
                    last_submob_index = -1
                sub_tex_mob.submobjects = [VectorizedPoint(
                    self.submobjects[last_submob_index].get_right()
                )]
            else:
                sub_tex_mob.submobjects = self.submobjects[curr_index:new_index]
            new_submobjects.append(sub_tex_mob)
            curr_index = new_index
        self.submobjects = new_submobjects
        return self

    def get_parts_by_tex(self, tex, substring = True):
        def test(tex1, tex2):
            return tex1 == tex2 or (substring and tex1 in tex2)

        tex_submobjects = filter(
            lambda m : isinstance(m, TexMobject),
            self.submobject_family()
        )
        if hasattr(self, "expression_parts"):
            tex_submobjects.remove(self)
        return VGroup(*filter(
            lambda m : test(tex, m.get_tex_string()),
            tex_submobjects
        ))

    def get_part_by_tex(self, tex, **kwargs):
        all_parts = self.get_parts_by_tex(tex, **kwargs)
        return all_parts[0] if all_parts else None

    def highlight_by_tex(self, tex, color, **kwargs):
        parts_to_color = self.get_parts_by_tex(tex, **kwargs)
        for part in parts_to_color:
            part.highlight(color)
        return self

    def highlight_by_tex_to_color_map(self, tex_to_color_map):
        for tex, color in tex_to_color_map.items():
            self.highlight_by_tex(tex, color)
        return self

    def index_of_part(self, part):
        split_self = self.split()
        if part not in split_self:
            raise Exception("Trying to get index of part not in TexMobject")
        return self.split().index(part)

    def index_of_part_by_tex(self, tex, **kwargs):
        part = self.get_part_by_tex(tex, **kwargs)
        return self.index_of_part(part)

    def organize_submobjects_left_to_right(self):
        self.submobjects.sort(
            lambda m1, m2 : int((m1.get_left()-m2.get_left())[0])
        )

    def add_background_rectangle(self, color = BLACK, opacity = 0.75):
        self.background_rectangle = BackgroundRectangle(
            self, color = color, 
            fill_opacity = opacity
        )
        letters = VMobject(*self.submobjects)
        self.submobjects = [self.background_rectangle, letters]
        return self

class TextMobject(TexMobject):
    CONFIG = {
        "template_tex_file" : TEMPLATE_TEXT_FILE,
        "alignment" : "\\centering",
    }

class Brace(TexMobject):
    CONFIG = {
        "buff" : 0.2,
        "width_multiplier" : 2,
        "max_num_quads" : 15,
        "min_num_quads" : 0,
    }
    def __init__(self, mobject, direction = DOWN, **kwargs):
        digest_config(self, kwargs, locals())
        angle = -np.arctan2(*direction[:2]) + np.pi
        mobject.rotate(-angle)
        left  = mobject.get_corner(DOWN+LEFT)
        right = mobject.get_corner(DOWN+RIGHT)
        target_width = right[0]-left[0]

        ## Adding int(target_width) qquads gives approximately the right width
        num_quads = np.clip(
            int(self.width_multiplier*target_width),
            self.min_num_quads, self.max_num_quads
        )
        tex_string = "\\underbrace{%s}"%(num_quads*"\\qquad")
        TexMobject.__init__(self, tex_string, **kwargs)
        self.tip_point_index = np.argmin(self.get_all_points()[:,1])
        self.stretch_to_fit_width(target_width)
        self.shift(left - self.get_corner(UP+LEFT) + self.buff*DOWN)
        for mob in mobject, self:
            mob.rotate(angle)

    def put_at_tip(self, mob, use_next_to = True, **kwargs):
        if use_next_to:
            mob.next_to(
                self.get_tip(), 
                np.round(self.get_direction()), 
                **kwargs
            )
        else:
            mob.move_to(self.get_tip())
            buff = kwargs.get("buff", DEFAULT_MOBJECT_TO_MOBJECT_BUFFER)
            shift_distance = mob.get_width()/2.0+buff
            mob.shift(self.get_direction()*shift_distance)
        return self

    def get_text(self, *text, **kwargs):
        text_mob = TextMobject(*text)
        self.put_at_tip(text_mob, **kwargs)
        return text_mob

    def get_tex(self, *tex, **kwargs):
        tex_mob = TexMobject(*tex)
        self.put_at_tip(tex_mob, **kwargs)
        return tex_mob

    def get_tip(self):
        # Very specific to the LaTeX representation
        # of a brace, but it's the only way I can think
        # of to get the tip regardless of orientation.
        return self.get_all_points()[self.tip_point_index]

    def get_direction(self):
        vect = self.get_tip() - self.get_center()
        return vect/np.linalg.norm(vect)

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
        print "Writing \"%s\" to %s"%(
            "".join(expression), result
        )
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

def dvi_to_svg(dvi_file, regen_if_exists = False):
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














