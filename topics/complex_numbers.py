from helpers import *


from mobject import VGroup
from mobject.tex_mobject import TexMobject, TextMobject
from number_line import NumberPlane
from animation import Animation
from animation.transform import ApplyPointwiseFunction, MoveToTarget
from animation.simple_animations import Homotopy, ShowCreation, \
    SmoothedVectorizedHomotopy
from scene import Scene


class ComplexTransformationScene(Scene):
    CONFIG = {
        "plane_config" : {},
        "background_fade_factor" : 0.5,
        "use_multicolored_plane" : False,
        "vert_start_color" : BLUE, ##TODO
        "vert_end_color" : BLUE,
        "horiz_start_color" : BLUE,
        "horiz_end_color" : BLUE,
        "num_anchors_to_add_per_line" : 50,
        "post_transformation_stroke_width" : None,
        "default_apply_complex_function_kwargs" : {
            "run_time" : 5,
        },
        "background_label_scale_val" : 0.5,
        "include_coordinate_labels" : True,
    }
    def setup(self):
        self.foreground_mobjects = []
        self.transformable_mobjects = []
        self.add_background_plane()
        if self.include_coordinate_labels:
            self.add_coordinate_labels()

    def add_foreground_mobject(self, mobject):
        self.add_foreground_mobjects(mobject)

    def add_transformable_mobjects(self, *mobjects):
        self.transformable_mobjects += list(mobjects)
        self.add(*mobjects)

    def add_foreground_mobjects(self, *mobjects):
        self.foreground_mobjects += list(mobjects)
        Scene.add(self, *mobjects)

    def add(self, *mobjects):
        Scene.add(self, *list(mobjects)+self.foreground_mobjects)

    def play(self, *animations, **kwargs):
        Scene.play(
            self,
            *list(animations)+map(Animation, self.foreground_mobjects),
            **kwargs
        )

    def add_background_plane(self):
        background = ComplexPlane(**self.plane_config)
        background.fade(self.background_fade_factor)
        self.add(background)
        self.background = background

    def add_coordinate_labels(self):
        self.background.add_coordinates()
        self.add(self.background)

    def add_transformable_plane(self, **kwargs):
        self.plane = self.get_transformable_plane()
        self.add(self.plane)

    def get_transformable_plane(self, x_range = None, y_range = None):
        """
        x_range and y_range would be tuples (min, max)
        """
        plane_config = dict(self.plane_config)
        shift_val = ORIGIN
        if x_range is not None:
            x_min, x_max = x_range
            plane_config["x_radius"] = x_max - x_min
            shift_val += (x_max+x_min)*RIGHT/2.
        if y_range is not None:
            y_min, y_max = y_range
            plane_config["y_radius"] = y_max - y_min
            shift_val += (y_max+y_min)*UP/2.
        plane = ComplexPlane(**plane_config)
        plane.shift(shift_val)
        if self.use_multicolored_plane:
            self.paint_plane(plane)
        return plane

    def prepare_for_transformation(self, mob):
        if hasattr(mob, "prepare_for_nonlinear_transform"):
            mob.prepare_for_nonlinear_transform(
                self.num_anchors_to_add_per_line
            )
        #TODO...

    def paint_plane(self, plane):
        for lines in plane.main_lines, plane.secondary_lines:
            lines.gradient_highlight(
                self.vert_start_color,
                self.vert_end_color,
                self.horiz_start_color,
                self.horiz_end_color,
            )
        # plane.axes.gradient_highlight(
        #     self.horiz_start_color,
        #     self.vert_start_color
        # )

    def z_to_point(self, z):
        return self.background.number_to_point(z)
        
    def get_transformer(self, **kwargs):
        transform_kwargs = dict(self.default_apply_complex_function_kwargs)
        transform_kwargs.update(kwargs)
        plane = self.plane
        self.prepare_for_transformation(plane)
        transformer = VGroup(
            plane, *self.transformable_mobjects
        )        
        return transformer, transform_kwargs


    def apply_complex_function(self, func, added_anims = [], **kwargs):
        transformer, transform_kwargs = self.get_transformer(**kwargs)
        transformer.generate_target()
        #Rescale, apply function, scale back
        transformer.target.shift(-self.background.get_center_point())
        transformer.target.scale(1./self.background.unit_size)
        transformer.target.apply_complex_function(func)
        transformer.target.scale(self.background.unit_size)
        transformer.target.shift(self.background.get_center_point())
        #

        for mob in transformer.target[0].family_members_with_points():
            mob.make_smooth()
        if self.post_transformation_stroke_width is not None:
            transformer.target.set_stroke(width = self.post_transformation_stroke_width)
        self.play(
            MoveToTarget(transformer, **transform_kwargs),
            *added_anims
        )

    def apply_complex_homotopy(self, complex_homotopy, added_anims = [], **kwargs):
        transformer, transform_kwargs = self.get_transformer(**kwargs)
        def homotopy(x, y, z, t):
            output = complex_homotopy(complex(x, y), t)
            rescaled_output = self.z_to_point(output)
            return (rescaled_output.real, rescaled_output.imag, z)

        self.play(
            SmoothedVectorizedHomotopy(
                homotopy, transformer,
                **transform_kwargs
            ),
            *added_anims
        )

##### Unsure about what comes under here...

def complex_string(complex_num):
    return filter(lambda c : c not in "()", str(complex_num))

class ComplexPlane(NumberPlane):
    CONFIG = {
        "color"                : BLUE,
        "unit_size"            : 1,
        "line_frequency"       : 1,
        "faded_line_frequency" : 0.5,
        "number_scale_factor"  : 0.5,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        kwargs.update({
            "x_unit_size" : self.unit_size,
            "y_unit_size" : self.unit_size,
            "x_line_frequency" : self.line_frequency,
            "x_faded_line_frequency" : self.faded_line_frequency,
            "y_line_frequency" : self.line_frequency,
            "y_faded_line_frequency" : self.faded_line_frequency,
        })
        NumberPlane.__init__(self, **kwargs)

    def number_to_point(self, number):
        number = complex(number)
        return self.coords_to_point(number.real, number.imag)

    def point_to_number(self, point):
        x, y = self.point_to_coords(point)
        return complex(x, y)

    def get_coordinate_labels(self, *numbers):
        result = VGroup()
        nudge = 0.1*(DOWN+RIGHT)
        if len(numbers) == 0:
            numbers = range(-int(self.x_radius), int(self.x_radius)+1)
            numbers += [
                complex(0, y)
                for y in range(-int(self.y_radius), int(self.y_radius)+1)
            ]
        for number in numbers:
            point = self.number_to_point(number)
            num_str = str(number).replace("j", "i")
            if num_str.startswith("0"):
                num_str = "0"
            elif num_str in ["1i", "-1i"]:
                num_str = num_str.replace("1", "")
            num_mob = TexMobject(num_str)
            num_mob.add_background_rectangle()
            num_mob.scale(self.number_scale_factor)
            if complex(number).imag != 0:
                vect = DOWN+RIGHT
            else:
                vect = DOWN+RIGHT
            num_mob.next_to(point, vect, SMALL_BUFF)
            result.add(num_mob)
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
        def homotopy(event):
            x, y, z, t = event
            c = complex_homotopy((complex(x, y), t))
            return (c.real, c.imag, z)
        Homotopy.__init__(self, homotopy, mobject, *args, **kwargs)





















