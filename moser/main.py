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

class CountLines(CircleScene):
    def __init__(self, radians, *args, **kwargs):
        CircleScene.__init__(self, radians, *args, **kwargs)
        #TODO, Count things explicitly?        
        text_center = (self.radius + 1, self.radius -1, 0)
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
                -(self.radius - 1), 
                self.radius - 1, 
                (2*self.radius - 2)/len(self.lines)
            )
        ]
        self.add(text)
        self.dither()
        self.animate(*[
           Transform(line1, line2, run_time = 2)
           for line1, line2 in zip(self.lines, new_lines)
        ])
        self.dither()
        self.remove(text)
        self.count(new_lines)
        anims = [FadeIn(formula)]
        for mob in self.mobjects:
            if mob == self.number: #put in during animate_count
                anims.append(Transform(mob, answer))
            else:
                anims.append(FadeOut(mob))
        self.animate(*anims, run_time = 1)

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
        #         -(self.radius - 1), 
        #         self.radius - 1, 
        #         (2*self.radius - 2)/choose(len(self.points), 4)
        #     )
        # ]
        # new_dots = CompoundMobject(*[
        #     Dot(point) for point in new_points
        # ])

        self.add(text)
        self.count(intersection_dots, "show", num_offset = (0, 0, 0))
        self.dither()
        # self.animate(Transform(intersection_dots, new_dots))
        anims = []
        for mob in self.mobjects:
            if mob == self.number: #put in during animate_count
                anims.append(Transform(mob, answer))
            else:
                anims.append(FadeOut(mob))
        anims.append(Animation(formula))
        self.animate(*anims, run_time = 1)

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
        text = tex_mobject(r"\text{This region disappears}", size = r"\large")
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
        self.animate(*[
            Transform(mob1, mob2, run_time = DEFAULT_ANIMATION_RUN_TIME)
            for mob1, mob2 in zip(self.mobjects, new_self.mobjects)
        ])

