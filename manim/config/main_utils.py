"""
main_utils.py
-------------

Functions called from __main__.py to interact with the config.

"""

import os
import sys
import argparse
import logging

import colour

from manim import constants, logger, config
from .utils import make_config_parser
from .logger import JSONFormatter
from ..utils.tex import TexTemplate, TexTemplateFromFile


def _find_subcommand(args):
    """Return the subcommand that has been passed, if any.

    Parameters
    ----------
    args : list
        The argument list.

    Returns
    -------
    Optional[:class:`str`]
        If a subcommand is found, returns the string of its name.  Returns None
        otherwise.

    Notes
    -----
    This assumes that "manim" is the first word in the argument list, and that
    the subcommand will be the second word, if it exists.

    """
    subcmd = args[1]
    if subcmd in [
        "cfg"
        # , 'init',
    ]:
        return subcmd
    else:
        return None


def _init_cfg_subcmd(subparsers):
    """Initialises the subparser for the `cfg` subcommand.

    Parameters
    ----------
    subparsers : :class:`argparse._SubParsersAction`
        The subparser object for which to add the sub-subparser for the cfg subcommand.

    Returns
    -------
    :class:`argparse.ArgumentParser`
        The parser that parser anything cfg subcommand related.
    """
    cfg_related = subparsers.add_parser("cfg")
    cfg_subparsers = cfg_related.add_subparsers(dest="cfg_subcommand")

    cfg_write_parser = cfg_subparsers.add_parser("write")
    cfg_write_parser.add_argument(
        "--level",
        choices=["user", "cwd"],
        default=None,
        help="Specify if this config is for user or just the working directory.",
    )
    cfg_write_parser.add_argument(
        "--open", action="store_const", const=True, default=False
    )
    cfg_subparsers.add_parser("show")

    cfg_export_parser = cfg_subparsers.add_parser("export")
    cfg_export_parser.add_argument("--dir", default=os.getcwd())

    return cfg_related


def _str2bool(s):
    if s == "True":
        return True
    elif s == "False":
        return False
    else:
        raise argparse.ArgumentTypeError("True or False expected")


def parse_args(args):
    if args[0] == "python" and args[1] == "-m":
        args = args[2:]

    subcmd = _find_subcommand(args)
    if subcmd == "cfg":
        return _parse_args_cfg_subcmd(args)
    # elif subcmd == some_other_future_subcmd:
    #     return _parse_args_some_other_subcmd(args)
    elif subcmd is None:
        return _parse_args_no_subcmd(args)


def _parse_args_cfg_subcmd(args):
    """Parse arguments of the form 'manim cfg <subcmd> <args>'."""
    parser = argparse.ArgumentParser(
        description="Animation engine for explanatory math videos",
        prog="manim cfg",
        epilog="Made with <3 by the manim community devs",
    )
    subparsers = parser.add_subparsers(help="subcommand", dest="subcmd")

    cfg_subparsers = {
        subcmd: subparsers.add_parser(subcmd) for subcmd in ["write", "show", "export"]
    }

    # Arguments for the write subcmd
    cfg_subparsers["write"].add_argument(
        "--level",
        choices=["user", "cwd"],
        default="cwd",
        help="Specify if this config is for user or the working directory.",
    )
    cfg_subparsers["write"].add_argument(
        "--open", action="store_const", const=True, default=False
    )

    # Arguments for the export subcmd
    cfg_subparsers["export"].add_argument("--dir", default=os.getcwd())

    # Arguments for the show subcmd: currently no arguments

    # Recall the argument list looks like 'manim cfg <subcmd> <args>' so we
    # only need to parse the remaining args
    parsed = parser.parse_args(args[2:])
    parsed.cmd = "cfg"
    parsed.cfg_subcommand = parsed.subcmd

    return parsed


