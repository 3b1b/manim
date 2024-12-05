from __future__ import annotations
import numpy as np

from manimlib.config import get_camera_config
from manimlib.config import FRAME_HEIGHT

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List
    from manimlib.typing import ManimColor, Vect3


# TODO, it feels a bit unprincipled to have some global constants
# depend on the output of this function, all for all that configuration
# code to be run merely upon importing from this file
CAMERA_CONFIG = get_camera_config()

# Sizes relevant to default camera frame
ASPECT_RATIO: float = CAMERA_CONFIG['pixel_width'] / CAMERA_CONFIG['pixel_height']
# FRAME_HEIGHT: float = 8.0
FRAME_WIDTH: float = FRAME_HEIGHT * ASPECT_RATIO
FRAME_SHAPE: tuple[float, float] = (FRAME_WIDTH, FRAME_HEIGHT)
FRAME_Y_RADIUS: float = FRAME_HEIGHT / 2
FRAME_X_RADIUS: float = FRAME_WIDTH / 2

DEFAULT_PIXEL_HEIGHT: int = CAMERA_CONFIG['pixel_height']
DEFAULT_PIXEL_WIDTH: int = CAMERA_CONFIG['pixel_width']
DEFAULT_FPS: int = 30

SMALL_BUFF: float = 0.1
MED_SMALL_BUFF: float = 0.25
MED_LARGE_BUFF: float = 0.5
LARGE_BUFF: float = 1

DEFAULT_MOBJECT_TO_EDGE_BUFFER: float = MED_LARGE_BUFF
DEFAULT_MOBJECT_TO_MOBJECT_BUFFER: float = MED_SMALL_BUFF


# In seconds
DEFAULT_WAIT_TIME: float = 1.0


ORIGIN: Vect3 = np.array([0., 0., 0.])
UP: Vect3 = np.array([0., 1., 0.])
DOWN: Vect3 = np.array([0., -1., 0.])
RIGHT: Vect3 = np.array([1., 0., 0.])
LEFT: Vect3 = np.array([-1., 0., 0.])
IN: Vect3 = np.array([0., 0., -1.])
OUT: Vect3 = np.array([0., 0., 1.])
X_AXIS: Vect3 = np.array([1., 0., 0.])
Y_AXIS: Vect3 = np.array([0., 1., 0.])
Z_AXIS: Vect3 = np.array([0., 0., 1.])

NULL_POINTS = np.array([[0., 0., 0.]])

# Useful abbreviations for diagonals
UL: Vect3 = UP + LEFT
UR: Vect3 = UP + RIGHT
DL: Vect3 = DOWN + LEFT
DR: Vect3 = DOWN + RIGHT

TOP: Vect3 = FRAME_Y_RADIUS * UP
BOTTOM: Vect3 = FRAME_Y_RADIUS * DOWN
LEFT_SIDE: Vect3 = FRAME_X_RADIUS * LEFT
RIGHT_SIDE: Vect3 = FRAME_X_RADIUS * RIGHT

PI: float = np.pi
TAU: float = 2 * PI
DEGREES: float = TAU / 360
# Nice to have a constant for readability
# when juxtaposed with expressions like 30 * DEGREES
RADIANS: float = 1

FFMPEG_BIN: str = "ffmpeg"

JOINT_TYPE_MAP: dict = {
    "no_joint": 0,
    "auto": 1,
    "bevel": 2,
    "miter": 3,
}

# Related to Text
NORMAL: str = "NORMAL"
ITALIC: str = "ITALIC"
OBLIQUE: str = "OBLIQUE"
BOLD: str = "BOLD"

DEFAULT_STROKE_WIDTH: float = 4

# For keyboard interactions
CTRL_SYMBOL: int = 65508
SHIFT_SYMBOL: int = 65505
COMMAND_SYMBOL: int = 65517
DELETE_SYMBOL: int = 65288
ARROW_SYMBOLS: list[int] = list(range(65361, 65365))

# Colors

