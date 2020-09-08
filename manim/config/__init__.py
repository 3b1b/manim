# Note that the global config dict is called 'config', just like the module
# itself.  That's why we import the module first with a different name
# (_config), and then the dict.
from . import config as _config
from .config import config, tempconfig, file_writer_config, camera_config
from .logger import logger, console

__all__ = [
    "_config",
    "config",
    "tempconfig",
    "file_writer_config",
    "camera_config",
    "logger",
    "console",
]
