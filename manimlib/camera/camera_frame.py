from __future__ import annotations

import math
import warnings

import numpy as np
from scipy.spatial.transform import Rotation
from pyrr import Matrix44

from manimlib.constants import DEGREES, RADIANS
from manimlib.constants import FRAME_SHAPE
from manimlib.constants import DOWN, LEFT, ORIGIN, OUT, RIGHT, UP
from manimlib.constants import PI
from manimlib.mobject.mobject import Mobject
from manimlib.utils.space_ops import normalize
from manimlib.utils.simple_functions import clip

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.typing import Vect3


class CameraFrame(Mobject):
    def __init__(
        self,
        frame_shape: tuple[float, float] = FRAME_SHAPE,
        center_point: Vect3 = ORIGIN,
        # Field of view in the y direction
        fovy: float = 45 * DEGREES,
        euler_axes: str = "zxz",
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.uniforms["orientation"] = Rotation.identity().as_quat()
        self.uniforms["fovy"] = fovy

        self.default_orientation = Rotation.identity()
        self.view_matrix = np.identity(4)
        self.camera_location = OUT  # This will be updated by set_points
        self.euler_axes = euler_axes

        self.set_points(np.array([ORIGIN, LEFT, RIGHT, DOWN, UP]))
        self.set_width(frame_shape[0], stretch=True)
        self.set_height(frame_shape[1], stretch=True)
        self.move_to(center_point)

    def set_orientation(self, rotation: Rotation):
        self.uniforms["orientation"][:] = rotation.as_quat()
        return self

    def get_orientation(self):
        return Rotation.from_quat(self.uniforms["orientation"])

    def make_orientation_default(self):
        self.default_orientation = self.get_orientation()
        return self

    def to_default_state(self):
        self.set_shape(*FRAME_SHAPE)
        self.center()
        self.set_orientation(self.default_orientation)
        return self

    def get_euler_angles(self) -> np.ndarray:
        orientation = self.get_orientation()
        if np.isclose(orientation.as_quat(), [0, 0, 0, 1]).all():
            return np.zeros(3)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)  # Ignore UserWarnings
            angles = orientation.as_euler(self.euler_axes)[::-1]
        # Handle Gimble lock case
        if np.isclose(angles[1], 0, atol=1e-2):
            angles[0] = angles[0] + angles[2]
            angles[2] = 0
        return angles

    def get_theta(self):
        return self.get_euler_angles()[0]

    def get_phi(self):
        return self.get_euler_angles()[1]

    def get_gamma(self):
        return self.get_euler_angles()[2]

    def get_scale(self):
        return self.get_height() / FRAME_SHAPE[1]

    def get_inverse_camera_rotation_matrix(self):
        return self.get_orientation().as_matrix().T

    def get_view_matrix(self, refresh=False):
        """
        Returns a 4x4 for the affine transformation mapping a point
        into the camera's internal coordinate system
        """
        if self._data_has_changed:
            shift = np.identity(4)
            rotation = np.identity(4)
            scale_mat = np.identity(4)

            shift[:3, 3] = -self.get_center()
            rotation[:3, :3] = self.get_inverse_camera_rotation_matrix()
            scale = self.get_scale()
            if scale > 0:
                scale_mat[:3, :3] /= self.get_scale()

            self.view_matrix = np.dot(scale_mat, np.dot(rotation, shift))

        return self.view_matrix

    def get_inv_view_matrix(self):
        return np.linalg.inv(self.get_view_matrix())

    @Mobject.affects_data
    def interpolate(self, *args, **kwargs):
        super().interpolate(*args, **kwargs)

    @Mobject.affects_data
    def rotate(self, angle: float, axis: np.ndarray = OUT, **kwargs):
        rot = Rotation.from_rotvec(angle * normalize(axis))
        self.set_orientation(rot * self.get_orientation())
        return self

    def set_euler_angles(
        self,
        theta: float | None = None,
        phi: float | None = None,
        gamma: float | None = None,
        units: float = RADIANS
    ):
        eulers = self.get_euler_angles()  # theta, phi, gamma
        for i, var in enumerate([theta, phi, gamma]):
            if var is not None:
                eulers[i] = var * units
        if all(eulers == 0):
            rot = Rotation.identity()
        else:
            rot = Rotation.from_euler(self.euler_axes, eulers[::-1])
        self.set_orientation(rot)
        return self

    def increment_euler_angles(
        self,
        dtheta: float = 0,
        dphi: float = 0,
        dgamma: float = 0,
        units: float = RADIANS
    ):
        angles = self.get_euler_angles()
        new_angles = angles + np.array([dtheta, dphi, dgamma]) * units
        new_angles[1] = clip(new_angles[1], 0, PI)  # Limit range for phi
        new_rot = Rotation.from_euler(self.euler_axes, new_angles[::-1])
        self.set_orientation(new_rot)
        return self

    def set_euler_axes(self, seq: str):
        self.euler_axes = seq

    def reorient(
        self,
        theta_degrees: float | None = None,
        phi_degrees: float | None = None,
        gamma_degrees: float | None = None,
        center: Vect3 | tuple[float, float, float] | None = None,
        height: float | None = None
    ):
        """
        Shortcut for set_euler_angles, defaulting to taking
        in angles in degrees
        """
        self.set_euler_angles(theta_degrees, phi_degrees, gamma_degrees, units=DEGREES)
        if center is not None:
            self.move_to(np.array(center))
        if height is not None:
            self.set_height(height)
        return self

    def set_theta(self, theta: float):
        return self.set_euler_angles(theta=theta)

    def set_phi(self, phi: float):
        return self.set_euler_angles(phi=phi)

    def set_gamma(self, gamma: float):
        return self.set_euler_angles(gamma=gamma)

    def increment_theta(self, dtheta: float, units=RADIANS):
        self.increment_euler_angles(dtheta=dtheta, units=units)
        return self

    def increment_phi(self, dphi: float, units=RADIANS):
        self.increment_euler_angles(dphi=dphi, units=units)
        return self

    def increment_gamma(self, dgamma: float, units=RADIANS):
        self.increment_euler_angles(dgamma=dgamma, units=units)
        return self

    def add_ambient_rotation(self, angular_speed=1 * DEGREES):
        self.add_updater(lambda m, dt: m.increment_theta(angular_speed * dt))
        return self

    @Mobject.affects_data
    def set_focal_distance(self, focal_distance: float):
        self.uniforms["fovy"] = 2 * math.atan(0.5 * self.get_height() / focal_distance)
        return self

    @Mobject.affects_data
    def set_field_of_view(self, field_of_view: float):
        self.uniforms["fovy"] = field_of_view
        return self

    def get_shape(self):
        return (self.get_width(), self.get_height())

    def get_aspect_ratio(self):
        width, height = self.get_shape()
        return width / height

    def get_center(self) -> np.ndarray:
        # Assumes first point is at the center
        return self.get_points()[0]

    def get_width(self) -> float:
        points = self.get_points()
        return points[2, 0] - points[1, 0]

    def get_height(self) -> float:
        points = self.get_points()
        return points[4, 1] - points[3, 1]

    def get_focal_distance(self) -> float:
        return 0.5 * self.get_height() / math.tan(0.5 * self.uniforms["fovy"])

    def get_field_of_view(self) -> float:
        return self.uniforms["fovy"]

    def get_implied_camera_location(self) -> np.ndarray:
        if self._data_has_changed:
            to_camera = self.get_inverse_camera_rotation_matrix()[2]
            dist = self.get_focal_distance()
            self.camera_location = self.get_center() + dist * to_camera
        return self.camera_location

    def to_fixed_frame_point(self, point: Vect3, relative: bool = False):
        view = self.get_view_matrix()
        point4d = [*point, 0 if relative else 1]
        return np.dot(point4d, view.T)[:3]

    def from_fixed_frame_point(self, point: Vect3, relative: bool = False):
        inv_view = self.get_inv_view_matrix()
        point4d = [*point, 0 if relative else 1]
        return np.dot(point4d, inv_view.T)[:3]
