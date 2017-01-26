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
from topics.objects import *
from scene import Scene
from scene.zoomed_scene import ZoomedScene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from eoc.chapter1 import OpeningQuote, PatreonThanks
from eoc.chapter2 import DISTANCE_COLOR, TIME_COLOR, VELOCITY_COLOR
from eoc.graph_scene import *

OUTPUT_COLOR = DISTANCE_COLOR
INPUT_COLOR = TIME_COLOR
DERIVATIVE_COLOR = VELOCITY_COLOR

class Chapter3OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            "You know, for a mathematician, he did not have \\\\ enough",
            "imagination.", 
            "But he has become a poet and \\\\ now he is fine.",
        ],
        "highlighted_quote_terms" : {
            "imagination." : BLUE,
        },
        "author" : "David Hilbert"
    }








class DerivativeOfXSquaredAsGraph(GraphScene, ZoomedScene, PiCreatureScene):
    CONFIG = {
        "start_x" : 2,
        "big_x" : 3,
        "dx" : 0.1,
        "x_min" : -9,
        "x_labeled_nums" : range(-8, 0, 2) + range(2, 10, 2),
        "y_labeled_nums" : range(2, 12, 2),
        "little_rect_nudge" : 0.5*(1.5*UP+RIGHT),
        "graph_origin" : 2.5*DOWN + LEFT,
        "zoomed_canvas_corner" : UP+LEFT,
    }
    def construct(self):
        self.draw_graph()
        self.ask_about_df_dx()
        self.show_differing_slopes()
        self.mention_alternate_view()

    def draw_graph(self):
        self.setup_axes()
        graph = self.get_graph(lambda x : x**2)
        label = self.get_graph_label(
            graph, "f(x) = x^2",
        )
        self.play(ShowCreation(graph))
        self.play(Write(label))
        self.dither()
        self.graph = graph

    def ask_about_df_dx(self):
        ss_group = self.get_secant_slope_group(
            self.start_x, self.graph,
            dx = self.dx,
            dx_label = "dx",
            df_label = "df",
        )
        secant_line = ss_group.secant_line
        ss_group.remove(secant_line)

        v_line, nudged_v_line = [
            self.get_vertical_line_to_graph(
                x, self.graph,
                line_class = DashedLine,
                color = RED,
                dashed_segment_length = 0.025
            )
            for x in self.start_x, self.start_x+self.dx
        ]

        df_dx = TexMobject("\\frac{df}{dx} ?")
        VGroup(*df_dx[:2]).highlight(ss_group.df_line.get_color())
        VGroup(*df_dx[3:5]).highlight(ss_group.dx_line.get_color())
        df_dx.next_to(
            self.input_to_graph_point(self.start_x, self.graph),
            DOWN+RIGHT,
            buff = MED_SMALL_BUFF
        )

        self.play(ShowCreation(v_line))
        self.dither()
        self.play(Transform(v_line.copy(), nudged_v_line))
        self.remove(self.get_mobjects_from_last_animation()[0])
        self.add(nudged_v_line)
        self.dither()
        self.activate_zooming()
        self.little_rectangle.replace(self.big_rectangle)
        self.play(
            FadeIn(self.little_rectangle),
            FadeIn(self.big_rectangle),
        )
        self.play(
            ApplyFunction(
                lambda r : self.position_little_rectangle(r, ss_group),
                self.little_rectangle
            ),
            self.pi_creature.change_mode, "pondering",
            self.pi_creature.look_at, ss_group
        )
        self.play(
            ShowCreation(ss_group.dx_line),
            Write(ss_group.dx_label),
        )
        self.dither()
        self.play(
            ShowCreation(ss_group.df_line),
            Write(ss_group.df_label),
        )
        self.dither()
        self.play(Write(df_dx))
        self.dither()
        self.play(*map(FadeOut, [
            v_line, nudged_v_line,
        ]))
        self.ss_group = ss_group

    def position_little_rectangle(self, rect, ss_group):
        rect.scale_to_fit_width(3*self.dx)
        rect.move_to(
            ss_group.dx_line.get_left()
        )
        rect.shift(
            self.dx*self.little_rect_nudge
        )
        return rect

    def show_differing_slopes(self):
        ss_group = self.ss_group
        def rect_update(rect):
            self.position_little_rectangle(rect, ss_group)

        self.play(
            ShowCreation(ss_group.secant_line),
            self.pi_creature.change_mode, "thinking"
        )
        ss_group.add(ss_group.secant_line)
        self.dither()
        for target_x in self.big_x, -self.dx/2, 1, 2:
            self.animate_secant_slope_group_change(
                ss_group, target_x = target_x,
                added_anims = [
                    UpdateFromFunc(self.little_rectangle, rect_update)
                ]
            )
            self.dither()

    def mention_alternate_view(self):
        self.remove(self.pi_creature)
        everything = VGroup(*self.get_mobjects())
        self.add(self.pi_creature)
        self.disactivate_zooming()
        self.play(
            ApplyMethod(
                everything.shift, 2*SPACE_WIDTH*LEFT,
                rate_func = lambda t : running_start(t, -0.1)
            ),
            self.pi_creature.change_mode, "happy"
        )
        self.say("Let's try \\\\ another view.", target_mode = "speaking")
        self.dither(2)

class NudgeSideLengthOfSquare(PiCreatureScene):
    CONFIG = {
        "square_width" : 3,
        "dx" : 0.5,
    }
    def construct(self):
        ApplyMethod(self.pi_creature.change_mode, "speaking").update(1)
        self.add_function_label()
        self.introduce_square()
        self.increase_area()
        self.examine_thin_rectangles()
        self.examine_tiny_square()
        self.write_out_derivative()
        self.shrink_dx()

    def add_function_label(self):
        label = TexMobject("f(x) = x^2")
        label.next_to(ORIGIN, RIGHT)
        label.to_edge(UP)
        self.add(label)

    def introduce_square(self):
        square = Square(
            side_length = self.square_width,
            stroke_width = 0,
            fill_opacity = 0.75,
            fill_color = BLUE,
        )
        square.to_corner(UP+LEFT, buff = LARGE_BUFF)
        x_squared = TexMobject("x^2")
        x_squared.move_to(square)

        braces = VGroup()
        for vect in DOWN, RIGHT:
            brace = Brace(square, vect)
            brace.add(brace.get_text("$x$"))
            braces.add(brace)

        self.play(DrawBorderThenFill(square))
        self.add(square, x_squared, braces)


    def increase_area(self):
        pass

    def examine_thin_rectangles(self):
        pass

    def examine_tiny_square(self):
        pass

    def write_out_derivative(self):
        pass

    def shrink_dx(self):
        pass











































