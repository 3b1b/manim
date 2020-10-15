"""
logger.py
---------

Functions to create and set the logger.

"""

import os
import logging
import json
import copy

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
from rich import print as printf
from rich import errors, color

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

    # finally, the logger
    logger = logging.getLogger("manim")
    logger.addHandler(rich_handler)
    logger.setLevel(verbosity)

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


def set_file_logger(config, verbosity):
    # Note: The log file name will be
    # <name_of_animation_file>_<name_of_scene>.log, gotten from
    # file_writer_config.  So it can differ from the real name of the scene.
    # <name_of_scene> would only appear if scene name was provided when manim
    # was called.
    scene_name_suffix = "".join(config["scene_names"])
    scene_file_name = os.path.basename(config["input_file"]).split(".")[0]
    log_file_name = (
        f"{scene_file_name}_{scene_name_suffix}.log"
        if scene_name_suffix
        else f"{scene_file_name}.log"
    )
    log_file_path = os.path.join(config["log_dir"], log_file_name)
    file_handler = logging.FileHandler(log_file_path, mode="w")
    file_handler.setFormatter(JSONFormatter())

    logger = logging.getLogger('manim')
    logger.addHandler(file_handler)
    logger.info("Log file will be saved in %(logpath)s", {"logpath": log_file_path})
    logger.setLevel(verbosity)


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
