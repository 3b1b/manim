import logging
from rich.logging import RichHandler
from .console import console

RichHandler.KEYWORDS = ['Played', 'animations', 'scene', 'Reading', 'Writing', 'script', 'arguments', 'Invalid', 'Aborting', 'module', 'File', 'Rendering']
logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console)]
)

logger = logging.getLogger("rich")
    