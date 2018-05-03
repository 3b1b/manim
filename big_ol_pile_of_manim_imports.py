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
as a convenience for scripts creating scenes for videos.
"""

from constants import *

from animation.animation import *
from animation.composition import *
from animation.creation import *
from animation.indication import *
from animation.movement import *
from animation.numbers import *
from animation.rotation import *
from animation.specialized import *
from animation.transform import *
from animation.update import *

from camera.camera import *
from camera.mapping_camera import *
from camera.moving_camera import *
from camera.three_d_camera import *

from continual_animation.continual_animation import *
from continual_animation.from_animation import *
from continual_animation.numbers import *
from continual_animation.update import *

from mobject.frame import *
from mobject.functions import *
from mobject.geometry import *
from mobject.matrix import *
from mobject.mobject import *
from mobject.number_line import *
from mobject.numbers import *
from mobject.probability import *
from mobject.shape_matchers import *
from mobject.svg.brace import *
from mobject.svg.drawings import *
from mobject.svg.svg_mobject import *
from mobject.svg.tex_mobject import *
from mobject.three_dimensions import *
from mobject.types.image_mobject import *
from mobject.types.point_cloud_mobject import *
from mobject.types.vectorized_mobject import *
from mobject.value_tracker import *

from for_3b1b_videos.common_scenes import *
from for_3b1b_videos.pi_creature import *
from for_3b1b_videos.pi_creature_animations import *
from for_3b1b_videos.pi_creature_scene import *

from once_useful_constructs.arithmetic import *
from once_useful_constructs.combinatorics import *
from once_useful_constructs.complex_transformation_scene import *
from once_useful_constructs.counting import *
from once_useful_constructs.fractals import *
from once_useful_constructs.graph_theory import *
from once_useful_constructs.light import *

from scene.graph_scene import *
from scene.moving_camera_scene import *
from scene.reconfigurable_scene import *
from scene.scene import *
from scene.sample_space_scene import *
from scene.graph_scene import *
from scene.scene_from_video import *
from scene.three_d_scene import *
from scene.vector_space_scene import *
from scene.zoomed_scene import *

from utils.bezier import *
from utils.color import *
from utils.config_ops import *
from utils.images import *
from utils.iterables import *
from utils.output_directory_getters import *
from utils.paths import *
from utils.rate_functions import *
from utils.simple_functions import *
from utils.sounds import *
from utils.space_ops import *
from utils.strings import *

# Non manim libraries that are also nice to have without thinking

import inspect
import itertools as it
import numpy as np
import operator as op
import os
import random
import re
import string
import sys

from PIL import Image
from colour import Color
