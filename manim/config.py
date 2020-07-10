"""
config.py
---------

Process the manim.cfg file and the command line arguments into a single
config object.

"""

import os
import sys
import argparse
import configparser
import colour
from .utils.tex import TexTemplateFromFile, TexTemplate
from .logger import logger
from . import constants

__all__ = ["file_writer_config", "config", "camera_config"]


def _parse_config(config_parser, args):
    """Parse config files and CLI arguments into a single dictionary."""
    # By default, use the CLI section of the digested .cfg files
    default = config_parser['CLI']

    # Handle the *_quality flags.  These determine the section to read
    # and are stored in 'camera_config'.  Note the highest resolution
    # passed as argument will be used.
    for flag in ['fourk_quality', 'high_quality', 'medium_quality', 'low_quality']:
        if getattr(args, flag):
            section = config_parser[flag]
            break
    else:
        section = config_parser['CLI']
    config = {opt: section.getint(opt) for opt in config_parser[flag]}

    # The -r, --resolution flag overrides the *_quality flags
    if args.resolution is not None:
        if "," in args.resolution:
            height_str, width_str = args.resolution.split(",")
            height, width = int(height_str), int(width_str)
        else:
            height, width = int(args.resolution), int(16 * height / 9)
        config['camera_config'].update({'pixel_height': height,
                                        'pixel_width': width})

    # Handle the -c (--color) flag
    if args.color is not None:
        try:
            background_color = colour.Color(args.color)
        except AttributeError as err:
            logger.warning('Please use a valid color.')
            logger.error(err)
            sys.exit(2)
    else:
        background_color = colour.Color(default['background_color'])
    config['background_color'] = background_color

    # Set the rest of the frame properties
    config['frame_height'] = 8.0
    config['frame_width'] = (config['frame_height']
                             * config['pixel_width']
                             / config['pixel_height'])
    config['frame_y_radius'] = config['frame_height'] / 2
    config['frame_x_radius'] = config['frame_width'] / 2
    config['top'] = config['frame_y_radius'] * constants.UP
    config['bottom'] = config['frame_y_radius'] * constants.DOWN
    config['left_side'] = config['frame_x_radius'] * constants.LEFT
    config['right_side'] = config['frame_x_radius'] * constants.RIGHT

    # Handle the --tex_template flag.  Note we accept None if the flag is absent
    filename = (os.path.expanduser(args.tex_template)
                if args.tex_template is not None
                else None)

    if filename is not None and not os.access(filename, os.R_OK):
        # custom template not available, fallback to default
        logger.warning(
            f"Custom TeX template {filename} not found or not readable. "
            "Falling back to the default template."
        )
        filename = None
    config['tex_template_file'] = filename
    config['tex_template'] = (TexTemplateFromFile(filename=filename)
                              if filename is not None
                              else TexTemplate())

    return config


