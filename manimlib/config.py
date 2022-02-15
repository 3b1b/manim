import argparse
import colour
import inspect
import importlib
import os
import sys
import yaml
from contextlib import contextmanager
from screeninfo import get_monitors

from manimlib.utils.config_ops import merge_dicts_recursively
from manimlib.utils.init_config import init_customization
from manimlib.logger import log


__config_file__ = "custom_config.yml"


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
            help="Scene will stay paused during wait calls until "
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
            help="Start rendering not from the first animation, but"
                 "from another, specified by its index.  If you pass"
                 "in two comma separated values, e.g. \"3,6\", it will end"
                 "the rendering at the second value",
        )
        parser.add_argument(
            "-e", "--embed", metavar="LINENO",
            help="Takes a line number as an argument, and results"
                 "in the scene being called as if the line `self.embed()`"
                 "was inserted into the scene code at that line number."
        )
        parser.add_argument(
            "-r", "--resolution",
            help="Resolution, passed as \"WxH\", e.g. \"1920x1080\"",
        )
        parser.add_argument(
            "--frame_rate",
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
        return args
    except argparse.ArgumentError as err:
        log.error(str(err))
        sys.exit(2)


def get_manim_dir():
    manimlib_module = importlib.import_module("manimlib")
    manimlib_dir = os.path.dirname(inspect.getabsfile(manimlib_module))
    return os.path.abspath(os.path.join(manimlib_dir, ".."))


def get_module(file_name):
    if file_name is None:
        return None
    module_name = file_name.replace(os.sep, ".").replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, file_name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def insert_embed_line(file_name, lineno):
    with open(file_name, 'r') as fp:
        lines = fp.readlines()
    line = lines[lineno - 1]
    n_spaces = len(line) - len(line.lstrip())
    lines.insert(lineno, " " * n_spaces + "self.embed()\n")

    alt_file = file_name.replace(".py", "_inserted_embed.py")
    with open(alt_file, 'w') as fp:
        fp.writelines(lines)

    try:
        yield alt_file
    finally:
        os.remove(alt_file)


def get_custom_config():
    global __config_file__

    global_defaults_file = os.path.join(get_manim_dir(), "manimlib", "default_config.yml")

    if os.path.exists(global_defaults_file):
        with open(global_defaults_file, "r") as file:
            config = yaml.safe_load(file)

        if os.path.exists(__config_file__):
            with open(__config_file__, "r") as file:
                local_defaults = yaml.safe_load(file)
            if local_defaults:
                config = merge_dicts_recursively(
                    config,
                    local_defaults,
                )
    else:
        with open(__config_file__, "r") as file:
            config = yaml.safe_load(file)

    return config


def check_temporary_storage(config):
    if config["directories"]["temporary_storage"] == "" and sys.platform == "win32":
        log.warning(
            "You may be using Windows platform and have not specified the path of"
            " `temporary_storage`, which may cause OSError. So it is recommended"
            " to specify the `temporary_storage` in the config file (.yml)"
        )


def get_configuration(args):
    global __config_file__

    # ensure __config_file__ always exists
    if args.config_file is not None:
        if not os.path.exists(args.config_file):
            log.error(f"Can't find {args.config_file}.")
            if sys.platform == 'win32':
                log.info(f"Copying default configuration file to {args.config_file}...")
                os.system(f"copy default_config.yml {args.config_file}")
            elif sys.platform in ["linux2", "darwin"]:
                log.info(f"Copying default configuration file to {args.config_file}...")
                os.system(f"cp default_config.yml {args.config_file}")
            else:
                log.info("Please create the configuration file manually.")
            log.info("Read configuration from default_config.yml.")
        else:
            __config_file__ = args.config_file

    global_defaults_file = os.path.join(get_manim_dir(), "manimlib", "default_config.yml")

    if not (os.path.exists(global_defaults_file) or os.path.exists(__config_file__)):
        log.info("There is no configuration file detected. Switch to the config file initializer:")
        init_customization()

    elif not os.path.exists(__config_file__):
        log.info(f"Using the default configuration file, which you can modify in `{global_defaults_file}`")
        log.info(
            "If you want to create a local configuration file, you can create a file named"
            f" `{__config_file__}`, or run `manimgl --config`"
        )

    custom_config = get_custom_config()
    check_temporary_storage(custom_config)

    write_file = any([args.write_file, args.open, args.finder])
    if args.transparent:
        file_ext = ".mov"
    elif args.gif:
        file_ext = ".gif"
    else:
        file_ext = ".mp4"

    file_writer_config = {
        "write_to_movie": not args.skip_animations and write_file,
        "break_into_partial_movies": custom_config["break_into_partial_movies"],
        "save_last_frame": args.skip_animations and write_file,
        "save_pngs": args.save_pngs,
        # If -t is passed in (for transparent), this will be RGBA
        "png_mode": "RGBA" if args.transparent else "RGB",
        "movie_file_extension": file_ext,
        "mirror_module_path": custom_config["directories"]["mirror_module_path"],
        "output_directory": args.video_dir or custom_config["directories"]["output"],
        "file_name": args.file_name,
        "input_file_path": args.file or "",
        "open_file_upon_completion": args.open,
        "show_file_location_upon_completion": args.finder,
        "quiet": args.quiet,
    }

    if args.embed is None:
        module = get_module(args.file)
    else:
        with insert_embed_line(args.file, int(args.embed)) as alt_file:
            module = get_module(alt_file)

    config = {
        "module": module,
        "scene_names": args.scene_names,
        "file_writer_config": file_writer_config,
        "quiet": args.quiet or args.write_all,
        "write_all": args.write_all,
        "skip_animations": args.skip_animations,
        "start_at_animation_number": args.start_at_animation_number,
        "end_at_animation_number": None,
        "preview": not write_file,
        "presenter_mode": args.presenter_mode,
        "leave_progress_bars": args.leave_progress_bars,
    }

    # Camera configuration
    config["camera_config"] = get_camera_configuration(args, custom_config)

    # Default to making window half the screen size
    # but make it full screen if -f is passed in
    monitors = get_monitors()
    mon_index = custom_config["window_monitor"]
    monitor = monitors[min(mon_index, len(monitors) - 1)]
    window_width = monitor.width
    if not (args.full_screen or custom_config["full_screen"]):
        window_width //= 2
    window_height = window_width * 9 // 16
    config["window_config"] = {
        "size": (window_width, window_height),
    }

    # Arguments related to skipping
    stan = config["start_at_animation_number"]
    if stan is not None:
        if "," in stan:
            start, end = stan.split(",")
            config["start_at_animation_number"] = int(start)
            config["end_at_animation_number"] = int(end)
        else:
            config["start_at_animation_number"] = int(stan)

    return config


def get_camera_configuration(args, custom_config):
    camera_config = {}
    camera_qualities = get_custom_config()["camera_qualities"]
    if args.low_quality:
        quality = camera_qualities["low"]
    elif args.medium_quality:
        quality = camera_qualities["medium"]
    elif args.hd:
        quality = camera_qualities["high"]
    elif args.uhd:
        quality = camera_qualities["ultra_high"]
    else:
        quality = camera_qualities[camera_qualities["default_quality"]]

    if args.resolution:
        quality["resolution"] = args.resolution
    if args.frame_rate:
        quality["frame_rate"] = int(args.frame_rate)

    width_str, height_str = quality["resolution"].split("x")
    width = int(width_str)
    height = int(height_str)

    camera_config.update({
        "pixel_width": width,
        "pixel_height": height,
        "frame_rate": quality["frame_rate"],
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
