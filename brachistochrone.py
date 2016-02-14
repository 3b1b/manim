#!/usr/bin/env python

import numpy as np
import itertools as it
import operator as op
import sys
import inspect
from PIL import Image
import cv2
import random
from scipy.spatial.distance import cdist
from scipy import ndimage

from helpers import *

from mobject.tex_mobject import TexMobject, TextMobject
from mobject import Mobject
from mobject.image_mobject import \
    MobjectFromRegion, ImageMobject, MobjectFromPixelArray

from animation.transform import \
    Transform, CounterclockwiseTransform, ApplyPointwiseFunction,\
    FadeIn, FadeOut, GrowFromCenter, ApplyFunction, ApplyMethod, \
    ShimmerIn
from animation.simple_animations import \
    ShowCreation, Homotopy, PhaseFlow, ApplyToCenters, DelayByOrder
from animation.playground import TurnInsideOut, Vibrate
from topics.geometry import \
    Line, Circle, Square, Grid, Rectangle, Arrow, Dot, Point, \
    Arc
from topics.characters import Randolph, Mathematician
from topics.functions import ParametricFunction, FunctionGraph
from topics.number_line import NumberPlane
from region import Region, region_from_polygon_vertices
from scene import Scene

RANDY_SCALE_VAL = 0.3

###########

def wavify(mobject):
    tangent_vectors = mobject.points[1:]-mobject.points[:-1]
    lengths = np.apply_along_axis(
        np.linalg.norm, 1, tangent_vectors
    )
    thick_lengths = lengths.repeat(3).reshape((len(lengths), 3))
    unit_tangent_vectors = tangent_vectors/thick_lengths
    rot_matrix = np.transpose(rotation_matrix(np.pi/2, OUT))
    normal_vectors = np.dot(unit_tangent_vectors, rot_matrix)
    # total_length = np.sum(lengths)
    times = np.cumsum(lengths)
    nudge_sizes = 0.1*np.sin(2*np.pi*times)
    thick_nudge_sizes = nudge_sizes.repeat(3).reshape((len(nudge_sizes), 3))
    nudges = thick_nudge_sizes*normal_vectors
    result = mobject.copy()
    result.points[1:] += nudges
    return result


###########

