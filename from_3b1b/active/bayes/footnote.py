from manimlib.imports import *
from from_3b1b.active.bayes.part1 import BayesDiagram

OUTPUT_DIRECTORY = "bayes/footnote"


class Test(Scene):
    def construct(self):
        diagram = BayesDiagram(0.4, 0.5, 0.2)
        self.add(diagram)
