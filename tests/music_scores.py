from manimlib.imports import *

class ScoreTest(CheckScore):
    CONFIG = {
        "file":"test_music1",
    }
    def show_blocks(self):
        self.imagen[24:76].set_color(HSL(120/360))
        self.imagen[88:].set_color(HSL(60/360))
