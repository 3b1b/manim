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

from .logger import logger

__all__ = ['config']


def _parse_config(input_file, config_files):
    # This only loads the [CLI] section of the manim.cfg file.  If using
    # CLI arguments, the _update_config_with_args function will take care
    # of overriding any of these defaults.
    config_parser = configparser.ConfigParser()
    successfully_read_files = config_parser.read(config_files)
    if not successfully_read_files:
        raise FileNotFoundError('Config file could not be read')

    # Put everything in a dict
    config = {}

    # Make sure we have an input file
    config['INPUT_FILE'] = input_file

    # ConfigParser options are all strings, so need to convert to the
    # appropriate type

    # booleans
    for opt in ['PREVIEW', 'SHOW_FILE_IN_FINDER', 'QUIET', 'SOUND',
                'LEAVE_PROGRESS_BARS', 'WRITE_ALL', 'WRITE_TO_MOVIE',
                'SAVE_LAST_FRAME', 'DRY_RUN', 'SAVE_PNGS', 'SAVE_AS_GIF']:
        config[opt] = config_parser['CLI'].getboolean(opt)

    # numbers
    for opt in ['FROM_ANIMATION_NUMBER', 'UPTO_ANIMATION_NUMBER',
                'BACKGROUND_OPACITY']:
        config[opt] = config_parser['CLI'].getint(opt)

    # UPTO_ANIMATION_NUMBER is special because -1 actually means np.inf
    if config['UPTO_ANIMATION_NUMBER'] == -1:
        import numpy as np
        config['UPTO_ANIMATION_NUMBER'] = np.inf

    # strings
    for opt in ['PNG_MODE', 'MOVIE_FILE_EXTENSION', 'MEDIA_DIR',
                'OUTPUT_FILE', 'VIDEO_DIR', 'TEX_DIR', 'TEXT_DIR',
                'BACKGROUND_COLOR']:
        config[opt] = config_parser['CLI'][opt]

    # streaming section -- all values are strings
    config['STREAMING'] = {}
    for opt in ['LIVE_STREAM_NAME', 'TWITCH_STREAM_KEY',
                'STREAMING_PROTOCOL', 'STREAMING_PROTOCOL', 'STREAMING_IP',
                'STREAMING_PORT', 'STREAMING_PORT', 'STREAMING_CLIENT',
                'STREAMING_CONSOLE_BANNER']:
        config['STREAMING'][opt] = config_parser['streaming'][opt]

    # for internal use (no CLI flag)
    config['SKIP_ANIMATIONS'] = any([
        config['SAVE_LAST_FRAME'],
        config['FROM_ANIMATION_NUMBER'],
    ])

    # camera config -- all happen to be integers
    config['CAMERA_CONFIG'] = {}
    for opt in ['FRAME_RATE', 'PIXEL_HEIGHT', 'PIXEL_WIDTH']:
        config['CAMERA_CONFIG'][opt] = config_parser['CLI'].getint(opt)

    # file writer config -- just pull them from the overall config for now
    config['FILE_WRITER_CONFIG'] = {key: config[key] for key in [
        "WRITE_TO_MOVIE", "SAVE_LAST_FRAME", "SAVE_PNGS",
        "SAVE_AS_GIF", "PNG_MODE", "MOVIE_FILE_EXTENSION",
        "OUTPUT_FILE", "INPUT_FILE"]}

    return config, config_parser


