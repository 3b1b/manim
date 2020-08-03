"""
config_utils.py
---------------

Utility functions for parsing manim config files.

"""

import argparse
import configparser
import os
import sys

import colour

from .. import constants
from .tex import TexTemplate, TexTemplateFromFile

__all__ = [
    "_run_config",
    "_paths_config_file",
    "_from_command_line",
    "finalized_configs_dict",
]

min_argvs = 3 if "-m" in sys.argv[0] else 2


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
        "show_file_in_finder",
        "quiet",
        "sound",
        "leave_progress_bars",
        "write_to_movie",
        "save_last_frame",
        "save_pngs",
        "save_as_gif",
        "write_all",
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
    dir_names = {"video_dir": "videos", "tex_dir": "Tex", "text_dir": "texts"}
    for name in dir_names:
        fw_config[name] = os.path.join(fw_config["media_dir"], dir_names[name])

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

    return fw_config


def _parse_cli(arg_list, input=True):
    parser = argparse.ArgumentParser(
        description="Animation engine for explanatory math videos",
        epilog="Made with <3 by the manim community devs",
    )
    if input:
        # If the only command is `manim`, we want both subcommands like `cfg`
        # and mandatory positional arguments like `file` to show up in the help section.
        if len(sys.argv) == min_argvs - 1 or _subcommands_exist():
            subparsers = parser.add_subparsers(dest="subcommands")
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

        if len(sys.argv) == min_argvs - 1 or not _subcommands_exist(
            ignore=["--help", "-h"]
        ):
            parser.add_argument(
                "file", help="path to file holding the python code for the scene",
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
        "--show_file_in_finder",
        action="store_const",
        const=True,
        help="Show the output file in finder",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_const", const=True, help="Quiet mode",
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
        help="Render the scene as a movie file",
    )
    parser.add_argument(
        "-s",
        "--save_last_frame",
        action="store_const",
        const=True,
        help="Save the last frame (and do not save movie)",
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
        "--log_to_file",
        action="store_const",
        const=True,
        help="Log terminal output to file.",
    )

    # The default value of the following is set in manim.cfg
    parser.add_argument(
        "-c", "--color", help="Background color",
    )
    parser.add_argument(
        "--background_opacity", help="Background opacity",
    )
    parser.add_argument(
        "--media_dir", help="directory to write media",
    )

    parser.add_argument(
        "--log_dir", help="directory to write log files to",
    )

    # video_group = parser.add_mutually_exclusive_group()
    # video_group.add_argument(
    #     "--video_dir",
    #     help="directory to write file tree for video",
    # )
    # parser.add_argument(
    #     "--tex_dir",
    #     help="directory to write tex",
    # )
    # parser.add_argument(
    #     "--text_dir",
    #     help="directory to write text",
    # )
    parser.add_argument(
        "--tex_template", help="Specify a custom TeX template file",
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
        help="Render to a movie file with an alpha channel",
    )

    # The following are mutually exclusive and each overrides
    # FRAME_RATE, PIXEL_HEIGHT, and PIXEL_WIDTH,
    parser.add_argument(
        "-l",
        "--low_quality",
        action="store_true",
        help="Render at low quality (for fastest rendering)",
    )
    parser.add_argument(
        "-m",
        "--medium_quality",
        action="store_true",
        help="Render at medium quality (for much faster rendering)",
    )
    parser.add_argument(
        "-e",
        "--high_quality",
        action="store_true",
        help="Render at high quality (for slightly faster rendering)",
    )
    parser.add_argument(
        "-k",
        "--fourk_quality",
        action="store_true",
        help="Render at 4K quality (slower rendering)",
    )

    # This overrides any of the above
    parser.add_argument(
        "-r", "--resolution", help='Resolution, passed as "height,width"',
    )

    # This sets FROM_ANIMATION_NUMBER and UPTO_ANIMATION_NUMBER
    parser.add_argument(
        "-n",
        "--from_animation_number",
        help="Start rendering not from the first animation, but"
        "from another, specified by its index.  If you pass"
        'in two comma separated values, e.g. "3,6", it will end'
        "the rendering at the second value",
    )

    # Specify the manim.cfg file
    parser.add_argument(
        "--config_file", help="Specify the configuration file",
    )
    parsed = parser.parse_args(arg_list)
    if hasattr(parsed, "subcommands"):
        setattr(
            parsed,
            "cfg_subcommand",
            cfg_related.parse_args(
                sys.argv[min_argvs - (0 if min_argvs == 2 else 1) :]
            ).cfg_subcommand,
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
    # ways.  The first two involve using the manim or manimcm commands
    prog = os.path.split(sys.argv[0])[-1]
    from_cli_command = prog in ["manim", "manimcm"]

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
        os.path.join(os.path.dirname(__file__), "..", "default.cfg")
    )
    if sys.platform.startswith("linux"):
        user_wide = os.path.expanduser(
            os.path.join("~", ".config", "manim", "manim.cfg")
        )
    elif sys.platform.startswith("darwin"):
        user_wide = os.path.expanduser(
            os.path.join("~", "Library", "Application Support", "Manim", "manim.cfg")
        )
    elif sys.platform.startswith("win32"):
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


def _subcommands_exist(ignore=[]):
    NON_ANIM_UTILS = ["cfg", "--help", "-h"]
    NON_ANIM_UTILS = [util for util in NON_ANIM_UTILS if util not in ignore]

    not_only_manim = len(sys.argv) > min_argvs - 1
    sub_command_exists = any(a == item for a in sys.argv for item in NON_ANIM_UTILS)
    return not_only_manim and sub_command_exists
