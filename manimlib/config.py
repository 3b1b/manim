import argparse
import colour
import inspect
import importlib
import os
import sys
import yaml
from screeninfo import get_monitors


def parse_cli():
    try:
        parser = argparse.ArgumentParser()
        module_location = parser.add_mutually_exclusive_group()
        module_location.add_argument(
            "file",
            nargs="?",
            help="path to file holding the python code for the scene",
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
            "-g", "--save_pngs",
            action="store_true",
            help="Save each frame as a png",
        )
        parser.add_argument(
            "-i", "--save_as_gif",
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
            help="directory to write video",
        )
        args = parser.parse_args()
        return args
    except argparse.ArgumentError as err:
        print(str(err))
        sys.exit(2)


def get_manim_dir():
    return os.path.dirname(inspect.getabsfile(importlib.import_module("manim")))


def get_module(file_name):
    if file_name is None:
        return None
    else:
        module_name = file_name.replace(os.sep, ".").replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, file_name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def get_custom_defaults():
    # See if there's a custom_defaults file in current directory,
    # otherwise fall back on the one in manimlib
    filename = "custom_defaults.yml"
    if not os.path.exists(filename):
        filename = os.path.join(get_manim_dir(), filename)

    with open(filename, "r") as file:
        custom_defaults = yaml.safe_load(file)
    return custom_defaults


def get_configuration(args):
    custom_defaults = get_custom_defaults()

    write_file = any([args.write_file, args.open, args.finder])
    file_writer_config = {
        "write_to_movie": not args.skip_animations and write_file,
        "save_last_frame": args.skip_animations and write_file,
        "save_pngs": args.save_pngs,
        "save_as_gif": args.save_as_gif,
        # If -t is passed in (for transparent), this will be RGBA
        "png_mode": "RGBA" if args.transparent else "RGB",
        "movie_file_extension": ".mov" if args.transparent else ".mp4",
        "mirror_module_path": custom_defaults["directories"]["mirror_module_path"],
        "output_directory": args.video_dir or custom_defaults["directories"]["output"],
        "file_name": args.file_name,
        "input_file_path": args.file or "",
        "open_file_upon_completion": args.open,
        "show_file_location_upon_completion": args.finder,
        "quiet": args.quiet,
    }

    module = get_module(args.file)
    config = {
        "module": module,
        "scene_names": args.scene_names,
        "file_writer_config": file_writer_config,
        "quiet": args.quiet or args.write_all,
        "write_all": args.write_all,
        "start_at_animation_number": args.start_at_animation_number,
        "preview": not write_file,
        "end_at_animation_number": None,
        "leave_progress_bars": args.leave_progress_bars,
    }

    # Camera configuration
    config["camera_config"] = get_camera_configuration(args, custom_defaults)

    # Default to putting window in the upper right of screen,
    # but make it full screen if -f is passed in
    monitor = get_monitors()[0]
    if args.full_screen:
        window_width = monitor.width
    else:
        window_width = monitor.width / 2
    window_height = window_width * 9 / 16
    window_position = (int(monitor.width - window_width), 0)
    config["window_config"] = {
        "size": (window_width, window_height),
        "position": window_position,
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

    config["skip_animations"] = any([
        args.skip_animations,
        args.start_at_animation_number,
    ])
    return config


def get_camera_configuration(args, custom_defaults):
    camera_config = {}
    camera_qualities = get_custom_defaults()["camera_qualities"]
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
        bg_color = args.color or custom_defaults["style"]["background_color"]
        camera_config["background_color"] = colour.Color(bg_color)
    except AttributeError as err:
        print("Please use a valid color")
        print(err)
        sys.exit(2)

    # If rendering a transparent image/move, make sure the
    # scene has a background opacity of 0
    if args.transparent:
        camera_config["background_opacity"] = 0

    return camera_config
