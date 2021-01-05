from manimlib.animation.animation import Animation
from manimlib.animation.transform import Transform
from manimlib.mobject.mobject import Group
from manimlib.constants import ORIGIN
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


class FadeInFromPoint(FadeIn):
    def __init__(self, mobject, point, **kwargs):
        super().__init__(mobject, shift=mobject.get_center() - point, **kwargs)


class FadeTransform(Transform):
    CONFIG = {
        "stretch": True,
        "dim_to_match": 1,
    }

    def __init__(self, mobject, target_mobject, **kwargs):
        self.to_add_on_completion = target_mobject
        mobject.save_state()
        super().__init__(
            Group(mobject, target_mobject.copy()),
            **kwargs
        )

    def begin(self):
        self.ending_mobject = self.mobject.copy()
        Animation.begin(self)
        # Both 'start' and 'end' consists of the source and target mobjects.
        # At the start, the traget should be faded replacing the source,
        # and at the end it should be the other way around.
        start, end = self.starting_mobject, self.ending_mobject
        for m0, m1 in ((start[1], start[0]), (end[0], end[1])):
            self.ghost_to(m0, m1)

    def ghost_to(self, source, target):
        source.replace(target, stretch=self.stretch, dim_to_match=self.dim_to_match)
        source.set_opacity(0)

    def get_all_mobjects(self):
        return [
            self.mobject,
            self.starting_mobject,
            self.ending_mobject,
        ]

    def get_all_families_zipped(self):
        return Animation.get_all_families_zipped(self)

    def clean_up_from_scene(self, scene):
        Animation.clean_up_from_scene(self, scene)
        scene.remove(self.mobject)
        self.mobject[0].restore()
        scene.add(self.to_add_on_completion)


class FadeTransformPieces(FadeTransform):
    def begin(self):
        self.mobject[0].align_submobjects(self.mobject[1])
        super().begin()

    def ghost_to(self, source, target):
        for sm0, sm1 in zip(source.get_family(), target.get_family()):
            super().ghost_to(sm0, sm1)


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
