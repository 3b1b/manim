import os

PRODUCTION_QUALITY = True
GENERALLY_BUFF_POINTS = PRODUCTION_QUALITY

DEFAULT_POINT_DENSITY_2D = 25  #if PRODUCTION_QUALITY else 20
DEFAULT_POINT_DENSITY_1D = 150 #if PRODUCTION_QUALITY else 50

DEFAULT_HEIGHT = 1440 if PRODUCTION_QUALITY else 480
DEFAULT_WIDTH  = 2560 if PRODUCTION_QUALITY else 640
#All in seconds
DEFAULT_FRAME_DURATION = 0.04 if PRODUCTION_QUALITY else 0.1
DEFAULT_ANIMATION_RUN_TIME = 3.0 
DEFAULT_TRANSFORM_RUN_TIME = 1.0
DEFAULT_DITHER_TIME = 1.0


DEFAULT_NUM_STARS = 1000

SPACE_HEIGHT = 4.0
SPACE_WIDTH = DEFAULT_WIDTH * SPACE_HEIGHT / DEFAULT_HEIGHT

THIS_DIR  = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = os.path.join(THIS_DIR, "images")
GIF_DIR   = os.path.join(THIS_DIR, "gifs")
MOVIE_DIR = os.path.join(THIS_DIR, "movies")
TEX_DIR   = os.path.join(THIS_DIR, "Tex")
TEX_IMAGE_DIR = os.path.join(IMAGE_DIR, "Tex")
TMP_IMAGE_DIR = "/tmp/animation_images/"
for folder in [IMAGE_DIR, GIF_DIR, MOVIE_DIR, TEX_DIR, TMP_IMAGE_DIR, TEX_IMAGE_DIR]:
    if not os.path.exists(folder):
        os.mkdir(folder)

PDF_DENSITY = 800
SIZE_TO_REPLACE = "SizeHere"
TEX_TEXT_TO_REPLACE = "YourTextHere"
TEMPLATE_TEX_FILE  = os.path.join(TEX_DIR, "template.tex")
TEMPLATE_TEXT_FILE = os.path.join(TEX_DIR, "text_template.tex")

LOGO_PATH = os.path.join(IMAGE_DIR, "logo.png")

