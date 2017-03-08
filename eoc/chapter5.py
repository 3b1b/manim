from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from scene import Scene
from scene.zoomed_scene import ZoomedScene
from scene.reconfigurable_scene import ReconfigurableScene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from eoc.chapter1 import OpeningQuote, PatreonThanks
from eoc.graph_scene import *

class Chapter3OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            "Using the chain rule is like peeling an onion: ",
            "you have to deal with each layer at a time, and ",
            "if it is too big you will start crying."
        ],
        "author" : "(Anonymous professor)"
    }