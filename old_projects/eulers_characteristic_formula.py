#!/usr/bin/env python


import numpy as np
import itertools as it
from copy import deepcopy
import sys


from animation import *
from mobject import *
from constants import *
from mobject.region import  *
import displayer as disp
from scene.scene import Scene, GraphScene
from scene.graphs import *
from .moser_main import EulersFormula
from script_wrapper import command_line_create_scene

MOVIE_PREFIX = "ecf_graph_scenes/"
RANDOLPH_SCALE_FACTOR = 0.3
EDGE_ANNOTATION_SCALE_FACTOR = 0.7
DUAL_CYCLE = [3, 4, 5, 6, 1, 0, 2, 3]

class EulersFormulaWords(Scene):
    def construct(self):
        self.add(TexMobject("V-E+F=2"))

class TheTheoremWords(Scene):
    def construct(self):
        self.add(TextMobject("The Theorem:"))

class ProofAtLastWords(Scene):
    def construct(self):
        self.add(TextMobject("The Proof At Last..."))

class DualSpanningTreeWords(Scene):
    def construct(self):
        self.add(TextMobject("Spanning trees have duals too!"))

class PreferOtherProofDialogue(Scene):
    def construct(self):
        teacher = Face("talking").shift(2*LEFT)
        student = Face("straight").shift(2*RIGHT)
        teacher_bubble = SpeechBubble(LEFT).speak_from(teacher)
        student_bubble = SpeechBubble(RIGHT).speak_from(student)
        teacher_bubble.write("Look at this \\\\ elegant proof!")
        student_bubble.write("I prefer the \\\\ other proof.")

        self.add(student, teacher, teacher_bubble, teacher_bubble.text)
        self.wait(2)
        self.play(Transform(
            Dot(student_bubble.tip).set_color("black"),
            Mobject(student_bubble, student_bubble.text)
        ))
        self.wait(2)
        self.remove(teacher_bubble.text)
        teacher_bubble.write("Does that make this \\\\ any less elegant?")
        self.add(teacher_bubble.text)
        self.wait(2)

