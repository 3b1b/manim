"""
utils.py
--------

Functions to create the logger and config.

"""

import os
import sys
import logging
from pathlib import Path
import configparser
import json
import copy

import colour
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
from rich import print as printf
from rich import errors, color

from .. import constants
from ..utils.tex import TexTemplate, TexTemplateFromFile

HIGHLIGHTED_KEYWORDS = [  # these keywords are highlighted specially
    "Played",
    "animations",
    "scene",
    "Reading",
    "Writing",
    "script",
    "arguments",
    "Invalid",
    "Aborting",
    "module",
    "File",
    "Rendering",
    "Rendered",
]

WRONG_COLOR_CONFIG_MSG = """
[logging.level.error]Your colour configuration couldn't be parsed.
Loading the default color configuration.[/logging.level.error]
"""


def config_file_paths():
    library_wide = Path.resolve(Path(__file__).parent / "default.cfg")
    if sys.platform.startswith("win32"):
        user_wide = Path.home() / "AppData" / "Roaming" / "Manim" / "manim.cfg"
    else:
        user_wide = Path.home() / ".config" / "manim" / "manim.cfg"
    folder_wide = Path("manim.cfg")
    return [library_wide, user_wide, folder_wide]


def make_config_parser():
    """Make a ConfigParser object and load the .cfg files."""
    library_wide, user_wide, folder_wide = config_file_paths()
    # From the documentation: "An application which requires initial values to
    # be loaded from a file should load the required file or files using
    # read_file() before calling read() for any optional files."
    # https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.read
    parser = configparser.ConfigParser()
    with open(library_wide) as file:
        parser.read_file(file)
    parser.read([user_wide, folder_wide])
    return parser


def make_logger(parser, verbosity):
    """Make the manim logger and the console."""
    # Throughout the codebase, use Console.print() instead of print()
    theme = parse_theme(parser)
    console = Console(theme=theme)

    # set the rich handler
    RichHandler.KEYWORDS = HIGHLIGHTED_KEYWORDS
    rich_handler = RichHandler(
        console=console, show_time=parser.getboolean("log_timestamps")
    )
    rich_handler.setLevel(verbosity)

    # finally, the logger
    logger = logging.getLogger("manim")
    logger.addHandler(rich_handler)

    return logger, console


def parse_theme(config_logger):
    theme = dict(
        zip(
            [key.replace("_", ".") for key in config_logger.keys()],
            list(config_logger.values()),
        )
    )

    theme["log.width"] = None if theme["log.width"] == "-1" else int(theme["log.width"])

    theme["log.height"] = (
        None if theme["log.height"] == "-1" else int(theme["log.height"])
    )
    theme["log.timestamps"] = False
    try:
        customTheme = Theme(
            {
                k: v
                for k, v in theme.items()
                if k not in ["log.width", "log.height", "log.timestamps"]
            }
        )
    except (color.ColorParseError, errors.StyleSyntaxError):
        printf(WRONG_COLOR_CONFIG_MSG)
        customTheme = None

    return customTheme


def make_config(parser):
    """Parse config files into a single dictionary exposed to the user."""
    # By default, use the CLI section of the digested .cfg files
    default = parser["CLI"]

    # Loop over [low_quality] for the keys, but get the values from [CLI]
    config = {opt: default.getint(opt) for opt in parser["low_quality"]}

    # Set the rest of the frame properties
    config["default_pixel_height"] = default.getint("pixel_height")
    config["default_pixel_width"] = default.getint("pixel_width")
    config["background_color"] = colour.Color(default["background_color"])
    config["frame_height"] = 8.0
    config["frame_width"] = (
        config["frame_height"] * config["pixel_width"] / config["pixel_height"]
    )
    config["frame_y_radius"] = config["frame_height"] / 2
    config["frame_x_radius"] = config["frame_width"] / 2
    config["top"] = config["frame_y_radius"] * constants.UP
    config["bottom"] = config["frame_y_radius"] * constants.DOWN
    config["left_side"] = config["frame_x_radius"] * constants.LEFT
    config["right_side"] = config["frame_x_radius"] * constants.RIGHT

    # Tex template
    tex_fn = None if not default["tex_template"] else default["tex_template"]
    if tex_fn is not None and not os.access(tex_fn, os.R_OK):
        # custom template not available, fallback to default
        logging.getLogger("manim").warning(
            f"Custom TeX template {tex_fn} not found or not readable. "
            "Falling back to the default template."
        )
        tex_fn = None
    config["tex_template_file"] = tex_fn
    config["tex_template"] = (
        TexTemplate() if not tex_fn else TexTemplateFromFile(filename=tex_fn)
    )

    # Choose the renderer
    config["use_js_renderer"] = default.getboolean("use_js_renderer")
    config["js_renderer_path"] = default.get("js_renderer_path")

    return config