class LineCorrespondsWithPair(CircleScene):
    args_list = [
        (RADIANS, 2, 5),
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
        self.animate(*[
            FadeOut(mob, alpha_func = not_quite_there) 
            for mob in self.lines + self.dots
        ])
        self.add(self.circle)
        self.animate(*[
            ScaleInPlace(mob, 3, alpha_func = there_and_back) 
            for mob in (dot0, dot1)
        ])
        self.animate(Transform(line, dot0))

class IllustrateNChooseK(Scene):
    args_list = [
        (7, 2),
        (6, 4),
    ]
    @staticmethod
    def args_to_string(*args):
        return int_list_to_string(args)

    def __init__(self, n, k, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
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

        self.add(*nrange_mobs)
        self.dither()
        run_time = 6.0
        frame_time = run_time / len(tuples)
        for tup, count in zip(tuples, it.count()):
            count_mob = tex_mobject(str(count+1))
            count_mob.center().shift(count_center)
            self.add(count_mob)
            tuple_copy = CompoundMobject(*[nrange_mobs[index-1] for index in tup])
            tuple_copy.highlight()
            self.add(tuple_copy)
            self.add(tuple_mobs[count])
            self.dither(frame_time)
            self.remove(count_mob)
            self.remove(tuple_copy)
        self.add(count_mob)
        self.animate(FadeIn(CompoundMobject(form1, form2)))

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
        for mob in self.mobjects:
            if mob in lines_to_save:
                line_highlights.append(Highlight(mob))
            elif mob in dots_to_save:
                dot_highlights.append(Highlight(mob))
                dot_pointers.append(Arrow(mob.get_center()).nudge())
            elif mob != intersection_dot:
                fade_outs.append(FadeOut(mob, alpha_func = not_quite_there))

        self.add(intersection_dot_arrow)
        self.animate(Highlight(intersection_dot))
        self.remove(intersection_dot_arrow)
        self.animate(*fade_outs)
        self.dither()
        self.add(line_statement)
        self.animate(*line_highlights)
        self.remove(line_statement)
        self.dither()
        self.add(dots_statement, *dot_pointers)
        self.animate(*dot_highlights)
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
        self.animate(*[
            FadeOut(mob, alpha_func = not_quite_there)
            for mob in self.mobjects if mob not in lines_to_save
        ])
        self.animate(*[
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
            dot_quad = CompoundMobject(*dot_quad)
            dot_quad.highlight()
            self.add(dot_quad)
            self.dither(frame_time / 3)
            self.animate(Transform(
                dot_quad,
                intersection_dot,
                run_time = 3*frame_time/2
            ))

class DefiningGraph(GraphScene):
    def __init__(self, *args, **kwargs):
        GraphScene.__init__(self, *args, **kwargs)
        dots, lines = self.vertices, self.edges
        self.remove(*dots + lines)
        all_dots = CompoundMobject(*dots)
        self.animate(ShowCreation(all_dots))
        self.remove(all_dots)
        self.add(*dots)
        self.dither()
        self.animate(*[
            ShowCreation(line) for line in lines
        ])

        #Move to new graph
        new_graph = deepcopy(self.graph)
        new_graph["vertices"] = [
            (v[0] + 3*random(), v[1] + 3*random(), 0)
            for v in new_graph["vertices"]
        ]
        new_graph_scene = GraphScene(new_graph)
        self.animate(*[
            Transform(m[0], m[1])
            for m in zip(self.mobjects, new_graph_scene.mobjects)
        ], run_time = 7.0)

class DoubledEdges(GraphScene):
    def __init__(self, *args, **kwargs):
        GraphScene.__init__(self, *args, **kwargs)
        lines_to_double = self.edges[:9:3]
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
        self.animate(*anims)
        self.dither()
        self.remove(*outward_curved_lines)

class EulersFormula(GraphScene):
    def __init__(self, *args, **kwargs):
        GraphScene.__init__(self, *args, **kwargs)
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
        self.add(formula)
        colored_dots = [
            deepcopy(d).scale_in_place(1.5).highlight("red") 
            for d in self.dots
        ]
        colored_edges = [
            deepcopy(e).highlight("red")
            for e in self.edges
        ]
        frame_time = 0.3

        self.generate_regions()
        parameters = [
            (colored_dots,  "V", "mobject", "-", "show_creation"),
            (colored_edges, "E", "mobject", "+", "show_creation"),
            (self.regions,    "F", "region", "=2", "show_all")
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
        self.reset_background()

class CannotDirectlyApplyEulerToMoser(CircleScene):
    def __init__(self, radians, *args, **kwargs):
        CircleScene.__init__(self, radians, *args, **kwargs)
        self.remove(self.n_equals)
        n_equals, intersection_count = tex_mobjects([
            r"&n = %d\\"%len(radians),
            r"&{%d \choose 4} = %d"%(len(radians), choose(len(radians), 4))
        ])
        shift_val = self.n_equals.get_center() - n_equals.get_center()
        for mob in n_equals, intersection_count:
            mob.shift(shift_val)
        self.add(n_equals)
        yellow_dots  = [d.highlight("yellow") for d in deepcopy(self.dots)]
        yellow_lines = [l.highlight("yellow") for l in deepcopy(self.lines)]
        self.animate(*[
            ShowCreation(dot) for dot in yellow_dots
        ], run_time = 1.0)
        self.dither()
        self.remove(*yellow_dots)
        self.animate(*[
            ShowCreation(line) for line in yellow_lines
        ], run_time = 1.0)
        self.dither()
        self.remove(yellow_lines)
        cannot_intersect = text_mobject(r"""
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
        self.animate(FadeIn(intersection_count), *[
            ShowCreation(dot) for dot in self.intersection_dots
        ])

class ShowMoserGraphLines(CircleScene):
    def __init__(self, radians, *args, **kwargs):
        radians = list(set(map(lambda x : x%(2*np.pi), radians)))
        radians.sort()
        CircleScene.__init__(self, radians, *args, **kwargs)

        self.chop_lines_at_intersection_points()
        self.add(*self.intersection_dots)
        small_lines = [
            deepcopy(line).scale_in_place(0.5) 
            for line in self.lines
        ]
        self.animate(*[
            Transform(line, small_line, run_time = 3.0)
            for line, small_line in zip(self.lines, small_lines)
        ])
        self.count(self.lines, color = "yellow", 
                 run_time = 9.0, num_offset = (0, 0, 0))
        self.dither()
        self.remove(self.number)
        self.chop_circle_at_points()
        self.animate(*[
            Transform(p, sp, run_time = 3.0)
            for p, sp in zip(self.circle_pieces, self.smaller_circle_pieces)
        ])
        self.count(self.circle_pieces, color = "yellow", 
                 run_time = 2.0, num_offset = (0, 0, 0))

class ApplyEulerToMoser(Scene):
    def __init__(self, *args, **kwargs):
        #Boy is this an ugly implementation..., maybe you should
        #make a generic formula manipuating module
        Scene.__init__(self, *args, **kwargs)
        expressions = []
        for i in range(4):
            V_exp = "V" if i < 2 else r"\left(n + {n \choose 4} \right)"
            E_exp = "E" if i < 3 else r"\left({n \choose 2} + 2{n \choose 4}\right)"
            if i == 0:
                form = [V_exp, "-", E_exp, "+", "F", "=", "2"]
            else:
                form = ["F", "&=", E_exp, "-", V_exp, "+", "2"]
            if i == 3:
                form += [r"\\&=",r"{n \choose 4} + {n \choose 2}+", "2"]
            expressions.append(tex_mobjects(form))
        final_F_pos = (-SPACE_WIDTH+1, 0, 0)
        for exp in expressions:
            shift_val = final_F_pos - exp[0].get_center()
            for mob in exp:
                mob.shift(shift_val)
        #rearange first expression            
        expressions[0] = [
            expressions[0][x] 
            for x in [4, 5, 2, 1, 0, 3, 6] #TODO, Better way in general for rearrangements?
        ]
        for i in range(3):
            self.remove(*self.mobjects)
            self.add(*expressions[i])
            self.dither()
            self.animate(*[
                SemiCircleTransform(x, y, run_time = 2) if i == 0 else Transform(x, y)
                for x, y in zip(expressions[i], expressions[i+1])
            ])
        self.dither()
        equals, simplified_exp = expressions[-1][-3], expressions[-1][-2:]
        self.animate(*[
            FadeIn(mob)
            for mob in [equals] + simplified_exp
        ])
        self.remove(*self.mobjects)
        shift_val = -CompoundMobject(*simplified_exp).get_center()
        self.animate(*[
            ApplyMethod((Mobject.shift, shift_val), mob)
            for mob in simplified_exp
        ])
        self.dither()
        one, two = tex_mobject("1"), simplified_exp[-1]
        one.center().shift(two.get_center())
        two.highlight()
        self.dither()
        self.animate(SemiCircleTransform(two, one))

class DrawPascalsTriangle(PascalsTriangleScene):
    def __init__(self, *args, **kwargs):
        PascalsTriangleScene.__init__(self, *args, **kwargs)
        self.remove(*self.mobjects)
        self.add(self.coords_to_mobs[0][0])
        for n in range(1, nrows):
            starts  = [deepcopy(self.coords_to_mobs[n-1][0])]
            starts += [
                CompoundMobject(
                    self.coords_to_mobs[n-1][k-1],
                    self.coords_to_mobs[n-1][k]
                )
                for k in range(1, n)
            ]
            starts.append(deepcopy(self.coords_to_mobs[n-1][n-1]))
            self.animate(*[
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
        plus = tex_mobject("+").scale(0.5)
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
            self.animate(*[
                SemiCircleTransform(
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
        formula_terms = left, n_mob, k_mob, right = tex_mobject([
            r"\left(", str(n), r"\atop %d"%k, r"\right)"
        ])
        formula_center = (SPACE_WIDTH - 1, SPACE_HEIGHT - 1, 0)
        self.remove(*triangle_terms)
        self.add(*formula_terms)
        self.dither()
        self.animate(*
            [
                ShowCreation(mob) for mob in triangle_terms
            ]+[
                ApplyMethod((Mobject.shift, formula_center), mob)
                for mob in formula_terms
            ], 
            run_time = 1.0
        )
        self.remove(n_mob, k_mob)
        for a in range(n+1):
            row = [self.coords_to_mobs[a][b] for b in range(a+1)]
            a_mob = tex_mobject(str(a))
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
            b_mob = tex_mobject(str(b))
            b_mob.shift(k_mob.get_center())
            b_mob.highlight("yellow")
            self.add(b_mob)
            self.coords_to_mobs[n][b].highlight("yellow")
            self.dither(dither_time)
            if b < k:
                self.coords_to_mobs[n][b].highlight("green")
                self.remove(b_mob)
        self.animate(*[
            ApplyMethod((Mobject.fade, 0.2), mob)
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
        plus = tex_mobject("+")
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
        equals = tex_mobject("=")
        equals.scale(min(1, 0.7 * self.cell_height / equals.get_width()))
        for n in range(self.nrows):
            new_equals = deepcopy(equals)
            pof2 = tex_mobjects(str(2**n))
            symbol = tex_mobject("2^{%d}"%n)
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
        self.animate(FadeIn(CompoundMobject(*pluses)))
        run_time = 0.5
        to_remove = []
        for n in range(self.nrows):
            start = CompoundMobject(*[self.coords_to_mobs[n][k] for k in range(n+1)])
            to_remove.append(start)
            self.animate(
                Transform(start, powers_of_two[n]),
                FadeIn(equalses[n]),
                run_time = run_time
            )
        self.dither()
        self.remove(*to_remove)
        self.add(*powers_of_two)
        for n in range(self.nrows):
            self.animate(SemiCircleTransform(
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
        terms = one, plus0, n_choose_2, plus1, n_choose_4 = tex_mobjects([
            "1", "+", r"{%d \choose 2}"%n, "+", r"{%d \choose 4}"%n
        ])
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
        self.animate(*
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
        self.animate(*
            [
                SemiCircleTransform(
                    self.coords_to_n_choose_k[n0][k0],
                    self.coords_to_mobs[n0][k0]
                )
                for n0, k0 in self.coords
                if (n0, k0) not in [(n, k) for k in term_range]
            ]+[
                SemiCircleTransform(terms[k], target_terms[k])
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
            self.animate(Transform(
                terms[k], 
                CompoundMobject(*above_terms).highlight(term_color)
            ))
            self.remove(*above_terms)
        self.dither()
        terms_sum = tex_mobject(str(moser_function(n)))
        terms_sum.shift((SPACE_WIDTH-1, terms[0].get_center()[1], 0))
        terms_sum.highlight(term_color)
        self.animate(Transform(CompoundMobject(*terms), terms_sum))



##################################################

if __name__ == "__main__":
    scene_classes = [
        pair[1]
        for pair in inspect.getmembers(
            sys.modules[__name__], 
            lambda obj : inspect.isclass(obj) and issubclass(obj, Scene)
        )
    ]
    command_line_create_scene(sys.argv[1:], scene_classes, MOVIE_PREFIX)



