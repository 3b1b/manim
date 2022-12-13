import logging

from rich.logging import RichHandler

__all__ = ["log"]


FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.WARNING, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("manimgl")
log.setLevel("DEBUG")
