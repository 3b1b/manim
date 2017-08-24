from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.continual_animation import ContinualAnimation
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from topics.probability import *
from topics.complex_numbers import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

E_COLOR = BLUE
M_COLOR = RED

class OscillatingVector(ContinualAnimation):
    CONFIG = {
        "tail" : ORIGIN,
        "frequency" : 1,
        "A_x" : 1,
        "A_y" : 0,
        "phi_x" : 0,
        "phi_y" : 0,
    }
    def setup(self):
        self.vector = self.mobject

    def update_mobject(self, dt):
        f = self.frequency
        t = self.internal_time
        angle = 2*np.pi*f*t
        vect = np.array([
            self.A_x*np.exp(complex(0, angle + self.phi_x)),
            self.A_y*np.exp(complex(0, angle + self.phi_y)),
            0,
        ]).real
        self.vector.put_start_and_end_on(self.tail, self.tail+vect)


class EMScene(Scene):
    def construct(self):
        pass


class Test(Scene):
    def construct(self):
        E_vect = Vector(UP, color = E_COLOR)
        wiggle = OscillatingVector(
            E_vect, 
            A_x = 2, 
            A_y = 1,
            phi_x = np.pi/2,
            frequency = 0.5,
            tail = UP+RIGHT,
        )
        randy = Randolph()

        self.add(randy)
        self.play(ShowCreation(wiggle.mobject))
        self.add(wiggle)
        self.dither(4)
        self.wind_down(wiggle)
        self.dither()
        # self.play(FadeOut(E_vect))
        # self.dither(2)





































