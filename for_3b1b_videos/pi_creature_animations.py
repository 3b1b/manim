from __future__ import absolute_import

from constants import *

from mobject.mobject import Group

from mobject.svg.drawings import SpeechBubble

from animation.creation import ShowCreation
from animation.creation import Write
from animation.composition import AnimationGroup
from animation.transform import ApplyMethod
from animation.creation import FadeOut
from animation.transform import MoveToTarget
from utils.config_ops import digest_config
from utils.rate_functions import squish_rate_func
from utils.rate_functions import there_and_back


class Blink(ApplyMethod):
    CONFIG = {
        "rate_func": squish_rate_func(there_and_back)
    }

    def __init__(self, pi_creature, **kwargs):
        ApplyMethod.__init__(self, pi_creature.blink, **kwargs)


class PiCreatureBubbleIntroduction(AnimationGroup):
    CONFIG = {
        "target_mode": "speaking",
        "bubble_class": SpeechBubble,
        "change_mode_kwargs": {},
        "bubble_creation_class": ShowCreation,
        "bubble_creation_kwargs": {},
        "bubble_kwargs": {},
        "content_introduction_class": Write,
        "content_introduction_kwargs": {},
        "look_at_arg": None,
    }

    def __init__(self, pi_creature, *content, **kwargs):
        digest_config(self, kwargs)
        bubble = pi_creature.get_bubble(
            *content,
            bubble_class=self.bubble_class,
            **self.bubble_kwargs
        )
        Group(bubble, bubble.content).shift_onto_screen()

        pi_creature.generate_target()
        pi_creature.target.change_mode(self.target_mode)
        if self.look_at_arg is not None:
            pi_creature.target.look_at(self.look_at_arg)

        change_mode = MoveToTarget(pi_creature, **self.change_mode_kwargs)
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


class PiCreatureSays(PiCreatureBubbleIntroduction):
    CONFIG = {
        "target_mode": "speaking",
        "bubble_class": SpeechBubble,
    }


class RemovePiCreatureBubble(AnimationGroup):
    CONFIG = {
        "target_mode": "plain",
        "look_at_arg": None,
        "remover": True,
    }

    def __init__(self, pi_creature, **kwargs):
        assert hasattr(pi_creature, "bubble")
        digest_config(self, kwargs, locals())

        pi_creature.generate_target()
        pi_creature.target.change_mode(self.target_mode)
        if self.look_at_arg is not None:
            pi_creature.target.look_at(self.look_at_arg)

        AnimationGroup.__init__(
            self,
            MoveToTarget(pi_creature),
            FadeOut(pi_creature.bubble),
            FadeOut(pi_creature.bubble.content),
        )

    def clean_up(self, surrounding_scene=None):
        AnimationGroup.clean_up(self, surrounding_scene)
        self.pi_creature.bubble = None
        if surrounding_scene is not None:
            surrounding_scene.add(self.pi_creature)
