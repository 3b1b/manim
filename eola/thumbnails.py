from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import VMobject

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.number_line import *
from topics.numerals import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from mobject.vectorized_mobject import *

from eola.matrix import *
from eola.two_d_space import *

class Chapter0(LinearTransformationScene):
    CONFIG = {
        "include_background_plane" : False,
        "t_matrix" : [[3, 1], [2, -1]]
    }
    def construct(self):
        self.setup()
        self.plane.fade()
        for mob in self.get_mobjects():
            mob.set_stroke(width = 6)
        self.apply_transposed_matrix(self.t_matrix, run_time = 0)

class Chapter1(Scene):
    def construct(self):
        arrow = Vector(2*UP+RIGHT)
        vs = TextMobject("vs.")
        array = Matrix([1, 2])
        array.highlight(TEAL)
        everyone = VMobject(arrow, vs, array)
        everyone.arrange_submobjects(RIGHT, buff = 0.5)
        everyone.scale_to_fit_height(4)
        self.add(everyone)

class Chapter2(LinearTransformationScene):
    def construct(self):
        self.lock_in_faded_grid()
        vectors = VMobject(*[
            Vector([x, y])
            for x in np.arange(-int(SPACE_WIDTH)+0.5, int(SPACE_WIDTH)+0.5)
            for y in np.arange(-int(SPACE_HEIGHT)+0.5, int(SPACE_HEIGHT)+0.5)
        ])
        vectors.submobject_gradient_highlight(PINK, BLUE_E)
        words = TextMobject("Span")
        words.scale(3)
        words.to_edge(UP)
        words.add_background_rectangle()
        self.add(vectors, words)


class Chapter3(Chapter0):
    CONFIG = {
        "t_matrix" : [[3, 0], [2, -1]]
    }

class Chapter4p1(Chapter0):
    CONFIG = {
        "t_matrix" : [[1, 0], [1, 1]]
    }

class Chapter4p2(Chapter0):
    CONFIG = {
        "t_matrix" : [[1, 2], [-1, 1]]
    }





















