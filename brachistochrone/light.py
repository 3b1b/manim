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

    def photon_along_path(self, path, color = YELLOW, run_time = 1):
        photon = self.wavify(path)
        photon.highlight(color)
        self.play(ShowPassingFlash(
            photon, 
            run_time = run_time,
            rate_func = None
        ))


class SimplePhoton(PhotonScene):
    def construct(self):
        text = TextMobject("Light")
        text.to_edge(UP)
        self.play(ShimmerIn(text))
        self.photon_along_path(Cycloid())
        self.dither()