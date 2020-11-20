"""
Constant definitions.
"""

import numpy as np


# Messages
NOT_SETTING_FONT_MSG = """
You haven't set font.
If you are not using English, this may cause text rendering problem.
You set font like:
text = Text('your text', font='your font')
or:
class MyText(Text):
    CONFIG = {
        'font': 'My Font'
    }
"""
SCENE_NOT_FOUND_MESSAGE = """
   {} is not in the script
"""
CHOOSE_NUMBER_MESSAGE = """
Choose number corresponding to desired scene/arguments.
(Use comma separated list for multiple entries)
Choice(s): """
INVALID_NUMBER_MESSAGE = "Invalid scene numbers have been specified. Aborting."
NO_SCENE_MESSAGE = """
   There are no scenes inside that module
"""

# Cairo and Pango stuff
NORMAL = "NORMAL"
ITALIC = "ITALIC"
OBLIQUE = "OBLIQUE"
BOLD = "BOLD"
# Only for Pango from below
THIN = "THIN"
ULTRALIGHT = "ULTRALIGHT"
LIGHT = "LIGHT"
SEMILIGHT = "SEMILIGHT"
BOOK = "BOOK"
MEDIUM = "MEDIUM"
SEMIBOLD = "SEMIBOLD"
ULTRABOLD = "ULTRABOLD"
HEAVY = "HEAVY"
ULTRAHEAVY = "ULTRAHEAVY"


# Geometry: directions
ORIGIN = np.array((0.0, 0.0, 0.0))
"""The center of the coordinate system."""

UP = np.array((0.0, 1.0, 0.0))
"""One unit step in the positive Y direction."""

DOWN = np.array((0.0, -1.0, 0.0))
"""One unit step in the negative Y direction."""

RIGHT = np.array((1.0, 0.0, 0.0))
"""One unit step in the positive X direction."""

LEFT = np.array((-1.0, 0.0, 0.0))
"""One unit step in the negative X direction."""

IN = np.array((0.0, 0.0, -1.0))
"""One unit step in the negative Z direction."""

OUT = np.array((0.0, 0.0, 1.0))
"""One unit step in the positive Z direction."""

# Geometry: axes
X_AXIS = np.array((1.0, 0.0, 0.0))
Y_AXIS = np.array((0.0, 1.0, 0.0))
Z_AXIS = np.array((0.0, 0.0, 1.0))

# Geometry: useful abbreviations for diagonals
UL = UP + LEFT
"""One step up plus one step left."""

UR = UP + RIGHT
"""One step up plus one step right."""

DL = DOWN + LEFT
"""One step down plus one step left."""

DR = DOWN + RIGHT
"""One step down plus one step right."""

# Geometry
START_X = 30
START_Y = 20

# Default buffers (padding)
SMALL_BUFF = 0.1
MED_SMALL_BUFF = 0.25
MED_LARGE_BUFF = 0.5
LARGE_BUFF = 1
DEFAULT_MOBJECT_TO_EDGE_BUFFER = MED_LARGE_BUFF
DEFAULT_MOBJECT_TO_MOBJECT_BUFFER = MED_SMALL_BUFF

# Times in seconds
DEFAULT_POINTWISE_FUNCTION_RUN_TIME = 3.0
DEFAULT_WAIT_TIME = 1.0

# Misc
DEFAULT_POINT_DENSITY_2D = 25
DEFAULT_POINT_DENSITY_1D = 250
DEFAULT_STROKE_WIDTH = 4

# Mathematical constants
PI = np.pi
"""The ratio of the circumference of a circle to its diameter."""

TAU = 2 * PI
"""The ratio of the circumference of a circle to its radius."""

DEGREES = TAU / 360
"""The exchange rate between radians and degrees."""

# ffmpeg stuff
FFMPEG_BIN = "ffmpeg"

# gif stuff
GIF_FILE_EXTENSION = ".gif"

FFMPEG_VERBOSITY_MAP = {
    "DEBUG": "error",
    "INFO": "error",
    "WARNING": "error",
    "ERROR": "error",
    "CRITICAL": "fatal",
}
VERBOSITY_CHOICES = FFMPEG_VERBOSITY_MAP.keys()
JS_RENDERER_INFO = (
    "The Electron frontend to Manim is hosted at "
    "https://github.com/ManimCommunity/manim-renderer. After cloning and building it, "
    "you can either start it prior to running Manim or specify the path to the "
    "executable with the --js_renderer_path flag."
)

# Video qualities
QUALITIES = {
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

DEFAULT_QUALITY = "high_quality"
DEFAULT_QUALITY_SHORT = QUALITIES[DEFAULT_QUALITY]["flag"]
