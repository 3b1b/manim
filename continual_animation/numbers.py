from __future__ import absolute_import

from continual_animation.from_animation import NormalAnimationAsContinualAnimation
from animation.numbers import ChangingDecimal


class ContinualChangingDecimal(NormalAnimationAsContinualAnimation):
    def __init__(self, *args, **kwargs):
        NormalAnimationAsContinualAnimation.__init__(
            self, ChangingDecimal(*args, **kwargs)
        )
