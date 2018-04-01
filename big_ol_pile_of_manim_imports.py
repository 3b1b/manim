"""
I won't pretend like this is best practice, by in creating animations for a video,
it can be very nice to simply have all of the Mobjects, Animations, Scenes, etc. 
of manim available without having to worry about what namespace they come from.

Rather than having a large pile of "from <module> import *" at the top of every such
script, the intent of this file is to make it so that one can just include 
"from big_ol_pile_of_manim_imports import *".  The effects of adding more modules
or refactoring the library on current or older scene scripts should be entirely 
addressible by changing this file.

Note: One should NOT import from this file for main library code, it is meant only
as a convenience for scripts createing scenes for videos
"""
from __future__ import absolute_import

from .constants import *

from .animation.animation import *
from .animation.compositions import *
from .animation.continual_animation import *
from .animation.playground import *
from .animation.simple_animations import *
from .animation.transform import *

from .camera.camera import *

from .mobject.image_mobject import *
from .mobject.mobject import *
from .mobject.point_cloud_mobject import *
from .mobject.svg_mobject import *
from .mobject.tex_mobject import *
from .mobject.vectorized_mobject import *

from .scene.moving_camera_scene import *
from .scene.reconfigurable_scene import *
from .scene.scene import *
from .scene.scene_from_video import *
from .scene.tk_scene import *
from .scene.zoomed_scene import *

from .topics.arithmetic import *
from .topics.characters import *
from .topics.combinatorics import *
from .topics.common_scenes import *
from .topics.complex_numbers import *
from .topics.counting import *
from .topics.fractals import *
from .topics.functions import *
from .topics.geometry import *
from .topics.graph_scene import *
from .topics.graph_theory import *
from .topics.light import *
from .topics.matrix import *
from .topics.number_line import *
from .topics.numerals import *
from .topics.objects import *
from .topics.probability import *
from .topics.three_dimensions import *
from .topics.vector_space_scene import *

from .utils.bezier import *
from .utils.color import *
from .utils.config_ops import *
from .utils.images import *
from .utils.iterables import *
from .utils.paths import *
from .utils.rate_functions import *
from .utils.simple_functions import *
from .utils.sounds import *
from .utils.space_ops import *
from .utils.strings import *

from special_animations import *

# Non manim libraries that are also nice to have without thinking

import numpy as np
import itertools as it
import operator as op
import random
import inspect
import string
import re
import os
from PIL import Image
from colour import Color

