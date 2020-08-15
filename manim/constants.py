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

# Cairo stuff
NORMAL = "NORMAL"
ITALIC = "ITALIC"
OBLIQUE = "OBLIQUE"
BOLD = "BOLD"

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

# Colors
COLOR_MAP = {
    "DARK_BLUE": "#236B8E",
    "DARK_BROWN": "#8B4513",
    "LIGHT_BROWN": "#CD853F",
    "BLUE_E": "#1C758A",
    "BLUE_D": "#29ABCA",
    "BLUE_C": "#58C4DD",
    "BLUE_B": "#9CDCEB",
    "BLUE_A": "#C7E9F1",
    "TEAL_E": "#49A88F",
    "TEAL_D": "#55C1A7",
    "TEAL_C": "#5CD0B3",
    "TEAL_B": "#76DDC0",
    "TEAL_A": "#ACEAD7",
    "GREEN_E": "#699C52",
    "GREEN_D": "#77B05D",
    "GREEN_C": "#83C167",
    "GREEN_B": "#A6CF8C",
    "GREEN_A": "#C9E2AE",
    "YELLOW_E": "#E8C11C",
    "YELLOW_D": "#F4D345",
    "YELLOW_C": "#FFFF00",
    "YELLOW_B": "#FFEA94",
    "YELLOW_A": "#FFF1B6",
    "GOLD_E": "#C78D46",
    "GOLD_D": "#E1A158",
    "GOLD_C": "#F0AC5F",
    "GOLD_B": "#F9B775",
    "GOLD_A": "#F7C797",
    "RED_E": "#CF5044",
    "RED_D": "#E65A4C",
    "RED_C": "#FC6255",
    "RED_B": "#FF8080",
    "RED_A": "#F7A1A3",
    "MAROON_E": "#94424F",
    "MAROON_D": "#A24D61",
    "MAROON_C": "#C55F73",
    "MAROON_B": "#EC92AB",
    "MAROON_A": "#ECABC1",
    "PURPLE_E": "#644172",
    "PURPLE_D": "#715582",
    "PURPLE_C": "#9A72AC",
    "PURPLE_B": "#B189C6",
    "PURPLE_A": "#CAA3E8",
    "WHITE": "#FFFFFF",
    "BLACK": "#000000",
    "LIGHT_GRAY": "#BBBBBB",
    "LIGHT_GREY": "#BBBBBB",
    "GRAY": "#888888",
    "GREY": "#888888",
    "DARK_GREY": "#444444",
    "DARK_GRAY": "#444444",
    "DARKER_GREY": "#222222",
    "DARKER_GRAY": "#222222",
    "GREY_BROWN": "#736357",
    "PINK": "#D147BD",
    "LIGHT_PINK": "#DC75CD",
    "GREEN_SCREEN": "#00FF00",
    "ORANGE": "#FF862F",
}
COLOR_MAP.update(
    {
        name.replace("_C", ""): COLOR_MAP[name]
        for name in COLOR_MAP
        if name.endswith("_C")
    }
)
PALETTE = list(COLOR_MAP.values())
locals().update(COLOR_MAP)
FFMPEG_VERBOSITY_MAP = {
    "DEBUG": "error",
    "INFO": "error",
    "WARNING": "error",
    "ERROR": "error",
    "CRITICAL": "fatal",
}
VERBOSITY_CHOICES = FFMPEG_VERBOSITY_MAP.keys()
