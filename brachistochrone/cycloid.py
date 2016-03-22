import numpy as np
import itertools as it

from helpers import *

from mobject.tex_mobject import TexMobject, TextMobject, Brace
from mobject import Mobject, Mobject1D
from mobject.image_mobject import \
    ImageMobject, MobjectFromPixelArray
from topics.three_dimensions import Stars

from animation import Animation
from animation.transform import *
from animation.simple_animations import *
from topics.geometry import *
from topics.characters import Randolph
from topics.functions import *
from mobject.region import  Region
from scene import Scene
from scene.zoomed_scene import ZoomedScene

from camera import Camera
from brachistochrone.curves import *

class RollAlongVector(Animation):
    def __init__(self, mobject, vector, **kwargs):
        radius = mobject.get_width()/2
        radians = np.linalg.norm(vector)/radius
        last_alpha = 0
        digest_config(self, kwargs, locals())
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        d_alpha = alpha - self.last_alpha
        self.last_alpha = alpha
        self.mobject.rotate_in_place(d_alpha*self.radians)
        self.mobject.shift(d_alpha*self.vector)


class CycloidScene(Scene):
    CONFIG = {
        "point_a"   : 6*LEFT+3*UP,
        "radius"    : 2,
        "end_theta" : 2*np.pi
    }
    def construct(self):
        self.generate_cycloid()
        self.generate_circle()
        self.generate_ceiling()

    def grow_parts(self):
        self.play(*[
            ShowCreation(mob)
            for mob in self.circle, self.ceiling
        ])

    def generate_cycloid(self):
        self.cycloid = Cycloid(
            point_a = self.point_a,
            radius = self.radius,
            end_theta = self.end_theta
        )

    def generate_circle(self, **kwargs):
        self.circle = Circle(radius = self.radius, **kwargs)
        self.circle.shift(self.point_a - self.circle.get_top())
        radial_line = Line(
            self.circle.get_center(), self.point_a
        )
        self.circle.add(radial_line)

    def generate_ceiling(self):
        self.ceiling = Line(SPACE_WIDTH*LEFT, SPACE_WIDTH*RIGHT)
        self.ceiling.shift(self.cycloid.get_top()[1]*UP)

    def draw_cycloid(self, run_time = 3, **kwargs):
        kwargs["run_time"] = run_time
        self.play(
            RollAlongVector(
                self.circle,
                self.cycloid.points[-1]-self.cycloid.points[0],
                **kwargs
            ),
            ShowCreation(self.cycloid, **kwargs)
        )


class IntroduceCycloid(CycloidScene):
    def construct(self):
        CycloidScene.construct(self)

        equation = TexMobject("""
            \\dfrac{\\sin(\\theta)}{\\sqrt{y}} = 
            \\text{constant}
        """)
        new_eq = equation.copy()
        new_eq.to_edge(UP, buff = 1.3)
        cycloid_word = TextMobject("Cycloid")
        arrow = Arrow(2*UP, cycloid_word)
        arrow.reverse_points()

        self.play(ShimmerIn(equation))
        self.dither()
        self.play(
            ApplyMethod(equation.shift, 2.2*UP),
            ShowCreation(arrow)
        )
        self.play(ShimmerIn(cycloid_word))
        self.dither()
        self.grow_parts()
        self.draw_cycloid()
        self.dither()














