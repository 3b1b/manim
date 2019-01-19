import numpy as np
import warnings

from manimlib.constants import *

from manimlib.mobject.mobject import Mobject
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.mobject.svg.tex_mobject import TextMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject

from manimlib.mobject.svg.drawings import ThoughtBubble

from manimlib.animation.transform import Transform
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import squish_rate_func
from manimlib.utils.rate_functions import there_and_back
from manimlib.utils.space_ops import get_norm

OMEGA_CREATURE_DIR = os.path.join(MEDIA_DIR, "designs","OmegaCreature")
OMEGA_CREATURE_SCALE_FACTOR = 0.5

LEFT_EYE_INDEX = 0
RIGHT_EYE_INDEX = 1
LEFT_PUPIL_INDEX = 2
RIGHT_PUPIL_INDEX = 3
BODY_INDEX = 4
MOUTH_INDEX = 5


class OmegaCreature(SVGMobject):
    CONFIG = {
        "color": RED,
        "file_name_prefix": "OmegaCreature",
        "stroke_width": 0,
        "stroke_color": BLACK,
        "fill_opacity": 1.0,
        "propagate_style_to_family": True,
        "height": 3,
        "corner_scale_factor": 0.75,
        "flip_at_start": False,
        "is_looking_direction_purposeful": False,
        "start_corner": None,
    }

    def __init__(self, mode="plain", **kwargs):
        digest_config(self, kwargs)
        self.mode = mode
        self.parts_named = False
        try:
            svg_file = os.path.join(
                OMEGA_CREATURE_DIR,
                "%s_%s.svg" % (self.file_name_prefix, mode)
            )
            SVGMobject.__init__(self, file_name=svg_file, **kwargs)
        except:
            warnings.warn("No %s design with mode %s" %
                          (self.file_name_prefix, mode))
            svg_file = os.path.join(
                FILE_DIR,
                "OmegaCreature_plain.svg",
            )
            SVGMobject.__init__(self, file_name=svg_file, **kwargs)

        if self.flip_at_start:
            self.flip()
        if self.start_corner is not None:
            self.to_corner(self.start_corner)

    def align_data(self, mobject):
        # This ensures that after a transform into a different mode,
        # the pi creatures mode will be updated appropriately
        SVGMobject.align_data(self, mobject)
        if isinstance(mobject, OmegaCreature):
            self.mode = mobject.get_mode()

    def name_parts(self):
        self.mouth = self.submobjects[MOUTH_INDEX]
        self.body = self.submobjects[BODY_INDEX]
        self.pupils = VGroup(*[
            self.submobjects[LEFT_PUPIL_INDEX],
            self.submobjects[RIGHT_PUPIL_INDEX]
        ])
        self.eyes = VGroup(*[
            self.submobjects[LEFT_EYE_INDEX],
            self.submobjects[RIGHT_EYE_INDEX]
        ])
        self.eye_parts = VGroup(self.eyes, self.pupils)
        self.parts_named = True

    def init_colors(self):
        SVGMobject.init_colors(self)
        if not self.parts_named:
            self.name_parts()
        self.mouth.set_fill(BLACK, opacity=1)
        self.body.set_fill(self.color, opacity=1)
        self.pupils.set_fill(BLACK, opacity=1)
        # self.pupils.set_stroke(DARK_GREY, width=1)
        self.add_pupil_light_spot(self.pupils)
        self.eyes.set_fill(WHITE, opacity=1)
        return self

    def add_pupil_light_spot(self, pupils):
        # Purely an artifact of how the SVGs were drawn.
        # In a perfect world, this wouldn't be needed
        for pupil in pupils:
            index = 16
            sub_points = pupil.points[:index]
            pupil.points = pupil.points[index + 2:]
            circle = VMobject()
            circle.points = sub_points
            circle.set_stroke(width=0)
            circle.set_fill(WHITE, 1)
            pupil.add(circle)

    def copy(self):
        copy_mobject = SVGMobject.copy(self)
        copy_mobject.name_parts()
        return copy_mobject

    def set_color(self, color):
        self.body.set_fill(color)
        self.color = color
        return self

    def change_mode(self, mode):
        new_self = self.__class__(
            mode=mode,
        )
        new_self.match_style(self)
        new_self.match_height(self)
        if self.is_flipped() != new_self.is_flipped():
            new_self.flip()
        new_self.shift(self.eyes.get_center() - new_self.eyes.get_center())
        if hasattr(self, "purposeful_looking_direction"):
            new_self.look(self.purposeful_looking_direction)
        Transform(self, new_self).update(1)
        self.mode = mode
        return self

    def get_mode(self):
        return self.mode

    def look(self, direction):
        norm = get_norm(direction)
        if norm == 0:
            return
        direction /= norm
        self.purposeful_looking_direction = direction
        for pupil, eye in zip(self.pupils.split(), self.eyes.split()):
            c = eye.get_center()
            right = eye.get_right() - c
            up = eye.get_top() - c
            vect = direction[0] * right + direction[1] * up
            v_norm = get_norm(vect)
            p_radius = 0.5 * pupil.get_width()
            vect *= (v_norm - 0.75 * p_radius) / v_norm
            pupil.move_to(c + vect)
        self.pupils[1].align_to(self.pupils[0], DOWN)
        return self

    def look_at(self, point_or_mobject):
        if isinstance(point_or_mobject, Mobject):
            point = point_or_mobject.get_center()
        else:
            point = point_or_mobject
        self.look(point - self.eyes.get_center())
        return self

    def change(self, new_mode, look_at_arg=None):
        self.change_mode(new_mode)
        if look_at_arg is not None:
            self.look_at(look_at_arg)
        return self

    def get_looking_direction(self):
        return np.sign(np.round(
            self.pupils.get_center() - self.eyes.get_center(),
            decimals=2
        ))

    def is_flipped(self):
        return self.eyes.submobjects[0].get_center()[0] > \
            self.eyes.submobjects[1].get_center()[0]

    def blink(self):
        eye_parts = self.eye_parts
        eye_bottom_y = eye_parts.get_bottom()[1]
        eye_parts.apply_function(
            lambda p: [p[0], eye_bottom_y, p[2]]
        )
        return self

    def to_corner(self, vect=None, **kwargs):
        if vect is not None:
            SVGMobject.to_corner(self, vect, **kwargs)
        else:
            self.scale(self.corner_scale_factor)
            self.to_corner(DOWN + LEFT, **kwargs)
        return self

    def get_bubble(self, *content, **kwargs):
        bubble_class = kwargs.get("bubble_class", ThoughtBubble)
        bubble = bubble_class(**kwargs)
        if len(content) > 0:
            if isinstance(content[0], str):
                content_mob = TextMobject(*content)
            else:
                content_mob = content[0]
            bubble.add_content(content_mob)
            if "height" not in kwargs and "width" not in kwargs:
                bubble.resize_to_content()
        bubble.pin_to(self)
        self.bubble = bubble
        return bubble

    def make_eye_contact(self, pi_creature):
        self.look_at(pi_creature.eyes)
        pi_creature.look_at(self.eyes)
        return self

    def shrug(self):
        self.change_mode("shruggie")
        top_mouth_point, bottom_mouth_point = [
            self.mouth.points[np.argmax(self.mouth.points[:, 1])],
            self.mouth.points[np.argmin(self.mouth.points[:, 1])]
        ]
        self.look(top_mouth_point - bottom_mouth_point)
        return self



def get_all_pi_creature_modes():
    result = []
    prefix = "%s_" % OmegaCreature.CONFIG["file_name_prefix"]
    suffix = ".svg"
    for file in os.listdir(OMEGA_CREATURE_DIR):
        if file.startswith(prefix) and file.endswith(suffix):
            result.append(
                file[len(prefix):-len(suffix)]
            )
    return result


class Alex(OmegaCreature):
    pass  # Nothing more than an alternative name

