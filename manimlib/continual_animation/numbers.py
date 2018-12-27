from manimlib.animation.numbers import ChangingDecimal
from manimlib.continual_animation.from_animation import NormalAnimationAsContinualAnimation


class ContinualChangingDecimal(NormalAnimationAsContinualAnimation):
    def __init__(self, *args, **kwargs):
        NormalAnimationAsContinualAnimation.__init__(
            self, ChangingDecimal(*args, **kwargs)
        )
