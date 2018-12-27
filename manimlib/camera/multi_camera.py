from manimlib.camera.moving_camera import MovingCamera
from manimlib.utils.iterables import list_difference_update


class MultiCamera(MovingCamera):
    CONFIG = {
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
        """ Reshape sub_camera pixel_arrays """
        for imfc in self.image_mobjects_from_cameras:
            pixel_height, pixel_width = self.get_pixel_array().shape[:2]
            imfc.camera.frame_shape = (
                imfc.camera.frame.get_height(),
                imfc.camera.frame.get_width(),
            )
            imfc.camera.reset_pixel_shape(
                int(pixel_height * imfc.get_height() / self.get_frame_height()),
                int(pixel_width * imfc.get_width() / self.get_frame_width()),
            )

    def reset(self):
        for imfc in self.image_mobjects_from_cameras:
            imfc.camera.reset()
        MovingCamera.reset(self)
        return self

    def capture_mobjects(self, mobjects, **kwargs):
        self.update_sub_cameras()
        for imfc in self.image_mobjects_from_cameras:
            to_add = list(mobjects)
            if not self.allow_cameras_to_capture_their_own_display:
                to_add = list_difference_update(
                    to_add, imfc.get_family()
                )
            imfc.camera.capture_mobjects(to_add, **kwargs)
        MovingCamera.capture_mobjects(self, mobjects, **kwargs)

    def get_mobjects_indicating_movement(self):
        return [self.frame] + [
            imfc.camera.frame
            for imfc in self.image_mobjects_from_cameras
        ]
