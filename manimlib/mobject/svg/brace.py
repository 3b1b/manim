from __future__ import annotations

import math
import copy

import numpy as np

from manimlib.constants import DEFAULT_MOBJECT_TO_MOBJECT_BUFF, SMALL_BUFF
from manimlib.constants import DOWN, LEFT, ORIGIN, RIGHT, DL, DR, UL
from manimlib.constants import PI
from manimlib.animation.composition import AnimationGroup
from manimlib.animation.fading import FadeIn
from manimlib.animation.growing import GrowFromCenter
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.svg.tex_mobject import TexText
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.iterables import listify
from manimlib.utils.space_ops import get_norm

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable

    from manimlib.animation.animation import Animation
    from manimlib.mobject.mobject import Mobject
    from manimlib.typing import Vect3


class Brace(Tex):
    def __init__(
        self,
        mobject: Mobject,
        direction: Vect3 = DOWN,
        buff: float = 0.2,
        tex_string: str = R"\underbrace{\qquad}",
        **kwargs
    ):
        super().__init__(tex_string, **kwargs)

        angle = -math.atan2(*direction[:2]) + PI
        mobject.rotate(-angle, about_point=ORIGIN)
        left = mobject.get_corner(DL)
        right = mobject.get_corner(DR)
        target_width = right[0] - left[0]

        self.tip_point_index = np.argmin(self.get_all_points()[:, 1])
        self.set_initial_width(target_width)
        self.shift(left - self.get_corner(UL) + buff * DOWN)
        for mob in mobject, self:
            mob.rotate(angle, about_point=ORIGIN)

    def set_initial_width(self, width: float):
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

    def put_at_tip(
        self,
        mob: Mobject,
        use_next_to: bool = True,
        **kwargs
    ):
        if use_next_to:
            mob.next_to(
                self.get_tip(),
                np.round(self.get_direction()),
                **kwargs
            )
        else:
            mob.move_to(self.get_tip())
            buff = kwargs.get("buff", DEFAULT_MOBJECT_TO_MOBJECT_BUFF)
            shift_distance = mob.get_width() / 2.0 + buff
            mob.shift(self.get_direction() * shift_distance)
        return self

    def get_text(self, text: str, **kwargs) -> Text:
        buff = kwargs.pop("buff", SMALL_BUFF)
        text_mob = Text(text, **kwargs)
        self.put_at_tip(text_mob, buff=buff)
        return text_mob

    def get_tex(self, *tex: str, **kwargs) -> Tex:
        buff = kwargs.pop("buff", SMALL_BUFF)
        tex_mob = Tex(*tex, **kwargs)
        self.put_at_tip(tex_mob, buff=buff)
        return tex_mob

    def get_tip(self) -> np.ndarray:
        # Very specific to the LaTeX representation
        # of a brace, but it's the only way I can think
        # of to get the tip regardless of orientation.
        return self.get_all_points()[self.tip_point_index]

    def get_direction(self) -> np.ndarray:
        vect = self.get_tip() - self.get_center()
        return vect / get_norm(vect)


class BraceLabel(VMobject):
    label_constructor: type = Tex

    def __init__(
        self,
        obj: VMobject | list[VMobject],
        text: str | Iterable[str],
        brace_direction: np.ndarray = DOWN,
        label_scale: float = 1.0,
        label_buff: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFF,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.brace_direction = brace_direction
        self.label_scale = label_scale
        self.label_buff = label_buff

        if isinstance(obj, list):
            obj = VGroup(*obj)
        self.brace = Brace(obj, brace_direction, **kwargs)

        self.label = self.label_constructor(*listify(text), **kwargs)
        self.label.scale(self.label_scale)

        self.brace.put_at_tip(self.label, buff=self.label_buff)
        self.set_submobjects([self.brace, self.label])

    def creation_anim(
        self,
        label_anim: Animation = FadeIn,
        brace_anim: Animation = GrowFromCenter
    ) -> AnimationGroup:
        return AnimationGroup(brace_anim(self.brace), label_anim(self.label))

    def shift_brace(self, obj: VMobject | list[VMobject], **kwargs):
        if isinstance(obj, list):
            obj = VMobject(*obj)
        self.brace = Brace(obj, self.brace_direction, **kwargs)
        self.brace.put_at_tip(self.label)
        self.submobjects[0] = self.brace
        return self

    def change_label(self, *text: str, **kwargs):
        self.label = self.label_constructor(*text, **kwargs)
        if self.label_scale != 1:
            self.label.scale(self.label_scale)

        self.brace.put_at_tip(self.label)
        self.submobjects[1] = self.label
        return self

    def change_brace_label(self, obj: VMobject | list[VMobject], *text: str):
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
    label_constructor: type = TexText
