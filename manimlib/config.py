from __future__ import annotations

import argparse
import colour
import importlib
import inspect
import os
import sys
import yaml
from ast import literal_eval

from functools import lru_cache

from manimlib.logger import log
from manimlib.utils.dict_ops import merge_dicts_recursively
from manimlib.utils.init_config import init_customization

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from argparse import Namespace
    from typing import Optional


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
            help="Render at a low quality (for faster rendering)",
        )
        parser.add_argument(
            "-m", "--medium_quality",
            action="store_true",
            help="Render at a medium quality",
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
            "-g", "--save_pngs",
            action="store_true",
            help="Save each frame as a png",
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
            "--config",
            action="store_true",
            help="Guide for automatic configuration",
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
            help="Creates a new file where the line `self.embed` is inserted " + \
                 "at the corresponding line number"
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
        args = parser.parse_args()
        args.write_file = any([args.write_file, args.open, args.finder])
        return args
    except argparse.ArgumentError as err:
        log.error(str(err))
        sys.exit(2)


def get_manim_dir():
    manimlib_module = importlib.import_module("manimlib")
    manimlib_dir = os.path.dirname(inspect.getabsfile(manimlib_module))
    return os.path.abspath(os.path.join(manimlib_dir, ".."))


def load_yaml(file_path: str):
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        return {}


@lru_cache
def get_global_config():
    args = parse_cli()
    global_defaults_file = os.path.join(get_manim_dir(), "manimlib", "default_config.yml")
    config = merge_dicts_recursively(
        load_yaml(global_defaults_file),
        load_yaml("custom_config.yml"),  # From current working directory
        load_yaml(args.config_file) if args.config_file else {},
    )

    # Set the subdirectories
    base = config['directories']['base']
    for key, subdir in config['directories']['subdirs'].items():
        config['directories'][key] = os.path.join(base, subdir)

    return config


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


def get_output_directory(args: Namespace, global_config: dict) -> str:
    dir_config = global_config["directories"]
    output_directory = args.video_dir or dir_config["output"]
    if dir_config["mirror_module_path"] and args.file:
        to_cut = dir_config["removed_mirror_prefix"]
        ext = os.path.abspath(args.file)
        ext = ext.replace(to_cut, "").replace(".py", "")
        if ext.startswith("_"):
            ext = ext[1:]
        output_directory = os.path.join(output_directory, ext)
    return output_directory


def get_file_writer_config(args: Namespace, global_config: dict) -> dict:
    result = {
        "write_to_movie": not args.skip_animations and args.write_file,
        "save_last_frame": args.skip_animations and args.write_file,
        "save_pngs": args.save_pngs,
        # If -t is passed in (for transparent), this will be RGBA
        "png_mode": "RGBA" if args.transparent else "RGB",
        "movie_file_extension": get_file_ext(args),
        "output_directory": get_output_directory(args, global_config),
        "file_name": args.file_name,
        "input_file_path": args.file or "",
        "open_file_upon_completion": args.open,
        "show_file_location_upon_completion": args.finder,
        "quiet": args.quiet,
        **global_config["file_writer"],
    }

    if args.vcodec:
        result["video_codec"] = args.vcodec
    elif args.transparent:
        result["video_codec"] = 'prores_ks'
        result["pixel_format"] = ''
    elif args.gif:
        result["video_codec"] = ''

    if args.pix_fmt:
        result["pixel_format"] = args.pix_fmt

    return result


def get_resolution(args: Optional[Namespace] = None, global_config: Optional[dict] = None):
    args = args or parse_cli()
    global_config = global_config or get_global_config()

    resolution_options = global_config["resolution_options"]
    if args.resolution:
        resolution = tuple(map(int, args.resolution.split("x")))
    elif args.low_quality:
        resolution = resolution_options["low"]
    elif args.medium_quality:
        resolution = resolution_options["med"]
    elif args.hd:
        resolution = resolution_options["high"]
    elif args.uhd:
        resolution = resolution_options["4k"]
    else:
        resolution = global_config["camera"]["resolution"]

    if isinstance(resolution, str):
        resolution = literal_eval(resolution)

    return resolution


def get_window_config(args: Namespace, global_config: dict) -> dict:
    window_config = global_config["window"]
    # Todo, this correction of configuration should maybe happen elsewhere
    for key in "position", "size":
        if window_config.get(key):
            window_config[key] = literal_eval(window_config[key])
    if args.full_screen:
        window_config["full_screen"] = True
    return window_config


def get_camera_config(args: Optional[Namespace] = None, global_config: Optional[dict] = None) -> dict:
    args = args or parse_cli()
    global_config = global_config or get_global_config()

    camera_config = global_config["camera"]

    # All of this should be taken care of during some initialization of global_config
    camera_config["resolution"] = get_resolution(args, global_config)
    if args.fps:
        camera_config["fps"] = args.fps
    if args.color:
        try:
            camera_config["background_color"] = colour.Color(args.color)
        except Exception:
            log.error("Please use a valid color")
            log.error(err)
            sys.exit(2)
    if args.transparent:
        camera_config["background_opacity"] = 0.0

    return camera_config


def get_scene_config(args: Namespace) -> dict:
    """
    Returns a dictionary to be used as key word arguments for Scene
    """
    global_config = get_global_config()
    camera_config = get_camera_config(args, global_config)
    file_writer_config = get_file_writer_config(args, global_config)
    start, end = get_animations_numbers(args)

    return {
        "file_writer_config": file_writer_config,
        "camera_config": camera_config,
        "skip_animations": args.skip_animations,
        "start_at_animation_number": start,
        "end_at_animation_number": end,
        "presenter_mode": args.presenter_mode,
        "leave_progress_bars": args.leave_progress_bars,
        "show_animation_progress": args.show_animation_progress,
        "embed_exception_mode": global_config["embed_exception_mode"],
        "embed_error_sound": global_config["embed_error_sound"],
    }


def get_run_config(args: Namespace):
    window_config = get_window_config(args, get_global_config())
    return {
        "file_name": args.file,
        "embed_line": int(args.embed) if args.embed is not None else None,
        "is_reload": False,
        "prerun": args.prerun,
        "scene_names": args.scene_names,
        "quiet": args.quiet or args.write_all,
        "write_all": args.write_all,
        "window_config": window_config,
        "show_in_window": not args.write_file
    }
