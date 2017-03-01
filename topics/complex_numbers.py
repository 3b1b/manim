from helpers import *


from mobject import VGroup
from mobject.tex_mobject import TexMobject, TextMobject
from number_line import NumberPlane
from animation import Animation
from animation.transform import ApplyPointwiseFunction
from animation.simple_animations import Homotopy, ShowCreation
from scene import Scene


class ComplexTransformationScene(Scene):
    CONFIG = {
        "plane_config" : {
            "x_line_frequency" : 1,
            "y_line_frequency" : 1,
            "secondary_line_ratio" : 1,
        },
        "background_fade_factor" : 0.5,
        "x_min" : -int(SPACE_WIDTH),
        "x_max" : int(SPACE_WIDTH),
        "y_min" : -SPACE_HEIGHT,
        "y_max" : SPACE_HEIGHT,
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
    }
    def setup(self):
        self.foreground_mobjects = []
        self.transformable_mobjects = []
        self.add_background_plane()

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
        background = NumberPlane(**self.plane_config).fade(
            self.background_fade_factor
        )
        real_labels = VGroup(*[
            TexMobject(str(x)).shift(
                background.num_pair_to_point((x, 0))
            )
            for x in range(-int(background.x_radius), int(background.x_radius))
        ])
        imag_labels = VGroup(*[
            TexMobject("%di"%y).shift(
                background.num_pair_to_point((0, y))
            )
            for y in range(-int(background.y_radius), int(background.y_radius))
            if y != 0
        ])
        for labels in real_labels, imag_labels:
            for label in labels:
                label.scale_in_place(self.background_label_scale_val)
                label.next_to(label.get_center(), DOWN+LEFT, buff = SMALL_BUFF)
                label.add_background_rectangle()
            background.add(labels)
        self.real_labels = real_labels
        self.imag_labels = imag_labels
        self.add(background)
        self.background = background

    def add_transformable_plane(self, animate = False):
        self.plane_config.update({
            "x_radius" : (self.x_max - self.x_min)/2.,
            "y_radius" : (self.y_max - self.y_min)/2.,
        })
        plane = NumberPlane(**self.plane_config)
        plane.shift(
            (self.x_max+self.x_min)*RIGHT/2.,
            (self.y_max+self.y_min)*UP/2.,
        )
        self.paint_plane(plane)
        if animate:
            self.play(ShowCreation(plane, run_time = 2))
        else:
            self.add(plane)
        self.plane = plane            

    def prepare_for_transformation(self, mob):
        if hasattr(mob, "prepare_for_nonlinear_transform"):
            mob.prepare_for_nonlinear_transform(
                self.num_anchors_to_add_per_line
            )
        #TODO...

    def paint_plane(self, plane):
        if self.use_multicolored_plane:
            for lines in plane.main_lines, plane.secondary_lines:
                lines.gradient_highlight(
                    self.vert_start_color,
                    self.vert_end_color,
                    self.horiz_start_color,
                    self.horiz_end_color,
                )
            plane.axes.gradient_highlight(
                self.horiz_start_color,
                self.vert_start_color
            )

    def z_to_point(self, z):
        z = complex(z)
        return self.background.num_pair_to_point((z.real, z.imag))
        
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
        transformer.target.apply_complex_function(func)
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
            return (output.real, output.imag, z)

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





















