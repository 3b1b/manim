from manimlib.animation.animation import Animation
from manimlib.animation.movement import ComplexHomotopy
from manimlib.animation.transform import MoveToTarget
from manimlib.constants import *
from manimlib.mobject.coordinate_systems import ComplexPlane
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.scene.scene import Scene


# TODO, refactor this full scene
class ComplexTransformationScene(Scene):
    CONFIG = {
        "plane_config": {},
        "background_fade_factor": 0.5,
        "use_multicolored_plane": False,
        "vert_start_color": BLUE,  # TODO
        "vert_end_color": BLUE,
        "horiz_start_color": BLUE,
        "horiz_end_color": BLUE,
        "num_anchors_to_add_per_line": 50,
        "post_transformation_stroke_width": None,
        "default_apply_complex_function_kwargs": {
            "run_time": 5,
        },
        "background_label_scale_val": 0.5,
        "include_coordinate_labels": True,
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
        Scene.add(self, *list(mobjects) + self.foreground_mobjects)

    def play(self, *animations, **kwargs):
        Scene.play(
            self,
            *list(animations) + list(map(Animation, self.foreground_mobjects)),
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

    def get_transformable_plane(self, x_range=None, y_range=None):
        """
        x_range and y_range would be tuples (min, max)
        """
        plane_config = dict(self.plane_config)
        shift_val = ORIGIN
        if x_range is not None:
            x_min, x_max = x_range
            plane_config["x_radius"] = x_max - x_min
            shift_val += (x_max + x_min) * RIGHT / 2.
        if y_range is not None:
            y_min, y_max = y_range
            plane_config["y_radius"] = y_max - y_min
            shift_val += (y_max + y_min) * UP / 2.
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
        # TODO...

    def paint_plane(self, plane):
        for lines in planes, plane.secondary_lines:
            lines.set_color_by_gradient(
                self.vert_start_color,
                self.vert_end_color,
                self.horiz_start_color,
                self.horiz_end_color,
            )
        # plane.axes.set_color_by_gradient(
        #     self.horiz_start_color,
        #     self.vert_start_color
        # )

    def z_to_point(self, z):
        return self.background.number_to_point(z)

    def get_transformer(self, **kwargs):
        transform_kwargs = dict(self.default_apply_complex_function_kwargs)
        transform_kwargs.update(kwargs)
        transformer = VGroup()
        if hasattr(self, "plane"):
            self.prepare_for_transformation(self.plane)
            transformer.add(self.plane)
        transformer.add(*self.transformable_mobjects)
        return transformer, transform_kwargs

    def apply_complex_function(self, func, added_anims=[], **kwargs):
        transformer, transform_kwargs = self.get_transformer(**kwargs)
        transformer.generate_target()
        # Rescale, apply function, scale back
        transformer.target.shift(-self.background.get_center_point())
        transformer.target.scale(1. / self.background.unit_size)
        transformer.target.apply_complex_function(func)
        transformer.target.scale(self.background.unit_size)
        transformer.target.shift(self.background.get_center_point())
        #

        for mob in transformer.target[0].family_members_with_points():
            mob.make_smooth()
        if self.post_transformation_stroke_width is not None:
            transformer.target.set_stroke(
                width=self.post_transformation_stroke_width)
        self.play(
            MoveToTarget(transformer, **transform_kwargs),
            *added_anims
        )

    def apply_complex_homotopy(self, complex_homotopy, added_anims=[], **kwargs):
        transformer, transform_kwargs = self.get_transformer(**kwargs)

        # def homotopy(x, y, z, t):
        #     output = complex_homotopy(complex(x, y), t)
        #     rescaled_output = self.z_to_point(output)
        #     return (rescaled_output.real, rescaled_output.imag, z)

        self.play(
            ComplexHomotopy(complex_homotopy, transformer, **transform_kwargs),
            *added_anims
        )
