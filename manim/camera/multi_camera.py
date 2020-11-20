"""A camera supporting multiple perspectives."""

__all__ = ["MultiCamera"]


from ..camera.moving_camera import MovingCamera
from ..utils.iterables import list_difference_update


class MultiCamera(MovingCamera):
    """Camera Object that allows for multiple perspectives."""

    CONFIG = {
        "allow_cameras_to_capture_their_own_display": False,
    }

    def __init__(
        self, video_quality_config, image_mobjects_from_cameras=None, **kwargs
    ):
        """Initalises the MultiCamera

        Parameters
        ----------
        image_mobjects_from_cameras : ImageMobject

        kwargs
            Any valid keyword arguments of MovingCamera.
        """
        self.image_mobjects_from_cameras = []
        if image_mobjects_from_cameras is not None:
            for imfc in image_mobjects_from_cameras:
                self.add_image_mobject_from_camera(imfc)
        MovingCamera.__init__(self, video_quality_config, **kwargs)

    def add_image_mobject_from_camera(self, image_mobject_from_camera):
        """Adds an ImageMobject that's been obtained from the camera
        into the list ``self.image_mobject_from_cameras``

        Parameters
        ----------
        image_mobject_from_camera : ImageMobject
            The ImageMobject to add to self.image_mobject_from_cameras
        """
        # A silly method to have right now, but maybe there are things
        # we want to guarantee about any imfc's added later.
        imfc = image_mobject_from_camera
        assert isinstance(imfc.camera, MovingCamera)
        self.image_mobjects_from_cameras.append(imfc)

    def update_sub_cameras(self):
        """ Reshape sub_camera pixel_arrays """
        for imfc in self.image_mobjects_from_cameras:
            pixel_height, pixel_width = self.pixel_array.shape[:2]
            imfc.camera.frame_shape = (
                imfc.camera.frame.get_height(),
                imfc.camera.frame.get_width(),
            )
            imfc.camera.reset_pixel_shape(
                int(pixel_height * imfc.get_height() / self.frame_height),
                int(pixel_width * imfc.get_width() / self.frame_width),
            )

    def reset(self):
        """Resets the MultiCamera.

        Returns
        -------
        MultiCamera
            The reset MultiCamera
        """
        for imfc in self.image_mobjects_from_cameras:
            imfc.camera.reset()
        MovingCamera.reset(self)
        return self

    def capture_mobjects(self, mobjects, **kwargs):
        self.update_sub_cameras()
        for imfc in self.image_mobjects_from_cameras:
            to_add = list(mobjects)
            if not self.allow_cameras_to_capture_their_own_display:
                to_add = list_difference_update(to_add, imfc.get_family())
            imfc.camera.capture_mobjects(to_add, **kwargs)
        MovingCamera.capture_mobjects(self, mobjects, **kwargs)

    def get_mobjects_indicating_movement(self):
        """Returns all mobjets whose movement implies that the camera
        should think of all other mobjects on the screen as moving

        Returns
        -------
        list
        """
        return [self.frame] + [
            imfc.camera.frame for imfc in self.image_mobjects_from_cameras
        ]
