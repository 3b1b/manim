# -*- coding: utf-8 -*-
from constants import *
import scipy.integrate

from manimlib.imports import *

USE_ALMOST_FOURIER_BY_DEFAULT = True
NUM_SAMPLES_FOR_FFT = 1000
DEFAULT_COMPLEX_TO_REAL_FUNC = lambda z : z.real


def get_fourier_graph(
    axes, time_func, t_min, t_max,
    n_samples = NUM_SAMPLES_FOR_FFT,
    complex_to_real_func = lambda z : z.real,
    color = RED,
    ):
    # N = n_samples
    # T = time_range/n_samples
    time_range = float(t_max - t_min)
    time_step_size = time_range/n_samples
    time_samples = np.vectorize(time_func)(np.linspace(t_min, t_max, n_samples))
    fft_output = np.fft.fft(time_samples)
    frequencies = np.linspace(0.0, n_samples/(2.0*time_range), n_samples//2)
    #  #Cycles per second of fouier_samples[1]
    # (1/time_range)*n_samples
    # freq_step_size = 1./time_range
    graph = VMobject()
    graph.set_points_smoothly([
        axes.coords_to_point(
            x, complex_to_real_func(y)/n_samples,
        )
        for x, y in zip(frequencies, fft_output[:n_samples//2])
    ])
    graph.set_color(color)
    f_min, f_max = [
        axes.x_axis.point_to_number(graph.points[i])
        for i in (0, -1)
    ]
    graph.underlying_function = lambda f : axes.y_axis.point_to_number(
        graph.point_from_proportion((f - f_min)/(f_max - f_min))
    )
    return graph

def get_fourier_transform(
    func, t_min, t_max, 
    complex_to_real_func = DEFAULT_COMPLEX_TO_REAL_FUNC,
    use_almost_fourier = USE_ALMOST_FOURIER_BY_DEFAULT,
    **kwargs ##Just eats these
    ):
    scalar = 1./(t_max - t_min) if use_almost_fourier else 1.0
    def fourier_transform(f):
        z = scalar*scipy.integrate.quad(
            lambda t : func(t)*np.exp(complex(0, -TAU*f*t)),
            t_min, t_max
        )[0]
        return complex_to_real_func(z)
    return fourier_transform

##

class Introduction(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Fourier Transform")
        title.scale(1.2)
        title.to_edge(UP, buff = MED_SMALL_BUFF)

        func = lambda t : np.cos(2*TAU*t) + np.cos(3*TAU*t)
        graph = FunctionGraph(func, x_min = 0, x_max = 5)
        graph.stretch(0.25, 1)
        graph.next_to(title, DOWN)
        graph.to_edge(LEFT)
        graph.set_color(BLUE)
        fourier_graph = FunctionGraph(
            get_fourier_transform(func, 0, 5),
            x_min = 0, x_max = 5
        )
        fourier_graph.move_to(graph)
        fourier_graph.to_edge(RIGHT)
        fourier_graph.set_color(RED)
        arrow = Arrow(graph, fourier_graph, color = WHITE)
        self.add(title, graph)

        self.student_thinks(
            "What's that?",
            look_at_arg = title,
            target_mode = "confused",
            student_index = 1,
        )
        self.play(
            GrowArrow(arrow),
            ReplacementTransform(graph.copy(), fourier_graph)
        )
        self.wait(2)
        self.student_thinks(
            "Pssht, I got this",
            target_mode = "tease",
            student_index = 2,
            added_anims = [RemovePiCreatureBubble(self.students[1])]
        )
        self.play(self.teacher.change, "hesitant")
        self.wait(2)

class TODOInsertUnmixingSound(TODOStub):
    CONFIG = {
        "message" : "Show unmixing sound"
    }

class OtherContexts(PiCreatureScene):
    def construct(self):
        items = VGroup(*list(map(TextMobject, [
            "Extracting frequencies from sound",
            "Uncertainty principle",
            "Riemann Zeta function and primes",
            "Differential equations",
        ])))
        items.arrange(
            DOWN, buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        items.to_corner(UP+LEFT)
        items[1:].set_fill(opacity = 0.2)

        morty = self.pi_creature
        morty.to_corner(UP+RIGHT)

        self.add(items)
        for item in items[1:]:
            self.play(
                LaggedStartMap(
                    ApplyMethod, item,
                    lambda m : (m.set_fill, {"opacity" : 1}),
                ), 
                morty.change, "thinking",
            )
            self.wait()

class TODOInsertCosineWrappingAroundCircle(TODOStub):
    CONFIG = {
        "message" : "Give a picture-in-picture \\\\ of cosine wrapping around circle",
    }

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
        A_label.set_color(self.A_color)
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
            axis_config = {"include_tip" : False},
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
        graph.set_color(self.A_color)
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
            ShowCreation(graph, run_time = 4, rate_func=linear),
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
        D_label.set_color(self.D_color)
        D_label.move_to(self.A_label)

        self.play(
            FadeOut(self.A_label),
            GrowFromCenter(D_label),
        )
        self.broadcast(
            ShowCreation(graph, run_time = 4, rate_func=linear),
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
                ShowCreation(graph, run_time = 4, rate_func=linear)
                for graph in (self.A_graph, self.D_graph)
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
            list(map(MoveToTarget, movers)),
            [
                ApplyMethod(mob.shift, FRAME_Y_RADIUS*DOWN, remover = True)
                for mob in  (randy, speaker)
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
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS).move_to(x_point)

        self.revert_to_original_skipping_status()
        self.play(GrowFromCenter(v_line))
        self.play(FadeOut(v_line))
        self.play(*list(map(ShowCreation, lines)))
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
        sum_graph.set_color(self.sum_color)
        thin_sum_graph = sum_graph.copy().fade()

        A_graph = self.A_graph
        D_graph = self.D_graph
        D_axes = self.D_axes

        rect = Rectangle(
            height = 2.5*FRAME_Y_RADIUS,
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
            rate_func=linear
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
        F_graph.set_color(self.F_color)
        C_graph = self.get_wave_graph(self.A_frequency*6.0/5, C_axes)
        C_graph.set_color(self.C_color)

        F_label = TextMobject("F349")
        C_label = TextMobject("C523")
        for label, graph in (F_label, F_graph), (C_label, C_graph):
            label.scale(0.5)
            label.set_color(graph.get_stroke_color())
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
        new_sum_graph.set_color(BLUE_C)
        thin_new_sum_graph = new_sum_graph.copy().fade()

        self.play(*it.chain(
            list(map(ShowCreation, [F_axes, C_axes, F_graph, C_graph])),
            list(map(Write, [F_label, C_label])),
            list(map(FadeOut, [self.sum_graph]))
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
        A_line.set_color(self.A_color)
        D_line.set_color(self.D_color)
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
        axes.stretch_to_fit_width(FRAME_WIDTH - 2)
        axes.stretch_to_fit_height(3)
        axes.center()
        axes.to_edge(LEFT)
        graph = axes.get_graph(func, num_graph_points = 200)
        graph.set_color(YELLOW)

        v_line = Line(ORIGIN, 4*UP)
        v_line.move_to(axes.coords_to_point(0, 0), DOWN)
        dot = Dot(color = PINK)
        dot.move_to(graph.point_from_proportion(0))

        self.add(axes, graph)
        self.play(
            v_line.move_to, axes.coords_to_point(5, 0), DOWN,
            MoveAlongPath(dot, graph),
            run_time = 8,
            rate_func=linear,
        )
        self.play(*list(map(FadeOut, [dot, v_line])))

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
        pure_graphs.set_color_by_gradient(BLUE, RED)
        pure_graphs.arrange(DOWN, buff = MED_LARGE_BUFF)
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
            LaggedStartMap(
                ApplyFunction, pure_graphs,
                lambda g : (lambda m : m.shift(SMALL_BUFF*UP).set_color(YELLOW), g),
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
            Quadrant().rotate(angle, about_point = ORIGIN).set_color(color)
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
            norms = np.apply_along_axis(get_norm, 1, points)

            points[:,0] -= dt*points[:,1]/np.clip(norms, 0.1, np.inf)
            points[:,1] += dt*points[:,0]/np.clip(norms, 0.1, np.inf)

            new_norms = np.apply_along_axis(get_norm, 1, points)
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
                ApplyMethod(mud_circle.restore, rate_func=linear)
            ],
            run_time = run_time
        )

#Incomplete, and probably not useful
class MachineThatTreatsOneFrequencyDifferently(Scene):
    def construct(self):
        graph = self.get_cosine_graph(0.5)
        frequency_mob = DecimalNumber(220, num_decimal_places = 0)
        frequency_mob.next_to(graph, UP, buff = MED_LARGE_BUFF)

        self.graph = graph
        self.frequency_mob = frequency_mob
        self.add(graph, frequency_mob)

        arrow1, q_marks, arrow2 = group = VGroup(
            Vector(DOWN), TextMobject("???").scale(1.5), Vector(DOWN)
        )
        group.set_color(WHITE)
        group.arrange(DOWN)
        group.next_to(graph, DOWN)
        self.add(group)

        self.change_graph_frequency(1)
        graph.set_color(GREEN)
        self.wait()
        graph.set_color(YELLOW)
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
            "axis_config" : {
                "color" : TEAL,
            },
            "x_min" : 0,
            "x_max" : 5.0,
            "x_axis_config" : {
                "unit_size" : 1.4,
                "numbers_to_show" : list(range(1, 6)),
            },
            "y_min" : -1.0,
            "y_max" : 1.0,
            "y_axis_config" : {
                "unit_size" : 1.8,
                "tick_frequency" : 0.5,
                "label_direction" : LEFT,
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
        frequency_axes.x_axis.add_numbers()
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
        t_axis = self.time_axes.x_axis
        t_min = t_axis.point_to_number(time_graph.points[0])
        t_max = t_axis.point_to_number(time_graph.points[-1])
        f_max = self.frequency_axes.x_max
        # result = get_fourier_graph(
        #     self.frequency_axes, func, t_min, t_max,
        #     **kwargs
        # )
        # too_far_right_point_indices = [
        #     i
        #     for i, point in enumerate(result.points)
        #     if self.frequency_axes.x_axis.point_to_number(point) > f_max
        # ]
        # if too_far_right_point_indices:
        #     i = min(too_far_right_point_indices)
        #     prop = float(i)/len(result.points)
        #     result.pointwise_become_partial(result, 0, prop)
        # return result
        return self.frequency_axes.get_graph(
            get_fourier_transform(func, t_min, t_max, **kwargs),
            color = self.center_of_mass_color,
            **kwargs
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
        x_min = x_axis.point_to_number(graph.points[0])
        x_max = x_axis.point_to_number(graph.points[-1])
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
            # Not sure why this is needed, but without smoothing 
            # out the alpha like this, the vector would occasionally
            # jump around
            point = center_of_mass([
                graph_copy.point_from_proportion(alpha+d)
                for d in np.linspace(-0.001, 0.001, 5)
            ])
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
        v_line.set_color(RED)

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
        self.show_finite_interval()
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
            for x in (1, 2)
        ])
        words = self.get_bps_label()
        words.save_state()
        words.next_to(axes.coords_to_point(1.5, 0), DOWN, MED_LARGE_BUFF)

        self.add(axes)
        self.play(ShowCreation(graph, run_time = 2, rate_func=linear))
        self.play(
            FadeIn(words),
            LaggedStartMap(FadeIn, braces),
            *list(map(ShowCreation, v_lines))
        )
        self.wait()
        self.play(
            FadeOut(VGroup(braces, v_lines)),
            words.restore,
        )
        self.wait()

        self.beats_per_second_label = words
        self.graph = graph

    def show_finite_interval(self):
        axes = self.time_axes
        v_line = DashedLine(
            axes.coords_to_point(0, 0),
            axes.coords_to_point(0, axes.y_max),
            color = RED,
            stroke_width = 6,
        )
        h_line = Line(
            axes.coords_to_point(0, 0),
            axes.coords_to_point(axes.x_max, 0),
        )
        rect = Rectangle(
            stroke_width = 0,
            fill_color = TEAL,
            fill_opacity = 0.5,
        )
        rect.match_height(v_line)
        rect.match_width(h_line, stretch = True)
        rect.move_to(v_line, DOWN+LEFT)
        right_v_line = v_line.copy()
        right_v_line.move_to(rect, RIGHT)

        rect.save_state()
        rect.stretch(0, 0, about_edge = ORIGIN)
        self.play(rect.restore, run_time = 2)
        self.play(FadeOut(rect))
        for line in v_line, right_v_line:
            self.play(ShowCreation(line))
            self.play(FadeOut(line))
        self.wait()

    def wrap_around_circle(self):
        graph = self.graph
        freq = self.initial_winding_frequency
        low_freq = freq/3
        polarized_graph = self.get_polarized_mobject(graph, low_freq)
        circle_plane = self.get_circle_plane()
        moving_graph = graph.copy()

        self.play(ShowCreation(circle_plane, lag_ratio = 0))
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
        self.play(LaggedStartMap(FadeIn, braces, run_time = 3))
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
        for target_freq in [1.23, 0.2, 0.79, 1.55, self.signal_frequency]:
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
                self.play(LaggedStartMap(
                    ApplyFunction, v_lines,
                    lambda mob : (
                        lambda m : m.shift(0.25*UP).set_color(YELLOW), 
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
            DecimalNumber(freq, num_decimal_places=2),
            TextMobject("cycles/second")
        )
        winding_freq_label.arrange(RIGHT)
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
        words.set_width(0.9*braces.get_width())
        words.move_to(braces, DOWN)
        return words

class DrawFrequencyPlot(WrapCosineGraphAroundCircle, PiCreatureScene):
    CONFIG = {
        "initial_winding_frequency" : 3.0,
        "center_of_mass_color" : RED,
        "center_of_mass_multiple" : 1,
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
        words.set_color(color)

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
        self.change_frequency(
            3.0, run_time = 30,
            rate_func = bezier([0, 0, 1, 1])
        )
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
        x_coord_label = TextMobject("$x$-coordinate for center of mass")
        x_coord_label.set_color(self.center_of_mass_color)
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
        self.play(LaggedStartMap(FadeIn, frequency_axes))
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
            graph_copy = group[0].copy().set_color(PINK)
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
        self.change_frequency(3.0, run_time = 15, rate_func=linear)
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
        result = center_of_mass(pg.get_anchors())
        if self.center_of_mass_multiple != 1:
            mult = self.center_of_mass_multiple
            origin = self.circle_plane.coords_to_point(0, 0)
            result = mult*(result - origin) + origin
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

    def generate_center_of_mass_dot_update_anim(self, multiplier = 1):
        origin = self.circle_plane.coords_to_point(0, 0)
        com = self.get_pol_graph_center_of_mass
        self.center_of_mass_dot_anim = UpdateFromFunc(
            self.center_of_mass_dot, 
            lambda d : d.move_to(
                multiplier*(com()-origin)+origin
            )
        )

    def change_frequency(self, new_freq, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", 3)
        rate_func = kwargs.pop("rate_func", None)
        if rate_func is None:
            rate_func = bezier([0, 0, 1, 1])
        added_anims = kwargs.get("added_anims", [])
        anims = [self.get_frequency_change_animation(self.graph, new_freq)]
        if hasattr(self, "winding_freq_label"):
            freq_label = [
                sm for sm in self.winding_freq_label
                if isinstance(sm, DecimalNumber)
            ][0]
            self.add(freq_label)
            anims.append(
                ChangeDecimalToValue(freq_label, new_freq)
            )
        if hasattr(self, "v_lines_indicating_periods"):
            anims.append(self.get_period_v_lines_update_anim())
        if hasattr(self, "center_of_mass_dot"):
            anims.append(self.center_of_mass_dot_anim)
        if hasattr(self, "fourier_graph_dot"):
            anims.append(self.fourier_graph_dot_anim)
        if hasattr(self, "fourier_graph_drawing_update_anim"):
            anims.append(self.fourier_graph_drawing_update_anim)
        for anim in anims:
            anim.rate_func = rate_func
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

class AskAboutAlmostFouierName(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "``Almost'' Fourier transform?",
            target_mode = "sassy"
        )
        self.change_student_modes("confused", "sassy", "confused")
        self.wait()
        self.teacher_says(
            "We'll get to the real \\\\ one in a few minutes",
            added_anims = [self.get_student_changes(*["plain"]*3)]
        )
        self.wait(2)

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
        graph.set_color(self.lower_signal_color)
        self.graph = graph
        ratio = float(self.higher_signal_frequency)/self.signal_frequency

        braces = VGroup(*self.get_peak_braces()[2:4])
        v_lines = VGroup(*[
            DashedLine(ORIGIN, 1.5*UP).move_to(
                axes.coords_to_point(x, 0), DOWN
            )
            for x in (1, 2)
        ])
        bps_label = self.get_bps_label(2)
        bps_label.save_state()
        bps_label.next_to(braces, UP, SMALL_BUFF)


        # self.add(start_graph)
        self.play(
            start_graph.stretch, ratio, 0, {"about_edge" : LEFT},
            start_graph.set_color, graph.get_color(),
        )
        self.play(FadeOut(start_graph), Animation(graph))
        self.remove(start_graph)
        self.play(
            Write(bps_label),
            LaggedStartMap(FadeIn, braces),
            *list(map(ShowCreation, v_lines)),
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
        self.play(*list(map(FadeOut, [arrow, com_words])))
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
        x_coord_label.set_color(self.center_of_mass_color)
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
        "low_freq" : 3.0,
        "high_freq" : 4.0,
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
            for freq in (low_freq, high_freq)
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
            graph.set_color(color)
            label.set_color(color)
        sum_label[0].match_color(low_freq_graph)
        sum_label[2].match_color(high_freq_graph)

        self.add(axes, low_freq_graph)
        self.play(
            FadeIn(axes_copy),
            ShowCreation(high_freq_graph),
        )
        self.play(LaggedStartMap(
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
        x_coord_label.set_color(self.center_of_mass_color)
        almost_fourier_label = TextMobject(
            "``Almost-Fourier transform''"
        )

        self.generate_fourier_dot_transform(fourier_graph)                

        self.play(LaggedStartMap(
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
        ta_group.arrange(DOWN, buff = MED_LARGE_BUFF)
        ta_group.to_corner(UP+LEFT, buff = MED_SMALL_BUFF)

        frequency_axes = Axes(**self.frequency_axes_config)
        frequency_axes.set_color(TEAL)
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
                ta.x_axis, RIGHT,
                submobject_to_align = fa.x_axis
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
            time_graph.set_color(color)
            label.set_color(color)
            label.scale(0.75)
            label.next_to(time_graph, UP, SMALL_BUFF)
            fourier = get_fourier_transform(
                func, ta.x_min, 4*ta.x_max
            )
            fourier_graph = fa.get_graph(fourier)
            fourier_graph.set_color(self.center_of_mass_color)

            arrow = Arrow(
                ta.x_axis, fa.x_axis, 
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
                for attr in ("x_axis", "y_axis", "graph")
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

        self.play(LaggedStartMap(GrowFromCenter, flat_rects))
        self.wait()
        self.play(LaggedStartMap(MoveToTarget, flat_rects))
        self.wait()

        sum_spike_rects = VGroup(*[
            self.get_spike_rect(fa_group[2], freq)
            for freq in freqs
        ])
        self.play(ReplacementTransform(
            flat_rects, sum_spike_rects
        ))
        self.play(LaggedStartMap(
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

class PauseAndPonder(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Pause and \\\\ ponder!",
            target_mode = "hooray"
        )
        self.change_student_modes(*["thinking"]*3)
        self.wait(4)

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
                formula.next_to, FRAME_X_RADIUS*RIGHT, RIGHT,
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
            for f in (0.5, 0.7, 1.0, 1.2, 3.0,)
        ])
        graph = axes.get_graph(func)
        graph.set_color(BLUE)

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
        frequency_axes.set_color(TEAL)
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
        fourier_graph.set_color(RED)
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
            VGroup(randy, speaker).shift, FRAME_Y_RADIUS*DOWN,
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
        new_graph.set_color(RED)

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
        filtered_graph.set_color(BLUE_C)

        to_fourier_arrow = self.to_fourier_arrow
        arrow = to_fourier_arrow.copy()
        arrow.rotate(TAU/2, about_edge = LEFT)
        arrow.shift(MED_SMALL_BUFF*LEFT)
        inv_fourier_words = TextMobject("Inverse Fourier \\\\ transform")
        inv_fourier_words.next_to(arrow, LEFT)
        VGroup(arrow, inv_fourier_words).set_color(MAROON_B)

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
            for n in (5, 7, 10, 12)
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
                "numbers_to_show" : list(range(1, 5)),
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
            wound_up_graph.next_to, FRAME_X_RADIUS*LEFT, LEFT,
            remover = True
        )
        self.wait()

        self.graph = new_fourier_graph
        wound_up_graph = self.get_polarized_mobject(new_fourier_graph, freq = 0)
        double_fourier_graph = frequency_axes.get_graph(
            lambda t : 0.25*np.cos(TAU*2*t)
        ).set_color(PINK)
        self.fourier_graph = double_fourier_graph
        self.remove(self.fourier_graph_dot)
        self.get_fourier_graph_drawing_update_anim(double_fourier_graph)
        self.generate_fourier_dot_transform(double_fourier_graph)
        self.center_of_mass_dot.set_color(PINK)
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
        self.change_frequency(5.0, run_time = 15, rate_func=linear)
        self.wait()

    ##

    def get_cosine_wave(self, freq, **kwargs):
        kwargs["shift_val"] = 0
        kwargs["scale_val"] = 1.0
        return DrawFrequencyPlot.get_cosine_wave(self, freq, **kwargs)

class WriteComplexExponentialExpression(DrawFrequencyPlot):
    CONFIG = {
        "signal_frequency" : 2.0,
        "default_num_v_lines_indicating_periods" : 0,
        "time_axes_scale_val" : 0.7,
        "initial_winding_frequency" : 0.1,
        "circle_plane_config" : {
            "unit_size" : 2,
            "y_radius" : FRAME_Y_RADIUS+LARGE_BUFF,
            "x_radius" : FRAME_X_RADIUS+LARGE_BUFF
        }
    }
    def construct(self):
        self.remove(self.pi_creature)
        self.setup_plane()
        self.setup_graph()
        self.show_winding_with_both_coordinates()
        self.show_plane_as_complex_plane()
        self.show_eulers_formula()
        self.show_winding_graph_expression()
        self.find_center_of_mass()

    def setup_plane(self):
        circle_plane = ComplexPlane(**self.circle_plane_config)
        circle_plane.shift(DOWN+LEFT)
        circle = DashedLine(ORIGIN, TAU*UP)
        circle.apply_complex_function(
            lambda z : R3_to_complex(
                circle_plane.number_to_point(np.exp(z))
            )
        )
        circle_plane.add(circle)

        time_axes = self.get_time_axes()
        time_axes.background_rectangle = BackgroundRectangle(
            time_axes, 
            fill_opacity = 0.9,
            buff = MED_SMALL_BUFF,
        ) 
        time_axes.add_to_back(time_axes.background_rectangle)
        time_axes.scale(self.time_axes_scale_val)
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
        freq = self.initial_winding_frequency
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
        lines.set_color(PINK)
        def lines_update(lines):
            point = com_dot.get_center()
            x, y = plane.point_to_coords(point)
            h_line.put_start_and_end_on(
                plane.coords_to_point(0, y), point
            )
            v_line.put_start_and_end_on(
                plane.coords_to_point(x, 0), point
            )
        lines_update_anim = Mobject.add_updater(lines, lines_update)
        lines_update_anim.update(0)
        self.add(lines_update_anim)

        self.change_frequency(
            2.04, 
            added_anims = [
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
        dot = self.center_of_mass_dot
        complex_plane_title = TextMobject("Complex plane")
        complex_plane_title.add_background_rectangle()
        complex_plane_title.to_edge(UP)
        coordinate_labels = plane.get_coordinate_labels()
        number_label = DecimalNumber(
            0, include_background_rectangle = True,
        )
        number_label_update_anim = ContinualChangingDecimal(
            number_label, 
            lambda a : plane.point_to_number(dot.get_center()),
            position_update_func = lambda l : l.next_to(
                dot, DOWN+RIGHT,
                buff = SMALL_BUFF
            ),
        )
        number_label_update_anim.update(0)
        flower_path = ParametricFunction(
            lambda t : plane.coords_to_point(
                np.sin(2*t)*np.cos(t),
                np.sin(2*t)*np.sin(t),
            ),
            t_min = 0, t_max = TAU,
        )
        flower_path.move_to(self.center_of_mass_dot)

        self.play(FadeOut(to_fade))
        self.play(Write(complex_plane_title))
        self.play(Write(coordinate_labels))
        self.wait()
        self.play(FadeIn(number_label))
        self.add(number_label_update_anim)
        self.play(MoveAlongPath(
            dot, flower_path, 
            run_time = 10,
            rate_func = bezier([0, 0, 1, 1])
        ))
        self.wait()
        self.play(ShowCreation(
            self.pol_graph, run_time = 3,
        ))
        self.play(FadeOut(self.pol_graph))
        self.wait()
        self.play(FadeOut(VGroup(
            dot, self.dot_component_anim.mobject, number_label
        )))
        self.remove(self.dot_component_anim)
        self.remove(number_label_update_anim)

        self.set_variables_as_attrs(
            number_label,
            number_label_update_anim,
            complex_plane_title,
        )

    def show_eulers_formula(self):
        plane = self.circle_plane

        ghost_dot = Dot(ORIGIN, fill_opacity = 0)
        def get_t():
            return ghost_dot.get_center()[0]
        def get_circle_point(scalar = 1, t_shift = 0):
            return plane.number_to_point(
                scalar*np.exp(complex(0, get_t()+t_shift))
            )
        vector = Vector(plane.number_to_point(1), color = GREEN)
        exp_base = TexMobject("e").scale(1.3)
        exp_base.add_background_rectangle()
        exp_decimal = DecimalNumber(0, unit = "i", include_background_rectangle = True)
        exp_decimal.scale(0.75)
        VGroup(exp_base, exp_decimal).match_color(vector)
        exp_decimal_update = ContinualChangingDecimal(
            exp_decimal, lambda a : get_t(),
            position_update_func = lambda d : d.move_to(
                exp_base.get_corner(UP+RIGHT), DOWN+LEFT
            )
        )
        exp_base_update = Mobject.add_updater(
            exp_base, lambda e : e.move_to(get_circle_point(
                scalar = 1.1, t_shift = 0.01*TAU
            ))
        )
        vector_update = Mobject.add_updater(
            vector, lambda v : v.put_start_and_end_on(
                plane.number_to_point(0), get_circle_point()
            )
        )
        updates = [exp_base_update, exp_decimal_update, vector_update]
        for update in updates:
            update.update(0)

        #Show initial vector
        self.play(
            GrowArrow(vector),
            FadeIn(exp_base),
            Write(exp_decimal)
        )
        self.add(*updates)
        self.play(ghost_dot.shift, 2*RIGHT, run_time = 3)
        self.wait()

        #Show arc
        arc, circle = [
            Line(ORIGIN, t*UP)
            for t in (get_t(), TAU)
        ]
        for mob in arc, circle:
            mob.insert_n_curves(20)
            mob.set_stroke(RED, 4)
            mob.apply_function(
                lambda p : plane.number_to_point(
                    np.exp(R3_to_complex(p))
                )
            )
        distance_label = DecimalNumber(
            exp_decimal.number,
            unit = "\\text{units}"
        )
        distance_label[-1].shift(SMALL_BUFF*RIGHT)
        distance_label.match_color(arc)
        distance_label.add_background_rectangle()
        distance_label.move_to(
            plane.number_to_point(
                1.1*np.exp(complex(0, 0.4*get_t())),
            ),
            DOWN+LEFT
        )

        self.play(ShowCreation(arc))
        self.play(ReplacementTransform(
            exp_decimal.copy(), distance_label
        ))
        self.wait()
        self.play(FadeOut(distance_label))

        #Show full cycle
        self.remove(arc)
        self.play(
            ghost_dot.move_to, TAU*RIGHT,
            ShowCreation(
                circle, 
                rate_func = lambda a : interpolate(
                    2.0/TAU, 1, smooth(a)
                ),
            ),
            run_time = 6,
        )
        self.wait()

        #Write exponential expression
        exp_expression = TexMobject("e", "^{-", "2\\pi i", "f", "t}")
        e, minus, two_pi_i, f, t = exp_expression
        exp_expression.next_to(
            plane.coords_to_point(1, 1), 
            UP+RIGHT
        )
        f.set_color(RED)
        t.set_color(YELLOW)
        exp_expression.add_background_rectangle()
        two_pi_i_f_t_group = VGroup(two_pi_i, f, t)
        two_pi_i_f_t_group.save_state()
        two_pi_i_f_t_group.move_to(minus, LEFT)
        exp_expression[1].remove(minus)
        t.save_state()
        t.align_to(f, LEFT)
        exp_expression[1].remove(f)

        labels = VGroup()
        for sym, word in (t, "Time"), (f, "Frequency"):
            label = TextMobject(word)
            label.match_style(sym)
            label.next_to(sym, UP, buff = MED_LARGE_BUFF)
            label.add_background_rectangle()
            label.arrow = Arrow(label, sym, buff = SMALL_BUFF)
            label.arrow.match_style(sym)
            labels.add(label)
        time_label, frequency_label = labels
        example_frequency = TexMobject("f = 1/10")
        example_frequency.add_background_rectangle()
        example_frequency.match_style(frequency_label)
        example_frequency.move_to(frequency_label, DOWN)

        self.play(ReplacementTransform(
            VGroup(exp_base[1], exp_decimal[1]).copy(),
            exp_expression
        ))
        self.play(FadeOut(circle))
        self.wait()

        ghost_dot.move_to(ORIGIN)
        always_shift(ghost_dot, rate = TAU)
        self.add(ghost_dot)
        
        self.play(
            Write(time_label),
            GrowArrow(time_label.arrow),
        )
        self.wait(12.5) #Leave time to say let's slow down
        self.remove(ghost_dot)
        self.play(
            FadeOut(time_label),
            FadeIn(frequency_label),
            t.restore,
            GrowFromPoint(f, frequency_label.get_center()),
            ReplacementTransform(
                time_label.arrow,
                frequency_label.arrow,
            )
        )
        ghost_dot.move_to(ORIGIN)
        ghost_dot.clear_updaters()
        always_shift(ghost_dot, rate=0.1*TAU)
        self.add(ghost_dot)
        self.wait(3)
        self.play(
            FadeOut(frequency_label),
            FadeIn(example_frequency)
        )
        self.wait(15) #Give time to reference other video
        #Reverse directions
        ghost_dot.clear_updaters()
        always_shift(ghost_dot, rate=-0.1 * TAU)
        self.play(
            FadeOut(example_frequency),
            FadeOut(frequency_label.arrow),
            GrowFromCenter(minus),
            two_pi_i_f_t_group.restore
        )
        self.wait(4)

        ghost_dot.clear_updaters()
        self.remove(*updates)
        self.play(*list(map(FadeOut, [
            update.mobject
            for update in updates
            if update.mobject is not vector
        ])))
        self.play(ghost_dot.move_to, ORIGIN)

        exp_expression[1].add(minus, f)
        exp_expression[1].sort(lambda p : p[0])

        self.set_variables_as_attrs(
            ambient_ghost_dot_movement, ghost_dot,
            vector, vector_update, exp_expression
        )

    def show_winding_graph_expression(self):
        ambient_ghost_dot_movement = self.ambient_ghost_dot_movement
        ghost_dot = self.ghost_dot
        vector = self.vector
        exp_expression = self.exp_expression
        plane = self.circle_plane
        time_axes_group = self.time_axes_group
        graph = self.graph
        pol_graph = self.get_polarized_mobject(graph, freq = 0.2)
        g_label = TexMobject("g(t)")
        g_label.match_color(graph)
        g_label.next_to(graph, UP)
        g_label.add_background_rectangle()
        g_scalar = g_label.copy()
        g_scalar.move_to(exp_expression, DOWN+LEFT)

        vector_animations = self.get_vector_animations(graph)
        vector_animations[1].mobject = vector
        graph_y_vector = vector_animations[0].mobject

        self.play(
            FadeIn(time_axes_group),
            FadeOut(self.complex_plane_title)
        )
        self.play(Write(g_label))
        self.wait()
        self.play(
            ReplacementTransform(g_label.copy(), g_scalar),
            exp_expression.next_to, g_scalar, RIGHT, SMALL_BUFF,
            exp_expression.shift, 0.5*SMALL_BUFF*UP,
        )
        self.play(*vector_animations, run_time = 15)
        self.add(*self.mobjects_from_last_animation)
        self.wait()

        integrand = VGroup(g_scalar, exp_expression)
        rect = SurroundingRectangle(integrand)
        morty = Mortimer()
        morty.next_to(rect, DOWN+RIGHT)
        morty.shift_onto_screen()
        self.play(
            ShowCreation(rect),
            FadeIn(morty)
        )
        self.play(morty.change, "raise_right_hand")
        self.play(Blink(morty))
        self.play(morty.change, "hooray", rect)
        self.wait(2)
        self.play(*list(map(FadeOut, [
            morty, rect, graph_y_vector, vector
        ])))

        self.integrand = integrand

    def find_center_of_mass(self):
        integrand = self.integrand
        integrand.generate_target()
        integrand.target.to_edge(RIGHT, buff = LARGE_BUFF)
        integrand.target.shift(MED_LARGE_BUFF*DOWN)
        sum_expr = TexMobject(
            "{1", "\\over", "N}",
            "\\sum", "_{k = 1}", "^N",
        )
        sum_expr.add_background_rectangle()
        sum_expr.shift(SMALL_BUFF*(UP+5*RIGHT))
        sum_expr.next_to(integrand.target, LEFT)

        integral = TexMobject(
            "{1", "\\over", "t_2 - t_1}",
            "\\int", "_{t_1}", "^{t_2}"
        )
        integral.move_to(sum_expr, RIGHT)
        time_interval_indicator = SurroundingRectangle(integral[2])
        integral.add_background_rectangle()
        axes = self.time_axes
        time_interval = Line(
            axes.coords_to_point(axes.x_min, 0),
            axes.coords_to_point(axes.x_max, 0),
        )
        time_interval.match_style(time_interval_indicator)
        time_interval_indicator.add(time_interval)
        dt_mob = TexMobject("dt")
        dt_mob.next_to(integrand.target, RIGHT, SMALL_BUFF, DOWN)
        dt_mob.add_background_rectangle()

        dots = self.show_center_of_mass_sampling(20)
        self.wait()
        self.play(
            Write(sum_expr),
            MoveToTarget(integrand),
        )

        #Add k subscript to t's
        t1 = integrand[0][1][2]
        t2 = integrand[1][1][-1]
        t_mobs = VGroup(t1, t2)
        t_mobs.save_state()
        t_mobs.generate_target()
        for i, t_mob in enumerate(t_mobs.target):
            k = TexMobject("k")
            k.match_style(t_mob)
            k.match_height(t_mob)
            k.scale(0.5)
            k.move_to(t_mob.get_corner(DOWN+RIGHT), LEFT)
            k.add_background_rectangle()
            t_mob.add(k)
            if i == 0:
                t_mob.shift(0.5*SMALL_BUFF*LEFT)

        self.play(MoveToTarget(t_mobs))
        self.play(LaggedStartMap(
            Indicate, dots[1],
            rate_func = there_and_back,
            color = TEAL,
        ))
        self.show_center_of_mass_sampling(100)
        dots = self.show_center_of_mass_sampling(500)
        self.wait()
        self.play(FadeOut(dots))
        self.play(
            ReplacementTransform(sum_expr, integral),
            FadeIn(dt_mob),
            t_mobs.restore,
        )
        self.wait()
        self.play(ShowCreation(time_interval_indicator))
        self.wait()
        self.play(FadeOut(time_interval_indicator))
        self.wait()

        #Show confusion
        randy = Randolph()
        randy.flip()
        randy.next_to(integrand, DOWN, LARGE_BUFF)
        randy.to_edge(RIGHT)
        full_expression_rect = SurroundingRectangle(
            VGroup(integral, dt_mob), color = RED
        )
        com_dot = self.center_of_mass_dot
        self.center_of_mass_dot_anim.update(0)
        com_arrow = Arrow(
            full_expression_rect.get_left(), com_dot,
            buff = SMALL_BUFF
        )
        com_arrow.match_color(com_dot)


        self.play(FadeIn(randy))
        self.play(randy.change, "confused", integral)
        self.play(Blink(randy))
        self.wait(2)
        self.play(ShowCreation(full_expression_rect))
        self.play(
            randy.change, "thinking", self.pol_graph,
            GrowArrow(com_arrow),
            GrowFromCenter(com_dot),
        )
        self.play(Blink(randy))
        self.wait(2)

    def show_center_of_mass_sampling(self, n_dots):
        time_graph = self.graph
        pol_graph = self.graph.polarized_mobject
        axes = self.time_axes

        dot = Dot(radius = 0.05, color = PINK)
        pre_dots = VGroup(*[
            dot.copy().move_to(axes.coords_to_point(t, 0))
            for t in np.linspace(axes.x_min, axes.x_max, n_dots)
        ])
        pre_dots.set_fill(opacity = 0)
        for graph in time_graph, pol_graph:
            if hasattr(graph, "dots"):
                graph.dot_fade_anims = [FadeOut(graph.dots)]
            else:
                graph.dot_fade_anims = []
            graph.save_state()
            graph.generate_target()
            if not hasattr(graph, "is_faded"):
                graph.target.fade(0.7)
            graph.is_faded = True
            graph.dots = VGroup(*[
                dot.copy().move_to(graph.point_from_proportion(a))
                for a in np.linspace(0, 1, n_dots)
            ])

        self.play(
            ReplacementTransform(
                pre_dots, time_graph.dots,
                lag_ratio = 0.5,
                run_time = 2,
            ),
            MoveToTarget(time_graph),
            *time_graph.dot_fade_anims
        )
        self.play(
            ReplacementTransform(
                time_graph.copy(), pol_graph.target
            ),
            MoveToTarget(pol_graph),
            ReplacementTransform(
                time_graph.dots.copy(),
                pol_graph.dots,
            ),
            *pol_graph.dot_fade_anims,
            run_time = 2
        )
        return VGroup(time_graph.dots, pol_graph.dots)

class EulersFormulaViaGroupTheoryWrapper(Scene):
    def construct(self):
        title = TextMobject("Euler's formula with introductory group theory")
        title.to_edge(UP)
        screen_rect = ScreenRectangle(height = 6)
        screen_rect.next_to(title, DOWN)
        self.add(title)
        self.play(ShowCreation(screen_rect))
        self.wait(2)

class WhyAreYouTellingUsThis(TeacherStudentsScene):
    def construct(self):
        self.student_says("Why are you \\\\ telling us this?")
        self.play(self.teacher.change, "happy")
        self.wait(2)

class BuildUpExpressionStepByStep(TeacherStudentsScene):
    def construct(self):
        expression = TexMobject(
            "\\frac{1}{t_2 - t_1}", "\\int_{t_1}^{t_2}",
            "g(t)", "e", "^{-2\\pi i", "f", "t}", "dt"
        )
        frac, integral, g, e, two_pi_i, f, t, dt = expression
        expression.next_to(self.teacher, UP+LEFT)
        t.set_color(YELLOW)
        g[2].set_color(YELLOW)
        dt[1].set_color(YELLOW)
        f.set_color(GREEN)
        t.save_state()
        t.move_to(f, LEFT)

        self.play(
            self.teacher.change, "raise_right_hand",
            FadeIn(e),
            FadeIn(two_pi_i),
        )
        self.play(
            self.get_student_changes(*["pondering"]*3),
            FadeIn(t),
        )
        self.play(
            FadeIn(f),
            t.restore,
        )
        self.wait()
        self.play(FadeIn(g), Blink(self.students[1]))
        self.wait()
        self.play(
            FadeIn(integral),
            FadeIn(frac),
            FadeIn(dt),
        )
        self.wait(3)
        self.teacher_says(
            "Just one final \\\\ distinction.",
            bubble_kwargs = {"height" : 2.5, "width" : 3.5},
            added_anims = [expression.to_corner, UP+RIGHT]
        )
        self.wait(3)

class ScaleUpCenterOfMass(WriteComplexExponentialExpression):
    CONFIG = {
        "time_axes_scale_val" : 0.6,
        "initial_winding_frequency" : 2.05
    }
    def construct(self):
        self.remove(self.pi_creature)
        self.setup_plane()
        self.setup_graph()
        self.add_center_of_mass_dot()
        self.add_expression()

        self.cross_out_denominator()
        self.scale_up_center_of_mass()
        self.comment_on_current_signal()

    def add_center_of_mass_dot(self):
        self.center_of_mass_dot = self.get_center_of_mass_dot()
        self.generate_center_of_mass_dot_update_anim()
        self.add(self.center_of_mass_dot)

    def add_expression(self):
        expression = TexMobject(
            "\\frac{1}{t_2 - t_1}", "\\int_{t_1}^{t_2}",
            "g(t)", "e", "^{-2\\pi i", "f", "t}", "dt"
        )
        frac, integral, g, e, two_pi_i, f, t, dt = expression
        expression.to_corner(UP+RIGHT)
        t.set_color(YELLOW)
        g[2].set_color(YELLOW)
        dt[1].set_color(YELLOW)
        f.set_color(GREEN)
        self.expression = expression
        self.add(expression)

        self.winding_freq_label.to_edge(RIGHT)
        self.winding_freq_label[1].match_color(f)
        self.winding_freq_label.align_to(
            self.circle_plane.coords_to_point(0, 0.1), DOWN
        )

    def cross_out_denominator(self):
        frac = self.expression[0]
        integral = self.expression[1:]
        for mob in frac, integral:
            mob.add_to_back(BackgroundRectangle(mob))
            self.add(mob)
        cross = Cross(frac)
        brace = Brace(integral, DOWN)
        label = brace.get_text("The actual \\\\ Fourier transform")
        label.add_background_rectangle()
        label.shift_onto_screen()
        rect = SurroundingRectangle(integral)

        self.play(ShowCreation(cross))
        self.wait()
        self.play(ShowCreation(rect))
        self.play(
            GrowFromCenter(brace),
            FadeIn(label)
        )
        self.wait(2)

        self.integral = integral
        self.frac = frac
        self.frac_cross = cross
        self.integral_rect = rect
        self.integral_brace = brace
        self.integral_label = label

    def scale_up_center_of_mass(self):
        plane = self.circle_plane
        origin = plane.coords_to_point(0, 0)
        com_dot = self.center_of_mass_dot
        com_vector = Arrow(
            origin, com_dot.get_center(), 
            buff = 0
        )
        com_vector.match_style(com_dot)
        vector_to_scale = com_vector.copy()
        def get_com_vector_copies(n):
            com_vector_copies = VGroup(*[
                com_vector.copy().shift(x*com_vector.get_vector())
                for x in range(1, n+1)
            ])
            com_vector_copies.set_color(TEAL)
            return com_vector_copies
        com_vector_update = UpdateFromFunc(
            com_vector,
            lambda v : v.put_start_and_end_on(origin, com_dot.get_center())
        )

        circle = Circle(color = TEAL)
        circle.surround(com_dot, buffer_factor = 1.2)

        time_span = Rectangle(
            stroke_width = 0,
            fill_color = TEAL,
            fill_opacity = 0.4
        )
        axes = self.time_axes
        time_span.replace(
            Line(axes.coords_to_point(0, 0), axes.coords_to_point(3, 1.5)),
            stretch = True
        )
        time_span.save_state()
        time_span.stretch(0, 0, about_edge = LEFT)

        graph = self.graph
        short_graph, long_graph = [
            axes.get_graph(
                graph.underlying_function, x_min = 0, x_max = t_max,
            ).match_style(graph)
            for t_max in (3, 6)
        ]
        for g in short_graph, long_graph:
            self.get_polarized_mobject(g, freq = self.initial_winding_frequency)

        self.play(
            FocusOn(circle, run_time = 2),
            Succession(
                ShowCreation, circle,
                FadeOut, circle,
            ),
        )
        self.play(
            com_dot.fade, 0.5,
            FadeIn(vector_to_scale)
        )
        self.wait()
        self.play(vector_to_scale.scale, 4, {"about_point" : origin})
        self.wait()
        self.play(
            FadeOut(vector_to_scale),
            FadeIn(com_vector),
        )
        self.remove(graph.polarized_mobject)
        self.play(
            com_dot.move_to, 
            center_of_mass(short_graph.polarized_mobject.points),
            com_vector_update,
            time_span.restore,
            ShowCreation(short_graph.polarized_mobject),
        )
        self.wait()
        # dot = Dot(fill_opacity = 0.5).move_to(time_span)
        # self.play(
        #     dot.move_to, com_vector,
        #     dot.set_fill, {"opacity" : 0},
        #     remover = True
        # )
        com_vector_copies = get_com_vector_copies(2)
        self.play(*[
            ReplacementTransform(
                com_vector.copy(), cvc,
                path_arc = -TAU/10
            )
            for cvc in com_vector_copies
        ])
        self.wait()

        #Squish_graph
        to_squish = VGroup(
            axes, graph, 
            time_span,
        )
        to_squish.generate_target()
        squish_factor = 0.75
        to_squish.target.stretch(squish_factor, 0, about_edge = LEFT)
        pairs = list(zip(
            to_squish.family_members_with_points(), 
            to_squish.target.family_members_with_points()
        ))
        to_unsquish = list(axes.x_axis.numbers) + list(axes.labels)
        for sm, tsm in pairs:
            if sm in to_unsquish:
                tsm.stretch(1/squish_factor, 0)
            if sm is axes.background_rectangle:
                tsm.stretch(1/squish_factor, 0, about_edge = LEFT)

        long_graph.stretch(squish_factor, 0)
        self.play(
            MoveToTarget(to_squish),
            FadeOut(com_vector_copies)
        )
        long_graph.move_to(graph, LEFT)
        self.play(
            com_dot.move_to, 
            center_of_mass(long_graph.polarized_mobject.points),
            com_vector_update,
            time_span.stretch, 2, 0, {"about_edge" : LEFT},
            *[
                ShowCreation(
                    mob,
                    rate_func = lambda a : interpolate(
                        0.5, 1, smooth(a)
                    )
                )
                for mob in (long_graph, long_graph.polarized_mobject)
            ],
            run_time = 2
        )
        self.remove(graph, short_graph.polarized_mobject)
        self.graph = long_graph
        self.wait()
        self.play(FocusOn(com_dot))
        com_vector_copies = get_com_vector_copies(5)
        self.play(*[
            ReplacementTransform(
                com_vector.copy(), cvc,
                path_arc = -TAU/10
            )
            for cvc in com_vector_copies
        ])
        self.wait()

        # Scale graph out even longer
        to_shift = VGroup(self.integral, self.integral_rect)
        to_fade = VGroup(
            self.integral_brace, self.integral_label,
            self.frac, self.frac_cross
        )
        self.play(
            to_shift.shift, 2*DOWN,
            FadeOut(to_fade),
            axes.background_rectangle.stretch, 2, 0, {"about_edge" : LEFT},
            Animation(axes),
            Animation(self.graph),
            FadeOut(com_vector_copies),
        )
        self.change_frequency(2.0, added_anims = [com_vector_update])
        very_long_graph = axes.get_graph(
            graph.underlying_function,
            x_min = 0, x_max = 12,
        )
        very_long_graph.match_style(graph)
        self.get_polarized_mobject(very_long_graph, freq = 2.0)
        self.play(
            com_dot.move_to,
            center_of_mass(very_long_graph.polarized_mobject.points),
            com_vector_update,
            ShowCreation(
                very_long_graph,
                rate_func = lambda a : interpolate(0.5, 1, a)
            ),
            ShowCreation(very_long_graph.polarized_mobject)
        )
        self.remove(graph, graph.polarized_mobject)
        self.graph = very_long_graph
        self.wait()
        self.play(
            com_vector.scale, 12, {"about_point" : origin},
            run_time = 2
        )
        # com_vector_copies = get_com_vector_copies(11)
        # self.play(ReplacementTransform(
        #     VGroup(com_vector.copy()), 
        #     com_vector_copies,
        #     path_arc = TAU/10,
        #     run_time = 1.5,
        #     lag_ratio = 0.5
        # ))
        self.wait()

        self.com_vector = com_vector
        self.com_vector_update = com_vector_update
        self.com_vector_copies = com_vector_copies

    def comment_on_current_signal(self):
        graph = self.graph
        com_dot = self.center_of_mass_dot 
        com_vector = self.com_vector
        com_vector_update = self.com_vector_update
        axes = self.time_axes
        origin = self.circle_plane.coords_to_point(0, 0)
        wps_label = self.winding_freq_label

        new_com_vector_update = UpdateFromFunc(
            com_vector, lambda v : v.put_start_and_end_on(
                origin, com_dot.get_center()
            ).scale(12, about_point = origin)
        )

        v_lines = self.get_v_lines_indicating_periods(
            freq = 1.0, n_lines = 3
        )[:2]
        graph_portion = axes.get_graph(
            graph.underlying_function, x_min = 1, x_max = 2
        )
        graph_portion.set_color(TEAL)
        bps_label = TextMobject("2 beats per second")
        bps_label.scale(0.75)
        bps_label.next_to(graph_portion, UP, aligned_edge = LEFT)
        bps_label.shift(SMALL_BUFF*RIGHT)
        bps_label.add_background_rectangle()

        self.play(
            ShowCreation(v_lines, lag_ratio = 0),
            ShowCreation(graph_portion),
            FadeIn(bps_label),
        )
        self.wait()
        self.play(ReplacementTransform(
            bps_label[1][0].copy(), wps_label[1]
        ))
        self.wait()
        self.play(
            com_vector.scale, 0.5, {"about_point" : origin},
            rate_func = there_and_back,
            run_time = 2
        )
        self.wait(2)
        self.change_frequency(2.5,
            added_anims = [new_com_vector_update],
            run_time = 20,
            rate_func=linear,
        )
        self.wait()

class TakeAStepBack(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Hang on, go over \\\\ that again?",
            target_mode = "confused"
        ),
        self.change_student_modes(*["confused"]*3)
        self.play(self.teacher.change, "happy")
        self.wait(3)

class SimpleCosineWrappingAroundCircle(WriteComplexExponentialExpression):
    CONFIG = {
        "initial_winding_frequency" : 0,
        "circle_plane_config" : {
            "unit_size" : 3,
        },
    }
    def construct(self):
        self.setup_plane()
        self.setup_graph()
        self.remove(self.pi_creature)
        self.winding_freq_label.shift(7*LEFT)
        VGroup(self.time_axes, self.graph).shift(4*UP)
        VGroup(
            self.circle_plane,
            self.graph.polarized_mobject
        ).move_to(ORIGIN)
        self.add(self.get_center_of_mass_dot())
        self.generate_center_of_mass_dot_update_anim()

        self.change_frequency(
            2.0, 
            rate_func=linear, 
            run_time = 30
        )
        self.wait()

class SummarizeTheFullTransform(DrawFrequencyPlot):
    CONFIG = {
        "time_axes_config" : {
            "x_max" : 4.5,
            "x_axis_config" : {
                "unit_size" : 1.2,
                "tick_frequency" : 0.5,
                # "numbers_with_elongated_ticks" : range(0, 10, 2),
                # "numbers_to_show" : range(0, 10, 2),
            }
        },
        "frequency_axes_config" : {
            "x_max" : 5,
            "x_axis_config" : {
                "unit_size" : 1,
                "numbers_to_show" : list(range(1, 5)),
            },
            "y_max" : 2,
            "y_min" : -2,
            "y_axis_config" : {
                "unit_size" : 0.75,
                "tick_frequency" : 1,
            },
        },
    }
    def construct(self):
        self.setup_all_axes()
        self.show_transform_function()
        self.show_winding()

    def setup_all_axes(self):
        time_axes = self.get_time_axes()
        time_label, intensity_label = time_axes.labels
        time_label.next_to(
            time_axes.x_axis.get_right(), 
            DOWN, SMALL_BUFF
        )
        intensity_label.next_to(time_axes.y_axis, UP, buff = SMALL_BUFF)
        intensity_label.to_edge(LEFT)

        frequency_axes = self.get_frequency_axes()
        frequency_axes.to_corner(UP+RIGHT)
        frequency_axes.shift(RIGHT)
        fy_axis = frequency_axes.y_axis
        for number in fy_axis.numbers:
            number.add_background_rectangle()
        fy_axis.remove(*fy_axis.numbers[1::2])
        frequency_axes.remove(frequency_axes.box)
        frequency_axes.label.shift_onto_screen()

        circle_plane = self.get_circle_plane()

        self.set_variables_as_attrs(time_axes, frequency_axes, circle_plane)
        self.add(time_axes)

    def show_transform_function(self):
        time_axes = self.time_axes
        frequency_axes = self.frequency_axes
        def func(t):
            return 0.5*(2+np.cos(2*TAU*t) + np.cos(3*TAU*t))
        fourier_func = get_fourier_transform(
            func, 
            t_min = time_axes.x_min,
            t_max = time_axes.x_max,
            use_almost_fourier = False,
        )

        graph = time_axes.get_graph(func)
        graph.set_color(GREEN)
        fourier_graph = frequency_axes.get_graph(fourier_func)
        fourier_graph.set_color(RED)

        g_t = TexMobject("g(t)")
        g_t[-2].match_color(graph)
        g_t.next_to(graph, UP)
        g_hat_f = TexMobject("\\hat g(f)")
        g_hat_f[-2].match_color(fourier_graph)
        g_hat_f.next_to(
            frequency_axes.input_to_graph_point(2, fourier_graph),
            UP
        )

        morty = self.pi_creature

        time_label = time_axes.labels[0]
        frequency_label = frequency_axes.label
        for label in time_label, frequency_label:
            label.rect = SurroundingRectangle(label)
        time_label.rect.match_style(graph)
        frequency_label.rect.match_style(fourier_graph)

        self.add(graph)
        g_t.save_state()
        g_t.move_to(morty, UP+LEFT)
        g_t.fade(1)
        self.play(
            morty.change, "raise_right_hand",
            g_t.restore,
        )
        self.wait()
        self.play(Write(frequency_axes, run_time = 1))
        self.play(
            ReplacementTransform(graph.copy(), fourier_graph),
            ReplacementTransform(g_t.copy(), g_hat_f),
        )
        self.wait(2)
        for label in time_label, frequency_label:
            self.play(
                ShowCreation(label.rect),
                morty.change, "thinking"
            )
            self.play(FadeOut(label.rect))
        self.wait()

        self.set_variables_as_attrs(
            graph, fourier_graph,
            g_t, g_hat_f
        )

    def show_winding(self):
        plane = self.circle_plane
        graph = self.graph
        fourier_graph = self.fourier_graph
        morty = self.pi_creature
        g_hat_f = self.g_hat_f
        g_hat_f_rect = SurroundingRectangle(g_hat_f)
        g_hat_f_rect.set_color(TEAL)
        g_hat_rect = SurroundingRectangle(g_hat_f[0])
        g_hat_rect.match_style(g_hat_f_rect)

        g_hat_f.generate_target()
        g_hat_f.target.next_to(plane, RIGHT)
        g_hat_f.target.shift(UP)
        arrow = Arrow(
            g_hat_f.target.get_left(),
            plane.coords_to_point(0, 0),
            color = self.center_of_mass_color,
        )

        frequency_axes = self.frequency_axes
        imaginary_fourier_graph = frequency_axes.get_graph(
            get_fourier_transform(
                graph.underlying_function,
                t_min = self.time_axes.x_min,
                t_max = self.time_axes.x_max,
                real_part = False,
                use_almost_fourier = False,
            )
        )
        imaginary_fourier_graph.set_color(BLUE)
        imaginary_fourier_graph.shift(
            frequency_axes.x_axis.get_right() - \
            imaginary_fourier_graph.points[-1],
        )

        real_part = TextMobject(
            "Real part of", "$\\hat g(f)$"
        )
        real_part[1].match_style(g_hat_f)
        real_part.move_to(g_hat_f)
        real_part.to_edge(RIGHT)

        self.get_polarized_mobject(graph, freq = 0)
        update_pol_graph = UpdateFromFunc(
            graph.polarized_mobject,
            lambda m : m.set_stroke(width = 2)
        )
        com_dot = self.get_center_of_mass_dot()

        winding_run_time = 40.0
        g_hat_f_indication = Succession(
            Animation, Mobject(), {"run_time" : 4},
            FocusOn, g_hat_f,
            ShowCreation, g_hat_f_rect,
            Animation, Mobject(),
            Transform, g_hat_f_rect, g_hat_rect,
            Animation, Mobject(),
            FadeOut, g_hat_f_rect,
            Animation, Mobject(),
            MoveToTarget, g_hat_f,
            UpdateFromAlphaFunc, com_dot, lambda m, a : m.set_fill(opacity = a),
            Animation, Mobject(), {"run_time" : 2},
            GrowArrow, arrow,
            FadeOut, arrow,
            Animation, Mobject(), {"run_time" : 5},
            Write, real_part, {"run_time" : 2},
            Animation, Mobject(), {"run_time" : 3},
            ShowCreation, imaginary_fourier_graph, {"run_time" : 3},
            rate_func = squish_rate_func(
                lambda x : x, 0, 31./winding_run_time
            ),
            run_time = winding_run_time
        )

        self.play(
            FadeIn(plane),
            ReplacementTransform(
                graph.copy(), graph.polarized_mobject
            ),
            morty.change, "happy",
        )
        self.generate_center_of_mass_dot_update_anim(multiplier = 4.5)
        self.generate_fourier_dot_transform(fourier_graph)
        self.change_frequency(
            5.0, 
            rate_func=linear, 
            run_time = winding_run_time,
            added_anims = [
                g_hat_f_indication, 
                update_pol_graph,
                Animation(frequency_axes.x_axis.numbers),
                Animation(self.fourier_graph_dot),
            ]
        )
        self.wait()

class SummarizeFormula(Scene):
    def construct(self):
        expression = self.get_expression()
        screen_rect = ScreenRectangle(height = 5)
        screen_rect.to_edge(DOWN)

        exp_rect, g_exp_rect, int_rect = [
            SurroundingRectangle(VGroup(
                expression.get_part_by_tex(p1),
                expression.get_part_by_tex(p2),
            ))
            for p1, p2 in [("e", "t}"), ("g({}", "t}"), ("\\int", "dt")]
        ]

        self.add(expression)
        self.wait()
        self.play(
            ShowCreation(screen_rect),
            ShowCreation(exp_rect),
        )
        self.wait(2)
        self.play(Transform(exp_rect, g_exp_rect))
        self.wait(2)
        self.play(Transform(exp_rect, int_rect))
        self.wait(2)

    def get_expression(self):
        expression = TexMobject(
            "\\hat g(", "f", ")", "=", "\\int", "_{t_1}", "^{t_2}",
            "g({}", "t", ")", "e", "^{-2\\pi i", "f", "t}", "dt"
        )
        expression.set_color_by_tex(
            "t", YELLOW, substring = False,
        )
        expression.set_color_by_tex("t}", YELLOW)
        expression.set_color_by_tex(
            "f", RED, substring = False,
        )
        expression.scale(1.2)
        expression.to_edge(UP)
        return expression

class OneSmallNote(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Just one \\\\ small note...",
            # target_mode = 
        )
        self.change_student_modes("erm", "happy", "sassy")
        self.wait(2)

class BoundsAtInfinity(SummarizeFormula):
    def construct(self):
        expression = self.get_expression()
        self.add(expression)
        self.add_graph()
        axes = self.axes
        graph = self.graph

        time_interval = self.get_time_interval(-2, 2)
        wide_interval = self.get_time_interval(-FRAME_X_RADIUS, FRAME_X_RADIUS)
        bounds = VGroup(*reversed(expression.get_parts_by_tex("t_")))
        bound_rects = VGroup(*[
            SurroundingRectangle(b, buff = 0.5*SMALL_BUFF)
            for b in bounds
        ])
        bound_rects.set_color(TEAL)
        inf_bounds = VGroup(*[
            VGroup(TexMobject(s + "\\infty"))
            for s in ("-", "+")
        ])
        decimal_bounds = VGroup(*[DecimalNumber(0) for x in range(2)])
        for bound, inf_bound, d_bound in zip(bounds, inf_bounds, decimal_bounds):
            for new_bound in inf_bound, d_bound:
                new_bound.scale(0.7)
                new_bound.move_to(bound, LEFT)
                new_bound.bound = bound
        def get_db_num_update(vect):
            return lambda a : axes.x_axis.point_to_number(
                time_interval.get_edge_center(vect)
            )
        decimal_updates = [
            ChangingDecimal(
                db, get_db_num_update(vect),
                position_update_func = lambda m : m.move_to(
                    m.bound, LEFT
                )
            )
            for db, vect in zip(decimal_bounds, [LEFT, RIGHT])
        ]
        for update in decimal_updates:
            update.update(1)

        time_interval.save_state()
        self.wait()
        self.play(ReplacementTransform(
            self.get_time_interval(0, 0.01), time_interval
        ))
        self.play(LaggedStartMap(ShowCreation, bound_rects))
        self.wait()
        self.play(FadeOut(bound_rects))
        self.play(ReplacementTransform(bounds, inf_bounds))
        self.play(Transform(
            time_interval, wide_interval,
            run_time = 4,
            rate_func = there_and_back
        ))
        self.play(
            ReplacementTransform(inf_bounds, decimal_bounds),
            time_interval.restore,
        )
        self.play(
            VGroup(axes, graph).stretch, 0.05, 0,
            Transform(time_interval, wide_interval),
            UpdateFromAlphaFunc(
                axes.x_axis.numbers, 
                lambda m, a : m.set_fill(opacity = 1-a)
            ),
            *decimal_updates,
            run_time = 12,
            rate_func = bezier([0, 0, 1, 1])
        )
        self.wait()


    def add_graph(self):
        axes = Axes(
            x_min = -140,
            x_max = 140,
            y_min = -2, 
            y_max = 2,
            axis_config = {
                "include_tip" : False,
            },
        )
        axes.x_axis.add_numbers(*list(filter(
            lambda x : x != 0,
            list(range(-8, 10, 2)),
        )))
        axes.shift(DOWN)
        self.add(axes)

        def func(x):
            return np.exp(-0.1*x**2)*(1 + np.cos(TAU*x))
        graph = axes.get_graph(func)
        self.add(graph)
        graph.set_color(YELLOW)

        self.set_variables_as_attrs(axes, graph)

    def get_time_interval(self, t1, t2):
        line = Line(*[
            self.axes.coords_to_point(t, 0)
            for t in (t1, t2)
        ])
        rect = Rectangle(
            stroke_width = 0,
            fill_color = TEAL,
            fill_opacity = 0.5,
        )
        rect.match_width(line)
        rect.stretch_to_fit_height(2.5)
        rect.move_to(line, DOWN)
        return rect

class MoreToCover(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Much more to say...",
            target_mode = "hooray",
            run_time = 1,
        )
        self.wait()
        self.teacher_says(
            "SO MUCH!",
            target_mode = "surprised",
            added_anims = [self.get_student_changes(*3*["happy"])],
            run_time = 0.5
        )
        self.wait(2)

class ShowUncertaintyPrinciple(Scene):
    def construct(self):
        title = TextMobject("Uncertainty principle")
        self.add(title)
        top_axes = Axes(
            x_min = -FRAME_X_RADIUS,
            x_max = FRAME_X_RADIUS,
            y_min = 0,
            y_max = 3,
            y_axis_config = {
                "unit_size" : 0.6,
                "include_tip" : False,
            }
        )
        bottom_axes = top_axes.deepcopy()
        arrow = Vector(DOWN, color = WHITE)
        group = VGroup(
            title, top_axes, arrow, bottom_axes
        )
        group.arrange(DOWN)
        title.shift(MED_SMALL_BUFF*UP)
        group.to_edge(UP)
        fourier_word = TextMobject("Fourier transform")
        fourier_word.next_to(arrow, RIGHT)
        self.add(group, fourier_word)

        ghost_dot = Dot(RIGHT, fill_opacity = 0)
        def get_bell_func(factor = 1):
            return lambda x : 2*np.exp(-factor*x**2)
        top_graph = top_axes.get_graph(get_bell_func())
        top_graph.set_color(YELLOW)
        bottom_graph = bottom_axes.get_graph(get_bell_func())
        bottom_graph.set_color(RED)
        def get_update_func(axes):
            def update_graph(graph):
                f = ghost_dot.get_center()[0]
                if axes == bottom_axes:
                    f = 1./f
                new_graph = axes.get_graph(get_bell_func(f))
                graph.points = new_graph.points
            return update_graph

        factors = [0.3, 0.1, 2, 10, 100, 0.01, 0.5]

        self.play(ShowCreation(top_graph))
        self.play(ReplacementTransform(
            top_graph.copy(),
            bottom_graph,
        ))
        self.wait(2)
        self.add(*[
            Mobject.add_updater(graph, get_update_func(axes))
            for graph, axes in [(top_graph, top_axes), (bottom_graph, bottom_axes)]
        ])
        for factor in factors:
            self.play(
                ghost_dot.move_to, factor*RIGHT,
                run_time = 2
            )
            self.wait()

class XCoordinateLabelTypoFix(Scene):
    def construct(self):
        words = TextMobject("$x$-coordinate for center of mass")
        words.set_color(RED)
        self.add(words)

class NextVideoWrapper(Scene):
    def construct(self):
        title = TextMobject("Next video")
        title.to_edge(UP)
        screen_rect = ScreenRectangle(height = 6)
        screen_rect.next_to(title, DOWN)
        self.add(title)
        self.play(ShowCreation(screen_rect))
        self.wait(2)

class SubscribeOrBinge(PiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        morty.center().to_edge(DOWN, LARGE_BUFF)
        subscribe = TextMobject("Subscribe")
        subscribe.set_color(RED)
        subscribe.next_to(morty, UP+RIGHT)
        binge = TextMobject("Binge")
        binge.set_color(BLUE)
        binge.next_to(morty, UP+LEFT)

        videos = VGroup(*[VideoIcon() for x in range(30)])
        colors = it.cycle([BLUE_D, BLUE_E, BLUE_C, GREY_BROWN])
        for video, color in zip(videos, colors):
            video.set_color(color)
        videos.move_to(binge.get_bottom(), UP)
        video_anim = LaggedStartMap(
            Succession, videos, 
            lambda v : (
                FadeIn, v,
                ApplyMethod, v.shift, 5*DOWN, {"run_time" : 6},
            ),
            run_time = 10
        )
        sub_arrow = Arrow(
            subscribe.get_bottom(),
            Dot().to_corner(DOWN+RIGHT, buff = LARGE_BUFF),
            color = RED
        )

        for word in subscribe, binge:
            word.save_state()
            word.shift(DOWN)
            word.set_fill(opacity = 0)

        self.play(
            subscribe.restore,
            morty.change, "raise_left_hand"
        )
        self.play(GrowArrow(sub_arrow))
        self.wait()
        self.play(
            video_anim,
            Succession(
                AnimationGroup(
                    ApplyMethod(binge.restore),
                    ApplyMethod(morty.change, "raise_right_hand", binge),
                ),
                Blink, morty,
                ApplyMethod, morty.change, "shruggie", videos,
                Animation, Mobject(), {"run_time" : 2},
                Blink, morty,
                Animation, Mobject(), {"run_time" : 4}
            )
        )

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
            line.set_color_by_tex_to_color_map({
                "$C$" : BLUE_D,
                "\\partial C" : BLUE_D,
                "$B$" : BLUE_C,
                "$D$" : YELLOW,
            })
        VGroup(lines[2][1][2], lines[2][1][6]).set_color(RED)
        VGroup(lines[2][1][4], lines[2][1][8]).set_color(MAROON_B)
        lines[2][1][10].set_color(BLUE_C)
        lines.scale(1.25)
        lines.arrange(DOWN, buff = LARGE_BUFF, aligned_edge = LEFT)

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

class FourierEndScreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons" : [
            "CrypticSwarm",
            "Ali Yahya",
            "Juan Benet",
            "Markus Persson",
            "Damion Kistler",
            "Burt Humburg",
            "Yu Jun",
            "Dave Nicponski",
            "Kaustuv DeBiswas",
            "Joseph John Cox",
            "Luc Ritchie",
            "Achille Brighton",
            "Rish Kundalia",
            "Yana Chernobilsky",
            "Shìmín Kuang",
            "Mathew Bramson",
            "Jerry Ling",
            "Mustafa Mahdi",
            "Meshal Alshammari",
            "Mayank M. Mehrotra",
            "Lukas Biewald",
            "Robert Teed",
            "One on Epsilon",
            "Samantha D. Suplee",
            "Mark Govea",
            "John Haley",
            "Julian Pulgarin",
            "Jeff Linse",
            "Cooper Jones",
            "Boris Veselinovich",
            "Ryan Dahl",
            "Ripta Pasay",
            "Eric Lavault",
            "Mads Elvheim",
            "Andrew Busey",
            "Randall Hunt",
            "Desmos",
            "Tianyu Ge",
            "Awoo",
            "Dr David G. Stork",
            "Linh Tran",
            "Jason Hise",
            "Bernd Sing",
            "Ankalagon",
            "Mathias Jansson",
            "David Clark",
            "Ted Suzman",
            "Eric Chow",
            "Michael Gardner",
            "Jonathan Eppele",
            "Clark Gaebel",
            "David Kedmey",
            "Jordan Scales",
            "Ryan Atallah",
            "supershabam",
            "1stViewMaths",
            "Jacob Magnuson",
            "Thomas Tarler",
            "Isak Hietala",
            "James Thornton",
            "Egor Gumenuk",
            "Waleed Hamied",
            "Oliver Steele",
            "Yaw Etse",
            "David B",
            "Julio Cesar Campo Neto",
            "Delton Ding",
            "George Chiesa",
            "Chloe Zhou",
            "Alexander Nye",
            "Ross Garber",
            "Wang HaoRan",
            "Felix Tripier",
            "Arthur Zey",
            "Norton",
            "Kevin Le",
            "Alexander Feldman",
            "David MacCumber",
        ],
    }

class Thumbnail(Scene):
    def construct(self):
        title = TextMobject("Fourier\\\\", "Visualized")
        title.set_color(YELLOW)
        title.set_stroke(RED, 2)
        title.scale(2.5)
        title.add_background_rectangle()

        def func(t):
            return np.cos(2*TAU*t) + np.cos(3*TAU*t) + np.cos(5*t)
        fourier = get_fourier_transform(func, -5, 5)

        graph = FunctionGraph(func, x_min = -5, x_max = 5)
        graph.set_color(BLUE)
        fourier_graph = FunctionGraph(fourier, x_min = 0, x_max = 6)
        fourier_graph.set_color(YELLOW)
        for g in graph, fourier_graph:
            g.stretch_to_fit_height(2)
            g.stretch_to_fit_width(10)
            g.set_stroke(width = 8)

        pol_graphs = VGroup()
        for f in np.linspace(1.98, 2.02, 7):
            pol_graph = ParametricFunction(
                lambda t : complex_to_R3(
                    (2+np.cos(2*TAU*t)+np.cos(3*TAU*t))*np.exp(-complex(0, TAU*f*t))
                ),
                t_min = -5,
                t_max = 5,
                num_graph_points = 200,
            )
            pol_graph.match_color(graph)
            pol_graph.set_height(2)
            pol_graphs.add(pol_graph)
        pol_graphs.arrange(RIGHT, buff = LARGE_BUFF)
        pol_graphs.set_color_by_gradient(BLUE_C, YELLOW)
        pol_graphs.match_width(graph)
        pol_graphs.set_stroke(width = 2)


        self.clear()
        title.center().to_edge(UP)
        pol_graphs.set_width(FRAME_WIDTH - 1)
        pol_graphs.center()
        title.move_to(pol_graphs)
        title.shift(SMALL_BUFF*LEFT)
        graph.next_to(title, UP)
        fourier_graph.next_to(title, DOWN)
        self.add(pol_graphs, title, graph, fourier_graph)















