#!/usr/bin/env python

import numpy as np
import itertools as it
from copy import deepcopy
import sys


from animation import *
from mobject import *
from constants import *
from region import *
from scene import Scene, GraphScene
from script_wrapper import command_line_create_scene


class SampleScene(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        self.generate_regions()
        self.generate_dual_graph()
        self.generate_spanning_tree()
        self.add(self.spanning_tree)
        for count in range(len(self.regions)):
            self.add(tex_mobject(str(count)).shift(self.dual_points[count]))
        for count in range(len(self.edges)):
            self.add(tex_mobject(str(count)).shift(self.edges[count].get_center()))




if __name__ == "__main__":
    command_line_create_scene()