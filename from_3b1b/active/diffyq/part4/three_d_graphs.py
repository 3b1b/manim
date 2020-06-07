from manimlib.imports import *
from active_projects.diffyq.part3.temperature_graphs import TemperatureGraphScene
from active_projects.diffyq.part2.wordy_scenes import WriteHeatEquationTemplate


class ShowLinearity(WriteHeatEquationTemplate, TemperatureGraphScene):
    CONFIG = {
        "temp_text": "Temp",
        "alpha": 0.1,
        "axes_config": {
            "z_max": 2,
            "z_min": -2,
            "z_axis_config": {
                "tick_frequency": 0.5,
                "unit_size": 1.5,
            },
        },
        "default_surface_config": {
            "resolution": (16, 16)
            # "resolution": (4, 4)
        },
        "freqs": [2, 5],
    }

    def setup(self):
        TemperatureGraphScene.setup(self)
        WriteHeatEquationTemplate.setup(self)

    def construct(self):
        self.init_camera()
        self.add_three_graphs()
        self.show_words()
        self.add_function_labels()
        self.change_scalars()

    def init_camera(self):
        self.camera.set_distance(1000)

    def add_three_graphs(self):
        axes_group = self.get_axes_group()
        axes0, axes1, axes2 = axes_group
        freqs = self.freqs
        scalar_trackers = Group(
            ValueTracker(1),
            ValueTracker(1),
        )
        graphs = VGroup(
            self.get_graph(axes0, [freqs[0]], [scalar_trackers[0]]),
            self.get_graph(axes1, [freqs[1]], [scalar_trackers[1]]),
            self.get_graph(axes2, freqs, scalar_trackers),
        )

        plus = TexMobject("+").scale(2)
        equals = TexMobject("=").scale(2)
        plus.move_to(midpoint(
            axes0.get_right(),
            axes1.get_left(),
        ))
        equals.move_to(midpoint(
            axes1.get_right(),
            axes2.get_left(),
        ))

        self.add(axes_group)
        self.add(graphs)
        self.add(plus)
        self.add(equals)

        self.axes_group = axes_group
        self.graphs = graphs
        self.scalar_trackers = scalar_trackers
        self.plus = plus
        self.equals = equals

    def show_words(self):
        equation = self.get_d1_equation()
        name = TextMobject("Heat equation")
        name.next_to(equation, DOWN)
        name.set_color_by_gradient(RED, YELLOW)
        group = VGroup(equation, name)
        group.to_edge(UP)

        shift_val = 0.5 * RIGHT

        arrow = Vector(1.5 * RIGHT)
        arrow.move_to(group)
        arrow.shift(shift_val)
        linear_word = TextMobject("``Linear''")
        linear_word.scale(2)
        linear_word.next_to(arrow, RIGHT)

        self.add(group)
        self.wait()
        self.play(
            ShowCreation(arrow),
            group.next_to, arrow, LEFT
        )
        self.play(FadeIn(linear_word, LEFT))
        self.wait()

    def add_function_labels(self):
        axes_group = self.axes_group
        graphs = self.graphs

        solution_labels = VGroup()
        for axes in axes_group:
            label = TextMobject("Solution", "$\\checkmark$")
            label.set_color_by_tex("checkmark", GREEN)
            label.next_to(axes, DOWN)
            solution_labels.add(label)

        kw = {
            "tex_to_color_map": {
                "T_1": BLUE,
                "T_2": GREEN,
            }
        }
        T1 = TexMobject("a", "T_1", **kw)
        T2 = TexMobject("b", "T_2", **kw)
        T_sum = TexMobject("T_1", "+", "T_2", **kw)
        T_sum_with_scalars = TexMobject(
            "a", "T_1", "+", "b", "T_2", **kw
        )

        T1.next_to(graphs[0], UP)
        T2.next_to(graphs[1], UP)
        T_sum.next_to(graphs[2], UP)
        T_sum.shift(SMALL_BUFF * DOWN)
        T_sum_with_scalars.move_to(T_sum)

        a_brace = Brace(T1[0], UP, buff=SMALL_BUFF)
        b_brace = Brace(T2[0], UP, buff=SMALL_BUFF)
        s1_decimal = DecimalNumber()
        s1_decimal.match_color(T1[1])
        s1_decimal.next_to(a_brace, UP, SMALL_BUFF)
        s1_decimal.add_updater(lambda m: m.set_value(
            self.scalar_trackers[0].get_value()
        ))
        s2_decimal = DecimalNumber()
        s2_decimal.match_color(T2[1])
        s2_decimal.next_to(b_brace, UP, SMALL_BUFF)
        s2_decimal.add_updater(lambda m: m.set_value(
            self.scalar_trackers[1].get_value()
        ))

        self.play(
            FadeIn(T1[1], DOWN),
            FadeIn(solution_labels[0], UP),
        )
        self.play(
            FadeIn(T2[1], DOWN),
            FadeIn(solution_labels[1], UP),
        )
        self.wait()
        self.play(
            TransformFromCopy(T1[1], T_sum[0]),
            TransformFromCopy(T2[1], T_sum[2]),
            TransformFromCopy(self.plus, T_sum[1]),
            *[
                Transform(
                    graph.copy().set_fill(opacity=0),
                    graphs[2].copy().set_fill(opacity=0),
                    remover=True
                )
                for graph in graphs[:2]
            ]
        )
        self.wait()
        self.play(FadeIn(solution_labels[2], UP))
        self.wait()

        # Show constants
        self.play(
            FadeIn(T1[0]),
            FadeIn(T2[0]),
            FadeIn(a_brace),
            FadeIn(b_brace),
            FadeIn(s1_decimal),
            FadeIn(s2_decimal),
            FadeOut(T_sum),
            FadeIn(T_sum_with_scalars),
        )

    def change_scalars(self):
        s1, s2 = self.scalar_trackers

        kw = {
            "run_time": 2,
        }
        for graph in self.graphs:
            graph.resume_updating()
        self.play(s2.set_value, -0.5, **kw)
        self.play(s1.set_value, -0.2, **kw)
        self.play(s2.set_value, 1.5, **kw)
        self.play(s1.set_value, 1.2, **kw)
        self.play(s2.set_value, 0.3, **kw)
        self.wait()

    #
    def get_axes_group(self):
        axes_group = VGroup(*[
            self.get_axes()
            for x in range(3)
        ])
        axes_group.arrange(RIGHT, buff=2)
        axes_group.set_width(FRAME_WIDTH - 1)
        axes_group.to_edge(DOWN, buff=1)
        return axes_group

    def get_axes(self, **kwargs):
        axes = self.get_three_d_axes(**kwargs)
        # axes.input_plane.set_fill(opacity=0)
        # axes.input_plane.set_stroke(width=0.5)
        # axes.add(axes.input_plane)
        self.orient_three_d_mobject(axes)
        axes.rotate(-5 * DEGREES, UP)
        axes.set_width(4)
        axes.x_axis.label.next_to(
            axes.x_axis.get_end(), DOWN,
            buff=2 * SMALL_BUFF
        )
        return axes

    def get_graph(self, axes, freqs, scalar_trackers):
        L = axes.x_max
        a = self.alpha

        def func(x, t):
            scalars = [st.get_value() for st in scalar_trackers]
            return np.sum([
                s * np.cos(k * x) * np.exp(-a * (k**2) * t)
                for freq, s in zip(freqs, scalars)
                for k in [freq * PI / L]
            ])

        def get_surface_graph_group():
            return VGroup(
                self.get_surface(axes, func),
                self.get_time_slice_graph(axes, func, t=0),
            )

        result = always_redraw(get_surface_graph_group)
        result.func = func
        result.suspend_updating()
        return result


