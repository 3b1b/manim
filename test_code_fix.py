from manimlib import *


class TestCodeFix(Scene):
    def construct(self):
        c = Code('sorted(iterable, key=None, reverse=False)')
        self.play(FadeIn(c))
        self.wait()
