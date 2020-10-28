from .. import file_writer_config, logger
from ..utils.hashing import get_hash_from_play_call, get_hash_from_wait_call
from ..constants import DEFAULT_WAIT_TIME


def handle_caching_play(func):
    """Decorator that returns a wrapped version of func that will compute
    the hash of the play invocation.

    The returned function will act according to the computed hash: either skip
    the animation because it's already cached, or let the invoked function
    play normally.

    Parameters
    ----------
    func : Callable[[...], None]
        The play like function that has to be written to the video file stream.
        Take the same parameters as `scene.play`.
    """

    def wrapper(self, scene, *args, **kwargs):
        self.revert_to_original_skipping_status()
        self.update_skipping_status()
        animations = scene.compile_play_args_to_animation_list(*args, **kwargs)
        scene.add_mobjects_from_animations(animations)
        if file_writer_config["skip_animations"]:
            logger.debug(f"Skipping animation {self.num_plays}")
            func(self, scene, *args, **kwargs)
            # If the animation is skipped, we mark its hash as None.
            # When sceneFileWriter will start combining partial movie files, it won't take into account None hashes.
            self.animations_hashes.append(None)
            self.file_writer.add_partial_movie_file(None)
            return
        if not file_writer_config["disable_caching"]:
            mobjects_on_scene = scene.get_mobjects()
            hash_play = get_hash_from_play_call(
                self, self.camera, animations, mobjects_on_scene
            )
            if self.file_writer.is_already_cached(hash_play):
                logger.info(
                    f"Animation {self.num_plays} : Using cached data (hash : %(hash_play)s)",
                    {"hash_play": hash_play},
                )
                file_writer_config["skip_animations"] = True
        else:
            hash_play = "uncached_{:05}".format(self.num_plays)
        self.animations_hashes.append(hash_play)
        self.file_writer.add_partial_movie_file(hash_play)
        logger.debug(
            "List of the first few animation hashes of the scene: %(h)s",
            {"h": str(self.animations_hashes[:5])},
        )
        func(self, scene, *args, **kwargs)

    return wrapper
