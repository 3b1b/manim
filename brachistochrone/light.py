import numpy as np
import itertools as it

from helpers import *

from mobject.tex_mobject import TexMobject, TextMobject, Brace
from mobject import Mobject
from mobject.image_mobject import \
    MobjectFromRegion, ImageMobject, MobjectFromPixelArray
from topics.three_dimensions import Stars

from animation import Animation
from animation.transform import \
    Transform, CounterclockwiseTransform, ApplyPointwiseFunction,\
    FadeIn, FadeOut, GrowFromCenter, ApplyFunction, ApplyMethod, \
    ShimmerIn
from animation.simple_animations import \
    ShowCreation, Homotopy, PhaseFlow, ApplyToCenters, DelayByOrder, \
    ShowPassingFlash
from animation.playground import TurnInsideOut, Vibrate
from topics.geometry import \
    Line, Circle, Square, Grid, Rectangle, Arrow, Dot, Point, \
    Arc, FilledRectangle
from topics.characters import Randolph, Mathematician
from topics.functions import ParametricFunction, FunctionGraph
from topics.number_line import NumberPlane
from region import Region, region_from_polygon_vertices
from scene import Scene

from brachistochrone.curves import Cycloid

class Lens(Arc):
    DEFAULT_CONFIG = {
        "radius" : 2,
        "angle" : np.pi/2,
        "color" : BLUE_B,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        Arc.__init__(self, self.angle, **kwargs)

    def generate_points(self):
        Arc.generate_points(self)
        self.rotate(-np.pi/4)
        self.shift(-self.get_left())
        self.add_points(self.copy().rotate(np.pi).points)



class PhotonScene(Scene):
    def wavify(self, mobject):
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


    def photon_run_along_path(self, path, color = YELLOW, **kwargs):
        photon = self.wavify(path)
        photon.highlight(color)
        return ShowPassingFlash(photon, **kwargs)


class SimplePhoton(PhotonScene):
    def construct(self):
        text = TextMobject("Light")
        text.to_edge(UP)
        self.play(ShimmerIn(text))
        self.play(self.photon_run_along_path(
            Cycloid(), rate_func = None
        ))
        self.dither()


class PhotonThroughLens(PhotonScene):
    def construct(self):
        lens = Lens()
        num_paths = 5
        interval_values = np.arange(num_paths)/(num_paths-1.)
        first_contact = [
            lens.point_from_interval(0.4*v+0.55)
            for v in reversed(interval_values)
        ]
        second_contact = [
            lens.point_from_interval(0.3*v + 0.1)
            for v in interval_values
        ]
        focal_point = 2*RIGHT
        paths = [
            Mobject(
                Line(SPACE_WIDTH*LEFT + fc[1]*UP, fc),
                Line(fc, sc),
                Line(sc, focal_point),
                Line(focal_point, 6*focal_point-5*sc)
            ).ingest_sub_mobjects()
            for fc, sc in zip(first_contact, second_contact)
        ]
        colors = Color(YELLOW).range_to(WHITE, len(paths))
        for path, color in zip(paths, colors):
            path.highlight(color)
        photon_runs = [
            self.photon_run_along_path(path)
            for path in paths
        ]
        self.add(lens)
        for photon_run, path in zip(photon_runs, paths):
            self.play(
                photon_run,
                ShowCreation(
                    path,
                    rate_func = lambda t : 0.9*smooth(t)
                )
            )
        self.dither()











