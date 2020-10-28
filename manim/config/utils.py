"""
utils.py
--------

Functions to create and set the config.

"""

import os
import sys
import copy
import logging
import configparser
from pathlib import Path
from collections.abc import Mapping, MutableMapping

import numpy as np
import colour

from .. import constants
from ..utils.tex import TexTemplate, TexTemplateFromFile
from .logger import set_file_logger


def init_dirs(config):
    for folder in [
        config["media_dir"],
        config["video_dir"],
        config["tex_dir"],
        config["text_dir"],
        config["log_dir"],
    ]:
        if not os.path.exists(folder):
            if folder == config["log_dir"] and (not config["log_to_file"]):
                pass
            else:
                os.makedirs(folder)


def config_file_paths():
    library_wide = Path.resolve(Path(__file__).parent / "default.cfg")
    if sys.platform.startswith("win32"):
        user_wide = Path.home() / "AppData" / "Roaming" / "Manim" / "manim.cfg"
    else:
        user_wide = Path.home() / ".config" / "manim" / "manim.cfg"
    folder_wide = Path("manim.cfg")
    return [library_wide, user_wide, folder_wide]


def make_config_parser(custom_file=None):
    """Make a ConfigParser object and load the .cfg files.

    Parameters
    ----------
    custom_file : str

        Path to a custom config file.  If used, the folder-wide file in the
        relevant directory will be ignored, if it exists.  If None, the
        folder-wide file will be used, if it exists.

    Notes
    -----
    The folder-wide file can be ignored by passing custom_file.  However, the
    user-wide and library-wide config files cannot be ignored.

    """
    library_wide, user_wide, folder_wide = config_file_paths()
    # From the documentation: "An application which requires initial values to
    # be loaded from a file should load the required file or files using
    # read_file() before calling read() for any optional files."
    # https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.read
    parser = configparser.ConfigParser()
    with open(library_wide) as file:
        parser.read_file(file)  # necessary file

    other_files = [user_wide, custom_file if custom_file else folder_wide]
    parser.read(other_files)    # optional files
    return parser


def determine_quality(args):
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
            hasattr(args, "quality")
            and args.quality == constants.QUALITIES[quality]["flag"]
        ):
            return quality

    for quality in old_qualities:
        if getattr(args, quality, None):
            logging.getLogger("manim").warning(
                f"Option -{quality} is deprecated please use the --quality/-q flag."
            )
            return old_qualities[quality]

    return constants.DEFAULT_QUALITY


