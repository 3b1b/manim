from __future__ import absolute_import

from constants import *

from continual_animation.continual_animation import ContinualMovement
from animation.transform import ApplyMethod
from camera.three_d_camera import ThreeDCamera
from scene.scene import Scene

from utils.iterables import list_update


class ThreeDScene(Scene):
    CONFIG = {
        "camera_class": ThreeDCamera,
        "ambient_camera_rotation": None,
    }

    def set_camera_position(self, phi=None, theta=None, distance=None,
                            center_x=None, center_y=None, center_z=None):
        self.camera.set_position(
            phi, theta, distance,
            center_x, center_y, center_z
        )

    def begin_ambient_camera_rotation(self, rate=0.01):
        self.ambient_camera_rotation = ContinualMovement(
            self.camera.rotation_mobject,
            direction=UP,
            rate=rate
        )
        self.add(self.ambient_camera_rotation)

    def stop_ambient_camera_rotation(self):
        if self.ambient_camera_rotation is not None:
            self.remove(self.ambient_camera_rotation)
        self.ambient_camera_rotation = None

    def move_camera(
        self,
        phi=None, theta=None, distance=None,
        center_x=None, center_y=None, center_z=None,
        added_anims=[],
        **kwargs
    ):
        target_point = self.camera.get_spherical_coords(phi, theta, distance)
        movement = ApplyMethod(
            self.camera.rotation_mobject.move_to,
            target_point,
            **kwargs
        )
        target_center = self.camera.get_center_of_rotation(
            center_x, center_y, center_z)
        movement_center = ApplyMethod(
            self.camera.moving_center.move_to,
            target_center,
            **kwargs
        )
        is_camera_rotating = self.ambient_camera_rotation in self.continual_animations
        if is_camera_rotating:
            self.remove(self.ambient_camera_rotation)
        self.play(movement, movement_center, *added_anims)
        target_point = self.camera.get_spherical_coords(phi, theta, distance)
        if is_camera_rotating:
            self.add(self.ambient_camera_rotation)

    def get_moving_mobjects(self, *animations):
        moving_mobjects = Scene.get_moving_mobjects(self, *animations)
        if self.camera.rotation_mobject in moving_mobjects:
            return list_update(self.mobjects, moving_mobjects)
        return moving_mobjects
