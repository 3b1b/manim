from manimlib.animation.animation import Animation
from manimlib.animation.transform import Transform
from manimlib.constants import ORIGIN
from manimlib.constants import DOWN
from manimlib.utils.bezier import interpolate
from manimlib.utils.rate_functions import there_and_back


DEFAULT_FADE_LAG_RATIO = 0


class Fade(Transform):
    CONFIG = {
        "lag_ratio": DEFAULT_FADE_LAG_RATIO,
    }

    def __init__(self, mobject, shift=ORIGIN, scale=1, **kwargs):
        self.shift_vect = shift
        self.scale_factor = scale
        super().__init__(mobject, **kwargs)


class FadeIn(Fade):
    CONFIG = {
        "lag_ratio": DEFAULT_FADE_LAG_RATIO,
    }

    def create_target(self):
        return self.mobject

    def create_starting_mobject(self):
        start = super().create_starting_mobject()
        start.set_opacity(0)
        start.scale(1.0 / self.scale_factor)
        start.shift(-self.shift_vect)
        return start


class FadeOut(Fade):
    CONFIG = {
        "remover": True,
        # Put it back in original state when done
        "final_alpha_value": 0,
    }

    def create_target(self):
        result = self.mobject.copy()
        result.set_opacity(0)
        result.shift(self.shift_vect)
        result.scale(self.scale_factor)
        return result


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
        super().__init__(mobject, shift=mobject.get_center() - point, **kwargs)


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
        "remover": True,
        # Put it back in original state when done
        "final_alpha_value": 0,
    }

    def interpolate_submobject(self, submob, start, alpha):
        super().interpolate_submobject(submob, start, 1 - alpha)


class VFadeInThenOut(VFadeIn):
    CONFIG = {
        "rate_func": there_and_back,
        "remover": True,
        # Put it back in original state when done
        "final_alpha_value": 0.5,
    }
