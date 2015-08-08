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
        start_terms = "a + b = c".split(" ")
        end_terms = "a = c - b + 0".split(" ")
        index_map = {
            0 : 0,
            1 : 3,
            2 : 4,
            3 : 1,
            4 : 2,
        }
        RearrangeEquation.construct(
            self, start_terms, end_terms, index_map
        )



if __name__ == "__main__":
    command_line_create_scene()