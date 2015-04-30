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

    def rotate_in_place(self, angle, axis = [0, 0, 1]):
        center = self.get_center()
        self.shift(-center)
        self.rotate(angle, axis)
        self.shift(center)
        return self

    def shift(self, vector):
        cycle = it.cycle(vector)
        v = np.array([cycle.next() for x in range(self.points.size)]).reshape(self.points.shape)
        self.points += v
        return self

    def center(self):
        self.shift(-self.get_center())
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

    def get_num_points(self):
        return self.points.shape[0]

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

    def fade(self, amount = 0.5):
        self.rgbs *= amount
        return self

    def filter_out(self, condition):
        to_eliminate = ~np.apply_along_axis(condition, 1, self.points)
        self.points = self.points[to_eliminate]
        self.rgbs   = self.rgbs[to_eliminate]
        return self

    ### Getters ###
    def get_center(self):
        return np.apply_along_axis(np.mean, 0, self.points)

    def get_width(self):
        return np.max(self.points[:, 0]) - np.min(self.points[:, 0])

    def get_height(self):
        return np.max(self.points[:, 1]) - np.min(self.points[:, 1])

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
        for mobject in mobjects:
            self.add_points(mobject.points, mobject.rgbs)


###### Concrete Mobjects ########

class Stars(Mobject):
    DEFAULT_COLOR = "white"
    SHOULD_BUFF_POINTS = False
    def __init__(self, num_points = DEFAULT_NUM_STARS, 
                 *args, **kwargs):
        self.num_points = num_points
        Mobject.__init__(self, *args, **kwargs)

    def generate_points(self):
        self.add_points([
            (
                r * np.sin(phi)*np.cos(theta), 
                r * np.sin(phi)*np.sin(theta), 
                r * np.cos(phi)
            )
            for x in range(self.num_points)
            for r, phi, theta in [[
                max(SPACE_HEIGHT, SPACE_WIDTH) * random(),
                np.pi * random(),
                2 * np.pi * random(),
            ]]
        ])

class Point(Mobject):
    def __init__(self, point = (0, 0, 0), *args, **kwargs):
        Mobject.__init__(self, *args, **kwargs)
        self.points = np.array(point).reshape(1, 3)
        self.rgbs = np.array(self.color.get_rgb()).reshape(1, 3)

class Arrow(Mobject1D):
    DEFAULT_COLOR = "white"
    NUNGE_DISTANCE = 0.1
    def __init__(self, point = (0, 0, 0), direction = (-1, 1, 0), 
                 length = 1, tip_length = 0.25,
                 normal = (0, 0, 1), *args, **kwargs):
        self.point = np.array(point)
        self.direction = np.array(direction) / np.linalg.norm(direction)
        self.normal = np.array(normal)
        self.length = length
        self.tip_length = tip_length
        Mobject1D.__init__(self, *args, **kwargs)

    def generate_points(self):
        self.add_points([
            [x, x, x] * self.direction + self.point
            for x in np.arange(-self.length, 0, self.epsilon)
        ])
        tips_dir = np.array(-self.direction), np.array(-self.direction)
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
    def __init__(self, center = (0, 0, 0), radius = 0.05, *args, **kwargs):
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
            for t in np.arange(0, self.radius, self.epsilon)
            for theta in np.arange(0, 2 * np.pi, self.epsilon)
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
        density *= np.linalg.norm(self.start - self.end)
        Mobject1D.__init__(self, density = density, *args, **kwargs)

    def generate_points(self):
        self.add_points([
            t * self.end + (1 - t) * self.start
            for t in np.arange(0, 1, self.epsilon)
        ])

class CurvedLine(Line):
    def generate_points(self):
        equidistant_point = rotate_vector(
            self.end - self.start, 
            np.pi/3, [0,0,1]
        ) + self.start
        self.add_points([
            (1 - t*(1-t))*(t*self.end + (1-t)*self.start) \
            +    t*(1-t)*equidistant_point
            for t in np.arange(0, 1, self.epsilon)
        ])
        self.ep = equidistant_point

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

    def unit_normal(self, coords):
        return np.array(map(lambda x : 1 if abs(x) == 1 else 0, coords))

class Cube(Mobject1D):
    DEFAULT_COLOR = "yellow"
    def generate_points(self):
        self.add_points([
            ([a, b, c][p[0]], [a, b, c][p[1]], [a, b, c][p[2]])
            for p in [(0, 1, 2), (2, 0, 1), (1, 2, 0)]
            for a, b, c in it.product([-1, 1], [-1, 1], np.arange(-1, 1, self.epsilon))
        ])
        self.pose_at_angle()


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

    def unit_normal(self, coords):
        return np.array(coords) / np.linalg.norm(coords)

