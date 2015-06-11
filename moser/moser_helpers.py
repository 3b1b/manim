import numpy as np
import itertools as it

from constants import *
from helpers import *
from image_mobject import *
from region import *
from scene import Scene

from graphs import *

RADIUS            = SPACE_HEIGHT - 0.1
CIRCLE_DENSITY    = DEFAULT_POINT_DENSITY_1D*RADIUS
MOVIE_PREFIX      = "moser/"
RADIANS           = np.arange(0, 6, 6.0/7)
MORE_RADIANS      = np.append(RADIANS, RADIANS + 0.5)
N_PASCAL_ROWS     = 7
BIG_N_PASCAL_ROWS = 11

############################################

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
        self.n_equals = tex_mobject(
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


##################################################

def int_list_to_string(int_list):
    return "-".join(map(str, int_list))

def moser_function(n):
    return choose(n, 4) + choose(n, 2) + 1



