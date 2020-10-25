import numpy as np
from .. import config, camera_config, file_writer_config
from ..utils.iterables import list_update
from ..utils.exceptions import EndSceneEarlyException
from ..constants import DEFAULT_WAIT_TIME
from ..scene.scene_file_writer import SceneFileWriter
from ..utils.caching import handle_caching_play, handle_caching_wait
from ..camera.camera import Camera


def pass_scene_reference(func):
    def wrapper(self, scene, *args, **kwargs):
        func(self, scene, *args, **kwargs)

    return wrapper


def handle_play_like_call(func):
    """
    This method is used internally to wrap the
    passed function, into a function that
    actually writes to the video stream.
    Simultaneously, it also adds to the number
    of animations played.

    Parameters
    ----------
    func : function
        The play() like function that has to be
        written to the video file stream.

    Returns
    -------
    function
        The play() like function that can now write
        to the video file stream.
    """

    def wrapper(self, scene, *args, **kwargs):
        allow_write = not file_writer_config["skip_animations"]
        self.file_writer.begin_animation(allow_write)
        func(self, scene, *args, **kwargs)
        self.file_writer.end_animation(allow_write)
        self.num_plays += 1

    return wrapper


class CairoRenderer:
    """A renderer using Cairo.

    num_plays : Number of play() functions in the scene.
    time: time elapsed since initialisation of scene.
    """

    def __init__(self, camera_class=None, **kwargs):
        # All of the following are set to EITHER the value passed via kwargs,
        # OR the value stored in the global config dict at the time of
        # _instance construction_.  Before, they were in the CONFIG dict, which
        # is a class attribute and is defined at the time of _class
        # definition_.  This did not allow for creating two Cameras with
        # different configurations in the same session.
        self.file_writer = None
        self.video_quality_config = {}
        for attr in [
            "pixel_height",
            "pixel_width",
            "frame_height",
            "frame_width",
            "frame_rate",
        ]:
            self.video_quality_config[attr] = kwargs.get(attr, config[attr])
        camera_cls = camera_class if camera_class is not None else Camera
        self.camera = camera_cls(self.video_quality_config, **camera_config)
        self.original_skipping_status = file_writer_config["skip_animations"]
        self.animations_hashes = []
        self.num_plays = 0
        self.time = 0
        self.static_mobject_data = None

    def init(self, scene):
        self.file_writer = SceneFileWriter(
            self,
            self.video_quality_config,
            scene.__class__.__name__,
            **file_writer_config,
        )

    @pass_scene_reference
    @handle_caching_play
    @handle_play_like_call
    def play(self, scene, *args, **kwargs):
        scene.play_internal(*args, **kwargs)

    @pass_scene_reference
    @handle_caching_wait
    @handle_play_like_call
    def wait(self, scene, duration=DEFAULT_WAIT_TIME, stop_condition=None):
        scene.wait_internal(duration=duration, stop_condition=stop_condition)

    def update_frame(  # TODO Description in Docstring
        self,
        scene,
        mobjects=None,
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
                scene.mobjects,
                scene.foreground_mobjects,
            )
        if self.static_mobject_data is not None:
            self.camera.set_frame_to_background(self.static_mobject_data)
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

    def save_static_mobject_data(self, scene, static_mobjects):
        self.update_frame(scene, static_mobjects)
        self.static_mobject_data = self.get_frame()

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
        self.time += num_frames * dt
        if file_writer_config["skip_animations"]:
            return
        for _ in range(num_frames):
            self.file_writer.write_frame(frame)

    def show_frame(self):
        """
        Opens the current frame in the Default Image Viewer
        of your system.
        """
        self.update_frame(ignore_skipping=True)
        self.camera.get_image().show()

    def update_skipping_status(self):
        """
        This method is used internally to check if the current
        animation needs to be skipped or not. It also checks if
        the number of animations that were played correspond to
        the number of animations that need to be played, and
        raises an EndSceneEarlyException if they don't correspond.
        """
        if file_writer_config["from_animation_number"]:
            if self.num_plays < file_writer_config["from_animation_number"]:
                file_writer_config["skip_animations"] = True
        if file_writer_config["upto_animation_number"]:
            if self.num_plays > file_writer_config["upto_animation_number"]:
                file_writer_config["skip_animations"] = True
                raise EndSceneEarlyException()

    def revert_to_original_skipping_status(self):
        """
        Forces the scene to go back to its original skipping status,
        by setting skip_animations to whatever it reads
        from original_skipping_status.

        Returns
        -------
        Scene
            The Scene, with the original skipping status.
        """
        if hasattr(self, "original_skipping_status"):
            file_writer_config["skip_animations"] = self.original_skipping_status
        return self

    def finish(self, scene):
        file_writer_config["skip_animations"] = False
        self.file_writer.finish()
        if file_writer_config["save_last_frame"]:
            self.update_frame(scene, ignore_skipping=True)
            self.file_writer.save_final_image(self.camera.get_image())
