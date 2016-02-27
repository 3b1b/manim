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
from mobject.region import  *
from scene import Scene, GraphScene, PascalsTriangleScene
from script_wrapper import command_line_create_scene

RADIUS            = SPACE_HEIGHT - 0.1
CIRCLE_DENSITY    = DEFAULT_POINT_DENSITY_1D*RADIUS
MOVIE_PREFIX      = "moser/"
RADIANS           = np.arange(0, 6, 6.0/7)
MORE_RADIANS      = np.append(RADIANS, RADIANS + 0.5)
N_PASCAL_ROWS     = 7
BIG_N_PASCAL_ROWS = 11

def int_list_to_string(int_list):
    return "-".join(map(str, int_list))

def moser_function(n):
    return choose(n, 4) + choose(n, 2) + 1

###########################################

class CircleScene(Scene):
    args_list = [
        (RADIANS[:x],)
        for x in range(1, len(RADIANS)+1)
    ]
    @staticmethod
    def args_to_string(*args):
        return str(len(args[0])) #Length of radians

    def __init__(self, radians, radius = RADIUS, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        self.radius = radius
        self.circle = Circle(density = CIRCLE_DENSITY).scale(self.radius)
        self.points = [
            (self.radius * np.cos(angle), self.radius * np.sin(angle), 0)
            for angle in radians
        ]
        self.dots = [Dot(point) for point in self.points]
        self.lines = [Line(p1, p2) for p1, p2 in it.combinations(self.points, 2)]
        self.n_equals = TexMobject(
            "n=%d"%len(radians),
        ).shift((-SPACE_WIDTH+1, SPACE_HEIGHT-1.5, 0))
        self.add(self.circle, self.n_equals, *self.dots + self.lines)


    def generate_intersection_dots(self):
        """
        Generates and adds attributes intersection_points and
        intersection_dots, but does not yet add them to the scene
        """
        self.intersection_points = [
            intersection((p[0], p[2]), (p[1], p[3]))
            for p in it.combinations(self.points, 4)
        ]
        self.intersection_dots = [
            Dot(point) for point in self.intersection_points
        ]

    def chop_lines_at_intersection_points(self):
        if not hasattr(self, "intersection_dots"):
            self.generate_intersection_dots()
        self.remove(*self.lines)
        self.lines = []
        for point_pair in it.combinations(self.points, 2):
            int_points = filter(
                lambda p : is_on_line(p, *point_pair), 
                self.intersection_points
            )
            points = list(point_pair) + int_points
            points = map(lambda p : (p[0], p[1], 0), points)
            points.sort(cmp = lambda x,y: cmp(x[0], y[0]))
            self.lines += [
                Line(points[i], points[i+1])
                for i in range(len(points)-1)
            ]
        self.add(*self.lines)

    def chop_circle_at_points(self):
        self.remove(self.circle)
        self.circle_pieces = []
        self.smaller_circle_pieces = []
        for i in range(len(self.points)):
            pp = self.points[i], self.points[(i+1)%len(self.points)]
            transform = np.array([
                [pp[0][0], pp[1][0], 0],
                [pp[0][1], pp[1][1], 0],
                [0, 0, 1]
            ])
            circle = deepcopy(self.circle)
            smaller_circle = deepcopy(self.circle)
            for c in circle, smaller_circle:
                c.points = np.dot(
                    c.points, 
                    np.transpose(np.linalg.inv(transform))
                )
                c.filter_out(
                    lambda p : p[0] < 0 or p[1] < 0
                )
                if c == smaller_circle:
                    c.filter_out(
                        lambda p : p[0] > 4*p[1] or p[1] > 4*p[0]
                    )
                c.points = np.dot(
                    c.points, 
                    np.transpose(transform)
                )
            self.circle_pieces.append(circle)
            self.smaller_circle_pieces.append(smaller_circle)
        self.add(*self.circle_pieces)

    def generate_regions(self):
        self.regions = plane_partition_from_points(*self.points)
        interior = Region(lambda x, y : x**2 + y**2 < self.radius**2)
        map(lambda r : r.intersect(interior), self.regions)
        self.exterior = interior.complement()


class CountSections(CircleScene):
    def __init__(self, *args, **kwargs):
        CircleScene.__init__(self, *args, **kwargs)
        self.remove(*self.lines)
        self.play(*[
            Transform(Dot(points[i]),Line(points[i], points[1-i]))
            for points in it.combinations(self.points, 2)
            for i in (0, 1)
        ], run_time = 2.0)
        regions = plane_partition_from_points(*self.points)
        interior = Region(lambda x, y : x**2 + y**2 < self.radius**2)
        map(lambda r : r.intersect(interior), regions)
        regions = filter(lambda r : r.bool_grid.any(), regions)
        self.count_regions(regions, num_offset = ORIGIN)

class MoserPattern(CircleScene):
    args_list = [(MORE_RADIANS,)]
    def __init__(self, radians, *args, **kwargs):
        CircleScene.__init__(self, radians, *args, **kwargs)
        self.remove(*self.dots + self.lines + [self.n_equals])
        n_equals, num = TexMobject(["n=", "10"]).split()
        for mob in n_equals, num:
            mob.shift((-SPACE_WIDTH + 1.5, SPACE_HEIGHT - 1.5, 0))
        self.add(n_equals)
        for n in range(1, len(radians)+1):
            self.add(*self.dots[:n])
            self.add(*[Line(p[0], p[1]) for p in it.combinations(self.points[:n], 2)])
            tex_stuffs = [
                TexMobject(str(moser_function(n))),
                TexMobject(str(n)).shift(num.get_center())
            ]
            self.add(*tex_stuffs)
            self.dither(0.5)
            self.remove(*tex_stuffs)

def hpsq_taylored_alpha(t):
    return 0.3*np.sin(5*t-5)*np.exp(-20*(t-0.6)**2) + smooth(t)

class HardProblemsSimplerQuestions(Scene):
    def __init__(self, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        right_center = np.array((4, 1, 0))
        left_center = np.array((-5, 1, 0))
        scale_factor = 0.7
        fermat = dict([
            (
                sym, 
                Mobject(*TexMobjects(
                    ["x","^"+sym,"+","y","^"+sym,"=","z","^"+sym]
                ))
            )
            for sym in ["n", "2", "3"]
        ])
        # not_that_hard = TextMobject("(maybe not that hard...)").scale(0.5)
        fermat2, fermat2_jargon = TexMobject([
            r"&x^2 + y^2 = z^2 \\",
            r"""
                &(3, 4, 5) \\
                &(5, 12, 13) \\
                &(15, 8, 17) \\
                &\quad \vdots \\
                (m^2 - &n^2, 2mn, m^2 + n^2) \\
                &\quad \vdots
            """
        ]).split()
        fermat3, fermat3_jargon = TexMobject([
            r"&x^3 + y^3 = z^3\\",
            r"""
                &y^3 = (z - x)(z - \omega x)(z - \omega^2 x) \\
                &\mathds{Z}[\omega] \text{ is a UFD...}
            """
        ]).split()
        for mob in [fermat2, fermat3, fermat["2"], fermat["3"],
                    fermat2_jargon, fermat3_jargon]:
            mob.scale(scale_factor)
        fermat["2"].shift(right_center)
        fermat["3"].shift(left_center)
        fermat["n"].shift((0, SPACE_HEIGHT - 1, 0))
        shift_val = right_center - fermat2.get_center()
        fermat2.shift(shift_val)
        fermat2_jargon.shift(shift_val)
        shift_val = left_center - fermat3.get_center()
        fermat3.shift(shift_val)
        fermat3_jargon.shift(shift_val)

        copies = [
            deepcopy(fermat["n"]).center().scale(scale_factor).shift(c)
            for c in [left_center, right_center]
        ]
        self.add(fermat["n"])
        self.play(*[
            Transform(deepcopy(fermat["n"]), f_copy)
            for f_copy in copies
        ])
        self.remove(*self.mobjects)
        self.add(fermat["n"])
        self.play(*[
            CounterclockwiseTransform(mobs[0], mobs[1])
            for f_copy, sym in zip(copies, ["3", "2"])            
            for mobs in zip(f_copy.split(), fermat[sym].split())
        ])
        self.remove(*self.mobjects)
        self.add(fermat["n"], fermat2, fermat3)
        self.dither()

        circle_grid = Mobject(
            Circle(), 
            Grid(radius = 2),
            TexMobject(r"\mathds{R}^2").shift((2, -2, 0))
        )
        start_line = Line((-1, 0, 0), (-1, 2, 0))
        end_line   = Line((-1, 0, 0), (-1, -2, 0))
        for mob in circle_grid, start_line, end_line:
            mob.scale(0.5).shift(right_center + (0, 2, 0))

        other_grid = Mobject(
            Grid(radius = 2),
            TexMobject(r"\mathds{C}").shift((2, -2, 0))
        )
        omega = np.array((0.5, 0.5*np.sqrt(3), 0))
        dots = Mobject(*[
            Dot(t*np.array((1, 0, 0)) + s * omega)
            for t, s in it.product(range(-2, 3), range(-2, 3))
        ])
        for mob in dots, other_grid:
            mob.scale(0.5).shift(left_center + (0, 2, 0))

        self.add(circle_grid, other_grid)
        self.play(
            FadeIn(fermat2_jargon),
            FadeIn(fermat3_jargon),
            CounterclockwiseTransform(start_line, end_line),
            ShowCreation(dots)
        )
        self.dither()
        all_mobjects = Mobject(*self.mobjects)
        self.remove(*self.mobjects)
        self.play(
            Transform(
                all_mobjects,
                Point((SPACE_WIDTH, 0, 0))
            ),
            Transform(
                Point((-SPACE_WIDTH, 0, 0)), 
                Mobject(*CircleScene(RADIANS).mobjects)
            )
        )

class CountLines(CircleScene):
    def __init__(self, radians, *args, **kwargs):
        CircleScene.__init__(self, radians, *args, **kwargs)
        #TODO, Count things explicitly?        
        text_center = (self.radius + 1, self.radius -1, 0)
        scale_factor = 0.4
        text = TexMobject(r"\text{How Many Lines?}", size = r"\large")
        n = len(radians)
        formula, answer = TexMobject([
            r"{%d \choose 2} = \frac{%d(%d - 1)}{2} = "%(n, n, n),
            str(choose(n, 2))
        ])
        text.scale(scale_factor).shift(text_center)
        x = text_center[0]
        new_lines = [
            Line((x-1, y, 0), (x+1, y, 0))
            for y in np.arange(
                -(self.radius - 1), 
                self.radius - 1, 
                (2*self.radius - 2)/len(self.lines)
            )
        ]
        self.add(text)
        self.dither()
        self.play(*[
           Transform(line1, line2, run_time = 2)
           for line1, line2 in zip(self.lines, new_lines)
        ])
        self.dither()
        self.remove(text)
        self.count(new_lines)
        anims = [FadeIn(formula)]
        for mob in self.mobjects:
            if mob == self.number:
                anims.append(Transform(mob, answer))
            else:
                anims.append(FadeOut(mob))
        self.play(*anims, run_time = 1)

class CountIntersectionPoints(CircleScene):
    def __init__(self, radians, *args, **kwargs):
        radians = [r % (2*np.pi) for r in radians]
        radians.sort()
        CircleScene.__init__(self, radians, *args, **kwargs)

        intersection_points = [
            intersection((p[0], p[2]), (p[1], p[3]))
            for p in it.combinations(self.points, 4)
        ]
        intersection_dots = [Dot(point) for point in intersection_points]
        text_center = (self.radius + 0.5, self.radius -0.5, 0)
        size = r"\large"
        scale_factor = 0.4
        text = TexMobject(r"\text{How Many Intersection Points?}", size = size)
        n = len(radians)
        formula, answer = TexMobject([
            r"{%d \choose 4} = \frac{%d(%d - 1)(%d - 2)(%d-3)}{1\cdot 2\cdot 3 \cdot 4}="%(n, n, n, n, n),
            str(choose(n, 4))
        ]).split()
        text.scale(scale_factor).shift(text_center)
        self.add(text)
        self.count(intersection_dots, mode="show", num_offset = ORIGIN)
        self.dither()
        anims = []
        for mob in self.mobjects:
            if mob == self.number: #put in during count
                anims.append(Transform(mob, answer))
            else:
                anims.append(FadeOut(mob))
        anims.append(Animation(formula))
        self.play(*anims, run_time = 1)

class NonGeneralPosition(CircleScene):
    args_list = []
    @staticmethod
    def args_to_string(*args):
        return ""

    def __init__(self, *args, **kwargs):
        radians = np.arange(1, 7)
        new_radians = (np.pi/3)*radians
        CircleScene.__init__(self, radians, *args, **kwargs)

        new_cs = CircleScene(new_radians)
        center_region = reduce(
            Region.intersect,
            [
                HalfPlane((self.points[x], self.points[(x+3)%6]))
                for x in [0, 4, 2]#Ya know, trust it
            ]
        )
        center_region
        text = TexMobject(r"\text{This region disappears}", size = r"\large")
        text.center().scale(0.5).shift((-self.radius, self.radius-0.3, 0))
        arrow = Arrow(
            point = (-0.35, -0.1, 0),
            direction = (1, -1, 0), 
            length = self.radius + 1,
            color = "white",
        )

        self.highlight_region(center_region, "green")
        self.add(text, arrow)
        self.dither(2)
        self.remove(text, arrow)
        self.reset_background()
        self.play(*[
            Transform(mob1, mob2, run_time = DEFAULT_ANIMATION_RUN_TIME)
            for mob1, mob2 in zip(self.mobjects, new_self.mobjects)
        ])

class GeneralPositionRule(Scene):
    def __init__(self, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        tuples = [
            (
                np.arange(0, 2*np.pi, np.pi/3), 
                "Not okay", 
                zip(range(3), range(3, 6))
            ),
            (
                RADIANS,
                "Okay",
                [],
            ),
            (
                np.arange(0, 2*np.pi, np.pi/4),
                "Not okay",
                zip(range(4), range(4, 8))
            ),
            (
                [2*np.pi*random() for x in range(5)],
                "Okay",
                [],
            ),
        ]
        first_time = True
        for radians, words, pairs in tuples:
            cs = CircleScene(radians)
            self.add(*cs.mobjects)
            words_mob = TextMobject(words).scale(2).shift((5, 3, 0))
            if not first_time:
                self.add(words_mob)
            if words == "Okay":
                words_mob.highlight("green")
                self.dither(2)                
            else:
                words_mob.highlight()
                intersecting_lines = [
                    line.scale_in_place(0.3).highlight()
                    for i, j in pairs                    
                    for line in [Line(cs.points[i], cs.points[j])]
                ]
                self.play(*[
                    ShowCreation(line, run_time = 1.0)
                    for line in intersecting_lines                    
                ])
                if first_time:
                    self.play(Transform(
                        Mobject(*intersecting_lines),
                        words_mob
                    ))
                    first_time = False
                self.dither()
            self.remove(*self.mobjects)


class LineCorrespondsWithPair(CircleScene):
    args_list = [
        (RADIANS, 2, 5),
        (RADIANS, 0, 4)
    ]
    @staticmethod
    def args_to_string(*args):
        return int_list_to_string(args[1:])

    def __init__(self, radians, dot0_index, dot1_index, 
                 *args, **kwargs):
        CircleScene.__init__(self, radians, *args, **kwargs)
        #Remove from self.lines list, so they won't be faded out
        radians = list(radians)    
        r1, r2 = radians[dot0_index], radians[dot1_index]
        line_index = list(it.combinations(radians, 2)).index((r1, r2))
        line, dot0, dot1 = self.lines[line_index], self.dots[dot0_index], self.dots[dot1_index]
        self.lines.remove(line)
        self.dots.remove(dot0)
        self.dots.remove(dot1)
        self.dither()
        self.play(*[
            ApplyMethod(mob.fade, 0.2)
            for mob in self.lines + self.dots
        ])
        self.play(*[
            Transform(
                dot, Dot(dot.get_center(), 3*dot.radius),
                rate_func = there_and_back
            )
            for dot in (dot0, dot1)
        ])
        self.play(Transform(line, dot0))

class IllustrateNChooseK(Scene):
    args_list = [
        (n, k)
        for n in range(1, 10)
        for k in range(n+1)
    ]
    @staticmethod
    def args_to_string(*args):
        return int_list_to_string(args)

    def __init__(self, n, k, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        nrange = range(1, n+1)
        tuples  = list(it.combinations(nrange, k))
        nrange_mobs = TexMobject([str(n) + r'\;' for n in nrange]).split()
        tuple_mobs  = TexMobjects(
            [
                (r'\\&' if c%(20//k) == 0 else r'\;\;') + str(p)
                for p, c in zip(tuples, it.count())
            ],
            size = r"\small",
        )#TODO, scale these up!
        tuple_terms = {
            2 : "pairs", 
            3 : "triplets",
            4 : "quadruplets",
        }
        tuple_term = tuple_terms[k] if k in tuple_terms else "tuples"
        if k == 2:
            str1 = r"{%d \choose %d} = \frac{%d(%d - 1)}{2}="%(n, k, n, n)
        elif k == 4:
            str1 = r"""
                {%d \choose %d} = 
                \frac{%d(%d - 1)(%d-2)(%d-3)}{1\cdot 2\cdot 3 \cdot 4}=
            """%(n, k, n, n, n, n)
        else: 
            str1 = r"{%d \choose %d} ="%(n, k)
        form1, count, form2 = TexMobject([
            str1,
            "%d"%choose(n, k),
            r" \text{ total %s}"%tuple_term
        ])
        pronunciation = TextMobject(
            "(pronounced ``%d choose %d\'\')"%(n, k)
        )
        for mob in nrange_mobs:
            mob.shift((0, 2, 0))
        for mob in form1, count, form2:
            mob.scale(0.75).shift((0, -SPACE_HEIGHT + 1, 0))
        count_center = count.get_center()
        for mob in tuple_mobs:
            mob.scale(0.6)
        pronunciation.shift(
            form1.get_center() + (0, 1, 0)
        )

        self.add(*nrange_mobs)
        self.dither()
        run_time = 6.0
        frame_time = run_time / len(tuples)
        for tup, count in zip(tuples, it.count()):
            count_mob = TexMobject(str(count+1))
            count_mob.center().shift(count_center)
            self.add(count_mob)
            tuple_copy = Mobject(*[nrange_mobs[index-1] for index in tup])
            tuple_copy.highlight()
            self.add(tuple_copy)
            self.add(tuple_mobs[count])
            self.dither(frame_time)
            self.remove(count_mob)
            self.remove(tuple_copy)
        self.add(count_mob)
        self.play(FadeIn(Mobject(form1, form2, pronunciation)))

class IntersectionPointCorrespondances(CircleScene):
    args_list = [
        (RADIANS, range(0, 7, 2)),
    ]
    @staticmethod
    def args_to_string(*args):
        return int_list_to_string(args[1])

    def __init__(self, radians, indices, *args, **kwargs):
        assert(len(indices) == 4)
        indices.sort()
        CircleScene.__init__(self, radians, *args, **kwargs)
        intersection_point = intersection(
            (self.points[indices[0]], self.points[indices[2]]),
            (self.points[indices[1]], self.points[indices[3]])
        )
        if len(intersection_point) == 2:
            intersection_point = list(intersection_point) + [0]
        intersection_dot = Dot(intersection_point)
        intersection_dot_arrow = Arrow(intersection_point).nudge()
        self.add(intersection_dot)
        pairs = list(it.combinations(range(len(radians)), 2))
        lines_to_save = [
            self.lines[pairs.index((indices[p0], indices[p1]))]
            for p0, p1 in [(0, 2), (1, 3)]
        ]
        dots_to_save = [
            self.dots[p]
            for p in indices
        ]
        line_statement = TexMobject(r"\text{Pair of Lines}")
        dots_statement = TexMobject(r"&\text{Quadruplet of} \\ &\text{outer dots}")
        for mob in line_statement, dots_statement:
            mob.center()
            mob.scale(0.7)
            mob.shift((SPACE_WIDTH-2, SPACE_HEIGHT - 1, 0))
        fade_outs = []
        line_highlights = []
        dot_highlights = []
        dot_pointers = []
        for mob in self.mobjects:
            if mob in lines_to_save:
                line_highlights.append(Highlight(mob))
            elif mob in dots_to_save:
                dot_highlights.append(Highlight(mob))
                dot_pointers.append(Arrow(mob.get_center()).nudge())
            elif mob != intersection_dot:
                fade_outs.append(FadeOut(mob, rate_func = not_quite_there))

        self.add(intersection_dot_arrow)
        self.play(Highlight(intersection_dot))
        self.remove(intersection_dot_arrow)
        self.play(*fade_outs)
        self.dither()
        self.add(line_statement)
        self.play(*line_highlights)
        self.remove(line_statement)
        self.dither()
        self.add(dots_statement, *dot_pointers)
        self.play(*dot_highlights)
        self.remove(dots_statement, *dot_pointers)

class LinesIntersectOutside(CircleScene):
    args_list = [
        (RADIANS, [2, 4, 5, 6]),
    ]
    @staticmethod
    def args_to_string(*args):
        return int_list_to_string(args[1])

    def __init__(self, radians, indices, *args, **kwargs):
        assert(len(indices) == 4)
        indices.sort()
        CircleScene.__init__(self, radians, *args, **kwargs)
        intersection_point = intersection(
            (self.points[indices[0]], self.points[indices[1]]),
            (self.points[indices[2]], self.points[indices[3]])
        )
        intersection_point = tuple(list(intersection_point) + [0])
        intersection_dot = Dot(intersection_point)
        pairs = list(it.combinations(range(len(radians)), 2))
        lines_to_save = [
            self.lines[pairs.index((indices[p0], indices[p1]))]
            for p0, p1 in [(0, 1), (2, 3)]
        ]
        self.play(*[
            FadeOut(mob, rate_func = not_quite_there)
            for mob in self.mobjects if mob not in lines_to_save
        ])
        self.play(*[
            Transform(
                Line(self.points[indices[p0]], self.points[indices[p1]]), 
                Line(self.points[indices[p0]], intersection_point))
            for p0, p1 in [(0, 1), (3, 2)]
        ] + [ShowCreation(intersection_dot)])

class QuadrupletsToIntersections(CircleScene):
    def __init__(self, radians, *args, **kwargs):
        CircleScene.__init__(self, radians, *args, **kwargs)
        quadruplets = it.combinations(range(len(radians)), 4)
        frame_time = 1.0
        for quad in quadruplets:
            intersection_dot = Dot(intersection(
                (self.points[quad[0]], self.points[quad[2]]),
                (self.points[quad[1]], self.points[quad[3]])
            )).repeat(3)
            dot_quad = [deepcopy(self.dots[i]) for i in quad]
            for dot in dot_quad:
                dot.scale_in_place(2)
            dot_quad = Mobject(*dot_quad)
            dot_quad.highlight()
            self.add(dot_quad)
            self.dither(frame_time / 3)
            self.play(Transform(
                dot_quad,
                intersection_dot,
                run_time = 3*frame_time/2
            ))

class GraphsAndEulersFormulaJoke(Scene):
    def __init__(self, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        axes = Mobject(
            NumberLine(),
            NumberLine().rotate(np.pi / 2)
        )
        graph = ParametricFunction(
            lambda t : (10*t, ((10*t)**3 - 10*t), 0),
            expected_measure = 40.0
        )
        graph.filter_out(lambda (x, y, z) : abs(y) > SPACE_HEIGHT)
        self.add(axes)
        self.play(ShowCreation(graph), run_time = 1.0)
        eulers = TexMobject("e^{\pi i} = -1").shift((0, 3, 0))
        self.play(CounterclockwiseTransform(
            deepcopy(graph), eulers
        ))
        self.dither()
        self.remove(*self.mobjects)
        self.add(eulers)
        self.play(CounterclockwiseTransform(
            Mobject(axes, graph),
            Point((-SPACE_WIDTH, SPACE_HEIGHT, 0))
        ))
        self.play(CounterclockwiseTransform(
            eulers,
            Point((SPACE_WIDTH, SPACE_HEIGHT, 0))
        ))

class DefiningGraph(GraphScene):
    def __init__(self, *args, **kwargs):
        GraphScene.__init__(self, *args, **kwargs)
        word_center = (0, 3, 0)
        vertices_word = TextMobject("``Vertices\"").shift(word_center)
        edges_word = TextMobject("``Edges\"").shift(word_center)
        dots, lines = self.vertices, self.edges
        self.remove(*dots + lines)
        all_dots = Mobject(*dots)
        self.play(ShowCreation(all_dots))
        self.remove(all_dots)
        self.add(*dots)
        self.play(FadeIn(vertices_word))
        self.dither()
        self.remove(vertices_word)
        self.play(*[
            ShowCreation(line) for line in lines
        ])
        self.play(FadeIn(edges_word))

        #Move to new graph
        # new_graph = deepcopy(self.graph)
        # new_graph.vertices = [
        #     (v[0] + 3*random(), v[1] + 3*random(), 0)
        #     for v in new_graph.vertices
        # ]
        # new_graph_scene = GraphScene(new_graph)
        # self.play(*[
        #     Transform(m[0], m[1])
        #     for m in zip(self.mobjects, new_graph_scene.mobjects)
        # ], run_time = 7.0)

class IntersectCubeGraphEdges(GraphScene):
    args_list = []
    @staticmethod
    def args_to_string(*args):
        return ""
    def __init__(self, *args, **kwargs):
        GraphScene.__init__(self, CubeGraph(), *args, **kwargs)
        self.remove(self.edges[0], self.edges[4])
        self.play(*[
            Transform(
                Line(self.points[i], self.points[j]),
                CurvedLine(self.points[i], self.points[j]),
            )
            for i, j in [(0, 1), (5, 4)]
        ])


class DoubledEdges(GraphScene):
    def __init__(self, *args, **kwargs):
        GraphScene.__init__(self, *args, **kwargs)
        lines_to_double = self.edges[:9:3]
        crazy_lines = [
            (
                line,
                Line(line.end, line.start),
                CurvedLine(line.start, line.end) ,
                CurvedLine(line.end, line.start)
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
        self.play(*anims)
        self.dither()
        self.remove(*outward_curved_lines)

class EulersFormula(GraphScene):
    def __init__(self, *args, **kwargs):
        GraphScene.__init__(self, *args, **kwargs)
        terms = "V - E + F =2".split(" ")
        form = dict([
            (key, mob)
            for key, mob in zip(terms, TexMobjects(terms))
        ])
        for mob in form.values():
            mob.shift((0, SPACE_HEIGHT-0.7, 0))
        formula = Mobject(*[form[k] for k in form.keys() if k != "=2"])
        new_form = dict([
            (key, deepcopy(mob).shift((0, -0.7, 0)))
            for key, mob in zip(form.keys(), form.values())
        ])
        self.add(formula)
        colored_dots = [
            deepcopy(d).scale_in_place(1.5).highlight("red") 
            for d in self.dots
        ]
        colored_edges = [
            Mobject(
                Line(midpoint, start),
                Line(midpoint, end),
            ).highlight("red")
            for e in self.edges
            for start, end, midpoint in [
                (e.start, e.end, (e.start + e.end)/2.0)
            ]
        ]
        frame_time = 0.3

        self.generate_regions()
        parameters = [
            (colored_dots,  "V", "mobject", "-", "show"),
            (colored_edges, "E", "mobject", "+", "show"),
            (self.regions,  "F", "region", "=2", "show_all")
        ]
        for items, letter, item_type, symbol, mode in parameters:
            self.count(
                items,
                item_type  = item_type,
                mode       = mode,
                num_offset = new_form[letter].get_center(), 
                run_time   = frame_time*len(items)
            )
            self.dither()
            if item_type == "mobject":
                self.remove(*items)
            self.add(new_form[symbol])

class CannotDirectlyApplyEulerToMoser(CircleScene):
    def __init__(self, radians, *args, **kwargs):
        CircleScene.__init__(self, radians, *args, **kwargs)
        self.remove(self.n_equals)
        n_equals, intersection_count = TexMobject([
            r"&n = %d\\"%len(radians),
            r"&{%d \choose 4} = %d"%(len(radians), choose(len(radians), 4))
        ]).split()
        shift_val = self.n_equals.get_center() - n_equals.get_center()
        for mob in n_equals, intersection_count:
            mob.shift(shift_val)
        self.add(n_equals)
        yellow_dots  = [
            d.highlight("yellow").scale_in_place(2)
            for d in deepcopy(self.dots)
        ]
        yellow_lines = Mobject(*[
            l.highlight("yellow") for l in deepcopy(self.lines)
        ])
        self.play(*[
            ShowCreation(dot) for dot in yellow_dots
        ], run_time = 1.0)
        self.dither()
        self.remove(*yellow_dots)
        self.play(ShowCreation(yellow_lines))
        self.dither()
        self.remove(yellow_lines)
        cannot_intersect = TextMobject(r"""
            Euler's formula does not apply to \\
            graphs whose edges intersect!
            """
        )
        cannot_intersect.center()
        for mob in self.mobjects:
            mob.fade(0.3)
        self.add(cannot_intersect)
        self.dither()
        self.remove(cannot_intersect)
        for mob in self.mobjects:
            mob.fade(1/0.3)
        self.generate_intersection_dots()
        self.play(FadeIn(intersection_count), *[
            ShowCreation(dot) for dot in self.intersection_dots
        ])

class ShowMoserGraphLines(CircleScene):
    def __init__(self, radians, *args, **kwargs):
        radians = list(set(map(lambda x : x%(2*np.pi), radians)))
        radians.sort()
        CircleScene.__init__(self, radians, *args, **kwargs)
        n, plus_n_choose_4 = TexMobject(["n", "+{n \\choose 4}"]).split()
        n_choose_2, plus_2_n_choose_4, plus_n = TexMobject([
            r"{n \choose 2}",r"&+2{n \choose 4}\\",r"&+n"
        ]).split()
        for mob in n, plus_n_choose_4, n_choose_2, plus_2_n_choose_4, plus_n:
            mob.shift((SPACE_WIDTH - 2, SPACE_HEIGHT-1, 0))
        self.chop_lines_at_intersection_points()
        self.add(*self.intersection_dots)
        small_lines = [
            deepcopy(line).scale_in_place(0.5) 
            for line in self.lines
        ]

        for mobs, symbol in [
            (self.dots, n), 
            (self.intersection_dots, plus_n_choose_4),
            (self.lines, n_choose_2)
            ]:
            self.add(symbol)
            compound = Mobject(*mobs)            
            if mobs in (self.dots, self.intersection_dots):
                self.remove(*mobs)
                self.play(CounterclockwiseTransform(
                    compound,
                    deepcopy(compound).scale(1.05),
                    rate_func = there_and_back,
                    run_time = 2.0,
                ))
            else:
                compound.highlight("yellow")
                self.play(ShowCreation(compound))
                self.remove(compound)
            if mobs == self.intersection_dots:
                self.remove(n, plus_n_choose_4)

        self.play(*[
            Transform(line, small_line, run_time = 3.0)
            for line, small_line in zip(self.lines, small_lines)
        ])
        yellow_lines = Mobject(*[
            line.highlight("yellow") for line in small_lines
        ])
        self.add(plus_2_n_choose_4)
        self.play(ShowCreation(yellow_lines))
        self.dither()
        self.remove(yellow_lines)
        self.chop_circle_at_points()
        self.play(*[
            Transform(p, sp, run_time = 3.0)
            for p, sp in zip(self.circle_pieces, self.smaller_circle_pieces)
        ])
        self.add(plus_n)
        self.play(ShowCreation(Mobject(*[
            mob.highlight("yellow") for mob in self.circle_pieces
        ])))

class HowIntersectionChopsLine(CircleScene):
    args_list = [
        (RADIANS, range(0, 7, 2)),
    ]
    @staticmethod
    def args_to_string(*args):
        return int_list_to_string(args[1])

    def __init__(self, radians, indices, *args, **kwargs):
        assert(len(indices) == 4)
        indices.sort()
        CircleScene.__init__(self, radians, *args, **kwargs)
        intersection_point = intersection(
            (self.points[indices[0]], self.points[indices[2]]),
            (self.points[indices[1]], self.points[indices[3]])
        )
        if len(intersection_point) == 2:
            intersection_point = list(intersection_point) + [0]
        pairs = list(it.combinations(range(len(radians)), 2))
        lines = [
            Line(self.points[indices[p0]], self.points[indices[p1]])
            for p0, p1 in [(2, 0), (1, 3)]
        ]
        self.remove(*[
            self.lines[pairs.index((indices[p0], indices[p1]))]
            for p0, p1 in [(0, 2), (1, 3)]
        ])
        self.add(*lines)
        self.play(*[
            FadeOut(mob)
            for mob in self.mobjects
            if mob not in lines
        ])
        new_lines = [
            Line(line.start, intersection_point)
            for line in lines
        ] + [
            Line(intersection_point, line.end)
            for line in lines
        ]
        self.play(*[
            Transform(
                line, 
                Line(
                    (-3, h, 0),
                    (3, h, 0)
                ), 
                rate_func = there_and_back, 
                run_time = 3.0
            )
            for line, h in zip(lines, (-1, 1))
        ])
        self.remove(*lines)
        self.play(*[
            Transform(
                line, 
                deepcopy(line).scale(1.1).scale_in_place(1/1.1),
                run_time = 1.5
            )
            for line in new_lines
        ])


class ApplyEulerToMoser(CircleScene):
    def __init__(self, *args, **kwargs):
        radius = 2
        CircleScene.__init__(self, *args, radius = radius, **kwargs)
        self.generate_intersection_dots()
        self.chop_lines_at_intersection_points()
        self.chop_circle_at_points()
        self.generate_regions()
        for dot in self.dots + self.intersection_dots:
            dot.scale_in_place(radius / RADIUS)
        self.remove(*self.mobjects)

        V      = {}
        minus  = {}
        minus1 = {}
        E      = {}
        plus   = {}
        plus1  = {}
        plus2  = {}
        F      = {}
        equals = {}
        two    = {}
        two1   = {}
        n      = {}
        n1     = {}
        nc2    = {}
        nc4    = {}
        nc41   = {}
        dicts = [V, minus, minus1, E, plus, plus1, plus2, F, 
                 equals, two, two1, n, n1, nc2, nc4, nc41]

        V[1], minus[1], E[1], plus[1], F[1], equals[1], two[1] = \
            TexMobject(["V", "-", "E", "+", "F", "=", "2"]).split()
        F[2], equals[2], E[2], minus[2], V[2], plus[2], two[2] = \
            TexMobject(["F", "=", "E", "-", "V", "+", "2"]).split()
        F[3], equals[3], E[3], minus[3], n[3], minus1[3], nc4[3], plus[3], two[3] = \
            TexMobject(["F", "=", "E", "-", "n", "-", r"{n \choose 4}", "+", "2"]).split()
        F[4], equals[4], nc2[4], plus1[4], two1[4], nc41[4], plus2[4], n1[4], minus[4], n[4], minus1[4], nc4[4], plus[4], two[4] = \
            TexMobject(["F", "=", r"{n \choose 2}", "+", "2", r"{n \choose 4}", "+", "n","-", "n", "-", r"{n \choose 4}", "+", "2"]).split()
        F[5], equals[5], nc2[5], plus1[5], two1[5], nc41[5], minus1[5], nc4[5], plus[5], two[5] = \
            TexMobject(["F", "=", r"{n \choose 2}", "+", "2", r"{n \choose 4}", "-", r"{n \choose 4}", "+", "2"]).split()
        F[6], equals[6], nc2[6], plus1[6], nc4[6], plus[6], two[6] = \
            TexMobject(["F", "=", r"{n \choose 2}", "+", r"{n \choose 4}", "+", "2"]).split()
        F[7], equals[7], two[7], plus[7], nc2[7], plus1[7], nc4[7] = \
            TexMobject(["F", "=", "2", "+", r"{n \choose 2}", "+", r"{n \choose 4}"]).split()
        shift_val = (0, 3, 0)
        for d in dicts:
            if not d:
                continue
            main_key = d.keys()[0]
            for key in d.keys():
                d[key].shift(shift_val)
            main_center = d[main_key].get_center()
            for key in d.keys():
                d[key] = deepcopy(d[main_key]).shift(
                    d[key].get_center() - main_center
                )

        self.play(*[
            CounterclockwiseTransform(d[1], d[2], run_time = 2.0)
            for d in [V, minus, E, plus, F, equals, two]
        ])
        self.dither()
        F[1].highlight()
        self.add(*self.lines + self.circle_pieces)
        for region in self.regions:
            self.highlight_region(region)
        self.highlight_region(self.exterior, "blue")
        self.dither()
        self.reset_background()
        F[1].highlight("white")
        E[1].highlight()
        self.remove(*self.lines + self.circle_pieces)
        self.play(*[
            Transform(
                deepcopy(line),
                deepcopy(line).scale_in_place(0.5),
                run_time = 2.0,
            )
            for line in self.lines
        ] + [
            Transform(
                deepcopy(cp), scp,
                run_time = 2.0
            )
            for cp, scp in zip(self.circle_pieces, self.smaller_circle_pieces)
        ])
        self.dither()
        E[1].highlight("white")
        V[1].highlight()
        self.add(*self.dots + self.intersection_dots)
        self.remove(*self.lines + self.circle_pieces)
        self.play(*[
            Transform(
                deepcopy(dot), 
                deepcopy(dot).scale_in_place(1.4).highlight("yellow")
            )
            for dot in self.dots + self.intersection_dots
        ] + [
            Transform(
                deepcopy(line),
                deepcopy(line).fade(0.4)
            )
            for line in self.lines + self.circle_pieces
        ])
        self.dither()
        all_mobs = [mob for mob in self.mobjects]
        self.remove(*all_mobs)
        self.add(*[d[1] for d in [V, minus, E, plus, F, equals, two]])
        V[1].highlight("white")
        two[1].highlight()
        self.dither()
        self.add(*all_mobs)
        self.remove(*[d[1] for d in [V, minus, E, plus, F, equals, two]])
        self.play(
            Transform(V[2].repeat(2), Mobject(n[3], minus1[3], nc4[3])),
            *[
                Transform(d[2], d[3])
                for d in [F, equals, E, minus, plus, two]
            ]
        )
        self.dither()
        self.remove(*self.mobjects)
        self.play(
            Transform(E[3], Mobject(
                nc2[4], plus1[4], two1[4], nc41[4], plus2[4], n1[4]
            )),
            *[
                Transform(d[3], d[4])
                for d in [F, equals, minus, n, minus1, nc4, plus, two]
            ] + [
                Transform(
                    deepcopy(line),
                    deepcopy(line).scale_in_place(0.5),
                )
                for line in self.lines
            ] + [
                Transform(deepcopy(cp), scp)
                for cp, scp in zip(self.circle_pieces, self.smaller_circle_pieces)
            ],
            run_time = 2.0
        )
        self.dither()
        self.remove(*self.mobjects)
        self.play(
            Transform(
                Mobject(plus2[4], n1[4], minus[4], n[4]),
                Point((SPACE_WIDTH, SPACE_HEIGHT, 0))
            ),
            *[
                Transform(d[4], d[5])
                for d in [F, equals, nc2, plus1, two1, 
                          nc41, minus1, nc4, plus, two]
            ]
        )
        self.dither()
        self.remove(*self.mobjects)
        self.play(
            Transform(nc41[5], nc4[6]),
            Transform(two1[5],  Point(nc4[6].get_center())),
            *[
                Transform(d[5], d[6])
                for d in [F, equals, nc2, plus1, nc4, plus, two]
            ]
        )
        self.dither()
        self.remove(*self.mobjects)
        self.play(
            CounterclockwiseTransform(two[6], two[7]),
            CounterclockwiseTransform(plus[6], plus[7]),
            *[
                Transform(d[6], d[7])
                for d in [F, equals, nc2, plus1, nc4]
            ]
        )
        self.dither()
        self.add(*self.lines + self.circle_pieces)        
        for region in self.regions:
            self.highlight_region(region)
        self.dither()
        self.highlight_region(self.exterior, "blue")
        self.dither()
        self.highlight_region(self.exterior, "black")
        self.remove(two[6])
        two = two[7]
        one = TexMobject("1").shift(two.get_center())
        two.highlight("red")
        self.add(two)
        self.play(CounterclockwiseTransform(two, one))

class FormulaRelatesToPowersOfTwo(Scene):
    def __init__(self, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        pof2_range = [1, 2, 3, 4, 5, 10]
        strings = [
            [
                r"&1 + {%d \choose 2} + {%d \choose 4} ="%(n, n),
                r"1 + %d + %d ="%(choose(n, 2), choose(n, 4)),
                r"%d \\"%moser_function(n)
            ]
            for n in [1, 2, 3, 4, 5, 10]
        ]
        everything = TexMobjects(sum(strings, []), size = r"\large")
        scale_factor = 1
        for mob in everything:
            mob.scale(scale_factor)
        Mobject(*everything).show()
        forms   = everything[0::3]
        sums    = everything[1::3]
        results = everything[2::3]
        self.add(*forms)
        self.play(*[
            FadeIn(s) for s in sums
        ])
        self.dither()
        self.play(*[
            Transform(deepcopy(s), result)
            for s, result in zip(sums, results)
        ])
        powers_of_two = [
            TexMobject("2^{%d}"%(i-1)
            ).scale(scale_factor
            ).shift(result.get_center()
            ).highlight()
            for i, result in zip(pof2_range, results)
        ]
        self.dither()
        self.remove(*self.mobjects)
        self.add(*forms + sums + results)
        self.play(*[
            CounterclockwiseTransform(result, pof2)
            for result, pof2 in zip(results, powers_of_two)
        ])        

class DrawPascalsTriangle(PascalsTriangleScene):
    def __init__(self, *args, **kwargs):
        PascalsTriangleScene.__init__(self, *args, **kwargs)
        self.remove(*self.mobjects)
        self.add(self.coords_to_mobs[0][0])
        for n in range(1, nrows):
            starts  = [deepcopy(self.coords_to_mobs[n-1][0])]
            starts += [
                Mobject(
                    self.coords_to_mobs[n-1][k-1],
                    self.coords_to_mobs[n-1][k]
                )
                for k in range(1, n)
            ]
            starts.append(deepcopy(self.coords_to_mobs[n-1][n-1]))
            self.play(*[
                Transform(starts[i], self.coords_to_mobs[n][i],
                          run_time = 1.5, black_out_extra_points = False)
                for i in range(n+1)
            ])

class PascalRuleExample(PascalsTriangleScene):
    def __init__(self, nrows, *args, **kwargs):
        assert(nrows > 1)    
        PascalsTriangleScene.__init__(self, nrows, *args, **kwargs)
        self.dither()
        n = randint(2, nrows-1)
        k = randint(1, n-1)
        self.coords_to_mobs[n][k].highlight("green")
        self.dither()
        plus = TexMobject("+").scale(0.5)
        nums_above = [self.coords_to_mobs[n-1][k-1], self.coords_to_mobs[n-1][k]]
        plus.center().shift(sum(map(Mobject.get_center, nums_above)) / 2)
        self.add(plus)
        for mob in nums_above + [plus]:
            mob.highlight("yellow")
        self.dither()

class PascalsTriangleWithNChooseK(PascalsTriangleScene):
    def __init__(self, *args, **kwargs):
        PascalsTriangleScene.__init__(self, *args, **kwargs)
        self.generate_n_choose_k_mobs()
        mob_dicts = (self.coords_to_mobs, self.coords_to_n_choose_k)
        for i in [0, 1]:
            self.dither()
            self.remove(*self.mobjects)
            self.play(*[
                CounterclockwiseTransform(
                    deepcopy(mob_dicts[i][n][k]), 
                    mob_dicts[1-i][n][k]
                )
                for n, k in self.coords
            ])
            self.remove(*self.mobjects)
            self.add(*[mob_dicts[1-i][n][k] for n, k in self.coords])

class PascalsTriangleNChooseKExample(PascalsTriangleScene):
    args_list = [
        (N_PASCAL_ROWS, 5, 3),
    ]
    @staticmethod
    def args_to_string(nrows, n, k):
        return "%d_n=%d_k=%d"%(nrows, n, k)

    def __init__(self, nrows, n, k, *args, **kwargs):
        PascalsTriangleScene.__init__(self, nrows, *args, **kwargs)
        dither_time = 0.5
        triangle_terms = [self.coords_to_mobs[a][b] for a, b in self.coords]
        formula_terms = left, n_mob, k_mob, right = TexMobject([
            r"\left(", str(n), r"\atop %d"%k, r"\right)"
        ])
        formula_center = (SPACE_WIDTH - 1, SPACE_HEIGHT - 1, 0)
        self.remove(*triangle_terms)
        self.add(*formula_terms)
        self.dither()
        self.play(*
            [
                ShowCreation(mob) for mob in triangle_terms
            ]+[
                ApplyMethod(mob.shift, formula_center)
                for mob in formula_terms
            ], 
            run_time = 1.0
        )
        self.remove(n_mob, k_mob)
        for a in range(n+1):
            row = [self.coords_to_mobs[a][b] for b in range(a+1)]
            a_mob = TexMobject(str(a))
            a_mob.shift(n_mob.get_center())
            a_mob.highlight("green")
            self.add(a_mob)
            for mob in row:
                mob.highlight("green")
            self.dither(dither_time)
            if a < n:
                for mob in row:
                    mob.highlight("white")
                self.remove(a_mob)
        self.dither()
        for b in range(k+1):
            b_mob = TexMobject(str(b))
            b_mob.shift(k_mob.get_center())
            b_mob.highlight("yellow")
            self.add(b_mob)
            self.coords_to_mobs[n][b].highlight("yellow")
            self.dither(dither_time)
            if b < k:
                self.coords_to_mobs[n][b].highlight("green")
                self.remove(b_mob)
        self.play(*[
            ApplyMethod(mob.fade, 0.2)
            for mob in triangle_terms
            if mob != self.coords_to_mobs[n][k]
        ])
        self.dither()

class PascalsTriangleSumRows(PascalsTriangleScene):
    def __init__(self, *args, **kwargs):
        PascalsTriangleScene.__init__(self, *args, **kwargs)
        pluses          = []
        powers_of_two   = []
        equalses        = []
        powers_of_two_symbols = []
        plus = TexMobject("+")
        desired_plus_width = self.coords_to_mobs[0][0].get_width()
        if plus.get_width() > desired_plus_width:
            plus.scale(desired_plus_width / plus.get_width())
        for n, k in self.coords:
            if k == 0:
                continue
            new_plus = deepcopy(plus)
            new_plus.center().shift(self.coords_to_mobs[n][k].get_center())
            new_plus.shift((-self.cell_width / 2.0, 0, 0))
            pluses.append(new_plus)
        equals = TexMobject("=")
        equals.scale(min(1, 0.7 * self.cell_height / equals.get_width()))
        for n in range(self.nrows):
            new_equals = deepcopy(equals)
            pof2 = TexMobjects(str(2**n))
            symbol = TexMobject("2^{%d}"%n)
            desired_center = np.array((
                self.diagram_width / 2.0, 
                self.coords_to_mobs[n][0].get_center()[1],
                0
            ))
            new_equals.shift(desired_center - new_equals.get_center())
            desired_center += (1.5*equals.get_width(), 0, 0)
            scale_factor = self.coords_to_mobs[0][0].get_height() / pof2.get_height()
            for mob in pof2, symbol:
                mob.center().scale(scale_factor).shift(desired_center)
            symbol.shift((0, 0.5*equals.get_height(), 0)) #FUAH! Stupid
            powers_of_two.append(pof2)
            equalses.append(new_equals)
            powers_of_two_symbols.append(symbol)
        self.play(FadeIn(Mobject(*pluses)))
        run_time = 0.5
        to_remove = []
        for n in range(self.nrows):
            start = Mobject(*[self.coords_to_mobs[n][k] for k in range(n+1)])
            to_remove.append(start)
            self.play(
                Transform(start, powers_of_two[n]),
                FadeIn(equalses[n]),
                run_time = run_time
            )
        self.dither()
        self.remove(*to_remove)
        self.add(*powers_of_two)
        for n in range(self.nrows):
            self.play(CounterclockwiseTransform(
                powers_of_two[n], powers_of_two_symbols[n], 
                run_time = run_time
            ))
            self.remove(powers_of_two[n])
            self.add(powers_of_two_symbols[n])
    

class MoserSolutionInPascal(PascalsTriangleScene):
    args_list = [
        (N_PASCAL_ROWS, n)
        for n in range(3, 8)
    ] + [
        (BIG_N_PASCAL_ROWS, 10)
    ]
    @staticmethod
    def args_to_string(nrows, n):
        return "%d_n=%d"%(nrows,n)

    def __init__(self, nrows, n, *args, **kwargs):
        PascalsTriangleScene.__init__(self, nrows, *args, **kwargs)
        term_color = "green"
        self.generate_n_choose_k_mobs()
        self.remove(*[self.coords_to_mobs[n0][k0] for n0, k0 in self.coords])
        terms = one, plus0, n_choose_2, plus1, n_choose_4 = TexMobject([
            "1", "+", r"{%d \choose 2}"%n, "+", r"{%d \choose 4}"%n
        ]).split()
        target_terms = []
        for k in range(len(terms)):
            if k%2 == 0 and k <= n:
                new_term = deepcopy(self.coords_to_n_choose_k[n][k])
                new_term.highlight(term_color)
            else:
                new_term = Point(
                    self.coords_to_center(n, k)
                )
            target_terms.append(new_term)
        self.add(*terms)
        self.dither()
        self.play(*
            [
                FadeIn(self.coords_to_n_choose_k[n0][k0])
                for n0, k0 in self.coords
                if (n0, k0) not in [(n, 0), (n, 2), (n, 4)]
            ]+[
                Transform(term, target_term)
                for term, target_term in zip(terms, target_terms)
            ]
        )
        self.dither()
        term_range = range(0, min(4, n)+1, 2)
        target_terms = dict([
            (k, deepcopy(self.coords_to_mobs[n][k]).highlight(term_color))
            for k in term_range
        ])
        self.play(*
            [
                CounterclockwiseTransform(
                    self.coords_to_n_choose_k[n0][k0],
                    self.coords_to_mobs[n0][k0]
                )
                for n0, k0 in self.coords
                if (n0, k0) not in [(n, k) for k in term_range]
            ]+[
                CounterclockwiseTransform(terms[k], target_terms[k])
                for k in term_range
            ]
        )
        self.dither()
        for k in term_range:
            if k == 0:
                above_terms = [self.coords_to_n_choose_k[n-1][k]]
            elif k == n:
                above_terms = [self.coords_to_n_choose_k[n-1][k-1]]
            else:
                above_terms = [
                    self.coords_to_n_choose_k[n-1][k-1],
                    self.coords_to_n_choose_k[n-1][k],
                ]
            self.add(self.coords_to_mobs[n][k])
            self.play(Transform(
                terms[k], 
                Mobject(*above_terms).highlight(term_color)
            ))
            self.remove(*above_terms)
        self.dither()
        terms_sum = TexMobject(str(moser_function(n)))
        terms_sum.shift((SPACE_WIDTH-1, terms[0].get_center()[1], 0))
        terms_sum.highlight(term_color)
        self.play(Transform(Mobject(*terms), terms_sum))

class RotatingPolyhedra(Scene):
    args_list = [
        ([Cube, Dodecahedron],)
    ]
    @staticmethod
    def args_to_string(class_list):
        return "".join([c.__name__ for c in class_list])

    def __init__(self, polyhedra_classes, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        rot_kwargs = {
            "radians"  : np.pi / 2,
            "run_time" : 5.0,
            "axis"     : [0, 1, 0]
        }
        polyhedra = [
            Class().scale(1.5).shift((1, 0, 0))
            for Class in polyhedra_classes
        ]
        curr_mob = polyhedra.pop()
        for mob in polyhedra:
            self.play(TransformAnimations(
                Rotating(curr_mob, **rot_kwargs),
                Rotating(mob, **rot_kwargs)
            ))
            for m in polyhedra:
                m.rotate(rot_kwargs["radians"], rot_kwargs["axis"])
        self.play(Rotating(curr_mob, **rot_kwargs))

class ExplainNChoose2Formula(Scene):
    args_list = [(7,2,6)]
    @staticmethod
    def args_to_string(n, a, b):
        return "n=%d_a=%d_b=%d"%(n, a, b)

    def __init__(self, n, a, b, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        r_paren, a_mob, comma, b_mob, l_paren = TexMobjects(
            ("( %d , %d )"%(a, b)).split(" ")
        )
        parens = Mobject(r_paren, comma, l_paren)
        nums = [TexMobject(str(k)) for k in range(1, n+1)]
        height = 1.5*nums[0].get_height()
        for x in range(n):
            nums[x].shift((0, x*height, 0))
        nums_compound = Mobject(*nums)
        nums_compound.shift(a_mob.get_center() - nums[0].get_center())
        n_mob, n_minus_1, over_2 = TexMobject([
            str(n), "(%d-1)"%n, r"\over{2}"
        ]).split()
        for part in n_mob, n_minus_1, over_2:
            part.shift((SPACE_WIDTH-1.5, SPACE_HEIGHT-1, 0))

        self.add(parens, n_mob)
        up_unit = np.array((0, height, 0))
        self.play(ApplyMethod(nums_compound.shift, -(n-1)*up_unit))
        self.play(ApplyMethod(nums_compound.shift, (n-a)*up_unit))
        self.remove(nums_compound)
        nums = nums_compound.split()
        a_mob = nums.pop(a-1)
        nums_compound = Mobject(*nums)
        self.add(a_mob, nums_compound)
        self.dither()        
        right_shift = b_mob.get_center() - a_mob.get_center()
        right_shift[1] = 0
        self.play(
            ApplyMethod(nums_compound.shift, right_shift),
            FadeIn(n_minus_1)
        )
        self.play(ApplyMethod(nums_compound.shift, (a-b)*up_unit))
        self.remove(nums_compound)
        nums = nums_compound.split()
        b_mob = nums.pop(b-2 if a < b else b-1)
        self.add(b_mob)
        self.play(*[
            CounterclockwiseTransform(
                mob, 
                Point(mob.get_center()).highlight("black")
            )
            for mob in nums
        ])
        self.play(*[
            ApplyMethod(mob.shift, (0, 1, 0))
            for mob in parens, a_mob, b_mob
        ])
        parens_copy = deepcopy(parens).shift((0, -2, 0))
        a_center = a_mob.get_center()
        b_center = b_mob.get_center()
        a_copy = deepcopy(a_mob).center().shift(b_center - (0, 2, 0))
        b_copy = deepcopy(b_mob).center().shift(a_center - (0, 2, 0))
        self.add(over_2, deepcopy(a_mob), deepcopy(b_mob))
        self.play(
            CounterclockwiseTransform(a_mob, a_copy),
            CounterclockwiseTransform(b_mob, b_copy),
            FadeIn(parens_copy),
            FadeIn(TextMobject("is considered the same as"))
        )

class ExplainNChoose4Formula(Scene):
    args_list = [(7,)]
    @staticmethod
    def args_to_string(n):
        return "n=%d"%n

    def __init__(self, n, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        # quad = list(it.combinations(range(1,n+1), 4))[randint(0, choose(n, 4)-1)]
        quad = (4, 2, 5, 1)
        tuple_mobs = TexMobjects(
            ("( %d , %d , %d , %d )"%quad).split(" ")
        )
        quad_mobs = tuple_mobs[1::2]
        parens = Mobject(*tuple_mobs[0::2])
        form_mobs = TexMobject([
            str(n), "(%d-1)"%n, "(%d-2)"%n,"(%d-3)"%n,
            r"\over {4 \cdot 3 \cdot 2 \cdot 1}"
        ]).split()
        form_mobs = Mobject(*form_mobs).scale(0.7).shift((4, 3, 0)).split()
        nums = [TexMobject(str(k)) for k in range(1, n+1)]
        height = 1.5*nums[0].get_height()
        for x in range(n):
            nums[x].shift((0, x*height, 0))
        nums_compound = Mobject(*nums)
        nums_compound.shift(quad_mobs[0].get_center() - nums[0].get_center())
        curr_num = 1 
        self.add(parens)
        up_unit = np.array((0, height, 0))
        for i in range(4):
            self.add(form_mobs[i])
            self.play(ApplyMethod(
                nums_compound.shift, (curr_num-quad[i])*up_unit))
            self.remove(nums_compound)
            nums = nums_compound.split()
            chosen = nums[quad[i]-1]
            nums[quad[i]-1] = Point(chosen.get_center()).highlight("black")
            nums_compound = Mobject(*nums)
            self.add(chosen)
            if i < 3:
                right_shift = quad_mobs[i+1].get_center() - chosen.get_center()
                right_shift[1] = 0
                self.play(
                    ApplyMethod(nums_compound.shift, right_shift)
                )
            else:
                self.play(*[
                    CounterclockwiseTransform(
                        mob, 
                        Point(mob.get_center()).highlight("black")
                    )
                    for mob in nums
                ])
            curr_num = quad[i]
        self.remove(*self.mobjects)
        num_perms_explain = TextMobject(
            r"There are $(4 \cdot 3 \cdot 2 \cdot 1)$ total permutations"
        ).shift((0, -2, 0))
        self.add(parens, num_perms_explain, *form_mobs)
        perms = list(it.permutations(range(4)))        
        for count in range(6):
            perm = perms[randint(0, 23)]
            new_quad_mobs = [
                deepcopy(quad_mobs[i]).shift(
                    quad_mobs[perm[i]].get_center() - \
                    quad_mobs[i].get_center()
                )
                for i in range(4)
            ]
            compound_quad = Mobject(*quad_mobs)
            self.play(CounterclockwiseTransform(
                compound_quad,
                Mobject(*new_quad_mobs)
            ))
            self.remove(compound_quad)
            quad_mobs = new_quad_mobs

class IntersectionChoppingExamples(Scene):
    def __init__(self, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        pairs1 = [
            ((-1,-1, 0), (-1, 0, 0)),
            ((-1, 0, 0), (-1, 1, 0)),
            ((-2, 0, 0), (-1, 0, 0)),
            ((-1, 0, 0), ( 1, 0, 0)),
            (( 1, 0, 0), ( 2, 0, 0)),
            (( 1,-1, 0), ( 1, 0, 0)),
            (( 1, 0, 0), ( 1, 1, 0)),
        ]
        pairs2 = pairs1 + [
            (( 1, 1, 0), ( 1, 2, 0)),
            (( 0, 1, 0), ( 1, 1, 0)),
            (( 1, 1, 0), ( 2, 1, 0)),
        ]
        for pairs, exp in [(pairs1, "3 + 2(2) = 7"), 
                           (pairs2, "4 + 2(3) = 10")]:
            lines = [Line(*pair).scale(2) for pair in pairs]
            self.add(TexMobject(exp).shift((0, SPACE_HEIGHT-1, 0)))
            self.add(*lines)
            self.dither()
            self.play(*[
                Transform(line, deepcopy(line).scale(1.2).scale_in_place(1/1.2))
                for line in lines
            ])
            self.count(lines, run_time = 3.0, num_offset = ORIGIN)
            self.dither()
            self.remove(*self.mobjects)




