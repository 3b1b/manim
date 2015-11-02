import numpy as np
import itertools as it
import operator as op
import os
from PIL import Image
from random import random
from copy import deepcopy
from colour import Color
import inspect

import displayer as disp
from helpers import *


class Mobject(object):
    """
    Mathematical Object
    """
    #Number of numbers used to describe a point (3 for pos, 3 for normal vector)
    DEFAULT_CONFIG = {
        "color" : WHITE,
        "point_thickness" : DEFAULT_POINT_THICKNESS,
        "name" : None,
    }
    DIM = 3
    def __init__(self, *sub_mobjects, **kwargs):
        digest_config(self, kwargs)
        self.sub_mobjects = list(sub_mobjects)
        self.color = Color(self.color)
        if self.name is None:
            self.name = self.__class__.__name__
        self.has_normals = hasattr(self, 'unit_normal')
        self.init_points()
        self.generate_points()
        if self.has_normals:
            self.unit_normals = np.apply_along_axis(
                self.unit_normal,
                1,
                self.points,
            )

    def init_points(self):
        for attr in self.get_array_attrs():
            setattr(self, attr, np.zeros((0, 3)))

    def __str__(self):
        return self.name

    def add_points(self, points, rgbs = None, color = None):
        """
        points must be a Nx3 numpy array, as must rgbs if it is not None
        """
        if not isinstance(points, np.ndarray):
            points = np.array(points)
        num_new_points = points.shape[0]
        self.points = np.append(self.points, points, axis = 0)
        if rgbs is None:
            color = Color(color) if color else self.color
            rgbs = np.array([color.get_rgb()] * num_new_points)
        elif rgbs.shape != points.shape:
            raise Exception("points and rgbs must have same shape")
        self.rgbs = np.append(self.rgbs, rgbs, axis = 0)
        if self.has_normals:
            self.unit_normals = np.append(
                self.unit_normals,
                np.apply_along_axis(self.unit_normal, 1, points),
                axis = 0
            )
        return self

    def add(self, *mobjects):
        self.sub_mobjects = list_update(self.sub_mobjects, mobjects)
        return self

    def get_array_attrs(self):
        result = ["points", "rgbs"]
        if self.has_normals:
            result.append("unit_normals")
        return result

    def digest_mobject_attrs(self):
        """
        Ensures all attributes which are mobjects are included
        in the sub_mobjects list.
        """
        mobject_attrs = filter(
            lambda x : isinstance(x, Mobject),
            self.__dict__.values()
        )
        self.sub_mobjects = list_update(self.sub_mobjects, mobject_attrs)
        return self


    def apply_over_attr_arrays(self, func):
        for attr in self.get_array_attrs():
            setattr(self, attr, func(getattr(self, attr)))
        return self

    def show(self):
        Image.fromarray(disp.paint_mobject(self)).show()

    def save_image(self, name = None):
        Image.fromarray(disp.paint_mobject(self)).save(
            os.path.join(MOVIE_DIR, (name or str(self)) + ".png")
        )


    #### Fundamental operations ######

    def shift(self, *vectors):
        total_vector = reduce(op.add, vectors)
        for mob in self.get_full_submobject_family():        
            mob.points += total_vector
        return self

    def scale(self, scale_factor):
        for mob in self.get_full_submobject_family():
            mob.points *= scale_factor
        return self

    def rotate(self, angle, axis = OUT):
        t_rotation_matrix = np.transpose(rotation_matrix(angle, axis))
        for mob in self.get_full_submobject_family():
            mob.points = np.dot(mob.points, t_rotation_matrix)
            if mob.has_normals:
                mob.unit_normals = np.dot(mob.unit_normals, t_rotation_matrix)
        return self

    def stretch(self, factor, dim):
        for mob in self.get_full_submobject_family():
            mob.points[:,dim] *= factor
        return self

    def apply_function(self, function):
        for mob in self.get_full_submobject_family():
            mob.points = np.apply_along_axis(function, 1, mob.points)
        return self

    def wag(self, direction = RIGHT, axis = DOWN, wag_factor = 1.0):
        for mob in self.get_full_submobject_family():
            alphas = np.dot(mob.points, np.transpose(axis))
            alphas -= min(alphas)
            alphas /= max(alphas)
            alphas = alphas**wag_factor
            mob.points += np.dot(
                alphas.reshape((len(alphas), 1)),
                np.array(direction).reshape((1, mob.DIM))
            )
        return self

    def highlight(self, color = "yellow", condition = None):
        """
        Condition is function which takes in one arguments, (x, y, z).
        """
        rgb = Color(color).get_rgb()
        for mob in self.get_full_submobject_family():
            if condition:
                to_change = np.apply_along_axis(condition, 1, mob.points)
                mob.rgbs[to_change, :] = rgb
            else:
                mob.rgbs[:,:] = rgb
        return self

    def filter_out(self, condition):
        for mob in self.get_full_submobject_family():
            to_eliminate = ~np.apply_along_axis(condition, 1, mob.points)
            mob.points = mob.points[to_eliminate]
            mob.rgbs = mob.rgbs[to_eliminate]
        return self

    def sort_points(self, function = lambda p : p[0]):
        """
        function is any map from R^3 to R
        """
        for mob in self.get_full_submobject_family():
            indices = range(len(mob.points))
            indices.sort(
                lambda *pair : cmp(*map(function, mob.points[pair, :]))
            )
            mob.points = mob.points[indices]
            mob.rgbs   = mob.rgbs[indices]
        return self

    def repeat(self, count):
        """
        This can make transition animations nicer
        """
        def repeat_array(array):
            return reduce(
                lambda a1, a2 : np.append(a1, a2, axis = 0),
                [array]*count
            )
        for mob in self.get_full_submobject_family():
            mob.apply_over_attr_arrays(repeat_array)
        return self

    #### In place operations ######

    def do_in_place(self, method, *args, **kwargs):
        center = self.get_center()
        self.shift(-center)
        method(*args, **kwargs)
        self.shift(center)
        return self

    def rotate_in_place(self, angle, axis = OUT):
        self.do_in_place(self.rotate, angle, axis)
        return self

    def scale_in_place(self, scale_factor):
        self.do_in_place(self.scale, scale_factor)
        return self

    def pose_at_angle(self):
        self.rotate_in_place(np.pi / 7, RIGHT+UP)
        return self

    def center(self):
        self.shift(-self.get_center())
        return self

    def align_on_border(self, direction, buff = DEFAULT_MOBJECT_TO_EDGE_BUFFER):
        """
        Direction just needs to be a vector pointing towards side or
        corner in the 2d plane.
        """
        target_point = np.sign(direction) * (SPACE_WIDTH, SPACE_HEIGHT, 0)
        anchor_point = self.get_critical_point(direction)
        self.shift(target - anchor_point - buff * np.array(direction))
        return self

    def to_corner(self, corner = LEFT+DOWN, buff = DEFAULT_MOBJECT_TO_EDGE_BUFFER):
        return self.align_on_border(corner, buff)

    def to_edge(self, edge = LEFT, buff = DEFAULT_MOBJECT_TO_EDGE_BUFFER):
        return self.align_on_border(edge, buff)

    def next_to(self, mobject, 
                direction = RIGHT, 
                buff = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
                aligned_edge = ORIGIN):
        anchor_point = self.get_critical_point(aligned_edge-direction)
        target_point = mobject.get_critical_point(aligned_edge+direction)
        self.shift(target_point - anchor_point + buff*direction)
        return self

    def stretch_to_fit(self, length, dim):
        old_length = self.length_over_dim(dim)
        self.do_in_place(self.stretch, length/old_length, dim)
        return self

    def stretch_to_fit_width(self, width):
        return self.stretch_to_fit(width, 0)

    def stretch_to_fit_height(self, height):
        return self.stretch_to_fit(height, 1)

    def scale_to_fit_width(self, width):
        return self.scale(width/self.get_width())

    def scale_to_fit_height(self, height):
        return self.scale(height/self.get_height())

    def replace(self, mobject, stretch = False):
        if mobject.get_num_points() == 0:
            raise Warning("Attempting to replace mobject with no points")
            return self
        if stretch:
            self.stretch_to_fit_width(mobject.get_width())
            self.stretch_to_fit_height(mobject.get_height())
        else:
            self.scale(mobject.get_width()/self.get_width())
        self.center().shift(mobject.get_center())
        return self

    def apply_complex_function(self, function):
        return self.apply_function(
            lambda (x, y, z) : complex_to_R3(function(complex(x, y)))
        )

    def set_color(self, color):
        self.highlight(color)
        self.color = Color(color)
        return self

    def to_original_color(self):
        self.highlight(self.color)
        return self

    def fade_to(self, color, alpha):
        self.rgbs = interpolate(self.rgbs, Color(color).rgb, alpha)
        for mob in self.sub_mobjects:
            mob.fade_to(color, alpha)
        return self

    def fade(self, brightness = 0.5):
        self.fade_to(BLACK, brightness)
        return self

    def reduce_across_dimension(self, points_func, reduce_func, dim):
        try:
            values = [points_func(self.points[:, dim])]
        except:
            values = []
        values += [
            mob.reduce_across_dimension(points_func, reduce_func, dim)
            for mob in self.sub_mobjects
        ]
        try:
            return reduce_func(values)
        except:
            return 0

    def get_merged_array(self, array_attr):
        return reduce(
            lambda a1, a2 : np.append(a1, a2, axis = 0),
            [getattr(self, array_attr)] + [
                mob.get_merged_array(array_attr) 
                for mob in self.sub_mobjects
            ]
        )

    def get_all_points(self):
        return self.get_merged_array("points")

    def ingest_sub_mobjects(self):
        for attr in self.get_array_attrs():
            setattr(self, attr, self.get_merged_array(attr))
        self.sub_mobjects = []
        return self

    def split(self):
        result = [self] if len(self.points) > 0 else []
        return result + self.sub_mobjects

    def get_full_submobject_family(self):
        sub_families = map(Mobject.get_full_submobject_family, self.sub_mobjects)
        all_mobjects = [self] + reduce(op.add, sub_families, [])
        return remove_list_redundancies(all_mobjects)

    ### Getters ###

    def get_num_points(self, including_submobjects = False):
        return self.reduce_across_dimension(len, sum, 0)

    def get_critical_point(self, direction):
        result = np.zeros(self.DIM)
        for dim in [0, 1]:
            if direction[dim] <= 0:
                min_point = self.reduce_across_dimension(np.min, np.min, dim)
            if direction[dim] >= 0:
                max_point = self.reduce_across_dimension(np.max, np.max, dim)

            if direction[dim] == 0:
                result[dim] = (max_point+min_point)/2
            elif direction[dim] < 0:
                result[dim] = min_point
            else:
                result[dim] = max_point
        return result

    # Pseudonyms for more general get_critical_point method
    def get_edge_center(self, direction):
        return self.get_critical_point(direction)

    def get_corner(self, direction):
        return self.get_critical_point(direction)

    def get_center(self):
        return self.get_critical_point(np.zeros(self.DIM))

    def get_center_of_mass(self):
        return np.apply_along_axis(np.mean, 0, self.get_all_points())

    def get_boundary_point(self, direction):
        all_points = self.get_all_points()
        return all_points[np.argmax(np.dot(all_points, direction))]

    def get_top(self):
        return self.get_edge_center(UP)

    def get_bottom(self):
        return self.get_edge_center(DOWN)

    def get_right(self):
        return self.get_edge_center(RIGHT)

    def get_left(self):
        return self.get_edge_center(LEFT)

    def length_over_dim(self, dim):
        return (
            self.reduce_across_dimension(np.max, np.max, dim) - 
            self.reduce_across_dimension(np.min, np.min, dim)
        )

    def get_width(self):
        return self.length_over_dim(0)

    def get_height(self):
        return self.length_over_dim(1)


    def get_color(self):
        color = Color()
        color.set_rgb(self.rgbs[0, :]) 
        return color

    ### Stuff subclasses should deal with ###
    def generate_points(self):
        #Typically implemented in subclass, unless purposefully left blank
        pass

    @staticmethod
    def align_data(mobject1, mobject2):
        count1 = len(mobject1.points)
        count2 = len(mobject2.points)
        if count1 != count2:
            if count1 < count2:
                smaller = mobject1
                target_size = count2
            else:
                smaller = mobject2
                target_size = count1
            if len(smaller.points) == 0:
                smaller.add_points([np.zeros(smaller.DIM)])
            smaller.apply_over_attr_arrays(
                lambda a : streth_array_to_length(a, target_size)
            )

        num_sub_mobjects1 = len(mobject1.sub_mobjects)
        num_sub_mobjects2 = len(mobject2.sub_mobjects)
        if num_sub_mobjects1 != num_sub_mobjects2:
            diff = abs(num_sub_mobjects1 - num_sub_mobjects2)
            if num_sub_mobjects1 < num_sub_mobjects2:
                larger, smaller = mobject2, mobject1
            else:
                larger, smaller = mobject1, mobject2
            for sub_mob in larger.sub_mobjects[-diff:]:
                center = sub_mob.get_center()
                point_distances = np.apply_along_axis(
                    lambda p : np.linalg.norm(p - center),
                    1, larger.points
                )
                index = np.argmin(point_distances)
                smaller.add(Point(
                    smaller.points[index],
                    color = Color(rgb = smaller.rgbs[index])
                ))
        for m1, m2 in zip(mobject1.sub_mobjects, mobject2.sub_mobjects):
            Mobject.align_data(m1, m2)

    def interpolate(self, mobject1, mobject2, alpha):
        """
        Turns target_mobject into an interpolation between mobject1 
        and mobject2.
        """
        #TODO
        Mobject.align_data(mobject1, mobject2)
        for attr in self.get_array_attrs():
            setattr(target_mobject, attr, interpolate(
                getattr(mobject1, attr), 
                getattr(mobject2, attr), 
            alpha))

#TODO, Make the two implementations bellow not redundant
class Mobject1D(Mobject):
    DEFAULT_CONFIG = {
        "density" : DEFAULT_POINT_DENSITY_1D,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        self.epsilon = 1.0 / self.density        
        Mobject.__init__(self, **kwargs)


    def add_line(self, start, end, min_density = 0.1, color = None):
        length = np.linalg.norm(end - start)
        epsilon = self.epsilon / max(length, min_density)
        self.add_points([
            interpolate(start, end, t)
            for t in np.arange(0, 1, epsilon)
        ], color = color)

class Mobject2D(Mobject):
    DEFAULT_CONFIG = {
        "density" : DEFAULT_POINT_DENSITY_2D,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        self.epsilon = 1.0 / self.density  
        Mobject.__init__(self, **kwargs)


class Point(Mobject):
    DEFAULT_CONFIG = {
        "color" : BLACK,
    }
    def __init__(self, location = ORIGIN, **kwargs):
        digest_locals(self)        
        Mobject.__init__(self, **kwargs)

    def generate_points(self):
        self.add_points([self.location])

















