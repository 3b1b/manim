from functools import reduce
import copy
import itertools as it
import operator as op
import random
import sys
import moderngl

import numpy as np

from manimlib.constants import *
from manimlib.utils.color import color_gradient
from manimlib.utils.color import get_colormap_list
from manimlib.utils.color import rgb_to_hex
from manimlib.utils.color import color_to_rgb
from manimlib.utils.config_ops import digest_config
from manimlib.utils.iterables import batch_by_property
from manimlib.utils.iterables import list_update
from manimlib.utils.iterables import resize_array
from manimlib.utils.iterables import resize_preserving_order
from manimlib.utils.bezier import interpolate
from manimlib.utils.paths import straight_path
from manimlib.utils.simple_functions import get_parameters
from manimlib.utils.space_ops import angle_of_vector
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import rotation_matrix_transpose
from manimlib.shader_wrapper import ShaderWrapper
from manimlib.shader_wrapper import get_colormap_code


# TODO: Explain array_attrs
# TODO: Incorporate shader defaults

class Mobject(object):
    """
    Mathematical Object
    """
    CONFIG = {
        "color": WHITE,
        "opacity": 1,
        "dim": 3,  # TODO, get rid of this
        # Lighting parameters
        # Positive gloss up to 1 makes it reflect the light.
        "gloss": 0.0,
        # Positive shadow up to 1 makes a side opposite the light darker
        "shadow": 0.0,
        # For shaders
        "shader_folder": "",
        "render_primitive": moderngl.TRIANGLE_STRIP,
        "texture_paths": None,
        "depth_test": False,
        # If true, the mobject will not get rotated according to camera position
        "is_fixed_in_frame": False,
        # Must match in attributes of vert shader
        "shader_dtype": [
            ('point', np.float32, (3,)),
        ]
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        self.submobjects = []
        self.parents = []
        self.family = [self]

        self.init_data()
        self.init_updaters()
        self.init_points()
        self.init_colors()
        self.init_shader_data()

        if self.is_fixed_in_frame:
            self.fix_in_frame()
        if self.depth_test:
            self.apply_depth_test()

    def __str__(self):
        return self.__class__.__name__

    # Related to data dict
    def init_data(self):
        self.data = {
            "points": np.zeros((0, 3)),
            "rgbas": np.zeros((1, 4)),
        }

    def init_colors(self):
        self.set_color(self.color, self.opacity)

    def init_points(self):
        # Typically implemented in subclass, unlpess purposefully left blank
        pass

    def set_data(self, data):
        for key in data:
            self.data[key] = data[key]

    def resize_points(self, new_length, resize_func=resize_array):
        if new_length != len(self.data["points"]):
            self.data["points"] = resize_func(self.data["points"], new_length)

    def set_points(self, points):
        self.resize_points(len(points))
        self.data["points"][:] = points

    def append_points(self, new_points):
        self.resize_points(self.get_num_points() + len(new_points))
        self.data["points"][-len(new_points):] = new_points
        return self

    def get_points(self):
        return self.data["points"]

    def clear_points(self):
        self.resize_points(0)

    def get_num_points(self):
        return len(self.data["points"])
    #

    # Family matters
    def __getitem__(self, value):
        self_list = self.split()
        if isinstance(value, slice):
            GroupClass = self.get_group_class()
            return GroupClass(*self_list.__getitem__(value))
        return self_list.__getitem__(value)

    def __iter__(self):
        return iter(self.split())

    def __len__(self):
        return len(self.split())

    def split(self):
        result = [self] if self.get_num_points() > 0 else []
        return result + self.submobjects

    def assemble_family(self):
        sub_families = [sm.get_family() for sm in self.submobjects]
        self.family = [self, *it.chain(*sub_families)]
        self.refresh_has_updater_status()
        for parent in self.parents:
            parent.assemble_family()
        return self

    def get_family(self, recurse=True):
        return self.family if recurse else [self]

    def family_members_with_points(self):
        return [m for m in self.get_family() if m.has_points()]

    def add(self, *mobjects):
        if self in mobjects:
            raise Exception("Mobject cannot contain self")
        for mobject in mobjects:
            if mobject not in self.submobjects:
                self.submobjects.append(mobject)
            if self not in mobject.parents:
                mobject.parents.append(self)
        self.assemble_family()
        return self

    def remove(self, *mobjects):
        for mobject in mobjects:
            if mobject in self.submobjects:
                self.submobjects.remove(mobject)
            if self in mobject.parents:
                mobject.parents.remove(self)
        self.assemble_family()
        return self

    def add_to_back(self, *mobjects):
        self.set_submobjects(list_update(mobjects, self.submobjects))
        return self

    def replace_submobject(self, index, new_submob):
        old_submob = self.submobjects[index]
        if self in old_submob.parents:
            old_submob.parents.remove(self)
        self.submobjects[index] = new_submob
        self.assemble_family()
        return self

    def set_submobjects(self, submobject_list):
        self.remove(*self.submobjects)
        self.add(*submobject_list)
        return self

    def get_array_attrs(self):
        # May be more for other Mobject types
        return ["points"]

    def digest_mobject_attrs(self):
        """
        Ensures all attributes which are mobjects are included
        in the submobjects list.
        """
        mobject_attrs = [x for x in list(self.__dict__.values()) if isinstance(x, Mobject)]
        self.set_submobjects(list_update(self.submobjects, mobject_attrs))
        return self

    def apply_over_attr_arrays(self, func):
        for attr in self.get_array_attrs():
            setattr(self, attr, func(getattr(self, attr)))
        return self

    def copy(self):
        # TODO, either justify reason for shallow copy, or
        # remove this redundancy everywhere
        # return self.deepcopy()

        parents = self.parents
        self.parents = []
        copy_mobject = copy.copy(self)
        self.parents = parents

        copy_mobject.data = dict(self.data)
        for key in self.data:
            copy_mobject.data[key] = self.data[key].copy()
        copy_mobject.submobjects = []
        copy_mobject.add(*[sm.copy() for sm in self.submobjects])
        copy_mobject.match_updaters(self)

        # Make sure any mobject or numpy array attributes are copied
        family = self.get_family()
        for attr, value in list(self.__dict__.items()):
            if isinstance(value, Mobject) and value in family and value is not self:
                setattr(copy_mobject, attr, value.copy())
            if isinstance(value, np.ndarray):
                setattr(copy_mobject, attr, value.copy())
            if isinstance(value, ShaderWrapper):
                setattr(copy_mobject, attr, value.copy())
        return copy_mobject

    def deepcopy(self):
        parents = self.parents
        self.parents = []
        result = copy.deepcopy(self)
        self.parents = parents
        return result

    def generate_target(self, use_deepcopy=False):
        self.target = None  # Prevent exponential explosion
        if use_deepcopy:
            self.target = self.deepcopy()
        else:
            self.target = self.copy()
        return self.target

    # Updating
    def init_updaters(self):
        self.time_based_updaters = []
        self.non_time_updaters = []
        self.has_updaters = False
        self.updating_suspended = False

    def update(self, dt=0, recursive=True):
        if not self.has_updaters or self.updating_suspended:
            return self
        for updater in self.time_based_updaters:
            updater(self, dt)
        for updater in self.non_time_updaters:
            updater(self)
        if recursive:
            for submob in self.submobjects:
                submob.update(dt, recursive)
        return self

    def get_time_based_updaters(self):
        return self.time_based_updaters

    def has_time_based_updater(self):
        return len(self.time_based_updaters) > 0

    def get_updaters(self):
        return self.time_based_updaters + self.non_time_updaters

    def get_family_updaters(self):
        return list(it.chain(*[sm.get_updaters() for sm in self.get_family()]))

    def add_updater(self, update_function, index=None, call_updater=True):
        if "dt" in get_parameters(update_function):
            updater_list = self.time_based_updaters
        else:
            updater_list = self.non_time_updaters

        if index is None:
            updater_list.append(update_function)
        else:
            updater_list.insert(index, update_function)

        self.refresh_has_updater_status()
        if call_updater:
            self.update()
        return self

    def remove_updater(self, update_function):
        for updater_list in [self.time_based_updaters, self.non_time_updaters]:
            while update_function in updater_list:
                updater_list.remove(update_function)
        return self

    def clear_updaters(self, recursive=True):
        self.time_based_updaters = []
        self.non_time_updaters = []
        if recursive:
            for submob in self.submobjects:
                submob.clear_updaters()
        self.suspend_updating(recursive)
        return self

    def match_updaters(self, mobject):
        self.clear_updaters()
        for updater in mobject.get_updaters():
            self.add_updater(updater)
        return self

    def suspend_updating(self, recursive=True):
        self.updating_suspended = True
        if recursive:
            for submob in self.submobjects:
                submob.suspend_updating(recursive)
        return self

    def resume_updating(self, recursive=True, call_updater=True):
        self.updating_suspended = False
        if recursive:
            for submob in self.submobjects:
                submob.resume_updating(recursive)
        for parent in self.parents:
            parent.resume_updating(recursive=False, call_updater=False)
        if call_updater:
            self.update(dt=0, recursive=recursive)
        return self

    def refresh_has_updater_status(self):
        self.has_updaters = len(self.get_family_updaters()) > 0
        return self

    # Transforming operations
    def apply_to_family(self, func):
        for mob in self.family_members_with_points():
            func(mob)

    def shift(self, *vectors):
        total_vector = reduce(op.add, vectors)
        for mob in self.get_family():
            mob.set_points(mob.get_points() + total_vector)
        return self

    def scale(self, scale_factor, **kwargs):
        """
        Default behavior is to scale about the center of the mobject.
        The argument about_edge can be a vector, indicating which side of
        the mobject to scale about, e.g., mob.scale(about_edge = RIGHT)
        scales about mob.get_right().

        Otherwise, if about_point is given a value, scaling is done with
        respect to that point.
        """
        self.apply_points_function(
            lambda points: scale_factor * points,
            **kwargs
        )
        return self

    def rotate_about_origin(self, angle, axis=OUT, axes=[]):
        return self.rotate(angle, axis, about_point=ORIGIN)

    def rotate(self, angle, axis=OUT, **kwargs):
        rot_matrix_T = rotation_matrix_transpose(angle, axis)
        self.apply_points_function(
            lambda points: np.dot(points, rot_matrix_T),
            **kwargs
        )
        return self

    def flip(self, axis=UP, **kwargs):
        return self.rotate(TAU / 2, axis, **kwargs)

    def stretch(self, factor, dim, **kwargs):
        def func(points):
            points[:, dim] *= factor
            return points
        self.apply_points_function(func, **kwargs)
        return self

    def apply_function(self, function, **kwargs):
        # Default to applying matrix about the origin, not mobjects center
        if len(kwargs) == 0:
            kwargs["about_point"] = ORIGIN
        self.apply_points_function(
            lambda points: np.array([function(p) for p in points]),
            **kwargs
        )
        return self

    def apply_function_to_position(self, function):
        self.move_to(function(self.get_center()))
        return self

    def apply_function_to_submobject_positions(self, function):
        for submob in self.submobjects:
            submob.apply_function_to_position(function)
        return self

    def apply_matrix(self, matrix, **kwargs):
        # Default to applying matrix about the origin, not mobjects center
        if ("about_point" not in kwargs) and ("about_edge" not in kwargs):
            kwargs["about_point"] = ORIGIN
        full_matrix = np.identity(self.dim)
        matrix = np.array(matrix)
        full_matrix[:matrix.shape[0], :matrix.shape[1]] = matrix
        self.apply_points_function(
            lambda points: np.dot(points, full_matrix.T),
            **kwargs
        )
        return self

    def apply_complex_function(self, function, **kwargs):
        def R3_func(point):
            x, y, z = point
            xy_complex = function(complex(x, y))
            return [
                xy_complex.real,
                xy_complex.imag,
                z
            ]
        return self.apply_function(R3_func)

    def wag(self, direction=RIGHT, axis=DOWN, wag_factor=1.0):
        for mob in self.family_members_with_points():
            alphas = np.dot(mob.get_points(), np.transpose(axis))
            alphas -= min(alphas)
            alphas /= max(alphas)
            alphas = alphas**wag_factor
            mob.set_points(mob.get_points() + np.dot(
                alphas.reshape((len(alphas), 1)),
                np.array(direction).reshape((1, mob.dim))
            ))
        return self

    def reverse_points(self):
        for mob in self.family_members_with_points():
            mob.apply_over_attr_arrays(lambda arr: arr[::-1])
        return self

    def repeat(self, count):
        """
        This can make transition animations nicer
        """
        for mob in self.family_members_with_points():
            mob.apply_over_attr_arrays(lambda arr: np.vstack([arr] * count))
        return self

    def apply_points_function(self, func, about_point=None, about_edge=None):
        if about_point is None:
            if about_edge is None:
                about_edge = ORIGIN
            about_point = self.get_bounding_box_point(about_edge)
        for mob in self.family_members_with_points():
            points = mob.get_points()
            points[:] = func(points - about_point) + about_point
        return self

    # Positioning methods
    def center(self):
        self.shift(-self.get_center())
        return self

    def align_on_border(self, direction, buff=DEFAULT_MOBJECT_TO_EDGE_BUFFER):
        """
        Direction just needs to be a vector pointing towards side or
        corner in the 2d plane.
        """
        target_point = np.sign(direction) * (FRAME_X_RADIUS, FRAME_Y_RADIUS, 0)
        point_to_align = self.get_bounding_box_point(direction)
        shift_val = target_point - point_to_align - buff * np.array(direction)
        shift_val = shift_val * abs(np.sign(direction))
        self.shift(shift_val)
        return self

    def to_corner(self, corner=LEFT + DOWN, buff=DEFAULT_MOBJECT_TO_EDGE_BUFFER):
        return self.align_on_border(corner, buff)

    def to_edge(self, edge=LEFT, buff=DEFAULT_MOBJECT_TO_EDGE_BUFFER):
        return self.align_on_border(edge, buff)

    def next_to(self, mobject_or_point,
                direction=RIGHT,
                buff=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
                aligned_edge=ORIGIN,
                submobject_to_align=None,
                index_of_submobject_to_align=None,
                coor_mask=np.array([1, 1, 1]),
                ):
        if isinstance(mobject_or_point, Mobject):
            mob = mobject_or_point
            if index_of_submobject_to_align is not None:
                target_aligner = mob[index_of_submobject_to_align]
            else:
                target_aligner = mob
            target_point = target_aligner.get_bounding_box_point(
                aligned_edge + direction
            )
        else:
            target_point = mobject_or_point
        if submobject_to_align is not None:
            aligner = submobject_to_align
        elif index_of_submobject_to_align is not None:
            aligner = self[index_of_submobject_to_align]
        else:
            aligner = self
        point_to_align = aligner.get_bounding_box_point(aligned_edge - direction)
        self.shift((target_point - point_to_align + buff * direction) * coor_mask)
        return self

    def shift_onto_screen(self, **kwargs):
        space_lengths = [FRAME_X_RADIUS, FRAME_Y_RADIUS]
        for vect in UP, DOWN, LEFT, RIGHT:
            dim = np.argmax(np.abs(vect))
            buff = kwargs.get("buff", DEFAULT_MOBJECT_TO_EDGE_BUFFER)
            max_val = space_lengths[dim] - buff
            edge_center = self.get_edge_center(vect)
            if np.dot(edge_center, vect) > max_val:
                self.to_edge(vect, **kwargs)
        return self

    def is_off_screen(self):
        if self.get_left()[0] > FRAME_X_RADIUS:
            return True
        if self.get_right()[0] < -FRAME_X_RADIUS:
            return True
        if self.get_bottom()[1] > FRAME_Y_RADIUS:
            return True
        if self.get_top()[1] < -FRAME_Y_RADIUS:
            return True
        return False

    def stretch_about_point(self, factor, dim, point):
        return self.stretch(factor, dim, about_point=point)

    def stretch_in_place(self, factor, dim):
        # Now redundant with stretch
        return self.stretch(factor, dim)

    def rescale_to_fit(self, length, dim, stretch=False, **kwargs):
        old_length = self.length_over_dim(dim)
        if old_length == 0:
            return self
        if stretch:
            self.stretch(length / old_length, dim, **kwargs)
        else:
            self.scale(length / old_length, **kwargs)
        return self

    def stretch_to_fit_width(self, width, **kwargs):
        return self.rescale_to_fit(width, 0, stretch=True, **kwargs)

    def stretch_to_fit_height(self, height, **kwargs):
        return self.rescale_to_fit(height, 1, stretch=True, **kwargs)

    def stretch_to_fit_depth(self, depth, **kwargs):
        return self.rescale_to_fit(depth, 1, stretch=True, **kwargs)

    def set_width(self, width, stretch=False, **kwargs):
        return self.rescale_to_fit(width, 0, stretch=stretch, **kwargs)

    def set_height(self, height, stretch=False, **kwargs):
        return self.rescale_to_fit(height, 1, stretch=stretch, **kwargs)

    def set_depth(self, depth, stretch=False, **kwargs):
        return self.rescale_to_fit(depth, 2, stretch=stretch, **kwargs)

    def set_coord(self, value, dim, direction=ORIGIN):
        curr = self.get_coord(dim, direction)
        shift_vect = np.zeros(self.dim)
        shift_vect[dim] = value - curr
        self.shift(shift_vect)
        return self

    def set_x(self, x, direction=ORIGIN):
        return self.set_coord(x, 0, direction)

    def set_y(self, y, direction=ORIGIN):
        return self.set_coord(y, 1, direction)

    def set_z(self, z, direction=ORIGIN):
        return self.set_coord(z, 2, direction)

    def space_out_submobjects(self, factor=1.5, **kwargs):
        self.scale(factor, **kwargs)
        for submob in self.submobjects:
            submob.scale(1. / factor)
        return self

    def move_to(self, point_or_mobject, aligned_edge=ORIGIN,
                coor_mask=np.array([1, 1, 1])):
        if isinstance(point_or_mobject, Mobject):
            target = point_or_mobject.get_bounding_box_point(aligned_edge)
        else:
            target = point_or_mobject
        point_to_align = self.get_bounding_box_point(aligned_edge)
        self.shift((target - point_to_align) * coor_mask)
        return self

    def replace(self, mobject, dim_to_match=0, stretch=False):
        if not mobject.get_num_points() and not mobject.submobjects:
            self.scale(0)
            return self
        if stretch:
            for i in range(self.dim):
                self.rescale_to_fit(mobject.length_over_dim(i), i, stretch=True)
        else:
            self.rescale_to_fit(
                mobject.length_over_dim(dim_to_match),
                dim_to_match,
                stretch=False
            )
        self.shift(mobject.get_center() - self.get_center())
        return self

    def surround(self, mobject,
                 dim_to_match=0,
                 stretch=False,
                 buff=MED_SMALL_BUFF):
        self.replace(mobject, dim_to_match, stretch)
        length = mobject.length_over_dim(dim_to_match)
        self.scale((length + buff) / length)
        return self

    def put_start_and_end_on(self, start, end):
        # TODO, this doesn't currently work in 3d
        curr_start, curr_end = self.get_start_and_end()
        curr_vect = curr_end - curr_start
        if np.all(curr_vect == 0):
            raise Exception("Cannot position endpoints of closed loop")
        target_vect = end - start
        self.scale(
            get_norm(target_vect) / get_norm(curr_vect),
            about_point=curr_start,
        )
        self.rotate(
            angle_of_vector(target_vect) - angle_of_vector(curr_vect),
            about_point=curr_start
        )
        self.shift(start - curr_start)
        return self

    # Background rectangle
    def add_background_rectangle(self, color=BLACK, opacity=0.75, **kwargs):
        # TODO, this does not behave well when the mobject has points,
        # since it gets displayed on top
        from manimlib.mobject.shape_matchers import BackgroundRectangle
        self.background_rectangle = BackgroundRectangle(
            self, color=color,
            fill_opacity=opacity,
            **kwargs
        )
        self.add_to_back(self.background_rectangle)
        return self

    def add_background_rectangle_to_submobjects(self, **kwargs):
        for submobject in self.submobjects:
            submobject.add_background_rectangle(**kwargs)
        return self

    def add_background_rectangle_to_family_members_with_points(self, **kwargs):
        for mob in self.family_members_with_points():
            mob.add_background_rectangle(**kwargs)
        return self

    # Color functions
    def set_rgba_array(self, color=None, opacity=None, name="rgbas", recurse=True):
        # TODO, account for if color or opacity are tuples
        rgb = color_to_rgb(color) if color else None
        for mob in self.get_family(recurse):
            if rgb is not None:
                mob.data[name][:, :3] = rgb
            if opacity is not None:
                mob.data[name][:, 3] = opacity
        return self

    def set_color(self, color, opacity=None, recurse=True):
        self.set_rgba_array(color, opacity, recurse=False)
        # Recurse to submobjects differently from how set_rgba_array
        # in case they implement set_color differently
        if recurse:
            for submob in self.submobjects:
                submob.set_color(color, recurse=True)
        return self

    def set_opacity(self, opacity, recurse=True):
        self.set_rgba_array(color=None, opacity=opacity, recurse=False)
        if recurse:
            for submob in self.submobjects:
                submob.set_opacity(opacity, recurse=True)
        return self

    def get_color(self):
        return rgb_to_hex(self.data["rgbas"][0, :3])

    def get_opacity(self):
        return self.data["rgbas"][0, 3]

    def set_color_by_gradient(self, *colors):
        self.set_submobject_colors_by_gradient(*colors)
        return self

    def set_submobject_colors_by_gradient(self, *colors):
        if len(colors) == 0:
            raise Exception("Need at least one color")
        elif len(colors) == 1:
            return self.set_color(*colors)

        mobs = self.family_members_with_points()
        new_colors = color_gradient(colors, len(mobs))

        for mob, color in zip(mobs, new_colors):
            mob.set_color(color, recurse=False)
        return self

    def fade(self, darkness=0.5, recurse=True):
        self.set_opacity(1.0 - darkness, recurse=recurse)

    def get_gloss(self):
        return self.gloss

    def set_gloss(self, gloss, recurse=True):
        for mob in self.get_family(recurse):
            mob.gloss = gloss
        return self

    def get_shadow(self):
        return self.shadow

    def set_shadow(self, shadow, recurse=True):
        for mob in self.get_family(recurse):
            mob.shadow = shadow
        return self

    ##

    def save_state(self, use_deepcopy=False):
        if hasattr(self, "saved_state"):
            # Prevent exponential growth of data
            self.saved_state = None
        if use_deepcopy:
            self.saved_state = self.deepcopy()
        else:
            self.saved_state = self.copy()
        return self

    def restore(self):
        if not hasattr(self, "saved_state") or self.save_state is None:
            raise Exception("Trying to restore without having saved")
        self.become(self.saved_state)
        return self

    ##

    def get_merged_array(self, array_attr):
        if self.submobjects:
            return np.vstack([
                getattr(sm, array_attr)
                for sm in self.get_family()
            ])
        else:
            return getattr(self, array_attr)

    def get_all_points(self):
        if self.submobjects:
            return np.vstack([sm.get_points() for sm in self.get_family()])
        else:
            return self.get_points()

    # Getters

    def get_points_defining_boundary(self):
        return self.get_all_points()

    def get_bounding_box_point(self, direction):
        result = np.zeros(self.dim)
        bb = self.get_bounding_box()
        result[direction < 0] = bb[0, direction < 0]
        result[direction == 0] = bb[1, direction == 0]
        result[direction > 0] = bb[2, direction > 0]
        return result

    def get_bounding_box(self):
        all_points = self.get_points_defining_boundary()
        if len(all_points) == 0:
            return np.zeros((3, self.dim))
        else:
            # Lower left and upper right corners
            mins = all_points.min(0)
            maxs = all_points.max(0)
            mids = (mins + maxs) / 2
            return np.array([mins, mids, maxs])

    # Pseudonyms for more general get_bounding_box_point method

    def get_edge_center(self, direction):
        return self.get_bounding_box_point(direction)

    def get_corner(self, direction):
        return self.get_bounding_box_point(direction)

    def get_center(self):
        return self.get_bounding_box_point(np.zeros(self.dim))

    def get_center_of_mass(self):
        return self.get_all_points().mean(0)

    def get_boundary_point(self, direction):
        all_points = self.get_points_defining_boundary()
        boundary_directions = all_points - self.get_center()
        norms = np.linalg.norm(boundary_directions, axis=1)
        boundary_directions /= np.repeat(norms, 3).reshape((len(norms), 3))
        index = np.argmax(np.dot(boundary_directions, np.array(direction).T))
        return all_points[index]

    def get_bounding_box_point_by_direction(self, direction):
        dl, center, ur = self.get_bounding_box()
        corner_vect = (ur - center)
        return center + direction / np.max(np.abs(np.true_divide(
            direction, corner_vect,
            out=np.zeros(len(direction)),
            where=((corner_vect) != 0)
        )))

    def get_top(self):
        return self.get_edge_center(UP)

    def get_bottom(self):
        return self.get_edge_center(DOWN)

    def get_right(self):
        return self.get_edge_center(RIGHT)

    def get_left(self):
        return self.get_edge_center(LEFT)

    def get_zenith(self):
        return self.get_edge_center(OUT)

    def get_nadir(self):
        return self.get_edge_center(IN)

    def length_over_dim(self, dim):
        bb = self.get_bounding_box()
        return (bb[2] - bb[0])[dim]

    def get_width(self):
        return self.length_over_dim(0)

    def get_height(self):
        return self.length_over_dim(1)

    def get_depth(self):
        return self.length_over_dim(2)

    def get_coord(self, dim, direction=ORIGIN):
        """
        Meant to generalize get_x, get_y, get_z
        """
        return self.get_bounding_box_point(direction)[dim]

    def get_x(self, direction=ORIGIN):
        return self.get_coord(0, direction)

    def get_y(self, direction=ORIGIN):
        return self.get_coord(1, direction)

    def get_z(self, direction=ORIGIN):
        return self.get_coord(2, direction)

    def get_start(self):
        self.throw_error_if_no_points()
        return np.array(self.get_points()[0])

    def get_end(self):
        self.throw_error_if_no_points()
        return np.array(self.get_points()[-1])

    def get_start_and_end(self):
        return self.get_start(), self.get_end()

    def point_from_proportion(self, alpha):
        raise Exception("Not implemented")

    def pfp(self, alpha):
        """Abbreviation fo point_from_proportion"""
        return self.point_from_proportion(alpha)

    def get_pieces(self, n_pieces):
        template = self.copy()
        template.set_submobjects([])
        alphas = np.linspace(0, 1, n_pieces + 1)
        return Group(*[
            template.copy().pointwise_become_partial(
                self, a1, a2
            )
            for a1, a2 in zip(alphas[:-1], alphas[1:])
        ])

    def get_z_index_reference_point(self):
        # TODO, better place to define default z_index_group?
        z_index_group = getattr(self, "z_index_group", self)
        return z_index_group.get_center()

    def has_points(self):
        return self.get_num_points() > 0

    def has_no_points(self):
        return not self.has_points()

    # Match other mobject properties

    def match_color(self, mobject):
        return self.set_color(mobject.get_color())

    def match_dim_size(self, mobject, dim, **kwargs):
        return self.rescale_to_fit(
            mobject.length_over_dim(dim), dim,
            **kwargs
        )

    def match_width(self, mobject, **kwargs):
        return self.match_dim_size(mobject, 0, **kwargs)

    def match_height(self, mobject, **kwargs):
        return self.match_dim_size(mobject, 1, **kwargs)

    def match_depth(self, mobject, **kwargs):
        return self.match_dim_size(mobject, 2, **kwargs)

    def match_coord(self, mobject, dim, direction=ORIGIN):
        return self.set_coord(
            mobject.get_coord(dim, direction),
            dim=dim,
            direction=direction,
        )

    def match_x(self, mobject, direction=ORIGIN):
        return self.match_coord(mobject, 0, direction)

    def match_y(self, mobject, direction=ORIGIN):
        return self.match_coord(mobject, 1, direction)

    def match_z(self, mobject, direction=ORIGIN):
        return self.match_coord(mobject, 2, direction)

    def align_to(self, mobject_or_point, direction=ORIGIN, alignment_vect=UP):
        """
        Examples:
        mob1.align_to(mob2, UP) moves mob1 vertically so that its
        top edge lines ups with mob2's top edge.

        mob1.align_to(mob2, alignment_vect = RIGHT) moves mob1
        horizontally so that it's center is directly above/below
        the center of mob2
        """
        if isinstance(mobject_or_point, Mobject):
            point = mobject_or_point.get_bounding_box_point(direction)
        else:
            point = mobject_or_point

        for dim in range(self.dim):
            if direction[dim] != 0:
                self.set_coord(point[dim], dim, direction)
        return self

    def get_group_class(self):
        return Group

    # Submobject organization
    def arrange(self, direction=RIGHT, center=True, **kwargs):
        for m1, m2 in zip(self.submobjects, self.submobjects[1:]):
            m2.next_to(m1, direction, **kwargs)
        if center:
            self.center()
        return self

    def arrange_in_grid(self, n_rows=None, n_cols=None,
                        buff=None,
                        h_buff=None,
                        v_buff=None,
                        buff_ratio=None,
                        h_buff_ratio=0.5,
                        v_buff_ratio=0.5,
                        aligned_edge=ORIGIN,
                        fill_rows_first=True):
        submobs = self.submobjects
        if n_rows is None and n_cols is None:
            n_rows = int(np.sqrt(len(submobs)))
        if n_rows is None:
            n_rows = len(submobs) // n_cols
        if n_cols is None:
            n_cols = len(submobs) // n_rows

        if buff is not None:
            h_buff = buff
            v_buff = buff
        else:
            if buff_ratio is not None:
                v_buff_ratio = buff_ratio
                h_buff_ratio = buff_ratio
            if h_buff is None:
                h_buff = h_buff_ratio * self[0].get_width()
            if v_buff is None:
                v_buff = v_buff_ratio * self[0].get_height()

        x_unit = h_buff + max([sm.get_width() for sm in submobs])
        y_unit = v_buff + max([sm.get_height() for sm in submobs])

        for index, sm in enumerate(submobs):
            if fill_rows_first:
                x, y = index % n_cols, index // n_cols
            else:
                x, y = index // n_rows, index % n_rows
            sm.move_to(ORIGIN, aligned_edge)
            sm.shift(x * x_unit * RIGHT + y * y_unit * DOWN)
        self.center()
        return self

    def get_grid(self, n_rows, n_cols, height=None, **kwargs):
        """
        Returns a new mobject containing multiple copies of this one
        arranged in a grid
        """
        grid = self.get_group_class()(
            *(self.copy() for n in range(n_rows * n_cols))
        )
        grid.arrange_in_grid(n_rows, n_cols, **kwargs)
        if height is not None:
            grid.set_height(height)
        return grid

    def sort(self, point_to_num_func=lambda p: p[0], submob_func=None):
        if submob_func is not None:
            self.submobjects.sort(key=submob_func)
        else:
            self.submobjects.sort(key=lambda m: point_to_num_func(m.get_center()))
        return self

    def shuffle(self, recurse=False):
        if recurse:
            for submob in self.submobjects:
                submob.shuffle(recurse=True)
        random.shuffle(self.submobjects)
        return self

    # Just here to keep from breaking old scenes.
    def arrange_submobjects(self, *args, **kwargs):
        return self.arrange(*args, **kwargs)

    def sort_submobjects(self, *args, **kwargs):
        return self.sort(*args, **kwargs)

    def shuffle_submobjects(self, *args, **kwargs):
        return self.shuffle(*args, **kwargs)

    # Alignment
    def align_data(self, mobject):
        self.null_point_align(mobject)  # Needed?
        self.align_submobjects(mobject)
        for mob1, mob2 in zip(self.get_family(), mobject.get_family()):
            # Separate out how points are treated so that subclasses
            # can handle that case differently if they choose
            mob1.align_points(mob2)
            for key in mob1.data:
                if key == "points":
                    continue
                arr1 = mob1.data[key]
                arr2 = mob2.data[key]
                if len(arr2) > len(arr1):
                    mob1.data[key] = resize_preserving_order(arr1, len(arr2))
                elif len(arr1) > len(arr2):
                    mob2.data[key] = resize_preserving_order(arr2, len(arr1))

    def align_points(self, mobject):
        max_len = max(self.get_num_points(), mobject.get_num_points())
        self.resize_points(max_len, resize_func=resize_preserving_order)
        mobject.resize_points(max_len, resize_func=resize_preserving_order)
        return self

    def align_submobjects(self, mobject):
        mob1 = self
        mob2 = mobject
        n1 = len(mob1.submobjects)
        n2 = len(mob2.submobjects)
        mob1.add_n_more_submobjects(max(0, n2 - n1))
        mob2.add_n_more_submobjects(max(0, n1 - n2))
        # Recurse
        for sm1, sm2 in zip(mob1.submobjects, mob2.submobjects):
            sm1.align_submobjects(sm2)
        return self

    def null_point_align(self, mobject):
        """
        If a mobject with points is being aligned to
        one without, treat both as groups, and push
        the one with points into its own submobjects
        list.
        """
        for m1, m2 in (self, mobject), (mobject, self):
            if m1.has_no_points() and m2.has_points():
                m2.push_self_into_submobjects()
        return self

    def push_self_into_submobjects(self):
        copy = self.deepcopy()
        copy.set_submobjects([])
        self.resize_points(0)
        self.add(copy)
        return self

    def add_n_more_submobjects(self, n):
        if n == 0:
            return

        curr = len(self.submobjects)
        if curr == 0:
            # If empty, simply add n point mobjects
            self.set_submobjects([
                self.copy().scale(0)
                for k in range(n)
            ])
            return
        target = curr + n
        repeat_indices = (np.arange(target) * curr) // target
        split_factors = [
            (repeat_indices == i).sum()
            for i in range(curr)
        ]
        new_submobs = []
        for submob, sf in zip(self.submobjects, split_factors):
            new_submobs.append(submob)
            for k in range(1, sf):
                new_submob = submob.copy()
                # If the submobject is at all transparent, then
                # make the copy completely transparent
                if submob.get_opacity() < 1:
                    new_submob.set_opacity(0)
                new_submobs.append(new_submob)
        self.set_submobjects(new_submobs)
        return self

    def interpolate(self, mobject1, mobject2, alpha, path_func=straight_path):
        """
        Turns self into an interpolation between mobject1
        and mobject2.
        """
        for key in self.data:
            func = path_func if key == "points" else interpolate
            self.data[key][:] = func(
                mobject1.data[key],
                mobject2.data[key],
                alpha
            )
        self.interpolate_light_style(mobject1, mobject2, alpha)  # TODO, interpolate uniforms instaed
        return self

    def interpolate_light_style(self, mobject1, mobject2, alpha):
        g0 = self.get_gloss()
        g1 = mobject1.get_gloss()
        g2 = mobject2.get_gloss()
        if not (g0 == g1 == g2):
            self.set_gloss(interpolate(g1, g2, alpha))

        s0 = self.get_shadow()
        s1 = mobject1.get_shadow()
        s2 = mobject2.get_shadow()
        if not (s0 == s1 == s2):
            self.set_shadow(interpolate(s1, s2, alpha))
        return self

    def become_partial(self, mobject, a, b):
        """
        Set points in such a way as to become only
        part of mobject.
        Inputs 0 <= a < b <= 1 determine what portion
        of mobject to become.
        """
        pass  # To implement in subclasses

        # TODO, color?

    def pointwise_become_partial(self, mobject, a, b):
        pass  # To implement in subclass

    def become(self, mobject):
        """
        Edit points, colors and submobjects to be idential
        to another mobject
        """
        self.align_submobjects(mobject)
        for sm1, sm2 in zip(self.get_family(), mobject.get_family()):
            sm1.set_data(sm2.data)
        return self

    def cleanup_from_animation(self):
        pass

    # Operations touching shader uniforms
    def affects_shader_info_id(func):
        def wrapper(self):
            for mob in self.get_family():
                func(mob)
                mob.refresh_shader_wrapper_id()
        return wrapper

    @affects_shader_info_id
    def fix_in_frame(self):
        self.is_fixed_in_frame = True
        return self

    @affects_shader_info_id
    def unfix_from_frame(self):
        self.is_fixed_in_frame = False
        return self

    @affects_shader_info_id
    def apply_depth_test(self):
        self.depth_test = True
        return self

    @affects_shader_info_id
    def deactivate_depth_test(self):
        self.depth_test = False
        return self

    # Shader code manipulation
    def replace_shader_code(self, old, new):
        for wrapper in self.get_shader_wrapper_list():
            wrapper.replace_code(old, new)
        return self

    def refresh_shader_code(self):
        for wrapper in self.get_shader_wrapper_list():
            wrapper.init_program_code()
            wrapper.refresh_id()
        return self

    def set_color_by_code(self, glsl_code):
        """
        Takes a snippet of code and inserts it into a
        context which has the following variables:
        vec4 color, vec3 point, vec3 unit_normal.
        The code should change the color variable
        """
        self.replace_shader_code(
            "///// INSERT COLOR FUNCTION HERE /////",
            glsl_code
        )
        return self

    def set_color_by_xyz_func(self, glsl_snippet,
                              min_value=-5.0, max_value=5.0,
                              colormap="viridis"):
        """
        Pass in a glsl expression in terms of x, y and z which returns
        a float.
        """
        # TODO, add a version of this which changes the point data instead
        # of the shader code
        for char in "xyz":
            glsl_snippet = glsl_snippet.replace(char, "point." + char)
        rgb_list = get_colormap_list(colormap)
        self.set_color_by_code(
            "color.rgb = float_to_color({}, {}, {}, {});".format(
                glsl_snippet,
                float(min_value),
                float(max_value),
                get_colormap_code(rgb_list)
            )
        )
        return self

    # For shader data
    def init_shader_data(self):
        self.shader_data = np.zeros(len(self.get_points()), dtype=self.shader_dtype)
        self.shader_indices = None
        self.shader_wrapper = ShaderWrapper(
            vert_data=self.shader_data,
            shader_folder=self.shader_folder,
            texture_paths=self.texture_paths,
            depth_test=self.depth_test,
            render_primitive=self.render_primitive,
        )

    def refresh_shader_wrapper_id(self):
        self.shader_wrapper.refresh_id()
        return self

    def get_resized_shader_data_array(self, size):
        # If possible, try to populate an existing array, rather
        # than recreating it each frame
        if self.shader_data.size != size:
            self.shader_data = resize_array(self.shader_data, size)
        return self.shader_data

    def get_shader_wrapper(self):
        self.shader_wrapper.vert_data = self.get_shader_data()
        self.shader_wrapper.vert_indices = self.get_shader_vert_indices()
        self.shader_wrapper.uniforms = self.get_shader_uniforms()
        self.shader_wrapper.depth_test = self.depth_test
        return self.shader_wrapper

    def get_shader_wrapper_list(self):
        shader_wrappers = it.chain(
            [self.get_shader_wrapper()],
            *[sm.get_shader_wrapper_list() for sm in self.submobjects]
        )
        batches = batch_by_property(shader_wrappers, lambda sw: sw.get_id())

        result = []
        for wrapper_group, sid in batches:
            shader_wrapper = wrapper_group[0]
            if not shader_wrapper.is_valid():
                continue
            shader_wrapper.combine_with(*wrapper_group[1:])
            if len(shader_wrapper.vert_data) > 0:
                result.append(shader_wrapper)
        return result

    def get_shader_data(self):
        data = self.get_resized_shader_data_array(self.get_num_points())
        data["point"] = self.data["points"]
        return data

    def get_shader_uniforms(self):
        return {
            "is_fixed_in_frame": float(self.is_fixed_in_frame),
            "gloss": self.gloss,
            "shadow": self.shadow,
        }

    def get_shader_vert_indices(self):
        return self.shader_indices

    # Errors
    def throw_error_if_no_points(self):
        if self.has_no_points():
            message = "Cannot call Mobject.{} " +\
                      "for a Mobject with no points"
            caller_name = sys._getframe(1).f_code.co_name
            raise Exception(message.format(caller_name))


class Group(Mobject):
    def __init__(self, *mobjects, **kwargs):
        if not all([isinstance(m, Mobject) for m in mobjects]):
            raise Exception("All submobjects must be of type Mobject")
        Mobject.__init__(self, **kwargs)
        self.add(*mobjects)


class Point(Mobject):
    CONFIG = {
        "artificial_width": 1e-6,
        "artificial_height": 1e-6,
    }

    def __init__(self, location=ORIGIN, **kwargs):
        Mobject.__init__(self, **kwargs)
        self.set_location(location)

    def get_width(self):
        return self.artificial_width

    def get_height(self):
        return self.artificial_height

    def get_location(self):
        return self.get_points()[0].copy()

    def get_bounding_box_point(self, *args, **kwargs):
        return self.get_location()

    def set_location(self, new_loc):
        self.set_points(np.array(new_loc, ndmin=2, dtype=float))
