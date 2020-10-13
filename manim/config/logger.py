"""
logger.py
---------

Functions to create and set the logger.

"""

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