class IllustrateDuality(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        self.generate_dual_graph()

        self.add(TextMobject("Duality").to_edge(UP))
        self.remove(*self.vertices)
        def special_alpha(t):
            if t > 0.5:
                t = 1 - t
            if t < 0.25:
                return smooth(4*t)
            else:
                return 1
        kwargs = {
            "run_time" : 5.0,
            "rate_func" : special_alpha
        }
        self.play(*[
            Transform(*edge_pair, **kwargs)
            for edge_pair in zip(self.edges, self.dual_edges)
        ] + [
            Transform(
                Mobject(*[
                    self.vertices[index]
                    for index in cycle
                ]),
                dv,
                **kwargs
            )
            for cycle, dv in zip(
                self.graph.region_cycles, 
                self.dual_vertices
            )
        ])
        self.wait()

class IntroduceGraph(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        tweaked_graph = deepcopy(self.graph)
        for index in 2, 4:
            tweaked_graph.vertices[index] += 2.8*RIGHT + 1.8*DOWN
        tweaked_self = GraphScene(tweaked_graph)
        edges_to_remove = [
            self.edges[self.graph.edges.index(pair)]
            for pair in [(4, 5), (0, 5), (1, 5), (7, 1), (8, 3)]
        ]

        connected, planar, graph = TextMobject([
            "Connected ", "Planar ", "Graph"
        ]).to_edge(UP).split()
        not_okay = TextMobject("Not Okay").set_color("red")
        planar_explanation = TextMobject("""
            (``Planar'' just means we can draw it without
             intersecting lines)
        """, size = "\\small")
        planar_explanation.shift(planar.get_center() + 0.5*DOWN)

        self.draw_vertices()
        self.draw_edges()
        self.clear()
        self.add(*self.vertices + self.edges)
        self.wait()
        self.add(graph)
        self.wait()
        kwargs = {
            "rate_func" : there_and_back,
            "run_time"   : 5.0
        }
        self.add(not_okay)
        self.play(*[
            Transform(*pair, **kwargs)
            for pair in zip(
                self.edges + self.vertices, 
                tweaked_self.edges + tweaked_self.vertices,
            )
        ])
        self.remove(not_okay)
        self.add(planar, planar_explanation)
        self.wait(2)
        self.remove(planar_explanation)
        self.add(not_okay)
        self.remove(*edges_to_remove)
        self.play(ShowCreation(
            Mobject(*edges_to_remove),
            rate_func = lambda t : 1 - t,
            run_time = 1.0
        ))
        self.wait(2)
        self.remove(not_okay)
        self.add(connected, *edges_to_remove)
        self.wait()


class OldIntroduceGraphs(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        self.draw_vertices()        
        self.draw_edges()
        self.wait()
        self.clear()
        self.add(*self.edges)
        self.replace_vertices_with(Face().scale(0.4))
        friends = TextMobject("Friends").scale(EDGE_ANNOTATION_SCALE_FACTOR)
        self.annotate_edges(friends.shift((0, friends.get_height()/2, 0)))
        self.play(*[
            CounterclockwiseTransform(vertex, Dot(point))
            for vertex, point in zip(self.vertices, self.points)
        ]+[
            Transform(ann, line)
            for ann, line in zip(
                self.edge_annotations, 
                self.edges
            )
        ])
        self.wait()

class PlanarGraphDefinition(Scene):
    def construct(self):
        Not, quote, planar, end_quote = TextMobject([
            "Not \\\\", "``", "Planar", "''",
            # "no matter how \\\\ hard you try"
        ]).split()
        shift_val = Mobject(Not, planar).to_corner().get_center()
        Not.set_color("red").shift(shift_val)
        graphs = [
            Mobject(*GraphScene(g).mobjects)
            for g in [
                CubeGraph(), 
                CompleteGraph(5),
                OctohedronGraph()
            ]
        ]

        self.add(quote, planar, end_quote)
        self.wait()
        self.play(
            FadeOut(quote),
            FadeOut(end_quote),
            ApplyMethod(planar.shift, shift_val),
            FadeIn(graphs[0]),
            run_time = 1.5
        )
        self.wait()
        self.remove(graphs[0])
        self.add(graphs[1])
        planar.set_color("red")
        self.add(Not)
        self.wait(2)
        planar.set_color("white")
        self.remove(Not)
        self.remove(graphs[1])
        self.add(graphs[2])
        self.wait(2)


class TerminologyFromPolyhedra(GraphScene):
    args_list = [(CubeGraph(),)]
    def construct(self):
        GraphScene.construct(self)
        rot_kwargs = {
            "radians" : np.pi / 3,
            "run_time" : 5.0
        }
        vertices = [
            point / 2 + OUT if abs(point[0]) == 2 else point + IN
            for point in self.points
        ]
        cube = Mobject(*[
            Line(vertices[edge[0]], vertices[edge[1]])
            for edge in self.graph.edges
        ])
        cube.rotate(-np.pi/3, [0, 0, 1])
        cube.rotate(-np.pi/3, [0, 1, 0])
        dots_to_vertices = TextMobject("Dots $\\to$ Vertices").to_corner()
        lines_to_edges = TextMobject("Lines $\\to$ Edges").to_corner()
        regions_to_faces = TextMobject("Regions $\\to$ Faces").to_corner()
        
        self.clear()
        # self.play(TransformAnimations(
        #     Rotating(Dodecahedron(), **rot_kwargs),
        #     Rotating(cube, **rot_kwargs)  
        # ))
        self.play(Rotating(cube, **rot_kwargs))
        self.clear()
        self.play(*[
            Transform(l1, l2)
            for l1, l2 in zip(cube.split(), self.edges)
        ])
        self.wait()
        self.add(dots_to_vertices)
        self.play(*[
            ShowCreation(dot, run_time = 1.0)
            for dot in self.vertices
        ])
        self.wait(2)
        self.remove(dots_to_vertices, *self.vertices)
        self.add(lines_to_edges)
        self.play(ApplyMethod(
            Mobject(*self.edges).set_color, "yellow"
        ))
        self.wait(2)
        self.clear()
        self.add(*self.edges)
        self.add(regions_to_faces)
        self.generate_regions()
        for region in self.regions:
            self.set_color_region(region)
        self.wait(3.0)


class ThreePiecesOfTerminology(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        terms = cycles, spanning_trees, dual_graphs = [
            TextMobject(phrase).shift(y*UP).to_edge()
            for phrase, y in [
                ("Cycles", 3),
                ("Spanning Trees", 1),
                ("Dual Graphs", -1),
            ]
        ]
        self.generate_spanning_tree()
        scale_factor = 1.2       
        def accent(mobject, color = "yellow"):
            return mobject.scale_in_place(scale_factor).set_color(color)
        def tone_down(mobject):
            return mobject.scale_in_place(1.0/scale_factor).set_color("white")

        self.add(accent(cycles))
        self.trace_cycle(run_time = 1.0)
        self.wait()
        tone_down(cycles)
        self.remove(self.traced_cycle)

        self.add(accent(spanning_trees))
        self.play(ShowCreation(self.spanning_tree), run_time = 1.0)
        self.wait()
        tone_down(spanning_trees)
        self.remove(self.spanning_tree)

        self.add(accent(dual_graphs, "red"))
        self.generate_dual_graph()
        for mob in self.mobjects:
            mob.fade
        self.play(*[
            ShowCreation(mob, run_time = 1.0)
            for mob in self.dual_vertices + self.dual_edges
        ])
        self.wait()

        self.clear()
        self.play(ApplyMethod(
            Mobject(*terms).center
        ))
        self.wait()

class WalkingRandolph(GraphScene):
    args_list = [
        (SampleGraph(), [0, 1, 7, 8]),
    ]
    @staticmethod
    def args_to_string(graph, path):
        return str(graph) + "".join(map(str, path))

    def __init__(self, graph, path, *args, **kwargs):
        self.path = path
        GraphScene.__init__(self, graph, *args, **kwargs)

    def construct(self):
        GraphScene.construct(self)
        point_path = [self.points[i] for i in self.path]
        randy = Randolph()
        randy.scale(RANDOLPH_SCALE_FACTOR)
        randy.move_to(point_path[0])
        for next, last in zip(point_path[1:], point_path):
            self.play(
                WalkPiCreature(randy, next),
                ShowCreation(Line(last, next).set_color("yellow")),
                run_time = 2.0
            )
        self.randy = randy


class PathExamples(GraphScene):
    args_list = [(SampleGraph(),)]
    def construct(self):
        GraphScene.construct(self)
        paths = [
            (1, 2, 4, 5, 6),
            (6, 7, 1, 3),
        ]
        non_paths = [
            [(0, 1), (7, 8), (5, 6),],
            [(5, 0), (0, 2), (0, 1)],
        ]
        valid_path = TextMobject("Valid \\\\ Path").set_color("green")
        not_a_path = TextMobject("Not a \\\\ Path").set_color("red")
        for mob in valid_path, not_a_path:
            mob.to_edge(UP)
        kwargs = {"run_time" : 1.0}
        for path, non_path in zip(paths, non_paths):
            path_lines = Mobject(*[
                Line(
                    self.points[path[i]], 
                    self.points[path[i+1]]
                ).set_color("yellow")
                for i in range(len(path) - 1)
            ])
            non_path_lines = Mobject(*[
                Line(
                    self.points[pp[0]],
                    self.points[pp[1]],
                ).set_color("yellow")
                for pp in non_path
            ])

            self.remove(not_a_path)
            self.add(valid_path)
            self.play(ShowCreation(path_lines, **kwargs))
            self.wait(2)
            self.remove(path_lines)

            self.remove(valid_path)
            self.add(not_a_path)
            self.play(ShowCreation(non_path_lines, **kwargs))
            self.wait(2)
            self.remove(non_path_lines)

class IntroduceCycle(WalkingRandolph):
    args_list = [
        (SampleGraph(), [0, 1, 3, 2, 0])
    ]
    def construct(self):
        WalkingRandolph.construct(self)
        self.remove(self.randy)
        encompassed_cycles = [c for c in self.graph.region_cycles if set(c).issubset(self.path)]
        regions = [
            self.region_from_cycle(cycle)
            for cycle in encompassed_cycles
        ]
        for region in regions:
            self.set_color_region(region)
        self.wait()



class IntroduceRandolph(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        randy = Randolph().move_to((-3, 0, 0))
        name = TextMobject("Randolph")
        self.play(Transform(
            randy,
            deepcopy(randy).scale(RANDOLPH_SCALE_FACTOR).move_to(self.points[0]),
        ))
        self.wait()
        name.shift((0, 1, 0))
        self.add(name)
        self.wait()

class DefineSpanningTree(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        randy = Randolph()
        randy.scale(RANDOLPH_SCALE_FACTOR).move_to(self.points[0])
        dollar_signs = TextMobject("\\$\\$")
        dollar_signs.scale(EDGE_ANNOTATION_SCALE_FACTOR)
        dollar_signs = Mobject(*[
            deepcopy(dollar_signs).shift(edge.get_center())
            for edge in self.edges
        ])
        unneeded = TextMobject("unneeded!")
        unneeded.scale(EDGE_ANNOTATION_SCALE_FACTOR)
        self.generate_spanning_tree()
        def green_dot_at_index(index):
            return Dot(
                self.points[index], 
                radius = 2*Dot.DEFAULT_RADIUS,
                color = "lightgreen",
            )
        def out_of_spanning_set(point_pair):
            stip = self.spanning_tree_index_pairs
            return point_pair not in stip and \
                   tuple(reversed(point_pair)) not in stip
        
        self.add(randy)
        self.accent_vertices(run_time = 2.0)
        self.add(dollar_signs)
        self.wait(2)
        self.remove(dollar_signs)
        run_time_per_branch = 0.5        
        self.play(
            ShowCreation(green_dot_at_index(0)),
            run_time = run_time_per_branch
        )
        for pair in self.spanning_tree_index_pairs:
            self.play(ShowCreation(
                Line(
                    self.points[pair[0]], 
                    self.points[pair[1]]
                ).set_color("yellow"),
                run_time = run_time_per_branch
            ))
            self.play(ShowCreation(
                green_dot_at_index(pair[1]),
                run_time = run_time_per_branch
            ))
        self.wait(2)

        unneeded_edges = list(filter(out_of_spanning_set, self.graph.edges))
        for edge, limit in zip(unneeded_edges, list(range(5))):
            line = Line(self.points[edge[0]], self.points[edge[1]])
            line.set_color("red")
            self.play(ShowCreation(line, run_time = 1.0))
            self.add(unneeded.center().shift(line.get_center() + 0.2*UP))
            self.wait()
            self.remove(line, unneeded)

class NamingTree(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        self.generate_spanning_tree()
        self.generate_treeified_spanning_tree()
        branches = self.spanning_tree.split()
        branches_copy = deepcopy(branches)
        treeified_branches = self.treeified_spanning_tree.split()
        tree = TextMobject("``Tree''").to_edge(UP)
        spanning_tree = TextMobject("``Spanning Tree''").to_edge(UP)

        self.add(*branches)
        self.play(
            FadeOut(Mobject(*self.edges + self.vertices)),
            Animation(Mobject(*branches)),
        )
        self.clear()
        self.add(tree, *branches)
        self.wait()
        self.play(*[
            Transform(b1, b2, run_time = 2)
            for b1, b2 in zip(branches, treeified_branches)
        ])
        self.wait()
        self.play(*[
            FadeIn(mob)
            for mob in self.edges + self.vertices
        ] + [
            Transform(b1, b2, run_time = 2)
            for b1, b2 in zip(branches, branches_copy)
        ])
        self.accent_vertices(run_time = 2)
        self.remove(tree)
        self.add(spanning_tree)
        self.wait(2)

class DualGraph(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        self.generate_dual_graph()
        self.add(TextMobject("Dual Graph").to_edge(UP).shift(2*LEFT))
        self.play(*[
            ShowCreation(mob)
            for mob in self.dual_edges + self.dual_vertices
        ])
        self.wait()

class FacebookLogo(Scene):
    def construct(self):
        im = ImageMobject("facebook_full_logo", invert = False)
        self.add(im.scale(0.7))


class FacebookGraph(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        account = ImageMobject("facebook_silhouette", invert = False)
        account.scale(0.05)
        logo = ImageMobject("facebook_logo", invert = False)
        logo.scale(0.1)
        logo.shift(0.2*LEFT + 0.1*UP)
        account.add(logo).center()
        account.shift(0.2*LEFT + 0.1*UP)
        friends = TexMobject(
            "\\leftarrow \\text{friends} \\rightarrow"
        ).scale(0.5*EDGE_ANNOTATION_SCALE_FACTOR)

        self.clear()
        accounts = [
            deepcopy(account).shift(point)
            for point in self.points
        ]
        self.add(*accounts)
        self.wait()
        self.annotate_edges(friends)
        self.wait()
        self.play(*[
            CounterclockwiseTransform(account, vertex)
            for account, vertex in zip(accounts, self.vertices)
        ])
        self.wait()
        self.play(*[
            Transform(ann, edge)
            for ann, edge in zip(self.edge_annotations, self.edges)
        ])
        self.wait()

class FacebookGraphAsAbstractSet(Scene):
    def construct(self):
        names = [
            "Louis",
            "Randolph",
            "Mortimer",
            "Billy Ray",
            "Penelope",
        ]
        friend_pairs = [
            (0, 1),
            (0, 2),
            (1, 2),
            (3, 0),
            (4, 0),
            (1, 3),
            (1, 2),
        ]
        names_string = "\\\\".join(names + ["$\\vdots$"])
        friends_string = "\\\\".join([
            "\\text{%s}&\\leftrightarrow\\text{%s}"%(names[i],names[j])
            for i, j in friend_pairs
        ] + ["\\vdots"])
        names_mob = TextMobject(names_string).shift(3*LEFT)
        friends_mob = TexMobject(
            friends_string, size = "\\Large"
        ).shift(3*RIGHT)
        accounts = TextMobject("\\textbf{Accounts}")
        accounts.shift(3*LEFT).to_edge(UP)
        friendships = TextMobject("\\textbf{Friendships}")
        friendships.shift(3*RIGHT).to_edge(UP)
        lines = Mobject(
            Line(UP*FRAME_Y_RADIUS, DOWN*FRAME_Y_RADIUS),
            Line(LEFT*FRAME_X_RADIUS + 3*UP, RIGHT*FRAME_X_RADIUS + 3*UP)
        ).set_color("white")

        self.add(accounts, friendships, lines)
        self.wait()
        for mob in names_mob, friends_mob:
            self.play(ShowCreation(
                mob, run_time = 1.0
            ))
        self.wait()


class ExamplesOfGraphs(GraphScene):
    def construct(self):
        buff = 0.5
        self.graph.vertices = [v + DOWN + RIGHT for v in self.graph.vertices]
        GraphScene.construct(self)
        self.generate_regions()
        objects, notions = Mobject(*TextMobject(
            ["Objects \\quad\\quad ", "Thing that connects objects"]
        )).to_corner().shift(0.5*RIGHT).split()
        horizontal_line = Line(
            (-FRAME_X_RADIUS, FRAME_Y_RADIUS-1, 0),
            (max(notions.points[:,0]), FRAME_Y_RADIUS-1, 0)
        )
        vert_line_x_val = min(notions.points[:,0]) - buff
        vertical_line = Line(
            (vert_line_x_val, FRAME_Y_RADIUS, 0),
            (vert_line_x_val,-FRAME_Y_RADIUS, 0)
        )
        objects_and_notions = [
            ("Facebook accounts", "Friendship"),
            ("English Words", "Differ by One Letter"),
            ("Mathematicians", "Coauthorship"),
            ("Neurons", "Synapses"),
            (
                "Regions our graph \\\\ cuts the plane into",
                "Shared edges"
            )
        ]


        self.clear()
        self.add(objects, notions, horizontal_line, vertical_line)
        for (obj, notion), height in zip(objects_and_notions, it.count(2, -1)):
            obj_mob = TextMobject(obj, size = "\\small").to_edge(LEFT)
            not_mob = TextMobject(notion, size = "\\small").to_edge(LEFT)
            not_mob.shift((vert_line_x_val + FRAME_X_RADIUS)*RIGHT)
            obj_mob.shift(height*UP)
            not_mob.shift(height*UP)

            if obj.startswith("Regions"):
                self.handle_dual_graph(obj_mob, not_mob)
            elif obj.startswith("English"):
                self.handle_english_words(obj_mob, not_mob)
            else:
                self.add(obj_mob)
                self.wait()
                self.add(not_mob)
                self.wait()

    def handle_english_words(self, words1, words2):
        words = list(map(TextMobject, ["graph", "grape", "gape", "gripe"]))
        words[0].shift(RIGHT)
        words[1].shift(3*RIGHT)
        words[2].shift(3*RIGHT + 2*UP)
        words[3].shift(3*RIGHT + 2*DOWN)
        lines = [
            Line(*pair)
            for pair in [
                (
                    words[0].get_center() + RIGHT*words[0].get_width()/2,
                    words[1].get_center() + LEFT*words[1].get_width()/2
                ),(
                    words[1].get_center() + UP*words[1].get_height()/2,
                    words[2].get_center() + DOWN*words[2].get_height()/2
                ),(
                    words[1].get_center() + DOWN*words[1].get_height()/2,
                    words[3].get_center() + UP*words[3].get_height()/2
                )
            ]
        ]

        comp_words = Mobject(*words)
        comp_lines = Mobject(*lines)
        self.add(words1)
        self.play(ShowCreation(comp_words, run_time = 1.0))
        self.wait()
        self.add(words2)
        self.play(ShowCreation(comp_lines, run_time = 1.0))
        self.wait()
        self.remove(comp_words, comp_lines)


    def handle_dual_graph(self, words1, words2):
        words1.set_color("yellow")
        words2.set_color("yellow")
        connected = TextMobject("Connected")
        connected.set_color("lightgreen")
        not_connected = TextMobject("Not Connected")
        not_connected.set_color("red")
        for mob in connected, not_connected:
            mob.shift(self.points[3] + UP)

        self.play(*[
            ShowCreation(mob, run_time = 1.0)
            for mob in self.edges + self.vertices
        ])
        self.wait()
        for region in self.regions:
            self.set_color_region(region)
        self.add(words1)
        self.wait()
        self.reset_background()
        self.add(words2)

        region_pairs = it.combinations(self.graph.region_cycles, 2)
        for x in range(6):
            want_matching = (x%2 == 0)
            found = False
            while True:
                try:
                    cycle1, cycle2 = next(region_pairs)
                except:
                    return
                shared = set(cycle1).intersection(cycle2)
                if len(shared) == 2 and want_matching:
                    break
                if len(shared) != 2 and not want_matching:
                    break
            for cycle in cycle1, cycle2:
                index = self.graph.region_cycles.index(cycle)
                self.set_color_region(self.regions[index])
            if want_matching:
                self.remove(not_connected)
                self.add(connected)
                tup = tuple(shared)
                if tup not in self.graph.edges:
                    tup = tuple(reversed(tup))
                edge = deepcopy(self.edges[self.graph.edges.index(tup)])
                edge.set_color("red")
                self.play(ShowCreation(edge), run_time = 1.0)
                self.wait()
                self.remove(edge)
            else:
                self.remove(connected)
                self.add(not_connected)
                self.wait(2)
            self.reset_background()





class DrawDualGraph(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        self.generate_regions()
        self.generate_dual_graph()
        region_mobs = [
            ImageMobject(disp.paint_region(reg, self.background), invert = False)
            for reg in self.regions
        ]
        for region, mob in zip(self.regions, region_mobs):
            self.set_color_region(region, mob.get_color())
        outer_region      = self.regions.pop()
        outer_region_mob  = region_mobs.pop()
        outer_dual_vertex = self.dual_vertices.pop()
        internal_edges = [e for e in self.dual_edges if abs(e.start[0]) < FRAME_X_RADIUS and \
                       abs(e.end[0]) < FRAME_X_RADIUS and \
                       abs(e.start[1]) < FRAME_Y_RADIUS and \
                       abs(e.end[1]) < FRAME_Y_RADIUS]
        external_edges = [e for e in self.dual_edges if e not in internal_edges]

        self.wait()
        self.reset_background()
        self.set_color_region(outer_region, outer_region_mob.get_color())
        self.play(*[
            Transform(reg_mob, dot)
            for reg_mob, dot in zip(region_mobs, self.dual_vertices)
        ])
        self.wait()
        self.reset_background()
        self.play(ApplyFunction(
            lambda p : (FRAME_X_RADIUS + FRAME_Y_RADIUS)*p/get_norm(p),
            outer_region_mob
        ))
        self.wait()
        for edges in internal_edges, external_edges:
            self.play(*[
                ShowCreation(edge, run_time = 2.0)
                for edge in edges
            ])
            self.wait()

class EdgesAreTheSame(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        self.generate_dual_graph()
        self.remove(*self.vertices)
        self.add(*self.dual_edges)
        self.wait()
        self.play(*[
            Transform(*pair, run_time = 2.0)
            for pair in zip(self.dual_edges, self.edges)
        ])
        self.wait()
        self.add(
            TextMobject("""
                (Or at least I would argue they should \\\\
                be thought of as the same thing.)
            """, size = "\\small").to_edge(UP)
        )
        self.wait()

class ListOfCorrespondances(Scene):
    def construct(self):
        buff = 0.5
        correspondances = [
            ["Regions cut out by", "Vertices of"],
            ["Edges of", "Edges of"],
            ["Cycles of", "Connected components of"],
            ["Connected components of", "Cycles of"],
            ["Spanning tree in", "Complement of spanning tree in"],
            ["", "Dual of"],
        ]
        for corr in correspondances:
            corr[0] += " original graph"
            corr[1] += " dual graph"
        arrow = TexMobject("\\leftrightarrow", size = "\\large")
        lines = []
        for corr, height in zip(correspondances, it.count(3, -1)):
            left  = TextMobject(corr[0], size = "\\small")
            right = TextMobject(corr[1], size = "\\small")
            this_arrow = deepcopy(arrow)
            for mob in left, right, this_arrow:
                mob.shift(height*UP)
            arrow_xs = this_arrow.points[:,0]
            left.to_edge(RIGHT)
            left.shift((min(arrow_xs) - FRAME_X_RADIUS, 0, 0))
            right.to_edge(LEFT)
            right.shift((max(arrow_xs) + FRAME_X_RADIUS, 0, 0))
            lines.append(Mobject(left, right, this_arrow))
        last = None
        for line in lines:
            self.add(line.set_color("yellow"))
            if last:
                last.set_color("white")
            last = line
            self.wait(1)


class CyclesCorrespondWithConnectedComponents(GraphScene):
    args_list = [(SampleGraph(),)]
    def construct(self):
        GraphScene.construct(self)
        self.generate_regions()
        self.generate_dual_graph()
        cycle = [4, 2, 1, 5, 4]
        enclosed_regions = [0, 2, 3, 4]
        dual_cycle = DUAL_CYCLE
        enclosed_vertices = [0, 1]
        randy = Randolph()
        randy.scale(RANDOLPH_SCALE_FACTOR)
        randy.move_to(self.points[cycle[0]])

        lines_to_remove = []
        for last, next in zip(cycle, cycle[1:]):
            line = Line(self.points[last], self.points[next])
            line.set_color("yellow")
            self.play(
                ShowCreation(line),
                WalkPiCreature(randy, self.points[next]),
                run_time = 1.0
            )
            lines_to_remove.append(line)
        self.wait()
        self.remove(randy, *lines_to_remove)
        for region in np.array(self.regions)[enclosed_regions]:
            self.set_color_region(region)
        self.wait(2)
        self.reset_background()
        lines = Mobject(*[
            Line(self.dual_points[last], self.dual_points[next])
            for last, next in zip(dual_cycle, dual_cycle[1:])
        ]).set_color("red")
        self.play(ShowCreation(lines))
        self.play(*[
            Transform(v, Dot(
                v.get_center(), 
                radius = 3*Dot.DEFAULT_RADIUS
            ).set_color("green"))
            for v in np.array(self.vertices)[enclosed_vertices]
        ] + [
            ApplyMethod(self.edges[0].set_color, "green")
        ])
        self.wait()

        
class IntroduceMortimer(GraphScene):
    args_list = [(SampleGraph(),)]
    def construct(self):
        GraphScene.construct(self)
        self.generate_dual_graph()
        self.generate_regions()
        randy = Randolph().shift(LEFT)
        morty = Mortimer().shift(RIGHT)
        name = TextMobject("Mortimer")
        name.shift(morty.get_center() + 1.2*UP)
        randy_path = (0, 1, 3)
        morty_path = (-2, -3, -4)
        morty_crossed_lines = [
            Line(self.points[i], self.points[j]).set_color("red")
            for i, j in [(7, 1), (1, 5)]
        ]
        kwargs = {"run_time" : 1.0}

        self.clear()
        self.add(randy)
        self.wait()
        self.add(morty, name)
        self.wait()
        self.remove(name)
        small_randy = deepcopy(randy).scale(RANDOLPH_SCALE_FACTOR)
        small_morty = deepcopy(morty).scale(RANDOLPH_SCALE_FACTOR)
        small_randy.move_to(self.points[randy_path[0]])
        small_morty.move_to(self.dual_points[morty_path[0]])
        self.play(*[
            FadeIn(mob)
            for mob in self.vertices + self.edges
        ] + [
            Transform(randy, small_randy),
            Transform(morty, small_morty),
        ], **kwargs)
        self.wait()


        self.set_color_region(self.regions[morty_path[0]])
        for last, next in zip(morty_path, morty_path[1:]):
            self.play(WalkPiCreature(morty, self.dual_points[next]),**kwargs)
            self.set_color_region(self.regions[next])
        self.wait()
        for last, next in zip(randy_path, randy_path[1:]):
            line = Line(self.points[last], self.points[next])
            line.set_color("yellow")
            self.play(
                WalkPiCreature(randy, self.points[next]),
                ShowCreation(line),
                **kwargs
            )
        self.wait()
        self.play(*[
            ApplyMethod(
                line.rotate_in_place, 
                np.pi/10, 
                rate_func = wiggle) 
            for line in morty_crossed_lines
        ], **kwargs)
        
        self.wait()

class RandolphMortimerSpanningTreeGame(GraphScene):
    args_list = [(SampleGraph(),)]
    def construct(self):
        GraphScene.construct(self)
        self.generate_spanning_tree()
        self.generate_dual_graph()
        self.generate_regions()
        randy = Randolph().scale(RANDOLPH_SCALE_FACTOR)
        morty = Mortimer().scale(RANDOLPH_SCALE_FACTOR)
        randy.move_to(self.points[0])
        morty.move_to(self.dual_points[0])
        attempted_dual_point_index = 2
        region_ordering = [0, 1, 7, 2, 3, 5, 4, 6]
        dual_edges = [1, 3, 4, 7, 11, 9, 13]
        time_per_dual_edge = 0.5

        self.add(randy, morty)
        self.play(ShowCreation(self.spanning_tree))
        self.wait()
        self.play(WalkPiCreature(
            morty, self.dual_points[attempted_dual_point_index],
            rate_func = lambda t : 0.3 * there_and_back(t),
            run_time = 2.0,
        ))
        self.wait()
        for index in range(len(self.regions)):
            # if index > 0:
            #     edge = self.edges[dual_edges[index-1]]
            #     midpoint = edge.get_center()
            #     self.play(*[
            #         ShowCreation(Line(
            #             midpoint,
            #             tip
            #         ).set_color("red"))
            #         for tip in edge.start, edge.end
            #     ], run_time = time_per_dual_edge)
            self.set_color_region(self.regions[region_ordering[index]])
            self.wait(time_per_dual_edge)
        self.wait()


        cycle_index = region_ordering[-1]
        cycle = self.graph.region_cycles[cycle_index]
        self.set_color_region(self.regions[cycle_index], "black")
        self.play(ShowCreation(Mobject(*[
            Line(self.points[last], self.points[next]).set_color("green")
            for last, next in zip(cycle, list(cycle)[1:] + [cycle[0]])
        ])))
        self.wait()

class MortimerCannotTraverseCycle(GraphScene):
    args_list = [(SampleGraph(),)]
    def construct(self):
        GraphScene.construct(self)
        self.generate_dual_graph()
        dual_cycle = DUAL_CYCLE
        trapped_points = [0, 1]
        morty = Mortimer().scale(RANDOLPH_SCALE_FACTOR)
        morty.move_to(self.dual_points[dual_cycle[0]])
        time_per_edge = 0.5
        text = TextMobject("""
            One of these lines must be included
            in the spanning tree if those two inner
            vertices are to be reached.
        """).scale(0.7).to_edge(UP)

        all_lines = []
        matching_edges = []
        kwargs = {"run_time" : time_per_edge, "rate_func" : None}
        for last, next in zip(dual_cycle, dual_cycle[1:]):
            line = Line(self.dual_points[last], self.dual_points[next])
            line.set_color("red")
            self.play(
                WalkPiCreature(morty, self.dual_points[next], **kwargs),
                ShowCreation(line, **kwargs),
            )
            all_lines.append(line)
            center = line.get_center()
            distances = [get_norm(center - e.get_center()) for e in self.edges]
            matching_edges.append(
                self.edges[distances.index(min(distances))]
            )
        self.play(*[
            Transform(v, Dot(
                v.get_center(), 
                radius = 3*Dot.DEFAULT_RADIUS,
                color = "green"
            ))
            for v in np.array(self.vertices)[trapped_points]
        ])
        self.add(text)
        self.play(*[
            Transform(line, deepcopy(edge).set_color(line.get_color()))
            for line, edge in zip(all_lines, matching_edges)
        ])
        self.wait()

class TwoPropertiesOfSpanningTree(Scene):
    def construct(self):
        spanning, tree = TextMobject(
            ["Spanning ", "Tree"], 
            size = "\\Huge"
        ).split()
        spanning_explanation = TextMobject("""
            Touches every vertex
        """).shift(spanning.get_center() + 2*DOWN)
        tree_explanation = TextMobject("""
            No Cycles
        """).shift(tree.get_center() + 2*UP)

        self.add(spanning, tree)
        self.wait()
        for word, explanation, vect in [
            (spanning, spanning_explanation, 0.5*UP),
            (tree, tree_explanation, 0.5*DOWN)
            ]:
            self.add(explanation)
            self.add(Arrow(
                explanation.get_center() + vect,
                tail = word.get_center() - vect,
            ))
            self.play(ApplyMethod(word.set_color, "yellow"))
            self.wait()


class DualSpanningTree(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        self.generate_dual_graph()
        self.generate_spanning_tree()
        randy = Randolph()
        randy.scale(RANDOLPH_SCALE_FACTOR)
        randy.move_to(self.points[0])
        morty = Mortimer()
        morty.scale(RANDOLPH_SCALE_FACTOR)
        morty.move_to(self.dual_points[0])
        dual_edges = [1, 3, 4, 7, 11, 9, 13]
        words = TextMobject("""
            The red edges form a spanning tree of the dual graph!
        """).to_edge(UP)

        self.add(self.spanning_tree, randy, morty)
        self.play(ShowCreation(Mobject(
            *np.array(self.edges)[dual_edges]
        ).set_color("red")))
        self.add(words)
        self.wait()

class TreeCountFormula(Scene):
    def construct(self):
        time_per_branch = 0.5
        text = TextMobject("""
            In any tree:
            $$E + 1 = V$$
        """)
        gs = GraphScene(SampleGraph())
        gs.generate_treeified_spanning_tree()
        branches = gs.treeified_spanning_tree.to_edge(LEFT).split()

        all_dots = [Dot(branches[0].points[0])]
        self.add(text, all_dots[0])
        for branch in branches:
            self.play(
                ShowCreation(branch), 
                run_time = time_per_branch
            )
            dot = Dot(branch.points[-1])
            self.add(dot)
            all_dots.append(dot)
        self.wait()
        self.remove(*all_dots)
        self.play(
            FadeOut(text), 
            FadeIn(Mobject(*gs.edges + gs.vertices)),
            *[
                Transform(*pair)
                for pair in zip(branches,gs.spanning_tree.split())
            ]
        )


class FinalSum(Scene):
    def construct(self):
        lines = TexMobject([
            "(\\text{Number of Randolph's Edges}) + 1 &= V \\\\ \n",
            "(\\text{Number of Mortimer's Edges}) + 1 &= F \\\\ \n",
            " \\Downarrow \\\\", "E","+","2","&=","V","+","F",
        ], size = "\\large").split()
        for line in lines[:2] + [Mobject(*lines[2:])]:
            self.add(line)
            self.wait()
        self.wait()

        symbols = V, minus, E, plus, F, equals, two = TexMobject(
            "V - E + F = 2".split(" ")
        )
        plus = TexMobject("+")
        anims = []
        for mob, index in zip(symbols, [-3, -2, -7, -6, -1, -4, -5]):
            copy = plus if index == -2 else deepcopy(mob)
            copy.center().shift(lines[index].get_center())
            copy.scale_in_place(lines[index].get_width()/mob.get_width())
            anims.append(CounterclockwiseTransform(copy, mob))
        self.clear()
        self.play(*anims, run_time = 2.0)
        self.wait()





if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)











