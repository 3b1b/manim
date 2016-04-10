import numpy as np
import operator as op
import os
from PIL import Image
from copy import deepcopy
from colour import Color

from helpers import *


#TODO: Explain array_attrs

class Mobject(object):
    """
    Mathematical Object

    """
    #Number of numbers used to describe a point (3 for pos, 3 for normal vector)
    CONFIG = {
        "color" : WHITE,
        "point_thickness" : DEFAULT_POINT_THICKNESS,
        "name" : None,
        "display_mode" : "points", #TODO, REMOVE
        "dim" : 3,
    }
    def __init__(self, *sub_mobjects, **kwargs):
        digest_config(self, kwargs)
        self.sub_mobjects = list(sub_mobjects)
        self.color = Color(self.color)
        if self.name is None:
            self.name = self.__class__.__name__
        self.init_points()
        self.init_colors()
        self.generate_points()

    def __str__(self):
        return self.name

    def init_points(self):
        self.points = np.zeros((0, self.dim))

    def init_colors(self):
        #For subclasses
        pass

    def generate_points(self):
        #Typically implemented in subclass, unless purposefully left blank
        pass

    def add(self, *mobjects):
        self.sub_mobjects = list_update(self.sub_mobjects, mobjects)
        return self

    def get_array_attrs(self):
        return ["points"]

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

    def get_image(self):
        from camera import Camera
        camera = Camera()
        camera.capture_mobject(self)
        return Image.fromarray(camera.get_image())

    def show(self):
        self.get_image().show()

    def save_image(self, name = None):
        self.get_image().save(
            os.path.join(MOVIE_DIR, (name or str(self)) + ".png")
        )

    def copy(self):
        return deepcopy(self)

    #### Transforming operations ######

    def apply_to_family(self, func):
        for mob in self.nonempty_family_members():
            func(mob)

    def shift(self, *vectors):
        total_vector = reduce(op.add, vectors)
        for mob in self.nonempty_family_members():        
           mob.points += total_vector
        return self        


    def scale(self, scale_factor):
        for mob in self.nonempty_family_members():
            mob.points *= scale_factor
        return self

    def rotate(self, angle, axis = OUT, axes = []):
        if len(axes) == 0:
            axes = [axis]
        rot_matrix = np.identity(self.DIM)
        for axis in axes:
            rot_matrix = np.dot(rot_matrix, rotation_matrix(angle, axis))
        t_rot_matrix = np.transpose(rot_matrix)
        for mob in self.nonempty_family_members():
            mob.points = np.dot(mob.points, t_rot_matrix)
        return self

    def stretch(self, factor, dim):
        for mob in self.nonempty_family_members():
            mob.points[:,dim] *= factor
        return self

    def apply_function(self, function):
        for mob in self.nonempty_family_members():
            mob.points = np.apply_along_axis(function, 1, mob.points)
        return self

    def wag(self, direction = RIGHT, axis = DOWN, wag_factor = 1.0):
        for mob in self.nonempty_family_members():
            alphas = np.dot(mob.points, np.transpose(axis))
            alphas -= min(alphas)
            alphas /= max(alphas)
            alphas = alphas**wag_factor
            mob.points += np.dot(
                alphas.reshape((len(alphas), 1)),
                np.array(direction).reshape((1, mob.DIM))
            )
        return self

    def reverse_points(self):
        for mob in self.nonempty_family_members():
            mob.apply_over_attr_arrays(
                lambda arr : np.array(list(reversed(arr)))
            )
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
        for mob in self.nonempty_family_members():
            mob.apply_over_attr_arrays(repeat_array)
        return self

    #### In place operations ######

    def do_in_place(self, method, *args, **kwargs):
        center = self.get_center()
        self.shift(-center)
        method(*args, **kwargs)
        self.shift(center)
        return self

    def rotate_in_place(self, angle, axis = OUT, axes = []):
        self.do_in_place(self.rotate, angle, axis, axes)
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
        shift_val = target_point - anchor_point - buff * np.array(direction) 
        shift_val = shift_val * abs(np.sign(direction))
        self.shift(shift_val)
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
        if not mobject.get_num_points() and not mobject.sub_mobjects:
            raise Warning("Attempting to replace mobject with no points")
            return self
        if stretch:
            self.stretch_to_fit_width(mobject.get_width())
            self.stretch_to_fit_height(mobject.get_height())
        else:
            self.scale(mobject.get_width()/self.get_width())
        self.center().shift(mobject.get_center())
        return self

    def position_endpoints_on(self, start, end):
        curr_vect = self.points[-1] - self.points[0]
        if np.all(curr_vect == 0):
            raise Exception("Cannot position endpoints of closed loop")
        target_vect = end - start
        self.scale(np.linalg.norm(target_vect)/np.linalg.norm(curr_vect))
        self.rotate(
            angle_of_vector(target_vect) - \
            angle_of_vector(curr_vect)
        )
        self.shift(start-self.points[0])
        return self

    ## Color functions

    def highlight(self, color = YELLOW_C, condition = None):
        """
        Condition is function which takes in one arguments, (x, y, z).
        """
        raise Exception("Not implemented")

    def gradient_highlight(self, start_color, end_color):
        raise Exception("Not implemented")        

    def set_color(self, color):
        self.highlight(color)
        self.color = Color(color)
        return self

    def to_original_color(self):
        self.highlight(self.color)
        return self

    def fade_to(self, color, alpha):
        start = color_to_rgb(self.get_color())
        end = color_to_rgb(color)
        new_rgb = interpolate(start, end, alpha)
        for mob in self.nonempty_family_members():
            mob.highlight(Color(rgb = new_rgb))
        return self

    def fade(self, darkness = 0.5):
        self.fade_to(BLACK, darkness)
        return self

    def get_color(self):
        return self.color
    ##


    def apply_complex_function(self, function):
        return self.apply_function(
            lambda (x, y, z) : complex_to_R3(function(complex(x, y)))
        )

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
        result = np.zeros((0, self.DIM))
        for mob in self.nonempty_family_members():
            result = np.append(result, getattr(mob, array_attr), 0)
        return result

    def get_all_points(self):
        return self.get_merged_array("points")

    ### Getters ###

    def get_num_points(self, including_submobjects = False):
        if including_submobjects:
            return self.reduce_across_dimension(len, sum, 0)
        else:
            return len(self.points)

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

    def point_from_proportion(self, alpha):
        raise Exception("Not implemented")


    ## Family matters        

    def split(self):
        result = [self] if len(self.points) > 0 else []
        return result + self.sub_mobjects

    def submobject_family(self):
        sub_families = map(Mobject.submobject_family, self.sub_mobjects)
        all_mobjects = [self] + reduce(op.add, sub_families, [])
        return remove_list_redundancies(all_mobjects)

    def nonempty_family_members(self):
        return filter(
            lambda m : m.get_num_points() > 0, 
            self.submobject_family()
        )

    ## Alignment                

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
                smaller.add_points(
                    [np.zeros(smaller.DIM)],
                    color = BLACK
                )
            smaller.apply_over_attr_arrays(
                lambda a : streth_array_to_length(a, target_size)
            )
        #Recurse
        diff = len(mobject1.sub_mobjects) - len(mobject2.sub_mobjects)
        
        if diff < 0:
            larger, smaller = mobject2, mobject1
        elif diff > 0:
            larger, smaller = mobject1, mobject2
        if diff != 0:            
            for sub_mob in larger.sub_mobjects[-abs(diff):]:
                smaller.add(Point(sub_mob.get_center()))
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
            setattr(self, attr, interpolate(
                getattr(mobject1, attr), 
                getattr(mobject2, attr), 
            alpha))           

















