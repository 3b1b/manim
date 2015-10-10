import numpy as np
import itertools as it
import operator as op
import os
from PIL import Image
from random import random
from copy import deepcopy
from colour import Color
import inspect


from constants import *
from helpers import *
import displayer as disp


class Mobject(object):
    """
    Mathematical Object
    """
    #Number of numbers used to describe a point (3 for pos, 3 for normal vector)
    DEFAULT_CONFIG = {
        "color" : "white",
        "point_thickness" : 2,
        "name" : None,
    }
    DIM = 3
    def __init__(self, **kwargs):
        digest_config(self, Mobject, kwargs)
        self.color = Color(self.color)
        if self.name is None:
            self.name = self.__class__.__name__
        self.has_normals = hasattr(self, 'unit_normal')
        self.init_points()
        self.generate_points()

    def init_points(self):
        self.points = np.zeros((0, 3))
        self.rgbs   = np.zeros((0, 3))
        if self.has_normals:
            self.unit_normals = np.zeros((0, 3))

    def __str__(self):
        return self.name

    def show(self):
        Image.fromarray(disp.paint_mobject(self)).show()

    def save_image(self, name = None):
        Image.fromarray(disp.paint_mobject(self)).save(
            os.path.join(MOVIE_DIR, (name or str(self)) + ".png")
        )

    def add_points(self, points, rgbs = None, color = None):
        """
        points must be a Nx3 numpy array, as must rgbs if it is not None
        """
        points = np.array(points)
        num_new_points = points.shape[0]
        self.points = np.append(self.points, points)
        self.points = self.points.reshape((self.points.size / 3, 3))
        if rgbs is None:
            color = Color(color) if color else self.color
            rgbs = np.array([color.get_rgb()] * num_new_points)
        else:
            if rgbs.shape != points.shape:
                raise Exception("points and rgbs must have same shape")
        self.rgbs = np.append(self.rgbs, rgbs)
        self.rgbs = self.rgbs.reshape((self.rgbs.size / 3, 3))
        if self.has_normals:
            self.unit_normals = np.append(
                self.unit_normals,
                np.array([self.unit_normal(point) for point in points])
            ).reshape(self.points.shape)
        return self

    def add(self, *mobjects):
        for mobject in mobjects:
            self.add_points(mobject.points, mobject.rgbs)
        return self


    def repeat(self, count):
        #Can make transition animations nicer
        points, rgbs = deepcopy(self.points), deepcopy(self.rgbs)
        for x in range(count - 1):
            self.add_points(points, rgbs)
        return self

    def do_in_place(self, method, *args, **kwargs):
        center = self.get_center()
        self.shift(-center)
        method(*args, **kwargs)
        self.shift(center)
        return self

    def rotate(self, angle, axis = OUT):
        t_rotation_matrix = np.transpose(rotation_matrix(angle, axis))
        self.points = np.dot(self.points, t_rotation_matrix)
        if self.has_normals:
            self.unit_normals = np.dot(self.unit_normals, t_rotation_matrix)
        return self

    def rotate_in_place(self, angle, axis = OUT):
        self.do_in_place(self.rotate, angle, axis)
        return self

    def shift(self, vector):
        self.points += vector
        return self

    def wag(self, wag_direction = RIGHT, wag_axis = DOWN,
            wag_factor = 1.0):
        alphas = np.dot(self.points, np.transpose(wag_axis))
        alphas -= min(alphas)
        alphas /= max(alphas)
        alphas = alphas**wag_factor
        self.points += np.dot(
            alphas.reshape((len(alphas), 1)),
            np.array(wag_direction).reshape((1, self.DIM))
        )
        return self

    def center(self):
        self.shift(-self.get_center())
        return self

    #Wrapper functions for better naming
    def to_corner(self, corner = LEFT+DOWN, buff = DEFAULT_MOBJECT_TO_EDGE_BUFFER):
        return self.align_on_border(corner, buff)

    def to_edge(self, edge = LEFT, buff = DEFAULT_MOBJECT_TO_EDGE_BUFFER):
        return self.align_on_border(edge, buff)

    def align_on_border(self, direction, buff = DEFAULT_MOBJECT_TO_EDGE_BUFFER):
        """
        Direction just needs to be a vector pointing towards side or
        corner in the 2d plane.
        """
        shift_val = np.zeros(3)
        space_dim = (SPACE_WIDTH, SPACE_HEIGHT)
        for i in [0, 1]:
            if direction[i] == 0:
                continue
            elif direction[i] > 0:
                shift_val[i] = space_dim[i]-buff-max(self.points[:,i])
            else:
                shift_val[i] = -space_dim[i]+buff-min(self.points[:,i])
        self.shift(shift_val)
        return self

    def next_to(self, mobject, 
                direction = RIGHT, 
                buff = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
                aligned_edge = None):
        if aligned_edge is not None:
            anchor_point = self.get_corner(aligned_edge-direction)
            target_point = mobject.get_corner(aligned_edge+direction)
        elif list(direction) in map(list, [LEFT, RIGHT, UP, DOWN]):
            anchor_point = self.get_edge_center(-direction)
            target_point = mobject.get_edge_center(direction)
        else:
            anchor_point = self.get_boundary_point(-direction)
            target_point = mobject.get_boundary_point(direction)
        self.shift(target_point - anchor_point + buff*direction)
        return self

    def scale(self, scale_factor):
        self.points *= scale_factor
        return self

    def scale_in_place(self, scale_factor):
        self.do_in_place(self.scale, scale_factor)
        return self

    def stretch(self, factor, dim):
        self.points[:,dim] *= factor
        return self

    def stretch_to_fit(self, length, dim):
        center = self.get_center()
        old_length = max(self.points[:,dim]) - min(self.points[:,dim])
        self.center()
        self.stretch(length/old_length, dim)
        self.shift(center)
        return self

    def stretch_to_fit_width(self, width):
        return self.stretch_to_fit(width, 0)

    def stretch_to_fit_height(self, height):
        return self.stretch_to_fit(height, 1)

    def pose_at_angle(self):
        self.rotate(np.pi / 7)
        self.rotate(np.pi / 7, [1, 0, 0])
        return self

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

    def apply_function(self, function):
        self.points = np.apply_along_axis(function, 1, self.points)
        return self

    def apply_complex_function(self, function):
        def point_map((x, y, z)):
            result = function(complex(x, y))
            return (result.real, result.imag, 0)
        return self.apply_function(point_map)

    def highlight(self, color = "yellow", condition = None):
        """
        Condition is function which takes in one arguments, (x, y, z).
        """
        rgb = Color(color).get_rgb()
        if condition:
            to_change = np.apply_along_axis(condition, 1, self.points)
            self.rgbs[to_change, :] = rgb
        else:
            self.rgbs[:,:] = rgb
        return self

    def set_color(self, color):
        self.highlight(color)
        self.color = Color(color)
        return self

    def to_original_color(self):
        self.highlight(self.color)
        return self

    def fade_to(self, color, alpha):
        self.rgbs = interpolate(self.rgbs, Color(color).rgb, alpha)
        return self

    def fade(self, brightness = 0.5):
        self.fade_to("black", brightness)
        return self

    def filter_out(self, condition):
        to_eliminate = ~np.apply_along_axis(condition, 1, self.points)
        self.points = self.points[to_eliminate]
        self.rgbs   = self.rgbs[to_eliminate]
        return self

    def sort_points(self, function = lambda p : p[0]):
        """
        function is any map from R^3 to R
        """
        indices = range(self.get_num_points())
        indices.sort(
            lambda *pair : cmp(*map(function, self.points[pair, :]))
        )
        self.points = self.points[indices]
        self.rgbs   = self.rgbs[indices]
        return self

    ### Getters ###

    def get_num_points(self):
        return len(self.points)

    def get_center(self):
        return (np.max(self.points, 0) + np.min(self.points, 0))/2.0

    def get_center_of_mass(self):
        return np.apply_along_axis(np.mean, 0, self.points)

    def get_boundary_point(self, direction):
        return self.points[np.argmax(np.dot(self.points, direction))]

    def get_edge_center(self, direction):
        dim = np.argmax(map(abs, direction))
        max_or_min_func = np.max if direction[dim] > 0 else np.min
        result = self.get_center()
        result[dim] = max_or_min_func(self.points[:,dim])
        return result

    def get_corner(self, direction):
        return sum([
            self.get_edge_center(RIGHT*direction[0]),
            self.get_edge_center(UP*direction[1]),
            -self.get_center()
        ])

    def get_top(self):
        return self.get_edge_center(UP)

    def get_bottom(self):
        return self.get_edge_center(DOWN)

    def get_right(self):
        return self.get_edge_center(RIGHT)

    def get_left(self):
        return self.get_edge_center(LEFT)

    def get_width(self):
        return np.max(self.points[:, 0]) - np.min(self.points[:, 0])

    def get_height(self):
        return np.max(self.points[:, 1]) - np.min(self.points[:, 1])

    def get_color(self):
        color = Color()
        color.set_rgb(self.rgbs[0, :]) 
        return color

    ### Stuff subclasses should deal with ###
    def generate_points(self):
        #Typically implemented in subclass, unless purposefully left blank
        pass

    ### Static Methods ###
    def align_data(mobject1, mobject2):
        count1, count2 = mobject1.get_num_points(), mobject2.get_num_points()
        if count1 == 0:
            mobject1.add_points([(0, 0, 0)])
        if count2 == 0:
            mobject2.add_points([(0, 0, 0)])
        if count1 == count2:
            return
        for attr in ['points', 'rgbs']:
            new_arrays = make_even(getattr(mobject1, attr), getattr(mobject2, attr))
            for array, mobject in zip(new_arrays, [mobject1, mobject2]):
                setattr(mobject, attr, np.array(array))

    def interpolate(mobject1, mobject2, target_mobject, alpha):
        """
        Turns target_mobject into an interpolation between mobject1 
        and mobject2.
        """
        Mobject.align_data(mobject1, mobject2)
        for attr in ['points', 'rgbs']:
            new_array = (1 - alpha) * getattr(mobject1, attr) + \
                              alpha * getattr(mobject2, attr)
            setattr(target_mobject, attr, new_array)

