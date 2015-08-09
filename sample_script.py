#!/usr/bin/env python

import numpy as np
import itertools as it
from copy import deepcopy
import sys


from animation import *
from mobject import *
from constants import *
from region import *
from scene import Scene, RearrangeEquation
from script_wrapper import command_line_create_scene


class SampleScene(RearrangeEquation):
    def construct(self):
        dot = Dot().shift(UP)
        self.add(dot)
        self.dither()
        self.animate(DelayByOrder(Transform(
            dot,
            Line(DOWN, UP)
        )))
        self.dither()




if __name__ == "__main__":
    command_line_create_scene()