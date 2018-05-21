from __future__ import absolute_import

import numpy as np

from constants import *

from camera.camera import Camera
from mobject.types.vectorized_mobject import VectorizedPoint
from mobject.three_dimensions import should_shade_in_3d

from utils.bezier import interpolate
from utils.space_ops import rotation_about_z
from utils.space_ops import rotation_matrix

# TODO: Make sure this plays well with latest camera updates


class CameraWithPerspective(Camera):
    CONFIG = {
        "camera_distance": 20,
    }

    def points_to_pixel_coords(self, points):
        distance_ratios = np.divide(
            self.camera_distance,
            self.camera_distance - points[:, 2]
        )
        scale_factors = interpolate(0, 1, distance_ratios)
        adjusted_points = np.array(points)
        for i in 0, 1:
            adjusted_points[:, i] *= scale_factors

        return Camera.points_to_pixel_coords(self, adjusted_points)


class ThreeDCamera(CameraWithPerspective):
    CONFIG = {
        "sun_vect": 5 * UP + LEFT,
        "shading_factor": 0.2,
        "distance": 5.,
        "default_distance": 5.,
        "phi": 0,  # Angle off z axis
        "theta": -TAU / 4,  # Rotation about z axis
    }

    def __init__(self, *args, **kwargs):
        Camera.__init__(self, *args, **kwargs)
        self.unit_sun_vect = self.sun_vect / np.linalg.norm(self.sun_vect)
        # rotation_mobject lives in the phi-theta-distance space
        # TODO, use ValueTracker for this instead
        self.rotation_mobject = VectorizedPoint()
        # moving_center lives in the x-y-z space
        # It representes the center of rotation
        self.moving_center = VectorizedPoint(self.frame_center)
        self.set_position(self.phi, self.theta, self.distance)

    def modified_rgb(self, vmobject, rgb):
        if should_shade_in_3d(vmobject):
            return self.get_shaded_rgb(rgb, self.get_unit_normal_vect(vmobject))
        else:
            return rgb

    def get_stroke_rgb(self, vmobject):
        return self.modified_rgb(vmobject, vmobject.get_stroke_rgb())

    def get_fill_rgb(self, vmobject):
        return self.modified_rgb(vmobject, vmobject.get_fill_rgb())

    def get_shaded_rgb(self, rgb, normal_vect):
        brightness = np.dot(normal_vect, self.unit_sun_vect)**2
        if brightness > 0:
            alpha = self.shading_factor * brightness
            return interpolate(rgb, np.ones(3), alpha)
        else:
            alpha = -self.shading_factor * brightness
            return interpolate(rgb, np.zeros(3), alpha)

    def get_unit_normal_vect(self, vmobject):
        anchors = vmobject.get_anchors()
        if len(anchors) < 3:
            return OUT
        normal = np.cross(anchors[1] - anchors[0], anchors[2] - anchors[1])
        if normal[2] < 0:
            normal = -normal
        length = np.linalg.norm(normal)
        if length == 0:
            return OUT
        return normal / length

    def display_multiple_vectorized_mobjects(self, vmobjects):
        camera_point = self.spherical_coords_to_point(
            *self.get_spherical_coords()
        )

        def z_cmp(*vmobs):
            # Compare to three dimensional mobjects based on
            # how close they are to the camera
            # return cmp(*[
            #     -np.linalg.norm(vm.get_center()-camera_point)
            #     for vm in vmobs
            # ])
            three_d_status = map(should_shade_in_3d, vmobs)
            has_points = [vm.get_num_points() > 0 for vm in vmobs]
            if all(three_d_status) and all(has_points):
                cmp_vect = self.get_unit_normal_vect(vmobs[1])
                return cmp(*[
                    np.dot(vm.get_center(), cmp_vect)
                    for vm in vmobs
                ])
            else:
                return 0
        Camera.display_multiple_vectorized_mobjects(
            self, sorted(vmobjects, cmp=z_cmp)
        )

    def get_spherical_coords(self, phi=None, theta=None, distance=None):
        curr_phi, curr_theta, curr_d = self.rotation_mobject.points[0]
        if phi is None:
            phi = curr_phi
        if theta is None:
            theta = curr_theta
        if distance is None:
            distance = curr_d
        return np.array([phi, theta, distance])

    def get_cartesian_coords(self, phi=None, theta=None, distance=None):
        spherical_coords_array = self.get_spherical_coords(
            phi, theta, distance)
        phi2 = spherical_coords_array[0]
        theta2 = spherical_coords_array[1]
        d2 = spherical_coords_array[2]
        return self.spherical_coords_to_point(phi2, theta2, d2)

    def get_phi(self):
        return self.get_spherical_coords()[0]

    def get_theta(self):
        return self.get_spherical_coords()[1]

    def get_distance(self):
        return self.get_spherical_coords()[2]

    def spherical_coords_to_point(self, phi, theta, distance):
        return distance * np.array([
            np.sin(phi) * np.cos(theta),
            np.sin(phi) * np.sin(theta),
            np.cos(phi)
        ])

    def get_center_of_rotation(self, x=None, y=None, z=None):
        curr_x, curr_y, curr_z = self.moving_center.points[0]
        if x is None:
            x = curr_x
        if y is None:
            y = curr_y
        if z is None:
            z = curr_z
        return np.array([x, y, z])

    def set_position(self, phi=None, theta=None, distance=None,
                     center_x=None, center_y=None, center_z=None):
        point = self.get_spherical_coords(phi, theta, distance)
        self.rotation_mobject.move_to(point)
        self.phi, self.theta, self.distance = point
        center_of_rotation = self.get_center_of_rotation(
            center_x, center_y, center_z)
        self.moving_center.move_to(center_of_rotation)
        self.frame_center = self.moving_center.points[0]

    def get_view_transformation_matrix(self):
        return (self.default_distance / self.get_distance()) * np.dot(
            rotation_matrix(self.get_phi(), LEFT),
            rotation_about_z(-self.get_theta() - np.pi / 2),
        )

    def points_to_pixel_coords(self, points):
        matrix = self.get_view_transformation_matrix()
        new_points = np.dot(points, matrix.T)
        self.frame_center = self.moving_center.points[0]

        return Camera.points_to_pixel_coords(self, new_points)