def _parse_file_writer_config(config_parser, args):
    """Parse config files and CLI arguments into a single dictionary."""
    # By default, use the CLI section of the digested .cfg files
    default = config_parser['CLI']

    # This will be the final file_writer_config dict exposed to the user
    fw_config = {}

    # Handle input files and scenes.  Note these cannot be set from
    # the .cfg files, only from CLI arguments
    fw_config['input_file'] = args.file
    fw_config['scene_names'] = (args.scene_names
                                if args.scene_names is not None else [])
    fw_config['output_file'] = args.output_file

    # Handle all options that are directly overridden by CLI
    # arguments.  Note ConfigParser options are all strings and each
    # needs to be converted to the appropriate type. Thus, we do this
    # in batches, depending on their type: booleans and strings
    for boolean_opt in ['preview', 'show_file_in_finder', 'quiet', 'sound',
                        'leave_progress_bars', 'write_to_movie', 'save_last_frame',
                        'save_pngs', 'save_as_gif', 'write_all']:
        attr = getattr(args, boolean_opt)
        fw_config[boolean_opt] = (default.getboolean(boolean_opt)
                                  if attr is None else attr)
    # for str_opt in ['media_dir', 'video_dir', 'tex_dir', 'text_dir']:
    for str_opt in ['media_dir']:
        attr = getattr(args, str_opt)
        fw_config[str_opt] = (default[str_opt] if attr is None else attr)
    dir_names = {'video_dir': 'videos',
                 'tex_dir': 'Tex',
                 'text_dir': 'texts'}
    for name in dir_names:
        fw_config[name] = os.path.join(fw_config['media_dir'], dir_names[name])

    # Handle the -s (--save_last_frame) flag: invalidate the -w flag
    # At this point the save_last_frame option has already been set by
    # both CLI and the cfg file, so read the config dict directly
    if fw_config['save_last_frame']:
        fw_config['write_to_movie'] = False

    # Handle the -t (--transparent) flag.  This flag determines which
    # section to use from the .cfg file.
    section = config_parser['transparent'] if args.transparent else default
    for opt in ['png_mode', 'movie_file_extension', 'background_opacity']:
        fw_config[opt] = section[opt]

    # Handle the -n flag.  Read first from the cfg and then override with CLI.
    # These two are integers -- use getint()
    for opt in ['from_animation_number', 'upto_animation_number']:
        fw_config[opt] = default.getint(opt)
    if fw_config['upto_animation_number'] == -1:
        fw_config['upto_animation_number'] = float('inf')
    nflag = args.from_animation_number
    if nflag is not None:
        if ',' in nflag:
            start, end = nflag.split(',')
            fw_config['from_animation_number'] = int(start)
            fw_config['upto_animation_number'] = int(end)
        else:
            fw_config['from_animation_number'] = int(nflag)

    # Handle the --dry_run flag.  This flag determines which section
    # to use from the .cfg file.  All options involved are boolean.
    # Note this overrides the flags -w, -s, -a, -g, and -i.
    if args.dry_run:
        for opt in ['write_to_movie', 'save_last_frame', 'save_pngs',
                    'save_as_gif', 'write_all']:
            fw_config[opt] = config_parser['dry_run'].getboolean(opt)

    # Read in the streaming section -- all values are strings
    fw_config['streaming'] = {opt: config_parser['streaming'][opt]
                              for opt in ['live_stream_name', 'twitch_stream_key',
                                          'streaming_protocol', 'streaming_ip',
                                          'streaming_protocol', 'streaming_client',
                                          'streaming_port', 'streaming_port',
                                          'streaming_console_banner']}

    # For internal use (no CLI flag)
    fw_config['skip_animations'] = any([fw_config['save_last_frame'],
                                        fw_config['from_animation_number']])

    return fw_config


