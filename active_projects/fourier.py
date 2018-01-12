from helpers import *


from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from animation.continual_animation import *
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
from mobject import *
from mobject.image_mobject import *
from mobject.vectorized_mobject import *
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from topics.graph_scene import *

class AddingPureFrequencies(PiCreatureScene):
    def construct(self):
        self.force_skipping()

        self.add_speaker()
        self.play_a440()
        self.measure_air_pressure()
        self.play_lower_pitch()
        self.play_mix()
        self.separate_out_parts()
        self.add_more_notes()

    def add_speaker(self):
        speaker = SVGMobject(file_name = "speaker")
        speaker.to_edge(DOWN)

        self.add(speaker)
        self.speaker = speaker

    def play_a440(self):
        randy = self.pi_creature
        a440_label = TextMobject("A440")
        a440_label.next_to(self.speaker, UP)

        self.broadcast(
            FadeIn(a440_label),
            randy.change, "pondering"
        )
        self.dither()

        self.set_variables_as_attrs(a440_label)

    def measure_air_pressure(self):
        randy = self.pi_creature
        axes = Axes(
            y_min = -1, y_max = 3,
            x_min = 0, x_max = 10,
            number_line_config = {"include_tip" : False},
        )
        axes.stretch_to_fit_height(2)
        axes.to_corner(UP+LEFT)
        axes.shift(MED_LARGE_BUFF*DOWN)

        frequency = 1.2
        func = self.get_wave_func(frequency, axes)
        graph = axes.get_graph(func)
        graph.highlight(YELLOW)
        pressure = TextMobject("Pressure")
        pressure.next_to(axes.y_axis, UP)
        pressure.shift_onto_screen()
        time = TextMobject("Time")
        time.next_to(axes.x_axis.get_right(), DOWN+LEFT)
        axes.labels = VGroup(pressure, time)
        axes.add(axes.labels)

        brace = Brace(Line(
            axes.coords_to_point(7/frequency, func(7/frequency)),
            axes.coords_to_point(8/frequency, func(8/frequency)),
        ), UP)
        words = brace.get_text("Imagine 440 per second", buff = SMALL_BUFF)

        self.revert_to_original_skipping_status()
        self.play(
            FadeIn(pressure),
            ShowCreation(axes.y_axis)
        )
        self.play(
            Write(time),
            ShowCreation(axes.x_axis)
        )
        self.dither()
        self.broadcast(
            ShowCreation(graph, run_time = 4, rate_func = None),
            randy.change, "erm", graph
        )
        self.play(
            GrowFromCenter(brace),
            Write(words)
        )
        self.dither(2)
        graph.save_state()
        self.play(
            FadeOut(brace),
            FadeOut(words),
            graph.fade, 0.7,
        )

        self.set_variables_as_attrs(
            axes,
            A440_func = func,
            A440_graph = graph,
        )

    def play_lower_pitch(self):
        pass

    def play_mix(self):
        pass

    def separate_out_parts(self):
        pass

    def add_more_notes(self):
        pass


    ####

    def broadcast(self, *added_anims, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", 5)
        kwargs["n_circles"] = kwargs.get("n_circles", 8)
        self.play(
            Broadcast(self.speaker[1], **kwargs),
            *added_anims
        )

    def get_wave_func(self, frequency, axes):
        tail_len = 3.0
        x_min, x_max = axes.x_min, axes.x_max
        def func(x):
            value = 0.8*np.cos(2*np.pi*frequency*x)
            if x - x_min < tail_len:
                value *= smooth((x-x_min)/tail_len)
            if x_max - x < tail_len:
                value *= smooth((x_max - x )/tail_len)
            return value + 1.5
        return func


    def create_pi_creature(self):
        return Randolph().to_corner(DOWN+LEFT)









