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
    #TODO, Count things explicitly?
    sc = CircleScene(radians)
    text_center = (sc.radius + 1, sc.radius -1, 0)
    scale_factor = 0.4
    text = tex_mobject(r"\text{How Many Lines?}", size = r"\large")
    n = len(radians)
    formula, answer = tex_mobject([
        r"{%d \choose 2} = \frac{%d(%d - 1)}{2} = "%(n, n, n),
        str(choose(n, 2))
    ])
    text.scale(scale_factor).shift(text_center)
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
    sc.dither()
    sc.remove(text)
    sc.count(new_lines)
    anims = [FadeIn(formula)]
    for mob in sc.mobjects:
        if mob == sc.number: #put in during animate_count
            anims.append(Transform(mob, answer))
        else:
            anims.append(FadeOut(mob))
    sc.animate(*anims, run_time = 1)
    return sc


def count_intersection_points(*radians):
    radians = [r % (2*np.pi) for r in radians]
    radians.sort()
    sc = CircleScene(radians)
    intersection_points = [
        intersection((p[0], p[2]), (p[1], p[3]))
        for p in it.combinations(sc.points, 4)
    ]
    intersection_dots = [Dot(point) for point in intersection_points]
    text_center = (sc.radius + 1, sc.radius -0.5, 0)
    size = r"\large"
    scale_factor = 0.4
    text = tex_mobject(r"\text{How Many Intersection Points?}", size = size)
    n = len(radians)
    formula, answer = tex_mobjects([
        r"{%d \choose 4} = \frac{%d(%d - 1)(%d - 2)(%d-3)}{1\cdot 2\cdot 3 \cdot 4}="%(n, n, n, n, n),
        str(choose(n, 4))
    ])
    text.scale(scale_factor).shift(text_center)
    # new_points = [
    #     (text_center[0], y, 0)
    #     for y in np.arange(
    #         -(sc.radius - 1), 
    #         sc.radius - 1, 
    #         (2*sc.radius - 2)/choose(len(sc.points), 4)
    #     )
    # ]
    # new_dots = CompoundMobject(*[
    #     Dot(point) for point in new_points
    # ])

    sc.add(text)
    sc.count(intersection_dots, "show_creation", num_offset = (0, 0, 0))
    sc.dither()
    # sc.animate(Transform(intersection_dots, new_dots))
    anims = []
    for mob in sc.mobjects:
        if mob == sc.number: #put in during animate_count
            anims.append(Transform(mob, answer))
        else:
            anims.append(FadeOut(mob))
    anims.append(FadeIn(formula)) #Put here to so they are foreground
    sc.animate(*anims, run_time = 1)
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

def line_corresponds_with_pair(radians, r1, r2):
    sc = CircleScene(radians)
    #Remove from sc.lines list, so they won't be faded out
    assert r1 in radians and r2 in radians
    line_index = list(it.combinations(radians, 2)).index((r1, r2))
    radians = list(radians)
    dot0_index, dot1_index = radians.index(r1), radians.index(r2)
    line, dot0, dot1 = sc.lines[line_index], sc.dots[dot0_index], sc.dots[dot1_index]
    sc.lines.remove(line)
    sc.dots.remove(dot0)
    sc.dots.remove(dot1)
    sc.dither()
    sc.animate(*[FadeOut(mob) for mob in sc.lines + sc.dots])
    sc.add(sc.circle)
    sc.animate(*[
        ScaleInPlace(mob, 3, alpha_func = there_and_back) 
        for mob in (dot0, dot1)
    ])
    sc.animate(Transform(line, dot0))
    return sc

def illustrate_n_choose_2(n):
    #TODO, maybe make this snazzy
    sc = Scene()
    nrange = range(1, n+1)
    nrange_im = tex_mobject(str(nrange))
    pairs_str = str(list(it.combinations(nrange, 2)))
    exp = tex_mobject(r"{{%d \choose 2} = %d \text{ total pairs}}"%(n, choose(n, 2)))
    pairs_im  = tex_mobject(r"\underbrace{%s}"%pairs_str, size=r"\tiny")
    nrange_im.shift((0, 2, 0))
    pairs_im.scale(0.7)
    exp.shift((0, -2, 0))
    sc.add(nrange_im)
    sc.dither()
    sc.animate(FadeIn(pairs_im), FadeIn(exp))
    sc.add(pairs_im)
    return sc
    

##################################################

if __name__ == '__main__':
    radians = np.arange(0, 6, 6.0/7)
    # count_lines(*radians).write_to_movie("moser/CountLines")
    count_intersection_points(*radians).write_to_movie("moser/CountIntersectionPoints")
    # non_general_position().write_to_movie("moser/NonGeneralPosition")
    # line_corresponds_with_pair(radians, radians[3], radians[4]).write_to_movie("moser/LineCorrespondsWithPair34")
    # line_corresponds_with_pair(radians, radians[2], radians[5]).write_to_movie("moser/LineCorrespondsWithPair25")
    # illustrate_n_choose_2(6).write_to_movie("moser/IllustrateNChoose2with6")
