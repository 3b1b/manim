#!/usr/bin/env python

import numpy as np
import itertools as it
from copy import deepcopy
import sys


from animation import *
from mobject import *
from constants import *
from region import *
from scene import Scene, NumberLineScene
from script_wrapper import command_line_create_scene


class SampleScene(NumberLineScene):
    def construct(self):
        NumberLineScene.construct(self)
        arrow = Arrow(2*RIGHT+UP, 2*RIGHT)
        self.add(arrow)
        self.dither(2)
        self.zoom_in_on(2.4, zoom_factor = 10)
        self.dither(2)

if __name__ == "__main__":
    command_line_create_scene()