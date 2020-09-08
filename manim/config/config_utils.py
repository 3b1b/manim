"""
config_utils.py
---------------

Utility functions for parsing manim config files.

"""


__all__ = [
    "_run_config",
    "_paths_config_file",
    "_from_command_line",
    "finalized_configs_dict",
]


import argparse
import configparser
import os
import sys

import colour

from .. import constants
from ..utils.tex import TexTemplate, TexTemplateFromFile


def _parse_file_writer_config(config_parser, args):
    """Parse config files and CLI arguments into a single dictionary."""
    # By default, use the CLI section of the digested .cfg files
    default = config_parser["CLI"]

    # This will be the final file_writer_config dict exposed to the user
    fw_config = {}

    # Handle input files and scenes.  Note these cannot be set from
    # the .cfg files, only from CLI arguments.
    # If a subcommand is given, manim will not render a video and
    # thus these specific input/output files are not needed.
    if not (hasattr(args, "subcommands")):
        fw_config["input_file"] = args.file
        fw_config["scene_names"] = (
            args.scene_names if args.scene_names is not None else []
        )
        fw_config["output_file"] = args.output_file

    # Handle all options that are directly overridden by CLI
    # arguments.  Note ConfigParser options are all strings and each
    # needs to be converted to the appropriate type. Thus, we do this
    # in batches, depending on their type: booleans and strings
    for boolean_opt in [
        "preview",
        "show_in_file_browser",
        "sound",
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
    for str_opt in ["media_dir", "log_dir"]:
        attr = getattr(args, str_opt)
        fw_config[str_opt] = os.path.relpath(default[str_opt]) if attr is None else attr
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
        fw_config["media_dir"] = config_parser["custom_folders"].get("media_dir")
        for opt in ["video_dir", "images_dir", "tex_dir", "text_dir"]:
            fw_config[opt] = config_parser["custom_folders"].get(opt)

    # Handle the -s (--save_last_frame) flag: invalidate the -w flag
    # At this point the save_last_frame option has already been set by
    # both CLI and the cfg file, so read the config dict directly
    if fw_config["save_last_frame"]:
        fw_config["write_to_movie"] = False

    # Handle the -t (--transparent) flag.  This flag determines which
    # section to use from the .cfg file.
    section = config_parser["transparent"] if args.transparent else default
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
            fw_config[opt] = config_parser["dry_run"].getboolean(opt)
    if not fw_config["write_to_movie"]:
        fw_config["disable_caching"] = True
    # Read in the streaming section -- all values are strings
    fw_config["streaming"] = {
        opt: config_parser["streaming"][opt]
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
    fw_config["skip_animations"] = any(
        [fw_config["save_last_frame"], fw_config["from_animation_number"]]
    )
    fw_config["max_files_cached"] = default.getint("max_files_cached")
    if fw_config["max_files_cached"] == -1:
        fw_config["max_files_cached"] = float("inf")
    # Parse the verbosity flag to read in the log level
    verbosity = getattr(args, "verbosity")
    verbosity = default["verbosity"] if verbosity is None else verbosity
    fw_config["verbosity"] = verbosity

    # Parse the ffmpeg log level in the config
    ffmpeg_loglevel = config_parser["ffmpeg"].get("loglevel", None)
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
    return fw_config


def _parse_cli(arg_list, input=True):
    parser = argparse.ArgumentParser(
        description="Animation engine for explanatory math videos",
        epilog="Made with <3 by the manim community devs",
    )
    if input:
        # If the only command is `manim`, we want both subcommands like `cfg`
        # and mandatory positional arguments like `file` to show up in the help section.
        only_manim = len(sys.argv) == 1

        if only_manim or _subcommand_name():
            subparsers = parser.add_subparsers(dest="subcommands")

            # More subcommands can be added here, with elif statements.
            # If a help command is passed, we still want subcommands to show
            # up, so we check for help commands as well before adding the
            # subcommand's subparser.
            if only_manim or _subcommand_name() in ["cfg", "--help", "-h"]:
                cfg_related = _init_cfg_subcmd(subparsers)

        if only_manim or not _subcommand_name(ignore=["--help", "-h"]):
            parser.add_argument(
                "file",
                help="path to file holding the python code for the scene",
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
        "-l",
        "--low_quality",
        action="store_true",
        help="Render at low quality",
    )
    parser.add_argument(
        "-m",
        "--medium_quality",
        action="store_true",
        help="Render at medium quality",
    )
    parser.add_argument(
        "-e",
        "--high_quality",
        action="store_true",
        help="Render at high quality",
    )
    parser.add_argument(
        "-k",
        "--fourk_quality",
        action="store_true",
        help="Render at 4K quality",
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
        help="Verbosity level. Also changes the ffmpeg log level unless the latter is specified in the config",
        choices=constants.VERBOSITY_CHOICES,
    )

    # Specify if the progress bar should be displayed
    def _str2bool(s):
        if s == "True":
            return True
        elif s == "False":
            return False
        else:
            raise argparse.ArgumentTypeError("True or False expected")

    parser.add_argument(
        "--progress_bar",
        type=_str2bool,
        help="Display the progress bar",
        metavar="True/False",
    )
    parsed = parser.parse_args(arg_list)
    if hasattr(parsed, "subcommands"):
        if _subcommand_name() == "cfg":
            setattr(
                parsed,
                "cfg_subcommand",
                cfg_related.parse_args(sys.argv[2:]).cfg_subcommand,
            )

    return parsed


def _init_dirs(config):
    # Make sure all folders exist
    for folder in [
        config["media_dir"],
        config["video_dir"],
        config["tex_dir"],
        config["text_dir"],
        config["log_dir"],
    ]:
        if not os.path.exists(folder):
            # If log_to_file is False, ignore log_dir
            if folder is config["log_dir"] and (not config["log_to_file"]):
                pass
            else:
                os.makedirs(folder)


def _from_command_line():
    """Determine if manim was called from the command line."""
    # Manim can be called from the command line in three different
    # ways.  The first two involve using the manim or manimcm commands.
    # Note that some Windows CLIs replace those commands with the path
    # to their executables, so we must check for this as well
    prog = os.path.split(sys.argv[0])[-1]
    from_cli_command = prog in ["manim", "manim.exe", "manimcm", "manimcm.exe"]

    # The third way involves using `python -m manim ...`.  In this
    # case, the CLI arguments passed to manim do not include 'manim',
    # 'manimcm', or even 'python'.  However, the -m flag will always
    # be the first argument.
    from_python_m = sys.argv[0] == "-m"

    return from_cli_command or from_python_m


def _from_dunder_main():
    dunder_main_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "__main__.py"
    )
    return sys.argv[0] == dunder_main_path


def _paths_config_file():
    library_wide = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "default.cfg")
    )
    if sys.platform.startswith("win32"):
        user_wide = os.path.expanduser(
            os.path.join("~", "AppData", "Roaming", "Manim", "manim.cfg")
        )
    else:
        user_wide = os.path.expanduser(
            os.path.join("~", ".config", "manim", "manim.cfg")
        )
    return [library_wide, user_wide]


