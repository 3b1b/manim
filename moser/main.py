#!/usr/bin/env python

import numpy as np
import itertools as it
import operator as op
from copy import deepcopy


from animation import *
from mobject import *
from image_mobject import *
from constants import *
from region import *
from scene import Scene

from moser_helpers import *

RADIUS = SPACE_HEIGHT - 0.1
CIRCLE_DENSITY = DEFAULT_POINT_DENSITY_1D*RADIUS


class CircleScene(Scene):
    def __init__(self, radians, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        self.radius = RADIUS
        self.circle = Circle(density = CIRCLE_DENSITY).scale(self.radius)
        self.points = [
            (self.radius * np.cos(angle), self.radius * np.sin(angle), 0)
            for angle in radians
        ]
        self.dots = [Dot(point) for point in self.points]
        self.lines = [Line(p1, p2) for p1, p2 in it.combinations(self.points, 2)]
        self.add(self.circle, *self.dots + self.lines)


##################################################

def count_lines(*radians):
    sc = CircleScene(radians)
    text = tex_mobject(r"\text{How Many Lines?}", size = r"\large")
    text_center = (sc.radius + 1, sc.radius -1, 0)
    text.scale(0.4).shift(text_center)
    x = text_center[0]
    new_lines = [
        Line((x-1, y, 0), (x+1, y, 0))
        for y in np.arange(
            -(sc.radius - 1), 
            sc.radius - 1, 
            (2*sc.radius - 2)/len(sc.lines)
        )
    ]
    sc.add(text)
    sc.dither()
    sc.animate(*[
       Transform(line1, line2, run_time = 2)
       for line1, line2 in zip(sc.lines, new_lines)
    ])
    return sc


def count_intersection_points(*radians):
    radians = [r % (2*np.pi) for r in radians]
    radians.sort()
    sc = CircleScene(radians)
    intersection_points = [
        intersection([p[0], p[2]], [p[1], p[3]])
        for p in it.combinations(sc.points, 4)
    ]
    intersection_dots = CompoundMobject(*[
        Dot(point) for point in intersection_points
    ])
    how_many = tex_mobject(r"""
        \text{How many}\\
        \text{intersection points?}
    """, size = r"\large")
    text_center = (sc.radius + 1, sc.radius -1, 0)
    how_many.scale(0.4).shift(text_center)
    new_points = [
        (text_center[0], y, 0)
        for y in np.arange(
            -(sc.radius - 1), 
            sc.radius - 1, 
            (2*sc.radius - 2)/choose(len(sc.points), 4)
        )
    ]
    new_dots = CompoundMobject(*[
        Dot(point) for point in new_points
    ])

    sc.add(how_many)
    sc.animate(ShowCreation(intersection_dots))
    sc.add(intersection_dots)
    sc.animate(Transform(intersection_dots, new_dots))
    sc.add(tex_mobject(str(len(new_points))).center())
    return sc

def non_general_position():
    radians = np.arange(1, 7)
    new_radians = (np.pi/3)*radians
    sc1 = CircleScene(radians)
    sc2 = CircleScene(new_radians)
    center_region = reduce(
        Region.intersect,
        [
            HalfPlane((sc1.points[x], sc1.points[(x+3)%6]))
            for x in [0, 4, 2]#Ya know, trust it
        ]
    )
    center_region
    text = tex_mobject(r"\text{This region disappears}", size = r"\large")
    text.center().scale(0.5).shift((-sc1.radius, sc1.radius-0.3, 0))
    arrow = Arrow(
        point = (-0.35, -0.1, 0),
        direction = (1, -1, 0), 
        length = sc1.radius + 1,
        color = "white",
    )

    sc1.highlight_region(center_region, "green")
    sc1.add(text, arrow)
    sc1.dither(2)
    sc1.remove(text, arrow)
    sc1.reset_background()
    sc1.animate(*[
        Transform(mob1, mob2, run_time = DEFAULT_ANIMATION_RUN_TIME)
        for mob1, mob2 in zip(sc1.mobjects, sc2.mobjects)
    ])
    return sc1


##################################################

if __name__ == '__main__':
    radians = np.arange(0, 6, 6.0/7)
    count_lines(*radians).write_to_movie("moser/CountLines")
    count_intersection_points(*radians).write_to_movie("moser/CountIntersectionPoints")
    non_general_position().write_to_movie("moser/NonGeneralPosition")
