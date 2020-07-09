import os
import sys

import colour

from . import constants
from .utils.config_utils import (
    _init_dirs,
    args,
    config_parser,
    file_writer_config,
    successfully_read_files,
)
from .logger import logger
from .utils.tex import TexTemplate, TexTemplateFromFile

__all__ = ["config", "camera_config"]

logger.info(f"Read configuration files: {successfully_read_files}")


def _parse_config(config_parser, args):
    """Parse config files and CLI arguments into a single dictionary."""
    # By default, use the CLI section of the digested .cfg files
    default = config_parser["CLI"]

    # Handle the *_quality flags.  These determine the section to read
    # and are stored in 'camera_config'.  Note the highest resolution
    # passed as argument will be used.
    for flag in ["fourk_quality", "high_quality", "medium_quality", "low_quality"]:
        if getattr(args, flag):
            section = config_parser[flag]
            break
    else:
        section = config_parser["CLI"]
    config = {opt: section.getint(opt) for opt in config_parser[flag]}

    # The -r, --resolution flag overrides the *_quality flags
    if args.resolution is not None:
        if "," in args.resolution:
            height_str, width_str = args.resolution.split(",")
            height, width = int(height_str), int(width_str)
        else:
            height, width = int(args.resolution), int(16 * height / 9)
        config["camera_config"].update({"pixel_height": height, "pixel_width": width})

    # Handle the -c (--color) flag
    if args.color is not None:
        try:
            background_color = colour.Color(args.color)
        except AttributeError as err:
            logger.warning("Please use a valid color.")
            logger.error(err)
            sys.exit(2)
    else:
        background_color = colour.Color(default["background_color"])
    config["background_color"] = background_color

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
    filename = (
        os.path.expanduser(args.tex_template) if args.tex_template is not None else None
    )

    if filename is not None and not os.access(filename, os.R_OK):
        # custom template not available, fallback to default
        logger.warning(
            f"Custom TeX template {filename} not found or not readable. "
            "Falling back to the default template."
        )
        filename = None
    config["tex_template_file"] = filename
    config["tex_template"] = (
        TexTemplateFromFile(filename=filename)
        if filename is not None
        else TexTemplate()
    )

    return config


# this is for the user
config = _parse_config(config_parser, args)
camera_config = config

_init_dirs(file_writer_config)
