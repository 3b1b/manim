from helpers import *
import scipy

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
from topics.common_scenes import *
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


def get_fourier_transform(
    func, t_min, t_max, 
    real_part = True, 
    use_almost_fourier = True,
    ):
    # part = "real" if real_part else "imag"
    trig = np.cos if real_part else np.sin
    scalar = 1./(t_max - t_min) if use_almost_fourier else 1.0
    def fourier_transform(f):
        return scalar*scipy.integrate.quad(
            lambda t : func(t)*trig(-TAU*f*t),
            t_min, t_max
        )[0]
    return fourier_transform

##

class AddingPureFrequencies(PiCreatureScene):
    CONFIG = {
        "A_frequency" : 2.1,
        "A_color" : YELLOW,
        "D_color" : PINK,
        "F_color" : TEAL,
        "C_color" : RED,
        "sum_color" : GREEN,
        "equilibrium_height" : 1.5,
    }
    def construct(self):
        self.add_speaker()
        self.play_A440()
        self.measure_air_pressure()
        self.play_lower_pitch()
        self.play_mix()
        self.separate_out_parts()
        self.draw_sum_at_single_point()
        self.draw_full_sum()
        self.add_more_notes()

    def add_speaker(self):
        speaker = SVGMobject(file_name = "speaker")
        speaker.to_edge(DOWN)

        self.add(speaker)
        self.speaker = speaker

    def play_A440(self):
        randy = self.pi_creature
        A_label = TextMobject("A440")
        A_label.highlight(self.A_color)
        A_label.next_to(self.speaker, UP)

        self.broadcast(
            FadeIn(A_label),
            Succession(
                ApplyMethod, randy.change, "pondering",
                Animation, randy,
                Blink, randy
            )
        )

        self.set_variables_as_attrs(A_label)

    def measure_air_pressure(self):
        randy = self.pi_creature
        axes = Axes(
            y_min = -2, y_max = 2,
            x_min = 0, x_max = 10,
            number_line_config = {"include_tip" : False},
        )
        axes.stretch_to_fit_height(2)
        axes.to_corner(UP+LEFT)
        axes.shift(LARGE_BUFF*DOWN)
        eh = self.equilibrium_height
        equilibrium_line = DashedLine(
            axes.coords_to_point(0, eh),
            axes.coords_to_point(axes.x_max, eh),
            stroke_width = 2,
            stroke_color = LIGHT_GREY
        )

        frequency = self.A_frequency
        graph = self.get_wave_graph(frequency, axes)
        func = graph.underlying_function
        graph.highlight(self.A_color)
        pressure = TextMobject("Pressure")
        time = TextMobject("Time")
        for label in pressure, time:
            label.scale_in_place(0.8)
        pressure.next_to(axes.y_axis, UP)
        pressure.to_edge(LEFT, buff = MED_SMALL_BUFF)
        time.next_to(axes.x_axis.get_right(), DOWN+LEFT)
        axes.labels = VGroup(pressure, time)

        n = 10
        brace = Brace(Line(
            axes.coords_to_point(n/frequency, func(n/frequency)),
            axes.coords_to_point((n+1)/frequency, func((n+1)/frequency)),
        ), UP)
        words = brace.get_text("Imagine 440 per second", buff = SMALL_BUFF)
        words.scale(0.8, about_point = words.get_bottom())

        self.play(
            FadeIn(pressure),
            ShowCreation(axes.y_axis)
        )
        self.play(
            Write(time),
            ShowCreation(axes.x_axis)
        )
        self.broadcast(
            ShowCreation(graph, run_time = 4, rate_func = None),
            ShowCreation(equilibrium_line),
        )
        axes.add(equilibrium_line)
        self.play(
            randy.change, "erm", graph,
            GrowFromCenter(brace),
            Write(words)
        )
        self.wait()
        graph.save_state()
        self.play(
            FadeOut(brace),
            FadeOut(words),
            VGroup(axes, graph, axes.labels).shift, 0.8*UP,
            graph.fade, 0.85,
            graph.shift, 0.8*UP,
        )

        graph.saved_state.move_to(graph)
        self.set_variables_as_attrs(axes, A_graph = graph)

    def play_lower_pitch(self):
        axes = self.axes
        randy = self.pi_creature

        frequency = self.A_frequency*(2.0/3.0)
        graph = self.get_wave_graph(frequency, axes)
        graph.set_color(self.D_color)

        D_label = TextMobject("D294")
        D_label.highlight(self.D_color)
        D_label.move_to(self.A_label)

        self.play(
            FadeOut(self.A_label),
            GrowFromCenter(D_label),
        )
        self.broadcast(
            ShowCreation(graph, run_time = 4, rate_func = None),
            randy.change, "happy",
            n_circles = 6,
        )
        self.play(randy.change, "confused", graph)
        self.wait(2)

        self.set_variables_as_attrs(
            D_label,
            D_graph = graph
        )

    def play_mix(self):
        self.A_graph.restore()
        self.broadcast(
            self.get_broadcast_animation(n_circles = 6),
            self.pi_creature.change, "thinking",
            *[
                ShowCreation(graph, run_time = 4, rate_func = None)
                for graph in self.A_graph, self.D_graph
            ]
        )
        self.wait()

    def separate_out_parts(self):
        axes = self.axes
        speaker = self.speaker
        randy = self.pi_creature

        A_axes = axes.deepcopy()
        A_graph = self.A_graph
        A_label = self.A_label
        D_axes = axes.deepcopy()
        D_graph = self.D_graph
        D_label = self.D_label
        movers = [A_axes, A_graph, A_label, D_axes, D_graph, D_label]
        for mover in movers:
            mover.generate_target()
        D_target_group = VGroup(D_axes.target, D_graph.target)
        A_target_group = VGroup(A_axes.target, A_graph.target)
        D_target_group.next_to(axes, DOWN, MED_LARGE_BUFF)
        A_target_group.next_to(D_target_group, DOWN, MED_LARGE_BUFF)
        A_label.fade(1)
        A_label.target.next_to(A_graph.target, UP)
        D_label.target.next_to(D_graph.target, UP)

        self.play(*it.chain(
            map(MoveToTarget, movers),
            [
                ApplyMethod(mob.shift, SPACE_HEIGHT*DOWN, remover = True)
                for mob in  randy, speaker
            ]
        ))
        self.wait()

        self.set_variables_as_attrs(A_axes, D_axes)

    def draw_sum_at_single_point(self):
        axes = self.axes
        A_axes = self.A_axes
        D_axes = self.D_axes
        A_graph = self.A_graph
        D_graph = self.D_graph

        x = 2.85
        A_line = self.get_A_graph_v_line(x)
        D_line = self.get_D_graph_v_line(x)
        lines = VGroup(A_line, D_line)
        sum_lines = lines.copy()
        sum_lines.generate_target()
        self.stack_v_lines(x, sum_lines.target)

        top_axes_point = axes.coords_to_point(x, self.equilibrium_height)
        x_point = np.array(top_axes_point)
        x_point[1] = 0
        v_line = Line(UP, DOWN).scale(SPACE_HEIGHT).move_to(x_point)

        self.revert_to_original_skipping_status()
        self.play(GrowFromCenter(v_line))
        self.play(FadeOut(v_line))
        self.play(*map(ShowCreation, lines))
        self.wait()
        self.play(MoveToTarget(sum_lines, path_arc = np.pi/4))
        self.wait(2)
        # self.play(*[
        #     Transform(
        #         line, 
        #         VectorizedPoint(axes.coords_to_point(0, self.equilibrium_height)),
        #         remover = True
        #     )
        #     for line, axes in [
        #         (A_line, A_axes),
        #         (D_line, D_axes),
        #         (sum_lines, axes),
        #     ]
        # ])
        self.lines_to_fade = VGroup(A_line, D_line, sum_lines)

    def draw_full_sum(self):
        axes = self.axes

        def new_func(x):
            result = self.A_graph.underlying_function(x)
            result += self.D_graph.underlying_function(x)
            result -= self.equilibrium_height
            return result

        sum_graph = axes.get_graph(new_func)
        sum_graph.highlight(self.sum_color)
        thin_sum_graph = sum_graph.copy().fade()

        A_graph = self.A_graph
        D_graph = self.D_graph
        D_axes = self.D_axes

        rect = Rectangle(
            height = 2.5*SPACE_HEIGHT,
            width = MED_SMALL_BUFF,
            stroke_width = 0,
            fill_color = YELLOW,
            fill_opacity = 0.4
        )

        self.play(
            ReplacementTransform(A_graph.copy(), thin_sum_graph),
            ReplacementTransform(D_graph.copy(), thin_sum_graph),
            # FadeOut(self.lines_to_fade)
        )
        self.play(
            self.get_graph_line_animation(self.A_axes, self.A_graph),
            self.get_graph_line_animation(self.D_axes, self.D_graph),
            self.get_graph_line_animation(axes, sum_graph.deepcopy()),
            ShowCreation(sum_graph),
            run_time = 15,
            rate_func = None
        )
        self.remove(thin_sum_graph)
        self.wait()
        for x in 2.85, 3.57:
            rect.move_to(D_axes.coords_to_point(x, 0))
            self.play(GrowFromPoint(rect, rect.get_top()))
            self.wait()
            self.play(FadeOut(rect))

        self.sum_graph = sum_graph

    def add_more_notes(self):
        axes = self.axes

        A_group = VGroup(self.A_axes, self.A_graph, self.A_label)
        D_group = VGroup(self.D_axes, self.D_graph, self.D_label)
        squish_group = VGroup(A_group, D_group)
        squish_group.generate_target()
        squish_group.target.stretch(0.5, 1)
        squish_group.target.next_to(axes, DOWN, buff = -SMALL_BUFF)
        for group in squish_group.target:
            label = group[-1]
            bottom = label.get_bottom()
            label.stretch_in_place(0.5, 0)
            label.move_to(bottom, DOWN)

        self.play(
            MoveToTarget(squish_group),
            FadeOut(self.lines_to_fade),
        )

        F_axes = self.D_axes.deepcopy()
        C_axes = self.A_axes.deepcopy()
        VGroup(F_axes, C_axes).next_to(squish_group, DOWN)
        F_graph = self.get_wave_graph(self.A_frequency*4.0/5, F_axes)
        F_graph.highlight(self.F_color)
        C_graph = self.get_wave_graph(self.A_frequency*6.0/5, C_axes)
        C_graph.highlight(self.C_color)

        F_label = TextMobject("F349")
        C_label = TextMobject("C523")
        for label, graph in (F_label, F_graph), (C_label, C_graph):
            label.scale(0.5)
            label.highlight(graph.get_stroke_color())
            label.next_to(graph, UP, SMALL_BUFF)

        graphs = VGroup(self.A_graph, self.D_graph, F_graph, C_graph)
        def new_sum_func(x):
            result = sum([
                graph.underlying_function(x) - self.equilibrium_height
                for graph in graphs
            ])
            result *= 0.5
            return result + self.equilibrium_height
        new_sum_graph = self.axes.get_graph(
            new_sum_func, 
            num_graph_points = 200
        )
        new_sum_graph.highlight(BLUE_C)
        thin_new_sum_graph = new_sum_graph.copy().fade()

        self.play(*it.chain(
            map(ShowCreation, [F_axes, C_axes, F_graph, C_graph]),
            map(Write, [F_label, C_label]),
            map(FadeOut, [self.sum_graph])
        ))
        self.play(ReplacementTransform(
            graphs.copy(), thin_new_sum_graph
        ))
        kwargs = {"rate_func" : None, "run_time" : 10}
        self.play(ShowCreation(new_sum_graph.copy(), **kwargs), *[
            self.get_graph_line_animation(curr_axes, graph, **kwargs)
            for curr_axes, graph in [
                (self.A_axes, self.A_graph),
                (self.D_axes, self.D_graph),
                (F_axes, F_graph),
                (C_axes, C_graph),
                (axes, new_sum_graph),
            ]
        ])
        self.wait()

    ####

    def broadcast(self, *added_anims, **kwargs):
        self.play(self.get_broadcast_animation(**kwargs), *added_anims)

    def get_broadcast_animation(self, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", 5)
        kwargs["n_circles"] = kwargs.get("n_circles", 10)
        return Broadcast(self.speaker[1], **kwargs)

    def get_wave_graph(self, frequency, axes):
        tail_len = 3.0
        x_min, x_max = axes.x_min, axes.x_max
        def func(x):
            value = 0.7*np.cos(2*np.pi*frequency*x)
            if x - x_min < tail_len:
                value *= smooth((x-x_min)/tail_len)
            if x_max - x < tail_len:
                value *= smooth((x_max - x )/tail_len)
            return value + self.equilibrium_height
        ngp = 2*(x_max - x_min)*frequency + 1
        graph = axes.get_graph(func, num_graph_points = int(ngp))
        return graph

    def get_A_graph_v_line(self, x):
        return self.get_graph_v_line(x, self.A_axes, self.A_graph)

    def get_D_graph_v_line(self, x):
        return self.get_graph_v_line(x, self.D_axes, self.D_graph)

    def get_graph_v_line(self, x, axes, graph):
        result = Line(
            axes.coords_to_point(x, self.equilibrium_height),
            # axes.coords_to_point(x, graph.underlying_function(x)),
            graph.point_from_proportion(float(x)/axes.x_max),
            color = WHITE,
            buff = 0,
        )
        return result

    def stack_v_lines(self, x, lines):
        point = self.axes.coords_to_point(x, self.equilibrium_height)
        A_line, D_line = lines
        A_line.shift(point - A_line.get_start())
        D_line.shift(A_line.get_end()-D_line.get_start())
        A_line.highlight(self.A_color)
        D_line.highlight(self.D_color)
        return lines

    def create_pi_creature(self):
        return Randolph().to_corner(DOWN+LEFT)

    def get_graph_line_animation(self, axes, graph, **kwargs):
        line = self.get_graph_v_line(0, axes, graph)
        x_max = axes.x_max
        def update_line(line, alpha):
            x = alpha*x_max
            Transform(line, self.get_graph_v_line(x, axes, graph)).update(1)
            return line

        return UpdateFromAlphaFunc(line, update_line, **kwargs)

class BreakApartSum(Scene):
    CONFIG = {
        "frequencies" : [0.5, 1.5, 2, 2.5, 5],
        "equilibrium_height" : 2.0,
    }
    def construct(self):
        self.show_initial_sound()
        self.decompose_sound()
        self.ponder_question()

    def show_initial_sound(self):
        def func(x):
            return self.equilibrium_height + 0.2*np.sum([
                np.cos(2*np.pi*f*x)
                for f in self.frequencies
            ])
        axes = Axes(
            x_min = 0, x_max = 5,
            y_min = -1, y_max = 5,
            x_axis_config = {
                "include_tip" : False,
                "unit_size" : 2.0,
            },
            y_axis_config = {
                "include_tip" : False,
                "unit_size" : 0.5,
            },
        )
        axes.stretch_to_fit_width(2*SPACE_WIDTH - 2)
        axes.stretch_to_fit_height(3)
        axes.center()
        axes.to_edge(LEFT)
        graph = axes.get_graph(func, num_graph_points = 200)
        graph.highlight(YELLOW)

        v_line = Line(ORIGIN, 4*UP)
        v_line.move_to(axes.coords_to_point(0, 0), DOWN)
        dot = Dot(color = PINK)
        dot.move_to(graph.point_from_proportion(0))

        self.add(axes, graph)
        self.play(
            v_line.move_to, axes.coords_to_point(5, 0), DOWN,
            MoveAlongPath(dot, graph),
            run_time = 8,
            rate_func = None,
        )
        self.play(*map(FadeOut, [dot, v_line]))

        self.set_variables_as_attrs(axes, graph)

    def decompose_sound(self):
        axes, graph = self.axes, self.graph

        pure_graphs = VGroup(*[
            axes.get_graph(
                lambda x : 0.5*np.cos(2*np.pi*freq*x),
                num_graph_points = 100,
            )
            for freq in self.frequencies
        ])
        pure_graphs.gradient_highlight(BLUE, RED)
        pure_graphs.arrange_submobjects(DOWN, buff = MED_LARGE_BUFF)
        h_line = DashedLine(6*LEFT, 6*RIGHT)

        self.play(
            FadeOut(axes),
            graph.to_edge, UP
        )
        pure_graphs.next_to(graph, DOWN, LARGE_BUFF)
        h_line.next_to(graph, DOWN, MED_LARGE_BUFF)
        self.play(ShowCreation(h_line))
        for pure_graph in reversed(pure_graphs):
            self.play(ReplacementTransform(graph.copy(), pure_graph))
        self.wait()

        self.all_graphs = VGroup(graph, h_line, pure_graphs)
        self.pure_graphs = pure_graphs

    def ponder_question(self):
        all_graphs = self.all_graphs
        pure_graphs = self.pure_graphs
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)

        self.play(
            FadeIn(randy),
            all_graphs.scale, 0.75,
            all_graphs.to_corner, UP+RIGHT,
        )
        self.play(randy.change, "pondering", all_graphs)
        self.play(Blink(randy))
        rect = SurroundingRectangle(pure_graphs, color = WHITE)
        self.play(
            ShowCreation(rect),
            LaggedStart(
                ApplyFunction, pure_graphs,
                lambda g : (lambda m : m.shift(SMALL_BUFF*UP).highlight(YELLOW), g),
                rate_func = wiggle
            )
        )
        self.play(FadeOut(rect))
        self.play(Blink(randy))
        self.wait()

