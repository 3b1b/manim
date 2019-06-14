from manimlib.animation.transform import ApplyMethod
from manimlib.camera.three_d_camera import ThreeDCamera
from manimlib.constants import DEGREES
from manimlib.constants import PRODUCTION_QUALITY_CAMERA_CONFIG
from manimlib.mobject.coordinate_systems import ThreeDAxes
from manimlib.mobject.geometry import Line
from manimlib.mobject.three_dimensions import Sphere
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VectorizedPoint
from manimlib.scene.scene import Scene
from manimlib.utils.config_ops import digest_config
from manimlib.utils.config_ops import merge_dicts_recursively


class ThreeDScene(Scene):
    CONFIG = {
        "camera_class": ThreeDCamera,
        "ambient_camera_rotation": None,
        "default_angled_camera_orientation_kwargs": {
            "phi": 70 * DEGREES,
            "theta": -135 * DEGREES,
        }
    }

    def set_camera_orientation(self, phi=None, theta=None, distance=None, gamma=None):
        if phi is not None:
            self.camera.set_phi(phi)
        if theta is not None:
            self.camera.set_theta(theta)
        if distance is not None:
            self.camera.set_distance(distance)
        if gamma is not None:
            self.camera.set_gamma(gamma)

    def begin_ambient_camera_rotation(self, rate=0.02):
        # TODO, use a ValueTracker for rate, so that it
        # can begin and end smoothly
        self.camera.theta_tracker.add_updater(
            lambda m, dt: m.increment_value(rate * dt)
        )
        self.add(self.camera.theta_tracker)

    def stop_ambient_camera_rotation(self):
        self.camera.theta_tracker.clear_updaters()
        self.remove(self.camera.theta_tracker)

    def move_camera(self,
                    phi=None,
                    theta=None,
                    distance=None,
                    gamma=None,
                    frame_center=None,
                    added_anims=[],
                    **kwargs):
        anims = []
        value_tracker_pairs = [
            (phi, self.camera.phi_tracker),
            (theta, self.camera.theta_tracker),
            (distance, self.camera.distance_tracker),
            (gamma, self.camera.gamma_tracker),
        ]
        for value, tracker in value_tracker_pairs:
            if value is not None:
                anims.append(
                    ApplyMethod(tracker.set_value, value, **kwargs)
                )
        if frame_center is not None:
            anims.append(ApplyMethod(
                self.camera.frame_center.move_to,
                frame_center
            ))

        self.play(*anims + added_anims)

    def get_moving_mobjects(self, *animations):
        moving_mobjects = Scene.get_moving_mobjects(self, *animations)
        camera_mobjects = self.camera.get_value_trackers()
        if any([cm in moving_mobjects for cm in camera_mobjects]):
            return self.mobjects
        return moving_mobjects

    def add_fixed_orientation_mobjects(self, *mobjects, **kwargs):
        self.add(*mobjects)
        self.camera.add_fixed_orientation_mobjects(*mobjects, **kwargs)

    def add_fixed_in_frame_mobjects(self, *mobjects):
        self.add(*mobjects)
        self.camera.add_fixed_in_frame_mobjects(*mobjects)

    def remove_fixed_orientation_mobjects(self, *mobjects):
        self.camera.remove_fixed_orientation_mobjects(*mobjects)

    def remove_fixed_in_frame_mobjects(self, *mobjects):
        self.camera.remove_fixed_in_frame_mobjects(*mobjects)

    ##
    def set_to_default_angled_camera_orientation(self, **kwargs):
        config = dict(self.default_camera_orientation_kwargs)
        config.update(kwargs)
        self.set_camera_orientation(**config)


class SpecialThreeDScene(ThreeDScene):
    CONFIG = {
        "cut_axes_at_radius": True,
        "camera_config": {
            "should_apply_shading": True,
            "exponential_projection": True,
        },
        "three_d_axes_config": {
            "num_axis_pieces": 1,
            "number_line_config": {
                "unit_size": 2,
                "tick_frequency": 1,
                "numbers_with_elongated_ticks": [0, 1, 2],
                "stroke_width": 2,
            }
        },
        "sphere_config": {
            "radius": 2,
            "resolution": (24, 48),
        },
        "default_angled_camera_position": {
            "phi": 70 * DEGREES,
            "theta": -110 * DEGREES,
        },
        # When scene is extracted with -l flag, this
        # configuration will override the above configuration.
        "low_quality_config": {
            "camera_config": {
                "should_apply_shading": False,
            },
            "three_d_axes_config": {
                "num_axis_pieces": 1,
            },
            "sphere_config": {
                "resolution": (12, 24),
            }
        }
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        if self.camera_config["pixel_width"] == PRODUCTION_QUALITY_CAMERA_CONFIG["pixel_width"]:
            config = {}
        else:
            config = self.low_quality_config
        config = merge_dicts_recursively(config, kwargs)
        ThreeDScene.__init__(self, **config)

    def get_axes(self):
        axes = ThreeDAxes(**self.three_d_axes_config)
        for axis in axes:
            if self.cut_axes_at_radius:
                p0 = axis.get_start()
                p1 = axis.number_to_point(-1)
                p2 = axis.number_to_point(1)
                p3 = axis.get_end()
                new_pieces = VGroup(
                    Line(p0, p1), Line(p1, p2), Line(p2, p3),
                )
                for piece in new_pieces:
                    piece.shade_in_3d = True
                new_pieces.match_style(axis.pieces)
                axis.pieces.submobjects = new_pieces.submobjects
            for tick in axis.tick_marks:
                tick.add(VectorizedPoint(
                    1.5 * tick.get_center(),
                ))
        return axes

    def get_sphere(self, **kwargs):
        config = merge_dicts_recursively(self.sphere_config, kwargs)
        return Sphere(**config)

    def get_default_camera_position(self):
        return self.default_angled_camera_position

    def set_camera_to_default_position(self):
        self.set_camera_orientation(
            **self.default_angled_camera_position
        )
