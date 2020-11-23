"""A camera that can be positioned and oriented in three-dimensional space."""

__all__ = ["ThreeDCamera"]


import numpy as np

from .. import config
from ..camera.camera import Camera
from ..constants import *
from ..mobject.three_d_utils import get_3d_vmob_end_corner
from ..mobject.three_d_utils import get_3d_vmob_end_corner_unit_normal
from ..mobject.three_d_utils import get_3d_vmob_start_corner
from ..mobject.three_d_utils import get_3d_vmob_start_corner_unit_normal
from ..mobject.types.point_cloud_mobject import Point
from ..mobject.value_tracker import ValueTracker
from ..utils.color import get_shaded_rgb
from ..utils.space_ops import rotation_about_z
from ..utils.space_ops import rotation_matrix
from ..utils.family import extract_mobject_family_members


class ThreeDCamera(Camera):
    CONFIG = {
        "shading_factor": 0.2,
        "distance": 20.0,
        "default_distance": 5.0,
        "phi": 0,  # Angle off z axis
        "theta": -90 * DEGREES,  # Rotation about z axis
        "gamma": 0,  # Rotation about normal vector to camera
        "light_source_start_point": 9 * DOWN + 7 * LEFT + 10 * OUT,
        "should_apply_shading": True,
        "exponential_projection": False,
    }

    def __init__(self, *args, **kwargs):
        """Initializes the ThreeDCamera

        Parameters
        ----------
        *args
            Any argument of Camera
        *kwargs
            Any keyword argument of Camera.
        """
        Camera.__init__(self, *args, **kwargs)
        self.max_allowable_norm = 3 * config["frame_width"]
        self.phi_tracker = ValueTracker(self.phi)
        self.theta_tracker = ValueTracker(self.theta)
        self.distance_tracker = ValueTracker(self.distance)
        self.gamma_tracker = ValueTracker(self.gamma)
        self.light_source = Point(self.light_source_start_point)
        self._frame_center = Point(kwargs.get("frame_center", ORIGIN))
        self.fixed_orientation_mobjects = dict()
        self.fixed_in_frame_mobjects = set()
        self.reset_rotation_matrix()

    @property
    def frame_center(self):
        return self._frame_center.points[0]

    @frame_center.setter
    def frame_center(self, point):
        self._frame_center.move_to(point)

    def capture_mobjects(self, mobjects, **kwargs):
        self.reset_rotation_matrix()
        Camera.capture_mobjects(self, mobjects, **kwargs)

    def get_value_trackers(self):
        """Returns list of ValueTrackers of phi, theta, distance and gamma

        Returns
        -------
        list
            list of ValueTracker objects
        """
        return [
            self.phi_tracker,
            self.theta_tracker,
            self.distance_tracker,
            self.gamma_tracker,
        ]

    def modified_rgbas(
        self, vmobject, rgbas
    ):  # TODO: Write DocStrings for this method.
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

    def get_stroke_rgbas(
        self, vmobject, background=False
    ):  # NOTE : DocStrings From parent
        return self.modified_rgbas(vmobject, vmobject.get_stroke_rgbas(background))

    def get_fill_rgbas(self, vmobject):  # NOTE : DocStrings From parent
        return self.modified_rgbas(vmobject, vmobject.get_fill_rgbas())

    def get_mobjects_to_display(self, *args, **kwargs):  # NOTE : DocStrings From parent
        mobjects = Camera.get_mobjects_to_display(self, *args, **kwargs)
        rot_matrix = self.get_rotation_matrix()

        def z_key(mob):
            if not (hasattr(mob, "shade_in_3d") and mob.shade_in_3d):
                return np.inf
            # Assign a number to a three dimensional mobjects
            # based on how close it is to the camera
            return np.dot(mob.get_z_index_reference_point(), rot_matrix.T)[2]

        return sorted(mobjects, key=z_key)

    def get_phi(self):
        """Returns the Polar angle (the angle off Z_AXIS) phi.

        Returns
        -------
        float
            The Polar angle in radians.
        """
        return self.phi_tracker.get_value()

    def get_theta(self):
        """Returns the Azimuthal i.e the angle that spins the camera around the Z_AXIS.

        Returns
        -------
        float
            The Azimuthal angle in radians.
        """
        return self.theta_tracker.get_value()

    def get_distance(self):
        """Returns radial distance from ORIGIN.

        Returns
        -------
        float
            The radial distance from ORIGIN in MUnits.
        """
        return self.distance_tracker.get_value()

    def get_gamma(self):
        """Returns the rotation of the camera about the vector from the ORIGIN to the Camera.

        Returns
        -------
        float
            The angle of rotation of the camera about the vector
            from the ORIGIN to the Camera in radians
        """
        return self.gamma_tracker.get_value()

    def set_phi(self, value):
        """Sets the polar angle i.e the angle between Z_AXIS and Camera through ORIGIN in radians.

        Parameters
        ----------
        value : int, float
            The new value of the polar angle in radians.
        """
        self.phi_tracker.set_value(value)

    def set_theta(self, value):
        """Sets the azimuthal angle i.e the angle that spins the camera around Z_AXIS in radians.

        Parameters
        ----------
        value : int, float
            The new value of the azimuthal angle in radians.
        """
        self.theta_tracker.set_value(value)

    def set_distance(self, value):
        """Sets the radial distance between the camera and ORIGIN.

        Parameters
        ----------
        value : int, float
            The new radial distance.
        """
        self.distance_tracker.set_value(value)

    def set_gamma(self, value):
        """Sets the angle of rotation of the camera about the vector from the ORIGIN to the Camera.

        Parameters
        ----------
        value : int, float
            The new angle of rotation of the camera.
        """
        self.gamma_tracker.set_value(value)

    def reset_rotation_matrix(self):
        """Sets the value of self.rotation_matrix to
        the matrix corresponding to the current position of the camera
        """
        self.rotation_matrix = self.generate_rotation_matrix()

    def get_rotation_matrix(self):
        """Returns the matrix corresponding to the current position of the camera.

        Returns
        -------
        np.array
            The matrix corresponding to the current position of the camera.
        """
        return self.rotation_matrix

    def generate_rotation_matrix(self):
        """Generates a rotation matrix based off the current position of the camera.

        Returns
        -------
        np.array
            The matrix corresponding to the current position of the camera.
        """
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
        """Applies the current rotation_matrix as a projection
        matrix to the passed array of points.

        Parameters
        ----------
        points : np.array, list
            The list of points to project.

        Returns
        -------
        np.array
            The points after projecting.
        """
        frame_center = self.frame_center
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
                factor[lt0] = distance / (distance - zs[lt0])
            else:
                factor = distance / (distance - zs)
                factor[(distance - zs) < 0] = 10 ** 6
            points[:, i] *= factor
        points = points + frame_center
        return points

    def project_point(self, point):
        """Applies the current rotation_matrix as a projection
        matrix to the passed point.

        Parameters
        ----------
        point : list, np.array
            The point to project.

        Returns
        -------
        np.array
            The point after projection.
        """
        return self.project_points(point.reshape((1, 3)))[0, :]

    def transform_points_pre_display(
        self, mobject, points
    ):  # TODO: Write Docstrings for this Method.
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
        self, *mobjects, use_static_center_func=False, center_func=None
    ):
        """This method allows the mobject to have a fixed orientation,
        even when the camera moves around.
        E.G If it was passed through this method, facing the camera, it
        will continue to face the camera even as the camera moves.
        Highly useful when adding labels to graphs and the like.

        Parameters
        ----------
        *mobjects : Mobject
            The mobject whose orientation must be fixed.
        use_static_center_func : bool, optional
            Whether or not to use the function that takes the mobject's
            center as centerpoint, by default False
        center_func : func, optional
            The function which returns the centerpoint
            with respect to which the mobjec will be oriented, by default None
        """
        # This prevents the computation of mobject.get_center
        # every single time a projetion happens
        def get_static_center_func(mobject):
            point = mobject.get_center()
            return lambda: point

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
        """This method allows the mobject to have a fixed position,
        even when the camera moves around.
        E.G If it was passed through this method, at the top of the frame, it
        will continue to be displayed at the top of the frame.

        Highly useful when displaying Titles or formulae or the like.

        Parameters
        ----------
        **mobjects : Mobject
            The mobject to fix in frame.
        """
        for mobject in extract_mobject_family_members(mobjects):
            self.fixed_in_frame_mobjects.add(mobject)

    def remove_fixed_orientation_mobjects(self, *mobjects):
        """If a mobject was fixed in its orientation by passing it through
        :meth:`.add_fixed_orientation_mobjects`, then this undoes that fixing.
        The Mobject will no longer have a fixed orientation.

        Parameters
        ----------
        mobjects : :class:`Mobject`
            The mobjects whose orientation need not be fixed any longer.
        """
        for mobject in self.extract_mobject_family_members(mobjects):
            if mobject in self.fixed_orientation_mobjects:
                self.fixed_orientation_mobjects.remove(mobject)

    def remove_fixed_in_frame_mobjects(self, *mobjects):
        """If a mobject was fixed in frame by passing it through
        :meth:`.add_fixed_in_frame_mobjects`, then this undoes that fixing.
        The Mobject will no longer be fixed in frame.

        Parameters
        ----------
        mobjects : :class:`Mobject`
            The mobjects which need not be fixed in frame any longer.
        """
        for mobject in self.extract_mobject_family_members(mobjects):
            if mobject in self.fixed_in_frame_mobjects:
                self.fixed_in_frame_mobjects.remove(mobject)
