from functools import reduce
import itertools as it
import operator as op

import numpy as np

from manimlib.constants import *
from manimlib.scene.scene import Scene
from manimlib.utils.rate_functions import there_and_back
from manimlib.utils.space_ops import center_of_mass


class Graph():
    def __init__(self):
        # List of points in R^3
        # vertices = []
        # List of pairs of indices of vertices
        # edges = []
        # List of tuples of indices of vertices.  The last should
        # be a cycle whose interior is the entire graph, and when
        # regions are computed its complement will be taken.
        # region_cycles = []

        self.construct()

    def construct(self):
        pass

    def __str__(self):
        return self.__class__.__name__


class CubeGraph(Graph):
    """
     5  7
      12
      03
     4  6
    """

    def construct(self):
        self.vertices = [
            (x, y, 0)
            for r in (1, 2)
            for x, y in it.product([-r, r], [-r, r])
        ]
        self.edges = [
            (0, 1),
            (0, 2),
            (3, 1),
            (3, 2),
            (4, 5),
            (4, 6),
            (7, 5),
            (7, 6),
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),
        ]
        self.region_cycles = [
            [0, 2, 3, 1],
            [4, 0, 1, 5],
            [4, 6, 2, 0],
            [6, 7, 3, 2],
            [7, 5, 1, 3],
            [4, 6, 7, 5],  # By convention, last region will be "outside"
        ]


class SampleGraph(Graph):
    """
      4 2  3     8
       0 1
              7
     5   6
    """

    def construct(self):
        self.vertices = [
            (0, 0, 0),
            (2, 0, 0),
            (1, 2, 0),
            (3, 2, 0),
            (-1, 2, 0),
            (-2, -2, 0),
            (2, -2, 0),
            (4, -1, 0),
            (6, 2, 0),
        ]
        self.edges = [
            (0, 1),
            (1, 2),
            (1, 3),
            (3, 2),
            (2, 4),
            (4, 0),
            (2, 0),
            (4, 5),
            (0, 5),
            (1, 5),
            (5, 6),
            (6, 7),
            (7, 1),
            (7, 8),
            (8, 3),
        ]
        self.region_cycles = [
            (0, 1, 2),
            (1, 3, 2),
            (2, 4, 0),
            (4, 5, 0),
            (0, 5, 1),
            (1, 5, 6, 7),
            (1, 7, 8, 3),
            (4, 5, 6, 7, 8, 3, 2),
        ]


class OctohedronGraph(Graph):
    """
           3

         1   0
           2
    4             5
    """

    def construct(self):
        self.vertices = [
            (r * np.cos(angle), r * np.sin(angle) - 1, 0)
            for r, s in [(1, 0), (3, 3)]
            for angle in (np.pi / 6) * np.array([s, 4 + s, 8 + s])
        ]
        self.edges = [
            (0, 1),
            (1, 2),
            (2, 0),
            (5, 0),
            (0, 3),
            (3, 5),
            (3, 1),
            (3, 4),
            (1, 4),
            (4, 2),
            (4, 5),
            (5, 2),
        ]
        self.region_cycles = [
            (0, 1, 2),
            (0, 5, 3),
            (3, 1, 0),
            (3, 4, 1),
            (1, 4, 2),
            (2, 4, 5),
            (5, 0, 2),
            (3, 4, 5),
        ]


class CompleteGraph(Graph):
    def __init__(self, num_vertices, radius=3):
        self.num_vertices = num_vertices
        self.radius = radius
        Graph.__init__(self)

    def construct(self):
        self.vertices = [
            (self.radius * np.cos(theta), self.radius * np.sin(theta), 0)
            for x in range(self.num_vertices)
            for theta in [2 * np.pi * x / self.num_vertices]
        ]
        self.edges = it.combinations(list(range(self.num_vertices)), 2)

    def __str__(self):
        return Graph.__str__(self) + str(self.num_vertices)


