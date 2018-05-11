from __future__ import absolute_import

from camera.moving_camera import MovingCamera
from utils.iterables import list_difference_update

# Distinct notions of view frame vs. display frame

# For now, let's say it is the responsibility of the scene holding
# this camera to add all of the relevant image_mobjects_from_cameras,
# as well as their display_frames


class MultiCamera(MovingCamera):
    CONFIG = {
        # "lock_display_frame_dimensions_to_view_frame": True,
        # "display_frame_fixed_dimension": 1,  # Height
        "allow_cameras_to_capture_their_own_display": False,
    }

    def __init__(self, *image_mobjects_from_cameras, **kwargs):
        self.image_mobjects_from_cameras = []
        for imfc in image_mobjects_from_cameras:
            self.add_image_mobject_from_camera(imfc)
        MovingCamera.__init__(self, **kwargs)

    def add_image_mobject_from_camera(self, image_mobject_from_camera):
        # A silly method to have right now, but maybe there are things
        # we want to guarantee about any imfc's added later.
        imfc = image_mobject_from_camera
        assert(isinstance(imfc.camera, MovingCamera))
        self.image_mobjects_from_cameras.append(imfc)

    def update_sub_cameras(self):
        # if self.lock_display_frame_dimensions_to_view_frame:
        #     for imfc in self.image_mobjects_from_cameras:
        #         aspect_ratio = imfc.view_frame.get_width() / imfc.view_frame.get_height()

        # Reshape sub_camera pixel_arrays
        for imfc in self.image_mobjects_from_cameras:
            frame_height, frame_width = self.frame_shape
            pixel_height, pixel_width = self.get_pixel_array().shape[:2]
            imfc.camera.frame_shape = (
                imfc.camera.frame.get_height(),
                imfc.camera.frame.get_width(),
            )
            imfc.camera.reset_pixel_shape((
                int(pixel_height * imfc.get_height() / frame_height),
                int(pixel_width * imfc.get_width() / frame_width),
            ))

    def reset(self):
        for imfc in self.image_mobjects_from_cameras:
            imfc.camera.reset()
        MovingCamera.reset(self)
        return self

    def capture_mobjects(self, mobjects, **kwargs):
        # Make sure all frames are in mobjects?  Or not?
        self.update_sub_cameras()
        for imfc in self.image_mobjects_from_cameras:
            to_add = list(mobjects)
            if not self.allow_cameras_to_capture_their_own_display:
                to_add = list_difference_update(
                    to_add, imfc.submobject_family()
                )
            imfc.camera.capture_mobjects(to_add, **kwargs)
        MovingCamera.capture_mobjects(self, mobjects, **kwargs)

