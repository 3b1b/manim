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

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import \
    MobjectFromRegion, ImageMobject, MobjectFromPixelArray

from animation.transform import \
    Transform, CounterclockwiseTransform, ApplyPointwiseFunction,\
    FadeIn, FadeOut, GrowFromCenter
from animation.simple_animations import \
    ShowCreation, Homotopy, PhaseFlow, ApplyToCenters, DelayByOrder
from animation.playground import TurnInsideOut, Vibrate
from topics.geometry import \
    Line, Circle, Square, Grid, Rectangle, Arrow, Dot, Point
from topics.characters import Randolph, Mathematician
from topics.functions import ParametricFunction
from topics.number_line import NumberPlane
from region import Region, region_from_polygon_vertices
from scene import Scene


DEFAULT_GAUSS_BLUR_CONFIG = {
    "ksize"  : (5, 5), 
    "sigmaX" : 10, 
    "sigmaY" : 10,
}

DEFAULT_CANNY_CONFIG = {
    "threshold1" : 75,
    "threshold2" : 150,
}

DEFAULT_BLUR_RADIUS = 0.5
DEFAULT_CONNECTED_COMPONENT_THRESHOLD = 25


def reverse_colors(nparray):
    return nparray[:,:,[2, 1, 0]]

def show(nparray):
    Image.fromarray(reverse_colors(nparray)).show()


def thicken(nparray):
    height, width = nparray.shape
    nparray = nparray.reshape((height, width, 1))
    return np.repeat(nparray, 3, 2)

def sort_by_color(mob):
    indices = np.argsort(np.apply_along_axis(
        lambda p : -np.linalg.norm(p),
        1,
        mob.rgbs
    ))
    mob.rgbs = mob.rgbs[indices]    
    mob.points = mob.points[indices]



def get_image_array(name):
    image_files = os.listdir(IMAGE_DIR)
    possibilities = filter(lambda s : s.startswith(name), image_files)
    for possibility in possibilities:
        try:
            path = os.path.join(IMAGE_DIR, possibility)
            image = Image.open(path)
            image = image.convert('RGB')
            return np.array(image)
        except:
            pass
    raise Exception("Image for %s not found"%name)

def get_edges(image_array):
    blurred = cv2.GaussianBlur(
        image_array, 
        **DEFAULT_GAUSS_BLUR_CONFIG
    )
    edges = cv2.Canny(
        blurred, 
        **DEFAULT_CANNY_CONFIG
    )
    return edges

def nearest_neighbor_align(mobject1, mobject2):
    distance_matrix = cdist(mobject1.points, mobject2.points)
    closest_point_indices = np.apply_along_axis(
        np.argmin, 0, distance_matrix
    )
    new_mob1 = Mobject()
    new_mob2 = Mobject()
    for n in range(mobject1.get_num_points()):
        indices = (closest_point_indices == n)
        new_mob1.add_points(
            [mobject1.points[n]]*sum(indices)
        )
        new_mob2.add_points(
            mobject2.points[indices],
            rgbs = mobject2.rgbs[indices]
        )
    return new_mob1, new_mob2

def get_connected_components(image_array, 
                             blur_radius = DEFAULT_BLUR_RADIUS, 
                             threshold = DEFAULT_CONNECTED_COMPONENT_THRESHOLD):
    blurred_image = ndimage.gaussian_filter(image_array, blur_radius)
    labels, component_count = ndimage.label(blurred_image > threshold)
    return [
        image_array * (labels == count)
        for count in range(1, component_count+1)
    ]

def color_region(bw_region, colored_image):
    return thicken(bw_region > 0) * colored_image


class TracePicture(Scene):
    args_list = [
        ("Newton",),
        ("Mark_Levi",),
        ("Steven_Strogatz",),
        ("Pierre_de_Fermat",),
        ("Galileo_Galilei",),
        ("Jakob_Bernoulli",),
        ("Johann_Bernoulli2",),
    ]

    @staticmethod
    def args_to_string(name):
        return name
        
    @staticmethod
    def string_to_args(name):
        return name

    def construct(self, name):
        run_time = 20
        scale_factor = 0.8
        image_array = get_image_array(name)
        edge_mobject = self.get_edge_mobject(image_array)
        full_picture = MobjectFromPixelArray(image_array)
        full_picture.point_thickness = 4        
        for mob in edge_mobject, full_picture:
            mob.scale(scale_factor)

        self.play(
            DelayByOrder(FadeIn(
                full_picture,
                run_time = run_time,
                rate_func = squish_rate_func(smooth, 0.7, 1)
            )),
            ShowCreation(
                edge_mobject,
                run_time = run_time,
                rate_func = None
            )
        )
        self.dither()


    def get_edge_mobject(self, image_array):
        edged_image = get_edges(image_array)
        individual_edges = get_connected_components(edged_image)
        colored_edges = [
            color_region(edge, image_array)
            for edge in individual_edges
        ]
        colored_edge_mobject_list = [
            MobjectFromPixelArray(colored_edge)
            for colored_edge in colored_edges
        ]
        random.shuffle(colored_edge_mobject_list)
        edge_mobject = Mobject(*colored_edge_mobject_list)
        edge_mobject.ingest_sub_mobjects()
        return edge_mobject
























