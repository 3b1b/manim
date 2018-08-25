#!/usr/bin/env python

from big_ol_pile_of_manim_imports import *
from dijkstra_scenes.graph import Graph
from collections import OrderedDict

# To watch one of these scenes, run the following:
# python extract_scene.py file_name <SceneName> -p
#
# Use the flat -l for a faster rendering at a lower
# quality, use -s to skip to the end and just show
# the final frame, and use -n <number> to skip ahead
# to the n'th animation of a scene.


class GraphTest(Scene):
    def construct(self):
        nodes = [
            (-3, 0, 0),
            (3, 0, 0),
        ]
        edges = [
            ((-3, 0, 0), (3, 0, 0))
        ]
        G = Graph(nodes, edges)
        self.play(ShowCreation(G))

        updates = OrderedDict([
            ("weight", TexMobject("a"))
        ])
        anims = G.update_component(edges[0], updates)
        a = anims[0]
        b = anims[1]
        self.play(*anims)
        self.wait(3)

class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        square.flip(RIGHT)
        square.rotate(-3 * TAU / 8)
        circle.set_fill(PINK, opacity=0.5)
        circle.wag(direction=UP)
        self.play(ShowCreation(circle))

        #a = TexMobject("a")
        #b = TexMobject("b").shift(DOWN)
        #self.play(ShowCreation(a))
        #self.play(ShowCreation(b))
        self.wait(5)


class WarpSquare(Scene):
    def construct(self):
        square = Square()
        self.play(ApplyPointwiseFunction(
            lambda point: complex_to_R3(np.exp(R3_to_complex(point))),
            square
        ))
        self.wait()


class WriteStuff(Scene):
    def construct(self):
        example_text = TextMobject(
            "This is a some text",
            tex_to_color_map={"text": YELLOW}
        )
        example_tex = TexMobject(
            "\\sum_{k=1}^\\infty {1 \\over k^2} = {\\pi^2 \\over 6}",
        )
        group = VGroup(example_text, example_tex)
        group.arrange_submobjects(DOWN)
        group.set_width(FRAME_WIDTH - 2 * LARGE_BUFF)

        self.play(Write(example_text))
        self.play(Write(example_tex))
        self.wait()


class UdatersExample(Scene):
    def construct(self):
        decimal = DecimalNumber(
            0,
            show_ellipsis=True,
            num_decimal_places=3,
            include_sign=True,
        )
        square = Square().to_edge(UP)

        decimal.add_updater(lambda d: d.next_to(square, RIGHT))
        decimal.add_updater(lambda d: d.set_value(square.get_center()[1]))
        self.add(square, decimal)
        self.play(
            square.to_edge, DOWN,
            rate_func=there_and_back,
            run_time=5,
        )
        self.wait()

# See old_projects folder for many, many more
