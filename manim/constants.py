"""
Constant definitions.
"""

import typing

import numpy as np

# Messages
NOT_SETTING_FONT_MSG: str = """
You haven't set font.
If you are not using English, this may cause text rendering problem.
You set font like:
text = Text('your text', font='your font')
"""
SCENE_NOT_FOUND_MESSAGE: str = """
   {} is not in the script
"""
CHOOSE_NUMBER_MESSAGE: str = """
Choose number corresponding to desired scene/arguments.
(Use comma separated list for multiple entries)
Choice(s): """
INVALID_NUMBER_MESSAGE: str = "Invalid scene numbers have been specified. Aborting."
NO_SCENE_MESSAGE: str = """
   There are no scenes inside that module
"""

# Cairo and Pango stuff
NORMAL: str = "NORMAL"
ITALIC: str = "ITALIC"
OBLIQUE: str = "OBLIQUE"
BOLD: str = "BOLD"
# Only for Pango from below
THIN: str = "THIN"
ULTRALIGHT: str = "ULTRALIGHT"
LIGHT: str = "LIGHT"
SEMILIGHT: str = "SEMILIGHT"
BOOK: str = "BOOK"
MEDIUM: str = "MEDIUM"
SEMIBOLD: str = "SEMIBOLD"
ULTRABOLD: str = "ULTRABOLD"
HEAVY: str = "HEAVY"
ULTRAHEAVY: str = "ULTRAHEAVY"


# Geometry: directions
ORIGIN: np.ndarray = np.array((0.0, 0.0, 0.0))
"""The center of the coordinate system."""

UP: np.ndarray = np.array((0.0, 1.0, 0.0))
"""One unit step in the positive Y direction."""

DOWN: np.ndarray = np.array((0.0, -1.0, 0.0))
"""One unit step in the negative Y direction."""

RIGHT: np.ndarray = np.array((1.0, 0.0, 0.0))
"""One unit step in the positive X direction."""

LEFT: np.ndarray = np.array((-1.0, 0.0, 0.0))
"""One unit step in the negative X direction."""

IN: np.ndarray = np.array((0.0, 0.0, -1.0))
"""One unit step in the negative Z direction."""

OUT: np.ndarray = np.array((0.0, 0.0, 1.0))
"""One unit step in the positive Z direction."""

# Geometry: axes
X_AXIS: np.ndarray = np.array((1.0, 0.0, 0.0))
Y_AXIS: np.ndarray = np.array((0.0, 1.0, 0.0))
Z_AXIS: np.ndarray = np.array((0.0, 0.0, 1.0))

# Geometry: useful abbreviations for diagonals
UL: np.ndarray = UP + LEFT
"""One step up plus one step left."""

UR: np.ndarray = UP + RIGHT
"""One step up plus one step right."""

DL: np.ndarray = DOWN + LEFT
"""One step down plus one step left."""

DR: np.ndarray = DOWN + RIGHT
"""One step down plus one step right."""

# Geometry
START_X: int = 30
START_Y: int = 20

# Default buffers (padding)
SMALL_BUFF: float = 0.1
MED_SMALL_BUFF: float = 0.25
MED_LARGE_BUFF: float = 0.5
LARGE_BUFF: float = 1
DEFAULT_MOBJECT_TO_EDGE_BUFFER: float = MED_LARGE_BUFF
DEFAULT_MOBJECT_TO_MOBJECT_BUFFER: float = MED_SMALL_BUFF

# Times in seconds
DEFAULT_POINTWISE_FUNCTION_RUN_TIME: float = 3.0
DEFAULT_WAIT_TIME: float = 1.0

# Misc
DEFAULT_POINT_DENSITY_2D: int = 25
DEFAULT_POINT_DENSITY_1D: int = 10
DEFAULT_STROKE_WIDTH: int = 4

# Mathematical constants
PI: float = np.pi
"""The ratio of the circumference of a circle to its diameter."""

TAU: float = 2 * PI
"""The ratio of the circumference of a circle to its radius."""

DEGREES: float = TAU / 360
"""The exchange rate between radians and degrees."""

# ffmpeg stuff
FFMPEG_BIN: str = "ffmpeg"

# gif stuff
GIF_FILE_EXTENSION: str = ".gif"

FFMPEG_VERBOSITY_MAP: typing.Dict[str, str] = {
    "DEBUG": "error",
    "INFO": "error",
    "WARNING": "error",
    "ERROR": "error",
    "CRITICAL": "fatal",
}
VERBOSITY_CHOICES = FFMPEG_VERBOSITY_MAP.keys()
WEBGL_RENDERER_INFO: str = (
    "The Electron frontend to Manim is hosted at "
    "https://github.com/ManimCommunity/manim-renderer. After cloning and building it, "
    "you can either start it prior to running Manim or specify the path to the "
    "executable with the --webgl_renderer_path flag."
)

# Video qualities
QUALITIES: typing.Dict[str, typing.Dict[str, typing.Union[str, int, None]]] = {
    "fourk_quality": {
        "flag": "k",
        "pixel_height": 2160,
        "pixel_width": 3840,
        "frame_rate": 60,
    },
    "production_quality": {
        "flag": "p",
        "pixel_height": 1440,
        "pixel_width": 2560,
        "frame_rate": 60,
    },
    "high_quality": {
        "flag": "h",
        "pixel_height": 1080,
        "pixel_width": 1920,
        "frame_rate": 60,
    },
    "medium_quality": {
        "flag": "m",
        "pixel_height": 720,
        "pixel_width": 1280,
        "frame_rate": 30,
    },
    "low_quality": {
        "flag": "l",
        "pixel_height": 480,
        "pixel_width": 854,
        "frame_rate": 15,
    },
    "example_quality": {
        "flag": None,
        "pixel_height": 480,
        "pixel_width": 854,
        "frame_rate": 30,
    },
}

DEFAULT_QUALITY: str = "high_quality"
DEFAULT_QUALITY_SHORT = QUALITIES[DEFAULT_QUALITY]["flag"]
