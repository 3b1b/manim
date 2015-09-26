import numpy as np
import itertools as it

from mobject import Mobject, Mobject1D, Mobject2D, CompoundMobject
from image_mobject import text_mobject
from constants import *
from helpers import *


class Point(Mobject):
    DEFAULT_COLOR = "black"
    def __init__(self, location = ORIGIN, *args, **kwargs):
        self.location = np.array(location)
        Mobject.__init__(self, *args, **kwargs)

    def generate_points(self):
        self.add_points(self.location.reshape((1, 3)))


class Dot(Mobject1D): #Use 1D density, even though 2D
    DEFAULT_COLOR = "white"
    DEFAULT_RADIUS = 0.05
    def __init__(self, center = ORIGIN, radius = DEFAULT_RADIUS, 
                 *args, **kwargs):
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
    MIN_DENSITY = 0.1
    def __init__(self, start, end, density = DEFAULT_POINT_DENSITY_1D, 
                 *args, **kwargs):
        self.set_start_and_end(start, end)
        density *= max(self.get_length(), self.MIN_DENSITY)
        Mobject1D.__init__(self, density = density, *args, **kwargs)

    def set_start_and_end(self, start, end):
        preliminary_start, preliminary_end = [
            arg.get_center() 
            if isinstance(arg, Mobject) 
            else np.array(arg)
            for arg in start, end
        ]
        start_to_end = preliminary_end - preliminary_start
        longer_dim = np.argmax(map(abs, start_to_end))
        self.start, self.end = [
            arg.get_edge_center(unit*start_to_end)
            if isinstance(arg, Mobject)
            else np.array(arg)
            for arg, unit in zip([start, end], [1, -1])
        ]

    def generate_points(self):
        self.add_points([
            interpolate(self.start, self.end, t)
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

class Arrow(Line):
    DEFAULT_COLOR = "white"
    DEFAULT_TIP_LENGTH = 0.25
    def __init__(self, *args, **kwargs):
        if "tip_length" in kwargs:
            tip_length = kwargs.pop("tip_length")
        else:
            tip_length = self.DEFAULT_TIP_LENGTH
        Line.__init__(self, *args, **kwargs)
        self.add_tip(tip_length)

    def add_tip(self, tip_length):
        vect = self.start-self.end
        vect = vect*tip_length/np.linalg.norm(vect)
        self.add_points([
            interpolate(self.end, self.end+v, t)
            for t in np.arange(0, 1, tip_length*self.epsilon)
            for v in [
                rotate_vector(vect, np.pi/4, axis)
                for axis in IN, OUT
            ]
        ])

class CurvedLine(Line):
    def __init__(self, start, end, via = None, *args, **kwargs):
        self.set_start_and_end(start, end)
        if via == None:
            self.via = rotate_vector(
                self.end - self.start, 
                np.pi/3, [0,0,1]
            ) + self.start
        elif isinstance(via, Mobject):
            self.via = via.get_center()
        else:
            self.via = via
        Line.__init__(self, start, end, *args, **kwargs)

    def generate_points(self):
        self.add_points([
            interpolate(
                interpolate(self.start, self.end, t),
                self.via,
                t*(1-t)
            )
            for t in np.arange(0, 1, self.epsilon)
        ])

class Circle(Mobject1D):
    DEFAULT_COLOR = "red"
    def __init__(self, radius = 1.0, **kwargs):
        self.radius = radius
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        self.add_points([
            (self.radius*np.cos(theta), self.radius*np.sin(theta), 0)
            for theta in np.arange(0, 2 * np.pi, self.epsilon/self.radius)
        ])

class Rectangle(Mobject1D):
    DEFAULT_COLOR = "yellow"
    def __init__(self, height = 2.0, width = 2.0, **kwargs):
        self.height, self.width = height, width
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        wh = [self.width/2.0, self.height/2.0]
        self.add_points([
            (x, u, 0) if dim==0 else (u, x, 0)
            for dim in 0, 1
            for u in wh[1-dim], -wh[1-dim]
            for x in np.arange(-wh[dim], wh[dim], self.epsilon)
        ])

class Square(Rectangle):
    def __init__(self, side_length = 2.0, **kwargs):
        Rectangle.__init__(self, side_length, side_length, **kwargs)

class Bubble(Mobject):
    def __init__(self, direction = LEFT, index_of_tip = -1, center = ORIGIN):
        self.direction = direction
        self.content = Mobject()
        self.index_of_tip = index_of_tip
        self.center_offset = center - Mobject.get_center(self)
        if direction[0] > 0:
            self.rotate(np.pi, UP)

    def get_tip(self):
        return self.points[self.index_of_tip]

    def get_bubble_center(self):
        return self.get_center()+self.center_offset

    def move_tip_to(self, point):
        self.shift(point - self.get_tip())
        return self

    def flip(self):
        self.direction = -np.array(self.direction)
        self.rotate(np.pi, UP)
        return self

    def pin_to(self, mobject):
        mob_center = mobject.get_center()
        if (mob_center[0] > 0) != (self.direction[0] > 0):
            self.flip()
        boundary_point = mobject.get_boundary_point(UP-self.direction)
        vector_from_center = 1.5*(boundary_point-mob_center)
        self.move_tip_to(mob_center+vector_from_center)
        return self

    def add_content(self, mobject):
        scaled_width = 0.75*self.get_width()
        if mobject.get_width() > scaled_width:
            mobject.scale(scaled_width / mobject.get_width())
        mobject.shift(self.get_bubble_center())
        self.content = mobject
        return self

    def write(self, text):
        self.add_content(text_mobject(text))
        return self

    def clear(self):
        self.content = Mobject()
        return self

class SpeechBubble(Bubble):
    INITIAL_WIDTH = 4
    INITIAL_HEIGHT = 2
    def __init__(self, *args, **kwargs):
        Mobject.__init__(self, *args, **kwargs)
        complex_power = 0.9
        radius = self.INITIAL_WIDTH/2
        circle = Circle(density = radius*DEFAULT_POINT_DENSITY_1D)
        circle.apply_complex_function(lambda z : z**complex_power)
        circle.scale(radius)
        boundary_point_as_complex = radius*complex(-1)**complex_power
        boundary_points = [
            [
                boundary_point_as_complex.real,
                unit*boundary_point_as_complex.imag,
                0
            ]
            for unit in -1, 1
        ]
        tip = radius*(1.5*LEFT+UP)
        self.add(
            circle,
            Line(boundary_points[0], tip),
            Line(boundary_points[1], tip)
        )
        self.highlight("white")
        self.rotate(np.pi/2)
        self.points[:,1] *= float(self.INITIAL_HEIGHT)/self.INITIAL_WIDTH
        Bubble.__init__(self, direction = LEFT)

class ThoughtBubble(Bubble):
    NUM_BULGES = 7
    INITIAL_INNER_RADIUS = 1.8
    INITIAL_WIDTH = 6
    def __init__(self, *args, **kwargs):
        Mobject.__init__(self, *args, **kwargs)
        self.add(Circle().scale(0.15).shift(2.5*DOWN+2*LEFT))
        self.add(Circle().scale(0.3).shift(2*DOWN+1.5*LEFT))
        for n in range(self.NUM_BULGES):
            theta = 2*np.pi*n/self.NUM_BULGES
            self.add(Circle().shift((np.cos(theta), np.sin(theta), 0)))
        self.filter_out(lambda p : np.linalg.norm(p) < self.INITIAL_INNER_RADIUS)
        self.stretch_to_fit_width(self.INITIAL_WIDTH)
        self.highlight("white")
        Bubble.__init__(
            self, 
            index_of_tip = np.argmin(self.points[:,1]),
            **kwargs
        )














       