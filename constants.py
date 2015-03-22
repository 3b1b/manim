import os

PRODUCTION_QUALITY = True

DEFAULT_POINT_DENSITY_2D = 25  if PRODUCTION_QUALITY else 20
DEFAULT_POINT_DENSITY_1D = 200 if PRODUCTION_QUALITY else 50

HEIGHT = 1024#1440 if PRODUCTION_QUALITY else 480
WIDTH  = 1024#2560 if PRODUCTION_QUALITY else 640
#All in seconds
DEFAULT_FRAME_DURATION = 0.04 if PRODUCTION_QUALITY else 0.1
DEFAULT_ANIMATION_RUN_TIME = 3.0 
DEFAULT_TRANSFORM_RUN_TIME = 1.0
DEFAULT_DITHER_TIME = 1.0

GENERALLY_BUFF_POINTS = PRODUCTION_QUALITY

BACKGROUND_COLOR = "black" #TODO, this is never actually enforced anywhere.

DEFAULT_NUM_STARS = 1000

SPACE_HEIGHT = 4.0
SPACE_WIDTH = WIDTH * SPACE_HEIGHT / HEIGHT

PDF_DENSITY = 400

IMAGE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
GIF_DIR   = os.path.join(os.getenv("HOME"), "Desktop", "math_gifs")
MOVIE_DIR  = os.path.join(os.getenv("HOME"), "Desktop", "math_movies")
PDF_DIR   = os.path.join(os.getenv("HOME"), "Documents", "Tex", "Animations")
TMP_IMAGE_DIR = "/tmp/animation_images/"
for folder in [IMAGE_DIR, GIF_DIR, MOVIE_DIR, TMP_IMAGE_DIR]:
    if not os.path.exists(folder):
        os.mkdir(folder)

LOGO_PATH = os.path.join(IMAGE_DIR, "logo.png")