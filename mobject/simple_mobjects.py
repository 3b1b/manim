import numpy as np
import itertools as it

from mobject import Mobject, Mobject1D, Mobject2D, CompoundMobject
from constants import *
from helpers import *

class Point(Mobject):
    def __init__(self, point = (0, 0, 0), *args, **kwargs):
        Mobject.__init__(self, *args, **kwargs)
        self.points = np.array(point).reshape(1, 3)
        self.rgbs = np.array(self.color.get_rgb()).reshape(1, 3)

class Arrow(Mobject1D):
    DEFAULT_COLOR = "white"
    NUNGE_DISTANCE = 0.1
    def __init__(self, point = (0, 0, 0), direction = (-1, 1, 0), 
                 tail = None, length = 1, tip_length = 0.25,
                 normal = (0, 0, 1), *args, **kwargs):
        self.point = np.array(point)
        if tail is not None:
            direction = self.point - tail
            length = np.linalg.norm(direction)
        self.direction = np.array(direction) / np.linalg.norm(direction)
        self.length = length
        self.normal = np.array(normal)
        self.tip_length = tip_length
        Mobject1D.__init__(self, *args, **kwargs)

    def generate_points(self):
        self.add_points([
            [x, x, x] * self.direction + self.point
            for x in np.arange(-self.length, 0, self.epsilon)
        ])
        tips_dir = [np.array(-self.direction), np.array(-self.direction)]
        for i, sgn in zip([0, 1], [-1, 1]):
            tips_dir[i] = rotate_vector(tips_dir[i], sgn * np.pi / 4, self.normal)
        self.add_points([
            [x, x, x] * tips_dir[i] + self.point
            for x in np.arange(0, self.tip_length, self.epsilon)
            for i in [0, 1]
        ])

    def nudge(self):
        return self.shift(-self.direction * self.NUNGE_DISTANCE)

class Vector(Arrow):
    def __init__(self, point = (1, 0, 0), *args, **kwargs):
        length = np.linalg.norm(point)
        Arrow.__init__(self, point = point, direction = point, 
                       length = length, tip_length = 0.2 * length, 
                       *args, **kwargs)

class Dot(Mobject1D): #Use 1D density, even though 2D
    DEFAULT_COLOR = "white"
    DEFAULT_RADIUS = 0.05
    def __init__(self, center = (0, 0, 0), radius = DEFAULT_RADIUS, *args, **kwargs):
        center = np.array(center)
        if center.size == 1:
            raise Exception("Center must have 2 or 3 coordinates!")
        elif center.size == 2:
            center = np.append(center, [0])
        self.center_point = center
        self.radius = radius
        Mobject1D.__init__(self, *args, **kwargs)

    def generate_points(self):
        self.add_points([
            np.array((t*np.cos(theta), t*np.sin(theta), 0)) + self.center_point
            for t in np.arange(self.epsilon, self.radius, self.epsilon)
            for new_epsilon in [2*np.pi*self.epsilon*self.radius/t]
            for theta in np.arange(0, 2 * np.pi, new_epsilon)
        ])

class Cross(Mobject1D):
    RADIUS = 0.3
    DEFAULT_COLOR = "white"
    def generate_points(self):
        self.add_points([
            (sgn * x, x, 0)
            for x in np.arange(-self.RADIUS / 2, self.RADIUS/2, self.epsilon)
            for sgn in [-1, 1]
        ])

class Line(Mobject1D):
    def __init__(self, start, end, density = DEFAULT_POINT_DENSITY_1D, *args, **kwargs):
        self.start = np.array(start)
        self.end = np.array(end)
        density *= self.get_length()
        Mobject1D.__init__(self, density = density, *args, **kwargs)

    def generate_points(self):
        self.add_points([
            t * self.end + (1 - t) * self.start
            for t in np.arange(0, 1, self.epsilon)
        ])

    def get_length(self):
        return np.linalg.norm(self.start - self.end)

    def get_slope(self):
        rise, run = [
            float(self.end[i] - self.start[i])
            for i in [1, 0]
        ]
        return rise/run

class CurvedLine(Line):
    def __init__(self, start, end, via = None, *args, **kwargs):
        if via == None:
            via = rotate_vector(
                end - start, 
                np.pi/3, [0,0,1]
            ) + start
        self.via = via
        Line.__init__(self, start, end, *args, **kwargs)

    def generate_points(self):
        self.add_points([
            4*(0.25-t*(1-t))*(t*self.end + (1-t)*self.start) + 
            4*t*(1-t)*self.via
            for t in np.arange(0, 1, self.epsilon)
        ])

class Circle(Mobject1D):
    DEFAULT_COLOR = "red"
    def generate_points(self):
        self.add_points([
            (np.cos(theta), np.sin(theta), 0)
            for theta in np.arange(0, 2 * np.pi, self.epsilon)
        ])









       