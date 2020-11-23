"""Utilities called from ``__main__.py`` to interact with the config."""

import os
import argparse

from manim import constants


__all__ = ["parse_args"]


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
    """Helper function that handles boolean CLI arguments."""
    if s == "True":
        return True
    elif s == "False":
        return False
    else:
        raise argparse.ArgumentTypeError("True or False expected")


def parse_args(args):
    """Parse CLI arguments.

    Parameters
    ----------
    args : :class:`list`
        A list of arguments; generally, this should be ``sys.argv``.

    Returns
    -------
    :class:`argparse.Namespace`
        An object returned by ``argparse.parse_args``.

    """
    if args[0] == "python" and args[1] == "-m":
        args = args[2:]

    if len(args) == 1:
        return _parse_args_no_subcmd(args)

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
    """Parse arguments of the form 'manim <args>', when no command is present."""
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
        choices=[
            constants.QUALITIES[q]["flag"]
            for q in constants.QUALITIES
            if constants.QUALITIES[q]["flag"]
        ],
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
