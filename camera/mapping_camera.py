from __future__ import absolute_import

import numpy as np

from camera.camera import Camera
from mobject.types.vectorized_mobject import VMobject
from utils.config_ops import DictAsObject
from utils.config_ops import digest_config

# TODO: Add an attribute to mobjects under which they can specify that they should just
# map their centers but remain otherwise undistorted (useful for labels, etc.)


class MappingCamera(Camera):
    CONFIG = {
        "mapping_func": lambda p: p,
        "min_anchor_points": 50,
        "allow_object_intrusion": False
    }

    def points_to_pixel_coords(self, points):
        return Camera.points_to_pixel_coords(self, np.apply_along_axis(self.mapping_func, 1, points))

    def capture_mobjects(self, mobjects, **kwargs):
        mobjects = self.get_mobjects_to_display(mobjects, **kwargs)
        if self.allow_object_intrusion:
            mobject_copies = mobjects
        else:
            mobject_copies = [mobject.copy() for mobject in mobjects]
        for mobject in mobject_copies:
            if isinstance(mobject, VMobject) and \
                    0 < mobject.get_num_anchor_points() < self.min_anchor_points:
                mobject.insert_n_anchor_points(self.min_anchor_points)
        Camera.capture_mobjects(
            self, mobject_copies,
            include_submobjects=False,
            excluded_mobjects=None,
        )

# Note: This allows layering of multiple cameras onto the same portion of the pixel array,
# the later cameras overwriting the former
#
# TODO: Add optional separator borders between cameras (or perhaps peel this off into a
# CameraPlusOverlay class)


class MultiCamera(Camera):
    def __init__(self, *cameras_with_start_positions, **kwargs):
        self.shifted_cameras = [
            DictAsObject(
                {
                    "camera": camera_with_start_positions[0],
                    "start_x": camera_with_start_positions[1][1],
                    "start_y": camera_with_start_positions[1][0],
                    "end_x": camera_with_start_positions[1][1] + camera_with_start_positions[0].pixel_shape[1],
                    "end_y": camera_with_start_positions[1][0] + camera_with_start_positions[0].pixel_shape[0],
                })
            for camera_with_start_positions in cameras_with_start_positions
        ]
        Camera.__init__(self, **kwargs)

    def capture_mobjects(self, mobjects, **kwargs):
        for shifted_camera in self.shifted_cameras:
            shifted_camera.camera.capture_mobjects(mobjects, **kwargs)

            self.pixel_array[
                shifted_camera.start_y:shifted_camera.end_y,
                shifted_camera.start_x:shifted_camera.end_x] \
                = shifted_camera.camera.pixel_array

    def set_background(self, pixel_array, **kwargs):
        for shifted_camera in self.shifted_cameras:
            shifted_camera.camera.set_background(
                pixel_array[
                    shifted_camera.start_y:shifted_camera.end_y,
                    shifted_camera.start_x:shifted_camera.end_x],
                **kwargs
            )

    def set_pixel_array(self, pixel_array, **kwargs):
        Camera.set_pixel_array(self, pixel_array, **kwargs)
        for shifted_camera in self.shifted_cameras:
            shifted_camera.camera.set_pixel_array(
                pixel_array[
                    shifted_camera.start_y:shifted_camera.end_y,
                    shifted_camera.start_x:shifted_camera.end_x],
                **kwargs
            )

    def init_background(self):
        Camera.init_background(self)
        for shifted_camera in self.shifted_cameras:
            shifted_camera.camera.init_background()

# A MultiCamera which, when called with two full-size cameras, initializes itself
# as a splitscreen, also taking care to resize each individual camera within it


class SplitScreenCamera(MultiCamera):
    def __init__(self, left_camera, right_camera, **kwargs):
        digest_config(self, kwargs)
        self.left_camera = left_camera
        self.right_camera = right_camera

        half_width = self.pixel_shape[1] / 2
        for camera in [self.left_camera, self.right_camera]:
            # TODO: Round up on one if width is odd
            camera.pixel_shape = (self.pixel_shape[0], half_width)
            camera.init_background()
            camera.resize_frame_shape()
            camera.reset()

        MultiCamera.__init__(self, (left_camera, (0, 0)),
                             (right_camera, (0, half_width)))
