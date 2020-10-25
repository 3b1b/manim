from manim import *
from tests.helpers.graphical_units import set_test_scene

# Note: DO NOT COMMIT THIS FILE. The purpose of this template is to produce control data for graphical_units_data. As
# soon as the test data is produced, please revert all changes you made to this file, so this template file will be
# still available for others :)
# More about graphical unit tests: https://github.com/ManimCommunity/manim/wiki/Testing#graphical-unit-test


class YourClassHere(Scene):
    def construct(self):
        circle = Circle()
        self.play(Animation(circle))


set_test_scene(
    YourClassHere, "<module_name>"
)  # <module_name> can be e.g.  "geometry" or "movements"
