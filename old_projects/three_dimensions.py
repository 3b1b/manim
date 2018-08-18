import numpy as np
import itertools as it

from mobject.mobject import Mobject, Mobject1D, Mobject2D, Mobject
from geometry import Line
from constants import *

class Stars(Mobject1D):
    CONFIG = {
        "stroke_width" : 1,
        "radius"          : FRAME_X_RADIUS,
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
        return np.array([1 if abs(x) == 1 else 0 for x in coords])

class Cube(Mobject1D):
    def generate_points(self):
        self.add_points([
            ([a, b, c][p[0]], [a, b, c][p[1]], [a, b, c][p[2]])
            for p in [(0, 1, 2), (2, 0, 1), (1, 2, 0)]
            for a, b, c in it.product([-1, 1], [-1, 1], np.arange(-1, 1, self.epsilon))
        ])
        self.pose_at_angle()
        self.set_color(YELLOW)

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
        self.set_color(MAROON_D)

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
            perm = [j%3 for j in range(i, i+3)]
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
        return np.array(coords) / get_norm(coords)

        