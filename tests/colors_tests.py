from manimlib.imports import *

set_custom_quality(1200,10)

OUTPUT_DIRECTORY = "TESTS/COLOR_TESTS"

class ColorScene1(Scene):
    def construct(self):
        rectangle=Rectangle(fill_color=BLACK,stroke_color=BLACK,fill_opacity=1)
        rectangle.scale(2)
        self.add(rectangle)