class Cycloid(ParametricFunction):
    DEFAULT_CONFIG = {
        "point_a"       : 6*LEFT+3*UP,
        "radius"        : 2,
        "end_theta"     : 3*np.pi/2,
        "density"       : 5*DEFAULT_POINT_DENSITY_1D,
        "color"         : BLUE_D
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        ParametricFunction.__init__(self, self.pos_func, **kwargs)

    def pos_func(self, t):
        T = t*self.end_theta
        return self.point_a + self.radius * np.array([
            T - np.sin(T),
            np.cos(T) - 1,
            0
        ])

class LoopTheLoop(ParametricFunction):
    DEFAULT_CONFIG = {
        "color" : YELLOW_D,
        "density" : 20*DEFAULT_POINT_DENSITY_1D
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        pre_func = lambda t : [
            t**3 - 1.5*t,
            t**2 + 0.6*(t**2 - 4)*(t**2 - 1),
            0
        ]
        ParametricFunction.__init__(
            self,
            lambda t : pre_func(4*t-2),
            **kwargs
        )


class PathSlidingScene(Scene):
    DEFAULT_CONFIG = {
        "gravity" : 3,
        "delta_t" : 0.05
    }
    def get_time_slices(self, points):
        dt_list = np.zeros(len(points))
        ds_list = np.apply_along_axis(
            np.linalg.norm,
            1,
            points[1:]-points[:-1]
        )
        delta_y_list = np.abs(points[0, 1] - points[1:,1])
        delta_y_list += 0.001*(delta_y_list == 0)
        v_list = self.gravity*np.sqrt(delta_y_list)
        dt_list[1:] = ds_list / v_list
        return np.cumsum(dt_list)

    def adjust_mobject_to_index(self, mobject, index, points):
        point_a, point_b = points[index-1], points[index]
        while np.all(point_a == point_b):
            index += 1
            point_b = points[index]
        theta = angle_of_vector(point_b - point_a)
        mobject.rotate(theta)
        mobject.shift(points[index])
        return mobject

    def slide(self, mobject, path, roll = False):
        points = path.points
        time_slices = self.get_time_slices(points)
        curr_t = 0
        last_index = 0
        curr_index = 1
        self.t_equals = TexMobject("t = ")
        self.t_equals.shift(3.5*UP+4*RIGHT)
        self.add(self.t_equals)
        while curr_index < len(points):
            self.slider = mobject.copy()
            self.adjust_mobject_to_index(
                self.slider, curr_index, points
            )
            if roll:
                distance = np.linalg.norm(
                    points[curr_index] - points[last_index]
                )
                self.roll(mobject, distance)
            self.add(self.slider)
            self.write_time(curr_t)
            self.dither(self.frame_duration)
            self.remove(self.slider)
            curr_t += self.delta_t
            last_index = curr_index
            while time_slices[curr_index] < curr_t:
                curr_index += 1
                if curr_index == len(points):
                    break
        self.add(self.slider)
        self.dither()

    def write_time(self, time):
        if hasattr(self, "time_mob"):
            self.remove(self.time_mob)
        digits = map(TexMobject, "%.2f"%time)
        digits[0].next_to(self.t_equals, buff = 0.1)
        for left, right in zip(digits, digits[1:]):
            right.next_to(left, buff = 0.1, aligned_edge = DOWN)
        self.time_mob = Mobject(*digits)
        self.add(self.time_mob)

    def roll(self, mobject, arc_length):
        radius = mobject.get_width()/2
        theta = arc_length / radius
        mobject.rotate_in_place(-theta)

class TryManyPaths(PathSlidingScene):
    def construct(self):
        randy = Randolph()
        randy.shift(-randy.get_bottom())
        self.slider = randy.copy()  
        randy.scale(RANDY_SCALE_VAL)
        paths = self.get_paths()
        point_a = Dot(paths[0].points[0])
        point_b = Dot(paths[0].points[-1])
        A = TexMobject("A").next_to(point_a, LEFT)
        B = TexMobject("B").next_to(point_b, RIGHT)
        for point, tex in [(point_a, A), (point_b, B)]:
            self.play(ShowCreation(point))
            self.play(ShimmerIn(tex))
            self.dither()
        curr_path = None        
        for path in paths:
            new_slider = self.adjust_mobject_to_index(
                randy.copy(), 1, path.points
            )
            if curr_path is None:
                curr_path = path
                self.play(ShowCreation(curr_path))
            else:
                self.play(Transform(curr_path, path))
            self.play(Transform(self.slider, new_slider))
            self.dither()
            self.remove(self.slider)
            self.slide(randy, curr_path)
        self.clear()
        self.add(point_a, point_b, A, B, curr_path)
        text = TextMobject("Which path is fastest?")
        text.to_edge(UP)
        self.play(ShimmerIn(text))
        for path in paths:
            self.play(Transform(
                curr_path, path,
                path_func = path_along_arc(np.pi/2),
                run_time = 3
            ))

    def get_paths(self):
        sharp_corner = Mobject(
            Line(3*UP+LEFT, LEFT),
            Arc(angle = np.pi/2, start_angle = np.pi),
            Line(DOWN, DOWN+3*RIGHT)
        ).ingest_sub_mobjects().highlight(GREEN)
        paths = [
            Line(7*LEFT, 7*RIGHT, color = RED_D),
            LoopTheLoop(),
            FunctionGraph(
                lambda x : 0.05*(x**2)+0.1*np.sin(2*x)
            ),
            Arc(
                angle = np.pi/2, 
                radius = 3, 
                start_angle = 4
            ),
            sharp_corner,
            FunctionGraph(
                lambda x : x**2, 
                x_min = -3, 
                x_max = 2,
                density = 3*DEFAULT_POINT_DENSITY_1D
            )
        ]
        cycloid = Cycloid()
        self.align_paths(paths, cycloid)
        return paths + [cycloid]

    def align_paths(self, paths, target_path):
        def path_displacement(path):
            return path.points[-1]-path.points[0]
        target = path_displacement(target_path)
        for path in paths:
            vect = path_displacement(path)
            path.scale(np.linalg.norm(target)/np.linalg.norm(vect))
            path.rotate(
                angle_of_vector(target) - \
                angle_of_vector(vect)
            )
            path.shift(target_path.points[0]-path.points[0])


class RollingRandolph(PathSlidingScene):
    def construct(self):
        cycloid = Cycloid()
        point_a = Dot(cycloid.points[0])
        point_b = Dot(cycloid.points[-1])
        A = TexMobject("A").next_to(point_a, LEFT)
        B = TexMobject("B").next_to(point_b, RIGHT)
        randy = Randolph()
        randy.scale(RANDY_SCALE_VAL)
        randy.shift(-randy.get_bottom())

        self.add(point_a, point_b, A, B, cycloid)
        self.slide(randy, cycloid, roll = True)



class SimplePhoton(Scene):
    def construct(self):
        photon = wavify(Cycloid())
        photon.highlight(YELLOW)
        shaddow = photon.copy().highlight(BLACK)

        self.play(
            ShowCreation(photon, rate_func = None),
            ShowCreation(
                shaddow,
                rate_func = lambda t : max(0, t-0.1)
            )
        )
        self.dither()















