"""
logger.py
---------
This is the logging library for manim.
This library uses rich for coloured log outputs.

"""
import configparser
import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
from rich import print as printf
from rich import errors, color

from .utils.config_utils import _run_config


def parse_theme(fp):
    config_parser.read(fp)
    theme = dict(config_parser["logger"])
    # replaces `_` by `.` as rich understands it
    for key in theme:
        temp = theme[key]
        del theme[key]
        key = key.replace("_", ".")
        theme[key] = temp
    try:
        customTheme = Theme(theme)
    except (color.ColorParseError, errors.StyleSyntaxError):
        customTheme = None
        printf(
            "[logging.level.error]It seems your colour configuration couldn't be parsed. Loading the default color configuration...[/logging.level.error]"
        )
    return customTheme


config_items = _run_config()
config_parser, successfully_read_files = config_items[1], config_items[-1]
try:
    customTheme = parse_theme(successfully_read_files)
    console = Console(theme=customTheme)
except KeyError:
    console = Console()
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
    handlers=[RichHandler(console=console)],
)

logger = logging.getLogger("rich")
