from __future__ import annotations

import argparse
import colour
import importlib
import inspect
import os
import sys
import yaml
from pathlib import Path
from ast import literal_eval
from addict import Dict

from manimlib.logger import log
from manimlib.utils.dict_ops import merge_dicts_recursively

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from argparse import Namespace
    from typing import Optional


def initialize_manim_config() -> Dict:
    """
    Return default configuration for various classes in manim, such as
    Scene, Window, Camera, and SceneFileWriter, as well as configuration
    determining how the scene is run (e.g. written to file or previewed in window).

    The result is initially on the contents of default_config.yml in the manimlib directory,
    which can be further updated by a custom configuration file custom_config.yml.
    It is further updated based on command line argument.
    """
    args = parse_cli()
    global_defaults_file = os.path.join(get_manim_dir(), "manimlib", "default_config.yml")
    config = Dict(merge_dicts_recursively(
        load_yaml(global_defaults_file),
        load_yaml("custom_config.yml"),  # From current working directory
        load_yaml(args.config_file) if args.config_file else dict(),
    ))

    log.setLevel(args.log_level or config["log_level"])

    update_directory_config(config)
    update_window_config(config, args)
    update_camera_config(config, args)
    update_file_writer_config(config, args)
    update_scene_config(config, args)
    update_run_config(config, args)
    update_embed_config(config, args)

    return config


def parse_cli():
    try:
        parser = argparse.ArgumentParser()
        module_location = parser.add_mutually_exclusive_group()
        module_location.add_argument(
            "file",
            nargs="?",
            help="Path to file holding the python code for the scene",
        )
        parser.add_argument(
            "scene_names",
            nargs="*",
            help="Name of the Scene class you want to see",
        )
        parser.add_argument(
            "-w", "--write_file",
            action="store_true",
            help="Render the scene as a movie file",
        )
        parser.add_argument(
            "-s", "--skip_animations",
            action="store_true",
            help="Save the last frame",
        )
        parser.add_argument(
            "-l", "--low_quality",
            action="store_true",
            help="Render at 480p",
        )
        parser.add_argument(
            "-m", "--medium_quality",
            action="store_true",
            help="Render at 720p",
        )
        parser.add_argument(
            "--hd",
            action="store_true",
            help="Render at a 1080p",
        )
        parser.add_argument(
            "--uhd",
            action="store_true",
            help="Render at a 4k",
        )
        parser.add_argument(
            "-f", "--full_screen",
            action="store_true",
            help="Show window in full screen",
        )
        parser.add_argument(
            "-p", "--presenter_mode",
            action="store_true",
            help="Scene will stay paused during wait calls until " + \
                 "space bar or right arrow is hit, like a slide show"
        )
        parser.add_argument(
            "-i", "--gif",
            action="store_true",
            help="Save the video as gif",
        )
        parser.add_argument(
            "-t", "--transparent",
            action="store_true",
            help="Render to a movie file with an alpha channel",
        )
        parser.add_argument(
            "--vcodec",
            help="Video codec to use with ffmpeg",
        )
        parser.add_argument(
            "--pix_fmt",
            help="Pixel format to use for the output of ffmpeg, defaults to `yuv420p`",
        )
        parser.add_argument(
            "-q", "--quiet",
            action="store_true",
            help="",
        )
        parser.add_argument(
            "-a", "--write_all",
            action="store_true",
            help="Write all the scenes from a file",
        )
        parser.add_argument(
            "-o", "--open",
            action="store_true",
            help="Automatically open the saved file once its done",
        )
        parser.add_argument(
            "--finder",
            action="store_true",
            help="Show the output file in finder",
        )
        parser.add_argument(
            "--subdivide",
            action="store_true",
            help="Divide the output animation into individual movie files " +
                 "for each animation",
        )
        parser.add_argument(
            "--file_name",
            help="Name for the movie or image file",
        )
        parser.add_argument(
            "-n", "--start_at_animation_number",
            help="Start rendering not from the first animation, but " + \
                 "from another, specified by its index.  If you pass " + \
                 "in two comma separated values, e.g. \"3,6\", it will end " + \
                 "the rendering at the second value",
        )
        parser.add_argument(
            "-e", "--embed",
            metavar="LINE_NUMBER",
            help="Adds a breakpoint at the inputted file dropping into an " + \
                 "interactive iPython session at that point of the code."
        )
        parser.add_argument(
            "-r", "--resolution",
            help="Resolution, passed as \"WxH\", e.g. \"1920x1080\"",
        )
        parser.add_argument(
            "--fps",
            help="Frame rate, as an integer",
        )
        parser.add_argument(
            "-c", "--color",
            help="Background color",
        )
        parser.add_argument(
            "--leave_progress_bars",
            action="store_true",
            help="Leave progress bars displayed in terminal",
        )
        parser.add_argument(
            "--show_animation_progress",
            action="store_true",
            help="Show progress bar for each animation",
        )
        parser.add_argument(
            "--prerun",
            action="store_true",
            help="Calculate total framecount, to display in a progress bar, by doing " + \
                 "an initial run of the scene which skips animations."
        )
        parser.add_argument(
            "--video_dir",
            help="Directory to write video",
        )
        parser.add_argument(
            "--config_file",
            help="Path to the custom configuration file",
        )
        parser.add_argument(
            "-v", "--version",
            action="store_true",
            help="Display the version of manimgl"
        )
        parser.add_argument(
            "--log-level",
            help="Level of messages to Display, can be DEBUG / INFO / WARNING / ERROR / CRITICAL"
        )
        parser.add_argument(
            "--clear-cache",
            action="store_true",
            help="Erase the cache used for Tex and Text Mobjects"
        )
        parser.add_argument(
            "--autoreload",
            action="store_true",
            help="Automatically reload Python modules to pick up code changes " +
                 "across different files",
        )
        args = parser.parse_args()
        args.write_file = any([args.write_file, args.open, args.finder])
        return args
    except argparse.ArgumentError as err:
        log.error(str(err))
        sys.exit(2)


