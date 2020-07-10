import configparser
import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
from rich import print as printf
from rich import errors,color

from .utils.config_utils import config_parser, successfully_read_files


def parse_theme(fp):
    config_parser.read(fp)
    theme = dict(config_parser["log.color"])
    try:
        customTheme = Theme(theme)
    except (color.ColorParseError,errors.StyleSyntaxError):
        customTheme = None
        printf("[logging.level.error]Looks like your colour configuration has an error. So loading default color configuration[/logging.level.error]")
        #console.log(e) #Not logging it as it looks clumsy
    return customTheme

try:
    customTheme = parse_theme(successfully_read_files)
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
