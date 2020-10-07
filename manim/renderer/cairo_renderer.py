import numpy as np
from .. import file_writer_config
from ..utils.iterables import list_update
from ..utils.exceptions import EndSceneEarlyException


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

    def add_frame(self, frame, num_frames=1):
        """
        Adds a frame to the video_file_stream

        Parameters
        ----------
        frame : numpy.ndarray
            The frame to add, as a pixel array.
        num_frames: int
            The number of times to add frame.
        """
        dt = 1 / self.camera.frame_rate
        self.scene.increment_time(num_frames * dt)
        if file_writer_config["skip_animations"]:
            return
        for _ in range(num_frames):
            self.file_writer.write_frame(frame)

    def update_skipping_status(self):
        """
        This method is used internally to check if the current
        animation needs to be skipped or not. It also checks if
        the number of animations that were played correspond to
        the number of animations that need to be played, and
        raises an EndSceneEarlyException if they don't correspond.
        """
        if file_writer_config["from_animation_number"]:
            if self.scene.num_plays < file_writer_config["from_animation_number"]:
                file_writer_config["skip_animations"] = True
        if file_writer_config["upto_animation_number"]:
            if self.scene.num_plays > file_writer_config["upto_animation_number"]:
                file_writer_config["skip_animations"] = True
                raise EndSceneEarlyException()