def _parse_args_no_subcmd(args):
    parser = argparse.ArgumentParser(
        description="Animation engine for explanatory math videos",
        prog="manim",
        usage=(
            "%(prog)s file [flags] [scene [scene ...]]\n"
            "       %(prog)s {cfg,init} [opts]"
        ),
        epilog="Made with <3 by the manim community devs",
    )

    parser.add_argument(
        "file",
        help="Path to file holding the python code for the scene",
    )
    parser.add_argument(
        "scene_names",
        nargs="*",
        help="Name of the Scene class you want to see",
        default=[""],
    )
    parser.add_argument(
        "-o",
        "--output_file",
        help="Specify the name of the output file, if "
        "it should be different from the scene class name",
        default="",
    )

    # The following use (action='store_const', const=True) instead of
    # the built-in (action='store_true').  This is because the latter
    # will default to False if not specified, while the former sets no
    # default value.  Since we want to set the default value in
    # manim.cfg rather than here, we use the former.
    parser.add_argument(
        "-p",
        "--preview",
        action="store_const",
        const=True,
        help="Automatically open the saved file once its done",
    )
    parser.add_argument(
        "-f",
        "--show_in_file_browser",
        action="store_const",
        const=True,
        help="Show the output file in the File Browser",
    )
    parser.add_argument(
        "--sound",
        action="store_const",
        const=True,
        help="Play a success/failure sound",
    )
    parser.add_argument(
        "--leave_progress_bars",
        action="store_const",
        const=True,
        help="Leave progress bars displayed in terminal",
    )
    parser.add_argument(
        "-a",
        "--write_all",
        action="store_const",
        const=True,
        help="Write all the scenes from a file",
    )
    parser.add_argument(
        "-w",
        "--write_to_movie",
        action="store_const",
        const=True,
        help="Render the scene as a movie file (this is on by default)",
    )
    parser.add_argument(
        "-s",
        "--save_last_frame",
        action="store_const",
        const=True,
        help="Save the last frame only (no movie file is generated)",
    )
    parser.add_argument(
        "-g",
        "--save_pngs",
        action="store_const",
        const=True,
        help="Save each frame as a png",
    )
    parser.add_argument(
        "-i",
        "--save_as_gif",
        action="store_const",
        const=True,
        help="Save the video as gif",
    )
    parser.add_argument(
        "--disable_caching",
        action="store_const",
        const=True,
        help="Disable caching (will generate partial-movie-files anyway)",
    )
    parser.add_argument(
        "--flush_cache",
        action="store_const",
        const=True,
        help="Remove all cached partial-movie-files",
    )
    parser.add_argument(
        "--log_to_file",
        action="store_const",
        const=True,
        help="Log terminal output to file",
    )
    # The default value of the following is set in manim.cfg
    parser.add_argument(
        "-c",
        "--background_color",
        help="Specify background color",
    )
    parser.add_argument(
        "--background_opacity",
        help="Specify background opacity",
    )
    parser.add_argument(
        "--media_dir",
        help="Directory to store media (including video files)",
    )
    parser.add_argument(
        "--log_dir",
        help="Directory to store log files",
    )
    parser.add_argument(
        "--tex_template",
        help="Specify a custom TeX template file",
    )

    # All of the following use (action="store_true"). This means that
    # they are by default False.  In contrast to the previous ones that
    # used (action="store_const", const=True), the following do not
    # correspond to a single configuration option.  Rather, they
    # override several options at the same time.

    # The following overrides -w, -a, -g, and -i
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Do a dry run (render scenes but generate no output files)",
    )

    # The following overrides PNG_MODE, MOVIE_FILE_EXTENSION, and
    # BACKGROUND_OPACITY
    parser.add_argument(
        "-t",
        "--transparent",
        action="store_true",
        help="Render a scene with an alpha channel",
    )

    # The following are mutually exclusive and each overrides
    # FRAME_RATE, PIXEL_HEIGHT, and PIXEL_WIDTH,
    parser.add_argument(
        "-q",
        "--quality",
        choices=constants.QUALITIES.values(),
        default=constants.DEFAULT_QUALITY_SHORT,
        help="Render at specific quality, short form of the --*_quality flags",
    )
    parser.add_argument(
        "--low_quality",
        action="store_true",
        help="Render at low quality",
    )
    parser.add_argument(
        "--medium_quality",
        action="store_true",
        help="Render at medium quality",
    )
    parser.add_argument(
        "--high_quality",
        action="store_true",
        help="Render at high quality",
    )
    parser.add_argument(
        "--production_quality",
        action="store_true",
        help="Render at default production quality",
    )
    parser.add_argument(
        "--fourk_quality",
        action="store_true",
        help="Render at 4K quality",
    )

    # Deprecated quality flags
    parser.add_argument(
        "-l",
        action="store_true",
        help="DEPRECATED: USE -ql or --quality l",
    )
    parser.add_argument(
        "-m",
        action="store_true",
        help="DEPRECATED: USE -qm or --quality m",
    )
    parser.add_argument(
        "-e",
        action="store_true",
        help="DEPRECATED: USE -qh or --quality h",
    )
    parser.add_argument(
        "-k",
        action="store_true",
        help="DEPRECATED: USE -qk or --quality k",
    )

    # This overrides any of the above
    parser.add_argument(
        "-r",
        "--resolution",
        help='Resolution, passed as "height,width". '
        "Overrides the -l, -m, -e, and -k flags, if present",
    )

    # This sets FROM_ANIMATION_NUMBER and UPTO_ANIMATION_NUMBER
    parser.add_argument(
        "-n",
        "--from_animation_number",
        help="Start rendering at the specified animation index, "
        "instead of the first animation.  If you pass in two comma "
        "separated values, e.g. '3,6', it will end "
        "the rendering at the second value",
    )

    parser.add_argument(
        "--use_js_renderer",
        help="Render animations using the javascript frontend",
        action="store_const",
        const=True,
    )

    parser.add_argument(
        "--js_renderer_path",
        help="Path to the javascript frontend",
    )

    # Specify the manim.cfg file
    parser.add_argument(
        "--config_file",
        help="Specify the configuration file",
    )

    # Specify whether to use the custom folders
    parser.add_argument(
        "--custom_folders",
        action="store_true",
        help="Use the folders defined in the [custom_folders] "
        "section of the config file to define the output folder structure",
    )

    # Specify the verbosity
    parser.add_argument(
        "-v",
        "--verbosity",
        type=str,
        help=(
            "Verbosity level. Also changes the ffmpeg log level unless "
            "the latter is specified in the config"
        ),
        choices=constants.VERBOSITY_CHOICES,
    )

    # Specify if the progress bar should be displayed
    parser.add_argument(
        "--progress_bar",
        type=_str2bool,
        help="Display the progress bar",
        metavar="True/False",
    )

    return parser.parse_args(args[1:])


