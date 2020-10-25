"""A scene suitable for rendering three-dimensional objects and animations."""

__all__ = ["ThreeDScene", "SpecialThreeDScene"]


from .. import config
from ..animation.transform import ApplyMethod
from ..camera.three_d_camera import ThreeDCamera
from ..constants import DEGREES
from ..mobject.coordinate_systems import ThreeDAxes
from ..mobject.geometry import Line
from ..mobject.three_dimensions import Sphere
from ..mobject.types.vectorized_mobject import VGroup
from ..mobject.types.vectorized_mobject import VectorizedPoint
from ..mobject.value_tracker import ValueTracker
from ..scene.scene import Scene
from ..utils.config_ops import digest_config
from ..utils.config_ops import merge_dicts_recursively
import numpy as np


class ThreeDScene(Scene):
    """
    This is a Scene, with special configurations and properties that
    make it suitable for Three Dimensional Scenes.
    """

    CONFIG = {
        "camera_class": ThreeDCamera,
        "ambient_camera_rotation": None,
        "default_angled_camera_orientation_kwargs": {
            "phi": 70 * DEGREES,
            "theta": -135 * DEGREES,
        },
    }

    def set_camera_orientation(self, phi=None, theta=None, distance=None, gamma=None):
        """
        This method sets the orientation of the camera in the scene.

        Parameters
        ----------
        phi : int or float, optional
            The polar angle i.e the angle between Z_AXIS and Camera through ORIGIN in radians.

        theta : int or float, optional
            The azimuthal angle i.e the angle that spins the camera around the Z_AXIS.

        distance : int or float, optional
            The radial distance between ORIGIN and Camera.

        gamma : int or float, optional
            The rotation of the camera about the vector from the ORIGIN to the Camera.
        """
        if phi is not None:
            self.renderer.camera.set_phi(phi)
        if theta is not None:
            self.renderer.camera.set_theta(theta)
        if distance is not None:
            self.renderer.camera.set_distance(distance)
        if gamma is not None:
            self.renderer.camera.set_gamma(gamma)

    def begin_ambient_camera_rotation(self, rate=0.02):
        """
        This method begins an ambient rotation of the camera about the Z_AXIS,
        in the anticlockwise direction

        Parameters
        ----------
        rate : int or float, optional
            The rate at which the camera should rotate about the Z_AXIS.
            Negative rate means clockwise rotation.
        """
        # TODO, use a ValueTracker for rate, so that it
        # can begin and end smoothly
        self.renderer.camera.theta_tracker.add_updater(
            lambda m, dt: m.increment_value(rate * dt)
        )
        self.add(self.renderer.camera.theta_tracker)

    def stop_ambient_camera_rotation(self):
        """
        This method stops all ambient camera rotation.
        """
        self.renderer.camera.theta_tracker.clear_updaters()
        self.remove(self.renderer.camera.theta_tracker)

    def begin_3dillusion_camera_rotation(
        self, rate=1, origin_theta=-60 * DEGREES, origin_phi=75 * DEGREES
    ):
        val_tracker_theta = ValueTracker(0)

        def uptate_theta(m, dt):
            val_tracker_theta.increment_value(dt * rate)
            val_for_left_right = 0.2 * np.sin(val_tracker_theta.get_value())
            return m.set_value(origin_theta + val_for_left_right)

        self.renderer.camera.theta_tracker.add_updater(uptate_theta)
        self.add(self.renderer.camera.theta_tracker)

        val_tracker_phi = ValueTracker(0)

        def update_phi(m, dt):
            val_tracker_phi.increment_value(dt * rate)
            val_for_up_down = 0.1 * np.cos(val_tracker_phi.get_value())
            return m.set_value(origin_phi + val_for_up_down)

        self.renderer.camera.phi_tracker.add_updater(update_phi)
        self.add(self.renderer.camera.phi_tracker)

    def stop_3dillusion_camera_rotation(self):
        """
        This method stops all illusion camera rotations.
        """
        self.renderer.camera.theta_tracker.clear_updaters()
        self.remove(self.renderer.camera.theta_tracker)
        self.renderer.camera.phi_tracker.clear_updaters()
        self.remove(self.renderer.camera.phi_tracker)

    def move_camera(
        self,
        phi=None,
        theta=None,
        distance=None,
        gamma=None,
        frame_center=None,
        added_anims=[],
        **kwargs,
    ):
        """
        This method animates the movement of the camera
        to the given spherical coordinates.

        Parameters
        ----------
        phi : int or float, optional
            The polar angle i.e the angle between Z_AXIS and Camera through ORIGIN in radians.

        theta : int or float, optional
            The azimuthal angle i.e the angle that spins the camera around the Z_AXIS.

        distance : int or float, optional
            The radial distance between ORIGIN and Camera.

        gamma : int or float, optional
            The rotation of the camera about the vector from the ORIGIN to the Camera.

        frame_center : list, tuple or np.array, optional
            The new center of the camera frame in cartesian coordinates

        added_anims : list, optional
            Any other animations to be played at the same time.

        """
        anims = []
        value_tracker_pairs = [
            (phi, self.renderer.camera.phi_tracker),
            (theta, self.renderer.camera.theta_tracker),
            (distance, self.renderer.camera.distance_tracker),
            (gamma, self.renderer.camera.gamma_tracker),
        ]
        for value, tracker in value_tracker_pairs:
            if value is not None:
                anims.append(ApplyMethod(tracker.set_value, value, **kwargs))
        if frame_center is not None:
            anims.append(
                ApplyMethod(self.renderer.camera.frame_center.move_to, frame_center)
            )

        self.play(*anims + added_anims)

    def get_moving_mobjects(self, *animations):
        """
        This method returns a list of all of the Mobjects in the Scene that
        are moving, that are also in the animations passed.

        Parameters
        ----------
        *animations : Animation
            The animations whose mobjects will be checked.
        """
        moving_mobjects = Scene.get_moving_mobjects(self, *animations)
        camera_mobjects = self.renderer.camera.get_value_trackers()
        if any([cm in moving_mobjects for cm in camera_mobjects]):
            return self.mobjects
        return moving_mobjects

    def add_fixed_orientation_mobjects(self, *mobjects, **kwargs):
        """
        This method is used to prevent the rotation and tilting
        of mobjects as the camera moves around. The mobject can
        still move in the x,y,z directions, but will always be
        at the angle (relative to the camera) that it was at
        when it was passed through this method.)

        Parameters
        ----------
        *mobjects : Mobject
            The Mobject(s) whose orientation must be fixed.

        **kwargs
            Some valid kwargs are
                use_static_center_func : bool
                center_func : function
        """
        self.add(*mobjects)
        self.renderer.camera.add_fixed_orientation_mobjects(*mobjects, **kwargs)

    def add_fixed_in_frame_mobjects(self, *mobjects):
        """
        This method is used to prevent the rotation and movement
        of mobjects as the camera moves around. The mobject is
        essentially overlayed, and is not impacted by the camera's
        movement in any way.

        Parameters
        ----------
        *mobjects : Mobjects
            The Mobjects whose orientation must be fixed.
        """
        self.add(*mobjects)
        self.renderer.camera.add_fixed_in_frame_mobjects(*mobjects)

    def remove_fixed_orientation_mobjects(self, *mobjects):
        """
        This method "unfixes" the orientation of the mobjects
        passed, meaning they will no longer be at the same angle
        relative to the camera. This only makes sense if the
        mobject was passed through add_fixed_orientation_mobjects first.

        Parameters
        ----------
        *mobjects : Mobjects
            The Mobjects whose orientation must be unfixed.
        """
        self.renderer.camera.remove_fixed_orientation_mobjects(*mobjects)

    def remove_fixed_in_frame_mobjects(self, *mobjects):
        """
         This method undoes what add_fixed_in_frame_mobjects does.
         It allows the mobject to be affected by the movement of
         the camera.

        Parameters
        ----------
        *mobjects : Mobjects
            The Mobjects whose position and orientation must be unfixed.
        """
        self.renderer.camera.remove_fixed_in_frame_mobjects(*mobjects)

    ##
    def set_to_default_angled_camera_orientation(self, **kwargs):
        """
        This method sets the default_angled_camera_orientation to the
        keyword arguments passed, and sets the camera to that orientation.

        Parameters
        ----------
        **kwargs
            Some recognised kwargs are phi, theta, distance, gamma,
            which have the same meaning as the parameters in set_camera_orientation.
        """
        config = dict(self.default_camera_orientation_kwargs)
        config.update(kwargs)
        self.set_camera_orientation(**config)


