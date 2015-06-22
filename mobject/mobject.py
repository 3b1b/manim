import numpy as np
import itertools as it
import os
from PIL import Image
from random import random
from copy import deepcopy
from colour import Color

from constants import *
from helpers import *
import displayer as disp


class Mobject(object):
    """
    Mathematical Object
    """
    #Number of numbers used to describe a point (3 for pos, 3 for normal vector)
    DIM = 3

    DEFAULT_COLOR = Color("skyblue")

    SHOULD_BUFF_POINTS = GENERALLY_BUFF_POINTS

    def __init__(self, 
                 color = None,
                 name = None,
                 center = None,
                 ):
        self.color = Color(color) if color else Color(self.DEFAULT_COLOR)
        if not hasattr(self, "name"):
            self.name = name or self.__class__.__name__
        self.has_normals = hasattr(self, 'unit_normal')
        self.points = np.zeros((0, 3))
        self.rgbs   = np.zeros((0, 3))
        if self.has_normals:
            self.unit_normals = np.zeros((0, 3))
        self.generate_points()
        if center:
            self.center().shift(center)

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
        self.rgbs = np.append(self.rgbs, rgbs).reshape(self.points.shape)
        if self.has_normals:
            self.unit_normals = np.append(
                self.unit_normals,
                np.array([self.unit_normal(point) for point in points])
            ).reshape(self.points.shape)
        return self

    def rotate(self, angle, axis = [0, 0, 1]):
        t_rotation_matrix = np.transpose(rotation_matrix(angle, axis))
        self.points = np.dot(self.points, t_rotation_matrix)
        if self.has_normals:
            self.unit_normals = np.dot(self.unit_normals, t_rotation_matrix)
        return self

    def rotate_in_place(self, angle, axis = (0, 0, 1)):
        center = self.get_center()
        self.shift(-center)
        self.rotate(angle, axis)
        self.shift(center)
        return self

    def shift(self, vector):
        cycle = it.cycle(vector)
        v = np.array([
            cycle.next() 
            for x in range(self.points.size)
        ]).reshape(self.points.shape)
        self.points += v
        return self

    def wag(self, wag_direction = RIGHT, wag_axis = DOWN,
            wag_factor = 1.0):
        alphas = np.dot(self.points, np.transpose(wag_axis))
        alphas -= min(alphas)
        alphas /= max(alphas)
        alphas = alphas**wag_factor
        self.points += np.dot(
            alphas.reshape((len(alphas), 1)),
            np.array(wag_direction).reshape((1, 3))
        )
        return self

    def center(self):
        self.shift(-self.get_center())
        return self

    #To wrapper functions for better naming
    def to_corner(self, corner = (-1, 1, 0), buff = 0.5):
        return self.align_on_border(corner, buff)

    def to_edge(self, edge = (-1, 0, 0), buff = 0.5):
        return self.align_on_border(edge, buff)

    def align_on_border(self, direction, buff = 0.5):
        """
        Direction just needs to be a vector pointing towards side or
        corner in the 2d plane.
        """
        shift_val = [0, 0, 0]
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


    def scale(self, scale_factor):
        self.points *= scale_factor
        return self

    def scale_in_place(self, scale_factor):
        center = self.get_center()
        return self.center().scale(scale_factor).shift(center)

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

    def pose_at_angle(self):
        self.rotate(np.pi / 7)
        self.rotate(np.pi / 7, [1, 0, 0])
        return self

    def apply_function(self, function):
        self.points = np.apply_along_axis(function, 1, self.points)
        return self

    def apply_complex_function(self, function):
        def point_map((x, y, z)):
            result = function(complex(x, y))
            return (result.real, result.imag, 0)
        return self.apply_function(point_map)

    def highlight(self, color = "red", condition = lambda x : True):
        """
        Condition is function which takes in one arguments, (x, y, z).
        """
        #TODO, Should self.color change?
        to_change = np.apply_along_axis(condition, 1, self.points)
        self.rgbs[to_change, :] *= 0
        self.rgbs[to_change, :] += Color(color).get_rgb()
        return self

    def fade(self, brightness = 0.5):
        self.rgbs *= brightness
        return self

    def filter_out(self, condition):
        to_eliminate = ~np.apply_along_axis(condition, 1, self.points)
        self.points = self.points[to_eliminate]
        self.rgbs   = self.rgbs[to_eliminate]
        return self

    ### Getters ###

    def get_num_points(self):
        return self.points.shape[0]

    def get_center(self):
        return np.apply_along_axis(np.mean, 0, self.points)

    def get_width(self):
        return np.max(self.points[:, 0]) - np.min(self.points[:, 0])

    def get_height(self):
        return np.max(self.points[:, 1]) - np.min(self.points[:, 1])

    def get_color(self):
        color = Color()
        color.set_rgb(self.rgbs[0, :]) 
        return color

    ### Stuff subclasses should deal with ###
    def should_buffer_points(self):
        # potentially changed in subclasses
        return GENERALLY_BUFF_POINTS

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

class Mobject1D(Mobject):
    def __init__(self, density = DEFAULT_POINT_DENSITY_1D, *args, **kwargs):
        self.epsilon = 1.0 / density

        Mobject.__init__(self, *args, **kwargs)

class Mobject2D(Mobject):
    def __init__(self, density = DEFAULT_POINT_DENSITY_2D, *args, **kwargs):
        self.epsilon = 1.0 / density
        Mobject.__init__(self, *args, **kwargs)

class CompoundMobject(Mobject):
    def __init__(self, *mobjects):
        Mobject.__init__(self)
        self.original_mobs_num_points = []
        for mobject in mobjects:
            self.original_mobs_num_points.append(mobject.points.shape[0])
            self.add_points(mobject.points, mobject.rgbs)

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