class CombineSeveralSolutions(ShowLinearity):
    CONFIG = {
        "default_surface_config": {
            "resolution": (16, 16),
            # "resolution": (4, 4),
        },
        "n_top_graphs": 5,
        "axes_config": {
            "y_max": 15,
        },
        "target_scalars": [
            0.81, -0.53, 0.41, 0.62, -0.95
        ],
        "final_run_time": 14,
    }

    def construct(self):
        self.init_camera()
        self.add_all_axes()
        self.setup_all_graphs()
        self.show_infinite_family()
        self.show_sum()
        self.show_time_passing()

    def add_all_axes(self):
        top_axes_group = VGroup(*[
            self.get_axes(
                z_min=-1.25,
                z_max=1.25,
                z_axis_config={
                    "unit_size": 2,
                    "tick_frequency": 0.5,
                },
            )
            for x in range(self.n_top_graphs)
        ])
        top_axes_group.arrange(RIGHT, buff=2)
        top_axes_group.set_width(FRAME_WIDTH - 1.5)
        top_axes_group.to_corner(UL)
        dots = TexMobject("\\dots")
        dots.next_to(top_axes_group, RIGHT)

        low_axes = self.get_axes()
        low_axes.center()
        low_axes.scale(1.2)
        low_axes.to_edge(DOWN, buff=SMALL_BUFF)

        self.add(top_axes_group)
        self.add(dots)
        self.add(low_axes)

        self.top_axes_group = top_axes_group
        self.low_axes = low_axes

    def setup_all_graphs(self):
        scalar_trackers = Group(*[
            ValueTracker(1)
            for x in range(self.n_top_graphs)
        ])
        freqs = np.arange(self.n_top_graphs)
        freqs += 1
        self.top_graphs = VGroup(*[
            self.get_graph(axes, [n], [st])
            for axes, n, st in zip(
                self.top_axes_group,
                freqs,
                scalar_trackers,
            )
        ])
        self.low_graph = self.get_graph(
            self.low_axes, freqs, scalar_trackers
        )

        self.scalar_trackers = scalar_trackers

    def show_infinite_family(self):
        top_axes_group = self.top_axes_group
        top_graphs = self.top_graphs
        scalar_trackers = self.scalar_trackers

        decimals = self.get_decimals(
            top_axes_group, scalar_trackers
        )

        self.play(LaggedStart(*[
            AnimationGroup(
                Write(graph[0]),
                FadeIn(graph[1]),
            )
            for graph in top_graphs
        ]))
        self.wait()
        self.play(FadeIn(decimals))
        for graph in top_graphs:
            graph.resume_updating()

        self.play(LaggedStart(*[
            ApplyMethod(st.set_value, value)
            for st, value in zip(
                scalar_trackers,
                self.target_scalars,
            )
        ]), run_time=3)
        self.wait()

    def show_sum(self):
        top_graphs = self.top_graphs
        low_graph = self.low_graph
        low_graph.resume_updating()
        low_graph.update()

        self.play(
            LaggedStart(*[
                Transform(
                    top_graph.copy().set_fill(opacity=0),
                    low_graph.copy().set_fill(opacity=0),
                    remover=True,
                )
                for top_graph in top_graphs
            ]),
            FadeIn(
                low_graph,
                rate_func=squish_rate_func(smooth, 0.7, 1)
            ),
            run_time=3,
        )
        self.wait()

    def show_time_passing(self):
        all_graphs = [*self.top_graphs, self.low_graph]
        all_axes = [*self.top_axes_group, self.low_axes]

        time_tracker = ValueTracker(0)
        get_t = time_tracker.get_value

        anims = [
            ApplyMethod(
                time_tracker.set_value, 1,
                run_time=1,
                rate_func=linear
            )
        ]

        for axes, graph_group in zip(all_axes, all_graphs):
            graph_group.clear_updaters()
            surface, gslice = graph_group
            plane = self.get_const_time_plane(axes)
            plane.t_tracker.add_updater(
                lambda m: m.set_value(get_t())
            )
            gslice.axes = axes
            gslice.func = graph_group.func
            gslice.add_updater(lambda m: m.become(
                self.get_time_slice_graph(
                    m.axes, m.func, t=get_t()
                )
            ))
            self.add(gslice)
            self.add(plane.t_tracker)
            anims.append(FadeIn(plane))

        self.play(*anims)
        run_time = self.final_run_time
        self.play(
            time_tracker.increment_value, run_time,
            run_time=run_time,
            rate_func=linear,
        )

    #
    def get_decimals(self, axes_group, scalar_trackers):
        result = VGroup()
        for axes, st in zip(axes_group, scalar_trackers):
            decimal = DecimalNumber()
            decimal.move_to(axes.get_bottom(), UP)
            decimal.shift(SMALL_BUFF * RIGHT)
            decimal.set_color(YELLOW)
            decimal.scalar_tracker = st
            times = TexMobject("\\times")
            times.next_to(decimal, LEFT, SMALL_BUFF)
            decimal.add_updater(lambda d: d.set_value(
                d.scalar_tracker.get_value()
            ))
            group = VGroup(times, decimal)
            group.scale(0.7)
            result.add(group)
        return result


class CycleThroughManyLinearCombinations(CombineSeveralSolutions):
    CONFIG = {
        "default_surface_config": {
            "resolution": (16, 16),
            # "resolution": (4, 4),
        },
        "n_cycles": 10,
    }

    def construct(self):
        self.init_camera()
        self.add_all_axes()
        self.setup_all_graphs()
        #
        self.cycle_through_superpositions()

    def cycle_through_superpositions(self):
        top_graphs = self.top_graphs
        low_graph = self.low_graph
        scalar_trackers = self.scalar_trackers
        self.add(self.get_decimals(
            self.top_axes_group, scalar_trackers
        ))

        for graph in [low_graph, *top_graphs]:
            graph.resume_updating()
            self.add(graph)

        nst = len(scalar_trackers)
        for x in range(self.n_cycles):
            self.play(LaggedStart(*[
                ApplyMethod(st.set_value, value)
                for st, value in zip(
                    scalar_trackers,
                    3 * np.random.random(nst) - 1.5
                )
            ]), run_time=3)
            self.wait()
