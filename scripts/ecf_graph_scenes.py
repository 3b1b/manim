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
from moser_main import EulersFormula
from script_wrapper import command_line_create_scene

MOVIE_PREFIX = "ecf_graph_scenes/"

class IntroduceGraphs(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        self.draw_vertices()        
        self.draw_edges()
        self.dither()
        self.clear()
        self.add(*self.edges)
        self.replace_vertices_with(SimpleFace().scale(0.4))
        friends = text_mobject("Friends").scale(0.5)
        self.annotate_edges(friends.shift((0, friends.get_height()/2, 0)))
        self.animate(*[
            SemiCircleTransform(vertex, Dot(point))
            for vertex, point in zip(self.vertices, self.points)
        ]+[
            Transform(ann, line)
            for ann, line in zip(
                self.edge_annotations, 
                self.edges
            )
        ])
        self.dither()

class PlanarGraphDefinition(Scene):
    def construct(self):
        


if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)