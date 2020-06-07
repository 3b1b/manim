from manimlib.animation.animation import Animation
from manimlib.animation.animation import DEFAULT_ANIMATION_LAG_RATIO
from manimlib.animation.transform import Transform
from manimlib.constants import ORIGIN
from manimlib.constants import DOWN
from manimlib.utils.bezier import interpolate
from manimlib.utils.rate_functions import there_and_back


DEFAULT_FADE_LAG_RATIO = 0


class FadeOut(Transform):
    CONFIG = {
        "remover": True,
        "lag_ratio": DEFAULT_FADE_LAG_RATIO,
    }

    def __init__(self, mobject, to_vect=ORIGIN, **kwargs):
        self.to_vect = to_vect
        super().__init__(mobject, **kwargs)

    def create_target(self):
        result = self.mobject.copy()
        result.set_opacity(0)
        result.shift(self.to_vect)
        return result

    def clean_up_from_scene(self, scene=None):
        super().clean_up_from_scene(scene)
        self.interpolate(0)


class FadeIn(Transform):
    CONFIG = {
        "lag_ratio": DEFAULT_FADE_LAG_RATIO,
    }

    def __init__(self, mobject, from_vect=ORIGIN, **kwargs):
        self.from_vect = from_vect
        super().__init__(mobject, **kwargs)

    def create_target(self):
        return self.mobject

    def create_starting_mobject(self):
        start = super().create_starting_mobject()
        start.set_opacity(0)
        start.shift(self.from_vect)
        return start


# Below will be deprecated


class FadeInFromDown(FadeIn):
    """
    Identical to FadeIn, just with a name that
    communicates the default
    """

    def __init__(self, mobject, **kwargs):
        super().__init__(mobject, DOWN, **kwargs)


class FadeOutAndShiftDown(FadeOut):
    """
    Identical to FadeOut, just with a name that
    communicates the default
    """

    def __init__(self, mobject, **kwargs):
        super().__init__(mobject, DOWN, **kwargs)


class FadeInFromPoint(FadeIn):
    def __init__(self, mobject, point, **kwargs):
        super().__init__(mobject, point - mobject.get_center(), **kwargs)


class FadeInFromLarge(FadeIn):
    CONFIG = {
        "scale_factor": 2,
    }

    def __init__(self, mobject, scale_factor=2, **kwargs):
        if scale_factor is not None:
            self.scale_factor = scale_factor
        super().__init__(mobject, **kwargs)

    def create_starting_mobject(self):
        start = super().create_starting_mobject()
        start.scale(self.scale_factor)
        return start


class VFadeIn(Animation):
    """
    VFadeIn and VFadeOut only work for VMobjects,
    """
    CONFIG = {
        "suspend_mobject_updating": False,
    }

    def interpolate_submobject(self, submob, start, alpha):
        submob.set_stroke(
            opacity=interpolate(0, start.get_stroke_opacity(), alpha)
        )
        submob.set_fill(
            opacity=interpolate(0, start.get_fill_opacity(), alpha)
        )


class VFadeOut(VFadeIn):
    CONFIG = {
        "remover": True
    }

    def interpolate_submobject(self, submob, start, alpha):
        super().interpolate_submobject(submob, start, 1 - alpha)


class VFadeInThenOut(VFadeIn):
    CONFIG = {
        "rate_func": there_and_back,
        "remover": True,
    }
