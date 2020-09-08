"""
logger.py
---------
This is the logging library for manim.
This library uses rich for coloured log outputs.

"""


__all__ = ["logger", "console"]


import configparser
import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
from rich import print as printf
from rich import errors, color

from .config_utils import _run_config


def parse_theme(fp):
    config_parser.read(fp)
    theme = dict(config_parser["logger"])
    # replaces `_` by `.` as rich understands it
    theme = dict(
        zip([key.replace("_", ".") for key in theme.keys()], list(theme.values()))
    )

    theme["log.width"] = None if theme["log.width"] == "-1" else int(theme["log.width"])

    theme["log.height"] = (
        None if theme["log.height"] == "-1" else int(theme["log.height"])
    )
    theme["log.timestamps"] = config_parser["logger"].getboolean("log.timestamps")
    try:
        customTheme = Theme(
            {
                k: v
                for k, v in theme.items()
                if k not in ["log.width", "log.height", "log.timestamps"]
            }
        )
    except (color.ColorParseError, errors.StyleSyntaxError):
        customTheme = None
        printf(
            "[logging.level.error]It seems your colour configuration couldn't be parsed. Loading the default color configuration...[/logging.level.error]"
        )
    return customTheme, theme


config_items = _run_config()
config_parser, successfully_read_files = config_items[1], config_items[-1]
try:
    customTheme, themedict = parse_theme(successfully_read_files)
    console = Console(
        theme=customTheme,
        record=True,
        height=themedict["log.height"],
        width=themedict["log.width"],
    )
except KeyError:
    console = Console(record=True)
    printf(
        "[logging.level.warning]No cfg file found, creating one in "
        + successfully_read_files[0]
        + " [/logging.level.warning]"
    )

# These keywords Are Highlighted specially.
RichHandler.KEYWORDS = [
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
logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, show_time=themedict["log.timestamps"])],
)

logger = logging.getLogger("rich")

# TODO : This is only temporary to keep the terminal output clean when working with ImageMobject and matplotlib plots
logging.getLogger("PIL").setLevel(logging.INFO)
logging.getLogger("matplotlib").setLevel(logging.INFO)