def update_config_with_cli(args):
    """Update the config dictionaries after parsing CLI flags."""
    parser = make_config_parser()
    default = parser["CLI"]

    ## Update config
    global config

    # Handle the *_quality flags.  These determine the section to read
    # and are stored in 'camera_config'.  Note the highest resolution
    # passed as argument will be used.
    quality = _determine_quality(args)
    section = parser[quality if quality != constants.DEFAULT_QUALITY else "CLI"]

    # Loop over low quality for the keys, could be any quality really
    config.update({opt: section.getint(opt) for opt in parser["low_quality"]})

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

    # Handle the --tex_template flag, if the flag is absent read it from the config.
    if args.tex_template:
        tex_fn = os.path.expanduser(args.tex_template)
    else:
        tex_fn = default["tex_template"] if default["tex_template"] != "" else None

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

    ## Update file_writer_config
    fw_config = {}

    if config["use_js_renderer"]:
        fw_config["disable_caching"] = True

    if not hasattr(args, "subcommands"):
        fw_config["input_file"] = args.file if args.file else ""
        fw_config["scene_names"] = (
            args.scene_names if args.scene_names is not None else []
        )
        fw_config["output_file"] = args.output_file if args.output_file else ""

    # Note ConfigParser options are all strings and each needs to be converted
    # to the appropriate type.
    for boolean_opt in [
        "preview",
        "show_in_file_browser",
        "leave_progress_bars",
        "write_to_movie",
        "save_last_frame",
        "save_pngs",
        "save_as_gif",
        "write_all",
        "disable_caching",
        "flush_cache",
        "log_to_file",
    ]:
        attr = getattr(args, boolean_opt)
        fw_config[boolean_opt] = (
            default.getboolean(boolean_opt) if attr is None else attr
        )
    # for str_opt in ['media_dir', 'video_dir', 'tex_dir', 'text_dir']:
    for str_opt in ["media_dir"]:
        attr = getattr(args, str_opt)
        fw_config[str_opt] = os.path.relpath(default[str_opt]) if attr is None else attr
    attr = getattr(args, "log_dir")
    fw_config["log_dir"] = (
        os.path.join(fw_config["media_dir"], default["log_dir"])
        if attr is None
        else attr
    )
    dir_names = {
        "video_dir": "videos",
        "images_dir": "images",
        "tex_dir": "Tex",
        "text_dir": "texts",
    }
    for name in dir_names:
        fw_config[name] = os.path.join(fw_config["media_dir"], dir_names[name])

    # the --custom_folders flag overrides the default folder structure with the
    # custom folders defined in the [custom_folders] section of the config file
    fw_config["custom_folders"] = args.custom_folders
    if fw_config["custom_folders"]:
        fw_config["media_dir"] = parser["custom_folders"].get("media_dir")
        for opt in ["video_dir", "images_dir", "tex_dir", "text_dir"]:
            fw_config[opt] = parser["custom_folders"].get(opt)

    # Handle the -s (--save_last_frame) flag: invalidate the -w flag
    # At this point the save_last_frame option has already been set by
    # both CLI and the cfg file, so read the config dict directly
    if fw_config["save_last_frame"]:
        fw_config["write_to_movie"] = False

    # Handle the -t (--transparent) flag.  This flag determines which
    # section to use from the .cfg file.
    section = parser["transparent"] if args.transparent else default
    for opt in ["png_mode", "movie_file_extension", "background_opacity"]:
        fw_config[opt] = section[opt]

    # Handle the -n flag.  Read first from the cfg and then override with CLI.
    # These two are integers -- use getint()
    for opt in ["from_animation_number", "upto_animation_number"]:
        fw_config[opt] = default.getint(opt)
    if fw_config["upto_animation_number"] == -1:
        fw_config["upto_animation_number"] = float("inf")
    nflag = args.from_animation_number
    if nflag is not None:
        if "," in nflag:
            start, end = nflag.split(",")
            fw_config["from_animation_number"] = int(start)
            fw_config["upto_animation_number"] = int(end)
        else:
            fw_config["from_animation_number"] = int(nflag)

    # Handle the --dry_run flag.  This flag determines which section
    # to use from the .cfg file.  All options involved are boolean.
    # Note this overrides the flags -w, -s, -a, -g, and -i.
    if args.dry_run:
        for opt in [
            "write_to_movie",
            "save_last_frame",
            "save_pngs",
            "save_as_gif",
            "write_all",
        ]:
            fw_config[opt] = parser["dry_run"].getboolean(opt)
    if not fw_config["write_to_movie"]:
        fw_config["disable_caching"] = True
    # Read in the streaming section -- all values are strings
    fw_config["streaming"] = {
        opt: parser["streaming"][opt]
        for opt in [
            "live_stream_name",
            "twitch_stream_key",
            "streaming_protocol",
            "streaming_ip",
            "streaming_protocol",
            "streaming_client",
            "streaming_port",
            "streaming_port",
            "streaming_console_banner",
        ]
    }

    # For internal use (no CLI flag)
    fw_config["skip_animations"] = fw_config["save_last_frame"]
    fw_config["max_files_cached"] = default.getint("max_files_cached")
    if fw_config["max_files_cached"] == -1:
        fw_config["max_files_cached"] = float("inf")
    # Parse the verbosity flag to read in the log level
    verbosity = getattr(args, "verbosity")
    verbosity = default["verbosity"] if verbosity is None else verbosity
    fw_config["verbosity"] = verbosity
    logger.setLevel(verbosity)

    # Parse the ffmpeg log level in the config
    ffmpeg_loglevel = parser["ffmpeg"].get("loglevel", None)
    fw_config["ffmpeg_loglevel"] = (
        constants.FFMPEG_VERBOSITY_MAP[verbosity]
        if ffmpeg_loglevel is None
        else ffmpeg_loglevel
    )

    # Parse the progress_bar flag
    progress_bar = getattr(args, "progress_bar")
    if progress_bar is None:
        progress_bar = default.getboolean("progress_bar")
    fw_config["progress_bar"] = progress_bar

    global file_writer_config
    file_writer_config.update(fw_config)


