from vectorized_mobject import VMobject
from svg_mobject import SVGMobject, VMobjectFromSVGPathstring
from topics.geometry import BackgroundRectangle
from helpers import *
import collections

TEX_MOB_SCALE_FACTOR = 0.05
TEXT_MOB_SCALE_FACTOR = 0.05


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
        "arg_separator"     : " ",
        "enforce_new_line_structure" : False,
        "initial_scale_factor" : TEX_MOB_SCALE_FACTOR,
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
        if self.enforce_new_line_structure:
            result = result.replace("\n", " \\\\ \n ")
        result = " ".join([self.alignment, result])
        result = result.strip()
        return result

    def get_tex_string(self):
        return self.tex_string

    def handle_multiple_args(self):
        new_submobjects = []
        curr_index = 0
        self.expression_parts = list(self.args)
        for expr in self.args:
            model = TexMobject(expr, **self.CONFIG)
            new_index = curr_index + len(model.submobjects)
            new_submobjects.append(VMobject(
                *self.submobjects[curr_index:new_index]
            ))
            curr_index = new_index
        self.submobjects = new_submobjects
        return self

    def highlight_by_tex(self, tex, color):
        if not hasattr(self, "expression_parts"):
            if tex == self.get_tex_string():
                self.highlight(color)
            return self
        for submob, part_tex in zip(self.split(), self.expression_parts):
            if part_tex == tex:
                submob.highlight(color)
        return self

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
        "initial_scale_factor" : TEXT_MOB_SCALE_FACTOR,
        "enforce_new_line_structure" : True,
        "alignment" : "\\centering",
    }



class Brace(TexMobject):
    CONFIG = {
        "buff" : 0.2,
    }
    TEX_STRING = "\\underbrace{%s}"%(3*"\\qquad")
    def __init__(self, mobject, direction = DOWN, **kwargs):
        digest_config(self, kwargs, locals())
        TexMobject.__init__(self, self.TEX_STRING, **kwargs)
        angle = -np.arctan2(*direction[:2]) + np.pi
        mobject.rotate(-angle)
        left  = mobject.get_corner(DOWN+LEFT)
        right = mobject.get_corner(DOWN+RIGHT)
        self.stretch_to_fit_width(right[0]-left[0])
        self.shift(left - self.get_corner(UP+LEFT) + self.buff*DOWN)
        for mob in mobject, self:
            mob.rotate(angle)

    def put_at_tip(self, mob, **kwargs):
        mob.next_to(self, self.direction, **kwargs)
        return self

    def get_text(self, *text, **kwargs):
        text_mob = TextMobject(*text)
        self.put_at_tip(text_mob, **kwargs)
        return text_mob


    
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














