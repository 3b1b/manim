import numpy as np
import itertools as it

from mobject import Mobject, Mobject1D, Mobject2D, CompoundMobject
from simple_mobjects import Line
from constants import *
from helpers import *

class Stars(Mobject):
    DEFAULT_CONFIG = {
        "point_thickness" : 1,
        "radius" : SPACE_WIDTH,
        "num_points" : 1000,
    }
    def __init__(self, **kwargs):
        digest_config(self, Stars, kwargs)
        Mobject.__init__(self, **kwargs)

    def generate_points(self):
        self.add_points([
            (
                r * np.sin(phi)*np.cos(theta), 
                r * np.sin(phi)*np.sin(theta), 
                r * np.cos(phi)
            )
            for x in range(self.num_points)
            for r, phi, theta in [[
                self.radius * random(),
                np.pi * random(),
                2 * np.pi * random(),
            ]]
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
        self.set_color("skyblue")

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
        self.set_color("yellow")

class Octohedron(Mobject1D):
    def generate_points(self):
        x = np.array([1, 0, 0])
        y = np.array([0, 1, 0])
        z = np.array([0, 0, 1])
        vertex_pairs = [(x+y, x-y), (x+y,-x+y), (-x-y,-x+y), (-x-y,x-y)]
        vertex_pairs += [
            (b[0]*x+b[1]*y, b[2]*np.sqrt(2)*z)
            for b in it.product(*[(-1, 1)]*3)
        ]
        for pair in vertex_pairs:
            self.add_points(
                Line(pair[0], pair[1], density = 1/self.epsilon).points
            )
        self.pose_at_angle()
        self.set_color("pink")

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
        five_lines_points = CompoundMobject(*[
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
        self.set_color("limegreen")

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
        self.set_color("blue")

    def unit_normal(self, coords):
        return np.array(coords) / np.linalg.norm(coords)

        