class Circle(Mobject1D):
    DEFAULT_COLOR = "red"
    def generate_points(self):
        self.add_points([
            (np.cos(theta), np.sin(theta), 0)
            for theta in np.arange(0, 2 * np.pi, self.epsilon)
        ])

class FunctionGraph(Mobject1D):
    DEFAULT_COLOR = "lightblue"
    def __init__(self, function, x_range = [-10, 10], *args, **kwargs):
        self.function = function
        self.x_min = x_range[0] / SPACE_WIDTH
        self.x_max = x_range[1] / SPACE_WIDTH
        Mobject1D.__init__(self, *args, **kwargs)

    def generate_points(self):
        scale_factor = 2.0 * SPACE_WIDTH / (self.x_max - self.x_min)
        self.epsilon /= scale_factor
        self.add_points([
            np.array([x, self.function(x), 0])
            for x in np.arange(self.x_min, self.x_max, self.epsilon)
        ])
        self.scale(scale_factor)


class ParametricFunction(Mobject):
    DEFAULT_COLOR = "lightblue"
    def __init__(self, 
                 function, 
                 dim = 1, 
                 expected_measure = 10.0, 
                 density = None,
                 *args, 
                 **kwargs):
        self.function = function
        self.dim = dim
        self.expected_measure = expected_measure
        if density:
            self.epsilon = 1.0 / density
        elif self.dim == 1:
            self.epsilon = 1.0 / expected_measure / DEFAULT_POINT_DENSITY_1D
        else:
            self.epsilon = 1.0 / np.sqrt(expected_measure) / DEFAULT_POINT_DENSITY_2D
        Mobject.__init__(self, *args, **kwargs)

    def generate_points(self):
        if self.dim == 1:
            self.add_points([
                self.function(t)
                for t in np.arange(-1, 1, self.epsilon)
            ])
        if self.dim == 2:
            self.add_points([
                self.function(s, t)
                for t in np.arange(-1, 1, self.epsilon)
                for s in np.arange(-1, 1, self.epsilon)
            ])

class Grid(Mobject1D):
    DEFAULT_COLOR = "green"
    def __init__(self, 
                 radius = max(SPACE_HEIGHT, SPACE_WIDTH), 
                 interval_size = 1.0,
                 subinterval_size = 0.5,
                 *args, **kwargs):
        self.radius = radius
        self.interval_size = interval_size
        self.subinterval_size = subinterval_size
        Mobject1D.__init__(self, *args, **kwargs)

    def generate_points(self):
        self.add_points([
            (sgns[0] * x, sgns[1] * y, 0)
            for beta in np.arange(0, self.radius, self.interval_size)
            for alpha in np.arange(0, self.radius, self.epsilon)
            for sgns in it.product((-1, 1), (-1, 1))
            for x, y in [(alpha, beta), (beta, alpha)]
        ])
        if self.subinterval_size:
            si = self.subinterval_size
            color = Color(self.color)
            color.set_rgb([x/2 for x in color.get_rgb()])
            self.add_points([
                (sgns[0] * x, sgns[1] * y, 0)
                for beta in np.arange(0, self.radius, si)
                if abs(beta % self.interval_size) > self.epsilon
                for alpha in np.arange(0, self.radius, self.epsilon)
                for sgns in it.product((-1, 1), (-1, 1))
                for x, y in [(alpha, beta), (beta, alpha)]
            ], color = color)

class NumberLine(Mobject1D):
    def __init__(self, 
                 radius = SPACE_WIDTH,
                 interval_size = 0.5, tick_size = 0.1, 
                 with_numbers = False, *args, **kwargs):
        self.radius = int(radius) + 1
        self.interval_size = interval_size
        self.tick_size = tick_size
        self.with_numbers = with_numbers
        Mobject1D.__init__(self, *args, **kwargs)

    def generate_points(self):
        self.add_points([
            (x, 0, 0)
            for x in np.arange(-self.radius, self.radius, self.epsilon)
        ])
        self.add_points([
            (0, y, 0)
            for y in np.arange(-2*self.tick_size, 2*self.tick_size, self.epsilon)
        ])
        self.add_points([
            (x, y, 0)
            for x in np.arange(-self.radius, self.radius, self.interval_size)
            for y in np.arange(-self.tick_size, self.tick_size, self.epsilon)
        ])
        if self.with_numbers: 
            #TODO, test
            vertical_displacement = -0.3
            nums = range(-self.radius, self.radius)
            nums = map(lambda x : x / self.interval_size, nums)
            mobs = tex_mobjects(*[str(num) for num in nums])
            for num, mob in zip(nums, mobs):
                mob.center().shift([num, vertical_displacement, 0])
            self.add(*mobs)

# class ComplexPlane(Grid):
#     def __init__(self, *args, **kwargs):
#         Grid.__init__(self, *args, **kwargs)
#         self.add(Dot())