import numpy as np

from manimlib.camera.camera import Camera
from manimlib.constants import *
from manimlib.mobject.three_d_utils import get_3d_vmob_end_corner
from manimlib.mobject.three_d_utils import get_3d_vmob_end_corner_unit_normal
from manimlib.mobject.three_d_utils import get_3d_vmob_start_corner
from manimlib.mobject.three_d_utils import get_3d_vmob_start_corner_unit_normal
from manimlib.mobject.types.point_cloud_mobject import Point
from manimlib.mobject.value_tracker import ValueTracker
from manimlib.utils.color import get_shaded_rgb
from manimlib.utils.simple_functions import clip_in_place
from manimlib.utils.space_ops import rotation_about_z
from manimlib.utils.space_ops import rotation_matrix


class ThreeDCamera(Camera):
    CONFIG = {
        "shading_factor": 0.2,
        "distance": 20.0,
        "default_distance": 5.0,
        "phi": 0,  # Angle off z axis
        "theta": -90 * DEGREES,  # Rotation about z axis
        "gamma": 0,  # Rotation about normal vector to camera
        "light_source_start_point": 9 * DOWN + 7 * LEFT + 10 * OUT,
        "frame_center": ORIGIN,
        "should_apply_shading": True,
        "exponential_projection": False,
        "max_allowable_norm": 3 * FRAME_WIDTH,
    }

    def __init__(self, *args, **kwargs):
        Camera.__init__(self, *args, **kwargs)
        self.phi_tracker = ValueTracker(self.phi)
        self.theta_tracker = ValueTracker(self.theta)
        self.distance_tracker = ValueTracker(self.distance)
        self.gamma_tracker = ValueTracker(self.gamma)
        self.light_source = Point(self.light_source_start_point)
        self.frame_center = Point(self.frame_center)
        self.fixed_orientation_mobjects = dict()
        self.fixed_in_frame_mobjects = set()
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
        if vmobject.shade_in_3d and (vmobject.get_num_points() > 0):
            light_source_point = self.light_source.points[0]
            if len(rgbas) < 2:
                shaded_rgbas = rgbas.repeat(2, axis=0)
            else:
                shaded_rgbas = np.array(rgbas[:2])
            shaded_rgbas[0, :3] = get_shaded_rgb(
                shaded_rgbas[0, :3],
                get_3d_vmob_start_corner(vmobject),
                get_3d_vmob_start_corner_unit_normal(vmobject),
                light_source_point,
            )
            shaded_rgbas[1, :3] = get_shaded_rgb(
                shaded_rgbas[1, :3],
                get_3d_vmob_end_corner(vmobject),
                get_3d_vmob_end_corner_unit_normal(vmobject),
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

    def get_mobjects_to_display(self, *args, **kwargs):
        mobjects = Camera.get_mobjects_to_display(
            self, *args, **kwargs
        )
        rot_matrix = self.get_rotation_matrix()

        def z_key(mob):
            if not (hasattr(mob, "shade_in_3d") and mob.shade_in_3d):
                return np.inf
            # Assign a number to a three dimensional mobjects
            # based on how close it is to the camera
            return np.dot(
                mob.get_z_index_reference_point(),
                rot_matrix.T
            )[2]
        return sorted(mobjects, key=z_key)

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

    def project_points(self, points):
        frame_center = self.get_frame_center()
        distance = self.get_distance()
        rot_matrix = self.get_rotation_matrix()

        points = points - frame_center
        points = np.dot(points, rot_matrix.T)
        zs = points[:, 2]
        for i in 0, 1:
            if self.exponential_projection:
                # Proper projedtion would involve multiplying
                # x and y by d / (d-z).  But for points with high
                # z value that causes weird artifacts, and applying
                # the exponential helps smooth it out.
                factor = np.exp(zs / distance)
                lt0 = zs < 0
                factor[lt0] = (distance / (distance - zs[lt0]))
            else:
                factor = (distance / (distance - zs))
                factor[(distance - zs) < 0] = 10**6
                # clip_in_place(factor, 0, 10**6)
            points[:, i] *= factor
        points = points + frame_center
        return points

    def project_point(self, point):
        return self.project_points(point.reshape((1, 3)))[0, :]

    def transform_points_pre_display(self, mobject, points):
        points = super().transform_points_pre_display(mobject, points)
        fixed_orientation = mobject in self.fixed_orientation_mobjects
        fixed_in_frame = mobject in self.fixed_in_frame_mobjects

        if fixed_in_frame:
            return points
        if fixed_orientation:
            center_func = self.fixed_orientation_mobjects[mobject]
            center = center_func()
            new_center = self.project_point(center)
            return points + (new_center - center)
        else:
            return self.project_points(points)

    def add_fixed_orientation_mobjects(
            self, *mobjects,
            use_static_center_func=False,
            center_func=None):
        # This prevents the computation of mobject.get_center
        # every single time a projetion happens
        def get_static_center_func(mobject):
            point = mobject.get_center()
            return (lambda: point)

        for mobject in mobjects:
            if center_func:
                func = center_func
            elif use_static_center_func:
                func = get_static_center_func(mobject)
            else:
                func = mobject.get_center
            for submob in mobject.get_family():
                self.fixed_orientation_mobjects[submob] = func

    def add_fixed_in_frame_mobjects(self, *mobjects):
        for mobject in self.extract_mobject_family_members(mobjects):
            self.fixed_in_frame_mobjects.add(mobject)

    def remove_fixed_orientation_mobjects(self, *mobjects):
        for mobject in self.extract_mobject_family_members(mobjects):
            if mobject in self.fixed_orientation_mobjects:
                self.fixed_orientation_mobjects.remove(mobject)

    def remove_fixed_in_frame_mobjects(self, *mobjects):
        for mobject in self.extract_mobject_family_members(mobjects):
            if mobject in self.fixed_in_frame_mobjects:
                self.fixed_in_frame_mobjects.remove(mobject)
