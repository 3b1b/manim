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
from mobject.region import  Region, region_from_polygon_vertices
from scene import Scene


class OceanScene(Scene):
    def construct(self):
        self.rolling_waves()

    def rolling_waves(self):
        if not hasattr(self, "ocean"):
            self.setup_ocean()
        for state in self.ocean_states:
            self.play(Transform(self.ocean, state))


    def setup_ocean(self):
        def func(points):
            result = np.zeros(points.shape)
            result[:,1] = 0.25 * np.sin(points[:,0]) * np.sin(points[:,1])
            return result

        self.ocean_states = []
        for unit in -1, 1:
            ocean = FilledRectangle(
                color = BLUE_D, 
                density = 25
            )
            nudges = unit*func(ocean.points)
            ocean.points += nudges
            alphas = nudges[:,1]
            alphas -= np.min(alphas)
            whites = np.ones(ocean.rgbs.shape)
            thick_alphas = alphas.repeat(3).reshape((len(alphas), 3))
            ocean.rgbs = interpolate(ocean.rgbs, whites, thick_alphas)
            self.ocean_states.append(ocean)
        self.ocean = self.ocean_states[1].copy()