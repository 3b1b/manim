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


class SampleScene(Scene):
    def construct(self):
        words = text_mobject("Hi There")
        self.paint_into_background(words.shift(UP).highlight(RED_A))
        self.paint_into_background(words.shift(DOWN).highlight(RED_E))





if __name__ == "__main__":
    command_line_create_scene()