class SpecialThreeDScene(ThreeDScene):
    """An extension of :class:`ThreeDScene` with more settings.

    It has some extra configuration for axes, spheres,
    and an override for low quality rendering. Further key differences
    are:

    * The camera shades applicable 3DMobjects by default,
      except if rendering in low quality.
    * Some default params for Spheres and Axes have been added.

    """

    CONFIG = {
        "cut_axes_at_radius": True,
        "camera_config": {"should_apply_shading": True, "exponential_projection": True},
        "three_d_axes_config": {
            "num_axis_pieces": 1,
            "axis_config": {
                "unit_size": 2,
                "tick_frequency": 1,
                "numbers_with_elongated_ticks": [0, 1, 2],
                "stroke_width": 2,
            },
        },
        "sphere_config": {"radius": 2, "resolution": (24, 48)},
        "default_angled_camera_position": {
            "phi": 70 * DEGREES,
            "theta": -110 * DEGREES,
        },
        # When scene is extracted with -l flag, this
        # configuration will override the above configuration.
        "low_quality_config": {
            "camera_config": {"should_apply_shading": False},
            "three_d_axes_config": {"num_axis_pieces": 1},
            "sphere_config": {"resolution": (12, 24)},
        },
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        if self.renderer.camera_config["pixel_width"] == config["pixel_width"]:
            config = {}
        else:
            config = self.low_quality_config
        config = merge_dicts_recursively(config, kwargs)
        ThreeDScene.__init__(self, **config)

    def get_axes(self):
        """Return a set of 3D axes.

        Returns
        -------
        :class:`.ThreeDAxes`
            A set of 3D axes.
        """
        axes = ThreeDAxes(**self.three_d_axes_config)
        for axis in axes:
            if self.cut_axes_at_radius:
                p0 = axis.get_start()
                p1 = axis.number_to_point(-1)
                p2 = axis.number_to_point(1)
                p3 = axis.get_end()
                new_pieces = VGroup(Line(p0, p1), Line(p1, p2), Line(p2, p3))
                for piece in new_pieces:
                    piece.shade_in_3d = True
                new_pieces.match_style(axis.pieces)
                axis.pieces.submobjects = new_pieces.submobjects
            for tick in axis.tick_marks:
                tick.add(VectorizedPoint(1.5 * tick.get_center()))
        return axes

    def get_sphere(self, **kwargs):
        """
        Returns a sphere with the passed keyword arguments as properties.

        Parameters
        ----------
        **kwargs
            Any valid parameter of :class:`.Sphere` or :class:`.ParametricSurface`.

        Returns
        -------
        :class:`.Sphere`
            The sphere object.
        """
        config = merge_dicts_recursively(self.sphere_config, kwargs)
        return Sphere(**config)

    def get_default_camera_position(self):
        """
        Returns the default_angled_camera position.

        Returns
        -------
        dict
            Dictionary of phi, theta, distance, and gamma.
        """
        return self.default_angled_camera_position

    def set_camera_to_default_position(self):
        """
        Sets the camera to its default position.
        """
        self.set_camera_orientation(**self.default_angled_camera_position)
