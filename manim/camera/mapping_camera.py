"""A camera that allows mapping between objects."""

__all__ = ["MappingCamera", "OldMultiCamera", "SplitScreenCamera"]


import numpy as np

from ..camera.camera import Camera
from ..mobject.types.vectorized_mobject import VMobject
from ..utils.config_ops import DictAsObject
from ..utils.config_ops import digest_config

# TODO: Add an attribute to mobjects under which they can specify that they should just
# map their centers but remain otherwise undistorted (useful for labels, etc.)


class MappingCamera(Camera):
    """Camera object that allows mapping
    between objects.
    """

    CONFIG = {
        "mapping_func": lambda p: p,
        "min_num_curves": 50,
        "allow_object_intrusion": False,
    }

    def points_to_pixel_coords(self, points):
        return Camera.points_to_pixel_coords(
            self, np.apply_along_axis(self.mapping_func, 1, points)
        )

    def capture_mobjects(self, mobjects, **kwargs):
        mobjects = self.get_mobjects_to_display(mobjects, **kwargs)
        if self.allow_object_intrusion:
            mobject_copies = mobjects
        else:
            mobject_copies = [mobject.copy() for mobject in mobjects]
        for mobject in mobject_copies:
            if (
                isinstance(mobject, VMobject)
                and 0 < mobject.get_num_curves() < self.min_num_curves
            ):
                mobject.insert_n_curves(self.min_num_curves)
        Camera.capture_mobjects(
            self,
            mobject_copies,
            include_submobjects=False,
            excluded_mobjects=None,
        )


# Note: This allows layering of multiple cameras onto the same portion of the pixel array,
# the later cameras overwriting the former
#
# TODO: Add optional separator borders between cameras (or perhaps peel this off into a
# CameraPlusOverlay class)

# TODO, the classes below should likely be deleted
class OldMultiCamera(Camera):
    def __init__(self, *cameras_with_start_positions, **kwargs):
        self.shifted_cameras = [
            DictAsObject(
                {
                    "camera": camera_with_start_positions[0],
                    "start_x": camera_with_start_positions[1][1],
                    "start_y": camera_with_start_positions[1][0],
                    "end_x": camera_with_start_positions[1][1]
                    + camera_with_start_positions[0].pixel_width,
                    "end_y": camera_with_start_positions[1][0]
                    + camera_with_start_positions[0].pixel_height,
                }
            )
            for camera_with_start_positions in cameras_with_start_positions
        ]
        Camera.__init__(self, **kwargs)

    def capture_mobjects(self, mobjects, **kwargs):
        for shifted_camera in self.shifted_cameras:
            shifted_camera.camera.capture_mobjects(mobjects, **kwargs)

            self.pixel_array[
                shifted_camera.start_y : shifted_camera.end_y,
                shifted_camera.start_x : shifted_camera.end_x,
            ] = shifted_camera.camera.pixel_array

    def set_background(self, pixel_array, **kwargs):
        for shifted_camera in self.shifted_cameras:
            shifted_camera.camera.set_background(
                pixel_array[
                    shifted_camera.start_y : shifted_camera.end_y,
                    shifted_camera.start_x : shifted_camera.end_x,
                ],
                **kwargs,
            )

    def set_pixel_array(self, pixel_array, **kwargs):
        Camera.set_pixel_array(self, pixel_array, **kwargs)
        for shifted_camera in self.shifted_cameras:
            shifted_camera.camera.set_pixel_array(
                pixel_array[
                    shifted_camera.start_y : shifted_camera.end_y,
                    shifted_camera.start_x : shifted_camera.end_x,
                ],
                **kwargs,
            )

    def init_background(self):
        Camera.init_background(self)
        for shifted_camera in self.shifted_cameras:
            shifted_camera.camera.init_background()


# A OldMultiCamera which, when called with two full-size cameras, initializes itself
# as a splitscreen, also taking care to resize each individual camera within it


class SplitScreenCamera(OldMultiCamera):
    def __init__(self, left_camera, right_camera, **kwargs):
        digest_config(self, kwargs)
        self.left_camera = left_camera
        self.right_camera = right_camera

        half_width = self.pixel_width / 2
        for camera in [self.left_camera, self.right_camera]:
            # TODO: Round up on one if width is odd
            camera.reset_pixel_shape(camera.pixel_height, half_width)

        OldMultiCamera.__init__(
            self,
            (left_camera, (0, 0)),
            (right_camera, (0, half_width)),
        )
