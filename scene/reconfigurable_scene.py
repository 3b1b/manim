import numpy as np

from scene import Scene
from animation.transform import Transform

from helpers import *

class ReconfigurableScene(Scene):
    CONFIG = {
        "allow_recursion" : True,
    }
    def setup(self):
        self.states = []
        self.num_recursions = 0

    def show_alt_config(self, return_to_original_configuration = True, **new_config):
        original_state = self.get_mobjects()
        state_copy = [m.copy() for m in original_state]
        self.states.append(state_copy)
        if not self.allow_recursion:
            return
        alt_scene = self.__class__(
            skip_animations = True, 
            allow_recursion = False,
            **new_config
        )
        alt_state = alt_scene.states[len(self.states)-1]

        if return_to_original_configuration:
            self.clear()
            self.transition_between_states(state_copy, alt_state)
            self.transition_between_states(state_copy, original_state)
            self.clear()
            self.add(*original_state)
        else:
            self.transition_between_states(original_state, alt_state)
            self.__dict__.update(new_config)

    def transition_between_states(self, start_state, target_state):
            self.play(*[
                Transform(*pair)
                for pair in zip(start_state, target_state)
            ])
            self.dither()