class DiscreteGraphScene(Scene):
    args_list = [
        (CubeGraph(),),
        (SampleGraph(),),
        (OctohedronGraph(),),
    ]

    @staticmethod
    def args_to_string(*args):
        return str(args[0])

    def __init__(self, graph, *args, **kwargs):
        # See CubeGraph() above for format of graph
        self.graph = graph
        Scene.__init__(self, *args, **kwargs)

    def construct(self):
        self.points = list(map(np.array, self.graph.vertices))
        self.vertices = self.dots = [Dot(p) for p in self.points]
        self.edges = self.lines = [
            Line(self.points[i], self.points[j])
            for i, j in self.graph.edges
        ]
        self.add(*self.dots + self.edges)

    def generate_regions(self):
        regions = [
            self.region_from_cycle(cycle)
            for cycle in self.graph.region_cycles
        ]
        regions[-1].complement()  # Outer region painted outwardly...
        self.regions = regions

    def region_from_cycle(self, cycle):
        point_pairs = [
            [
                self.points[cycle[i]],
                self.points[cycle[(i + 1) % len(cycle)]]
            ]
            for i in range(len(cycle))
        ]
        return region_from_line_boundary(
            *point_pairs, shape=self.shape
        )

    def draw_vertices(self, **kwargs):
        self.clear()
        self.play(ShowCreation(Mobject(*self.vertices), **kwargs))

    def draw_edges(self):
        self.play(*[
            ShowCreation(edge, run_time=1.0)
            for edge in self.edges
        ])

    def accent_vertices(self, **kwargs):
        self.remove(*self.vertices)
        start = Mobject(*self.vertices)
        end = Mobject(*[
            Dot(point, radius=3 * Dot.DEFAULT_RADIUS, color="lightgreen")
            for point in self.points
        ])
        self.play(Transform(
            start, end, rate_func=there_and_back,
            **kwargs
        ))
        self.remove(start)
        self.add(*self.vertices)

    def replace_vertices_with(self, mobject):
        mobject.center()
        diameter = max(mobject.get_height(), mobject.get_width())
        self.play(*[
            CounterclockwiseTransform(
                vertex,
                mobject.copy().shift(vertex.get_center())
            )
            for vertex in self.vertices
        ] + [
            ApplyMethod(
                edge.scale_in_place,
                (edge.get_length() - diameter) / edge.get_length()
            )
            for edge in self.edges
        ])

    def annotate_edges(self, mobject, fade_in=True, **kwargs):
        angles = list(map(np.arctan, list(map(Line.get_slope, self.edges))))
        self.edge_annotations = [
            mobject.copy().rotate(angle).move_to(edge.get_center())
            for angle, edge in zip(angles, self.edges)
        ]
        if fade_in:
            self.play(*[
                FadeIn(ann, **kwargs)
                for ann in self.edge_annotations
            ])

    def trace_cycle(self, cycle=None, color="yellow", run_time=2.0):
        if cycle is None:
            cycle = self.graph.region_cycles[0]
        time_per_edge = run_time / len(cycle)
        next_in_cycle = it.cycle(cycle)
        next(next_in_cycle)  # jump one ahead
        self.traced_cycle = Mobject(*[
            Line(self.points[i], self.points[j]).set_color(color)
            for i, j in zip(cycle, next_in_cycle)
        ])
        self.play(
            ShowCreation(self.traced_cycle),
            run_time=run_time
        )

    def generate_spanning_tree(self, root=0, color="yellow"):
        self.spanning_tree_root = 0
        pairs = deepcopy(self.graph.edges)
        pairs += [tuple(reversed(pair)) for pair in pairs]
        self.spanning_tree_index_pairs = []
        curr = root
        spanned_vertices = set([curr])
        to_check = set([curr])
        while len(to_check) > 0:
            curr = to_check.pop()
            for pair in pairs:
                if pair[0] == curr and pair[1] not in spanned_vertices:
                    self.spanning_tree_index_pairs.append(pair)
                    spanned_vertices.add(pair[1])
                    to_check.add(pair[1])
        self.spanning_tree = Mobject(*[
            Line(
                self.points[pair[0]],
                self.points[pair[1]]
            ).set_color(color)
            for pair in self.spanning_tree_index_pairs
        ])

    def generate_treeified_spanning_tree(self):
        bottom = -FRAME_Y_RADIUS + 1
        x_sep = 1
        y_sep = 2
        if not hasattr(self, "spanning_tree"):
            self.generate_spanning_tree()
        root = self.spanning_tree_root
        color = self.spanning_tree.get_color()
        indices = list(range(len(self.points)))
        # Build dicts
        parent_of = dict([
            tuple(reversed(pair))
            for pair in self.spanning_tree_index_pairs
        ])
        children_of = dict([(index, []) for index in indices])
        for child in parent_of:
            children_of[parent_of[child]].append(child)

        x_coord_of = {root: 0}
        y_coord_of = {root: bottom}
        # width to allocate to a given node, computed as
        # the maxium number of decendents in a single generation,
        # minus 1, multiplied by x_sep
        width_of = {}
        for index in indices:
            next_generation = children_of[index]
            curr_max = max(1, len(next_generation))
            while next_generation != []:
                next_generation = reduce(op.add, [
                    children_of[node]
                    for node in next_generation
                ])
                curr_max = max(curr_max, len(next_generation))
            width_of[index] = x_sep * (curr_max - 1)
        to_process = [root]
        while to_process != []:
            index = to_process.pop()
            if index not in y_coord_of:
                y_coord_of[index] = y_sep + y_coord_of[parent_of[index]]
            children = children_of[index]
            left_hand = x_coord_of[index] - width_of[index] / 2.0
            for child in children:
                x_coord_of[child] = left_hand + width_of[child] / 2.0
                left_hand += width_of[child] + x_sep
            to_process += children

        new_points = [
            np.array([
                x_coord_of[index],
                y_coord_of[index],
                0
            ])
            for index in indices
        ]
        self.treeified_spanning_tree = Mobject(*[
            Line(new_points[i], new_points[j]).set_color(color)
            for i, j in self.spanning_tree_index_pairs
        ])

    def generate_dual_graph(self):
        point_at_infinity = np.array([np.inf] * 3)
        cycles = self.graph.region_cycles
        self.dual_points = [
            center_of_mass([
                self.points[index]
                for index in cycle
            ])
            for cycle in cycles
        ]
        self.dual_vertices = [
            Dot(point).set_color("green")
            for point in self.dual_points
        ]
        self.dual_vertices[-1] = Circle().scale(FRAME_X_RADIUS + FRAME_Y_RADIUS)
        self.dual_points[-1] = point_at_infinity

        self.dual_edges = []
        for pair in self.graph.edges:
            dual_point_pair = []
            for cycle in cycles:
                if not (pair[0] in cycle and pair[1] in cycle):
                    continue
                index1, index2 = cycle.index(pair[0]), cycle.index(pair[1])
                if abs(index1 - index2) in [1, len(cycle) - 1]:
                    dual_point_pair.append(
                        self.dual_points[cycles.index(cycle)]
                    )
            assert(len(dual_point_pair) == 2)
            for i in 0, 1:
                if all(dual_point_pair[i] == point_at_infinity):
                    new_point = np.array(dual_point_pair[1 - i])
                    vect = center_of_mass([
                        self.points[pair[0]],
                        self.points[pair[1]]
                    ]) - new_point
                    new_point += FRAME_X_RADIUS * vect / get_norm(vect)
                    dual_point_pair[i] = new_point
            self.dual_edges.append(
                Line(*dual_point_pair).set_color()
            )