#TODO, Make the two implementations bellow not redundant
class Mobject1D(Mobject):
    DEFAULT_CONFIG = {
        "density" : DEFAULT_POINT_DENSITY_1D,
    }
    def __init__(self, **kwargs):
        digest_config(self, Mobject1D, kwargs)
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
        digest_config(self, Mobject1D, kwargs)
        self.epsilon = 1.0 / self.density
        Mobject.__init__(self, **kwargs)

class CompoundMobject(Mobject):
    def __init__(self, *mobjects):
        Mobject.__init__(self)
        self.original_mobs_num_points = []
        for mobject in mobjects:
            self.original_mobs_num_points.append(mobject.points.shape[0])
            self.add_points(mobject.points, mobject.rgbs)
        self.point_thickness = max([
            m.point_thickness 
            for m in mobjects
        ])

    def split(self):
        result = []
        curr = 0
        for num_points in self.original_mobs_num_points:
            result.append(Mobject().add_points(
                self.points[curr:curr+num_points, :],
                self.rgbs[curr:curr+num_points, :]
            ))
            curr += num_points
        return result

# class CompoundMobject(Mobject):
#     """
#     Treats a collection of mobjects as if they were one.

#     A weird form of inhertance is at play here...
#     """
#     def __init__(self, *mobjects):
#         Mobject.__init__(self)
#         self.mobjects = mobjects
#         name_to_method = dict(
#             inspect.getmembers(Mobject, predicate = inspect.ismethod)
#         )
#         names = name_to_method.keys()
#         #Most reductions take the form of mapping a given method across
#         #all constituent mobjects, then just returning self.
#         name_to_reduce = dict([
#             (name, lambda list : self)
#             for name in names
#         ])
#         name_to_reduce.update(self.get_special_reduce_functions())
#         def make_pseudo_method(name):
#             return lambda *args, **kwargs : name_to_reduce[name]([
#                 name_to_method[name](mob, *args, **kwargs)
#                 for mob in self.mobjects
#             ])
#         for name in names:
#             setattr(self, name, make_pseudo_method(name))

#     def show(self):


#     def get_special_reduce_functions(self):
#         return {}

#     def handle_method(self, method_name, *args, **kwargs):
#         pass





















