"""
config.py
---------
Process the manim.cfg file and the command line arguments into a single
config object.
"""


__all__ = ["file_writer_config", "config", "camera_config", "tempconfig"]


import os
import sys
from contextlib import contextmanager

import colour

from .. import constants
from .config_utils import (
    _determine_quality,
    _run_config,
    _init_dirs,
    _from_command_line,
)

from .logger import set_rich_logger, set_file_logger, logger
from ..utils.tex import TexTemplate, TexTemplateFromFile

__all__ = ["file_writer_config", "config", "camera_config", "tempconfig"]


config = None


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


def _parse_config(config_parser, args):
    """Parse config files and CLI arguments into a single dictionary."""
    # By default, use the CLI section of the digested .cfg files
    default = config_parser["CLI"]

    # Handle the *_quality flags.  These determine the section to read
    # and are stored in 'camera_config'.  Note the highest resolution
    # passed as argument will be used.
    quality = _determine_quality(args)
    section = config_parser[quality if quality != "production" else "CLI"]

    # Loop over low quality for the keys, could be any quality really
    config = {opt: section.getint(opt) for opt in config_parser["low_quality"]}

    config["default_pixel_height"] = default.getint("pixel_height")
    config["default_pixel_width"] = default.getint("pixel_width")
    # The -r, --resolution flag overrides the *_quality flags
    if args.resolution is not None:
        if "," in args.resolution:
            height_str, width_str = args.resolution.split(",")
            height, width = int(height_str), int(width_str)
        else:
            height = int(args.resolution)
            width = int(16 * height / 9)
        config.update({"pixel_height": height, "pixel_width": width})

    # Handle the -c (--background_color) flag
    if args.background_color is not None:
        try:
            background_color = colour.Color(args.background_color)
        except AttributeError as err:
            logger.warning("Please use a valid color.")
            logger.error(err)
            sys.exit(2)
    else:
        background_color = colour.Color(default["background_color"])
    config["background_color"] = background_color

    config["use_js_renderer"] = args.use_js_renderer or default.getboolean(
        "use_js_renderer"
    )

    config["js_renderer_path"] = args.js_renderer_path or default.get(
        "js_renderer_path"
    )

    # Set the rest of the frame properties
    config["frame_height"] = 8.0
    config["frame_width"] = (
        config["frame_height"] * config["pixel_width"] / config["pixel_height"]
    )
    config["frame_y_radius"] = config["frame_height"] / 2
    config["frame_x_radius"] = config["frame_width"] / 2
    config["top"] = config["frame_y_radius"] * constants.UP
    config["bottom"] = config["frame_y_radius"] * constants.DOWN
    config["left_side"] = config["frame_x_radius"] * constants.LEFT
    config["right_side"] = config["frame_x_radius"] * constants.RIGHT

    # Handle the --tex_template flag.  Note we accept None if the flag is absent
    tex_fn = os.path.expanduser(args.tex_template) if args.tex_template else None

    if tex_fn is not None and not os.access(tex_fn, os.R_OK):
        # custom template not available, fallback to default
        logger.warning(
            f"Custom TeX template {tex_fn} not found or not readable. "
            "Falling back to the default template."
        )
        tex_fn = None
    config["tex_template_file"] = tex_fn
    config["tex_template"] = (
        TexTemplateFromFile(filename=tex_fn) if tex_fn is not None else TexTemplate()
    )

    return config


args, config_parser, file_writer_config, successfully_read_files = _run_config()
logger.setLevel(file_writer_config["verbosity"])
set_rich_logger(config_parser["logger"], file_writer_config["verbosity"])

if _from_command_line():
    logger.debug(
        f"Read configuration files: {[os.path.abspath(cfgfile) for cfgfile in successfully_read_files]}"
    )
    if not (hasattr(args, "subcommands")):
        _init_dirs(file_writer_config)
config = _parse_config(config_parser, args)
if config["use_js_renderer"]:
    file_writer_config["disable_caching"] = True
camera_config = config

if file_writer_config["log_to_file"]:
    # IMPORTANT note about file name : The log file name will be the scene_name get from the args (contained in file_writer_config). So it can differ from the real name of the scene.
    log_file_path = os.path.join(
        file_writer_config["log_dir"],
        "".join(file_writer_config["scene_names"]) + ".log",
    )
    set_file_logger(log_file_path)
    logger.info("Log file wil be saved in %(logpath)s", {"logpath": log_file_path})
