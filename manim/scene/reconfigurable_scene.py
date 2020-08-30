__all__ = ["ReconfigurableScene"]

from ..animation.transform import Transform
from ..constants import *
from ..mobject.mobject import Mobject
from ..scene.scene import Scene


class ReconfigurableScene(Scene):
    """
    Note, this seems to no longer work as intented.
    """

    CONFIG = {
        "allow_recursion": True,
    }

    def setup(self):
        self.states = []
        self.num_recursions = 0

    def transition_to_alt_config(
        self,
        return_to_original_configuration=True,
        transformation_kwargs=None,
        **new_config,
    ):
        if transformation_kwargs is None:
            transformation_kwargs = {}
        original_state = self.get_state()
        state_copy = original_state.copy()
        self.states.append(state_copy)
        if not self.allow_recursion:
            return
        alt_scene = self.__class__(
            skip_animations=True, allow_recursion=False, **new_config
        )
        alt_state = alt_scene.states[len(self.states) - 1]

        if return_to_original_configuration:
            self.clear()
            self.transition_between_states(
                state_copy, alt_state, **transformation_kwargs
            )
            self.transition_between_states(
                state_copy, original_state, **transformation_kwargs
            )
            self.clear()
            self.add(*original_state)
        else:
            self.transition_between_states(
                original_state, alt_state, **transformation_kwargs
            )
            self.__dict__.update(new_config)

    def get_state(self):
        # Want to return a mobject that maintains the most
        # structure.  The way to do that is to extract only
        # those that aren't inside another.
        return Mobject(*self.get_top_level_mobjects())

    def transition_between_states(self, start_state, target_state, **kwargs):
        self.play(Transform(start_state, target_state, **kwargs))
        self.wait()