class ManimConfig(MutableMapping):

    _OPTS = {
        "background_color",
        "background_opacity",
        "custom_folders",
        "disable_caching",
        "ffmpeg_loglevel",
        "flush_cache",
        "frame_height",
        "frame_rate",
        "frame_width",
        "frame_x_radius",
        "frame_y_radius",
        "from_animation_number",
        "images_dir",
        "input_file",
        "js_renderer_path",
        "leave_progress_bars",
        "log_dir",
        "log_to_file",
        "max_files_cached",
        "media_dir",
        "movie_file_extension",
        "pixel_height",
        "pixel_width",
        "png_mode",
        "preview",
        "progress_bar",
        "save_as_gif",
        "save_last_frame",
        "save_pngs",
        "scene_names",
        "show_in_file_browser",
        "skip_animations",
        "sound",
        "tex_dir",
        "tex_template_file",
        "text_dir",
        "upto_animation_number",
        "use_js_renderer",
        "verbosity",
        "video_dir",
        "write_all",
        "write_to_movie",
    }

    def __init__(self, parser=None):
        self._d = {k: None for k in self._OPTS}
        self._parser = parser
        if parser:
            self.digest_parser(parser)

    # behave like a dict
    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __contains__(self, key):
        try:
            self.__getitem__(key)
            return True
        except AttributeError:
            return False

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        getattr(ManimConfig, key).fset(self, val)  # fset is the property's setter

    def update(self, obj):
        if isinstance(obj, ManimConfig):
            self._d.update(obj._d)

        elif isinstance(obj, dict):
            # First update the underlying _d, then update other properties
            _dict = {k: v for k, v in obj.items() if k in self._d}
            for k, v in _dict.items():
                self[k] = v

            _dict = {k: v for k, v in obj.items() if k not in self._d}
            for k, v in _dict.items():
                self[k] = v


    # don't allow to delete anything
    def __delitem__(self, key):
        raise AttributeError("'ManimConfig' object does not support item deletion")

    def __delattr__(self, key):
        raise AttributeError("'ManimConfig' object does not support item deletion")

    # copy functions
    def copy(self):
        return copy.deepcopy(self)

    def __copy__(self):
        return copy.deepcopy(self)

    def __deepcopy__(self, memo):
        c = ManimConfig()
        c._d = copy.deepcopy(self._d, memo)
        return c

    # helper type-checking methods
    def _set_from_list(self, key, val, values):
        if val in values:
            self._d[key] = val
        else:
            raise ValueError(f"attempted to set {key} to {val}; must be in {values}")

    def _set_boolean(self, key, val):
        if val in [True, False]:
            self._d[key] = val
        else:
            raise ValueError(f"{key} must be boolean")

    def _set_str(self, key, val):
        if isinstance(val, str):
            self._d[key] = val
        elif not val:
            self._d[key] = ""
        else:
            raise ValueError(f"{key} must be str or falsy value")

    def _set_between(self, key, val, lo, hi):
        if lo <= val <= hi:
            self._d[key] = val
        else:
            raise ValueError(f"{key} must be {lo} <= {key} <= {hi}")

    def _set_pos_number(self, key, val, allow_inf):
        if isinstance(val, int) and val > -1:
            self._d[key] = val
        elif allow_inf and (val == -1 or val == float("inf")):
            self._d[key] = float("inf")
        else:
            raise ValueError(
                f"{key} must be a non-negative integer (use -1 for infinity)"
            )

    # builders
    def digest_parser(self, parser):
        self._parser = parser

        # boolean keys
        for key in [
            "write_to_movie",
            "save_last_frame",
            "write_all",
            "save_pngs",
            "save_as_gif",
            "preview",
            "show_in_file_browser",
            "progress_bar",
            "sound",
            "leave_progress_bars",
            "log_to_file",
            "disable_caching",
            "flush_cache",
            "custom_folders",
            "skip_animations",
            "use_js_renderer",
        ]:
            setattr(self, key, parser["CLI"].getboolean(key, fallback=False))

        # int keys
        for key in [
            "from_animation_number",
            "upto_animation_number",
            "frame_rate",
            "max_files_cached",
            "pixel_height",
            "pixel_width",
        ]:
            setattr(self, key, parser["CLI"].getint(key))

        # str keys
        for key in [
            "verbosity",
            "media_dir",
            "log_dir",
            "video_dir",
            "images_dir",
            "text_dir",
            "tex_dir",
            "input_file",
            "output_file",
            "png_mode",
            "movie_file_extension",
            "background_color",
            "js_renderer_path",
        ]:
            setattr(self, key, parser["CLI"].get(key, fallback="", raw=True))

        # float keys
        for key in ["background_opacity"]:
            setattr(self, key, parser["CLI"].getfloat(key))

        # other logic
        self["frame_height"] = 8.0
        self["frame_width"] = (
            self["frame_height"] * self["pixel_width"] / self["pixel_height"]
        )

        val = parser["CLI"].get("tex_template_file")
        if val:
            setattr(self, "tex_template_file", val)

        val = parser["ffmpeg"].get("loglevel")
        if val:
            setattr(self, "ffmpeg_loglevel", val)

        return self

    def digest_args(self, args):
        # if a config file has been passed, digest it first so that other CLI
        # flags supersede it
        if args.config_file:
            self.digest_file(args.config_file)

        self.input_file = args.file
        self.scene_names = args.scene_names if args.scene_names is not None else []
        self.output_file = args.output_file

        for key in [
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
            "transparent",
            "scene_names",
            "verbosity",
            "background_color",
        ]:
            if hasattr(args, key):
                attr = getattr(args, key)
                # if attr is None, then no argument was passed and we should
                # not change the current config
                if attr is not None:
                    self[key] = attr

        # dry_run is special because it can only be set to True
        if hasattr(args, "dry_run"):
            if getattr(args, "dry_run"):
                self["dry_run"] = True

        for key in [
            "media_dir",  # always set this one first
            "video_dir",
            "images_dir",
            "tex_dir",
            "text_dir",
            "log_dir",
            "custom_folders",
            "log_to_file",  # always set this one last
        ]:
            if hasattr(args, key):
                attr = getattr(args, key)
                # if attr is None, then no argument was passed and we should
                # not change the current config
                if attr is not None:
                    self[key] = attr

        # The -s (--save_last_frame) flag invalidates -w (--write_to_movie).
        if self["save_last_frame"]:
            self["write_to_movie"] = False

        # Handle the -n flag.
        nflag = args.from_animation_number
        if nflag is not None:
            if "," in nflag:
                start, end = nflag.split(",")
                self.from_animation_number = int(start)
                self.upto_animation_number = int(end)
            else:
                self.from_animation_number = int(nflag)

        # Handle the quality flags
        self.quality = determine_quality(args)

        # Handle the -r flag.
        rflag = args.resolution
        if rflag is not None:
            try:
                w, h = rflag.split(",")
                self.pixel_width = int(w)
                self.pixel_height = int(h)
            except ValueError:
                raise ValueError(
                    f'invalid argument {rflag} for -r flag (must have a comma ",")'
                )

        # Handle --custom_folders
        if args.custom_folders:
            for opt in ["media_dir", "video_dir", "text_dir", "tex_dir", "log_dir"]:
                self[opt] = self._parser["custom_folders"].get(opt, raw=True)

        return self

    def digest_dict(self, _dict):
        pass

    def digest_file(self, filename):
        if filename:
            return self.digest_parser(make_config_parser(filename))

    # config options are properties
    preview = property(
        lambda self: self._d["preview"],
        lambda self, val: self._set_boolean("preview", val),
        doc="Whether to play the movie once it is done rendering",
    )

    show_in_file_browser = property(
        lambda self: self._d["show_in_file_browser"],
        lambda self, val: self._set_boolean("show_in_file_browser", val),
        doc="Whether to show the rendered file in the file browser",
    )

    progress_bar = property(
        lambda self: self._d["progress_bar"],
        lambda self, val: self._set_boolean("progress_bar", val),
        doc="Whether to show progress bars while rendering animations",
    )

    leave_progress_bars = property(
        lambda self: self._d["leave_progress_bars"],
        lambda self, val: self._set_boolean("leave_progress_bars", val),
        doc="Whether to leave the progress bar for each animations",
    )

    @property
    def log_to_file(self):
        """Whether to save logs to a file"""
        return self._d["log_to_file"]

    @log_to_file.setter
    def log_to_file(self, val):
        self._set_boolean("log_to_file", val)
        if val:
            if not os.path.exists(self["log_dir"]):
                os.makedirs(self["log_dir"])
            set_file_logger(self, self["verbosity"])

    sound = property(
        lambda self: self._d["sound"],
        lambda self, val: self._set_boolean("sound", val),
        doc="Whether to play a sound to notify when a scene is rendered",
    )

    write_to_movie = property(
        lambda self: self._d["write_to_movie"],
        lambda self, val: self._set_boolean("write_to_movie", val),
        doc="Whether to render the scene to a movie file",
    )

    save_last_frame = property(
        lambda self: self._d["save_last_frame"],
        lambda self, val: self._set_boolean("save_last_frame", val),
        doc="Whether to save the last frame of the scene as an image file",
    )

    write_all = property(
        lambda self: self._d["write_all"],
        lambda self, val: self._set_boolean("write_all", val),
        doc="Whether to render all scenes in the input file",
    )

    save_pngs = property(
        lambda self: self._d["save_pngs"],
        lambda self, val: self._set_boolean("save_pngs", val),
        doc="Whether to save all frames in the scene as images files",
    )

    save_as_gif = property(
        lambda self: self._d["save_as_gif"],
        lambda self, val: self._set_boolean("save_as_gif", val),
        doc="Whether to save the rendered scene in .gif format.",
    )

    @property
    def verbosity(self):
        return self._d["verbosity"]

    @verbosity.setter
    def verbosity(self, val):
        """Verbosity level of the logger."""
        self._set_from_list(
            "verbosity",
            val,
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )
        logging.getLogger("manim").setLevel(val)

    ffmpeg_loglevel = property(
        lambda self: self._d["ffmpeg_loglevel"],
        lambda self, val: self._set_from_list(
            "ffmpeg_loglevel", val, ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        ),
        doc="Verbosity level of ffmpeg.",
    )

    pixel_width = property(
        lambda self: self._d["pixel_width"],
        lambda self, val: self._set_pos_number("pixel_width", val, False),
        doc="Frame width in pixels",
    )

    pixel_height = property(
        lambda self: self._d["pixel_height"],
        lambda self, val: self._set_pos_number("pixel_height", val, False),
        doc="Frame height in pixels",
    )

    aspect_ratio = property(
        lambda self: self._d["pixel_width"] / self._d["pixel_height"],
        doc="Aspect ratio (width / height) in pixels",
    )

    frame_height = property(
        lambda self: self._d["frame_height"],
        lambda self, val: self._d.__setitem__("frame_height", val),
        doc="Frame height in logical units",
    )

    frame_width = property(
        lambda self: self._d["frame_width"],
        lambda self, val: self._d.__setitem__("frame_width", val),
        doc="Frame width in logical units",
    )

    frame_y_radius = property(
        lambda self: self._d["frame_height"] / 2,
        lambda self, val: (
            self._d.__setitem__("frame_y_radius", val)
            or self._d.__setitem__("frame_height", 2 * val)
        ),
        doc="Half the frame height",
    )

    frame_x_radius = property(
        lambda self: self._d["frame_width"] / 2,
        lambda self, val: (
            self._d.__setitem__("frame_x_radius", val)
            or self._d.__setitem__("frame_width", 2 * val)
        ),
        doc="Half the frame width",
    )

    top = property(
        lambda self: self.frame_y_radius * constants.UP,
        doc="One unit step in the positive vertical direction",
    )

    bottom = property(
        lambda self: self.frame_y_radius * constants.DOWN,
        doc="One unit step in the negative vertical direction",
    )

    left_side = property(
        lambda self: self.frame_x_radius * constants.LEFT,
        doc="One unit step in the negative horizontal direction",
    )

    right_side = property(
        lambda self: self.frame_x_radius * constants.RIGHT,
        doc="One unit step in the positive horizontal direction",
    )

    frame_rate = property(
        lambda self: self._d["frame_rate"],
        lambda self, val: self._d.__setitem__("frame_rate", val),
        doc="Frame rate in fps (rames per second)",
    )

    background_color = property(
        lambda self: self._d["background_color"],
        lambda self, val: self._d.__setitem__("background_color", colour.Color(val)),
        doc="Background color of the scene.",
    )

    from_animation_number = property(
        lambda self: self._d["from_animation_number"],
        lambda self, val: self._d.__setitem__("from_animation_number", val),
        doc="Set to a number greater than 1 to skip animations.",
    )

    upto_animation_number = property(
        lambda self: self._d["upto_animation_number"],
        lambda self, val: self._set_pos_number("upto_animation_number", val, True),
        doc=(
            "Set to less than the number of animations to skip "
            "animations. Use -1 to avoid skipping."
        ),
    )

    skip_animations = property(
        lambda self: self._d["skip_animations"],
        lambda self, val: self._set_boolean("skip_animations", val),
        doc=(
            "Set to less than the number of animations to skip "
            "animations. Use -1 to avoid skipping."
        ),
    )

    max_files_cached = property(
        lambda self: self._d["max_files_cached"],
        lambda self, val: self._set_pos_number("max_files_cached", val, True),
        doc="Maximum number of files cached. Use -1 for infinity.",
    )

    flush_cache = property(
        lambda self: self._d["flush_cache"],
        lambda self, val: self._set_boolean("flush_cache", val),
        doc="whether to delete all the cached partial movie files.",
    )

    disable_caching = property(
        lambda self: self._d["disable_caching"],
        lambda self, val: self._set_boolean("disable_caching", val),
        doc="whether to use scene caching.",
    )

    png_mode = property(
        lambda self: self._d["png_mode"],
        lambda self, val: self._set_from_list("png_mode", val, ["RGB", "RGBA"]),
        doc="Either RGA (no transparency) or RGBA (with transparency).",
    )

    movie_file_extension = property(
        lambda self: self._d["movie_file_extension"],
        lambda self, val: self._set_from_list(
            "movie_file_extension", val, [".mp4", ".mov"]
        ),
        doc="Either .mp4 or .mov.",
    )

    background_opacity = property(
        lambda self: self._d["background_opacity"],
        lambda self, val: self._set_between("background_opacity", val, 0, 1),
        doc="A number between 0.0 (fully transparent) and 1.0 (fully opaque).",
    )

    frame_size = property(
        lambda self: (self._d["pixel_width"], self._d["pixel_height"]),
        lambda self, tup: (
            self._d.__setitem__("pixel_width", tup[0])
            or self._d.__setitem__("pixel_height", tup[1])
        ),
        doc="",
    )

    @property
    def quality(self):
        """Video quality."""
        keys = ["pixel_width", "pixel_height", "frame_rate"]
        q = {k: self[k] for k in keys}
        for qual in constants.QUALITIES:
            if all([q[k] == constants.QUALITIES[qual][k] for k in keys]):
                return qual
        else:
            return None

    @quality.setter
    def quality(self, qual):
        if qual not in constants.QUALITIES:
            raise KeyError(f"quality must be one of {list(constants.QUALITIES.keys())}")
        q = constants.QUALITIES[qual]
        self.frame_size = q["pixel_width"], q["pixel_height"]
        self.frame_rate = q["frame_rate"]

    @property
    def transparent(self):
        """Whether the background opacity is 0.0."""
        return self._d["background_opacity"] == 0.0

    @transparent.setter
    def transparent(self, val):
        if val:
            self.png_mode = "RGBA"
            self.movie_file_extension = ".mov"
            self.background_opacity = 0.0
        else:
            self.png_mode = "RGB"
            self.movie_file_extension = ".mp4"
            self.background_opacity = 1.0

    @property
    def dry_run(self):
        """Whether dry run is enabled."""
        return (
            self.write_to_movie is False
            and self.write_all is False
            and self.save_last_frame is False
            and self.save_pngs is False
            and self.save_as_gif is False
        )

    @dry_run.setter
    def dry_run(self, val):
        if val:
            self.write_to_movie = False
            self.write_all = False
            self.save_last_frame = False
            self.save_pngs = False
            self.save_as_gif = False
        else:
            raise ValueError(
                "It is unclear what it means to set dry_run to "
                "False.  Instead, try setting each option "
                "individually. (write_to_movie, write_alll, "
                "save_last_frame, save_pngs, or save_as_gif)"
            )

    @property
    def use_js_renderer(self):
        self._d["use_js_renderer"]

    @use_js_renderer.setter
    def use_js_renderer(self, val):
        self._d["use_js_renderer"] = val
        if val:
            self["disable_caching"] = True

    js_renderer_path = property(
        lambda self: self._d["js_renderer_path"],
        lambda self, val: self._d.__setitem__("js_renderer_path", val),
        doc="Path to JS renderer.",
    )

    media_dir = property(
        lambda self: Path(self._d["media_dir"]),
        lambda self, val: self._d.__setitem__("media_dir", val),
        doc="Main output directory, relative to execution directory.",
    )

    def _get_dir(self, key):
        dirs = [
            "media_dir",
            "video_dir",
            "images_dir",
            "text_dir",
            "tex_dir",
            "log_dir",
            "input_file",
            "output_file",
        ]
        dirs.remove(key)
        dirs = {k: self._d[k] for k in dirs}
        path = self._d[key].format(**dirs)
        return Path(path) if path else None

    def _set_dir(self, key, val):
        if isinstance(val, Path):
            self._d.__setitem__(key, str(val))
        else:
            self._d.__setitem__(key, val)

    log_dir = property(
        lambda self: self._get_dir("log_dir"),
        lambda self, val: self._set_dir("log_dir", val),
        doc="Directory to place logs",
    )

    video_dir = property(
        lambda self: self._get_dir("video_dir"),
        lambda self, val: self._set_dir("video_dir", val),
        doc="Directory to place videos",
    )

    images_dir = property(
        lambda self: self._get_dir("images_dir"),
        lambda self, val: self._set_dir("images_dir", val),
        doc="Directory to place images",
    )

    text_dir = property(
        lambda self: self._get_dir("text_dir"),
        lambda self, val: self._set_dir("text_dir", val),
        doc="Directory to place text",
    )

    tex_dir = property(
        lambda self: self._get_dir("tex_dir"),
        lambda self, val: self._set_dir("tex_dir", val),
        doc="Directory to place tex",
    )

    custom_folders = property(
        lambda self: self._d["custom_folders"],
        lambda self, val: self._set_boolean("custom_folders", val),
        doc="Whether to use custom folders.",
    )

    input_file = property(
        lambda self: self._get_dir("input_file"),
        lambda self, val: self._set_dir("input_file", val),
        doc="Input file name.",
    )

    output_file = property(
        lambda self: self._get_dir("output_file"),
        lambda self, val: self._set_dir("output_file", val),
        doc="Output file name.",
    )

    scene_names = property(
        lambda self: self._d["scene_names"],
        lambda self, val: self._d.__setitem__("scene_names", val),
        doc="Scenes to play from file.",
    )

    @property
    def tex_template(self):
        if not hasattr(self, "_tex_template") or not self._tex_template:
            fn = self._d["tex_template_file"]
            if fn:
                self._tex_template = TexTemplateFromFile(filename=fn)
            else:
                self._tex_template = TexTemplate()
        return self._tex_template

    @tex_template.setter
    def tex_template(self, val):
        if isinstance(val, (TexTemplateFromFile, TexTemplate)):
            self._tex_template = val

    @property
    def tex_template_file(self):
        return self._d["tex_template_file"]

    @tex_template_file.setter
    def tex_template_file(self, val):
        if val:
            if not os.access(val, os.R_OK):
                logging.getLogger("manim").warning(
                    f"Custom TeX template {val} not found or not readable."
                )
            else:
                self._d["tex_template_file"] = Path(val)
                self._tex_template = TexTemplateFromFile(filename=val)
        else:
            self._d["tex_template_file"] = val  # actually set the falsy value
            self._tex_template = TexTemplate()  # but don't use it


