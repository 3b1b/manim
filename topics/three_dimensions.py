import numpy as np
import itertools as it

from mobject import Mobject, Mobject1D, Mobject2D, Mobject, VMobject
from geometry import Line
from helpers import *

class Stars(Mobject1D):
    CONFIG = {
        "stroke_width" : 1,
        "radius"          : SPACE_WIDTH,
        "num_points"      : 1000,
    }
    def generate_points(self):
        radii, phis, thetas = [
            scalar*np.random.random(self.num_points)
            for scalar in [self.radius, np.pi, 2*np.pi]
        ]
        self.add_points([
            (
                r * np.sin(phi)*np.cos(theta), 
                r * np.sin(phi)*np.sin(theta), 
                r * np.cos(phi)
            )
            for r, phi, theta in zip(radii, phis, thetas)
        ])
class StarsCartesian(Mobject2D):
    CONFIG = {
        "stroke_width" : 1,
        "radius"       : 2*SPACE_WIDTH,
        "num_points"   : 1000,
    }
    def generate_points(self):
        xs, ys, zs = [
            scalar*np.random.random(self.num_points)
            for scalar in [self.radius, self.radius, self.radius]
        ]
        self.add_points([
            (
                x - self.radius/2,
                y - self.radius/2,
                z - self.radius/2
            )
            for x, y, z in zip(xs, ys, zs)
        ])

class CubeWithFaces(Mobject2D):
    def generate_points(self):
        self.add_points([
            sgn * np.array(coords)
            for x in np.arange(-1, 1, self.epsilon)
            for y in np.arange(x, 1, self.epsilon) 
            for coords in it.permutations([x, y, 1]) 
            for sgn in [-1, 1]
        ])
        self.pose_at_angle()
        self.set_color(BLUE)

    def unit_normal(self, coords):
        return np.array(map(lambda x : 1 if abs(x) == 1 else 0, coords))

class Cube(Mobject1D):
    def generate_points(self):
        self.add_points([
            ([a, b, c][p[0]], [a, b, c][p[1]], [a, b, c][p[2]])
            for p in [(0, 1, 2), (2, 0, 1), (1, 2, 0)]
            for a, b, c in it.product([-1, 1], [-1, 1], np.arange(-1, 1, self.epsilon))
        ])
        self.pose_at_angle()
        self.set_color(YELLOW)

class Octohedron(VMobject):
    CONFIG = {

    }
    def generate_points(self):
        # TODO in a more generalized way where you can just define the vertices?
        vertex_pairs = [
            (LEFT+UP, RIGHT+UP),
            (RIGHT+UP, RIGHT+DOWN),
            (RIGHT+DOWN, LEFT+DOWN),
            (LEFT+DOWN, LEFT+UP),

            (LEFT+UP, IN*np.sqrt(2)),
            (RIGHT+UP, IN*np.sqrt(2)),
            (RIGHT+DOWN, IN*np.sqrt(2)),
            (LEFT+DOWN, IN*np.sqrt(2)),

            (LEFT+UP, OUT*np.sqrt(2)),
            (RIGHT+UP, OUT*np.sqrt(2)),
            (RIGHT+DOWN, OUT*np.sqrt(2)),
            (LEFT+DOWN, OUT*np.sqrt(2))
        ]

        for pair in vertex_pairs:
            self.add(Line(pair[0], pair[1]))


        self.rotate_in_place(- 3 * np.pi / 7, RIGHT)
        self.rotate_in_place(np.pi / 12, UP)

class Dodecahedron(Mobject1D):
    def generate_points(self):
        phi = (1 + np.sqrt(5)) / 2
        x = np.array([1, 0, 0])
        y = np.array([0, 1, 0])
        z = np.array([0, 0, 1])
        v1, v2 = (phi, 1/phi, 0), (phi, -1/phi, 0)
        vertex_pairs = [
            (v1, v2),
            (x+y+z, v1),
            (x+y-z, v1),
            (x-y+z, v2),
            (x-y-z, v2),
        ]
        five_lines_points = Mobject(*[
            Line(pair[0], pair[1], density = 1.0/self.epsilon)
            for pair in vertex_pairs
        ]).points
        #Rotate those 5 edges into all 30.
        for i in range(3):
            perm = map(lambda j : j%3, range(i, i+3))
            for b in [-1, 1]:
                matrix = b*np.array([x[perm], y[perm], z[perm]])
                self.add_points(np.dot(five_lines_points, matrix))
        self.pose_at_angle()
        self.set_color(GREEN)

class Sphere(Mobject2D):
    def generate_points(self):
        self.add_points([
            (
                np.sin(phi) * np.cos(theta),
                np.sin(phi) * np.sin(theta),
                np.cos(phi)
            )
            for phi in np.arange(self.epsilon, np.pi, self.epsilon)
            for theta in np.arange(0, 2 * np.pi, 2 * self.epsilon / np.sin(phi)) 
        ])
        self.set_color(BLUE)

    def unit_normal(self, coords):
        return np.array(coords) / np.linalg.norm(coords)

        