class Quadrant(VMobject):
    CONFIG = {
        "radius" : 2,
        "stroke_width": 0,
        "fill_opacity" : 1,
        "density" : 50,
        "density_exp" : 2.0,
    }
    def generate_points(self):
        points = [r*RIGHT for r in np.arange(0, self.radius, 1./self.density)]
        points += [
            self.radius*(np.cos(theta)*RIGHT + np.sin(theta)*UP)
            for theta in np.arange(0, TAU/4, 1./(self.radius*self.density))
        ]
        points += [r*UP for r in np.arange(self.radius, 0, -1./self.density)]
        self.set_points_smoothly(points)

class UnmixMixedPaint(Scene):
    CONFIG = {
        "colors" : [BLUE, RED, YELLOW, GREEN],
    }
    def construct(self):
        angles = np.arange(4)*np.pi/2
        quadrants = VGroup(*[
            Quadrant().rotate(angle, about_point = ORIGIN).highlight(color)
            for color, angle in zip(self.colors, angles)
        ])
        quadrants.add(*it.chain(*[
            quadrants.copy().rotate(angle)
            for angle in np.linspace(0, 0.02*TAU, 10)
        ]))
        quadrants.set_fill(opacity = 0.5)

        mud_color = average_color(*self.colors)
        mud_circle = Circle(radius = 2, stroke_width = 0)
        mud_circle.set_fill(mud_color, 1)
        mud_circle.save_state()
        mud_circle.scale(0)

        def update_quadrant(quadrant, alpha):
            points = quadrant.get_anchors()
            dt = 0.03 #Hmm, this has no dependency on frame rate...
            norms = np.apply_along_axis(np.linalg.norm, 1, points)

            points[:,0] -= dt*points[:,1]/np.clip(norms, 0.1, np.inf)
            points[:,1] += dt*points[:,0]/np.clip(norms, 0.1, np.inf)

            new_norms = np.apply_along_axis(np.linalg.norm, 1, points)
            new_norms = np.clip(new_norms, 0.001, np.inf)
            radius = np.max(norms)
            multiplier = norms/new_norms
            multiplier = multiplier.reshape((len(multiplier), 1))
            multiplier.repeat(points.shape[1], axis = 1)
            points *= multiplier
            quadrant.set_points_smoothly(points)

        self.add(quadrants)
        run_time = 30
        self.play(
            *[
                UpdateFromAlphaFunc(quadrant, update_quadrant)
                for quadrant in quadrants
            ] + [
                ApplyMethod(mud_circle.restore, rate_func = None)
            ],
            run_time = run_time
        )

