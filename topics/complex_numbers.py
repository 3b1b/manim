from helpers import *

from number_line import NumberPlane
from animation.transform import ApplyPointwiseFunction
from animation.simple_animations import Homotopy
from scene import Scene


def complex_string(complex_num):
    return filter(lambda c : c not in "()", str(complex_num))

class ComplexPlane(NumberPlane):
    CONFIG = {
        "color"                 : GREEN,
        "unit_to_spatial_width" : 1,
        "line_frequency"        : 1,
        "faded_line_frequency"  : 0.5,
        "number_at_center"      : complex(0),
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        kwargs.update({
            "x_unit_to_spatial_width"  : self.unit_to_spatial_width,
            "y_unit_to_spatial_height" : self.unit_to_spatial_width,
            "x_line_frequency"         : self.line_frequency,
            "x_faded_line_frequency"   : self.faded_line_frequency,
            "y_line_frequency"         : self.line_frequency,
            "y_faded_line_frequency"   : self.faded_line_frequency,
            "num_pair_at_center"       : (self.number_at_center.real, 
                                          self.number_at_center.imag),
        })
        NumberPlane.__init__(self, **kwargs)

    def number_to_point(self, number):
        number = complex(number)
        return self.num_pair_to_point((number.real, number.imag))

    def get_coordinate_labels(self, *numbers):
        result = []
        nudge = 0.1*(DOWN+RIGHT)
        if len(numbers) == 0:
            numbers = range(-int(self.x_radius), int(self.x_radius))
            numbers += [
                complex(0, y)
                for y in range(-int(self.y_radius), int(self.y_radius))
            ]
        for number in numbers:
            point = self.number_to_point(number)
            if number == 0:
                num_str = "0"
            else:
                num_str = str(number).replace("j", "i")
            num = TexMobject(num_str)
            num.scale(self.number_scale_factor)
            num.shift(point-num.get_corner(UP+LEFT)+nudge)
            result.append(num)
        return result

    def add_coordinates(self, *numbers):
        self.add(*self.get_coordinate_labels(*numbers))
        return self

    def add_spider_web(self, circle_freq = 1, angle_freq = np.pi/6):
        self.fade(self.fade_factor)
        config = {
            "color" : self.color,
            "density" : self.density,
        }
        for radius in np.arange(circle_freq, SPACE_WIDTH, circle_freq):
            self.add(Circle(radius = radius, **config))
        for angle in np.arange(0, 2*np.pi, angle_freq):
            end_point = np.cos(angle)*RIGHT + np.sin(angle)*UP
            end_point *= SPACE_WIDTH
            self.add(Line(ORIGIN, end_point, **config))
        return self


class ComplexFunction(ApplyPointwiseFunction):
    def __init__(self, function, mobject = ComplexPlane, **kwargs):
        if "path_func" not in kwargs:
            self.path_func = path_along_arc(
                np.log(function(complex(1))).imag
            )
        ApplyPointwiseFunction.__init__(
            self,
            lambda (x, y, z) : complex_to_R3(function(complex(x, y))),
            instantiate(mobject),
            **kwargs
        )

class ComplexHomotopy(Homotopy):
    def __init__(self, complex_homotopy, mobject = ComplexPlane, **kwargs):
        """
        Complex Hootopy a function Cx[0, 1] to C
        """
        def homotopy((x, y, z, t)):
            c = complex_homotopy((complex(x, y), t))
            return (c.real, c.imag, z)
        Homotopy.__init__(self, homotopy, mobject, *args, **kwargs)


class ComplexMultiplication(Scene):
    @staticmethod
    def args_to_string(multiplier, mark_one = False):
        num_str = complex_string(multiplier)
        arrow_str = "MarkOne" if mark_one else ""
        return num_str + arrow_str

    @staticmethod
    def string_to_args(arg_string):
        parts = arg_string.split()
        multiplier = complex(parts[0])
        mark_one = len(parts) > 1 and parts[1] == "MarkOne"
        return (multiplier, mark_one)

    def construct(self, multiplier, mark_one = False, **plane_config):
        norm = np.linalg.norm(multiplier)
        arg  = np.log(multiplier).imag
        plane_config["faded_line_frequency"] = 0
        plane_config.update(DEFAULT_PLANE_CONFIG)
        if norm > 1 and "density" not in plane_config:
            plane_config["density"] = norm*DEFAULT_POINT_DENSITY_1D
        if "radius" not in plane_config:
            radius = SPACE_WIDTH
            if norm > 0 and norm < 1:
                radius /= norm
        else:
            radius = plane_config["radius"]
        plane_config["x_radius"] = plane_config["y_radius"] = radius            
        plane = ComplexPlane(**plane_config)
        self.plane = plane
        self.add(plane)
        # plane.add_spider_web()
        self.anim_config = {
            "run_time" : 2.0,
            "path_func" : path_along_arc(arg)
        }

        plane_config["faded_line_frequency"] = 0.5
        background = ComplexPlane(color = "grey", **plane_config)
        # background.add_spider_web()
        labels = background.get_coordinate_labels()
        self.paint_into_background(background, *labels)
        self.mobjects_to_move_without_molding = []
        if mark_one:
            self.draw_dot("1", 1, True)
            self.draw_dot("z", multiplier)


        self.mobjects_to_multiply = [plane]

        self.additional_animations = []        
        self.multiplier = multiplier
        if self.__class__ == ComplexMultiplication:
            self.apply_multiplication()

    def draw_dot(self, tex_string, value, move_dot = False):
        dot = Dot(
            self.plane.number_to_point(value),
            radius = 0.1*self.plane.unit_to_spatial_width, 
            color = BLUE if value == 1 else YELLOW
        )
        label = TexMobject(tex_string)
        label.shift(dot.get_center()+1.5*UP+RIGHT)
        arrow = Arrow(label, dot)
        self.add(label)
        self.play(ShowCreation(arrow))
        self.play(ShowCreation(dot))
        self.dither()

        self.remove(label, arrow)
        if move_dot:
            self.mobjects_to_move_without_molding.append(dot)
        return dot


    def apply_multiplication(self):
        def func((x, y, z)):
            complex_num = self.multiplier*complex(x, y)
            return (complex_num.real, complex_num.imag, z)
        mobjects = self.mobjects_to_multiply
        mobjects += self.mobjects_to_move_without_molding
        mobjects += [anim.mobject for anim in self.additional_animations]                    


        self.add(*mobjects)
        full_multiplications = [
            ApplyMethod(mobject.apply_function, func, **self.anim_config)
            for mobject in self.mobjects_to_multiply
        ]
        movements_with_plane = [
            ApplyMethod(
                mobject.shift, 
                func(mobject.get_center())-mobject.get_center(),
                **self.anim_config            
            )
            for mobject in self.mobjects_to_move_without_molding
        ]
        self.dither()
        self.play(*reduce(op.add, [
            full_multiplications,
            movements_with_plane,
            self.additional_animations
        ]))
        self.dither()
