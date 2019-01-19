

from manimlib.constants import *

from manimlib.mobject.mobject import Group

from manimlib.mobject.svg.drawings import SpeechBubble
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.animation.animation import Animation
from manimlib.animation.creation import GrowFromCenter
from manimlib.animation.creation import ShowCreation
from manimlib.animation.creation import Write
from manimlib.animation.composition import AnimationGroup
from manimlib.animation.transform import ApplyMethod
from manimlib.animation.creation import FadeOut
from manimlib.animation.transform import MoveToTarget
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import squish_rate_func
from manimlib.utils.rate_functions import there_and_back

from manimlib.for_tb_videos import omega_creature


class OmegaCreatureClass(VGroup):
    CONFIG = {
        "width" : 3,
        "height" : 2
    }

    def __init__(self, **kwargs):
        VGroup.__init__(self, **kwargs)
        for i in range(self.width):
            for j in range(self.height):
                omega = OmegaCreature().scale(0.3)
                omega.move_to(i*DOWN + j* RIGHT)
                self.add(omega)



class OmegaCreatureDice(AnimationGroup):
    CONFIG = {
        "target_mode": "speaking",
        "bubble_class": SpeechBubble,
        "change_mode_kwargs": {},
        "bubble_creation_class": GrowFromCenter,
        "bubble_creation_kwargs": {},
        "bubble_kwargs": {},
        "content_introduction_class": GrowFromCenter,
        "content_introduction_kwargs": {},
        "look_at_arg": None,
    }

    def __init__(self, omega_creature, *content, **kwargs):
        digest_config(self, kwargs)
        bubble = omega_creature.get_bubble(
            *content,
            bubble_class=self.bubble_class,
            **self.bubble_kwargs
        )
        Group(bubble, bubble.content).shift_onto_screen()

        omega_creature.generate_target()
        omega_creature.target.change_mode(self.target_mode)
        if self.look_at_arg is not None:
            omega_creature.target.look_at(self.look_at_arg)

        change_mode = MoveToTarget(omega_creature, **self.change_mode_kwargs)
        bubble_creation = self.bubble_creation_class(
            bubble, **self.bubble_creation_kwargs
        )
        content_introduction = self.content_introduction_class(
            bubble.content, **self.content_introduction_kwargs
        )
        AnimationGroup.__init__(
            self, change_mode, bubble_creation, content_introduction,
            **kwargs
        )


class OmegaCreatureHabla(OmegaCreatureDice):
    CONFIG = {
        "target_mode": "speaking",
        "bubble_class": SpeechBubble,
    }


class RemueveDialogo(AnimationGroup):
    CONFIG = {
        "target_mode": "plain",
        "look_at_arg": None,
        "remover": True,
    }

    def __init__(self, omega_creature, **kwargs):
        assert hasattr(omega_creature, "bubble")
        digest_config(self, kwargs, locals())

        omega_creature.generate_target()
        omega_creature.target.change_mode(self.target_mode)
        if self.look_at_arg is not None:
            omega_creature.target.look_at(self.look_at_arg)

        AnimationGroup.__init__(
            self,
            MoveToTarget(omega_creature),
            FadeOut(omega_creature.bubble),
            FadeOut(omega_creature.bubble.content),
        )

    def clean_up(self, surrounding_scene=None):
        AnimationGroup.clean_up(self, surrounding_scene)
        self.omega_creature.bubble = None
        if surrounding_scene is not None:
            surrounding_scene.add(self.omega_creature)


class Blink(ApplyMethod):
    CONFIG = {
        "rate_func": squish_rate_func(there_and_back)
    }

    def __init__(self, omega_creature, **kwargs):
        ApplyMethod.__init__(self, omega_creature.blink, **kwargs)












