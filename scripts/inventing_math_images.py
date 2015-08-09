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


class BuildFromTheStart(Scene):
    def construct(self):
        self.add(text_mobject("Build from the start..."))

