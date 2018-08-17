

import numpy as np

from constants import *

from camera.camera import Camera
from mobject.types.point_cloud_mobject import Point
from mobject.three_dimensions import ThreeDVMobject
from mobject.value_tracker import ValueTracker

from utils.color import get_shaded_rgb
from utils.space_ops import rotation_about_z
from utils.space_ops import rotation_matrix


class ThreeDCamera(Camera):
    CONFIG = {
        "sun_vect": 5 * UP + LEFT,
        "shading_factor": 0.2,
        "distance": 20.0,
        "default_distance": 5.0,
        "phi": 0,  # Angle off z axis
        "theta": -90 * DEGREES,  # Rotation about z axis
        "gamma": 0,  # Rotation about normal vector to camera
        "light_source_start_point": 9 * DOWN + 7 * LEFT + 10 * OUT,
        "frame_center": ORIGIN,
        "should_apply_shading": True,
    }

    def __init__(self, *args, **kwargs):
        Camera.__init__(self, *args, **kwargs)
        self.phi_tracker = ValueTracker(self.phi)
        self.theta_tracker = ValueTracker(self.theta)
        self.distance_tracker = ValueTracker(self.distance)
        self.gamma_tracker = ValueTracker(self.gamma)
        self.light_source = Point(self.light_source_start_point)
        self.frame_center = Point(self.frame_center)
        self.reset_rotation_matrix()

    def capture_mobjects(self, mobjects, **kwargs):
        self.reset_rotation_matrix()
        Camera.capture_mobjects(self, mobjects, **kwargs)

    def get_value_trackers(self):
        return [
            self.phi_tracker,
            self.theta_tracker,
            self.distance_tracker,
            self.gamma_tracker,
        ]

    def modified_rgbas(self, vmobject, rgbas):
        if not self.should_apply_shading:
            return rgbas
        is_3d = isinstance(vmobject, ThreeDVMobject)
        has_points = (vmobject.get_num_points() > 0)
        if is_3d and has_points:
            light_source_point = self.light_source.points[0]
            if len(rgbas) < 2:
                shaded_rgbas = rgbas.repeat(2, axis=0)
            else:
                shaded_rgbas = np.array(rgbas[:2])
            shaded_rgbas[0, :3] = get_shaded_rgb(
                shaded_rgbas[0, :3],
                vmobject.get_start_corner(),
                vmobject.get_start_corner_unit_normal(),
                light_source_point,
            )
            shaded_rgbas[1, :3] = get_shaded_rgb(
                shaded_rgbas[1, :3],
                vmobject.get_end_corner(),
                vmobject.get_end_corner_unit_normal(),
                light_source_point,
            )
            return shaded_rgbas
        return rgbas

    def get_stroke_rgbas(self, vmobject, background=False):
        return self.modified_rgbas(
            vmobject, vmobject.get_stroke_rgbas(background)
        )

    def get_fill_rgbas(self, vmobject):
        return self.modified_rgbas(
            vmobject, vmobject.get_fill_rgbas()
        )

    def display_multiple_vectorized_mobjects(self, vmobjects, pixel_array):
        rot_matrix = self.get_rotation_matrix()

        def z_key(vmob):
            # Assign a number to a three dimensional mobjects
            # based on how close it is to the camera
            if isinstance(vmob, ThreeDVMobject):
                return np.dot(
                    vmob.get_center(),
                    rot_matrix.T
                )[2]
            else:
                return np.inf
        Camera.display_multiple_vectorized_mobjects(
            self, sorted(vmobjects, key=z_key), pixel_array
        )

    def get_phi(self):
        return self.phi_tracker.get_value()

    def get_theta(self):
        return self.theta_tracker.get_value()

    def get_distance(self):
        return self.distance_tracker.get_value()

    def get_gamma(self):
        return self.gamma_tracker.get_value()

    def get_frame_center(self):
        return self.frame_center.points[0]

    def set_phi(self, value):
        self.phi_tracker.set_value(value)

    def set_theta(self, value):
        self.theta_tracker.set_value(value)

    def set_distance(self, value):
        self.distance_tracker.set_value(value)

    def set_gamma(self, value):
        self.gamma_tracker.set_value(value)

    def set_frame_center(self, point):
        self.frame_center.move_to(point)

    def reset_rotation_matrix(self):
        self.rotation_matrix = self.generate_rotation_matrix()

    def get_rotation_matrix(self):
        return self.rotation_matrix

    def generate_rotation_matrix(self):
        phi = self.get_phi()
        theta = self.get_theta()
        gamma = self.get_gamma()
        matrices = [
            rotation_about_z(-theta - 90 * DEGREES),
            rotation_matrix(-phi, RIGHT),
            rotation_about_z(gamma),
        ]
        result = np.identity(3)
        for matrix in matrices:
            result = np.dot(matrix, result)
        return result

    def transform_points_pre_display(self, points):
        fc = self.get_frame_center()
        distance = self.get_distance()
        points -= fc
        rot_matrix = self.get_rotation_matrix()
        points = np.dot(points, rot_matrix.T)
        zs = points[:, 2]
        zs[zs >= distance] = distance - 0.001
        for i in 0, 1:
            points[:, i] *= distance / (distance - zs)
        points += fc
        return points
