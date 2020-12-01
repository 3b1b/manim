#!/usr/bin/env python

# Importing the config module should be the first thing we do, since other
# modules depend on the global config dict for initialization.
from ._config import *

from .constants import *

from .container import *

from .animation.animation import *
from .animation.composition import *
from .animation.creation import *
from .animation.fading import *
from .animation.growing import *
from .animation.indication import *
from .animation.movement import *
from .animation.numbers import *
from .animation.rotation import *
from .animation.transform import *
from .animation.update import *

from .renderer.cairo_renderer import *

from .camera.camera import *
from .camera.mapping_camera import *
from .camera.moving_camera import *
from .camera.three_d_camera import *
from .camera.multi_camera import *

from .mobject.coordinate_systems import *
from .mobject.changing import *
from .mobject.frame import *
from .mobject.functions import *
from .mobject.geometry import *
from .mobject.logo import *
from .mobject.matrix import *
from .mobject.mobject import *
from .mobject.number_line import *
from .mobject.numbers import *
from .mobject.probability import *
from .mobject.shape_matchers import *
from .mobject.svg.brace import *
from .mobject.svg.svg_mobject import *
from .mobject.svg.tex_mobject import *
from .mobject.svg.text_mobject import *
from .mobject.svg.code_mobject import *
from .mobject.three_d_utils import *
from .mobject.three_dimensions import *
from .mobject.types.image_mobject import *
from .mobject.types.point_cloud_mobject import *
from .mobject.types.vectorized_mobject import *
from .mobject.mobject_update_utils import *
from .mobject.value_tracker import *
from .mobject.vector_field import *

from .scene.graph_scene import *
from .scene.moving_camera_scene import *
from .scene.reconfigurable_scene import *

try:
    from .scene.js_scene import *
except ModuleNotFoundError:
    pass  # optional deps
from .scene.scene import *
from .scene.sample_space_scene import *
from .scene.three_d_scene import *
from .scene.vector_space_scene import *
from .scene.zoomed_scene import *
from .scene.scene_file_writer import *

from .utils.bezier import *
from .utils.color import *
from .utils import color as color
from .utils.config_ops import *
from .utils.debug import *
from .utils.images import *
from .utils.iterables import *
from .utils.file_ops import *
from .utils.paths import *
from .utils.rate_functions import *
from .utils import rate_functions
from .utils.simple_functions import *
from .utils.sounds import *
from .utils.space_ops import *
from .utils.strings import *
from .utils.tex import *
from .utils.tex_templates import *