def _parse_cli():
    parser = argparse.ArgumentParser(
        description='Animation engine for explanatory math videos',
        epilog='Made with <3 by the manim community devs'
    )
    parser.add_argument(
        "file",
        help="path to file holding the python code for the scene",
    )
    parser.add_argument(
        "--scene_names",
        nargs="*",
        help="Name of the Scene class you want to see",
    )
    parser.add_argument(
        "-o", "--output_file",
        help="Specify the name of the output file, if"
             "it should be different from the scene class name",
    )

    # Note the following use (action='store_const', const=True),
    # instead of using the built-in (action='store_true').  The reason
    # is that these two are not equivalent.  The latter is equivalent
    # to (action='store_const', const=True, default=False), while the
    # former sets no default value.  We do not want to set the default
    # here, but in the manim.cfg file.  Therefore we use the latter,
    # (action='store_const', const=True).
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
        help="Save the last frame",
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
    video_group = parser.add_mutually_exclusive_group()
    video_group.add_argument(
        "--video_dir",
        help="directory to write file tree for video",
    )
    parser.add_argument(
        "--tex_dir",
        help="directory to write tex",
    )
    parser.add_argument(
        "--text_dir",
        help="directory to write text",
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

    return parser.parse_args()


def _update_config_with_args(config, config_parser, args):
    # Take care of options that do not have defaults in manim.cfg
    config['FILE'] = args.file
    config['SCENE_NAMES'] = (args.scene_names
                             if args.scene_names is not None else [])

    # Flags that directly override config defaults.
    for opt in ['PREVIEW', 'SHOW_FILE_IN_FINDER', 'QUIET', 'SOUND',
                'LEAVE_PROGRESS_BARS', 'WRITE_ALL', 'WRITE_TO_MOVIE',
                'SAVE_LAST_FRAME', 'SAVE_PNGS', 'SAVE_AS_GIF', 'MEDIA_DIR',
                'VIDEO_DIR', 'TEX_DIR', 'TEXT_DIR', 'BACKGROUND_OPACITY',
                'OUTPUT_FILE']:
        if getattr(args, opt.lower()) is not None:
            config[opt] = getattr(args, opt.lower())

   # Parse the -n flag.
    nflag = args.from_animation_number
    if nflag is not None:
        if ',' in nflag:
            start, end = nflag.split(',')
            config['FROM_ANIMATION_NUMBER'] = int(start)
            config['UPTO_ANIMATION_NUMBER'] = int(end)
        else:
            config['FROM_ANIMATION_NUMBER'] = int(nflag)

    # The following flags use the options in the corresponding manim.cfg
    # sections to override default options.  For example, passing the -t
    # (--transparent) flag takes all of the options defined in the
    # [transparent] section of manim.cfg and uses their values to override
    # the values of those options defined in CLI.

    # -t, --transparent
    if args.transparent:
        config.update({
            'PNG_MODE': config_parser['transparent']['PNG_MODE'],
            'MOVIE_FILE_EXTENSION': config_parser['transparent']['MOVIE_FILE_EXTENSION'],
            'BACKGROUND_OPACITY': config_parser['transparent'].getfloat('BACKGROUND_OPACITY')
        })

    # --dry_run happens to override options that are all booleans
    if args.dry_run:
        config.update({opt.upper(): config_parser['dry_run'].getboolean(opt)
                       for opt in config_parser['dry_run']})

    # the *_quality arguments happen to override options that are all ints
    for flag in ['fourk_quality', 'high_quality', 'medium_quality',
                 'low_quality']:
        if getattr(args, flag) is not None:
            config['CAMERA_CONFIG'].update(
                {opt.upper(): config_parser[flag].getint(opt)
                 for opt in config_parser[flag]})

    # Parse the -r (--resolution) flag.  Note the -r flag does not
    # correspond to any section in manim.cfg, but overrides the same
    # options as the *_quality sections.
    if args.resolution is not None:
        if  "," in args.resolution:
            height_str, width_str = args.resolution.split(",")
            height = int(height_str)
            width = int(width_str)
        else:
            height = int(args.resolution)
            width = int(16 * height / 9)
        config['CAMERA_CONFIG'].update({'pixel_height': height,
                                        'pixel_width': width})

    # Parse the -c (--color) flag
    if args.color is not None:
        try:
            config['CAMERA_CONFIG']['BACKGROUND_COLOR'] = colour.Color(args.color)
        except AttributeError as err:
            logger.warning('Please use a valid color')
            logger.error(err)
            sys.exit(2)

    # As before, make FILE_WRITER_CONFIG by pulling form the overall
    config['FILE_WRITER_CONFIG'] = {key: config[key] for key in [
        "WRITE_TO_MOVIE", "SAVE_LAST_FRAME", "SAVE_PNGS",
        "SAVE_AS_GIF", "PNG_MODE", "MOVIE_FILE_EXTENSION",
        "OUTPUT_FILE", "INPUT_FILE"]}

    return config


def _init_dirs(config):
    if not (config["VIDEO_DIR"] and config["TEX_DIR"]):
        if config["MEDIA_DIR"]:
            if not os.path.isdir(config["MEDIA_DIR"]):
                os.makedirs(config["MEDIA_DIR"])
        if not os.path.isdir(config["MEDIA_DIR"]):
            config["MEDIA_DIR"] = "./media"
        else:
            logger.warning(
                f"Media will be written to {config['media_dir'] + os.sep}. You can change "
                "this behavior with the --media_dir flag, or by adjusting manim.cfg."
            )
    else:
        if config["MEDIA_DIR"]:
            logger.warning(
                "Ignoring --media_dir, since both --tex_dir and --video_dir were passed."
            )

    # Make sure all folders exist
    for folder in [config["VIDEO_DIR"], config["TEX_DIR"], config["TEXT_DIR"]]:
        if not os.path.exists(folder):
            os.makedirs(folder)


# Config files to be parsed, in ascending priority
library_wide = os.path.join(os.path.dirname(__file__), 'default.cfg'),
config_files = [
    # Lowest priority: library-wide defaults
    library_wide,
    # Medium priority: look for a 'manim.cfg' in the user home
    os.path.expanduser('~/.manim.cfg'),
    # Highest priority: look for a 'manim.cfg' in the current dir
    os.path.join(os.getcwd(), 'manim.cfg'),
    ]

prog = os.path.split(sys.argv[0])[-1]
if prog in ['manim', 'manimcm']:
    # If called as entrypoint, set default config, and override the
    # defaults using CLI arguments
    args = _parse_cli()

    # If the user specified a config file, only use that one and the
    # library-wide defaults.
    if args.config_file is not None:
        config_files = [library_wide, args.config_file]

    config, config_parser = _parse_config(args.file, config_files)
    _update_config_with_args(config, config_parser, args)

else:
    config, _ = _parse_config('', config_files)

_init_dirs(config)
