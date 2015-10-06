#!/usr/bin/env python

import numpy as np
import itertools as it
from copy import deepcopy
import sys


from animation import *
from mobject import *
from constants import *
from region import *
from scene import Scene
from script_wrapper import command_line_create_scene

MOVIE_PREFIX = "matrix_as_transform_2d/"

class TransformScene2D(Scene):
    def construct(self):
        pass

class SampleScene(Scene):
    def construct(self):
        self.add(Grid())
        self.add(Line(LEFT+SPACE_HEIGHT*DOWN, RIGHT+SPACE_HEIGHT*UP))
        self.dither()
        def func((x, y, z)):
            return ((SPACE_HEIGHT+y)*x, y, z)
        self.apply(ApplyPointwiseFunction, func, interpolation_function = clockwise_path)
        self.dither()

if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)