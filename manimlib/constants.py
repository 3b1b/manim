from __future__ import annotations
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List
    from manimlib.typing import ManimColor, Vect3

# See manimlib/default_config.yml
from manimlib.config import GLOBAL_CONFIG


DEFAULT_RESOLUTION: tuple[int, int] = GLOBAL_CONFIG["camera"]["resolution"]
DEFAULT_PIXEL_WIDTH: int = DEFAULT_RESOLUTION[0]
DEFAULT_PIXEL_HEIGHT: int = DEFAULT_RESOLUTION[1]
DEFAULT_FPS: int = GLOBAL_CONFIG["camera"]["fps"]

# Sizes relevant to default camera frame
ASPECT_RATIO: float = DEFAULT_PIXEL_WIDTH / DEFAULT_PIXEL_HEIGHT
FRAME_HEIGHT: float = GLOBAL_CONFIG["sizes"]["frame_height"]
FRAME_WIDTH: float = FRAME_HEIGHT * ASPECT_RATIO
FRAME_SHAPE: tuple[float, float] = (FRAME_WIDTH, FRAME_HEIGHT)
FRAME_Y_RADIUS: float = FRAME_HEIGHT / 2
FRAME_X_RADIUS: float = FRAME_WIDTH / 2


# Helpful values for positioning mobjects
SMALL_BUFF: float = GLOBAL_CONFIG["sizes"]["small_buff"]
MED_SMALL_BUFF: float = GLOBAL_CONFIG["sizes"]["med_small_buff"]
MED_LARGE_BUFF: float = GLOBAL_CONFIG["sizes"]["med_large_buff"]
LARGE_BUFF: float = GLOBAL_CONFIG["sizes"]["large_buff"]

DEFAULT_MOBJECT_TO_EDGE_BUFF: float = GLOBAL_CONFIG["sizes"]["default_mobject_to_edge_buff"]
DEFAULT_MOBJECT_TO_MOBJECT_BUFF: float = GLOBAL_CONFIG["sizes"]["default_mobject_to_mobject_buff"]


# Standard vectors
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

FFMPEG_BIN: str = GLOBAL_CONFIG["ffmpeg_bin"]

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

DEFAULT_STROKE_WIDTH: float = GLOBAL_CONFIG["vmobject"]["default_stroke_width"]

# For keyboard interactions
CTRL_SYMBOL: int = 65508
SHIFT_SYMBOL: int = 65505
COMMAND_SYMBOL: int = 65517
DELETE_SYMBOL: int = 65288
ARROW_SYMBOLS: list[int] = list(range(65361, 65365))

# Colors
colors = GLOBAL_CONFIG["colors"]

BLUE_E: ManimColor = colors["blue_e"]
BLUE_D: ManimColor = colors["blue_d"]
BLUE_C: ManimColor = colors["blue_c"]
BLUE_B: ManimColor = colors["blue_b"]
BLUE_A: ManimColor = colors["blue_a"]
TEAL_E: ManimColor = colors["teal_e"]
TEAL_D: ManimColor = colors["teal_d"]
TEAL_C: ManimColor = colors["teal_c"]
TEAL_B: ManimColor = colors["teal_b"]
TEAL_A: ManimColor = colors["teal_a"]
GREEN_E: ManimColor = colors["green_e"]
GREEN_D: ManimColor = colors["green_d"]
GREEN_C: ManimColor = colors["green_c"]
GREEN_B: ManimColor = colors["green_b"]
GREEN_A: ManimColor = colors["green_a"]
YELLOW_E: ManimColor = colors["yellow_e"]
YELLOW_D: ManimColor = colors["yellow_d"]
YELLOW_C: ManimColor = colors["yellow_c"]
YELLOW_B: ManimColor = colors["yellow_b"]
YELLOW_A: ManimColor = colors["yellow_a"]
GOLD_E: ManimColor = colors["gold_e"]
GOLD_D: ManimColor = colors["gold_d"]
GOLD_C: ManimColor = colors["gold_c"]
GOLD_B: ManimColor = colors["gold_b"]
GOLD_A: ManimColor = colors["gold_a"]
RED_E: ManimColor = colors["red_e"]
RED_D: ManimColor = colors["red_d"]
RED_C: ManimColor = colors["red_c"]
RED_B: ManimColor = colors["red_b"]
RED_A: ManimColor = colors["red_a"]
MAROON_E: ManimColor = colors["maroon_e"]
MAROON_D: ManimColor = colors["maroon_d"]
MAROON_C: ManimColor = colors["maroon_c"]
MAROON_B: ManimColor = colors["maroon_b"]
MAROON_A: ManimColor = colors["maroon_a"]
PURPLE_E: ManimColor = colors["purple_e"]
PURPLE_D: ManimColor = colors["purple_d"]
PURPLE_C: ManimColor = colors["purple_c"]
PURPLE_B: ManimColor = colors["purple_b"]
PURPLE_A: ManimColor = colors["purple_a"]
GREY_E: ManimColor = colors["grey_e"]
GREY_D: ManimColor = colors["grey_d"]
GREY_C: ManimColor = colors["grey_c"]
GREY_B: ManimColor = colors["grey_b"]
GREY_A: ManimColor = colors["grey_a"]
WHITE: ManimColor = colors["white"]
BLACK: ManimColor = colors["black"]
GREY_BROWN: ManimColor = colors["grey_brown"]
DARK_BROWN: ManimColor = colors["dark_brown"]
LIGHT_BROWN: ManimColor = colors["light_brown"]
PINK: ManimColor = colors["pink"]
LIGHT_PINK: ManimColor = colors["light_pink"]
GREEN_SCREEN: ManimColor = colors["green_screen"]
ORANGE: ManimColor = colors["orange"]

MANIM_COLORS: List[ManimColor] = list(colors.values())

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
