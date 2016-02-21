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
from mobject.tex_mobject import TextMobject, TexMobject    

from animation.transform import \
    Transform, CounterclockwiseTransform, ApplyPointwiseFunction,\
    FadeIn, FadeOut, GrowFromCenter, ShimmerIn, ApplyMethod
from animation.simple_animations import \
    ShowCreation, Homotopy, PhaseFlow, ApplyToCenters, DelayByOrder
from animation.playground import TurnInsideOut, Vibrate
from topics.geometry import \
    Line, Circle, Square, Grid, Rectangle, Arrow, Dot, Point
from topics.characters import Randolph, Mathematician, ThoughtBubble
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
        ("Jacob_Bernoulli",),
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
        for mob in edge_mobject, full_picture:
            # mob.point_thickness = 4
            mob.scale(scale_factor)
            mob.show()

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
        self.remove(edge_mobject)
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



class JohannThinksHeIsBetter(Scene):
    def construct(self):
        names = [
            "Johann_Bernoulli2",
            "Jacob_Bernoulli",
            "Gottfried_Wilhelm_von_Leibniz",
        ]
        guys = [
            ImageMobject(name, invert = False)
            for name in names
        ]
        johann = guys[0]
        johann.scale(0.8)
        pensive_johann = johann.copy()
        pensive_johann.scale(0.25)
        pensive_johann.to_corner(DOWN+LEFT)
        comparitive_johann = johann.copy()
        template = Square(side_length = 2)
        comparitive_johann.replace(template)
        comparitive_johann.shift(UP+LEFT)
        greater_than = TexMobject(">")
        greater_than.next_to(comparitive_johann)
        for guy, name in zip(guys, names)[1:]:
            guy.replace(template)
            guy.next_to(greater_than)
            name_mob = TextMobject(name.replace("_", " "))
            name_mob.scale(0.5)
            name_mob.next_to(guy, DOWN)
            guy.name_mob = name_mob
            guy.sort_points(lambda p : np.dot(p, DOWN+RIGHT))
        bubble = ThoughtBubble(initial_width = 12)
        bubble.stretch_to_fit_height(6)
        bubble.ingest_sub_mobjects()
        bubble.pin_to(pensive_johann)
        bubble.shift(DOWN)
        point = Point(johann.get_corner(UP+RIGHT))

        self.add(johann)
        self.dither()
        self.play(
            Transform(johann, pensive_johann),
            Transform(point, bubble),
            run_time = 2
        )
        self.remove(point)
        self.add(bubble)
        weakling = guys[1]        
        self.play(
            FadeIn(comparitive_johann),
            ShowCreation(greater_than),
            FadeIn(weakling)
        )
        self.dither(2)
        for guy in guys[2:]:
            self.play(
                DelayByOrder(Transform(weakling, guy)),
                ShimmerIn(guy.name_mob)
            )
            self.dither(3)
            self.remove(guy.name_mob)


class NewtonVsJohann(Scene):
    def construct(self):
        newton, johann = [
            ImageMobject(name, invert = False).scale(0.5)
            for name in "Newton", "Johann_Bernoulli2"
        ]
        greater_than = TexMobject(">")
        newton.next_to(greater_than, RIGHT)
        johann.next_to(greater_than, LEFT)
        self.add(johann, greater_than, newton)
        for i in range(2):
            kwargs = {
                "path_func" : counterclockwise_path(),
                "run_time"  : 2 
            }
            self.play(
                ApplyMethod(newton.replace, johann, **kwargs),
                ApplyMethod(johann.replace, newton, **kwargs),
            )
            self.dither()


class JohannThinksOfFermat(Scene):
    def construct(self):
        johann, fermat = [
            ImageMobject(name, invert = False)
            for name in "Johann_Bernoulli2", "Pierre_de_Fermat"
        ]
        johann.scale(0.2)
        johann.to_corner(DOWN+LEFT)
        bubble = ThoughtBubble(initial_width = 12)
        bubble.stretch_to_fit_height(6)
        bubble.pin_to(johann)
        bubble.shift(DOWN)
        bubble.add_content(fermat)
        fermat.scale_in_place(0.4)


        self.add(johann, bubble)
        self.dither()
        self.play(FadeIn(fermat))
        self.dither()