def update_directory_config(config: Dict):
    dir_config = config.directories
    base = dir_config.base
    for key, subdir in dir_config.subdirs.items():
        dir_config[key] = os.path.join(base, subdir)


def update_window_config(config: Dict, args: Namespace):
    window_config = config.window
    for key in "position", "size":
        if window_config.get(key):
            window_config[key] = literal_eval(window_config[key])
    if args.full_screen:
        window_config.full_screen = True


def update_camera_config(config: Dict, args: Namespace):
    camera_config = config.camera
    arg_resolution = get_resolution_from_args(args, config.resolution_options)
    camera_config.resolution = arg_resolution or literal_eval(camera_config.resolution)
    if args.fps:
        camera_config.fps = args.fps
    if args.color:
        try:
            camera_config.background_color = colour.Color(args.color)
        except Exception:
            log.error("Please use a valid color")
            log.error(err)
            sys.exit(2)
    if args.transparent:
        camera_config.background_opacity = 0.0


def update_file_writer_config(config: Dict, args: Namespace):
    file_writer_config = config.file_writer
    file_writer_config.update(
        write_to_movie=(not args.skip_animations and args.write_file),
        subdivide_output=args.subdivide,
        save_last_frame=(args.skip_animations and args.write_file),
        png_mode=("RGBA" if args.transparent else "RGB"),
        movie_file_extension=(get_file_ext(args)),
        output_directory=get_output_directory(args, config),
        file_name=args.file_name,
        open_file_upon_completion=args.open,
        show_file_location_upon_completion=args.finder,
        quiet=args.quiet,
    )

    if args.vcodec:
        file_writer_config.video_codec = args.vcodec
    elif args.transparent:
        file_writer_config.video_codec = 'prores_ks'
        file_writer_config.pixel_format = ''
    elif args.gif:
        file_writer_config.video_codec = ''

    if args.pix_fmt:
        file_writer_config.pixel_format = args.pix_fmt


def update_scene_config(config: Dict, args: Namespace):
    scene_config = config.scene
    start, end = get_animations_numbers(args)
    scene_config.update(
        # Note, Scene.__init__ makes use of both manimlib.camera and
        # manimlib.file_writer below, so the arguments here are just for
        # any future specifications beyond what the global configuration holds
        camera_config=dict(),
        file_writer_config=dict(),
        skip_animations=args.skip_animations,
        start_at_animation_number=start,
        end_at_animation_number=end,
        presenter_mode=args.presenter_mode,
    )
    if args.leave_progress_bars:
        scene_config.leave_progress_bars = True
    if args.show_animation_progress:
        scene_config.show_animation_progress = True


def update_run_config(config: Dict, args: Namespace):
    config.run = Dict(
        file_name=args.file,
        embed_line=(int(args.embed) if args.embed is not None else None),
        is_reload=False,
        prerun=args.prerun,
        scene_names=args.scene_names,
        quiet=args.quiet or args.write_all,
        write_all=args.write_all,
        show_in_window=not args.write_file
    )


def update_embed_config(config: Dict, args: Namespace):
    if args.autoreload:
        config.embed.autoreload = True


# Helpers for the functions above


def load_yaml(file_path: str):
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        return {}


def get_manim_dir():
    manimlib_module = importlib.import_module("manimlib")
    manimlib_dir = os.path.dirname(inspect.getabsfile(manimlib_module))
    return os.path.abspath(os.path.join(manimlib_dir, ".."))


def get_resolution_from_args(args: Optional[Namespace], resolution_options: dict) -> Optional[tuple[int, int]]:
    if args.resolution:
        return tuple(map(int, args.resolution.split("x")))
    if args.low_quality:
        return literal_eval(resolution_options["low"])
    if args.medium_quality:
        return literal_eval(resolution_options["med"])
    if args.hd:
        return literal_eval(resolution_options["high"])
    if args.uhd:
        return literal_eval(resolution_options["4k"])
    return None


def get_file_ext(args: Namespace) -> str:
    if args.transparent:
        file_ext = ".mov"
    elif args.gif:
        file_ext = ".gif"
    else:
        file_ext = ".mp4"
    return file_ext


def get_animations_numbers(args: Namespace) -> tuple[int | None, int | None]:
    stan = args.start_at_animation_number
    if stan is None:
        return (None, None)
    elif "," in stan:
        return tuple(map(int, stan.split(",")))
    else:
        return int(stan), None


def get_output_directory(args: Namespace, config: Dict) -> str:
    dir_config = config.directories
    out_dir = args.video_dir or dir_config.output
    if dir_config.mirror_module_path and args.file:
        file_path = Path(args.file).absolute()
        rel_path = file_path.relative_to(dir_config.removed_mirror_prefix)
        rel_path = Path(str(rel_path).lstrip("_"))
        out_dir = Path(out_dir, rel_path).with_suffix("")
    return out_dir


# Create global configuration
manim_config: Dict = initialize_manim_config()
