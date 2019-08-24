from manimlib.imports import *

set_custom_quality(800,20)

OUTPUT_DIRECTORY = "TESTS/UNIQUE_SCENE"

class Test(Scene):
    def construct(self):
        self.add(Dot().scale(4))