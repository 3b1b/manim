import numpy as np
import operator as op
import itertools as it

from constants import *
from image_mobject import *
from region import *
from scene import Scene

RADIUS = SPACE_HEIGHT - 0.1
CIRCLE_DENSITY = DEFAULT_POINT_DENSITY_1D*RADIUS

############################################

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
        self.n_equals = tex_mobject(
            "n=%d"%len(radians), 
            size = r"\small"
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

class GraphScene(Scene):
    #Note, the placement of vertices in this is pretty hard coded, be
    #warned if you want to change it.
    def __init__(self, graph, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        #See CUBE_GRAPH above for format of graph
        self.graph = graph
        self.points = map(np.array, graph["vertices"])
        self.vertices = self.dots = [Dot(p) for p in self.points]
        self.edges = [
            Line(self.points[i], self.points[j])
            for i, j in graph["edges"]
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

class PascalsTriangleScene(Scene): 
    def __init__(self, nrows, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        diagram_height   = 2*SPACE_HEIGHT - 1
        diagram_width    = 1.5*SPACE_WIDTH
        cell_height      = diagram_height / nrows
        cell_width       = diagram_width / nrows
        portion_to_fill  = 0.7
        bottom_left      = np.array(
            (-cell_width * nrows / 2.0, -cell_height * nrows / 2.0, 0)
        )
        num_to_num_mob   = {} 
        coords_to_mobs   = {}
        coords = [(n, k) for n in range(nrows) for k in range(n+1)]    
        for n, k in coords:
            num = choose(n, k)              
            center = bottom_left + (
                cell_width * (k+nrows/2.0 - n/2.0), 
                cell_height * (nrows - n), 
                0
            )
            if num not in num_to_num_mob:
                num_to_num_mob[num] = tex_mobject(str(num))
            num_mob = deepcopy(num_to_num_mob[num])  
            scale_factor = min(
                1,
                portion_to_fill * cell_height / num_mob.get_height(),
                portion_to_fill * cell_width / num_mob.get_width(),
            )
            num_mob.center().scale(scale_factor).shift(center)
            if n not in coords_to_mobs:
                coords_to_mobs[n] = {}
            coords_to_mobs[n][k] = num_mob
        self.add(*[coords_to_mobs[n][k] for n, k in coords])
        #Add attributes
        self.nrows          = nrows
        self.coords         = coords
        self.diagram_height = diagram_height
        self.diagram_width  = diagram_width
        self.cell_height    = cell_height
        self.cell_width     = cell_width
        self.portion_to_fill= portion_to_fill
        self.coords_to_mobs = coords_to_mobs


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



##################################################

def choose(n, r):
    if n < r: return 0
    if r == 0: return 1
    denom = reduce(op.mul, xrange(1, r+1), 1)
    numer = reduce(op.mul, xrange(n, n-r, -1), 1)
    return numer//denom

def moser_function(n):
    return choose(n, 4) + choose(n, 2) + 1

def is_on_line(p0, p1, p2, threshold = 0.01):
    """
    Returns true of p0 is on the line between p1 and p2
    """
    p0, p1, p2 = map(lambda tup : np.array(tup[:2]), [p0, p1, p2])
    p1 -= p0
    p2 -= p0
    return abs((p1[0] / p1[1]) - (p2[0] / p2[1])) < threshold


def intersection(line1, line2):
    """
    A "line" should come in the form [(x0, y0), (x1, y1)] for two
    points it runs through
    """
    p0, p1, p2, p3 = map(
        lambda tup : np.array(tup[:2]),
        [line1[0], line1[1], line2[0], line2[1]]
    )
    p1, p2, p3 = map(lambda x : x - p0, [p1, p2, p3])
    transform = np.zeros((2, 2))
    transform[:,0], transform[:,1] = p1, p2
    if np.linalg.det(transform) == 0: return
    inv = np.linalg.inv(transform)
    new_p3 = np.dot(inv, p3.reshape((2, 1)))
    #Where does line connecting (0, 1) to new_p3 hit x axis
    x_intercept = new_p3[0] / (1 - new_p3[1]) 
    result = np.dot(transform, [[x_intercept], [0]])
    result = result.reshape((2,)) + p0
    return result



