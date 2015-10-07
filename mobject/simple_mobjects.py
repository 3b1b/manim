import numpy as np
import itertools as it

from mobject import Mobject, Mobject1D, Mobject2D, CompoundMobject
from image_mobject import text_mobject
from constants import *
from helpers import *


class Point(Mobject):
    DEFAULT_CONFIG = {
        "color" : "black",
    }
    def __init__(self, location = ORIGIN, **kwargs):
        digest_config(self, Point, kwargs, locals())
        Mobject.__init__(self, **kwargs)

    def generate_points(self):
        self.add_points([self.location])


class Dot(Mobject1D): #Use 1D density, even though 2D
    DEFAULT_CONFIG = {
        "radius" : 0.05
    }
    def __init__(self, center_point = ORIGIN, **kwargs):
        digest_config(self, Dot, kwargs, locals())
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        self.add_points([
            np.array((t*np.cos(theta), t*np.sin(theta), 0)) + self.center_point
            for t in np.arange(self.epsilon, self.radius, self.epsilon)
            for new_epsilon in [2*np.pi*self.epsilon*self.radius/t]
            for theta in np.arange(0, 2 * np.pi, new_epsilon)
        ])

class Cross(Mobject1D):
    DEFAULT_CONFIG = {
        "color" : "yellow",
        "radius" : 0.3
    }
    def __init__(self, center_point = ORIGIN, **kwargs):
        digest_config(self, Cross, kwargs, locals())
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        self.add_points([
            (sgn * x, x, 0)
            for x in np.arange(-self.radius / 2, self.radius/2, self.epsilon)
            for sgn in [-1, 1]
        ])
        self.shift(self.center_point)

class Line(Mobject1D):
    DEFAULT_CONFIG = {
        "min_density" : 0.1
    }
    def __init__(self, start, end, **kwargs):
        digest_config(self, Line, kwargs)
        self.set_start_and_end(start, end)
        Mobject1D.__init__(self, **kwargs)

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
        length = np.linalg.norm(self.end - self.start)
        epsilon = self.epsilon / max(length, self.min_density)
        self.add_points([
            interpolate(self.start, self.end, t)
            for t in np.arange(0, 1, epsilon)
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
    DEFAULT_CONFIG = {
        "color" : "white",
        "tip_length" : 0.25
    }
    def __init__(self, *args, **kwargs):
        digest_config(self, Arrow, kwargs)
        Line.__init__(self, *args, **kwargs)
        self.add_tip()

    def add_tip(self):
        num_points = self.get_num_points()
        vect = self.start-self.end
        vect = vect*self.tip_length/np.linalg.norm(vect)
        self.add_points([
            interpolate(self.end, self.end+v, t)
            for t in np.arange(0, 1, self.tip_length*self.epsilon)
            for v in [
                rotate_vector(vect, np.pi/4, axis)
                for axis in IN, OUT
            ]
        ])
        self.num_tip_points = self.get_num_points()-num_points

    def remove_tip(self):
        if not hasattr(self, "num_tip_points"):
            return self
        for attr in "points", "rgbs":
            setattr(self, attr, getattr(self, attr)[:-self.num_tip_points])
        return self

class CurvedLine(Line):
    def __init__(self, start, end, via = None, **kwargs):
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
        Line.__init__(self, start, end, **kwargs)

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
    DEFAULT_CONFIG = {
        "color" : "red",
        "radius" : 1.0
    }
    def __init__(self, **kwargs):
        digest_config(self, Circle, kwargs)
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        self.add_points([
            (self.radius*np.cos(theta), self.radius*np.sin(theta), 0)
            for theta in np.arange(0, 2 * np.pi, self.epsilon/self.radius)
        ])

class Rectangle(Mobject1D):
    DEFAULT_CONFIG = {
        "color" : "yellow",
        "height" : 2.0,
        "width" : 4.0
    }
    def __init__(self, **kwargs):
        digest_config(self, Rectangle, kwargs)
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
    DEFAULT_CONFIG = {
        "height" : 2.0,
        "width" : 2.0,
    }
    def __init__(self, **kwargs):
        digest_config(self, Square, kwargs)
        Rectangle.__init__(self, **kwargs)

class Bubble(Mobject):
    DEFAULT_CONFIG = {
        "direction" : LEFT,
        "index_of_tip" : -1,
        "center_point" : ORIGIN,
    }
    def __init__(self, **kwargs):
        digest_config(self, Bubble, kwargs)
        Mobject.__init__(self, **kwargs)
        self.center_offset = self.center_point - Mobject.get_center(self)
        if self.direction[0] > 0:
            self.rotate(np.pi, UP)
        self.content = Mobject()

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
    DEFAULT_CONFIG = {
        "initial_width" : 4,
        "initial_height" : 2,
    }
    def __init__(self, **kwargs):
        digest_config(self, SpeechBubble, kwargs)
        Bubble.__init__(self, **kwargs)

    def generate_points(self):
        complex_power = 0.9
        radius = self.initial_width/2
        circle = Circle(radius = radius)
        circle.scale(1.0/radius)
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
        self.points[:,1] *= float(self.initial_height)/self.initial_width

class ThoughtBubble(Bubble):
    DEFAULT_CONFIG = {
        "num_bulges" : 7,
        "initial_inner_radius" : 1.8,
        "initial_width" : 6
    }
    def __init__(self, **kwargs):
        digest_config(self, ThoughtBubble, kwargs)
        Bubble.__init__(self, **kwargs)
        self.index_of_tip = np.argmin(self.points[:,1])

    def generate_points(self):
        self.add(Circle().scale(0.15).shift(2.5*DOWN+2*LEFT))
        self.add(Circle().scale(0.3).shift(2*DOWN+1.5*LEFT))
        for n in range(self.num_bulges):
            theta = 2*np.pi*n/self.num_bulges
            self.add(Circle().shift((np.cos(theta), np.sin(theta), 0)))
        self.filter_out(lambda p : np.linalg.norm(p) < self.initial_inner_radius)
        self.stretch_to_fit_width(self.initial_width)
        self.highlight("white")














       