def _determine_quality(args):
    old_qualities = {
        "k": "fourk_quality",
        "e": "high_quality",
        "m": "medium_quality",
        "l": "low_quality",
    }

    for quality in constants.QUALITIES:
        if quality == constants.DEFAULT_QUALITY:
            # Skip so we prioritize anything that overwrites the default quality.
            pass
        elif getattr(args, quality, None) or (
            hasattr(args, "quality") and args.quality == constants.QUALITIES[quality]
        ):
            return quality

    for quality in old_qualities:
        if getattr(args, quality, None):
            logger.warning(
                f"Option -{quality} is deprecated please use the --quality/-q flag."
            )
            return old_qualities[quality]

    return constants.DEFAULT_QUALITY


def set_file_logger():
    # Note: The log file name will be
    # <name_of_animation_file>_<name_of_scene>.log, gotten from
    # file_writer_config.  So it can differ from the real name of the scene.
    # <name_of_scene> would only appear if scene name was provided when manim
    # was called.
    scene_name_suffix = "".join(file_writer_config["scene_names"])
    scene_file_name = os.path.basename(file_writer_config["input_file"]).split(".")[0]
    log_file_name = (
        f"{scene_file_name}_{scene_name_suffix}.log"
        if scene_name_suffix
        else f"{scene_file_name}.log"
    )
    log_file_path = os.path.join(file_writer_config["log_dir"], log_file_name)

    file_handler = logging.FileHandler(log_file_path, mode="w")
    file_handler.setFormatter(JSONFormatter())

    logger.addHandler(file_handler)
    logger.info("Log file will be saved in %(logpath)s", {"logpath": log_file_path})