def _run_config():
    # Config files to be parsed, in ascending priority
    config_files = _paths_config_file()
    if _from_command_line() or _from_dunder_main():
        args = _parse_cli(sys.argv[1:])
        if not hasattr(args, "subcommands"):
            if args.config_file is not None:
                if os.path.exists(args.config_file):
                    config_files.append(args.config_file)
                else:
                    raise FileNotFoundError(
                        f"Config file {args.config_file} doesn't exist"
                    )
            else:
                script_directory_file_config = os.path.join(
                    os.path.dirname(args.file), "manim.cfg"
                )
                if os.path.exists(script_directory_file_config):
                    config_files.append(script_directory_file_config)
        else:
            working_directory_file_config = os.path.join(os.getcwd(), "manim.cfg")
            if os.path.exists(working_directory_file_config):
                config_files.append(working_directory_file_config)

    else:
        # In this case, we still need an empty args object.
        args = _parse_cli([], input=False)
        # Need to populate the options left out
        args.file, args.scene_names, args.output_file = "", "", ""

    config_parser = configparser.ConfigParser()
    successfully_read_files = config_parser.read(config_files)

    # this is for internal use when writing output files
    file_writer_config = _parse_file_writer_config(config_parser, args)
    return args, config_parser, file_writer_config, successfully_read_files


def finalized_configs_dict():
    config = _run_config()[1]
    return {section: dict(config[section]) for section in config.sections()}


def _subcommand_name(ignore=()):
    """Goes through sys.argv to check if any subcommand has been passed,
    and returns the first such subcommand's name, if found.

    Parameters
    ----------
    ignore : Iterable[:class:`str`], optional
        List of NON_ANIM_UTILS to ignore when searching for subcommands, by default []

    Returns
    -------
    Optional[:class:`str`]
        If a subcommand is found, returns the string of its name. Returns None if no
        subcommand is found.
    """
    NON_ANIM_UTILS = ["cfg", "--help", "-h"]
    NON_ANIM_UTILS = [util for util in NON_ANIM_UTILS if util not in ignore]

    # If a subcommand is found, break out of the inner loop, and hit the break of the outer loop
    # on the way out, effectively breaking out of both loops. The value of arg will be the
    # subcommand to be taken.
    # If no subcommand is found, none of the breaks are hit, and the else clause of the outer loop
    # is run, setting arg to None.

    for item in NON_ANIM_UTILS:
        for arg in sys.argv:
            if arg == item:
                break
        else:
            continue
        break
    else:
        arg = None

    return arg


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
    cfg_related = subparsers.add_parser(
        "cfg",
    )
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