class ManimFrame(Mapping):
    _OPTS = {
        "pixel_width",
        "pixel_height",
        "aspect_ratio",
        "frame_height",
        "frame_width",
        "frame_y_radius",
        "frame_x_radius",
        "top",
        "bottom",
        "left_side",
        "right_side",
    }
    _CONSTANTS = {
        "UP": np.array((0.0, 1.0, 0.0)),
        "DOWN": np.array((0.0, -1.0, 0.0)),
        "RIGHT": np.array((1.0, 0.0, 0.0)),
        "LEFT": np.array((-1.0, 0.0, 0.0)),
        "IN": np.array((0.0, 0.0, -1.0)),
        "OUT": np.array((0.0, 0.0, 1.0)),
        "ORIGIN": np.array((0.0, 0.0, 0.0)),
        "X_AXIS": np.array((1.0, 0.0, 0.0)),
        "Y_AXIS": np.array((0.0, 1.0, 0.0)),
        "Z_AXIS": np.array((0.0, 0.0, 1.0)),
        "UL": np.array((-1.0, 1.0, 0.0)),
        "UR": np.array((1.0, 1.0, 0.0)),
        "DL": np.array((-1.0, -1.0, 0.0)),
        "DR": np.array((1.0, -1.0, 0.0)),
    }

    def __init__(self, c):
        if not isinstance(c, ManimConfig):
            raise TypeError("argument must be instance of 'ManimConfig'")
        # need to use __dict__ directly because setting attributes is not
        # allowed (see __setattr__)
        self.__dict__["_c"] = c

    # there are required by parent class Mapping to behave like a dict
    def __getitem__(self, key):
        if key in self._OPTS:
            return self._c[key]
        elif key in self._CONSTANTS:
            return self._CONSTANTS[key]
        else:
            raise KeyError(key)

    def __iter__(self):
        return iter(list(self._OPTS) + list(self._CONSTANTS))

    def __len__(self):
        return len(self._OPTS)

    # make this truly immutable
    def __setattr__(self, attr, val):
        raise TypeError("'ManimFrame' object does not support item assignment")

    def __setitem__(self, key, val):
        raise TypeError("'ManimFrame' object does not support item assignment")

    def __delitem__(self, key):
        raise TypeError("'ManimFrame' object does not support item deletion")


for opt in list(ManimFrame._OPTS) + list(ManimFrame._CONSTANTS):
    setattr(ManimFrame, opt, property(lambda self, o=opt: self[o]))
