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

from topics.matrix import *
from topics.vector_space_scene import *
from eola.chapter9 import Jennifer, You

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

class Chapter5(LinearTransformationScene):
    def construct(self):
        self.plane.fade()
        self.add_unit_square()        
        self.plane.set_stroke(width = 6)
        VMobject(self.i_hat, self.j_hat).set_stroke(width = 10)
        self.square.set_fill(YELLOW, opacity = 0.7)
        self.square.set_stroke(width = 0)
        self.apply_transposed_matrix(self.t_matrix, run_time = 0)

class Chapter9(Scene):
    def construct(self):
        you = You()
        jenny = Jennifer()
        you.change_mode("erm")
        jenny.change_mode("speaking")
        you.shift(LEFT)
        jenny.shift(2*RIGHT)

        vector = Vector([3, 2])
        vector.center().shift(2*DOWN)
        vector.set_stroke(width = 8)
        vector.tip.scale_in_place(2)

        you.coords = Matrix([3, 2])
        jenny.coords = Matrix(["5/3", "1/3"])
        for pi in jenny, you:
            pi.bubble = pi.get_bubble(SpeechBubble, width = 3, height = 3)
            if pi is you:
                pi.bubble.shift(MED_SMALL_BUFF*RIGHT)
            else:
                pi.coords.scale(0.8)
                pi.bubble.shift(MED_SMALL_BUFF*LEFT)
            pi.bubble.add_content(pi.coords)
            pi.add(pi.bubble, pi.coords)
            pi.look_at(vector)

        self.add(you, jenny, vector)

class Chapter10(LinearTransformationScene):
    CONFIG = {
        "foreground_plane_kwargs" : {
            "x_radius" : 2*SPACE_WIDTH,
            "y_radius" : 2*SPACE_HEIGHT,
            "secondary_line_ratio" : 1

        },
        "include_background_plane" : False,
    }

    def construct(self):
        v_tex = "\\vec{\\textbf{v}}"
        eq = TexMobject("A", v_tex, "=", "\\lambda", v_tex)
        eq.highlight_by_tex(v_tex, YELLOW)
        eq.highlight_by_tex("\\lambda", MAROON_B)
        eq.scale(3)
        eq.add_background_rectangle()
        eq.shift(2*DOWN)        

        title = TextMobject(
            "Eigen", "vectors \\\\",
            "Eigen", "values"
        , arg_separator = "")
        title.scale(2.5)
        title.to_edge(UP)
        # title.highlight_by_tex("Eigen", MAROON_B)
        title[0].highlight(YELLOW)
        title[2].highlight(MAROON_B)
        title.add_background_rectangle()


        self.add_vector([-1, 1], color = YELLOW, animate = False)
        self.apply_transposed_matrix([[3, 0], [1, 2]])        
        self.plane.fade()
        self.remove(self.j_hat)
        self.add(eq, title)



















