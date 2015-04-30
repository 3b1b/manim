#!/usr/bin/env python

import numpy as np
import itertools as it
import operator as op
from copy import deepcopy
from random import random


from animation import *
from mobject import *
from image_mobject import *
from constants import *
from region import *
from scene import Scene

from moser_helpers import *
from graphs import *


movie_prefix = "moser/"

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
    sc.write_to_movie(movie_prefix + "CountLines%dPoints"%len(radians))


def count_intersection_points(*radians):
    radians = [r % (2*np.pi) for r in radians]
    radians.sort()
    sc = CircleScene(radians)
    intersection_points = [
        intersection((p[0], p[2]), (p[1], p[3]))
        for p in it.combinations(sc.points, 4)
    ]
    intersection_dots = [Dot(point) for point in intersection_points]
    text_center = (sc.radius + 0.5, sc.radius -0.5, 0)
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
    sc.count(intersection_dots, "show", num_offset = (0, 0, 0))
    sc.dither()
    # sc.animate(Transform(intersection_dots, new_dots))
    anims = []
    for mob in sc.mobjects:
        if mob == sc.number: #put in during animate_count
            anims.append(Transform(mob, answer))
        else:
            anims.append(FadeOut(mob))
    anims.append(Animation(formula))
    sc.animate(*anims, run_time = 1)

    name = "CountIntersectionPoints%dPoints"%len(radians)
    sc.write_to_movie(movie_prefix + name)

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
    sc1.write_to_movie(movie_prefix + "NonGeneralPosition")

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
    sc.animate(*[
        FadeOut(mob, alpha_func = not_quite_there) 
        for mob in sc.lines + sc.dots
    ])
    sc.add(sc.circle)
    sc.animate(*[
        ScaleInPlace(mob, 3, alpha_func = there_and_back) 
        for mob in (dot0, dot1)
    ])
    sc.animate(Transform(line, dot0))
    name = "LineCorrspondsWithPair%d%d"%(dot0_index, dot1_index)
    sc.write_to_movie(movie_prefix + name)

