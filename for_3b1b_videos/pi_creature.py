import numpy as np
import warnings

from constants import *

from mobject.mobject import Mobject
from mobject.svg.svg_mobject import SVGMobject
from mobject.svg.tex_mobject import TextMobject
from mobject.types.vectorized_mobject import VGroup
from mobject.types.vectorized_mobject import VMobject

from mobject.svg.drawings import ThoughtBubble

from animation.transform import Transform
from utils.config_ops import digest_config
from utils.rate_functions import squish_rate_func
from utils.rate_functions import there_and_back

PI_CREATURE_DIR = os.path.join(MEDIA_DIR, "designs", "PiCreature")
PI_CREATURE_SCALE_FACTOR = 0.5

LEFT_EYE_INDEX = 0
RIGHT_EYE_INDEX = 1
LEFT_PUPIL_INDEX = 2
RIGHT_PUPIL_INDEX = 3
BODY_INDEX = 4
MOUTH_INDEX = 5


class PiCreature(SVGMobject):
    CONFIG = {
        "color": BLUE_E,
        "file_name_prefix": "PiCreatures",
        "stroke_width": 0,
        "stroke_color": BLACK,
        "fill_opacity": 1.0,
        "propagate_style_to_family": True,
        "height": 3,
        "corner_scale_factor": 0.75,
        "flip_at_start": False,
        "is_looking_direction_purposeful": False,
        "start_corner": None,
        # Range of proportions along body where arms are
        "right_arm_range": [0.55, 0.7],
        "left_arm_range": [.34, .462],
    }

    def __init__(self, mode="plain", **kwargs):
        digest_config(self, kwargs)
        self.parts_named = False
        try:
            svg_file = os.path.join(
                PI_CREATURE_DIR,
                "%s_%s.svg" % (self.file_name_prefix, mode)
            )
            SVGMobject.__init__(self, file_name=svg_file, **kwargs)
        except:
            warnings.warn("No %s design with mode %s" %
                          (self.file_name_prefix, mode))
            svg_file = os.path.join(
                FILE_DIR,
                "PiCreatures_plain.svg",
            )
            SVGMobject.__init__(self, file_name=svg_file, **kwargs)

        if self.flip_at_start:
            self.flip()
        if self.start_corner is not None:
            self.to_corner(self.start_corner)

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
        self.eyes.set_fill(WHITE, opacity=1)
        return self

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
            mode = mode,
        )
        new_self.match_style(self)
        new_self.match_height(self)
        if self.is_flipped() ^ new_self.is_flipped():
            new_self.flip()
        new_self.shift(self.eyes.get_center() - new_self.eyes.get_center())
        if hasattr(self, "purposeful_looking_direction"):
            new_self.look(self.purposeful_looking_direction)
        Transform(self, new_self).update(1)
        return self

    def look(self, direction):
        norm = np.linalg.norm(direction)
        if norm == 0:
            return
        direction /= norm
        self.purposeful_looking_direction = direction
        for pupil, eye in zip(self.pupils.split(), self.eyes.split()):
            pupil_radius = pupil.get_width() / 2.
            eye_radius = eye.get_width() / 2.
            pupil.move_to(eye)
            if direction[1] < 0:
                pupil.shift(pupil_radius * DOWN / 3)
            pupil.shift(direction * (eye_radius - pupil_radius))
            bottom_diff = eye.get_bottom()[1] - pupil.get_bottom()[1]
            if bottom_diff > 0:
                pupil.shift(bottom_diff * UP)
            # TODO, how to handle looking up...
            # top_diff = eye.get_top()[1]-pupil.get_top()[1]
            # if top_diff < 0:
            #     pupil.shift(top_diff*UP)
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

    def get_arm_copies(self):
        body = self.body
        return VGroup(*[
            body.copy().pointwise_become_partial(body, *alpha_range)
            for alpha_range in self.right_arm_range, self.left_arm_range
        ])


def get_all_pi_creature_modes():
    result = []
    prefix = "%s_" % PiCreature.CONFIG["file_name_prefix"]
    suffix = ".svg"
    for file in os.listdir(PI_CREATURE_DIR):
        if file.startswith(prefix) and file.endswith(suffix):
            result.append(
                file[len(prefix):-len(suffix)]
            )
    return result


class Randolph(PiCreature):
    pass  # Nothing more than an alternative name


class Mortimer(PiCreature):
    CONFIG = {
        "color": GREY_BROWN,
        "flip_at_start": True,
    }


class Mathematician(PiCreature):
    CONFIG = {
        "color": GREY,
    }


class BabyPiCreature(PiCreature):
    CONFIG = {
        "scale_factor": 0.5,
        "eye_scale_factor": 1.2,
        "pupil_scale_factor": 1.3
    }

    def __init__(self, *args, **kwargs):
        PiCreature.__init__(self, *args, **kwargs)
        self.scale(self.scale_factor)
        self.shift(LEFT)
        self.to_edge(DOWN, buff=LARGE_BUFF)
        eyes = VGroup(self.eyes, self.pupils)
        eyes_bottom = eyes.get_bottom()
        eyes.scale(self.eye_scale_factor)
        eyes.move_to(eyes_bottom, aligned_edge=DOWN)
        looking_direction = self.get_looking_direction()
        for pupil in self.pupils:
            pupil.scale_in_place(self.pupil_scale_factor)
        self.look(looking_direction)


class TauCreature(PiCreature):
    CONFIG = {
        "file_name_prefix": "TauCreatures"
    }


class ThreeLeggedPiCreature(PiCreature):
    CONFIG = {
        "file_name_prefix": "ThreeLeggedPiCreatures"
    }


class Eyes(VMobject):
    CONFIG = {
        "height": 0.3,
        "thing_looked_at": None,
        "mode": "plain",
    }

    def __init__(self, mobject, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.mobject = mobject
        self.submobjects = self.get_eyes().submobjects

    def get_eyes(self, mode=None, thing_to_look_at=None):
        mode = mode or self.mode
        if thing_to_look_at is None:
            thing_to_look_at = self.thing_looked_at

        pi = Randolph(mode=mode)
        eyes = VGroup(pi.eyes, pi.pupils)
        pi.scale(self.height / eyes.get_height())
        if self.submobjects:
            eyes.move_to(self, DOWN)
        else:
            eyes.move_to(self.mobject.get_top(), DOWN)
        if thing_to_look_at is not None:
            pi.look_at(thing_to_look_at)
        return eyes

    def change_mode_anim(self, mode, **kwargs):
        self.mode = mode
        return Transform(self, self.get_eyes(mode=mode), **kwargs)

    def look_at_anim(self, point_or_mobject, **kwargs):
        self.thing_looked_at = point_or_mobject
        return Transform(
            self, self.get_eyes(thing_to_look_at=point_or_mobject),
            **kwargs
        )

    def blink_anim(self, **kwargs):
        target = self.copy()
        bottom_y = self.get_bottom()[1]
        for submob in target:
            submob.apply_function(
                lambda p: [p[0], bottom_y, p[2]]
            )
        if "rate_func" not in kwargs:
            kwargs["rate_func"] = squish_rate_func(there_and_back)
        return Transform(self, target, **kwargs)
