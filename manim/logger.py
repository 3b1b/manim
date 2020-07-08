import logging
import configparser

from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
#from .config import config

#print(config)
def parseTheme(fp):
    config = configparser.ConfigParser()
    config.read(fp)
    theme=dict(config['log.color'])
    customTheme=Theme(theme)
    return customTheme
try:
    customTheme =  parseTheme("manim.cfg")
    console = Console(theme=customTheme)
except KeyError:
    console = Console()

RichHandler.KEYWORDS = ['Played', 'animations', 'scene', 'Reading', 'Writing', 'script', 'arguments', 'Invalid', 'Aborting', 'module', 'File', 'Rendering']
logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console)]
)

logger = logging.getLogger("rich")
    