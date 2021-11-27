import numpy as np
import math

from manimlib.animation.composition import AnimationGroup
from manimlib.constants import *
from manimlib.animation.fading import FadeIn
from manimlib.animation.growing import GrowFromCenter
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.svg.tex_mobject import SingleStringTex
from manimlib.mobject.svg.tex_mobject import TexText
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.space_ops import get_norm


class Brace(SingleStringTex):
    CONFIG = {
        "buff": 0.2,
        "tex_string": r"\underbrace{\qquad}"
    }

    def __init__(self, mobject, direction=DOWN, **kwargs):
        digest_config(self, kwargs, locals())
        angle = -math.atan2(*direction[:2]) + PI
        mobject.rotate(-angle, about_point=ORIGIN)
        left = mobject.get_corner(DOWN + LEFT)
        right = mobject.get_corner(DOWN + RIGHT)
        target_width = right[0] - left[0]

        super().__init__(self.tex_string, **kwargs)
        self.tip_point_index = np.argmin(self.get_all_points()[:, 1])
        self.set_initial_width(target_width)
        self.shift(left - self.get_corner(UP + LEFT) + self.buff * DOWN)
        for mob in mobject, self:
            mob.rotate(angle, about_point=ORIGIN)

    def set_initial_width(self, width):
        width_diff = width - self.get_width()
        if width_diff > 0:
            for tip, rect, vect in [(self[0], self[1], RIGHT), (self[5], self[4], LEFT)]:
                rect.set_width(
                    width_diff / 2 + rect.get_width(),
                    about_edge=vect, stretch=True
                )
                tip.shift(-width_diff / 2 * vect)
        else:
            self.set_width(width, stretch=True)
        return self

    def put_at_tip(self, mob, use_next_to=True, **kwargs):
        if use_next_to:
            mob.next_to(
                self.get_tip(),
                np.round(self.get_direction()),
                **kwargs
            )
        else:
            mob.move_to(self.get_tip())
            buff = kwargs.get("buff", DEFAULT_MOBJECT_TO_MOBJECT_BUFFER)
            shift_distance = mob.get_width() / 2.0 + buff
            mob.shift(self.get_direction() * shift_distance)
        return self

    def get_text(self, text, **kwargs):
        buff = kwargs.pop("buff", SMALL_BUFF)
        text_mob = Text(text, **kwargs)
        self.put_at_tip(text_mob, buff=buff)
        return text_mob

    def get_tex(self, *tex, **kwargs):
        tex_mob = Tex(*tex)
        self.put_at_tip(tex_mob, **kwargs)
        return tex_mob

    def get_tip(self):
        # Very specific to the LaTeX representation
        # of a brace, but it's the only way I can think
        # of to get the tip regardless of orientation.
        return self.get_all_points()[self.tip_point_index]

    def get_direction(self):
        vect = self.get_tip() - self.get_center()
        return vect / get_norm(vect)


class BraceLabel(VMobject):
    CONFIG = {
        "label_constructor": Tex,
        "label_scale": 1,
    }

    def __init__(self, obj, text, brace_direction=DOWN, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.brace_direction = brace_direction
        if isinstance(obj, list):
            obj = VMobject(*obj)
        self.brace = Brace(obj, brace_direction, **kwargs)

        if isinstance(text, tuple) or isinstance(text, list):
            self.label = self.label_constructor(*text, **kwargs)
        else:
            self.label = self.label_constructor(str(text))
        if self.label_scale != 1:
            self.label.scale(self.label_scale)

        self.brace.put_at_tip(self.label)
        self.set_submobjects([self.brace, self.label])

    def creation_anim(self, label_anim=FadeIn, brace_anim=GrowFromCenter):
        return AnimationGroup(brace_anim(self.brace), label_anim(self.label))

    def shift_brace(self, obj, **kwargs):
        if isinstance(obj, list):
            obj = VMobject(*obj)
        self.brace = Brace(obj, self.brace_direction, **kwargs)
        self.brace.put_at_tip(self.label)
        self.submobjects[0] = self.brace
        return self

    def change_label(self, *text, **kwargs):
        self.label = self.label_constructor(*text, **kwargs)
        if self.label_scale != 1:
            self.label.scale(self.label_scale)

        self.brace.put_at_tip(self.label)
        self.submobjects[1] = self.label
        return self

    def change_brace_label(self, obj, *text):
        self.shift_brace(obj)
        self.change_label(*text)
        return self

    def copy(self):
        copy_mobject = copy.copy(self)
        copy_mobject.brace = self.brace.copy()
        copy_mobject.label = self.label.copy()
        copy_mobject.set_submobjects([copy_mobject.brace, copy_mobject.label])

        return copy_mobject


class BraceText(BraceLabel):
    CONFIG = {
        "label_constructor": TexText
    }
