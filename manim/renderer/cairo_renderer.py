import numpy as np
from .. import file_writer_config
from ..utils.iterables import list_update


class CairoRenderer:
    def __init__(self, scene, camera, file_writer):
        self.scene = scene
        self.camera = camera
        self.file_writer = file_writer

    def update_frame(  # TODO Description in Docstring
        self,
        mobjects=None,
        background=None,
        include_submobjects=True,
        ignore_skipping=True,
        **kwargs,
    ):
        """Update the frame.

        Parameters
        ----------
        mobjects: list, optional
            list of mobjects

        background: np.ndarray, optional
            Pixel Array for Background.

        include_submobjects: bool, optional

        ignore_skipping : bool, optional

        **kwargs

        """
        if file_writer_config["skip_animations"] and not ignore_skipping:
            return
        if mobjects is None:
            mobjects = list_update(
                self.scene.mobjects,
                self.scene.foreground_mobjects,
            )
        if background is not None:
            self.camera.set_frame_to_background(background)
        else:
            self.camera.reset()

        kwargs["include_submobjects"] = include_submobjects
        self.camera.capture_mobjects(mobjects, **kwargs)

    def get_frame(self):
        """
        Gets the current frame as NumPy array.

        Returns
        -------
        np.array
            NumPy array of pixel values of each pixel in screen.
            The shape of the array is height x width x 3
        """
        return np.array(self.camera.pixel_array)
