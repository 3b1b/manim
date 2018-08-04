from __future__ import absolute_import
from __future__ import print_function

import copy
import itertools as it
import numpy as np
import operator as op
import os
import pytest
import random

from colour import Color

from constants import *
from container.container import Container
from mobject.mobject import Mobject
from utils.bezier import interpolate
from utils.color import color_gradient
from utils.color import color_to_rgb
from utils.color import interpolate_color
from utils.iterables import list_update
from utils.iterables import remove_list_redundancies
from utils.paths import straight_path
from utils.space_ops import angle_of_vector
from utils.space_ops import complex_to_R3
from utils.space_ops import rotation_matrix
from functools import reduce

def test_init():
    m = Mobject()

    # test default instance variables
    default_config = Mobject.CONFIG
    assert(m.color == Color(default_config["color"]))
    assert(m.name == m.__class__.__name__)
    assert(m.dim == default_config["dim"])
    assert(m.target == default_config["target"])
    assert(m.submobjects == [])

    # All submobjects must be of type Mobject
    with pytest.raises(Exception):
        m = Mobject(5)

def test_str():
    m = Mobject()
    assert(str(m) == "Mobject")

def test_init_points():
    m = Mobject()
    m.init_points()
    assert(np.all(m.points == np.zeros((0, m.dim))))

def test_add():
    m = Mobject()
    s1 = Mobject()
    s2 = Mobject()

    # All submobjects must be of type Mobject
    with pytest.raises(Exception):
        m.add(5)

    # Mobject cannot contain self
    with pytest.raises(Exception):
        m.add(m)

    m.add(s1)
    assert(m.submobjects == [s1])

    # Mobject.submobjects cannot contain duplicates
    m.add(s1)
    assert(m.submobjects == [s1])

    # Newly added Mobjects become the last elements of Mobject.submobjects
    m.add(s2)
    assert(m.submobjects == [s1, s2])

    # Repeated additions move mobjects to the end
    m.add(s1)
    assert(m.submobjects == [s2, s1])

def test_add_to_back():
    s1 = Mobject()
    s2 = Mobject()
    s3 = Mobject()
    m = Mobject(s1, s2, s3)

    # All submobjects must be of type Mobject
    with pytest.raises(Exception):
        m.add_to_back(5)

    # Mobject cannot contain self
    with pytest.raises(Exception):
        m.add_to_back(m)

    # Newly added Mobjects become the first elements of Mobject.submobjects
    s4 = Mobject()
    m.add_to_back(s4)
    assert(m.submobjects == [s4, s1, s2, s3])

    m.add_to_back(s1, s2)
    assert(m.submobjects == [s1, s2, s4, s3])

def test_add_to_front():
    s1 = Mobject()
    s2 = Mobject()
    s3 = Mobject()
    m = Mobject(s1, s2, s3)

    # All submobjects must be of type Mobject
    with pytest.raises(Exception):
        m.add_to_front(5)

    # Mobject cannot contain self
    with pytest.raises(Exception):
        m.add_to_front(m)

    # Newly added Mobjects become the first elements of Mobject.submobjects
    s4 = Mobject()
    m.add_to_front(s4)
    assert(m.submobjects == [s4, s1, s2, s3])

    m.add_to_front(s1, s2)
    assert(m.submobjects == [s1, s2, s4, s3])

def test_remove():
    s1 = Mobject()
    s2 = Mobject()
    s3 = Mobject()
    m = Mobject(s1, s2, s3)

    m.remove(s2)
    assert(m.submobjects == [s1, s3])

    m.remove(s1, s3)
    assert(m.submobjects == [])

    m.remove(s1)
    assert(m.submobjects == [])

def test_get_array_attrs():
    assert(Mobject().get_array_attrs() == ["points"])

def test_digest_mobject_attrs():
    m = Mobject()
    a = Mobject()
    m.attr = a
    m.digest_mobject_attrs()
    assert(m.submobjects == [a])

    m.attr = m
    with pytest.raises(Exception):
        m.digest_mobject_attrs()

#def apply_over_attr_arrays():
#def get_image():
#def show():
#def save_image():
#def copy():
#def deepcopy():
#def generate_target():
#def apply_to_family():
#def shift():
#def scale():
#def rotate_about_origin():
#def rotate():
#def flip():
#def stretch():
#    def func():
#def apply_function():
#def apply_function_to_position():
#def apply_function_to_submobject_positions():
#def apply_matrix():
#def apply_complex_function():
#def wag():
#def reverse_points():
#def repeat():
#    def repeat_array():
## Note, much of these are now redundant with default behavior of
#def apply_points_function_about_point():
#def rotate_in_place():
#    # redundant with default behavior of rotate now.
#def scale_in_place():
#    # Redundant with default behavior of scale now.
#def scale_about_point():
#    # Redundant with default behavior of scale now.
#def pose_at_angle():
#def center():
#def align_on_border():
#def to_corner():
#def to_edge():
#def next_to(self, mobject_or_point,
#def align_to():
#def shift_onto_screen():
#def is_off_screen():
#def stretch_about_point():
#def stretch_in_place():
#def rescale_to_fit():
#def stretch_to_fit_width():
#def stretch_to_fit_height():
#def stretch_to_fit_depth():
#def scale_to_fit_width():
#def scale_to_fit_height():
#def scale_to_fit_depth():
#def space_out_submobjects():
#def move_to(self, point_or_mobject, aligned_edge=ORIGIN,
#def replace():
#def surround():
#def position_endpoints_on():
#def add_background_rectangle():
#def add_background_rectangle_to_submobjects():
#def add_background_rectangle_to_family_members_with_points():
#def match_color():
#def match_dim():
#def match_width():
#def match_height():
#def match_depth():
#def set_color():
#def set_color_by_gradient():
#def set_colors_by_radial_gradient():
#def set_submobject_colors_by_gradient():
#def set_submobject_colors_by_radial_gradient():
#def to_original_color():
## used by default for fade()ing
#def fade_to_no_recurse():
#def fade_to():
#def fade_no_recurse():
#def fade():
#def get_color():
#def save_state():
#def restore():
#def reduce_across_dimension():
#        # Note, this default means things like empty VGroups
#def nonempty_submobjects():
#def get_merged_array():
#def get_all_points():
#def get_points_defining_boundary():
#def get_num_points():
#def get_critical_point():
#def get_edge_center():
#def get_corner():
#def get_center():
#def get_center_of_mass():
#def get_boundary_point():
#def get_top():
#def get_bottom():
#def get_right():
#def get_left():
#def get_zenith():
#def get_nadir():
#def length_over_dim():
#def get_width():
#def get_height():
#def get_depth():
#def point_from_proportion():
#def __getitem__():
#def __iter__():
#def __len__():
#def get_group_class():
#def split():
#def submobject_family():
#def family_members_with_points():
#def arrange_submobjects():
#def arrange_submobjects_in_grid():
#def sort_submobjects():
#def shuffle_submobjects():
#def print_submobject_family():
#def align_data():
#def get_point_mobject():
#def align_points():
#def align_points_with_larger():
#def align_submobjects():
#def null_point_align():
#def push_self_into_submobjects():
#def add_n_more_submobjects():
#def repeat_submobject():
#def interpolate(self, mobject1, mobject2,
#def interpolate_color():
#def become_partial():
#def pointwise_become_partial():
