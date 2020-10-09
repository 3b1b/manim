import numpy as np
from .. import camera_config, file_writer_config, logger
from ..utils.iterables import list_update
from ..utils.exceptions import EndSceneEarlyException
from ..utils.hashing import get_hash_from_play_call, get_hash_from_wait_call
from ..constants import DEFAULT_WAIT_TIME
from ..scene.scene_file_writer import SceneFileWriter


def handle_caching_play(func):
    """
    Decorator that returns a wrapped version of func that will compute the hash of the play invocation.

    The returned function will act according to the computed hash: either skip the animation because it's already cached, or let the invoked function play normally.

    Parameters
    ----------
    func : Callable[[...], None]
        The play like function that has to be written to the video file stream. Take the same parameters as `scene.play`.
    """

    def wrapper(self, *args, **kwargs):
        self.revert_to_original_skipping_status()
        self.update_skipping_status()
        animations = self.scene.compile_play_args_to_animation_list(*args, **kwargs)
        self.scene.add_mobjects_from_animations(animations)
        if file_writer_config["skip_animations"]:
            logger.debug(f"Skipping animation {self.num_plays}")
            func(self, *args, **kwargs)
            return
        if not file_writer_config["disable_caching"]:
            mobjects_on_scene = self.scene.get_mobjects()
            hash_play = get_hash_from_play_call(
                self, self.camera, animations, mobjects_on_scene
            )
            self.play_hashes_list.append(hash_play)
            if self.file_writer.is_already_cached(hash_play):
                logger.info(
                    f"Animation {self.num_plays} : Using cached data (hash : %(hash_play)s)",
                    {"hash_play": hash_play},
                )
                file_writer_config["skip_animations"] = True
        else:
            hash_play = "uncached_{:05}".format(self.num_plays)
            self.play_hashes_list.append(hash_play)
        func(self, *args, **kwargs)

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

    def wrapper(self, *args, **kwargs):
        allow_write = not file_writer_config["skip_animations"]
        self.file_writer.begin_animation(allow_write)
        func(self, *args, **kwargs)
        self.file_writer.end_animation(allow_write)
        self.num_plays += 1

    return wrapper


class CairoRenderer:
    """A renderer using Cairo.

    num_plays : Number of play() functions in the scene.
    time: time elapsed since initialisation of scene.
    """

    def __init__(self, scene, camera):
        self.camera = camera
        self.file_writer = SceneFileWriter(
            scene,
            **file_writer_config,
        )
        self.scene = scene
        self.original_skipping_status = file_writer_config["skip_animations"]
        self.play_hashes_list = []
        self.num_plays = 0
        self.time = 0

    @handle_caching_play
    @handle_play_like_call
    def play(self, *args, **kwargs):
        self.scene.play_internal(*args, **kwargs)

    @handle_caching_play
    @handle_play_like_call
    def wait(self, duration=DEFAULT_WAIT_TIME, stop_condition=None):
        self.scene.wait_internal(duration=duration, stop_condition=stop_condition)

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

    def finish(self):
        file_writer_config["skip_animations"] = False
        self.file_writer.finish()
        logger.info(f"Rendered {str(self.scene)}\nPlayed {self.num_plays} animations")
