from vectorized_mobject import VMobject
from svg_mobject import SVGMobject, VMobjectFromSVGPathstring
from topics.geometry import Rectangle
from helpers import *
import collections

TEX_MOB_SCALE_VAL = 0.05
TEXT_MOB_SCALE_VAL = 0.05


class TexSymbol(VMobjectFromSVGPathstring):
    def pointwise_become_partial(self, mobject, a, b):
        #TODO, this assumes a = 0
        if b < 0.5:
            b = 2*b 
            width = 1
            opacity = 0
        else:
            width = 2 - 2*b
            opacity = 2*b - 1
            b = 1
        VMobjectFromSVGPathstring.pointwise_become_partial(
            self, mobject, 0, b
        )
        self.set_stroke(width = width)
        self.set_fill(opacity = opacity)


class TexMobject(SVGMobject):
    CONFIG = {
        "template_tex_file" : TEMPLATE_TEX_FILE,
        "stroke_width"      : 0,
        "fill_opacity"      : 1.0,
        "fill_color"        : WHITE,
        "should_center"     : True,
        "separate_list_arg_with_spaces" : True,
        "enforce_new_line_structure" : False,
        "initial_scale_val" : TEX_MOB_SCALE_VAL,
        "organize_left_to_right" : False,
        "propogate_style_to_family" : True,
    }
    def __init__(self, expression, **kwargs):
        digest_config(self, kwargs, locals())
        self.is_input_a_list = isinstance(expression, list)
        VMobject.__init__(self, **kwargs)
        self.move_into_position()
        if self.organize_left_to_right:
            self.organize_submobjects_left_to_right()

    def handle_input_type(self):
        if isinstance(self.expression, str):
            self.is_input_a_list = False
        elif isinstance(self.expression, collections.Iterable):
            self.is_input_a_list = True
            self.expression = list(self.expression)
        else:
            raise Exception(
                "TexMobject was expecting string or list, got " + \
                str(type(self.expression)) + \
                " instead."
            )

    def path_string_to_mobject(self, path_string):
        #Overwrite superclass default to use
        #specialized path_string mobject
        return TexSymbol(path_string)


    def generate_points(self):
        self.svg_file = tex_to_svg_file(
            self.get_modified_expression(),
            self.template_tex_file
        )
        SVGMobject.generate_points(self)
        if self.is_input_a_list:
            self.handle_list_expression(self.expression)

    def get_modified_expression(self):
        separator = ""
        if self.is_input_a_list and self.separate_list_arg_with_spaces:
            separator = " "
        result = separator.join(self.expression)
        if self.enforce_new_line_structure:
            result = result.replace("\n", " \\\\ \n ")
        return result

    def handle_list_expression(self, list_expression):
        new_submobjects = []
        curr_index = 0
        for expr in list_expression:
            model = TexMobject(expr, **self.CONFIG)
            new_index = curr_index + len(model.submobjects)
            new_submobjects.append(VMobject(
                *self.submobjects[curr_index:new_index]
            ))
            curr_index = new_index
        self.submobjects = new_submobjects
        return self

    def organize_submobjects_left_to_right(self):
        self.submobjects.sort(
            lambda m1, m2 : int((m1.get_left()-m2.get_left())[0])
        )

    def add_background_rectangle(self, color = BLACK, opacity = 0.75):
        rect = Rectangle(
            stroke_width = 0,
            fill_color = color,
            fill_opacity = opacity
        )
        rect.replace(self, stretch = True)
        self.submobjects = [rect, VMobject(*self.submobjects)]
        return self

class TextMobject(TexMobject):
    CONFIG = {
        "template_tex_file" : TEMPLATE_TEXT_FILE,
        "initial_scale_val" : TEXT_MOB_SCALE_VAL,
        "enforce_new_line_structure" : True,
    }



class Brace(TexMobject):
    CONFIG = {
        "buff" : 0.2,
    }
    TEX_STRING = "\\underbrace{%s}"%(3*"\\qquad")
    def __init__(self, mobject, direction = DOWN, **kwargs):
        TexMobject.__init__(self, self.TEX_STRING, **kwargs)
        angle = -np.arctan2(*direction[:2]) + np.pi
        mobject.rotate(-angle)
        left  = mobject.get_corner(DOWN+LEFT)
        right = mobject.get_corner(DOWN+RIGHT)
        self.stretch_to_fit_width(right[0]-left[0])
        self.shift(left - self.get_corner(UP+LEFT) + self.buff*DOWN)
        for mob in mobject, self:
            mob.rotate(angle)

    
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
    )+".tex"
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

def tex_to_dvi(tex_file):
    result = tex_file.replace(".tex", ".dvi")
    if not os.path.exists(result):
        commands = [
            "latex", 
            "-interaction=batchmode", 
            "-output-directory=" + TEX_DIR,
            tex_file,
            "> /dev/null"
        ]
        #TODO, Error check
        os.system(" ".join(commands))
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
            "> /dev/null"
        ]
        os.system(" ".join(commands))
    return result














