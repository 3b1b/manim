import numpy as np
from pydub import AudioSegment
import shutil
import subprocess
import os
import _thread as thread
from time import sleep
import datetime
from PIL import Image

from ..constants import FFMPEG_BIN, GIF_FILE_EXTENSION
from ..config import file_writer_config
from ..logger import logger
from ..utils.config_ops import digest_config
from ..utils.file_ops import guarantee_existence
from ..utils.file_ops import add_extension_if_not_present
from ..utils.file_ops import get_sorted_integer_files
from ..utils.sounds import get_full_sound_file_path


class SceneFileWriter(object):
    """
    SceneFileWriter is the object that actually writes the animations
    played, into video files, using FFMPEG, and Sox, if sound is needed.
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
    """

    def __init__(self, scene, **kwargs):
        digest_config(self, kwargs)
        self.scene = scene
        self.stream_lock = False
        self.init_output_directories()
        self.init_audio()
        self.frame_count = 0

    # Output directories and files
    def init_output_directories(self):
        """
        This method initialises the directories to which video
        files will be written to and read from (within MEDIA_DIR).
        If they don't already exist, they will be created.
        """
        module_directory = self.get_default_module_directory()
        scene_name = self.get_default_scene_name()
        if file_writer_config['save_last_frame'] or file_writer_config['save_pngs']:
            if file_writer_config['media_dir'] != "":
                image_dir = guarantee_existence(os.path.join(
                    file_writer_config['media_dir'],
                    "images",
                    module_directory,
                ))
            self.image_file_path = os.path.join(
                image_dir,
                add_extension_if_not_present(scene_name, ".png")
            )

        if file_writer_config['write_to_movie']:
            if file_writer_config['video_dir']:
                movie_dir = guarantee_existence(os.path.join(
                    file_writer_config['video_dir'],
                    module_directory,
                    self.get_resolution_directory(),
                ))
            self.movie_file_path = os.path.join(
                movie_dir,
                add_extension_if_not_present(
                    scene_name, file_writer_config['movie_file_extension']
                )
            )
            self.gif_file_path = os.path.join(
                movie_dir,
                add_extension_if_not_present(
                    scene_name, GIF_FILE_EXTENSION
                )
            )
            self.partial_movie_directory = guarantee_existence(os.path.join(
                movie_dir,
                "partial_movie_files",
                scene_name,
            ))

    def get_default_module_directory(self):
        """
        This method gets the name of the directory containing
        the file that has the Scene that is being rendered.

        Returns
        -------
        str
            The name of the directory.
        """
        filename = os.path.basename(file_writer_config['input_file'])
        root, _ = os.path.splitext(filename)
        return root

    def get_default_scene_name(self):
        """
        This method returns the default scene name
        which is the value of "output_file", if it exists and
        the actual name of the class that inherited from
        Scene in your animation script, if "output_file" is None.

        Returns
        -------
        str
            The default scene name.
        """
        fn = file_writer_config['output_file']
        return (fn if fn else self.scene.__class__.__name__)

    def get_resolution_directory(self):
        """
        This method gets the name of the directory that immediately contains the
        video file. This name is <height_in_pixels_of_video>p<frame_rate>
        E.G:
            If you are rendering an 854x480 px animation at 15fps, the name of the directory
            that immediately contains the video file will be
            480p15.
            The file structure should look something like:

            MEDIA_DIR
                |--Tex
                |--texts
                |--videos
                |--<name_of_file_containing_scene>
                    |--<height_in_pixels_of_video>p<frame_rate>
                        |--<scene_name>.mp4
        Returns
        -------
        str
            The name of the directory.
        """
        pixel_height = self.scene.camera.pixel_height
        frame_rate = self.scene.camera.frame_rate
        return "{}p{}".format(
            pixel_height, frame_rate
        )

    # Directory getters
    def get_image_file_path(self):
        """
        This returns the directory path to which any images will be
        written to.
        It is usually named "images", but can be changed by changing
        "image_file_path".

        Returns
        -------
        str
            The path of the directory.
        """
        return self.image_file_path

    def get_next_partial_movie_path(self):
        """
        Manim renders each play-like call in a short partial
        video file. All such files are then concatenated with
        the help of FFMPEG.

        This method returns the path of the next partial movie.

        Returns
        -------
        str
            The path of the next partial movie.
        """
        result = os.path.join(
            self.partial_movie_directory,
            "{:05}{}".format(
                self.scene.num_plays,
                file_writer_config['movie_file_extension'],
            )
        )
        return result

    def get_movie_file_path(self):
        """
        Returns the final path of the written video file.

        Returns
        -------
        str
            The path of the movie file.
        """
        return self.movie_file_path

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

    def add_audio_segment(self, new_segment,
                          time=None,
                          gain_to_background=None):
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
            raise Exception("Adding sound at timestamp < 0")

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
        if file_writer_config['write_to_movie'] and allow_write:
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
        if file_writer_config['write_to_movie'] and allow_write:
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
        if file_writer_config['write_to_movie']:
            self.writing_process.stdin.write(frame.tostring())
        if file_writer_config['save_pngs']:
            path, extension = os.path.splitext(self.image_file_path)
            Image.fromarray(frame).save(f'{path}{self.frame_count}{extension}')
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
        file_path = self.get_image_file_path()
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
            self.add_frames(*[frame] * n_frames)
            b = datetime.datetime.now()
            time_diff = (b - a).total_seconds()
            frame_duration = 1 / self.scene.camera.frame_rate
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
        if file_writer_config['write_to_movie']:
            if hasattr(self, "writing_process"):
                self.writing_process.terminate()
            self.combine_movie_files()
        if file_writer_config['save_last_frame']:
            self.scene.update_frame(ignore_skipping=True)
            self.save_final_image(self.scene.get_image())

    def open_movie_pipe(self):
        """
        Used internally by Manim to initalise
        FFMPEG and begin writing to FFMPEG's input
        buffer.
        """
        file_path = self.get_next_partial_movie_path()
        temp_file_path = (os.path.splitext(file_path)[0]
                          + '_temp'
                          + file_writer_config['movie_file_extension'])
        self.partial_movie_file_path = file_path
        self.temp_partial_movie_file_path = temp_file_path

        fps = self.scene.camera.frame_rate
        height = self.scene.camera.get_pixel_height()
        width = self.scene.camera.get_pixel_width()

        command = [
            FFMPEG_BIN,
            '-y',  # overwrite output file if it exists
            '-f', 'rawvideo',
            '-s', '%dx%d' % (width, height),  # size of one frame
            '-pix_fmt', 'rgba',
            '-r', str(fps),  # frames per second
            '-i', '-',  # The imput comes from a pipe
            '-an',  # Tells FFMPEG not to expect any audio
            '-loglevel', 'error',
        ]
        # TODO, the test for a transparent background should not be based on
        # the file extension.
        if file_writer_config['movie_file_extension'] == ".mov":
            # This is if the background of the exported
            # video should be transparent.
            command += [
                '-vcodec', 'qtrle',
            ]
        else:
            command += [
                '-vcodec', 'libx264',
                '-pix_fmt', 'yuv420p',
            ]
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

    def combine_movie_files(self):
        """
        Used internally by Manim to combine the separate
        partial movie files that make up a Scene into a single
        video file for that Scene.
        """
        # Manim renders the scene as many smaller movie files
        # which are then concatenated to a larger one.  The reason
        # for this is that sometimes video-editing is made easier when
        # one works with the broken up scene, which effectively has
        # cuts at all the places you might want.  But for viewing
        # the scene as a whole, one of course wants to see it as a
        # single piece.
        kwargs = {
            "remove_non_integer_files": True,
            "extension": file_writer_config['movie_file_extension'],
        }
        if file_writer_config['from_animation_number'] is not None:
            kwargs["min_index"] = file_writer_config['from_animation_number']
        if file_writer_config['upto_animation_number'] not in [None, np.inf]:
            kwargs["max_index"] = file_writer_config['upto_animation_number']
        else:
            kwargs["remove_indices_greater_than"] = self.scene.num_plays - 1
        partial_movie_files = get_sorted_integer_files(
            self.partial_movie_directory,
            **kwargs
        )
        if len(partial_movie_files) == 0:
            logger.error("No animations in this scene")
            return

        # Write a file partial_file_list.txt containing all
        # partial movie files
        file_list = os.path.join(
            self.partial_movie_directory,
            "partial_movie_file_list.txt"
        )
        with open(file_list, 'w') as fp:
            for pf_path in partial_movie_files:
                if os.name == 'nt':
                    pf_path = pf_path.replace('\\', '/')
                fp.write("file \'file:{}\'\n".format(pf_path))

        movie_file_path = self.get_movie_file_path()
        commands = [
            FFMPEG_BIN,
            '-y',  # overwrite output file if it exists
            '-f', 'concat',
            '-safe', '0',
            '-i', file_list,
            '-loglevel', 'error',
        ]

        if self.write_to_movie:
            commands += [
            '-c', 'copy',
            movie_file_path
            ]

        if self.save_as_gif:
            commands += [
                self.gif_file_path
            ]
        if not self.includes_sound:
            commands.insert(-1, '-an')

        combine_process = subprocess.Popen(commands)
        combine_process.wait()

        if self.includes_sound:
            sound_file_path = movie_file_path.replace(
                file_writer_config['movie_file_extension'], ".wav"
            )
            # Makes sure sound file length will match video file
            self.add_audio_segment(AudioSegment.silent(0))
            self.audio_segment.export(
                sound_file_path,
                bitrate='312k',
            )
            temp_file_path = movie_file_path.replace(".", "_temp.")
            commands = [
                FFMPEG_BIN,
                "-i", movie_file_path,
                "-i", sound_file_path,
                '-y',  # overwrite output file if it exists
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "320k",
                # select video stream from first file
                "-map", "0:v:0",
                # select audio stream from second file
                "-map", "1:a:0",
                '-loglevel', 'error',
                # "-shortest",
                temp_file_path,
            ]
            subprocess.call(commands)
            shutil.move(temp_file_path, movie_file_path)
            os.remove(sound_file_path)

        self.print_file_ready_message(movie_file_path)

    def print_file_ready_message(self, file_path):
        """
        Prints the "File Ready" message to STDOUT.
        """
        logger.info("\nFile ready at {}\n".format(file_path))
