"""
logger.py
---------
This is the logging library for manim.
This library uses rich for coloured log outputs.

"""


__all__ = ["logger", "console"]


import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
from rich.traceback import install
from rich import print as printf
from rich import errors, color
import json
import copy


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


def _parse_theme(config_logger):
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
        customTheme = None
        printf(
            "[logging.level.error]It seems your colour configuration couldn't be parsed. Loading the default color configuration...[/logging.level.error]"
        )
    return customTheme


def set_rich_logger(config_logger, verbosity):
    """Will set the RichHandler of the logger.

    Parameter
    ----------
    config_logger :class:
        Config object of the logger.
    """
    theme = _parse_theme(config_logger)
    global console
    console = Console(theme=theme)
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
    rich_handler = RichHandler(
        console=console, show_time=config_logger.getboolean("log_timestamps")
    )
    global logger
    rich_handler.setLevel(verbosity)
    logger.addHandler(rich_handler)


def set_file_logger(log_file_path):
    file_handler = logging.FileHandler(log_file_path, mode="w")
    file_handler.setFormatter(JSONFormatter())
    global logger
    logger.addHandler(file_handler)


logger = logging.getLogger("manim")
# The console is set to None as it will be changed by set_rich_logger.
console = None
install()
# TODO : This is only temporary to keep the terminal output clean when working with ImageMobject and matplotlib plots
logging.getLogger("PIL").setLevel(logging.INFO)
logging.getLogger("matplotlib").setLevel(logging.INFO)
