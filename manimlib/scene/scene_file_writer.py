from __future__ import annotations

import os
import platform
import shutil
import subprocess as sp
import sys

import numpy as np
from pydub import AudioSegment
from tqdm.auto import tqdm as ProgressDisplay
from pathlib import Path

from manimlib.logger import log
from manimlib.mobject.mobject import Mobject
from manimlib.utils.file_ops import get_sorted_integer_files
from manimlib.utils.file_ops import guarantee_existence
from manimlib.utils.sounds import get_full_sound_file_path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL.Image import Image

    from manimlib.camera.camera import Camera
    from manimlib.scene.scene import Scene


class SceneFileWriter(object):
    def __init__(
        self,
        scene: Scene,
        write_to_movie: bool = False,
        subdivide_output: bool = False,
        png_mode: str = "RGBA",
        save_last_frame: bool = False,
        movie_file_extension: str = ".mp4",
        # What python file is generating this scene
        input_file_path: str = "",
        # Where should this be written
        output_directory: str = "",
        file_name: str | None = None,
        open_file_upon_completion: bool = False,
        show_file_location_upon_completion: bool = False,
        quiet: bool = False,
        total_frames: int = 0,
        progress_description_len: int = 40,
        # Name of the binary used for ffmpeg
        ffmpeg_bin: str = "ffmpeg",
        video_codec: str = "libx264",
        pixel_format: str = "yuv420p",
        saturation: float = 1.0,
        gamma: float = 1.0,
    ):
        self.scene: Scene = scene
        self.write_to_movie = write_to_movie
        self.subdivide_output = subdivide_output
        self.png_mode = png_mode
        self.save_last_frame = save_last_frame
        self.movie_file_extension = movie_file_extension
        self.input_file_path = input_file_path
        self.output_directory = output_directory
        self.file_name = file_name
        self.open_file_upon_completion = open_file_upon_completion
        self.show_file_location_upon_completion = show_file_location_upon_completion
        self.quiet = quiet
        self.total_frames = total_frames
        self.progress_description_len = progress_description_len
        self.ffmpeg_bin = ffmpeg_bin
        self.video_codec = video_codec
        self.pixel_format = pixel_format
        self.saturation = saturation
        self.gamma = gamma

        # State during file writing
        self.writing_process: sp.Popen | None = None
        self.progress_display: ProgressDisplay | None = None
        self.ended_with_interrupt: bool = False

        self.init_output_directories()
        self.init_audio()

    # Output directories and files
    def init_output_directories(self) -> None:
        if self.save_last_frame:
            self.image_file_path = self.init_image_file_path()
        if self.write_to_movie:
            self.movie_file_path = self.init_movie_file_path()
        if self.subdivide_output:
            self.partial_movie_directory = self.init_partial_movie_directory()

    def init_image_file_path(self) -> Path:
        return self.get_output_file_rootname().with_suffix(".png")

    def init_movie_file_path(self) -> Path:
        return self.get_output_file_rootname().with_suffix(self.movie_file_extension)

    def init_partial_movie_directory(self):
        return guarantee_existence(self.get_output_file_rootname())

    def get_output_file_rootname(self) -> Path:
        return Path(
            guarantee_existence(self.output_directory),
            self.get_output_file_name()
        )

    def get_output_file_name(self) -> str:
        if self.file_name:
            return self.file_name
        # Otherwise, use the name of the scene, potentially
        # appending animation numbers
        name = str(self.scene)
        saan = self.scene.start_at_animation_number
        eaan = self.scene.end_at_animation_number
        if saan is not None:
            name += f"_{saan}"
        if eaan is not None:
            name += f"_{eaan}"
        return name

    # Directory getters
    def get_image_file_path(self) -> str:
        return self.image_file_path

    def get_next_partial_movie_path(self) -> str:
        result = Path(self.partial_movie_directory, f"{self.scene.num_plays:05}")
        return result.with_suffix(self.movie_file_extension)

    def get_movie_file_path(self) -> str:
        return self.movie_file_path

    # Sound
    def init_audio(self) -> None:
        self.includes_sound: bool = False

    def create_audio_segment(self) -> None:
        self.audio_segment = AudioSegment.silent()

    def add_audio_segment(
        self,
        new_segment: AudioSegment,
        time: float | None = None,
        gain_to_background: float | None = None
    ) -> None:
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

    def add_sound(
        self,
        sound_file: str,
        time: float | None = None,
        gain: float | None = None,
        gain_to_background: float | None = None
    ) -> None:
        file_path = get_full_sound_file_path(sound_file)
        new_segment = AudioSegment.from_file(file_path)
        if gain:
            new_segment = new_segment.apply_gain(gain)
        self.add_audio_segment(new_segment, time, gain_to_background)

    # Writers
    def begin(self) -> None:
        if not self.subdivide_output and self.write_to_movie:
            self.open_movie_pipe(self.get_movie_file_path())

    def begin_animation(self) -> None:
        if self.subdivide_output and self.write_to_movie:
            self.open_movie_pipe(self.get_next_partial_movie_path())

    def end_animation(self) -> None:
        if self.subdivide_output and self.write_to_movie:
            self.close_movie_pipe()

    def finish(self) -> None:
        if not self.subdivide_output and self.write_to_movie:
            self.close_movie_pipe()
            if self.includes_sound:
                self.add_sound_to_video()
            self.print_file_ready_message(self.get_movie_file_path())
        if self.save_last_frame:
            self.scene.update_frame(force_draw=True)
            self.save_final_image(self.scene.get_image())
        if self.should_open_file():
            self.open_file()

    def open_movie_pipe(self, file_path: str) -> None:
        stem, ext = os.path.splitext(file_path)
        self.final_file_path = file_path
        self.temp_file_path = stem + "_temp" + ext

        fps = self.scene.camera.fps
        width, height = self.scene.camera.get_pixel_shape()

        vf_arg = 'vflip'
        vf_arg += f',eq=saturation={self.saturation}:gamma={self.gamma}'

        command = [
            self.ffmpeg_bin,
            '-y',  # overwrite output file if it exists
            '-f', 'rawvideo',
            '-s', f'{width}x{height}',  # size of one frame
            '-pix_fmt', 'rgba',
            '-r', str(fps),  # frames per second
            '-i', '-',  # The input comes from a pipe
            '-vf', vf_arg,
            '-an',  # Tells ffmpeg not to expect any audio
            '-loglevel', 'error',
        ]
        if self.video_codec:
            command += ['-vcodec', self.video_codec]
        if self.pixel_format:
            command += ['-pix_fmt', self.pixel_format]
        command += [self.temp_file_path]
        self.writing_process = sp.Popen(command, stdin=sp.PIPE)

        if not self.quiet:
            self.progress_display = ProgressDisplay(
                range(self.total_frames),
                leave=False,
                ascii=True if platform.system() == 'Windows' else None,
                dynamic_ncols=True,
            )
            self.set_progress_display_description()

    def use_fast_encoding(self):
        self.video_codec = "libx264rgb"
        self.pixel_format = "rgb32"

    def get_insert_file_path(self, index: int) -> Path:
        movie_path = Path(self.get_movie_file_path())
        scene_name = movie_path.stem
        insert_dir = Path(movie_path.parent, "inserts")
        guarantee_existence(insert_dir)
        return Path(insert_dir, f"{scene_name}_{index}").with_suffix(self.movie_file_extension)

    def begin_insert(self):
        # Begin writing process
        self.write_to_movie = True
        self.init_output_directories()
        index = 0
        while (insert_path := self.get_insert_file_path(index)).exists():
            index += 1
        self.inserted_file_path = insert_path
        self.open_movie_pipe(self.inserted_file_path)

    def end_insert(self):
        self.close_movie_pipe()
        self.write_to_movie = False
        self.print_file_ready_message(self.inserted_file_path)

    def has_progress_display(self):
        return self.progress_display is not None

    def set_progress_display_description(self, file: str = "", sub_desc: str = "") -> None:
        if self.progress_display is None:
            return

        desc_len = self.progress_description_len
        if not file:
            file = os.path.split(self.get_movie_file_path())[1]
        full_desc = f"{file} {sub_desc}"
        if len(full_desc) > desc_len:
            full_desc = full_desc[:desc_len - 3] + "..."
        else:
            full_desc += " " * (desc_len - len(full_desc))
        self.progress_display.set_description(full_desc)

    def write_frame(self, camera: Camera) -> None:
        if self.write_to_movie:
            raw_bytes = camera.get_raw_fbo_data()
            self.writing_process.stdin.write(raw_bytes)
            if self.progress_display is not None:
                self.progress_display.update()

    def close_movie_pipe(self) -> None:
        self.writing_process.stdin.close()
        self.writing_process.wait()
        self.writing_process.terminate()
        if self.progress_display is not None:
            self.progress_display.close()

        if not self.ended_with_interrupt:
            shutil.move(self.temp_file_path, self.final_file_path)
        else:
            self.movie_file_path = self.temp_file_path

    def add_sound_to_video(self) -> None:
        movie_file_path = self.get_movie_file_path()
        stem, ext = os.path.splitext(movie_file_path)
        sound_file_path = stem + ".wav"
        # Makes sure sound file length will match video file
        self.add_audio_segment(AudioSegment.silent(0))
        self.audio_segment.export(
            sound_file_path,
            bitrate='312k',
        )
        temp_file_path = stem + "_temp" + ext
        commands = [
            self.ffmpeg_bin,
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
        sp.call(commands)
        shutil.move(temp_file_path, movie_file_path)
        os.remove(sound_file_path)

    def save_final_image(self, image: Image) -> None:
        file_path = self.get_image_file_path()
        image.save(file_path)
        self.print_file_ready_message(file_path)

    def print_file_ready_message(self, file_path: str) -> None:
        if not self.quiet:
            log.info(f"File ready at {file_path}")

    def should_open_file(self) -> bool:
        return any([
            self.show_file_location_upon_completion,
            self.open_file_upon_completion,
        ])

    def open_file(self) -> None:
        if self.quiet:
            curr_stdout = sys.stdout
            sys.stdout = open(os.devnull, "w")

        current_os = platform.system()
        file_paths = []

        if self.save_last_frame:
            file_paths.append(self.get_image_file_path())
        if self.write_to_movie:
            file_paths.append(self.get_movie_file_path())

        for file_path in file_paths:
            if current_os == "Windows":
                os.startfile(file_path)
            else:
                commands = []
                if current_os == "Linux":
                    commands.append("xdg-open")
                elif current_os.startswith("CYGWIN"):
                    commands.append("cygstart")
                else:  # Assume macOS
                    commands.append("open")

                if self.show_file_location_upon_completion:
                    commands.append("-R")

                commands.append(file_path)

                FNULL = open(os.devnull, 'w')
                sp.call(commands, stdout=FNULL, stderr=sp.STDOUT)
                FNULL.close()

        if self.quiet:
            sys.stdout.close()
            sys.stdout = curr_stdout
