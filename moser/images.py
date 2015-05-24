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
from image_mobject import *
from constants import *
from region import *
from scene import Scene
from script_wrapper import command_line_create_scene

from moser_helpers import *
from graphs import *

if __name__ == "__main__":
    prefix = "moser_images/"
    # cs_outer = CircleScene(RADIANS[:6])
    # cs_outer.highlight_region(
    #     Region(lambda x, y : x**2 + y**2 > RADIUS**2)
    # )

    # cs_graph = CircleScene(RADIANS)
    # cs_graph.generate_intersection_dots()
    # cs_graph.add(*cs_graph.intersection_dots)
    # cs_graph.chop_lines_at_intersection_points()
    # cs_graph.chop_circle_at_points()
    # for line in cs_graph.lines:
    #     line.scale_in_place(0.5)
    # for piece in cs_graph.smaller_circle_pieces:
    #     piece.highlight("yellow")
    # cs_graph.remove(*cs_graph.circle_pieces)
    # cs_graph.add(*cs_graph.smaller_circle_pieces)
    
    savable_things = [
        # (Mobject(), "Blackness")
        # (tex_mobject(r"V-E+F=2"), "EulersFormula"),
        # (PascalsTriangleScene(N_PASCAL_ROWS), "PascalsTriangle"),
        # (tex_mobject(r"1, 2, 4, 8, 16, 31, \dots"), "FalsePattern"),
        # (
        #     tex_mobject(r"""
        #         \underbrace{1, 2, 4, 16, 31, 57, 99, 163, 256, 386, \dots}_{
        #         \text{What is this pattern?}
        #         }
        #     """),
        #     "WhatIsThisPattern"
        # ),
        # (tex_mobject(r"n \choose k"), "NChooseK"),
        # (GraphScene(SAMPLE_GRAPH), "SampleGraph"),
        # (text_mobject("You don't even want me to draw this..."), "DontWantToDraw"),
        # (tex_mobject(r"{100 \choose 2} = \frac{100 \cdot 99}{2} = 4950"), "100Choose2"),
        # (text_mobject("What? You actually want me to draw it?  Okay..."), "ReallyDontWant"),
        # (text_mobject(r"There! You happy? \\ It's just one big blue blob."), "YouHappy"),
        # (
        #     tex_mobject(
        #         r"{100 \choose 4} = \frac{(100)(99)(98)(97)}{(1)(2)(3)(4)} = 3,921,225"
        #     ),
        #     "100Choose4"
        # ),
        # (text_mobject("Euler's Characteristic Formula"), "EF_Words"),
        # (cs_outer, "OuterRegion"),
        # (text_mobject("Pause and see if you can remember on your own!"), "Recap")
        # (CircleScene([2*np.pi*random() for x in range(100)]), "CircleScene100")
        # (text_mobject(r"""
        #     \textbf{Eul$\cdot$er's} (\text{oil}\textschwa\text{rz}), \emph{adj}:
        #     \begin{enumerate}
        #         \item Beautiful
        #         \item Demonstrating an unexpected logical aesthetic, especially in the context of mathematics.
        #     \end{enumerate}
        # """), "EulersDefinition"),
        # (cs_graph, "SuitableGraph"),
    ]
    for thing, name in savable_things:
        thing.save_image(prefix + name)

