#!/usr/bin/env python

import numpy as np
import itertools as it
import operator as op
from copy import deepcopy
from random import random, randint
import sys
import inspect


from animation import *
from mobject import *
from constants import *
from region import *
from scene import Scene
from script_wrapper import command_line_create_scene


class SampleScene(Scene):
    def construct(self):
        mob = Mobject()
        circle9 = Circle().repeat(9).scale(3)
        Mobject.interpolate(Circle().scale(3), circle9, mob, 0.8)
        self.animate(Transform(
            mob, 
            circle9, 
            run_time = 3.0,
            alpha_func = there_and_back,
        ))


if __name__ == "__main__":
    command_line_create_scene(sys.argv[1:])