import numpy as np

# Sizes relevant to default camera frame
ASPECT_RATIO = 16.0 / 9.0
FRAME_HEIGHT = 8.0
FRAME_WIDTH = FRAME_HEIGHT * ASPECT_RATIO
FRAME_Y_RADIUS = FRAME_HEIGHT / 2
FRAME_X_RADIUS = FRAME_WIDTH / 2

SMALL_BUFF = 0.1
MED_SMALL_BUFF = 0.25
MED_LARGE_BUFF = 0.5
LARGE_BUFF = 1

DEFAULT_MOBJECT_TO_EDGE_BUFFER = MED_LARGE_BUFF
DEFAULT_MOBJECT_TO_MOBJECT_BUFFER = MED_SMALL_BUFF


# All in seconds
DEFAULT_POINTWISE_FUNCTION_RUN_TIME = 3.0
DEFAULT_WAIT_TIME = 1.0


ORIGIN = np.array((0., 0., 0.))
UP = np.array((0., 1., 0.))
DOWN = np.array((0., -1., 0.))
RIGHT = np.array((1., 0., 0.))
LEFT = np.array((-1., 0., 0.))
IN = np.array((0., 0., -1.))
OUT = np.array((0., 0., 1.))
X_AXIS = np.array((1., 0., 0.))
Y_AXIS = np.array((0., 1., 0.))
Z_AXIS = np.array((0., 0., 1.))

# Useful abbreviations for diagonals
UL = UP + LEFT
UR = UP + RIGHT
DL = DOWN + LEFT
DR = DOWN + RIGHT

TOP = FRAME_Y_RADIUS * UP
BOTTOM = FRAME_Y_RADIUS * DOWN
LEFT_SIDE = FRAME_X_RADIUS * LEFT
RIGHT_SIDE = FRAME_X_RADIUS * RIGHT

PI = np.pi
TAU = 2 * PI
DEGREES = TAU / 360

FFMPEG_BIN = "ffmpeg"

# Related to Text
NOT_SETTING_FONT_MSG = '''
Warning:
You haven't set font.
If you are not using English, this may cause text rendering problem.
You set font like:
text = Text('your text', font='your font')
or:
class MyText(Text):
    CONFIG = {
        'font': 'My Font'
    }
'''
START_X = 30
START_Y = 20
NORMAL = 'NORMAL'
ITALIC = 'ITALIC'
OBLIQUE = 'OBLIQUE'
BOLD = 'BOLD'


LOW_QUALITY_CAMERA_CONFIG = {
    "pixel_height": 480,
    "pixel_width": 854,
    "frame_rate": 15,
}

MEDIUM_QUALITY_CAMERA_CONFIG = {
    "pixel_height": 720,
    "pixel_width": 1280,
    "frame_rate": 30,
}

HIGH_QUALITY_CAMERA_CONFIG = {
    "pixel_height": 1080,
    "pixel_width": 1920,
    "frame_rate": 60,
}

UHD_QUALITY_CAMERA_CONFIG = {
    "pixel_height": 2160,
    "pixel_width": 3840,
    "frame_rate": 60,
}

# TOOD, remove these
DEFAULT_PIXEL_HEIGHT = UHD_QUALITY_CAMERA_CONFIG["pixel_height"]
DEFAULT_PIXEL_WIDTH = UHD_QUALITY_CAMERA_CONFIG["pixel_width"]
DEFAULT_FRAME_RATE = 60

DEFAULT_STROKE_WIDTH = 4


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
    "GREY_A": "#DDDDDD",
    "GREY_B": "#BBBBBB",
    "GREY_C": "#888888",
    "GREY_D": "#444444",
    "GREY_E": "#222222",
    # TODO, remove these greys
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
PALETTE = list(COLOR_MAP.values())
locals().update(COLOR_MAP)
for name in [s for s in list(COLOR_MAP.keys()) if s.endswith("_C")]:
    locals()[name.replace("_C", "")] = locals()[name]