def make_file_writer_config(parser, config):
    """Parse config files into a single dictionary used internally."""
    # By default, use the CLI section of the digested .cfg files
    default = parser["CLI"]

    # This will be the final file_writer_config dict exposed to the user
    fw_config = {}

    # These may be overriden by CLI arguments
    fw_config["input_file"] = ""
    fw_config["scene_names"] = ""
    fw_config["output_file"] = ""
    fw_config["custom_folders"] = False

    # Note ConfigParser options are all strings and each needs to be converted
    # to the appropriate type.
    for boolean_opt in [
        "preview",
        "show_in_file_browser",
        "leave_progress_bars",
        "write_to_movie",
        "save_last_frame",
        "save_pngs",
        "save_as_gif",
        "write_all",
        "disable_caching",
        "flush_cache",
        "log_to_file",
        "progress_bar",
    ]:
        fw_config[boolean_opt] = default.getboolean(boolean_opt)

    for str_opt in [
        "png_mode",
        "movie_file_extension",
        "background_opacity",
    ]:
        fw_config[str_opt] = default.get(str_opt)

    for int_opt in [
        "from_animation_number",
        "upto_animation_number",
    ]:
        fw_config[int_opt] = default.getint(int_opt)
    if fw_config["upto_animation_number"] == -1:
        fw_config["upto_animation_number"] = float("inf")

    # for str_opt in ['media_dir', 'video_dir', 'tex_dir', 'text_dir']:
    for str_opt in ["media_dir", "log_dir"]:
        fw_config[str_opt] = Path(default[str_opt]).relative_to(".")
    dir_names = {
        "video_dir": "videos",
        "images_dir": "images",
        "tex_dir": "Tex",
        "text_dir": "texts",
    }
    for name in dir_names:
        fw_config[name] = fw_config["media_dir"] / dir_names[name]

    if not fw_config["write_to_movie"]:
        fw_config["disable_caching"] = True

    if config["use_js_renderer"]:
        file_writer_config["disable_caching"] = True

    # Read in the streaming section -- all values are strings
    fw_config["streaming"] = {
        opt: parser["streaming"].get(opt) for opt in parser["streaming"]
    }

    # For internal use (no CLI flag)
    fw_config["skip_animations"] = fw_config["save_last_frame"]
    fw_config["max_files_cached"] = default.getint("max_files_cached")
    if fw_config["max_files_cached"] == -1:
        fw_config["max_files_cached"] = float("inf")

    # Parse the verbosity flag to read in the log level
    fw_config["verbosity"] = default["verbosity"]

    # Parse the ffmpeg log level in the config
    ffmpeg_loglevel = parser["ffmpeg"].get("loglevel", None)
    fw_config["ffmpeg_loglevel"] = (
        constants.FFMPEG_VERBOSITY_MAP[fw_config["verbosity"]]
        if ffmpeg_loglevel is None
        else ffmpeg_loglevel
    )

    return fw_config


class JSONFormatter(logging.Formatter):
    """Subclass of `:class:`logging.Formatter`, to build our own format of the logs (JSON)."""

    def format(self, record):
        record_c = copy.deepcopy(record)
        if record_c.args:
            for arg in record_c.args:
                record_c.args[arg] = "<>"
        return json.dumps(
            {
                "levelname": record_c.levelname,
                "module": record_c.module,
                "message": super().format(record_c),
            }
        )