def _parse_cli(arg_list, input=True):
    parser = argparse.ArgumentParser(
        description='Animation engine for explanatory math videos',
        epilog='Made with <3 by the manim community devs'
    )
    if input:
        parser.add_argument(
            "file",
            help="path to file holding the python code for the scene",
        )
        parser.add_argument(
            "scene_names",
            nargs="*",
            help="Name of the Scene class you want to see",
            default=[''],
        )
        parser.add_argument(
            "-o", "--output_file",
            help="Specify the name of the output file, if "
                 "it should be different from the scene class name",
            default='',
        )

    # The following use (action='store_const', const=True) instead of
    # the built-in (action='store_true').  This is because the latter
    # will default to False if not specified, while the former sets no
    # default value.  Since we want to set the default value in
    # manim.cfg rather than here, we use the former.
    parser.add_argument(
        "-p", "--preview",
        action="store_const",
        const=True,
        help="Automatically open the saved file once its done",
    )
    parser.add_argument(
        "-f", "--show_file_in_finder",
        action="store_const",
        const=True,
        help="Show the output file in finder",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_const",
        const=True,
        help="Quiet mode",
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
        "-a", "--write_all",
        action="store_const",
        const=True,
        help="Write all the scenes from a file",
    )
    parser.add_argument(
        "-w", "--write_to_movie",
        action="store_const",
        const=True,
        help="Render the scene as a movie file",
    )
    parser.add_argument(
        "-s", "--save_last_frame",
        action="store_const",
        const=True,
        help="Save the last frame (and do not save movie)",
    )
    parser.add_argument(
        "-g", "--save_pngs",
        action="store_const",
        const=True,
        help="Save each frame as a png",
    )
    parser.add_argument(
        "-i", "--save_as_gif",
        action="store_const",
        const=True,
        help="Save the video as gif",
    )

    # The default value of the following is set in manim.cfg
    parser.add_argument(
        "-c", "--color",
        help="Background color",
    )
    parser.add_argument(
        "--background_opacity",
        help="Background opacity",
    )
    parser.add_argument(
        "--media_dir",
        help="directory to write media",
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
        "-t", "--transparent",
        action="store_true",
        help="Render to a movie file with an alpha channel",
    )

    # The following are mutually exclusive and each overrides
    # FRAME_RATE, PIXEL_HEIGHT, and PIXEL_WIDTH,
    parser.add_argument(
        "-l", "--low_quality",
        action="store_true",
        help="Render at low quality (for fastest rendering)",
    )
    parser.add_argument(
        "-m", "--medium_quality",
        action="store_true",
        help="Render at medium quality (for much faster rendering)",
    )
    parser.add_argument(
        "-e", "--high_quality",
        action="store_true",
        help="Render at high quality (for slightly faster rendering)",
    )
    parser.add_argument(
        "-k", "--fourk_quality",
        action="store_true",
        help="Render at 4K quality (slower rendering)",
    )

    # This overrides any of the above
    parser.add_argument(
        "-r", "--resolution",
        help="Resolution, passed as \"height,width\"",
    )

    # This sets FROM_ANIMATION_NUMBER and UPTO_ANIMATION_NUMBER
    parser.add_argument(
        "-n", "--from_animation_number",
        help="Start rendering not from the first animation, but"
             "from another, specified by its index.  If you pass"
             "in two comma separated values, e.g. \"3,6\", it will end"
             "the rendering at the second value",
    )

    # Specify the manim.cfg file
    parser.add_argument(
        "--config_file",
        help="Specify the configuration file",
    )

    return parser.parse_args(arg_list)


def _init_dirs(config):
    # Make sure all folders exist
    for folder in [config["media_dir"], config["video_dir"],
                   config["tex_dir"], config["text_dir"]]:
        if not os.path.exists(folder):
            os.makedirs(folder)


def _from_command_line():
    """Determine if manim was called from the command line."""
    # Manim can be called from the command line in three different
    # ways.  The first two involve using the manim or manimcm commands
    prog = os.path.split(sys.argv[0])[-1]
    from_cli_command = prog in ['manim', 'manimcm']

    # The third way involves using `python -m manim ...`.  In this
    # case, the CLI arguments passed to manim do not include 'manim',
    # 'manimcm', or even 'python'.  However, the -m flag will always
    # be the first argument.
    from_python_m = sys.argv[0] == '-m'

    return from_cli_command or from_python_m


# Config files to be parsed, in ascending priority
library_wide = os.path.join(os.path.dirname(__file__), 'default.cfg')
config_files = [
    library_wide,
    os.path.expanduser('~/.manim.cfg'),
]

if _from_command_line():
    args = _parse_cli(sys.argv[1:])
    if args.config_file is not None:
        if os.path.exists(args.config_file):
            config_files.append(args.config_file)
        else:
            raise FileNotFoundError(f"Config file {args.config_file} doesn't exist")
    else:
        script_directory_file_config = os.path.join(os.path.dirname(args.file), 'manim.cfg')
        if os.path.exists(script_directory_file_config):
            config_files.append(script_directory_file_config)

else:
    # In this case, we still need an empty args object.
    args = _parse_cli([], input=False)
    # Need to populate the options left out
    args.file, args.scene_names, args.output_file = '', '', ''

config_parser = configparser.ConfigParser()
successfully_read_files = config_parser.read(config_files)
logger.info(f'Read configuration files: {successfully_read_files}')

# this is for internal use when writing output files
file_writer_config = _parse_file_writer_config(config_parser, args)

# this is for the user
config = _parse_config(config_parser, args)
camera_config = config

_init_dirs(file_writer_config)
