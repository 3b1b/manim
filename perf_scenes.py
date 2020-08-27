from manimlib.imports import *

"""
A set of scenes to be used for performance testing of Manim.
"""


class Perf1(GraphScene):
    """
    A simple scene of two animations from the end of a video on recursion.

    - Uses a graph in 1/4 of the scene.
    - First fades in multiple lines of text and equations, and the graph axes.
    - Next animates creation of two graphs and the creation of their text
      labels.
    """
    CONFIG = {
        "x_axis_label":
        "$n$",
        "y_axis_label":
        "$time$",
        "x_axis_width":
        FRAME_HEIGHT,
        "y_axis_height":
        FRAME_HEIGHT / 2,
        "y_max":
        50,
        "y_min":
        0,
        "x_max":
        100,
        "x_min":
        0,
        "x_labeled_nums": [50, 100],
        "y_labeled_nums":
        range(0, 51, 10),
        "y_tick_frequency":
        10,
        "x_tick_frequency":
        10,
        "axes_color":
        BLUE,
        "graph_origin":
        np.array(
            (-FRAME_X_RADIUS + LARGE_BUFF, -FRAME_Y_RADIUS + LARGE_BUFF, 0))
    }

    def construct(self):
        t1 = TextMobject(
            "Dividing a problem in half over and over means\\\\"
            "the work done is proportional to $\\log_2{n}$").to_edge(UP)

        t2 = TextMobject(
            '\\textit{This is one of our\\\\favorite things to do in CS!}')
        t2.to_edge(RIGHT)

        t3 = TextMobject(
            'The new \\texttt{power(x,n)} is \\underline{much}\\\\better than the old!'
        )
        t3.scale(0.8)
        p1f = TexMobject('x^n=x \\times x^{n-1}').set_color(ORANGE)
        t4 = TextMobject('\\textit{vs.}').scale(0.8)
        p2f = TexMobject(
            'x^n=x^{\\frac{n}{2}} \\times x^{\\frac{n}{2}}').set_color(GREEN)
        p1v2g = VGroup(t3, p1f, t4, p2f).arrange(DOWN).center().to_edge(RIGHT)

        self.setup_axes()
        o_n = self.get_graph(lambda x: x, color=ORANGE, x_min=1, x_max=50)
        o_log2n = self.get_graph(lambda x: math.log2(x),
                                 color=GREEN,
                                 x_min=2,
                                 x_max=90)
        onl = TexMobject('O(n)')
        olog2nl = TexMobject('O(\\log_2{n})')
        onl.next_to(o_n.get_point_from_function(0.6), UL)
        olog2nl.next_to(o_log2n.get_point_from_function(0.8), UP)
        self.play(
            FadeIn(t1),
            FadeIn(self.axes),
            # FadeInFromDown(t2),
            FadeIn(p1v2g),
        )
        self.play(ShowCreation(o_n),
                  ShowCreation(o_log2n),
                  ShowCreation(onl),
                  ShowCreation(olog2nl),
                  run_time=3)
        self.wait(duration=5)