BLUE_E: ManimColor = "#1C758A"
BLUE_D: ManimColor = "#29ABCA"
BLUE_C: ManimColor = "#58C4DD"
BLUE_B: ManimColor = "#9CDCEB"
BLUE_A: ManimColor = "#C7E9F1"
TEAL_E: ManimColor = "#49A88F"
TEAL_D: ManimColor = "#55C1A7"
TEAL_C: ManimColor = "#5CD0B3"
TEAL_B: ManimColor = "#76DDC0"
TEAL_A: ManimColor = "#ACEAD7"
GREEN_E: ManimColor = "#699C52"
GREEN_D: ManimColor = "#77B05D"
GREEN_C: ManimColor = "#83C167"
GREEN_B: ManimColor = "#A6CF8C"
GREEN_A: ManimColor = "#C9E2AE"
YELLOW_E: ManimColor = "#E8C11C"
YELLOW_D: ManimColor = "#F4D345"
YELLOW_C: ManimColor = "#FFFF00"
YELLOW_B: ManimColor = "#FFEA94"
YELLOW_A: ManimColor = "#FFF1B6"
GOLD_E: ManimColor = "#C78D46"
GOLD_D: ManimColor = "#E1A158"
GOLD_C: ManimColor = "#F0AC5F"
GOLD_B: ManimColor = "#F9B775"
GOLD_A: ManimColor = "#F7C797"
RED_E: ManimColor = "#CF5044"
RED_D: ManimColor = "#E65A4C"
RED_C: ManimColor = "#FC6255"
RED_B: ManimColor = "#FF8080"
RED_A: ManimColor = "#F7A1A3"
MAROON_E: ManimColor = "#94424F"
MAROON_D: ManimColor = "#A24D61"
MAROON_C: ManimColor = "#C55F73"
MAROON_B: ManimColor = "#EC92AB"
MAROON_A: ManimColor = "#ECABC1"
PURPLE_E: ManimColor = "#644172"
PURPLE_D: ManimColor = "#715582"
PURPLE_C: ManimColor = "#9A72AC"
PURPLE_B: ManimColor = "#B189C6"
PURPLE_A: ManimColor = "#CAA3E8"
GREY_E: ManimColor = "#222222"
GREY_D: ManimColor = "#444444"
GREY_C: ManimColor = "#888888"
GREY_B: ManimColor = "#BBBBBB"
GREY_A: ManimColor = "#DDDDDD"
WHITE: ManimColor = "#FFFFFF"
BLACK: ManimColor = "#000000"
GREY_BROWN: ManimColor = "#736357"
DARK_BROWN: ManimColor = "#8B4513"
LIGHT_BROWN: ManimColor = "#CD853F"
PINK: ManimColor = "#D147BD"
LIGHT_PINK: ManimColor = "#DC75CD"
GREEN_SCREEN: ManimColor = "#00FF00"
ORANGE: ManimColor = "#FF862F"

MANIM_COLORS: List[ManimColor] = [
    BLACK, GREY_E, GREY_D, GREY_C, GREY_B, GREY_A, WHITE,
    BLUE_E, BLUE_D, BLUE_C, BLUE_B, BLUE_A,
    TEAL_E, TEAL_D, TEAL_C, TEAL_B, TEAL_A,
    GREEN_E, GREEN_D, GREEN_C, GREEN_B, GREEN_A,
    YELLOW_E, YELLOW_D, YELLOW_C, YELLOW_B, YELLOW_A,
    GOLD_E, GOLD_D, GOLD_C, GOLD_B, GOLD_A,
    RED_E, RED_D, RED_C, RED_B, RED_A,
    MAROON_E, MAROON_D, MAROON_C, MAROON_B, MAROON_A,
    PURPLE_E, PURPLE_D, PURPLE_C, PURPLE_B, PURPLE_A,
    GREY_BROWN, DARK_BROWN, LIGHT_BROWN,
    PINK, LIGHT_PINK,
]

# Abbreviated names for the "median" colors
BLUE: ManimColor = BLUE_C
TEAL: ManimColor = TEAL_C
GREEN: ManimColor = GREEN_C
YELLOW: ManimColor = YELLOW_C
GOLD: ManimColor = GOLD_C
RED: ManimColor = RED_C
MAROON: ManimColor = MAROON_C
PURPLE: ManimColor = PURPLE_C
GREY: ManimColor = GREY_C

COLORMAP_3B1B: List[ManimColor] = [BLUE_E, GREEN, YELLOW, RED]
