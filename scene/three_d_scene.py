from constants import *

from continual_animation.update import ContinualGrowValue
from animation.transform import ApplyMethod
from camera.three_d_camera import ThreeDCamera
from scene.scene import Scene


class ThreeDScene(Scene):
    CONFIG = {
        "camera_class": ThreeDCamera,
        "ambient_camera_rotation": None,
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

    def begin_ambient_camera_rotation(self, rate=0.05):
        self.ambient_camera_rotation = ContinualGrowValue(
            self.camera.theta_tracker,
            rate=rate
        )
        self.add(self.ambient_camera_rotation)

    def stop_ambient_camera_rotation(self):
        if self.ambient_camera_rotation is not None:
            self.remove(self.ambient_camera_rotation)
        self.ambient_camera_rotation = None

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
        is_camera_rotating = self.ambient_camera_rotation in self.continual_animations
        if is_camera_rotating:
            self.remove(self.ambient_camera_rotation)
        self.play(*anims + added_anims)
        if is_camera_rotating:
            self.add(self.ambient_camera_rotation)

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
