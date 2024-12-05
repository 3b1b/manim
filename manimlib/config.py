from __future__ import annotations

import argparse
from argparse import Namespace
import colour
import importlib
import inspect
import os
import screeninfo
import sys
import yaml

from functools import lru_cache

from manimlib.logger import log
from manimlib.utils.dict_ops import merge_dicts_recursively
from manimlib.utils.init_config import init_customization

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    Module = importlib.util.types.ModuleType
    from typing import Optional


# This has to be here instead of in constants.py
# due to its use in creating the camera configuration
FRAME_HEIGHT: float = 8.0


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
            nargs="?",
            const="",
            help="Creates a new file where the line `self.embed` is inserted " + \
                 "into the Scenes construct method. " + \
                 "If a string is passed in, the line will be inserted below the " + \
                 "last line of code including that string."
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
            "--autoreload",
            action="store_true",
            help="Automatically reload Python modules to pick up code changes"
            + " across different files",
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


def get_module(file_name: str | None) -> Module:
    if file_name is None:
        return None
    module_name = file_name.replace(os.sep, ".").replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, file_name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_indent(line: str):
    return len(line) - len(line.lstrip())


def get_module_with_inserted_embed_line(
    file_name: str, scene_name: str, line_marker: str
):
    """
    This is hacky, but convenient. When user includes the argument "-e", it will try
    to recreate a file that inserts the line `self.embed()` into the end of the scene's
    construct method. If there is an argument passed in, it will insert the line after
    the last line in the sourcefile which includes that string.
    """
    with open(file_name, 'r') as fp:
        lines = fp.readlines()

    try:
        scene_line_number = next(
            i for i, line in enumerate(lines)
            if line.startswith(f"class {scene_name}")
        )
    except StopIteration:
        log.error(f"No scene {scene_name}")
        return

    prev_line_num = -1
    n_spaces = None
    if len(line_marker) == 0:
        # Find the end of the construct method
        in_construct = False
        for index in range(scene_line_number, len(lines) - 1):
            line = lines[index]
            if line.lstrip().startswith("def construct"):
                in_construct = True
                n_spaces = get_indent(line) + 4
            elif in_construct:
                if len(line.strip()) > 0 and get_indent(line) < (n_spaces or 0):
                    prev_line_num = index - 1
                    break
        if prev_line_num < 0:
            prev_line_num = len(lines) - 1
    elif line_marker.isdigit():
        # Treat the argument as a line number
        prev_line_num = int(line_marker) - 1
    elif len(line_marker) > 0:
        # Treat the argument as a string
        try:
            prev_line_num = next(
                i
                for i in range(scene_line_number, len(lines) - 1)
                if line_marker in lines[i]
            )
        except StopIteration:
            log.error(f"No lines matching {line_marker}")
            sys.exit(2)

    # Insert the embed line, rewrite file, then write it back when done
    if n_spaces is None:
        n_spaces = get_indent(lines[prev_line_num])
    inserted_line = " " * n_spaces + "self.embed()\n"
    new_lines = list(lines)
    new_lines.insert(prev_line_num + 1, inserted_line)
    new_file = file_name.replace(".py", "_insert_embed.py")

    with open(new_file, 'w') as fp:
        fp.writelines(new_lines)

    module = get_module(new_file)
    # This is to pretend the module imported from the edited lines
    # of code actually comes from the original file.
    module.__file__ = file_name

    os.remove(new_file)

    return module


def get_scene_module(args: Namespace) -> Module:
    if args.embed is None:
        return get_module(args.file)
    else:
        return get_module_with_inserted_embed_line(
            args.file, args.scene_names[0], args.embed
        )


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


def get_output_directory(args: Namespace, custom_config: dict) -> str:
    dir_config = custom_config["directories"]
    output_directory = args.video_dir or dir_config["output"]
    if dir_config["mirror_module_path"] and args.file:
        to_cut = dir_config["removed_mirror_prefix"]
        ext = os.path.abspath(args.file)
        ext = ext.replace(to_cut, "").replace(".py", "")
        if ext.startswith("_"):
            ext = ext[1:]
        output_directory = os.path.join(output_directory, ext)
    return output_directory