def illustrate_n_choose_k(n, k):
    sc = Scene()
    nrange = range(1, n+1)
    tuples  = list(it.combinations(nrange, k))
    nrange_mobs = tex_mobjects([str(n) + r'\;' for n in nrange])
    tuple_mobs  = tex_mobjects(
        [
            (r'\\&' if c%(20//k) == 0 else r'\;\;') + str(p)
            for p, c in zip(tuples, it.count())
        ], 
        size = r"\small"
    )
    tuple_terms = {
        2 : "pairs", 
        3 : "triplets",
        4 : "quadruplets",
    }
    tuple_term = tuple_terms[k] if k in tuple_terms else "tuples"
    form1, count, form2 = tex_mobject([
        r"{%d \choose %d} = "%(n, k),
        "%d"%choose(n, k),
        r" \text{ total %s}"%tuple_term
    ])
    for mob in nrange_mobs:
        mob.shift((0, 2, 0))
    for mob in form1, count, form2:
        mob.shift((0, -SPACE_HEIGHT + 1, 0))
    count_center = count.get_center()
    for mob in tuple_mobs:
        mob.scale(0.6)

    sc.add(*nrange_mobs)
    sc.dither()
    run_time = 6.0
    frame_time = run_time / len(tuples)
    for tup, count in zip(tuples, it.count()):
        count_mob = tex_mobject(str(count+1))
        count_mob.center().shift(count_center)
        sc.add(count_mob)
        tuple_copy = CompoundMobject(*[nrange_mobs[index-1] for index in tup])
        tuple_copy.highlight()
        sc.add(tuple_copy)
        sc.add(tuple_mobs[count])
        sc.dither(frame_time)
        sc.remove(count_mob)
        sc.remove(tuple_copy)
    sc.add(count_mob)
    sc.animate(FadeIn(CompoundMobject(form1, form2)))
    sc.write_to_movie(movie_prefix + "Illustrate%dChoose%d"%(n, k))

def intersection_point_correspondances(radians, indices):
    assert(len(indices) == 4)
    indices.sort()
    sc = CircleScene(radians)
    intersection_point = intersection(
        (sc.points[indices[0]], sc.points[indices[2]]),
        (sc.points[indices[1]], sc.points[indices[3]])
    )
    intersection_point = tuple(list(intersection_point) + [0])
    intersection_dot = Dot(intersection_point)
    intersection_dot_arrow = Arrow(intersection_point).nudge()
    sc.add(intersection_dot)
    pairs = list(it.combinations(range(len(radians)), 2))
    lines_to_save = [
        sc.lines[pairs.index((indices[p0], indices[p1]))]
        for p0, p1 in [(0, 2), (1, 3)]
    ]
    dots_to_save = [
        sc.dots[p]
        for p in indices
    ]
    line_statement = tex_mobject(r"\text{Pair of Lines}")
    dots_statement = tex_mobject(r"&\text{Quadruplet of} \\ &\text{outer dots}")
    for mob in line_statement, dots_statement:
        mob.center()
        mob.scale(0.7)
        mob.shift((SPACE_WIDTH-2, SPACE_HEIGHT - 1, 0))
    fade_outs = []
    line_highlights = []
    dot_highlights = []
    dot_pointers = []
    for mob in sc.mobjects:
        if mob in lines_to_save:
            line_highlights.append(Highlight(mob))
        elif mob in dots_to_save:
            dot_highlights.append(Highlight(mob))
            dot_pointers.append(Arrow(mob.get_center()).nudge())
        elif mob != intersection_dot:
            fade_outs.append(FadeOut(mob, alpha_func = not_quite_there))

    sc.add(intersection_dot_arrow)
    sc.animate(Highlight(intersection_dot))
    sc.remove(intersection_dot_arrow)
    sc.animate(*fade_outs)
    sc.dither()
    sc.add(line_statement)
    sc.animate(*line_highlights)
    sc.remove(line_statement)
    sc.dither()
    sc.add(dots_statement, *dot_pointers)
    sc.animate(*dot_highlights)
    sc.remove(dots_statement, *dot_pointers)

    name = "IntersectionPointCorrespondances"
    for ind in indices:
        name += str(ind)
    sc.write_to_movie(movie_prefix + name)

def lines_intersect_outside(radians, indices):
    assert(len(indices) == 4)
    indices.sort()
    sc = CircleScene(radians)
    intersection_point = intersection(
        (sc.points[indices[0]], sc.points[indices[1]]),
        (sc.points[indices[2]], sc.points[indices[3]])
    )
    intersection_point = tuple(list(intersection_point) + [0])
    intersection_dot = Dot(intersection_point)
    pairs = list(it.combinations(range(len(radians)), 2))
    lines_to_save = [
        sc.lines[pairs.index((indices[p0], indices[p1]))]
        for p0, p1 in [(0, 1), (2, 3)]
    ]
    sc.animate(*[
        FadeOut(mob, alpha_func = not_quite_there)
        for mob in sc.mobjects if mob not in lines_to_save
    ])
    sc.animate(*[
        Transform(
            Line(sc.points[indices[p0]], sc.points[indices[p1]]), 
            Line(sc.points[indices[p0]], intersection_point))
        for p0, p1 in [(0, 1), (3, 2)]
    ] + [ShowCreation(intersection_dot)])

    name = "LinesIntersectOutside"
    for ind in indices:
        name += str(ind)
    sc.write_to_movie(movie_prefix + name)

def quadruplets_to_intersections(*radians):
    sc = CircleScene(radians)
    quadruplets = it.combinations(range(len(radians)), 4)
    frame_time = 1.0
    for quad in quadruplets:
        intersection_dot = Dot(intersection(
            (sc.points[quad[0]], sc.points[quad[2]]),
            (sc.points[quad[1]], sc.points[quad[3]])
        )).repeat(3)
        dot_quad = [deepcopy(sc.dots[i]) for i in quad]
        for dot in dot_quad:
            dot.scale_in_place(2)
        # arrows = [Arrow(d.get_center()) for d in dot_quad]
        dot_quad = CompoundMobject(*dot_quad)
        # arrows = CompoundMobject(*arrows)
        dot_quad.highlight()
        # sc.add(arrows)
        sc.add(dot_quad)
        sc.dither(frame_time / 3)
        sc.animate(Transform(
            dot_quad,
            intersection_dot,
            run_time = 3*frame_time/2
        ))
        # sc.remove(arrows)

    name = "QuadrupletsToIntersections%d"%len(radians)
    sc.write_to_movie(movie_prefix + name)

def defining_graph(graph):
    gs = GraphScene(graph)
    dots, lines = gs.vertices, gs.edges
    gs.remove(*dots + lines)
    all_dots = CompoundMobject(*dots)
    gs.animate(ShowCreation(all_dots))
    gs.remove(all_dots)
    gs.add(*dots)
    gs.dither()
    gs.animate(*[
        ShowCreation(line) for line in lines
    ])

    #Move to new graph
    new_graph = deepcopy(graph)
    new_graph["vertices"] = [
        (v[0] + 3*random(), v[1] + 3*random(), 0)
        for v in new_graph["vertices"]
    ]
    ngs = GraphScene(new_graph)
    gs.animate(*[
        Transform(m[0], m[1])
        for m in zip(gs.mobjects, ngs.mobjects)
    ], run_time = 7.0)

    name = "DefiningGraph" + graph["name"]
    gs.write_to_movie(movie_prefix + name)

def doubled_edges(graph):
    gs = GraphScene(graph)
    lines_to_double = gs.edges[:9:3]
    crazy_lines = [
        (
            line,
            Line(line.end, line.start),
            CurvedLine(line.start, line.end) ,
            CurvedLine(line.end,   line.start)
        )
        for line in lines_to_double
    ]
    anims = []
    outward_curved_lines = []
    kwargs = {"run_time" : 3.0}
    for straight, backwards, inward, outward in crazy_lines:
        anims += [
            Transform(straight, inward, **kwargs),
            Transform(backwards, outward, **kwargs),
        ]
        outward_curved_lines.append(outward)
    gs.animate(*anims)
    gs.dither()
    gs.remove(*outward_curved_lines)

    name = "DoubledEdges" + graph["name"]
    gs.write_to_movie(movie_prefix + name)


def eulers_formula(graph):
    gs = GraphScene(graph)
    terms = "V - E + F =2".split(" ")
    form = dict([
        (key, mob)
        for key, mob in zip(terms, tex_mobjects(terms))
    ])
    for mob in form.values():
        mob.shift((0, SPACE_HEIGHT-1.5, 0))
    formula = CompoundMobject(*[form[k] for k in form.keys() if k != "=2"])
    new_form = dict([
        (key, deepcopy(mob).shift((0, -0.7, 0)))
        for key, mob in zip(form.keys(), form.values())
    ])
    gs.add(formula)
    colored_dots = [
        deepcopy(d).scale_in_place(1.5).highlight("red") 
        for d in gs.dots
    ]
    colored_edges = [
        deepcopy(e).highlight("red")
        for e in gs.edges
    ]
    frame_time = 0.3

    gs.generate_regions()
    parameters = [
        (colored_dots,  "V", "mobject", "-", "show_creation"),
        (colored_edges, "E", "mobject", "+", "show_creation"),
        (gs.regions,    "F", "region", "=2", "show_all")
    ]
    for items, letter, item_type, symbol, mode in parameters:
        gs.count(
            items, 
            item_type  = item_type,
            mode       = mode,
            num_offset = new_form[letter].get_center(), 
            run_time   = frame_time*len(items)
        )
        gs.dither()        
        if item_type == "mobject":
            gs.remove(*items)
        gs.add(new_form[symbol])
    gs.reset_background()

    name = "EulersFormula" + graph["name"]
    gs.write_to_movie(movie_prefix + name)

def apply_euler_to_moser(*radians):
    cs = CircleScene(radians)
    cs.remove(cs.n_equals)
    n_equals, intersection_count = tex_mobjects([
        r"&n = %d\\"%len(radians),
        r"&{%d \choose 4} = %d"%(len(radians), choose(len(radians), 4))
    ])
    shift_val = cs.n_equals.get_center() - n_equals.get_center()
    for mob in n_equals, intersection_count:
        mob.shift(shift_val)
    cs.add(n_equals)
    yellow_dots  = [d.highlight("yellow") for d in deepcopy(cs.dots)]
    yellow_lines = [l.highlight("yellow") for l in deepcopy(cs.lines)]
    cs.animate(*[
        ShowCreation(dot) for dot in yellow_dots
    ], run_time = 1.0)
    cs.dither()
    cs.remove(*yellow_dots)
    cs.animate(*[
        ShowCreation(line) for line in yellow_lines
    ], run_time = 1.0)
    cs.dither()
    cs.remove(yellow_lines)
    cannot_intersect = text_mobject(r"""
        Euler's formula does not apply to \\
        graphs whose edges intersect!
        """
    )
    cannot_intersect.center()
    for mob in cs.mobjects:
        mob.fade(0.3)
    cs.add(cannot_intersect)
    cs.dither()
    cs.remove(cannot_intersect)
    for mob in cs.mobjects:
        mob.fade(1/0.3)
    cs.generate_intersection_dots()
    cs.animate(FadeIn(intersection_count), *[
        ShowCreation(dot) for dot in cs.intersection_dots
    ])


    name = "ApplyEulerToMoser%d"%len(radians)
    cs.write_to_movie(movie_prefix + name)

def show_moser_graph_lines(*radians):
    radians = list(set(map(lambda x : x%(2*np.pi), radians)))
    radians.sort()

    cs = CircleScene(radians)
    cs.chop_lines_at_intersection_points()
    cs.add(*cs.intersection_dots)
    small_lines = [
        deepcopy(line).scale_in_place(0.5) 
        for line in cs.lines
    ]
    cs.animate(*[
        Transform(line, small_line, run_time = 3.0)
        for line, small_line in zip(cs.lines, small_lines)
    ])
    cs.count(cs.lines, color = "yellow", 
             run_time = 9.0, num_offset = (0, 0, 0))
    cs.dither()
    cs.remove(cs.number)
    cs.chop_circle_at_points()
    cs.animate(*[
        Transform(p, sp, run_time = 3.0)
        for p, sp in zip(cs.circle_pieces, cs.smaller_circle_pieces)
    ])
    cs.count(cs.circle_pieces, color = "yellow", 
             run_time = 2.0, num_offset = (0, 0, 0))
    name = "ShowMoserGraphLines%d"%len(radians)
    cs.write_to_movie(movie_prefix + name)

    

##################################################

if __name__ == '__main__':
    radians = np.arange(0, 6, 6.0/7)
    # count_lines(*radians)
    # count_lines(*radians[:4])
    # count_intersection_points(*radians[:4])
    # count_intersection_points(*radians[:6])
    # count_intersection_points(*radians)
    # non_general_position()
    # line_corresponds_with_pair(radians, radians[3], radians[4])
    # line_corresponds_with_pair(radians, radians[2], radians[5])
    # illustrate_n_choose_k(7, 2)
    # illustrate_n_choose_k(6, 4)
    # intersection_point_correspondances(radians, range(0, 7, 2))
    # lines_intersect_outside(radians, [2, 4, 5, 6])
    # quadruplets_to_intersections(*radians[:6]) 
    # defining_graph(SAMPLE_GRAPH)
    # doubled_edges(CUBE_GRAPH)
    # eulers_formula(CUBE_GRAPH)
    # eulers_formula(SAMPLE_GRAPH)
    # eulers_formula(OCTOHEDRON_GRAPH)
    # apply_euler_to_moser(*radians)
    show_moser_graph_lines(*radians[:6])






