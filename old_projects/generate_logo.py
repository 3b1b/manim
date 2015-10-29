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

class LogoGeneration(Scene):
    LOGO_RADIUS = 1.5
    INNER_RADIUS_RATIO = 0.55
    CIRCLE_DENSITY = 100
    CIRCLE_BLUE = "skyblue"
    SPHERE_DENSITY = 50
    SPHERE_BLUE = DARK_BLUE
    CIRCLE_SPHERE_INTERPOLATION = 0.3
    FRAME_DURATION = 0.01

    def construct(self):
        self.frame_duration = FRAME_DURATION
        circle = Circle(
            density = self.CIRCLE_DENSITY, 
            color = self.CIRCLE_BLUE
        ).repeat(5).scale(self.LOGO_RADIUS)
        sphere = Sphere(
            density = self.SPHERE_DENSITY, 
            color = self.SPHERE_BLUE
        ).scale(self.LOGO_RADIUS)
        sphere.rotate(-np.pi / 7, [1, 0, 0])
        sphere.rotate(-np.pi / 7)
        alpha = 0.3
        iris = Mobject()
        Mobject.interpolate(
            circle, sphere, iris, 
            self.CIRCLE_SPHERE_INTERPOLATION
        )
        for mob, color in [(iris, LIGHT_BROWN), (circle, DARK_BROWN)]:
            mob.highlight(color, lambda (x, y, z) : x < 0 and y > 0)
            mob.highlight(
                "black", 
                lambda point: np.linalg.norm(point) < \
                              self.INNER_RADIUS_RATIO*self.LOGO_RADIUS
            )
        name = TextMobject("3Blue1Brown").center()
        name.highlight("grey")
        name.shift(2*DOWN)

        self.play(Transform(
            circle, iris, 
            run_time = DEFAULT_ANIMATION_RUN_TIME
        ))
        self.add(name)
        self.dither()
        print "Dragging pixels..."
        self.frames = drag_pixels(self.frames)