def get_file_writer_config(args: Namespace, custom_config: dict) -> dict:
    result = {
        "write_to_movie": not args.skip_animations and args.write_file,
        "save_last_frame": args.skip_animations and args.write_file,
        "save_pngs": args.save_pngs,
        # If -t is passed in (for transparent), this will be RGBA
        "png_mode": "RGBA" if args.transparent else "RGB",
        "movie_file_extension": get_file_ext(args),
        "output_directory": get_output_directory(args, custom_config),
        "file_name": args.file_name,
        "input_file_path": args.file or "",
        "open_file_upon_completion": args.open,
        "show_file_location_upon_completion": args.finder,
        "quiet": args.quiet,
        **custom_config["file_writer_config"],
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


def get_window_config(args: Namespace, custom_config: dict, camera_config: dict) -> dict:
    # Default to making window half the screen size
    # but make it full screen if -f is passed in
    try:
        monitors = screeninfo.get_monitors()
    except screeninfo.ScreenInfoError:
        # Default fallback
        monitors = [screeninfo.Monitor(width=1920, height=1080)]
    mon_index = custom_config["window_monitor"]
    monitor = monitors[min(mon_index, len(monitors) - 1)]
    aspect_ratio = camera_config["pixel_width"] / camera_config["pixel_height"]
    window_width = monitor.width
    if not (args.full_screen or custom_config["full_screen"]):
        window_width //= 2
    window_height = int(window_width / aspect_ratio)
    return dict(size=(window_width, window_height))


def get_camera_config(args: Optional[Namespace] = None, custom_config: Optional[dict] = None) -> dict:
    if args is None:
        args = parse_cli()
    if custom_config is None:
        custom_config = get_global_config()

    camera_config = dict()
    camera_resolutions = custom_config["camera_resolutions"]
    if args.resolution:
        resolution = args.resolution
    elif args.low_quality:
        resolution = camera_resolutions["low"]
    elif args.medium_quality:
        resolution = camera_resolutions["med"]
    elif args.hd:
        resolution = camera_resolutions["high"]
    elif args.uhd:
        resolution = camera_resolutions["4k"]
    else:
        resolution = camera_resolutions[camera_resolutions["default_resolution"]]

    if args.fps:
        fps = int(args.fps)
    else:
        fps = custom_config["fps"]

    width_str, height_str = resolution.split("x")
    width = int(width_str)
    height = int(height_str)

    camera_config.update({
        "pixel_width": width,
        "pixel_height": height,
        "frame_config": {
            "frame_shape": ((width / height) * FRAME_HEIGHT, FRAME_HEIGHT),
        },
        "fps": fps,
    })

    try:
        bg_color = args.color or custom_config["style"]["background_color"]
        camera_config["background_color"] = colour.Color(bg_color)
    except ValueError as err:
        log.error("Please use a valid color")
        log.error(err)
        sys.exit(2)

    # If rendering a transparent image/move, make sure the
    # scene has a background opacity of 0
    if args.transparent:
        camera_config["background_opacity"] = 0

    return camera_config


def get_scene_config(args: Namespace) -> dict:
    """
    Returns a dictionary to be used as key word arguments for Scene
    """
    global_config = get_global_config()
    camera_config = get_camera_config(args, global_config)
    window_config = get_window_config(args, global_config, camera_config)
    start, end = get_animations_numbers(args)

    return {
        "file_writer_config": get_file_writer_config(args, global_config),
        "camera_config": camera_config,
        "window_config": window_config,
        "skip_animations": args.skip_animations,
        "start_at_animation_number": start,
        "end_at_animation_number": end,
        "preview": not args.write_file,
        "presenter_mode": args.presenter_mode,
        "leave_progress_bars": args.leave_progress_bars,
        "show_animation_progress": args.show_animation_progress,
        "embed_exception_mode": global_config["embed_exception_mode"],
        "embed_error_sound": global_config["embed_error_sound"],
    }


def get_run_config(args: Namespace):
    return {
        "module": get_scene_module(args),
        "prerun": args.prerun,
        "scene_names": args.scene_names,
        "quiet": args.quiet or args.write_all,
        "write_all": args.write_all,
    }
