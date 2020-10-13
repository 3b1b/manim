import logging
from contextlib import contextmanager

from .logger import make_logger
from .utils import make_config_parser, make_config, make_file_writer_config

__all__ = [
    "logger",
    "console",
    "config",
    "file_writer_config",
    "camera_config",
    "tempconfig",
]

parser = make_config_parser()

# The logger can be accessed from anywhere as manim.logger, or as
# logging.getLogger("manim").  The console must be accessed as manim.console.
# Throughout the codebase, use manim.console.print() instead of print().
logger, console = make_logger(parser["logger"], parser["CLI"]["verbosity"])
# TODO: temporary to have a clean terminal output when working with PIL or matplotlib
logging.getLogger("PIL").setLevel(logging.INFO)
logging.getLogger("matplotlib").setLevel(logging.INFO)

config = make_config(parser)
camera_config = config
file_writer_config = make_file_writer_config(parser, config)


# This has to go here because it needs access to this module's config
@contextmanager
def tempconfig(temp):
    """Context manager that temporarily modifies the global config dict.

    The code block inside the ``with`` statement will use the modified config.
    After the code block, the config will be restored to its original value.

    Parameters
    ----------

    temp : :class:`dict`
        A dictionary whose keys will be used to temporarily update the global
        config.

    Examples
    --------
    Use ``with tempconfig({...})`` to temporarily change the default values of
    certain objects.

    .. code_block:: python

       c = Camera()
       c.frame_width == config['frame_width']        # -> True
       with tempconfig({'frame_width': 100}):
           c = Camera()
           c.frame_width == config['frame_width']    # -> False
           c.frame_width == 100                      # -> True

    """
    global config
    original = config.copy()

    temp = {k: v for k, v in temp.items() if k in original}

    # In order to change the config that every module has acces to, use
    # update(), DO NOT use assignment.  Assigning config = some_dict will just
    # make the local variable named config point to a new dictionary, it will
    # NOT change the dictionary that every module has a reference to.
    config.update(temp)
    try:
        yield
    finally:
        config.update(original)  # update, not assignment!
