import numpy as np
import itertools as it

from scene import Scene
from graphs import *

from mobject import *
from animation import *
from region import *
from constants import *
from helpers import *

class GraphScene(Scene):
    args_list = [
        (CUBE_GRAPH,),
        (SAMPLE_GRAPH,),
        (OCTOHEDRON_GRAPH,),
    ]
    @staticmethod
    def args_to_string(*args):
        return args[0]["name"]

    def __init__(self, graph, *args, **kwargs):
        #See CUBE_GRAPH above for format of graph
        self.graph = graph
        Scene.__init__(self, *args, **kwargs)

    def construct(self):
        self.points = map(np.array, self.graph["vertices"])
        self.vertices = self.dots = [Dot(p) for p in self.points]
        self.edges = [
            Line(self.points[i], self.points[j])
            for i, j in self.graph["edges"]
        ]
        self.add(*self.dots + self.edges)

    def generate_regions(self):
        regions = [
            region_from_line_boundary(*[
                [
                    self.points[rc[i]], 
                    self.points[rc[(i+1)%len(rc)]]
                ]
                for i in range(len(rc))
            ])
            for rc in self.graph["region_cycles"]
        ]
        regions[-1].complement()#Outer region painted outwardly...
        self.regions = regions

    def generate_spanning_tree(self):
       pass

    def draw_vertices(self):
        self.clear()
        self.animate(ShowCreation(CompoundMobject(*self.vertices)))

    def draw_edges(self):
        self.animate(*[
            ShowCreation(edge, run_time = 1.0)
            for edge in self.edges
        ])

    def replace_vertices_with(self, mobject):
        mobject.center()
        diameter = max(mobject.get_height(), mobject.get_width())
        self.animate(*[
            SemiCircleTransform(
                vertex,
                deepcopy(mobject).shift(vertex.get_center())
            )
            for vertex in self.vertices
        ] + [
            ApplyMethod(
                edge.scale_in_place,
                (edge.get_length() - diameter) / edge.get_length()
            )
            for edge in self.edges
        ])

    def annotate_edges(self, mobject):
        angles = map(np.arctan, map(Line.get_slope, self.edges))
        self.edge_annotations = [
            deepcopy(mobject).rotate(angle).shift(edge.get_center())
            for angle, edge in zip(angles, self.edges)
        ]
        self.animate(*[
            FadeIn(ann)
            for ann in self.edge_annotations
        ])




BIG_N_PASCAL_ROWS = 11
N_PASCAL_ROWS = 7
class PascalsTriangleScene(Scene):
    args_list = [
        (N_PASCAL_ROWS,),
        (BIG_N_PASCAL_ROWS,),
    ]
    @staticmethod
    def args_to_string(*args):
        return str(args[0])

    def __init__(self, nrows, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        self.nrows            = nrows
        self.diagram_height   = 2*SPACE_HEIGHT - 1
        self.diagram_width    = 1.5*SPACE_WIDTH
        self.cell_height      = self.diagram_height / nrows
        self.cell_width       = self.diagram_width / nrows
        self.portion_to_fill  = 0.7
        self.bottom_left      = np.array(
            (-self.cell_width * nrows / 2.0, -self.cell_height * nrows / 2.0, 0)
        )
        num_to_num_mob   = {} 
        self.coords_to_mobs   = {}
        self.coords = [(n, k) for n in range(nrows) for k in range(n+1)]    
        for n, k in self.coords:
            num = choose(n, k)              
            center = self.coords_to_center(n, k)
            if num not in num_to_num_mob:
                num_to_num_mob[num] = tex_mobject(str(num))
            num_mob = deepcopy(num_to_num_mob[num])  
            scale_factor = min(
                1,
                self.portion_to_fill * self.cell_height / num_mob.get_height(),
                self.portion_to_fill * self.cell_width / num_mob.get_width(),
            )
            num_mob.center().scale(scale_factor).shift(center)
            if n not in self.coords_to_mobs:
                self.coords_to_mobs[n] = {}
            self.coords_to_mobs[n][k] = num_mob
        self.add(*[self.coords_to_mobs[n][k] for n, k in self.coords])

    def coords_to_center(self, n, k):
        return self.bottom_left + (
                self.cell_width * (k+self.nrows/2.0 - n/2.0), 
                self.cell_height * (self.nrows - n), 
                0
            )

    def generate_n_choose_k_mobs(self):
        self.coords_to_n_choose_k = {}
        for n, k in self.coords:
            nck_mob = tex_mobject(r"{%d \choose %d}"%(n, k)) 
            scale_factor = min(
                1,
                self.portion_to_fill * self.cell_height / nck_mob.get_height(),
                self.portion_to_fill * self.cell_width / nck_mob.get_width(),
            )
            center = self.coords_to_mobs[n][k].get_center()
            nck_mob.center().scale(scale_factor).shift(center)
            if n not in self.coords_to_n_choose_k:
                self.coords_to_n_choose_k[n] = {}
            self.coords_to_n_choose_k[n][k] = nck_mob

    def generate_sea_of_zeros(self):
        zero = tex_mobject("0")
        self.sea_of_zeros = []
        for n in range(self.nrows):
            for a in range((self.nrows - n)/2 + 1):
                for k in (n + a + 1, -a -1):
                    self.coords.append((n, k))
                    mob = deepcopy(zero)
                    mob.shift(self.coords_to_center(n, k))
                    self.coords_to_mobs[n][k] = mob
                    self.add(mob)