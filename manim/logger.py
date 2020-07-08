import configparser
import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

from .config_utils import config_parser, successfully_read_files


def parseTheme(fp):
    config_parser.read(fp)
    theme = dict(config_parser["log.color"])
    customTheme = Theme(theme)
    return customTheme


try:
    customTheme = parseTheme(successfully_read_files)
    console = Console(theme=customTheme)
except KeyError:
    console = Console()

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
]
logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console)],
)

logger = logging.getLogger("rich")
