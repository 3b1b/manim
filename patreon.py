from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

class RandolphWatching(Scene):
    def construct(self):
        randy = Randolph()
        randy.shift(2*LEFT)
        randy.look(RIGHT)

        self.add(randy)
        self.dither()
        self.play(Blink(randy))
        self.dither()
        self.play(
            randy.change_mode, "pondering",
            randy.look, RIGHT
        )
        self.play(Blink(randy))
        self.dither()

class RandolphWatchingWithLaptop(Scene):
    pass

class GrowRonaksSierpinski(Scene):
    CONFIG = {
        "colors" : [BLUE, YELLOW, BLUE_C, BLUE_E],
        "dot_radius" : 0.08,
        "n_layers" : 64,
    }
    def construct(self):
        sierp = self.get_ronaks_sierpinski(self.n_layers)
        dots = self.get_dots(self.n_layers)
        self.triangle = VGroup(sierp, dots)
        self.triangle.scale(1.5)
        self.triangle.shift(3*UP)
        sierp_layers = sierp.submobjects
        dot_layers = dots.submobjects

        last_dot_layer = dot_layers[0]
        self.play(ShowCreation(last_dot_layer))
        run_time = 1
        for n, sierp_layer, dot_layer in zip(it.count(1), sierp_layers, dot_layers[1:]):
            self.play(
                ShowCreation(sierp_layer, submobject_mode = "one_at_a_time"),
                Animation(last_dot_layer),
                run_time = run_time
            )
            self.play(ShowCreation(
                dot_layer,
                run_time = run_time,
                submobject_mode = "all_at_once"
            ))
            if n == 2:
                dot = dot_layer[1]
                words = TextMobject("Stop growth at pink")
                words.next_to(dot, DOWN, 2)
                arrow = Arrow(words, dot)
                self.play(
                    Write(words),
                    ShowCreation(arrow)
                )
                self.dither()
                self.play(*map(FadeOut, [words, arrow]))
            log2 = np.log2(n)
            if n > 2 and log2-np.round(log2) == 0 and n < self.n_layers:
                self.dither()
                self.rescale()
                run_time /= 1.3
            last_dot_layer = dot_layer

    def rescale(self):
        shown_mobs = VGroup(*self.get_mobjects())
        shown_mobs_copy = shown_mobs.copy()
        self.remove(shown_mobs)
        self.add(shown_mobs_copy)
        top = shown_mobs.get_top()
        self.triangle.scale(0.5)
        self.triangle.move_to(top, aligned_edge = UP)
        self.play(Transform(shown_mobs_copy, shown_mobs))
        self.remove(shown_mobs_copy)
        self.add(shown_mobs)

    def get_pascal_point(self, n, k):
        return n*rotate_vector(RIGHT, -2*np.pi/3) + k*RIGHT

    def get_lines_at_layer(self, n):
        lines = VGroup()
        for k in range(n+1):
            if choose(n, k)%2 == 1:
                p1 = self.get_pascal_point(n, k)
                p2 = self.get_pascal_point(n+1, k)
                p3 = self.get_pascal_point(n+1, k+1)
                lines.add(Line(p1, p2), Line(p1, p3))
        return lines

    def get_dot_layer(self, n):
        dots = VGroup()
        for k in range(n+1):
            p = self.get_pascal_point(n, k)
            dot = Dot(p, radius = self.dot_radius)
            if choose(n, k)%2 == 0:
                if choose(n-1, k)%2 == 0:
                    continue
                dot.highlight(PINK)
            else:
                dot.highlight(WHITE)
            dots.add(dot)
        return dots

    def get_ronaks_sierpinski(self, n_layers):
        ronaks_sierpinski = VGroup()
        for n in range(n_layers):
            ronaks_sierpinski.add(self.get_lines_at_layer(n))
        ronaks_sierpinski.gradient_highlight(*self.colors)
        ronaks_sierpinski.set_stroke(width = 3)
        return ronaks_sierpinski

    def get_dots(self, n_layers):
        dots = VGroup()        
        for n in range(n_layers+1):
            dots.add(self.get_dot_layer(n))
        return dots

class PatreonLogin(Scene):
    pass

class PythagoreanTransformation(Scene):
    def construct(self):
        tri1 = VGroup(
            Line(ORIGIN, 2*RIGHT, color = BLUE),
            Line(2*RIGHT, 3*UP, color = YELLOW),
            Line(3*UP, ORIGIN, color = MAROON_B),
        )
        tri1.shift(2.5*(DOWN+LEFT))
        tri2, tri3, tri4 = copies = [
            tri1.copy().rotate(-i*np.pi/2)
            for i in range(1, 4)
        ]
        a = TexMobject("a").next_to(tri1[0], DOWN, buff = MED_BUFF)
        b = TexMobject("b").next_to(tri1[2], LEFT, buff = MED_BUFF)
        c = TexMobject("c").next_to(tri1[1].get_center(), UP+RIGHT)

        c_square = Polygon(*[
            tri[1].get_end()
            for tri in [tri1] + copies
        ])
        c_square.set_stroke(width = 0)
        c_square.set_fill(color = YELLOW, opacity = 0.5)
        c_square_tex = TexMobject("c^2")
        big_square = Polygon(*[
            tri[0].get_start()
            for tri in [tri1] + copies
        ])
        big_square.highlight(WHITE)
        a_square = Square(side_length = 2)
        a_square.shift(1.5*(LEFT+UP))
        a_square.set_stroke(width = 0)
        a_square.set_fill(color = BLUE, opacity = 0.5)
        a_square_tex = TexMobject("a^2")
        a_square_tex.move_to(a_square)
        b_square = Square(side_length = 3)
        b_square.move_to(
            a_square.get_corner(DOWN+RIGHT),
            aligned_edge = UP+LEFT
        )
        b_square.set_stroke(width = 0)
        b_square.set_fill(color = MAROON_B, opacity = 0.5)
        b_square_tex = TexMobject("b^2")
        b_square_tex.move_to(b_square)

        self.play(ShowCreation(tri1, run_time = 2))
        self.play(*map(Write, [a, b, c]))
        self.dither()
        self.play(
            FadeIn(c_square),
            Animation(c)
        )
        self.play(Transform(c, c_square_tex))
        self.dither(2)
        mover = tri1.copy()
        for copy in copies:
            self.play(Transform(
                mover, copy,
                path_arc = -np.pi/2
            ))
            self.add(copy)
        self.remove(mover)
        self.add(big_square, *[tri1]+copies)
        self.dither(2)
        self.play(*map(FadeOut, [a, b, c, c_square]))
        self.play(
            tri3.shift,
            tri1.get_corner(UP+LEFT) -\
            tri3.get_corner(UP+LEFT)
        )
        self.play(tri2.shift, 2*RIGHT)
        self.play(tri4.shift, 3*UP)
        self.dither()
        self.play(FadeIn(a_square))
        self.play(FadeIn(b_square))
        self.play(Write(a_square_tex))
        self.play(Write(b_square_tex))
        self.dither(2)































