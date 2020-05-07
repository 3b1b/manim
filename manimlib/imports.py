"""
I won't pretend like this is best practice, by in creating animations for a video,
it can be very nice to simply have all of the Mobjects, Animations, Scenes, etc.
of manim available without having to worry about what namespace they come from.

Rather than having a large pile of "from <module> import *" at the top of every such
script, the intent of this file is to make it so that one can just include
"from manimlib.imports import *".  The effects of adding more modules
or refactoring the library on current or older scene scripts should be entirely
addressible by changing this file.

Note: One should NOT import from this file for main library code, it is meant only
as a convenience for scripts creating scenes for videos.
"""


from manimlib.constants import *

from manimlib.animation.animation import *
from manimlib.animation.composition import *
from manimlib.animation.creation import *
from manimlib.animation.fading import *
from manimlib.animation.growing import *
from manimlib.animation.indication import *
from manimlib.animation.movement import *
from manimlib.animation.numbers import *
from manimlib.animation.rotation import *
from manimlib.animation.specialized import *
from manimlib.animation.transform import *
from manimlib.animation.update import *

from manimlib.camera.camera import *
from manimlib.camera.mapping_camera import *
from manimlib.camera.moving_camera import *
from manimlib.camera.three_d_camera import *

from manimlib.mobject.coordinate_systems import *
from manimlib.mobject.changing import *
from manimlib.mobject.frame import *
from manimlib.mobject.functions import *
from manimlib.mobject.geometry import *
from manimlib.mobject.matrix import *
from manimlib.mobject.mobject import *
from manimlib.mobject.number_line import *
from manimlib.mobject.numbers import *
from manimlib.mobject.probability import *
from manimlib.mobject.shape_matchers import *
from manimlib.mobject.svg.brace import *
from manimlib.mobject.svg.drawings import *
from manimlib.mobject.svg.svg_mobject import *
from manimlib.mobject.svg.tex_mobject import *
from manimlib.mobject.svg.text_mobject import *
from manimlib.mobject.svg.code_mobject import *
from manimlib.mobject.three_d_utils import *
from manimlib.mobject.three_dimensions import *
from manimlib.mobject.types.image_mobject import *
from manimlib.mobject.types.point_cloud_mobject import *
from manimlib.mobject.types.vectorized_mobject import *
from manimlib.mobject.mobject_update_utils import *
from manimlib.mobject.value_tracker import *
from manimlib.mobject.vector_field import *

from manimlib.for_3b1b_videos.common_scenes import *
from manimlib.for_3b1b_videos.pi_creature import *
from manimlib.for_3b1b_videos.pi_creature_animations import *
from manimlib.for_3b1b_videos.pi_creature_scene import *

from manimlib.once_useful_constructs.arithmetic import *
from manimlib.once_useful_constructs.combinatorics import *
from manimlib.once_useful_constructs.complex_transformation_scene import *
from manimlib.once_useful_constructs.counting import *
from manimlib.once_useful_constructs.fractals import *
from manimlib.once_useful_constructs.graph_theory import *
from manimlib.once_useful_constructs.light import *

from manimlib.scene.graph_scene import *
from manimlib.scene.moving_camera_scene import *
from manimlib.scene.reconfigurable_scene import *
from manimlib.scene.scene import *
from manimlib.scene.sample_space_scene import *
from manimlib.scene.graph_scene import *
from manimlib.scene.scene_from_video import *
from manimlib.scene.three_d_scene import *
from manimlib.scene.vector_space_scene import *
from manimlib.scene.zoomed_scene import *

from manimlib.utils.bezier import *
from manimlib.utils.color import *
from manimlib.utils.config_ops import *
from manimlib.utils.debug import *
from manimlib.utils.images import *
from manimlib.utils.iterables import *
from manimlib.utils.file_ops import *
from manimlib.utils.paths import *
from manimlib.utils.rate_functions import *
from manimlib.utils.simple_functions import *
from manimlib.utils.sounds import *
from manimlib.utils.space_ops import *
from manimlib.utils.strings import *

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
import math

from PIL import Image
from colour import Color