#Incomplete, and probably not useful
class MachineThatTreatsOneFrequencyDifferently(Scene):
    def construct(self):
        graph = self.get_cosine_graph(0.5)
        frequency_mob = DecimalNumber(220, num_decimal_points = 0)
        frequency_mob.next_to(graph, UP, buff = MED_LARGE_BUFF)

        self.graph = graph
        self.frequency_mob = frequency_mob
        self.add(graph, frequency_mob)

        arrow1, q_marks, arrow2 = group = VGroup(
            Vector(DOWN), TextMobject("???").scale(1.5), Vector(DOWN)
        )
        group.highlight(WHITE)
        group.arrange_submobjects(DOWN)
        group.next_to(graph, DOWN)
        self.add(group)

        self.change_graph_frequency(1)
        graph.highlight(GREEN)
        self.wait()
        graph.highlight(YELLOW)
        self.change_graph_frequency(2)
        self.wait()


    def change_graph_frequency(self, frequency, run_time = 2):
        graph = self.graph
        frequency_mob = self.frequency_mob
        curr_frequency = graph.frequency
        self.play(
            UpdateFromAlphaFunc(
                graph, self.get_signal_update_func(graph, frequency),
            ),
            ChangingDecimal(
                frequency_mob, 
                lambda a : 440*interpolate(curr_frequency, frequency, a)
            ),
            run_time = run_time,
        )
        graph.frequency = frequency

    def get_signal_update_func(self, graph, target_frequency):
        curr_frequency = graph.frequency
        def update(graph, alpha):
            frequency = interpolate(curr_frequency, target_frequency, alpha)
            new_graph = self.get_cosine_graph(frequency)
            Transform(graph, new_graph).update(1)
            return graph
        return update

    def get_cosine_graph(self, frequency, num_steps = 200, color = YELLOW):
        result = FunctionGraph(
            lambda x : 0.5*np.cos(2*np.pi*frequency*x),
            num_steps = num_steps
        )
        result.frequency = frequency
        result.shift(2*UP)
        return result

