"""The interface between scenes and ffmpeg."""

__all__ = ["SceneFileWriter"]


import numpy as np
from pydub import AudioSegment
import shutil
import subprocess
import os
from time import sleep
import datetime
from PIL import Image
from pathlib import Path

from .. import config, logger
from ..constants import FFMPEG_BIN, GIF_FILE_EXTENSION
from ..utils.config_ops import digest_config
from ..utils.file_ops import guarantee_existence
from ..utils.file_ops import add_extension_if_not_present
from ..utils.file_ops import modify_atime
from ..utils.sounds import get_full_sound_file_path


class SceneFileWriter(object):
    """
    SceneFileWriter is the object that actually writes the animations
    played, into video files, using FFMPEG.
    This is mostly for Manim's internal use. You will rarely, if ever,
    have to use the methods for this class, unless tinkering with the very
    fabric of Manim's reality.

    Some useful attributes are:
        "write_to_movie" (bool=False)
            Whether or not to write the animations into a video file.
        "png_mode" (str="RGBA")
            The PIL image mode to use when outputting PNGs
        "movie_file_extension" (str=".mp4")
            The file-type extension of the outputted video.
        "partial_movie_files"
            List of all the partial-movie files.

    """

    def __init__(self, renderer, video_quality_config, scene_name, **kwargs):
        digest_config(self, kwargs)
        self.renderer = renderer
        self.video_quality_config = video_quality_config
        self.stream_lock = False
        self.init_output_directories(scene_name)
        self.init_audio()
        self.frame_count = 0
        self.partial_movie_files = []

    def init_output_directories(self, scene_name):
        """Initialise output directories.

        Notes
        -----
        The directories are read from ``config``, for example
        ``config['media_dir']``.  If the target directories don't already
        exist, they will be created.

        """
        if config["dry_run"]:  # in dry-run mode there is no output
            return

        if config["input_file"]:
            module_name = config.get_dir("input_file").stem
        else:
            module_name = ""

        if config["output_file"]:
            default_name = config.get_dir("output_file")
        else:
            default_name = Path(scene_name)

        if config["save_last_frame"] or config["save_pngs"]:
            if config["media_dir"]:
                image_dir = guarantee_existence(
                    config.get_dir("images_dir", module_name=module_name)
                )
            self.image_file_path = os.path.join(
                image_dir, add_extension_if_not_present(default_name, ".png")
            )

        if config["write_to_movie"]:
            movie_dir = guarantee_existence(
                config.get_dir("video_dir", module_name=module_name)
            )

            self.movie_file_path = os.path.join(
                movie_dir,
                add_extension_if_not_present(
                    default_name, config["movie_file_extension"]
                ),
            )
            if config["save_as_gif"]:
                self.gif_file_path = os.path.join(
                    movie_dir,
                    add_extension_if_not_present(default_name, GIF_FILE_EXTENSION),
                )

            self.partial_movie_directory = guarantee_existence(
                config.get_dir(
                    "partial_movie_dir",
                    scene_name=default_name,
                    module_name=module_name,
                )
            )

    def add_partial_movie_file(self, hash_animation):
        """Adds a new partial movie file path to scene.partial_movie_files from an hash. This method will compute the path from the hash.

        Parameters
        ----------
        hash_animation : str
            Hash of the animation.
        """
        if not hasattr(self, "partial_movie_directory"):
            return

        # None has to be added to partial_movie_files to keep the right index with scene.num_plays.
        # i.e if an animation is skipped, scene.num_plays is still incremented and we add an element to partial_movie_file be even with num_plays.
        if hash_animation is None:
            self.partial_movie_files.append(None)
            return
        new_partial_movie_file = os.path.join(
            self.partial_movie_directory,
            "{}{}".format(
                hash_animation,
                config["movie_file_extension"],
            ),
        )
        self.partial_movie_files.append(new_partial_movie_file)

    def get_resolution_directory(self):
        """Get the name of the resolution directory directly containing
        the video file.

        This method gets the name of the directory that immediately contains the
        video file. This name is ``<height_in_pixels_of_video>p<frame_rate>``.
        For example, if you are rendering an 854x480 px animation at 15fps,
        the name of the directory that immediately contains the video,  file
        will be ``480p15``.

        The file structure should look something like::

            MEDIA_DIR
                |--Tex
                |--texts
                |--videos
                |--<name_of_file_containing_scene>
                    |--<height_in_pixels_of_video>p<frame_rate>
                        |--<scene_name>.mp4

        Returns
        -------
        :class:`str`
            The name of the directory.
        """
        pixel_height = config["pixel_height"]
        frame_rate = config["frame_rate"]
        return "{}p{}".format(pixel_height, frame_rate)

    # Sound
    def init_audio(self):
        """
        Preps the writer for adding audio to the movie.
        """
        self.includes_sound = False

    def create_audio_segment(self):
        """
        Creates an empty, silent, Audio Segment.
        """
        self.audio_segment = AudioSegment.silent()

    def add_audio_segment(self, new_segment, time=None, gain_to_background=None):
        """
        This method adds an audio segment from an
        AudioSegment type object and suitable parameters.

        Parameters
        ----------
        new_segment : AudioSegment
            The audio segment to add

        time : int, float, optional
            the timestamp at which the
            sound should be added.

        gain_to_background : optional
            The gain of the segment from the background.
        """
        if not self.includes_sound:
            self.includes_sound = True
            self.create_audio_segment()
        segment = self.audio_segment
        curr_end = segment.duration_seconds
        if time is None:
            time = curr_end
        if time < 0:
            raise ValueError("Adding sound at timestamp < 0")

        new_end = time + new_segment.duration_seconds
        diff = new_end - curr_end
        if diff > 0:
            segment = segment.append(
                AudioSegment.silent(int(np.ceil(diff * 1000))),
                crossfade=0,
            )
        self.audio_segment = segment.overlay(
            new_segment,
            position=int(1000 * time),
            gain_during_overlay=gain_to_background,
        )

    def add_sound(self, sound_file, time=None, gain=None, **kwargs):
        """
        This method adds an audio segment from a sound file.

        Parameters
        ----------
        sound_file : str
            The path to the sound file.

        time : float or int, optional
            The timestamp at which the audio should be added.

        gain : optional
            The gain of the given audio segment.

        **kwargs
            This method uses add_audio_segment, so any keyword arguments
            used there can be referenced here.

        """
        file_path = get_full_sound_file_path(sound_file)
        new_segment = AudioSegment.from_file(file_path)
        if gain:
            new_segment = new_segment.apply_gain(gain)
        self.add_audio_segment(new_segment, time, **kwargs)

    # Writers
    def begin_animation(self, allow_write=False):
        """
        Used internally by manim to stream the animation to FFMPEG for
        displaying or writing to a file.

        Parameters
        ----------
        allow_write : bool, optional
            Whether or not to write to a video file.
        """
        if config["write_to_movie"] and allow_write:
            self.open_movie_pipe()

    def end_animation(self, allow_write=False):
        """
        Internally used by Manim to stop streaming to
        FFMPEG gracefully.

        Parameters
        ----------
        allow_write : bool, optional
            Whether or not to write to a video file.
        """
        if config["write_to_movie"] and allow_write:
            self.close_movie_pipe()

    def write_frame(self, frame):
        """
        Used internally by Manim to write a frame to
        the FFMPEG input buffer.

        Parameters
        ----------
        frame : np.array
            Pixel array of the frame.
        """
        if config["write_to_movie"]:
            self.writing_process.stdin.write(frame.tostring())
        if config["save_pngs"]:
            path, extension = os.path.splitext(self.image_file_path)
            Image.fromarray(frame).save(f"{path}{self.frame_count}{extension}")
            self.frame_count += 1

    def save_final_image(self, image):
        """
        The name is a misnomer. This method saves the image
        passed to it as an in the default image directory.

        Parameters
        ----------
        image : np.array
            The pixel array of the image to save.
        """
        file_path = self.image_file_path
        image.save(file_path)
        self.print_file_ready_message(file_path)

    def idle_stream(self):
        """
        Doesn't write anything to the FFMPEG frame buffer.
        """
        while self.stream_lock:
            a = datetime.datetime.now()
            self.update_frame()
            n_frames = 1
            frame = self.get_frame()
            self.add_frame(*[frame] * n_frames)
            b = datetime.datetime.now()
            time_diff = (b - a).total_seconds()
            frame_duration = 1 / config["frame_rate"]
            if time_diff < frame_duration:
                sleep(frame_duration - time_diff)

    def finish(self):
        """
        Finishes writing to the FFMPEG buffer.
        Combines the partial movie files into the
        whole scene.
        If save_last_frame is True, saves the last
        frame in the default image directory.
        """
        if config["write_to_movie"]:
            if hasattr(self, "writing_process"):
                self.writing_process.terminate()
            self.combine_movie_files()
            if config["flush_cache"]:
                self.flush_cache_directory()
            else:
                self.clean_cache()

    def open_movie_pipe(self):
        """
        Used internally by Manim to initalise
        FFMPEG and begin writing to FFMPEG's input
        buffer.
        """
        file_path = self.partial_movie_files[self.renderer.num_plays]

        # TODO #486 Why does ffmpeg need temp files ?
        temp_file_path = (
            os.path.splitext(file_path)[0] + "_temp" + config["movie_file_extension"]
        )
        self.partial_movie_file_path = file_path
        self.temp_partial_movie_file_path = temp_file_path

        fps = config["frame_rate"]
        height = config["pixel_height"]
        width = config["pixel_width"]

        command = [
            FFMPEG_BIN,
            "-y",  # overwrite output file if it exists
            "-f",
            "rawvideo",
            "-s",
            "%dx%d" % (width, height),  # size of one frame
            "-pix_fmt",
            "rgba",
            "-r",
            str(fps),  # frames per second
            "-i",
            "-",  # The imput comes from a pipe
            "-an",  # Tells FFMPEG not to expect any audio
            "-loglevel",
            config["ffmpeg_loglevel"].lower(),
        ]
        if config["transparent"]:
            command += ["-vcodec", "qtrle"]
        else:
            command += ["-vcodec", "libx264", "-pix_fmt", "yuv420p"]
        command += [temp_file_path]
        self.writing_process = subprocess.Popen(command, stdin=subprocess.PIPE)

    def close_movie_pipe(self):
        """
        Used internally by Manim to gracefully stop writing to FFMPEG's
        input buffer, and move the temporary files into their permananant
        locations
        """
        self.writing_process.stdin.close()
        self.writing_process.wait()
        shutil.move(
            self.temp_partial_movie_file_path,
            self.partial_movie_file_path,
        )
        logger.info(
            f"Animation {self.renderer.num_plays} : Partial movie file written in %(path)s",
            {"path": {self.partial_movie_file_path}},
        )

    def is_already_cached(self, hash_invocation):
        """Will check if a file named with `hash_invocation` exists.

        Parameters
        ----------
        hash_invocation : :class:`str`
            The hash corresponding to an invocation to either `scene.play` or `scene.wait`.

        Returns
        -------
        :class:`bool`
            Whether the file exists.
        """
        if not hasattr(self, "partial_movie_directory"):
            return False
        path = os.path.join(
            self.partial_movie_directory,
            "{}{}".format(hash_invocation, config["movie_file_extension"]),
        )
        return os.path.exists(path)

    def combine_movie_files(self):
        """
        Used internally by Manim to combine the separate
        partial movie files that make up a Scene into a single
        video file for that Scene.
        """
        # Manim renders the scene as many smaller movie files which are then
        # concatenated to a larger one.  The reason for this is that sometimes
        # video-editing is made easier when one works with the broken up scene,
        # which effectively has cuts at all the places you might want.  But for
        # viewing the scene as a whole, one of course wants to see it as a
        # single piece.
        partial_movie_files = [el for el in self.partial_movie_files if el is not None]
        # NOTE : Here we should do a check and raise an exeption if partial
        # movie file is empty.  We can't, as a lot of stuff (in particular, in
        # tests) use scene initialization, and this error would be raised as
        # it's just an empty scene initialized.

        # Write a file partial_file_list.txt containing all partial movie
        # files. This is used by FFMPEG.
        file_list = os.path.join(
            self.partial_movie_directory, "partial_movie_file_list.txt"
        )
        logger.debug(
            f"Partial movie files to combine ({len(partial_movie_files)} files): %(p)s",
            {"p": partial_movie_files[:5]},
        )
        with open(file_list, "w") as fp:
            fp.write("# This file is used internally by FFMPEG.\n")
            for pf_path in partial_movie_files:
                if os.name == "nt":
                    pf_path = pf_path.replace("\\", "/")
                fp.write("file 'file:{}'\n".format(pf_path))
        movie_file_path = self.movie_file_path
        commands = [
            FFMPEG_BIN,
            "-y",  # overwrite output file if it exists
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            file_list,
            "-loglevel",
            config["ffmpeg_loglevel"].lower(),
        ]

        if config["write_to_movie"] and not config["save_as_gif"]:
            commands += ["-c", "copy", movie_file_path]

        if config["save_as_gif"]:
            commands += [self.gif_file_path]

        if not self.includes_sound:
            commands.insert(-1, "-an")

        combine_process = subprocess.Popen(commands)
        combine_process.wait()

        if self.includes_sound:
            sound_file_path = movie_file_path.replace(
                config["movie_file_extension"], ".wav"
            )
            # Makes sure sound file length will match video file
            self.add_audio_segment(AudioSegment.silent(0))
            self.audio_segment.export(
                sound_file_path,
                bitrate="312k",
            )
            temp_file_path = movie_file_path.replace(".", "_temp.")
            commands = [
                FFMPEG_BIN,
                "-i",
                movie_file_path,
                "-i",
                sound_file_path,
                "-y",  # overwrite output file if it exists
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-b:a",
                "320k",
                # select video stream from first file
                "-map",
                "0:v:0",
                # select audio stream from second file
                "-map",
                "1:a:0",
                "-loglevel",
                config["ffmpeg_loglevel"].lower(),
                # "-shortest",
                temp_file_path,
            ]
            subprocess.call(commands)
            shutil.move(temp_file_path, movie_file_path)
            os.remove(sound_file_path)

        self.print_file_ready_message(
            self.gif_file_path if config["save_as_gif"] else movie_file_path
        )
        if config["write_to_movie"]:
            for file_path in partial_movie_files:
                # We have to modify the accessed time so if we have to clean the cache we remove the one used the longest.
                modify_atime(file_path)

    def clean_cache(self):
        """Will clean the cache by removing the partial_movie_files used by manim the longest ago."""
        cached_partial_movies = [
            os.path.join(self.partial_movie_directory, file_name)
            for file_name in os.listdir(self.partial_movie_directory)
            if file_name != "partial_movie_file_list.txt"
        ]
        if len(cached_partial_movies) > config["max_files_cached"]:
            number_files_to_delete = (
                len(cached_partial_movies) - config["max_files_cached"]
            )
            oldest_files_to_delete = sorted(
                [partial_movie_file for partial_movie_file in cached_partial_movies],
                key=os.path.getatime,
            )[:number_files_to_delete]
            # oldest_file_path = min(cached_partial_movies, key=os.path.getatime)
            for file_to_delete in oldest_files_to_delete:
                os.remove(file_to_delete)
            logger.info(
                f"The partial movie directory is full (> {config['max_files_cached']} files). Therefore, manim has removed {number_files_to_delete} file(s) used by it the longest ago."
                + "You can change this behaviour by changing max_files_cached in config."
            )

    def flush_cache_directory(self):
        """Delete all the cached partial movie files"""
        cached_partial_movies = [
            os.path.join(self.partial_movie_directory, file_name)
            for file_name in os.listdir(self.partial_movie_directory)
            if file_name != "partial_movie_file_list.txt"
        ]
        for f in cached_partial_movies:
            os.remove(f)
        logger.info(
            f"Cache flushed. {len(cached_partial_movies)} file(s) deleted in %(par_dir)s.",
            {"par_dir": self.partial_movie_directory},
        )

    def print_file_ready_message(self, file_path):
        """Prints the "File Ready" message to STDOUT."""
        logger.info("\nFile ready at %(file_path)s\n", {"file_path": file_path})
