import os
import numpy as np


DEFAULT_HEIGHT = 1440
DEFAULT_WIDTH  = 2560
DEFAULT_FRAME_DURATION = 0.04

PRODUCTION_QUALITY_DISPLAY_CONFIG = {
    "height"         : DEFAULT_HEIGHT,
    "width"          : DEFAULT_WIDTH ,
    "frame_duration" : DEFAULT_FRAME_DURATION,
}

MEDIUM_QUALITY_DISPLAY_CONFIG = {
    "height"         : 720,
    "width"          : 1280,
    "frame_duration" : 0.04,
}

LOW_QUALITY_DISPLAY_CONFIG = {
    "height"         : 480,
    "width"          : 840,
    "frame_duration" : 0.04,
}


DEFAULT_POINT_DENSITY_2D = 25 
DEFAULT_POINT_DENSITY_1D = 200

DEFAULT_POINT_THICKNESS = 6

#TODO, Make sure these are not needed
SPACE_HEIGHT = 4.0
SPACE_WIDTH = SPACE_HEIGHT * DEFAULT_WIDTH / DEFAULT_HEIGHT


DEFAULT_MOBJECT_TO_EDGE_BUFFER = 0.5
DEFAULT_MOBJECT_TO_MOBJECT_BUFFER = 0.2


#All in seconds
DEFAULT_ANIMATION_RUN_TIME = 1.0
DEFAULT_POINTWISE_FUNCTION_RUN_TIME = 3.0
DEFAULT_DITHER_TIME = 1.0


ORIGIN = np.array(( 0, 0, 0))
UP     = np.array(( 0, 1, 0))
DOWN   = np.array(( 0,-1, 0))
RIGHT  = np.array(( 1, 0, 0))
LEFT   = np.array((-1, 0, 0))
IN     = np.array(( 0, 0,-1))
OUT    = np.array(( 0, 0, 1))

TOP        = SPACE_HEIGHT*UP
BOTTOM     = SPACE_HEIGHT*DOWN
LEFT_SIDE  = SPACE_WIDTH*LEFT
RIGHT_SIDE = SPACE_WIDTH*RIGHT

THIS_DIR          = os.path.dirname(os.path.realpath(__file__))
FILE_DIR          = os.path.join(THIS_DIR, os.pardir, "animation_files")
IMAGE_DIR         = os.path.join(FILE_DIR, "images")
GIF_DIR           = os.path.join(FILE_DIR, "gifs")
MOVIE_DIR         = os.path.join(FILE_DIR, "movies")
TEX_DIR           = os.path.join(FILE_DIR, "Tex")
TEX_IMAGE_DIR     = os.path.join(IMAGE_DIR, "Tex")
MOBJECT_DIR       = os.path.join(FILE_DIR, "mobjects")
IMAGE_MOBJECT_DIR = os.path.join(MOBJECT_DIR, "image")

for folder in [IMAGE_DIR, GIF_DIR, MOVIE_DIR, TEX_DIR, 
               TEX_IMAGE_DIR, MOBJECT_DIR, IMAGE_MOBJECT_DIR]:
    if not os.path.exists(folder):
        os.mkdir(folder)

PDF_DENSITY = 800
SIZE_TO_REPLACE = "SizeHere"
TEX_TEXT_TO_REPLACE = "YourTextHere"
TEMPLATE_TEX_FILE  = os.path.join(THIS_DIR, "template.tex")
TEMPLATE_TEXT_FILE = os.path.join(THIS_DIR, "text_template.tex")
MAX_LEN_FOR_HUGE_TEX_FONT = 25

LOGO_PATH = os.path.join(IMAGE_DIR, "logo.png")


### Colors ###


COLOR_MAP = {
    "DARK_BLUE"   : "#236B8E",
    "DARK_BROWN"  : "#8B4513",
    "LIGHT_BROWN" : "#CD853F",
    "BLUE_E"      : "#1C758A",
    "BLUE_D"      : "#29ABCA",
    "BLUE_C"      : "#58C4DD",
    "BLUE_B"      : "#9CDCEB",
    "BLUE_A"      : "#C7E9F1",
    "TEAL_E"      : "#49A88F",
    "TEAL_D"      : "#55C1A7",
    "TEAL_C"      : "#5CD0B3",
    "TEAL_B"      : "#76DDC0",
    "TEAL_A"      : "#ACEAD7",
    "GREEN_E"     : "#699C52",
    "GREEN_D"     : "#77B05D",
    "GREEN_C"     : "#83C167",
    "GREEN_B"     : "#A6CF8C",
    "GREEN_A"     : "#C9E2AE",
    "YELLOW_E"    : "#E8C11C",
    "YELLOW_D"    : "#F4D345",
    "YELLOW_C"    : "#FCE15B",
    "YELLOW_B"    : "#FFEA94",
    "YELLOW_A"    : "#FFF1B6",
    "GOLD_E"      : "#C78D46",
    "GOLD_D"      : "#E1A158",
    "GOLD_C"      : "#F0AC5F",
    "GOLD_B"      : "#F9B775",
    "GOLD_A"      : "#F7C797",
    "RED_E"       : "#CF5044",
    "RED_D"       : "#E65A4C",
    "RED_C"       : "#FC6255",
    "RED_B"       : "#FF8080",
    "RED_A"       : "#F7A1A3",
    "MAROON_E"    : "#94424F",
    "MAROON_D"    : "#A24D61",
    "MAROON_C"    : "#C55F73",
    "MAROON_B"    : "#EC92AB",
    "MAROON_A"    : "#ECABC1",
    "PURPLE_E"    : "#644172",
    "PURPLE_D"    : "#715582",
    "PURPLE_C"    : "#9A72AC",
    "PURPLE_B"    : "#B189C6",
    "PURPLE_A"    : "#CAA3E8",
    "WHITE"       : "#FFFFFF",
    "BLACK"       : "#000000",
}
PALETTE = COLOR_MAP.values()
globals().update(COLOR_MAP)
for name in filter(lambda s : s.endswith("_C"), COLOR_MAP.keys()):
    globals()[name.replace("_C", "")] = globals()[name]










