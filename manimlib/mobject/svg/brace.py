from __future__ import annotations

import math
import copy

import numpy as np

from manimlib.constants import DEFAULT_MOBJECT_TO_MOBJECT_BUFF, SMALL_BUFF
from manimlib.constants import UP, DOWN, ORIGIN, RIGHT, UL, UR, DR
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


class Brace(Text):
    def __init__(
        self,
        mobject: Mobject,
        direction: Vect3 = DOWN,
        buff: float = 0.2,
        # This depends on font that you choose.
        # Used to align different parts of the brace
        extend_offset: float = .0085,
        **kwargs
    ):
        # \u's are different parts of the brace
        super().__init__("\u23AB\n\u23AA\n\u23AC\n\u23AA\n\u23AD", **kwargs)

        angle = PI / 2 - math.atan2(*direction[:2])
        mobject.rotate(-angle, about_point=ORIGIN)
        up = mobject.get_corner(UR)
        down = mobject.get_corner(DR)
        target_height = up[1] - down[1]

        self.extend_offset = extend_offset
        self.tip_point_index = np.argmax(self.get_all_points()[:, 0])
        self.set_initial_height(target_height)
        self.shift(up - self.get_corner(UL) + buff * RIGHT)
        for mob in mobject, self:
            mob.rotate(angle, about_point=ORIGIN)

    def set_initial_height(self, height: float):
        h0 = sum([self[i].get_height() for i in [0,2,4]])
        extend_height = max(height - h0, 0) / 2
        for extend in self[1::2]:
            extend.set_height(extend_height, True)
            extend.shift(RIGHT * self.extend_offset)
        self.arrange(DOWN, buff=0, coor_mask=UP)
        if extend_height == 0:
          self.set_height(height, True)

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