class FourierMachineScene(Scene):
    CONFIG = {
        "time_axes_config" : {
            "x_min" : 0,
            "x_max" : 4.4,
            "x_axis_config" : {
                "unit_size" : 3,
                "tick_frequency" : 0.25,
                "numbers_with_elongated_ticks" : [1, 2, 3],
            },
            "y_min" : 0,
            "y_max" : 2,
            "y_axis_config" : {"unit_size" : 0.8},
        },
        "time_label_t" : 3.4,
        "circle_plane_config" : {
            "x_radius" : 2.1,
            "y_radius" : 2.1,
            "x_unit_size" : 1,
            "y_unit_size" : 1,
        },
        "frequency_axes_config" : {
            "number_line_config" : {
                "color" : TEAL,
            },
            "x_min" : 0,
            "x_max" : 5.0,
            "x_axis_config" : {
                "unit_size" : 1.4,
            },
            "y_min" : -1.0,
            "y_max" : 1.0,
            "y_axis_config" : {
                "unit_size" : 1.8,
                "tick_frequency" : 0.5,
                "line_to_number_vect" : LEFT,
            },
            "color" : TEAL,
        },
        "frequency_axes_box_color" : TEAL_E,
        "text_scale_val" : 0.75,
        "default_graph_config" : {
            "num_graph_points" : 100,
            "color" : YELLOW,
        },
        "equilibrium_height" : 1,
        "default_y_vector_animation_config" : {
            "run_time" : 5,
            "rate_func" : None,
            "remover" : True,
        },
        "default_time_sweep_config" : {
            "rate_func" : None,
            "run_time" : 5,
        },
        "default_num_v_lines_indicating_periods" : 20,
    }

    def get_time_axes(self):
        time_axes = Axes(**self.time_axes_config)
        time_axes.x_axis.add_numbers()
        time_label = TextMobject("Time")
        intensity_label = TextMobject("Intensity")
        labels = VGroup(time_label, intensity_label)
        for label in labels:
            label.scale(self.text_scale_val)
        time_label.next_to(
            time_axes.coords_to_point(self.time_label_t,0), 
            DOWN
        )
        intensity_label.next_to(time_axes.y_axis.get_top(), RIGHT)
        time_axes.labels = labels
        time_axes.add(labels)
        time_axes.to_corner(UP+LEFT)
        self.time_axes = time_axes
        return time_axes

    def get_circle_plane(self):
        circle_plane = NumberPlane(**self.circle_plane_config)
        circle_plane.to_corner(DOWN+LEFT)
        circle = DashedLine(ORIGIN, TAU*UP).apply_complex_function(np.exp)
        circle.scale(circle_plane.x_unit_size)
        circle.move_to(circle_plane.coords_to_point(0, 0))
        circle_plane.circle = circle
        circle_plane.add(circle)
        circle_plane.fade()
        self.circle_plane = circle_plane
        return circle_plane

    def get_frequency_axes(self):
        frequency_axes = Axes(**self.frequency_axes_config)
        frequency_axes.x_axis.add_numbers(*range(1, 6))
        frequency_axes.y_axis.add_numbers(
            *frequency_axes.y_axis.get_tick_numbers()
        )
        box = SurroundingRectangle(
            frequency_axes,
            buff = MED_SMALL_BUFF,
            color = self.frequency_axes_box_color,
        )
        frequency_axes.box = box
        frequency_axes.add(box)
        frequency_axes.to_corner(DOWN+RIGHT, buff = MED_SMALL_BUFF)

        frequency_label = TextMobject("Frequency")
        frequency_label.scale(self.text_scale_val)
        frequency_label.next_to(
            frequency_axes.x_axis.get_right(), DOWN, 
            buff = MED_LARGE_BUFF,
            aligned_edge = RIGHT,
        )
        frequency_axes.label = frequency_label
        frequency_axes.add(frequency_label)

        self.frequency_axes = frequency_axes
        return frequency_axes

    def get_time_graph(self, func, **kwargs):
        if not hasattr(self, "time_axes"):
            self.get_time_axes()
        config = dict(self.default_graph_config)
        config.update(kwargs)
        graph = self.time_axes.get_graph(func, **config)
        return graph

    def get_cosine_wave(self, freq = 1, shift_val = 1, scale_val = 0.9):
        return self.get_time_graph(
            lambda t : shift_val + scale_val*np.cos(TAU*freq*t)
        )

    def get_fourier_transform_graph(self, time_graph, **kwargs):
        if not hasattr(self, "frequency_axes"):
            self.get_frequency_axes()
        func = time_graph.underlying_function
        t_min = self.time_axes.x_min
        t_max = self.time_axes.x_max
        return self.frequency_axes.get_graph(
            get_fourier_transform(func, t_min, t_max, **kwargs),
            color = self.center_of_mass_color,
        )

    def get_polarized_mobject(self, mobject, freq = 1.0):
        if not hasattr(self, "circle_plane"):
            self.get_circle_plane()
        polarized_mobject = mobject.copy()
        polarized_mobject.apply_function(lambda p : self.polarize_point(p, freq))
        # polarized_mobject.make_smooth()
        mobject.polarized_mobject = polarized_mobject
        polarized_mobject.frequency = freq
        return polarized_mobject

    def polarize_point(self, point, freq = 1.0):
        t, y = self.time_axes.point_to_coords(point)
        z = y*np.exp(complex(0, -2*np.pi*freq*t))
        return self.circle_plane.coords_to_point(z.real, z.imag)

    def get_polarized_animation(self, mobject, freq = 1.0):
        p_mob = self.get_polarized_mobject(mobject, freq = freq)
        def update_p_mob(p_mob):
            Transform(
                p_mob, 
                self.get_polarized_mobject(mobject, freq = freq)
            ).update(1)
            mobject.polarized_mobject = p_mob
            return p_mob
        return UpdateFromFunc(p_mob, update_p_mob)

    def animate_frequency_change(self, mobjects, new_freq, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", 3.0)
        added_anims = kwargs.get("added_anims", [])
        self.play(*[
            self.get_frequency_change_animation(mob, new_freq, **kwargs)
            for mob in mobjects
        ] + added_anims)

    def get_frequency_change_animation(self, mobject, new_freq, **kwargs):
        if not hasattr(mobject, "polarized_mobject"):
            mobject.polarized_mobject = self.get_polarized_mobject(mobject)
        start_freq = mobject.polarized_mobject.frequency
        def update(pm, alpha):
            freq = interpolate(start_freq, new_freq, alpha)
            new_pm = self.get_polarized_mobject(mobject, freq)
            Transform(pm, new_pm).update(1)
            mobject.polarized_mobject = pm
            mobject.polarized_mobject.frequency = freq
            return pm
        return UpdateFromAlphaFunc(mobject.polarized_mobject, update, **kwargs)

    def get_time_graph_y_vector_animation(self, graph, **kwargs):
        config = dict(self.default_y_vector_animation_config)
        config.update(kwargs)
        vector = Vector(UP, color = WHITE)
        graph_copy = graph.copy()
        x_axis = self.time_axes.x_axis
        x_min, x_max = x_axis.x_min, x_axis.x_max
        def update_vector(vector, alpha):
            x = interpolate(x_min, x_max, alpha)
            vector.put_start_and_end_on(
                self.time_axes.coords_to_point(x, 0),
                self.time_axes.input_to_graph_point(x, graph_copy)
            )
            return vector
        return UpdateFromAlphaFunc(vector, update_vector, **config)

    def get_polarized_vector_animation(self, polarized_graph, **kwargs):
        config = dict(self.default_y_vector_animation_config)
        config.update(kwargs)
        vector = Vector(RIGHT, color = WHITE)
        origin = self.circle_plane.coords_to_point(0, 0)
        graph_copy = polarized_graph.copy()
        def update_vector(vector, alpha):
            point = graph_copy.point_from_proportion(alpha)
            vector.put_start_and_end_on_with_projection(origin, point)
            return vector
        return UpdateFromAlphaFunc(vector, update_vector, **config)

    def get_vector_animations(self, graph, draw_polarized_graph = True, **kwargs):
        config = dict(self.default_y_vector_animation_config)
        config.update(kwargs)
        anims = [
            self.get_time_graph_y_vector_animation(graph, **config),
            self.get_polarized_vector_animation(graph.polarized_mobject, **config),
        ]
        if draw_polarized_graph:
            new_config = dict(config)
            new_config["remover"] = False
            anims.append(ShowCreation(graph.polarized_mobject, **new_config))
        return anims

    def animate_time_sweep(self, freq, n_repeats = 1, t_max = None, **kwargs):
        added_anims = kwargs.pop("added_anims", [])
        config = dict(self.default_time_sweep_config)
        config.update(kwargs)
        circle_plane = self.circle_plane
        time_axes = self.time_axes
        ctp = time_axes.coords_to_point
        t_max = t_max or time_axes.x_max
        v_line = DashedLine(
            ctp(0, 0), ctp(0, time_axes.y_max),
            stroke_width = 6,
        )
        v_line.highlight(RED)

        for x in range(n_repeats):
            v_line.move_to(ctp(0, 0), DOWN)
            self.play(
                ApplyMethod(
                    v_line.move_to, 
                    ctp(t_max, 0), DOWN
                ),
                self.get_polarized_animation(v_line, freq = freq),
                *added_anims,
                **config
            )
            self.remove(v_line.polarized_mobject)
        self.play(FadeOut(VGroup(v_line, v_line.polarized_mobject)))

    def get_v_lines_indicating_periods(self, freq, n_lines = None):
        if n_lines is None:
            n_lines = self.default_num_v_lines_indicating_periods
        period = np.divide(1., max(freq, 0.01))
        v_lines = VGroup(*[
            DashedLine(ORIGIN, 1.5*UP).move_to(
                self.time_axes.coords_to_point(n*period, 0),
                DOWN
            )
            for n in range(1, n_lines + 1)
        ])
        v_lines.set_stroke(LIGHT_GREY)
        return v_lines

    def get_period_v_lines_update_anim(self):
        def update_v_lines(v_lines):
            freq = self.graph.polarized_mobject.frequency
            Transform(
                v_lines,
                self.get_v_lines_indicating_periods(freq)
            ).update(1)
        return UpdateFromFunc(
            self.v_lines_indicating_periods, update_v_lines
        )

class WrapCosineGraphAroundCircle(FourierMachineScene):
    CONFIG = {
        "initial_winding_frequency" : 0.5,
        "signal_frequency" : 3.0,
    }
    def construct(self):
        self.show_initial_signal()
        self.wrap_around_circle()
        self.show_time_sweeps()
        self.compare_two_frequencies()
        self.change_wrapping_frequency()

    def show_initial_signal(self):
        axes = self.get_time_axes()
        graph = self.get_cosine_wave(freq = self.signal_frequency)
        self.graph = graph
        braces = VGroup(*self.get_peak_braces()[3:6])
        v_lines = VGroup(*[
            DashedLine(
                ORIGIN, 2*UP, color = RED
            ).move_to(axes.coords_to_point(x, 0), DOWN)
            for x in 1, 2
        ])
        words = self.get_bps_label()
        words.save_state()
        words.next_to(axes.coords_to_point(1.5, 0), DOWN, MED_LARGE_BUFF)

        self.add(axes)
        self.play(ShowCreation(graph, run_time = 2, rate_func = None))
        self.play(
            FadeIn(words),
            LaggedStart(FadeIn, braces),
            *map(ShowCreation, v_lines)
        )
        self.wait()
        self.play(
            FadeOut(VGroup(braces, v_lines)),
            words.restore,
        )
        self.wait()

        self.beats_per_second_label = words
        self.graph = graph

    def wrap_around_circle(self):
        graph = self.graph
        freq = self.initial_winding_frequency
        low_freq = freq/3
        polarized_graph = self.get_polarized_mobject(graph, low_freq)
        circle_plane = self.get_circle_plane()
        moving_graph = graph.copy()

        self.play(ShowCreation(circle_plane, submobject_mode = "all_at_once"))
        self.play(ReplacementTransform(
            moving_graph,
            polarized_graph,
            run_time = 3,
            path_arc = -TAU/2
        ))
        self.animate_frequency_change([graph], freq)
        self.wait()
        pg_copy = polarized_graph.copy()
        self.remove(polarized_graph)
        self.play(pg_copy.fade, 0.75)
        self.play(*self.get_vector_animations(graph), run_time = 15)
        self.remove(pg_copy)
        self.wait()

    def show_time_sweeps(self):
        freq = self.initial_winding_frequency
        graph = self.graph

        v_lines = self.get_v_lines_indicating_periods(freq)
        winding_freq_label = self.get_winding_frequency_label()

        self.animate_time_sweep(
            freq = freq,
            t_max = 4,
            run_time = 6,
            added_anims = [FadeIn(v_lines)]
        )
        self.play(
            FadeIn(winding_freq_label),
            *self.get_vector_animations(graph)
        )
        self.wait()

        self.v_lines_indicating_periods = v_lines

    def compare_two_frequencies(self):
        bps_label = self.beats_per_second_label
        wps_label = self.winding_freq_label
        for label in bps_label, wps_label:
            label.rect = SurroundingRectangle(
                label, color = RED
            )
        graph = self.graph
        freq = self.initial_winding_frequency
        braces = self.get_peak_braces(buff = 0)

        self.play(ShowCreation(bps_label.rect))
        self.play(FadeOut(bps_label.rect))
        self.play(LaggedStart(FadeIn, braces, run_time = 3))
        self.play(FadeOut(braces))
        self.play(ShowCreation(wps_label.rect))
        self.play(FadeOut(wps_label.rect))
        self.animate_time_sweep(freq = freq, t_max = 4)
        self.wait()

    def change_wrapping_frequency(self):
        graph = self.graph
        v_lines = self.v_lines_indicating_periods
        freq_label = self.winding_freq_label[0]

        count = 0
        for target_freq in [1.23, 0.2, 1.55, self.signal_frequency]:
            self.play(
                Transform(
                    v_lines, 
                    self.get_v_lines_indicating_periods(target_freq)
                ),
                ChangeDecimalToValue(freq_label, target_freq),
                self.get_frequency_change_animation(graph, target_freq),
                run_time = 4,
            )
            self.wait()
            if count == 2:
                self.play(LaggedStart(
                    ApplyFunction, v_lines,
                    lambda mob : (
                        lambda m : m.shift(0.25*UP).highlight(YELLOW), 
                        mob
                    ),
                    rate_func = there_and_back
                ))
                self.animate_time_sweep(target_freq, t_max = 2)
            count += 1
        self.wait()
        self.play(
            *self.get_vector_animations(graph, False),
            run_time = 15
        )

    ##

    def get_winding_frequency_label(self):
        freq = self.initial_winding_frequency
        winding_freq_label = VGroup(
            DecimalNumber(freq, num_decimal_points = 2),
            TextMobject("cycles/second")
        )
        winding_freq_label.arrange_submobjects(RIGHT)
        winding_freq_label.next_to(
            self.circle_plane, RIGHT, aligned_edge = UP
        )
        self.winding_freq_label = winding_freq_label
        return winding_freq_label

    def get_peak_braces(self, **kwargs):
        peak_points = [
            self.time_axes.input_to_graph_point(x, self.graph)
            for x in np.arange(0, 3.5, 1./self.signal_frequency)
        ]
        return VGroup(*[
            Brace(Line(p1, p2), UP, **kwargs)
            for p1, p2 in zip(peak_points, peak_points[1:])
        ])

    def get_bps_label(self, freq = 3):
        braces = VGroup(*self.get_peak_braces()[freq:2*freq])
        words = TextMobject("%d beats/second"%freq)
        words.scale_to_fit_width(0.9*braces.get_width())
        words.move_to(braces, DOWN)
        return words

class DrawFrequencyPlot(WrapCosineGraphAroundCircle, PiCreatureScene):
    CONFIG = {
        "initial_winding_frequency" : 3.0,
        "center_of_mass_color" : RED,
    }
    def construct(self):
        self.remove(self.pi_creature)
        self.setup_graph()
        self.indicate_weight_of_wire()
        self.show_center_of_mass_dot()
        self.change_to_various_frequencies()
        self.introduce_frequency_plot()
        self.draw_full_frequency_plot()
        self.recap_objects_on_screen()
        self.lower_graph()
        self.label_as_almost_fourier()

    def setup_graph(self):
        self.add(self.get_time_axes())
        self.add(self.get_circle_plane())
        self.graph = self.get_cosine_wave(self.signal_frequency)
        self.add(self.graph)
        self.add(self.get_polarized_mobject(
            self.graph, self.initial_winding_frequency
        ))
        self.add(self.get_winding_frequency_label())
        self.beats_per_second_label = self.get_bps_label()
        self.add(self.beats_per_second_label)        
        self.v_lines_indicating_periods = self.get_v_lines_indicating_periods(
            self.initial_winding_frequency
        )
        self.add(self.v_lines_indicating_periods)
        self.change_frequency(1.03)
        self.wait()

    def indicate_weight_of_wire(self):
        graph = self.graph
        pol_graph = graph.polarized_mobject.copy()
        pol_graph.save_state()
        morty = self.pi_creature
        morty.change("raise_right_hand")
        morty.save_state()
        morty.change("plain")
        morty.fade(1)

        self.play(
            morty.restore,
            pol_graph.scale, 0.5,
            pol_graph.next_to, morty.get_corner(UP+LEFT), UP, -SMALL_BUFF,
        )
        self.play(
            morty.change, "lower_right_hand", pol_graph.get_bottom(),
            pol_graph.shift, 0.45*DOWN,
            rate_func = there_and_back,
            run_time = 2,
        )
        self.wait()

        metal_wire = pol_graph.copy().set_stroke(LIGHT_GREY)
        self.play(
            ShowCreationThenDestruction(metal_wire),
            run_time = 2,
        )
        self.play(
            pol_graph.restore,
            morty.change, "pondering"
        )
        self.remove(pol_graph)

    def show_center_of_mass_dot(self):
        color = self.center_of_mass_color
        dot = self.get_center_of_mass_dot()
        dot.save_state()
        arrow = Vector(DOWN+2*LEFT, color = color)
        arrow.next_to(dot.get_center(), UP+RIGHT, buff = SMALL_BUFF)
        dot.move_to(arrow.get_start())
        words = TextMobject("Center of mass")
        words.next_to(arrow.get_start(), RIGHT)
        words.highlight(color)

        self.play(
            GrowArrow(arrow),
            dot.restore,
        )
        self.play(Write(words))
        self.play(FadeOut(arrow), FadeOut(self.pi_creature))
        self.wait()

        self.generate_center_of_mass_dot_update_anim()
        self.center_of_mass_label = words

    def change_to_various_frequencies(self):
        for new_freq in [0.5, 0.2, 1.04, 2.21, 3.0]:
            self.change_frequency(new_freq)
            self.wait()
        self.play(
            *self.get_vector_animations(self.graph),
            run_time = 15
        )

    def introduce_frequency_plot(self):
        wps_label = self.winding_freq_label
        wps_label.add_to_back(BackgroundRectangle(wps_label))
        com_label = self.center_of_mass_label
        com_label.add_background_rectangle()
        frequency_axes = self.get_frequency_axes()
        x_coord_label = TextMobject("$x$-coordiante for center of mass")
        x_coord_label.highlight(self.center_of_mass_color)
        x_coord_label.scale(self.text_scale_val)
        x_coord_label.next_to(
            frequency_axes.y_axis.get_top(),
            RIGHT, aligned_edge = UP, buff = LARGE_BUFF
        )
        x_coord_label.add_background_rectangle()
        flower_path = ParametricFunction(
            lambda t : self.circle_plane.coords_to_point(
                np.sin(2*t)*np.cos(t),
                np.sin(2*t)*np.sin(t),
            ),
            t_min = 0, t_max = TAU,
        )
        flower_path.move_to(self.center_of_mass_dot)

        self.play(
            wps_label.move_to, self.circle_plane.get_top(),
            com_label.move_to, self.circle_plane, DOWN,
        )
        self.play(LaggedStart(FadeIn, frequency_axes))
        self.wait()
        self.play(MoveAlongPath(
            self.center_of_mass_dot, flower_path,
            run_time = 4,
        ))
        self.play(ReplacementTransform(
            com_label.copy(), x_coord_label
        ))
        self.wait()

        self.x_coord_label = x_coord_label

    def draw_full_frequency_plot(self):
        graph = self.graph
        fourier_graph = self.get_fourier_transform_graph(graph)
        fourier_graph.save_state()
        fourier_graph_update = self.get_fourier_graph_drawing_update_anim(
            fourier_graph
        )
        v_line = DashedLine(
            self.frequency_axes.coords_to_point(0, 0),
            self.frequency_axes.coords_to_point(0, 1),
            stroke_width = 6,
            color = fourier_graph.get_color()
        )

        self.change_frequency(0.0)
        self.generate_fourier_dot_transform(fourier_graph)
        self.wait()
        self.play(ShowCreation(v_line))
        self.play(
            GrowFromCenter(self.fourier_graph_dot),
            FadeOut(v_line)
        )
        f_max = int(self.frequency_axes.x_max)
        for freq in [0.2, 1.5, 3.0, 4.0, 5.0]:
            fourier_graph.restore()
            self.change_frequency(
                freq,
                added_anims = [fourier_graph_update],
                run_time = 8,
            )
            self.wait()
        self.fourier_graph = fourier_graph

    def recap_objects_on_screen(self):
        rect = FullScreenFadeRectangle()
        time_group = VGroup(
            self.graph,
            self.time_axes,
            self.beats_per_second_label,
        ).copy()
        circle_group = VGroup(
            self.graph.polarized_mobject,
            self.circle_plane,
            self.winding_freq_label,
            self.center_of_mass_label,
            self.center_of_mass_dot,
        ).copy()
        frequency_group = VGroup(
            self.fourier_graph,
            self.frequency_axes,
            self.x_coord_label,
        ).copy()
        groups = [time_group, circle_group, frequency_group]

        self.play(FadeIn(rect))
        self.wait()
        for group in groups:
            graph_copy = group[0].copy().highlight(PINK)
            self.play(FadeIn(group))
            self.play(ShowCreation(graph_copy))
            self.play(FadeOut(graph_copy))
            self.wait()
            self.play(FadeOut(group))
        self.wait()
        self.play(FadeOut(rect))

    def lower_graph(self):
        graph = self.graph
        time_axes = self.time_axes
        shift_vect = time_axes.coords_to_point(0, 1)
        shift_vect -= time_axes.coords_to_point(0, 0)
        fourier_graph = self.fourier_graph
        new_graph = self.get_cosine_wave(
            self.signal_frequency, shift_val = 0
        )
        new_fourier_graph = self.get_fourier_transform_graph(new_graph)
        for mob in graph, time_axes, fourier_graph:
            mob.save_state()

        new_freq = 0.03
        self.change_frequency(new_freq)
        self.wait()
        self.play(
            time_axes.shift, shift_vect/2,
            graph.shift, -shift_vect/2,
            self.get_frequency_change_animation(
                self.graph, new_freq
            ),
            self.center_of_mass_dot_anim,
            self.get_period_v_lines_update_anim(),
            Transform(fourier_graph, new_fourier_graph),
            self.fourier_graph_dot.move_to,
                self.frequency_axes.coords_to_point(new_freq, 0),
            run_time = 2
        )
        self.wait()
        self.remove(self.fourier_graph_dot)
        self.generate_fourier_dot_transform(new_fourier_graph)
        self.change_frequency(3.0, run_time = 15, rate_func = None)
        self.wait()
        self.play(
            graph.restore, 
            time_axes.restore,
            self.get_frequency_change_animation(
                self.graph, 3.0
            ),
            self.center_of_mass_dot_anim,
            self.get_period_v_lines_update_anim(),
            fourier_graph.restore,
            Animation(self.fourier_graph_dot),
            run_time = 2
        )
        self.generate_fourier_dot_transform(self.fourier_graph)
        self.wait()
        self.play(FocusOn(self.fourier_graph_dot))
        self.wait()

    def label_as_almost_fourier(self):
        x_coord_label = self.x_coord_label
        almost_fourier_label = TextMobject(
            "``Almost Fourier Transform''",
        )
        almost_fourier_label.move_to(x_coord_label, UP+LEFT)
        x_coord_label.generate_target()
        x_coord_label.target.next_to(almost_fourier_label, DOWN)

        self.play(
            MoveToTarget(x_coord_label),
            Write(almost_fourier_label)
        )
        self.wait(2)

    ##

    def get_center_of_mass_dot(self):
        dot = Dot(
            self.get_pol_graph_center_of_mass(),
            color = self.center_of_mass_color
        )
        self.center_of_mass_dot = dot
        return dot

    def get_pol_graph_center_of_mass(self):
        pg = self.graph.polarized_mobject
        result = center_of_mass([
            pg.point_from_proportion(alpha)
            for alpha in np.linspace(0, 1, 1000)
        ])
        return result

    def generate_fourier_dot_transform(self, fourier_graph):
        self.fourier_graph_dot = Dot(color = WHITE, radius = 0.05)
        def update_dot(dot):
            f = self.graph.polarized_mobject.frequency
            dot.move_to(self.frequency_axes.input_to_graph_point(
                f, fourier_graph
            ))
        self.fourier_graph_dot_anim = UpdateFromFunc(
            self.fourier_graph_dot, update_dot
        )
        self.fourier_graph_dot_anim.update(0)

    def get_fourier_graph_drawing_update_anim(self, fourier_graph):
        fourier_graph_copy = fourier_graph.copy()
        max_freq = self.frequency_axes.x_max
        def update_fourier_graph(fg):
            freq = self.graph.polarized_mobject.frequency
            fg.pointwise_become_partial(
                fourier_graph_copy,
                0, freq/max_freq
            )
            return fg
        self.fourier_graph_drawing_update_anim = UpdateFromFunc(
            fourier_graph, update_fourier_graph
        )
        return self.fourier_graph_drawing_update_anim

    def generate_center_of_mass_dot_update_anim(self):
        self.center_of_mass_dot_anim = UpdateFromFunc(
            self.center_of_mass_dot, 
            lambda d : d.move_to(self.get_pol_graph_center_of_mass())
        )

    def change_frequency(self, new_freq, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", 3)
        added_anims = kwargs.get("added_anims", [])
        freq_label = filter(
            lambda sm : isinstance(sm, DecimalNumber),
            self.winding_freq_label
        )[0]
        anims = [
            ChangeDecimalToValue(freq_label, new_freq),
            self.get_frequency_change_animation(
                self.graph, new_freq
            )
        ]
        if hasattr(self, "v_lines_indicating_periods"):
            anims.append(self.get_period_v_lines_update_anim())
        if hasattr(self, "center_of_mass_dot"):
            anims.append(self.center_of_mass_dot_anim)
        if hasattr(self, "fourier_graph_dot"):
            anims.append(self.fourier_graph_dot_anim)
        if hasattr(self, "fourier_graph_drawing_update_anim"):
            anims.append(self.fourier_graph_drawing_update_anim)
        anims += added_anims
        self.play(*anims, **kwargs)

    def create_pi_creature(self):
        return Mortimer().to_corner(DOWN+RIGHT)

class StudentsHorrifiedAtScene(TeacherStudentsScene):
    def construct(self):
        self.change_student_modes(
            *3*["horrified"],
            look_at_arg = 2*UP + 3*LEFT
        )
        self.wait(4)

class ShowLowerFrequency(DrawFrequencyPlot):
    CONFIG = {
        "signal_frequency" : 2.0,
        "higher_signal_frequency" : 3.0,
        "lower_signal_color" : PINK,
    }
    def construct(self):
        self.setup_all_axes()
        self.show_lower_frequency_signal()
        self.play_with_lower_frequency_signal()

    def setup_all_axes(self):
        self.add(self.get_time_axes())
        self.add(self.get_circle_plane())
        self.add(self.get_frequency_axes())
        self.remove(self.pi_creature)

    def show_lower_frequency_signal(self):
        axes = self.time_axes
        start_graph = self.get_cosine_wave(freq = self.higher_signal_frequency)
        graph = self.get_cosine_wave(
            freq = self.signal_frequency,
        )
        graph.highlight(self.lower_signal_color)
        self.graph = graph
        ratio = float(self.higher_signal_frequency)/self.signal_frequency

        braces = VGroup(*self.get_peak_braces()[2:4])
        v_lines = VGroup(*[
            DashedLine(ORIGIN, 1.5*UP).move_to(
                axes.coords_to_point(x, 0), DOWN
            )
            for x in 1, 2
        ])
        bps_label = self.get_bps_label(2)
        bps_label.save_state()
        bps_label.next_to(braces, UP, SMALL_BUFF)


        # self.add(start_graph)
        self.play(
            start_graph.stretch, ratio, 0, {"about_edge" : LEFT},
            start_graph.highlight, graph.get_color(),
        )
        self.play(FadeOut(start_graph), Animation(graph))
        self.remove(start_graph)
        self.play(
            Write(bps_label),
            LaggedStart(FadeIn, braces),
            *map(ShowCreation, v_lines),
            run_time = 1
        )
        self.wait()
        self.play(
            FadeOut(v_lines),
            FadeOut(braces),
            bps_label.restore,
        )

    def play_with_lower_frequency_signal(self):
        freq = 0.1

        #Wind up graph
        graph = self.graph
        pol_graph = self.get_polarized_mobject(graph, freq)
        v_lines = self.get_v_lines_indicating_periods(freq)
        self.v_lines_indicating_periods = v_lines
        wps_label = self.get_winding_frequency_label()
        ChangeDecimalToValue(wps_label[0], freq).update(1)
        wps_label.add_to_back(BackgroundRectangle(wps_label))
        wps_label.move_to(self.circle_plane, UP)

        self.play(
            ReplacementTransform(
                graph.copy(), pol_graph,
                run_time = 2,
                path_arc = -TAU/4,
            ),
            FadeIn(wps_label),
        )
        self.change_frequency(freq, run_time = 0)
        self.change_frequency(0.7)
        self.wait()

        #Show center of mass
        dot = Dot(
            self.get_pol_graph_center_of_mass(),
            color = self.center_of_mass_color
        )
        dot.save_state()
        self.center_of_mass_dot = dot
        com_words = TextMobject("Center of mass")
        com_words.add_background_rectangle()
        com_words.move_to(self.circle_plane, DOWN)
        arrow = Arrow(
            com_words.get_top(),
            dot.get_center(),
            buff = SMALL_BUFF,
            color = self.center_of_mass_color
        )
        dot.move_to(arrow.get_start())
        self.generate_center_of_mass_dot_update_anim()

        self.play(
            GrowArrow(arrow),
            dot.restore,
            Write(com_words)
        )
        self.wait()
        self.play(*map(FadeOut, [arrow, com_words]))
        self.change_frequency(0.0)
        self.wait()

        #Show fourier graph
        fourier_graph = self.get_fourier_transform_graph(graph)
        fourier_graph_update = self.get_fourier_graph_drawing_update_anim(
            fourier_graph
        )
        x_coord_label = TextMobject(
            "x-coordinate of center of mass"
        )
        x_coord_label.scale(self.text_scale_val)
        x_coord_label.next_to(
            self.frequency_axes.input_to_graph_point(
                self.signal_frequency, fourier_graph
            ), UP
        )
        x_coord_label.highlight(self.center_of_mass_color)
        self.generate_fourier_dot_transform(fourier_graph)

        self.play(Write(x_coord_label))
        self.change_frequency(
            self.signal_frequency,
            run_time = 10,
            rate_func = smooth,
        )
        self.wait()
        self.change_frequency(
            self.frequency_axes.x_max,
            run_time = 15,
            rate_func = smooth,
        )
        self.wait()

        self.set_variables_as_attrs(
            fourier_graph,
            fourier_graph_update,
        )

class MixingUnmixingTODOStub(TODOStub):
    CONFIG = {
        "message" : "Insert mixing and unmixing of signals"
    }

class ShowLinearity(DrawFrequencyPlot):
    CONFIG = {
        "high_freq_color": YELLOW,
        "low_freq_color": PINK,
        "sum_color": GREEN,
        "low_freq" : 2.0,
        "high_freq" : 3.0,
        "circle_plane_config" : {
            "x_radius" : 2.5,
            "y_radius" : 2.7,
            "x_unit_size" : 0.8,
            "y_unit_size" : 0.8,
        },
    }
    def construct(self):
        self.remove(self.pi_creature)
        self.show_sum_of_signals()
        self.show_winding_with_sum_graph()
        self.show_vector_rotation()

    def show_sum_of_signals(self):
        low_freq, high_freq = self.low_freq, self.high_freq
        axes = self.get_time_axes()
        axes_copy = axes.copy()
        low_freq_graph, high_freq_graph = [
            self.get_cosine_wave(
                freq = freq, 
                scale_val = 0.5,
                shift_val = 0.55,
            )
            for freq in low_freq, high_freq
        ]
        sum_graph = self.get_time_graph(
            lambda t : sum([
                low_freq_graph.underlying_function(t),
                high_freq_graph.underlying_function(t),
            ])
        )
        VGroup(axes_copy, high_freq_graph).next_to(
            axes, DOWN, MED_LARGE_BUFF
        )

        low_freq_label = TextMobject("%d Hz"%int(low_freq))
        high_freq_label = TextMobject("%d Hz"%int(high_freq))
        sum_label = TextMobject(
            "%d Hz"%int(low_freq), "+",
            "%d Hz"%int(high_freq)
        )
        trips = [
            (low_freq_label, low_freq_graph, self.low_freq_color), 
            (high_freq_label, high_freq_graph, self.high_freq_color),
            (sum_label, sum_graph, self.sum_color),
        ]
        for label, graph, color in trips:
            label.next_to(graph, UP)
            graph.highlight(color)
            label.highlight(color)
        sum_label[0].match_color(low_freq_graph)
        sum_label[2].match_color(high_freq_graph)

        self.add(axes, low_freq_graph)
        self.play(
            FadeIn(axes_copy),
            ShowCreation(high_freq_graph),
        )
        self.play(LaggedStart(
            FadeIn, VGroup(high_freq_label, low_freq_label)
        ))
        self.wait()
        self.play(
            ReplacementTransform(axes_copy, axes),
            ReplacementTransform(high_freq_graph, sum_graph),
            ReplacementTransform(low_freq_graph, sum_graph),
            ReplacementTransform(
                VGroup(low_freq_label, high_freq_label),
                sum_label
            )
        )
        self.wait()
        self.graph = graph

    def show_winding_with_sum_graph(self):
        graph = self.graph
        circle_plane = self.get_circle_plane()
        frequency_axes = self.get_frequency_axes()
        pol_graph = self.get_polarized_mobject(graph, freq = 0.0)

        wps_label = self.get_winding_frequency_label()
        ChangeDecimalToValue(wps_label[0], 0.0).update(1)
        wps_label.add_to_back(BackgroundRectangle(wps_label))
        wps_label.move_to(circle_plane, UP)

        v_lines = self.get_v_lines_indicating_periods(0.001)
        self.v_lines_indicating_periods = v_lines

        dot = Dot(
            self.get_pol_graph_center_of_mass(),
            color = self.center_of_mass_color
        )
        self.center_of_mass_dot = dot
        self.generate_center_of_mass_dot_update_anim()

        fourier_graph = self.get_fourier_transform_graph(graph)
        fourier_graph_update = self.get_fourier_graph_drawing_update_anim(
            fourier_graph
        )
        x_coord_label = TextMobject(
            "x-coordinate of center of mass"
        )
        x_coord_label.scale(self.text_scale_val)
        x_coord_label.next_to(
            self.frequency_axes.input_to_graph_point(
                self.signal_frequency, fourier_graph
            ), UP
        )
        x_coord_label.highlight(self.center_of_mass_color)
        almost_fourier_label = TextMobject(
            "``Almost-Fourier transform''"
        )

        self.generate_fourier_dot_transform(fourier_graph)                

        self.play(LaggedStart(
            FadeIn, VGroup(
                circle_plane, wps_label,
                frequency_axes, x_coord_label,
            ),
            run_time = 1,
        ))
        self.play(
            ReplacementTransform(graph.copy(), pol_graph),
            GrowFromCenter(dot)
        )
        freqs = [
            self.low_freq, self.high_freq,
            self.frequency_axes.x_max
        ]
        for freq in freqs:
            self.change_frequency(
                freq,
                run_time = 8,
                rate_func = bezier([0, 0, 1, 1]),
            )

    def show_vector_rotation(self):
        self.fourier_graph_drawing_update_anim = Animation(Mobject())
        self.change_frequency(self.low_freq)
        self.play(*self.get_vector_animations(
            self.graph, draw_polarized_graph = False,
            run_time = 20,
        ))
        self.wait()

class ShowCommutativeDiagram(ShowLinearity):
    CONFIG = {
        "time_axes_config" : {
            "x_max" : 1.9,
            "y_max" : 2.0,
            "y_min" : -2.0,
            "y_axis_config" : {
                "unit_size" : 0.5,
            },
            "x_axis_config" : {
                "numbers_to_show" : [1],
            }
        },
        "time_label_t" : 1.5,
        "frequency_axes_config" : {
            "x_min" : 0.0,
            "x_max" : 4.0,
            "y_min" : -0.1,
            "y_max" : 0.5,
            "y_axis_config" : {
                "unit_size" : 1.5,
                "tick_frequency" : 0.5,
            },
        }
    } 
    def construct(self):
        self.show_diagram()
        self.point_out_spikes()

    def show_diagram(self):
        self.remove(self.pi_creature)

        #Setup axes
        time_axes = self.get_time_axes()
        time_axes.scale(0.8)
        ta_group = VGroup(
            time_axes, time_axes.deepcopy(), time_axes.deepcopy(),
        )
        ta_group.arrange_submobjects(DOWN, buff = MED_LARGE_BUFF)
        ta_group.to_corner(UP+LEFT, buff = MED_SMALL_BUFF)

        frequency_axes = Axes(**self.frequency_axes_config)
        frequency_axes.highlight(TEAL)
        freq_label = TextMobject("Frequency")
        freq_label.scale(self.text_scale_val)
        freq_label.next_to(frequency_axes.x_axis, DOWN, SMALL_BUFF, RIGHT)
        frequency_axes.label = freq_label
        frequency_axes.add(freq_label)
        frequency_axes.scale(0.8)
        fa_group = VGroup(
            frequency_axes, frequency_axes.deepcopy(), frequency_axes.deepcopy()
        )
        VGroup(ta_group[1], fa_group[1]).shift(MED_LARGE_BUFF*UP)
        for ta, fa in zip(ta_group, fa_group):
            fa.next_to(
                ta.x_axis.main_line, RIGHT,
                submobject_to_align = fa.x_axis.main_line
            )
            fa.to_edge(RIGHT)
            ta.remove(ta.labels)
            fa.remove(fa.label)

        ## Add graphs
        funcs = [
            lambda t : np.cos(2*TAU*t),
            lambda t : np.cos(3*TAU*t),
        ]
        funcs.append(lambda t : funcs[0](t)+funcs[1](t))
        colors = [
            self.low_freq_color, 
            self.high_freq_color,
            self.sum_color,
        ]
        labels = [
            TextMobject("2 Hz"),
            TextMobject("3 Hz"),
            # TextMobject("2 Hz", "+", "3 Hz"),
            VectorizedPoint()
        ]
        for func, color, label, ta, fa in zip(funcs, colors, labels, ta_group, fa_group):
            time_graph = ta.get_graph(func)
            time_graph.highlight(color)
            label.highlight(color)
            label.scale(0.75)
            label.next_to(time_graph, UP, SMALL_BUFF)
            fourier = get_fourier_transform(
                func, ta.x_min, 4*ta.x_max
            )
            fourier_graph = fa.get_graph(fourier)
            fourier_graph.highlight(self.center_of_mass_color)

            arrow = Arrow(
                ta.x_axis.main_line, fa.x_axis.main_line, 
                color = WHITE,
                buff = MED_LARGE_BUFF,
            )
            words = TextMobject("Almost-Fourier \\\\ transform")
            words.scale(0.6)
            words.next_to(arrow, UP)
            arrow.words = words

            ta.graph = time_graph
            ta.graph_label = label
            ta.arrow = arrow
            ta.add(time_graph, label)
            fa.graph = fourier_graph
            fa.add(fourier_graph)
        # labels[-1][0].match_color(labels[0])
        # labels[-1][2].match_color(labels[1])


        #Add arrows
        sum_arrows = VGroup()
        for group in ta_group, fa_group:
            arrow = Arrow(
                group[1].graph, group[2].graph,
                color = WHITE,
                buff = SMALL_BUFF
            )
            arrow.scale(0.8, about_edge = UP)
            arrow.words = TextMobject("Sum").scale(0.75)
            arrow.words.next_to(arrow, RIGHT, buff = MED_SMALL_BUFF)
            sum_arrows.add(arrow)

        def apply_transform(index):
            ta = ta_group[index].deepcopy()
            fa = fa_group[index]
            anims = [
                ReplacementTransform(
                    getattr(ta, attr), getattr(fa, attr)
                )
                for attr in "x_axis", "y_axis", "graph"
            ]
            anims += [
                GrowArrow(ta.arrow),
                Write(ta.arrow.words),
            ]
            if index == 0:
                anims.append(ReplacementTransform(
                    ta.labels[0],
                    fa.label
                ))
            self.play(*anims, run_time = 1.5)


        #Animations
        self.add(*ta_group[:2])
        self.add(ta_group[0].labels)
        self.wait()
        apply_transform(0)
        apply_transform(1)
        self.wait()
        self.play(
            GrowArrow(sum_arrows[1]),
            Write(sum_arrows[1].words),
            *[
                ReplacementTransform(
                    fa.copy(), fa_group[2]
                )
                for fa in fa_group[:2]
            ]
        )
        self.wait(2)
        self.play(
            GrowArrow(sum_arrows[0]),
            Write(sum_arrows[0].words),
            *[
                ReplacementTransform(
                    mob.copy(), ta_group[2], 
                    run_time = 1
                )
                for mob in ta_group[:2]
            ]
        )
        self.wait()
        apply_transform(2)
        self.wait()

        self.time_axes_group = ta_group
        self.frequency_axes_group = fa_group

    def point_out_spikes(self):
        fa_group = self.frequency_axes_group
        freqs = self.low_freq, self.high_freq
        flat_rects = VGroup()
        for freq, axes in zip(freqs, fa_group[:2]):
            flat_rect = SurroundingRectangle(axes.x_axis)
            flat_rect.stretch(0.5, 1)
            spike_rect = self.get_spike_rect(axes, freq)
            flat_rect.match_style(spike_rect)
            flat_rect.target = spike_rect
            flat_rects.add(flat_rect)

        self.play(LaggedStart(GrowFromCenter, flat_rects))
        self.wait()
        self.play(LaggedStart(MoveToTarget, flat_rects))
        self.wait()

        sum_spike_rects = VGroup(*[
            self.get_spike_rect(fa_group[2], freq)
            for freq in freqs
        ])
        self.play(ReplacementTransform(
            flat_rects, sum_spike_rects
        ))
        self.play(LaggedStart(
            WiggleOutThenIn, sum_spike_rects,
            run_time = 1,
            lag_ratio = 0.7,
        ))
        self.wait()

    ##

    def get_spike_rect(self, axes, freq):
        peak_point = axes.input_to_graph_point(
            freq, axes.graph
        )
        f_axis_point = axes.coords_to_point(freq, 0)
        line = Line(f_axis_point, peak_point)
        spike_rect = SurroundingRectangle(line)
        spike_rect.set_stroke(width = 0)
        spike_rect.set_fill(YELLOW, 0.5)
        return spike_rect

class BeforeGettingToTheFullMath(TeacherStudentsScene):
    def construct(self):
        formula = TexMobject(
            "\\hat{g}(f) = \\int_{-\\infty}^{\\infty}" + \
            "g(t)e^{-2\\pi i f t}dt"
        )
        formula.next_to(self.teacher, UP+LEFT)

        self.play(
            Write(formula),
            self.teacher.change, "raise_right_hand",
            self.get_student_changes(*["confused"]*3)
        )
        self.wait()
        self.play(
            ApplyMethod(
                formula.next_to, SPACE_WIDTH*RIGHT, RIGHT,
                path_arc = TAU/16,
                rate_func = running_start,
            ),
            self.get_student_changes(*["pondering"]*3)
        )
        self.teacher_says("Consider sound editing\\dots")
        self.wait(3)

class FilterOutHighPitch(AddingPureFrequencies, ShowCommutativeDiagram):
    def construct(self):
        self.add_speaker()
        self.play_sound()
        self.show_intensity_vs_time_graph()
        self.take_fourier_transform()
        self.filter_out_high_pitch()
        self.mention_inverse_transform()

    def play_sound(self):
        randy = self.pi_creature

        self.play(
            Succession(
                ApplyMethod, randy.look_at, self.speaker,
                Animation, randy,
                ApplyMethod, randy.change, "telepath", randy,
                Animation, randy, 
                Blink, randy,
                Animation, randy, {"run_time" : 2},
            ),
            *self.get_broadcast_anims(),
            run_time = 7
        )
        self.play(randy.change, "angry", self.speaker)
        self.wait()

    def show_intensity_vs_time_graph(self):
        randy = self.pi_creature

        axes = Axes(
            x_min = 0,
            x_max = 12,
            y_min = -6,
            y_max = 6,
            y_axis_config = {
                "unit_size" : 0.15,
                "tick_frequency" : 3,
            }
        )
        axes.set_stroke(width = 2)
        axes.to_corner(UP+LEFT)
        time_label = TextMobject("Time")
        intensity_label = TextMobject("Intensity")
        labels = VGroup(time_label, intensity_label)
        labels.scale(0.75)
        time_label.next_to(
            axes.x_axis, DOWN, 
            aligned_edge = RIGHT,
            buff = SMALL_BUFF
        )
        intensity_label.next_to(
            axes.y_axis, RIGHT, 
            aligned_edge = UP,
            buff = SMALL_BUFF
        )
        axes.labels = labels

        func = lambda t : sum([
            np.cos(TAU*f*t)
            for f in 0.5, 0.7, 1.0, 1.2, 3.0,
        ])
        graph = axes.get_graph(func)
        graph.highlight(BLUE)

        self.play(
            FadeIn(axes), 
            FadeIn(axes.labels), 
            randy.change, "pondering", axes,
            ShowCreation(
                graph, run_time = 4, 
                rate_func = bezier([0, 0, 1, 1])
            ),
            *self.get_broadcast_anims(run_time = 6)
        )
        self.wait()

        self.time_axes = axes
        self.time_graph = graph

    def take_fourier_transform(self):
        time_axes = self.time_axes
        time_graph = self.time_graph
        randy = self.pi_creature
        speaker = self.speaker

        frequency_axes = Axes(
            x_min = 0,
            x_max = 3.5,
            x_axis_config = {"unit_size" : 3.5},
            y_min = 0,
            y_max = 1,
            y_axis_config = {"unit_size" : 2},
        )
        frequency_axes.highlight(TEAL)
        frequency_axes.next_to(time_axes, DOWN, LARGE_BUFF, LEFT)
        freq_label = TextMobject("Frequency")
        freq_label.scale(0.75)
        freq_label.next_to(frequency_axes.x_axis, DOWN, MED_SMALL_BUFF, RIGHT)
        frequency_axes.label = freq_label

        fourier_func = get_fourier_transform(
            time_graph.underlying_function, 
            t_min = 0, t_max = 30,
        )
        # def alt_fourier_func(t):
        #     bell = smooth(t)*0.3*np.exp(-0.8*(t-0.9)**2)
        #     return bell + (smooth(t/3)+0.2)*fourier_func(t)
        fourier_graph = frequency_axes.get_graph(
            fourier_func, num_graph_points = 150,
        )
        fourier_graph.highlight(RED)
        frequency_axes.graph = fourier_graph

        arrow = Arrow(time_graph, fourier_graph, color = WHITE)
        ft_words = TextMobject("Fourier \\\\ transform")
        ft_words.next_to(arrow, RIGHT)

        spike_rect = self.get_spike_rect(frequency_axes, 3)
        spike_rect.stretch(2, 0)

        self.play(
            ReplacementTransform(time_axes.copy(), frequency_axes),
            ReplacementTransform(time_graph.copy(), fourier_graph),
            ReplacementTransform(time_axes.labels[0].copy(), freq_label),
            GrowArrow(arrow),
            Write(ft_words),
            VGroup(randy, speaker).shift, SPACE_HEIGHT*DOWN,
        )
        self.remove(randy, speaker)
        self.wait()
        self.play(DrawBorderThenFill(spike_rect))
        self.wait()

        self.frequency_axes = frequency_axes
        self.fourier_graph = fourier_graph
        self.spike_rect = spike_rect
        self.to_fourier_arrow = arrow

    def filter_out_high_pitch(self): 
        fourier_graph = self.fourier_graph
        spike_rect = self.spike_rect
        frequency_axes = self.frequency_axes

        def filtered_func(f):
            result = fourier_graph.underlying_function(f)
            result *= np.clip(smooth(3-f), 0, 1)
            return result

        new_graph = frequency_axes.get_graph(
            filtered_func, num_graph_points = 300
        )
        new_graph.highlight(RED)

        self.play(spike_rect.stretch, 4, 0)
        self.play(
            Transform(fourier_graph, new_graph),
            spike_rect.stretch, 0.01, 1, {
                "about_point" : frequency_axes.coords_to_point(0, 0)
            },
            run_time = 2
        )
        self.wait()

    def mention_inverse_transform(self):
        time_axes = self.time_axes
        time_graph = self.time_graph
        fourier_graph = self.fourier_graph
        frequency_axes = self.frequency_axes
        f_min = frequency_axes.x_min
        f_max = frequency_axes.x_max

        filtered_graph = time_axes.get_graph(
            lambda t : time_graph.underlying_function(t)-np.cos(TAU*3*t)
        )
        filtered_graph.highlight(BLUE_C)

        to_fourier_arrow = self.to_fourier_arrow
        arrow = to_fourier_arrow.copy()
        arrow.rotate(TAU/2, about_edge = LEFT)
        arrow.shift(MED_SMALL_BUFF*LEFT)
        inv_fourier_words = TextMobject("Inverse Fourier \\\\ transform")
        inv_fourier_words.next_to(arrow, LEFT)
        VGroup(arrow, inv_fourier_words).highlight(MAROON_B)

        self.play(
            GrowArrow(arrow),
            Write(inv_fourier_words)
        )
        self.wait()
        self.play(
            time_graph.fade, 0.9,
            ReplacementTransform(
                fourier_graph.copy(), filtered_graph
            )
        )
        self.wait()

    ##

    def get_broadcast_anims(self, run_time = 7, **kwargs):
        return [
            self.get_broadcast_animation(
                n_circles = n,
                run_time = run_time,
                big_radius = 7,
                start_stroke_width = 5,
                **kwargs
            )
            for n in 5, 7, 10, 12
        ]

class AskAboutInverseFourier(TeacherStudentsScene):
    def construct(self):
        self.student_says("Inverse Fourier?")
        self.change_student_modes("confused", "raise_right_hand", "confused")
        self.wait(2)

class ApplyFourierToFourier(DrawFrequencyPlot):
    CONFIG = {
        "time_axes_config" : {
            "y_min" : -1.5,
            "y_max" : 1.5,
            "x_max" : 5,
            "x_axis_config" : {
                "numbers_to_show" : range(1, 5),
                "unit_size" : 2.5,
            },
        },
        "frequency_axes_config" : {
            "y_min" : -0.6,
            "y_max" : 0.6,
        },
        "circle_plane_config" : {
            "x_radius" : 1.5,
            "y_radius" : 1.35,
            "x_unit_size" : 1.5,
            "y_unit_size" : 1.5,
        },
        "default_num_v_lines_indicating_periods" : 0,
        "signal_frequency" : 2,
    }
    def construct(self):
        self.setup_fourier_display()
        self.swap_graphs()

    def setup_fourier_display(self):
        self.force_skipping()
        self.setup_graph()
        self.show_center_of_mass_dot()
        self.introduce_frequency_plot()
        self.draw_full_frequency_plot()
        self.time_axes.remove(self.time_axes.labels)
        self.remove(self.beats_per_second_label)
        VGroup(
            self.time_axes, self.graph,
            self.frequency_axes, self.fourier_graph,
            self.x_coord_label,
            self.fourier_graph_dot,
        ).to_edge(UP, buff = MED_SMALL_BUFF)
        self.revert_to_original_skipping_status()

    def swap_graphs(self):
        fourier_graph = self.fourier_graph
        time_graph = self.graph
        wound_up_graph = time_graph.polarized_mobject
        time_axes = self.time_axes
        frequency_axes = self.frequency_axes

        f_max = self.frequency_axes.x_max
        new_fourier_graph = time_axes.get_graph(
            lambda t : 2*fourier_graph.underlying_function(t)
        )
        new_fourier_graph.match_style(fourier_graph)

        self.remove(fourier_graph)
        self.play(
            ReplacementTransform(
                fourier_graph.copy(), 
                new_fourier_graph
            ),
            ApplyMethod(
                time_graph.shift, 3*UP+10*LEFT,
                remover = True,
            ),
        )
        self.play(
            wound_up_graph.next_to, SPACE_WIDTH*LEFT, LEFT,
            remover = True
        )
        self.wait()

        self.graph = new_fourier_graph
        wound_up_graph = self.get_polarized_mobject(new_fourier_graph, freq = 0)
        double_fourier_graph = frequency_axes.get_graph(
            lambda t : 0.25*np.cos(TAU*2*t)
        ).highlight(PINK)
        self.fourier_graph = double_fourier_graph
        self.remove(self.fourier_graph_dot)
        self.get_fourier_graph_drawing_update_anim(double_fourier_graph)
        self.generate_fourier_dot_transform(double_fourier_graph)
        self.center_of_mass_dot.highlight(PINK)
        self.generate_center_of_mass_dot_update_anim()
        def new_get_pol_graph_center_of_mass():
            result = DrawFrequencyPlot.get_pol_graph_center_of_mass(self)
            result -= self.circle_plane.coords_to_point(0, 0)
            result *= 25
            result += self.circle_plane.coords_to_point(0, 0)
            return result
        self.get_pol_graph_center_of_mass = new_get_pol_graph_center_of_mass

        self.play(
            ReplacementTransform(self.graph.copy(), wound_up_graph),
            ChangeDecimalToValue(
                self.winding_freq_label[1], 0.0,
                run_time = 0.2,
            )
        )
        self.change_frequency(5.0, run_time = 15, rate_func = None)
        self.wait()

    ##

    def get_cosine_wave(self, freq, **kwargs):
        kwargs["shift_val"] = 0
        kwargs["scale_val"] = 1.0
        return DrawFrequencyPlot.get_cosine_wave(self, freq, **kwargs)

class WhiteComplexExponentialExpression(DrawFrequencyPlot):
    CONFIG = {
        "signal_frequency" : 2.0,
        "default_num_v_lines_indicating_periods" : 0,
    }
    def construct(self):
        self.remove(self.pi_creature)
        self.setup_plane()
        self.setup_graph()
        self.show_winding_with_both_coordinates()
        self.show_plane_as_complex_plane()
        self.show_eulers_formula()
        self.reference_other_video()
        self.show_winding_graph_expression()

    def setup_plane(self):
        circle_plane = ComplexPlane(
            unit_size = 2,
            y_radius = SPACE_HEIGHT+LARGE_BUFF
        )
        circle_plane.shift(DOWN)
        circle = DashedLine(ORIGIN, TAU*UP)
        circle.apply_complex_function(
            lambda z : R3_to_complex(
                circle_plane.number_to_point(np.exp(z))
            )
        )
        circle_plane.add(circle)

        time_axes = self.get_time_axes()
        time_axes.add_to_back(BackgroundRectangle(
            time_axes, 
            fill_opacity = 0.9,
            buff = MED_SMALL_BUFF,
        ))
        time_axes.scale(0.7)
        time_axes.to_corner(UP+LEFT, buff = 0)
        time_axes.set_stroke(color = WHITE, width = 1)

        self.add(circle_plane)
        self.add(time_axes)

        self.circle_plane = circle_plane
        self.time_axes = time_axes

    def setup_graph(self):
        plane = self.circle_plane
        graph = self.graph = self.get_cosine_wave(
            freq = self.signal_frequency,
            scale_val = 0.5,
            shift_val = 0.75,
        )
        freq = 0.1
        pol_graph = self.get_polarized_mobject(graph, freq = freq)
        wps_label = self.get_winding_frequency_label()
        ChangeDecimalToValue(wps_label[0], freq).update(1)
        wps_label.add_to_back(BackgroundRectangle(wps_label))
        wps_label.next_to(plane.coords_to_point(0, 1), DOWN)
        wps_label.to_edge(LEFT)
        self.get_center_of_mass_dot()
        self.generate_center_of_mass_dot_update_anim()

        self.add(graph, pol_graph, wps_label)
        self.set_variables_as_attrs(pol_graph, wps_label)
        self.time_axes_group = VGroup(self.time_axes, graph)

    def show_winding_with_both_coordinates(self):
        com_dot = self.center_of_mass_dot
        plane = self.circle_plane
        v_line = Line(ORIGIN, UP)
        h_line = Line(ORIGIN, RIGHT)
        lines = VGroup(v_line, h_line)
        lines.highlight(PINK)
        def lines_update(lines):
            point = com_dot.get_center()
            x, y = plane.point_to_coords(point)
            h_line.put_start_and_end_on(
                plane.coords_to_point(0, y), point
            )
            v_line.put_start_and_end_on(
                plane.coords_to_point(x, 0), point
            )
        lines_update_anim = UpdateFromFunc(lines, lines_update)
        lines_update_anim.update(0)
        self.add(lines)

        self.change_frequency(
            2.04, 
            added_anims = [
                lines_update_anim,
                self.center_of_mass_dot_anim,
            ],
            run_time = 15,
            rate_func = bezier([0, 0, 1, 1])
        )
        self.wait()

        self.dot_component_anim = lines_update_anim

    def show_plane_as_complex_plane(self):
        to_fade = VGroup(
            self.time_axes_group, self.pol_graph, self.wps_label
        )
        plane = self.circle_plane
        complex_plane_title = TextMobject("Complex plane")
        complex_plane_title.add_background_rectangle()
        complex_plane_title.to_edge(UP)
        coordinate_labels = plane.get_coordinate_labels()

        self.play(FadeOut(to_fade))
        self.play(Write(complex_plane_title))
        self.play(Write(coordinate_labels))
        self.wait()


    def show_eulers_formula(self):
        pass

    def reference_other_video(self):
        pass

    def show_winding_graph_expression(self):
        pass










class CloseWithAPuzzle(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Close with a puzzle!", run_time = 1)
        self.change_student_modes(*["hooray"]*3)
        self.wait(3)

class PuzzleDescription(Scene):
    def construct(self):
        lines = VGroup(
            TextMobject("Convex set", "$C$", "in $\\mathds{R}^3$"),
            TextMobject("Boundary", "$B$", "$=$", "$\\partial C$"),
            TextMobject("$D$", "$=\\{p+q | p, q \\in B\\}$"),
            TextMobject("Prove that", "$D$", "is convex")
        )
        for line in lines:
            line.highlight_by_tex_to_color_map({
                "$C$" : BLUE_D,
                "\\partial C" : BLUE_D,
                "$B$" : BLUE_C,
                "$D$" : YELLOW,
            })
        VGroup(lines[2][1][2], lines[2][1][6]).highlight(RED)
        VGroup(lines[2][1][4], lines[2][1][8]).highlight(MAROON_B)
        lines[2][1][10].highlight(BLUE_C)
        lines.scale(1.25)
        lines.arrange_submobjects(DOWN, buff = LARGE_BUFF, aligned_edge = LEFT)

        lines.to_corner(UP+RIGHT)

        for line in lines:
            self.play(Write(line))
            self.wait(2)

class SponsorScreenGrab(PiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        screen = ScreenRectangle(height = 5)
        screen.to_corner(UP+LEFT)
        screen.shift(MED_LARGE_BUFF*DOWN)
        url = TextMobject("janestreet.com/3b1b")
        url.next_to(screen, UP)

        self.play(
            morty.change, "raise_right_hand",
            ShowCreation(screen)
        )
        self.play(Write(url))
        self.wait(2)
        for mode in "happy", "thinking", "pondering", "thinking":
            self.play(morty.change, mode, screen)
            self.wait(4)
























