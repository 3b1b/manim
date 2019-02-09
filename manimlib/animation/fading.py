from manimlib.animation.animation import Animation
from manimlib.animation.transform import Transform
from manimlib.constants import DOWN
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.bezier import interpolate


class FadeOut(Transform):
    CONFIG = {
        "remover": True,
    }

    def create_target(self):
        return self.mobject.copy().fade(1)

    def clean_up_from_scene(self, scene=None):
        Transform.clean_up_from_scene(self, scene)
        self.interpolate(0)


class FadeIn(Transform):
    def create_target(self):
        return self.mobject

    def create_starting_mobject(self):
        start = super().create_starting_mobject()
        start.fade(1)
        if isinstance(start, VMobject):
            start.set_stroke(width=0)
            start.set_fill(opacity=0)
        return start


class FadeInFrom(Transform):
    CONFIG = {
        "direction": DOWN,
    }

    def __init__(self, mobject, direction=None, **kwargs):
        if direction is not None:
            self.direction = direction
        Transform.__init__(self, mobject, **kwargs)

    def create_target(self):
        return self.mobject.copy()

    def begin(self):
        super().begin()
        self.starting_mobject.shift(self.direction)
        self.starting_mobject.fade(1)


class FadeInFromDown(FadeInFrom):
    """
    Identical to FadeInFrom, just with a name that
    communicates the default
    """
    CONFIG = {
        "direction": DOWN,
    }


class FadeOutAndShift(FadeOut):
    CONFIG = {
        "direction": DOWN,
    }

    def __init__(self, mobject, direction=None, **kwargs):
        if direction is not None:
            self.direction = direction
        FadeOut.__init__(self, mobject, **kwargs)

    def create_target(self):
        target = super().create_target()
        target.shift(self.direction)
        return target


class FadeOutAndShiftDown(FadeOutAndShift):
    """
    Identical to FadeOutAndShift, just with a name that
    communicates the default
    """
    CONFIG = {
        "direction": DOWN,
    }


class FadeInFromLarge(FadeIn):
    CONFIG = {
        "scale_factor": 2,
    }

    def __init__(self, mobject, scale_factor=2, **kwargs):
        if scale_factor is not None:
            self.scale_factor = scale_factor
        FadeIn.__init__(self, mobject, **kwargs)

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

    def update_mobjects(self, dt):
        pass


class VFadeOut(VFadeIn):
    CONFIG = {
        "remover": True
    }

    def interpolate_submobject(self, submob, start, alpha):
        VFadeIn.interpolate_submobject(
            self, submob, start, 1 - alpha
        )
