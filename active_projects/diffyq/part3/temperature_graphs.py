from scipy import integrate

from manimlib.imports import *
from active_projects.ode.part2.heat_equation import *


class TemperatureGraphScene(SpecialThreeDScene):
    CONFIG = {
        "axes_config": {
            "x_min": 0,
            "x_max": TAU,
            "y_min": 0,
            "y_max": 10,
            "z_min": -3,
            "z_max": 3,
            "x_axis_config": {
                "tick_frequency": TAU / 8,
                "include_tip": False,
            },
            "num_axis_pieces": 1,
        },
        "default_graph_style": {
            "stroke_width": 2,
            "stroke_color": WHITE,
            "background_image_file": "VerticalTempGradient",
        },
        "default_surface_config": {
            "fill_opacity": 0.1,
            "checkerboard_colors": [LIGHT_GREY],
            "stroke_width": 0.5,
            "stroke_color": WHITE,
            "stroke_opacity": 0.5,
        },
        "temp_text": "Temperature",
    }

    def get_three_d_axes(self, include_labels=True, include_numbers=False, **kwargs):
        config = dict(self.axes_config)
        config.update(kwargs)
        axes = ThreeDAxes(**config)
        axes.set_stroke(width=2)

        if include_numbers:
            self.add_axes_numbers(axes)

        if include_labels:
            self.add_axes_labels(axes)

        # Adjust axis orientation
        axes.x_axis.rotate(
            90 * DEGREES, RIGHT,
            about_point=axes.c2p(0, 0, 0),
        )
        axes.y_axis.rotate(
            90 * DEGREES, UP,
            about_point=axes.c2p(0, 0, 0),
        )

        # Add xy-plane
        input_plane = self.get_surface(
            axes, lambda x, t: 0
        )
        input_plane.set_style(
            fill_opacity=0.5,
            fill_color=BLUE_B,
            stroke_width=0.5,
            stroke_color=WHITE,
        )

        axes.input_plane = input_plane

        return axes

    def add_axes_numbers(self, axes):
        x_axis = axes.x_axis
        y_axis = axes.y_axis
        tex_vals = [
            ("\\pi \\over 2", TAU / 4),
            ("\\pi", TAU / 2),
            ("3\\pi \\over 2", 3 * TAU / 4),
            ("2\\pi", TAU)
        ]
        x_labels = VGroup()
        for tex, val in tex_vals:
            label = TexMobject(tex)
            label.scale(0.5)
            label.next_to(x_axis.n2p(val), DOWN)
            x_labels.add(label)
        x_axis.add(x_labels)
        x_axis.numbers = x_labels

        y_axis.add_numbers()
        for number in y_axis.numbers:
            number.rotate(90 * DEGREES)
        return axes

    def add_axes_labels(self, axes):
        x_label = TexMobject("x")
        x_label.next_to(axes.x_axis.get_end(), RIGHT)
        axes.x_axis.label = x_label

        t_label = TextMobject("Time")
        t_label.rotate(90 * DEGREES, OUT)
        t_label.next_to(axes.y_axis.get_end(), UP)
        axes.y_axis.label = t_label

        temp_label = TextMobject(self.temp_text)
        temp_label.rotate(90 * DEGREES, RIGHT)
        temp_label.next_to(axes.z_axis.get_zenith(), RIGHT)
        axes.z_axis.label = temp_label
        for axis in axes:
            axis.add(axis.label)
        return axes

    def get_time_slice_graph(self, axes, func, t, **kwargs):
        config = dict()
        config.update(self.default_graph_style)
        config.update({
            "t_min": axes.x_min,
            "t_max": axes.x_max,
        })
        config.update(kwargs)
        return ParametricFunction(
            lambda x: axes.c2p(
                x, t, func(x, t)
            ),
            **config,
        )

    def get_initial_state_graph(self, axes, func, **kwargs):
        return self.get_time_slice_graph(
            axes,
            lambda x, t: func(x),
            t=0,
            **kwargs
        )

    def get_surface(self, axes, func, **kwargs):
        config = {
            "u_min": axes.x_min,
            "u_max": axes.x_max,
            "v_min": axes.y_min,
            "v_max": axes.y_max,
            "resolution": (
                (axes.x_max - axes.x_min) // axes.x_axis.tick_frequency,
                (axes.y_max - axes.y_min) // axes.y_axis.tick_frequency,
            ),
        }
        config.update(self.default_surface_config)
        config.update(kwargs)
        return ParametricSurface(
            lambda x, t: axes.c2p(
                x, t, func(x, t)
            ),
            **config
        )

    def orient_three_d_mobject(self, mobject,
                               phi=85 * DEGREES,
                               theta=-80 * DEGREES):
        mobject.rotate(-90 * DEGREES - theta, OUT)
        mobject.rotate(phi, LEFT)
        return mobject

    def get_rod_length(self):
        return self.axes_config["x_max"]

    def get_const_time_plane(self, axes):
        t_tracker = ValueTracker(0)
        plane = Polygon(
            *[
                axes.c2p(x, 0, z)
                for x, z in [
                    (axes.x_min, axes.z_min),
                    (axes.x_max, axes.z_min),
                    (axes.x_max, axes.z_max),
                    (axes.x_min, axes.z_max),
                ]
            ],
            stroke_width=0,
            fill_color=WHITE,
            fill_opacity=0.2
        )
        plane.add_updater(lambda m: m.move_to(
            axes.c2p(
                axes.x_min,
                t_tracker.get_value(),
                axes.z_min,
            ),
            IN + LEFT,
        ))
        plane.t_tracker = t_tracker
        return plane


class SimpleCosExpGraph(TemperatureGraphScene):
    def construct(self):
        axes = self.get_three_d_axes()
        cos_graph = self.get_cos_graph(axes)
        cos_exp_surface = self.get_cos_exp_surface(axes)

        self.set_camera_orientation(
            phi=80 * DEGREES,
            theta=-80 * DEGREES,
        )
        self.camera.frame_center.shift(3 * RIGHT)
        self.begin_ambient_camera_rotation(rate=0.01)

        self.add(axes)
        self.play(ShowCreation(cos_graph))
        self.play(UpdateFromAlphaFunc(
            cos_exp_surface,
            lambda m, a: m.become(
                self.get_cos_exp_surface(axes, v_max=a * 10)
            ),
            run_time=3
        ))

        self.add(cos_graph.copy())

        t_tracker = ValueTracker(0)
        get_t = t_tracker.get_value
        cos_graph.add_updater(
            lambda m: m.become(self.get_time_slice_graph(
                axes,
                lambda x: self.cos_exp(x, get_t()),
                t=get_t()
            ))
        )

        plane = Rectangle(
            stroke_width=0,
            fill_color=WHITE,
            fill_opacity=0.1,
        )
        plane.rotate(90 * DEGREES, RIGHT)
        plane.match_width(axes.x_axis)
        plane.match_depth(axes.z_axis, stretch=True)
        plane.move_to(axes.c2p(0, 0, 0), LEFT)

        self.add(plane, cos_graph)
        self.play(
            ApplyMethod(
                t_tracker.set_value, 10,
                run_time=10,
                rate_func=linear,
            ),
            ApplyMethod(
                plane.shift, 10 * UP,
                run_time=10,
                rate_func=linear,
            ),
            VFadeIn(plane),
        )
        self.wait(10)

    #
    def cos_exp(self, x, t, A=2, omega=1.5, k=0.1):
        return A * np.cos(omega * x) * np.exp(-k * (omega**2) * t)

    def get_cos_graph(self, axes, **config):
        return self.get_initial_state_graph(
            axes,
            lambda x: self.cos_exp(x, 0),
            **config
        )

    def get_cos_exp_surface(self, axes, **config):
        return self.get_surface(
            axes,
            lambda x, t: self.cos_exp(x, t),
            **config
        )


class AddMultipleSolutions(SimpleCosExpGraph):
    CONFIG = {
        "axes_config": {
            "x_axis_config": {
                "unit_size": 0.7,
            },
        }
    }

    def construct(self):
        axes1, axes2, axes3 = all_axes = VGroup(*[
            self.get_three_d_axes(
                include_labels=False,
            )
            for x in range(3)
        ])
        all_axes.scale(0.5)
        self.orient_three_d_mobject(all_axes)

        As = [1.5, 1.5]
        omegas = [1.5, 2.5]
        ks = [0.1, 0.1]
        quads = [
            (axes1, [As[0]], [omegas[0]], [ks[0]]),
            (axes2, [As[1]], [omegas[1]], [ks[1]]),
            (axes3, As, omegas, ks),
        ]

        for axes, As, omegas, ks in quads:
            graph = self.get_initial_state_graph(
                axes,
                lambda x: np.sum([
                    self.cos_exp(x, 0, A, omega, k)
                    for A, omega, k in zip(As, omegas, ks)
                ])
            )
            surface = self.get_surface(
                axes,
                lambda x, t: np.sum([
                    self.cos_exp(x, t, A, omega, k)
                    for A, omega, k in zip(As, omegas, ks)
                ])
            )
            surface.sort(lambda p: -p[2])

            axes.add(surface, graph)
            axes.graph = graph
            axes.surface = surface

        self.set_camera_orientation(distance=100)
        plus = TexMobject("+").scale(2)
        equals = TexMobject("=").scale(2)
        group = VGroup(
            axes1, plus, axes2, equals, axes3,
        )
        group.arrange(RIGHT, buff=SMALL_BUFF)

        for axes in all_axes:
            checkmark = TexMobject("\\checkmark")
            checkmark.set_color(GREEN)
            checkmark.scale(2)
            checkmark.next_to(axes, UP)
            checkmark.shift(0.7 * DOWN)
            axes.checkmark = checkmark

        self.add(axes1, axes2)
        self.play(
            LaggedStart(
                Write(axes1.surface),
                Write(axes2.surface),
            ),
            LaggedStart(
                FadeInFrom(axes1.checkmark, DOWN),
                FadeInFrom(axes2.checkmark, DOWN),
            ),
            lag_ratio=0.2,
            run_time=1,
        )
        self.wait()
        self.play(Write(plus))
        self.play(
            Transform(
                axes1.copy().set_fill(opacity=0),
                axes3
            ),
            Transform(
                axes2.copy().set_fill(opacity=0),
                axes3
            ),
            FadeInFrom(equals, LEFT)
        )
        self.play(
            FadeInFrom(axes3.checkmark, DOWN),
        )
        self.wait()


class BreakDownAFunction(SimpleCosExpGraph):
    CONFIG = {
        "axes_config": {
            "z_axis_config": {
                "unit_size": 0.75,
                "include_tip": False,
            },
            "z_min": -2,
            "y_max": 20,
        },
        "n_low_axes": 4,
        "k": 0.2,
    }

    def construct(self):
        self.set_camera_orientation(distance=100)
        self.set_axes()
        self.setup_graphs()
        self.show_break_down()
        self.show_solutions_for_waves()

    def set_axes(self):
        top_axes = self.get_three_d_axes()
        top_axes.z_axis.label.next_to(
            top_axes.z_axis.get_end(), OUT, SMALL_BUFF
        )
        top_axes.y_axis.set_opacity(0)
        self.orient_three_d_mobject(top_axes)
        top_axes.y_axis.label.rotate(-10 * DEGREES, UP)
        top_axes.scale(0.75)
        top_axes.center()
        top_axes.to_edge(UP)

        low_axes = self.get_three_d_axes(
            z_min=-3,
            z_axis_config={"unit_size": 1}
        )
        low_axes.y_axis.set_opacity(0)
        for axis in low_axes:
            axis.label.fade(1)
        # low_axes.add(low_axes.input_plane)
        # low_axes.input_plane.set_opacity(0)

        self.orient_three_d_mobject(low_axes)
        low_axes_group = VGroup(*[
            low_axes.deepcopy()
            for x in range(self.n_low_axes)
        ])
        low_axes_group.arrange(
            RIGHT, buff=low_axes.get_width() / 3
        )
        low_axes_group.set_width(FRAME_WIDTH - 2.5)
        low_axes_group.next_to(top_axes, DOWN, LARGE_BUFF)
        low_axes_group.to_edge(LEFT)

        self.top_axes = top_axes
        self.low_axes_group = low_axes_group

    def setup_graphs(self):
        top_axes = self.top_axes
        low_axes_group = self.low_axes_group

        top_graph = self.get_initial_state_graph(
            top_axes,
            self.initial_func,
            discontinuities=self.get_initial_func_discontinuities(),
            color=YELLOW,
        )
        top_graph.set_stroke(width=4)

        fourier_terms = self.get_fourier_cosine_terms(
            self.initial_func
        )

        low_graphs = VGroup(*[
            self.get_initial_state_graph(
                axes,
                lambda x: A * np.cos(n * x / 2)
            )
            for n, axes, A in zip(
                it.count(),
                low_axes_group,
                fourier_terms
            )
        ])
        k = self.k
        low_surfaces = VGroup(*[
            self.get_surface(
                axes,
                lambda x, t: np.prod([
                    A,
                    np.cos(n * x / 2),
                    np.exp(-k * (n / 2)**2 * t)
                ])
            )
            for n, axes, A in zip(
                it.count(),
                low_axes_group,
                fourier_terms
            )
        ])
        top_surface = self.get_surface(
            top_axes,
            lambda x, t: np.sum([
                np.prod([
                    A,
                    np.cos(n * x / 2),
                    np.exp(-k * (n / 2)**2 * t)
                ])
                for n, A in zip(
                    it.count(),
                    fourier_terms
                )
            ])
        )

        self.top_graph = top_graph
        self.low_graphs = low_graphs
        self.low_surfaces = low_surfaces
        self.top_surface = top_surface

    def show_break_down(self):
        top_axes = self.top_axes
        low_axes_group = self.low_axes_group
        top_graph = self.top_graph
        low_graphs = self.low_graphs

        plusses = VGroup(*[
            TexMobject("+").next_to(
                axes.x_axis.get_end(),
                RIGHT, MED_SMALL_BUFF
            )
            for axes in low_axes_group
        ])
        dots = TexMobject("\\cdots")
        dots.next_to(plusses, RIGHT, MED_SMALL_BUFF)

        arrow = Arrow(
            dots.get_right(),
            top_graph.get_end() + 1.4 * DOWN + 1.7 * RIGHT,
            path_arc=90 * DEGREES,
        )

        top_words = TextMobject("Arbitrary\\\\function")
        top_words.next_to(top_axes, LEFT, MED_LARGE_BUFF)
        top_words.set_color(YELLOW)
        top_arrow = Arrow(
            top_words.get_right(),
            top_graph.point_from_proportion(0.3)
        )

        low_words = TextMobject("Sine curves")
        low_words.set_color(BLUE)
        low_words.next_to(low_axes_group, DOWN, MED_LARGE_BUFF)

        self.add(top_axes)
        self.play(ShowCreation(top_graph))
        self.play(
            FadeInFrom(top_words, RIGHT),
            ShowCreation(top_arrow)
        )
        self.wait()
        self.play(
            LaggedStartMap(FadeIn, low_axes_group),
            FadeInFrom(low_words, UP),
            LaggedStartMap(FadeInFromDown, [*plusses, dots]),
            *[
                TransformFromCopy(top_graph, low_graph)
                for low_graph in low_graphs
            ],
        )
        self.play(ShowCreation(arrow))
        self.wait()

    def show_solutions_for_waves(self):
        low_axes_group = self.low_axes_group
        top_axes = self.top_axes
        low_graphs = self.low_graphs
        low_surfaces = self.low_surfaces
        top_surface = self.top_surface
        top_graph = self.top_graph

        for surface in [top_surface, *low_surfaces]:
            surface.sort(lambda p: -p[2])

        anims1 = []
        anims2 = [
            ApplyMethod(
                top_axes.y_axis.set_opacity, 1,
            ),
        ]
        for axes, surface, graph in zip(low_axes_group, low_surfaces, low_graphs):
            axes.y_axis.set_opacity(1)
            axes.y_axis.label.fade(1)
            anims1 += [
                ShowCreation(axes.y_axis),
                Write(surface, run_time=2),
            ]
            anims2.append(AnimationGroup(
                TransformFromCopy(graph, top_graph.copy()),
                Transform(
                    surface.copy().set_fill(opacity=0),
                    top_surface,
                )
            ))

        self.play(*anims1)
        self.wait()
        self.play(LaggedStart(*anims2, run_time=2))
        self.wait()

        checkmark = TexMobject("\\checkmark")
        checkmark.set_color(GREEN)
        low_checkmarks = VGroup(*[
            checkmark.copy().next_to(
                surface.get_top(), UP, SMALL_BUFF
            )
            for surface in low_surfaces
        ])
        top_checkmark = checkmark.copy()
        top_checkmark.scale(1.5)
        top_checkmark.move_to(top_axes.get_corner(UR))

        self.play(LaggedStartMap(FadeInFromDown, low_checkmarks))
        self.wait()
        self.play(*[
            TransformFromCopy(low_checkmark, top_checkmark.copy())
            for low_checkmark in low_checkmarks
        ])
        self.wait()

    #
    def initial_func(self, x):
        # return 3 * np.exp(-(x - PI)**2)

        x1 = TAU / 4 - 1
        x2 = TAU / 4 + 1
        x3 = 3 * TAU / 4 - 1.6
        x4 = 3 * TAU / 4 + 0.3

        T0 = -2
        T1 = 2
        T2 = 1

        if x < x1:
            return T0
        elif x < x2:
            alpha = inverse_interpolate(x1, x2, x)
            return bezier([T0, T0, T1, T1])(alpha)
        elif x < x3:
            return T1
        elif x < x4:
            alpha = inverse_interpolate(x3, x4, x)
            return bezier([T1, T1, T2, T2])(alpha)
        else:
            return T2

    def get_initial_func_discontinuities(self):
        # return [TAU / 4, 3 * TAU / 4]
        return []

    def get_fourier_cosine_terms(self, func, n_terms=40):
        result = [
            integrate.quad(
                lambda x: (1 / PI) * func(x) * np.cos(n * x / 2),
                0, TAU
            )[0]
            for n in range(n_terms)
        ]
        result[0] = result[0] / 2
        return result


class OceanOfPossibilities(TemperatureGraphScene):
    CONFIG = {
        "axes_config": {
            "z_min": 0,
            "z_max": 4,
        },
        "k": 0.2,
        "default_surface_config": {
            # "resolution": (32, 20),
            # "resolution": (8, 5),
        }
    }

    def construct(self):
        self.setup_camera()
        self.setup_axes()
        self.setup_surface()
        self.show_solution()
        self.reference_boundary_conditions()
        self.reference_initial_condition()
        self.ambiently_change_solution()

    def setup_camera(self):
        self.set_camera_orientation(
            phi=80 * DEGREES,
            theta=-80 * DEGREES,
        )
        self.begin_ambient_camera_rotation(rate=0.01)

    def setup_axes(self):
        axes = self.get_three_d_axes(include_numbers=True)
        axes.add(axes.input_plane)
        axes.scale(0.8)
        axes.center()
        axes.shift(OUT + RIGHT)

        self.add(axes)
        self.axes = axes

    def setup_surface(self):
        axes = self.axes
        k = self.k

        # Parameters for surface function
        initial_As = [2] + [
            0.8 * random.choice([-1, 1]) / n
            for n in range(1, 20)
        ]
        A_trackers = Group(*[
            ValueTracker(A)
            for A in initial_As
        ])

        def get_As():
            return [At.get_value() for At in A_trackers]

        omegas = [n / 2 for n in range(0, 10)]

        def func(x, t):
            return np.sum([
                np.prod([
                    A * np.cos(omega * x),
                    np.exp(-k * omega**2 * t)
                ])
                for A, omega in zip(get_As(), omegas)
            ])

        # Surface and graph
        surface = always_redraw(
            lambda: self.get_surface(axes, func)
        )
        t_tracker = ValueTracker(0)
        graph = always_redraw(
            lambda: self.get_time_slice_graph(
                axes, func, t_tracker.get_value(),
            )
        )

        surface.suspend_updating()
        graph.suspend_updating()

        self.surface_func = func
        self.surface = surface
        self.graph = graph
        self.t_tracker = t_tracker
        self.A_trackers = A_trackers
        self.omegas = omegas

    def show_solution(self):
        axes = self.axes
        surface = self.surface
        graph = self.graph
        t_tracker = self.t_tracker
        get_t = t_tracker.get_value

        opacity_tracker = ValueTracker(0)
        plane = always_redraw(lambda: Polygon(
            *[
                axes.c2p(x, get_t(), T)
                for x, T in [
                    (0, 0), (TAU, 0), (TAU, 4), (0, 4)
                ]
            ],
            stroke_width=0,
            fill_color=WHITE,
            fill_opacity=opacity_tracker.get_value(),
        ))

        self.add(surface, plane, graph)
        graph.resume_updating()
        self.play(
            opacity_tracker.set_value, 0.2,
            ApplyMethod(
                t_tracker.set_value, 1,
                rate_func=linear
            ),
            run_time=1
        )
        self.play(
            ApplyMethod(
                t_tracker.set_value, 10,
                rate_func=linear,
                run_time=9
            )
        )
        self.wait()

        self.plane = plane

    def reference_boundary_conditions(self):
        axes = self.axes
        t_numbers = axes.y_axis.numbers

        lines = VGroup(*[
            Line(
                axes.c2p(x, 0, 0),
                axes.c2p(x, axes.y_max, 0),
                stroke_width=3,
                stroke_color=MAROON_B,
            )
            for x in [0, axes.x_max]
        ])
        surface_boundary_lines = always_redraw(lambda: VGroup(*[
            ParametricFunction(
                lambda t: axes.c2p(
                    x, t,
                    self.surface_func(x, t)
                ),
                t_max=axes.y_max
            ).match_style(self.graph)
            for x in [0, axes.x_max]
        ]))
        # surface_boundary_lines.suspend_updating()
        words = VGroup()
        for line in lines:
            word = TextMobject("Boundary")
            word.set_stroke(BLACK, 3, background=True)
            word.scale(1.5)
            word.match_color(line)
            word.rotate(90 * DEGREES, RIGHT)
            word.rotate(90 * DEGREES, OUT)
            word.next_to(line, OUT, SMALL_BUFF)
            words.add(word)

        self.stop_ambient_camera_rotation()
        self.move_camera(
            theta=-45 * DEGREES,
            added_anims=[
                LaggedStartMap(ShowCreation, lines),
                LaggedStartMap(
                    FadeInFrom, words,
                    lambda m: (m, IN)
                ),
                FadeOut(t_numbers),
            ]
        )
        self.play(
            LaggedStart(*[
                TransformFromCopy(l1, l2)
                for l1, l2 in zip(lines, surface_boundary_lines)
            ])
        )
        self.add(surface_boundary_lines)
        self.wait()
        self.move_camera(
            theta=-70 * DEGREES,
        )

        self.surface_boundary_lines = surface_boundary_lines

    def reference_initial_condition(self):
        plane = self.plane
        t_tracker = self.t_tracker

        self.play(
            t_tracker.set_value, 0,
            run_time=2
        )
        plane.clear_updaters()
        self.play(FadeOut(plane))

    def ambiently_change_solution(self):
        A_trackers = self.A_trackers

        def generate_A_updater(A, rate):
            def update(m, dt):
                m.total_time += dt
                m.set_value(
                    2 * A * np.sin(rate * m.total_time + PI / 6)
                )
            return update

        rates = [0, 0.2] + [
            0.5 + 0.5 * np.random.random()
            for x in range(len(A_trackers) - 2)
        ]

        for tracker, rate in zip(A_trackers, rates):
            tracker.total_time = 0
            tracker.add_updater(generate_A_updater(
                tracker.get_value(),
                rate
            ))

        self.add(*A_trackers)
        self.surface_boundary_lines.resume_updating()
        self.surface.resume_updating()
        self.graph.resume_updating()
        self.begin_ambient_camera_rotation(rate=0.01)
        self.wait(30)


class AnalyzeSineCurve(TemperatureGraphScene):
    CONFIG = {
        "origin_point": 3 * LEFT,
        "axes_config": {
            "z_min": -1.5,
            "z_max": 1.5,
            "z_axis_config": {
                "unit_size": 2,
                "tick_frequency": 0.5,
            }
        },
        "tex_to_color_map": {
            "{x}": GREEN,
            "T": YELLOW,
            "=": WHITE,
            "0": WHITE,
            "\\Delta t": WHITE,
            "\\sin": WHITE,
            "{t}": PINK,
        }
    }

    def construct(self):
        self.setup_axes()
        self.ask_about_sine_curve()
        self.show_sine_wave_on_axes()
        self.reference_curvature()
        self.show_derivatives()
        self.show_curvature_matching_height()
        self.show_time_step_scalings()
        self.smooth_evolution()

    def setup_axes(self):
        axes = self.get_three_d_axes()
        axes.rotate(90 * DEGREES, LEFT)
        axes.shift(self.origin_point - axes.c2p(0, 0, 0))
        y_axis = axes.y_axis
        y_axis.fade(1)
        z_axis = axes.z_axis
        z_axis.label.next_to(z_axis.get_end(), UP, SMALL_BUFF)

        self.add_axes_numbers(axes)
        y_axis.remove(y_axis.numbers)
        axes.z_axis.add_numbers(
            *range(-1, 2),
            direction=LEFT,
        )

        self.axes = axes

    def ask_about_sine_curve(self):
        curve = FunctionGraph(
            lambda t: np.sin(t),
            x_min=0,
            x_max=TAU,
        )
        curve.move_to(DR)
        curve.set_width(5)
        curve.set_color(YELLOW)
        question = TextMobject("What's so special?")
        question.scale(1.5)
        question.to_edge(UP)
        question.shift(2 * LEFT)
        arrow = Arrow(
            question.get_bottom(),
            curve.point_from_proportion(0.25)
        )

        self.play(
            ShowCreation(curve),
            Write(question, run_time=1),
            GrowArrow(arrow),
        )
        self.wait()

        self.quick_sine_curve = curve
        self.question_group = VGroup(question, arrow)

    def show_sine_wave_on_axes(self):
        axes = self.axes
        graph = self.get_initial_state_graph(
            axes, lambda x: np.sin(x)
        )
        graph.set_stroke(width=4)
        graph_label = TexMobject(
            "T({x}, 0) = \\sin\\left({x}\\right)",
            tex_to_color_map=self.tex_to_color_map,
        )
        graph_label.next_to(
            graph.point_from_proportion(0.25), UR,
            buff=SMALL_BUFF,
        )

        v_line, x_tracker = self.get_v_line_with_x_tracker(graph)

        xs = VGroup(
            *graph_label.get_parts_by_tex("x"),
            axes.x_axis.label,
        )

        self.play(
            Write(axes),
            self.quick_sine_curve.become, graph,
            FadeOutAndShift(self.question_group, UP),
        )
        self.play(
            FadeInFromDown(graph_label),
            FadeIn(graph),
        )
        self.remove(self.quick_sine_curve)
        self.add(v_line)
        self.play(
            ApplyMethod(
                x_tracker.set_value, TAU,
                rate_func=lambda t: smooth(t, 3),
                run_time=5,
            ),
            LaggedStartMap(
                ShowCreationThenFadeAround, xs,
                run_time=3,
                lag_ratio=0.2,
            )
        )
        self.remove(v_line, x_tracker)
        self.wait()

        self.graph = graph
        self.graph_label = graph_label
        self.v_line = v_line
        self.x_tracker = x_tracker

    def reference_curvature(self):
        curve_segment, curve_x_tracker = \
            self.get_curve_segment_with_x_tracker(self.graph)

        self.add(curve_segment)
        self.play(
            curve_x_tracker.set_value, TAU,
            run_time=5,
            rate_func=lambda t: smooth(t, 3),
        )
        self.play(FadeOut(curve_segment))

        self.curve_segment = curve_segment
        self.curve_x_tracker = curve_x_tracker

    def show_derivatives(self):
        deriv1 = TexMobject(
            "{\\partial T \\over \\partial {x}}({x}, 0)",
            "= \\cos\\left({x}\\right)",
            tex_to_color_map=self.tex_to_color_map,
        )
        deriv2 = TexMobject(
            "{\\partial^2 T \\over \\partial {x}^2}({x}, 0)",
            "= -\\sin\\left({x}\\right)",
            tex_to_color_map=self.tex_to_color_map,
        )

        deriv1.to_corner(UR)
        deriv2.next_to(
            deriv1, DOWN,
            buff=0.75,
            aligned_edge=LEFT,
        )
        VGroup(deriv1, deriv2).shift(1.4 * RIGHT)

        self.play(
            Animation(Group(*self.get_mobjects())),
            FadeInFrom(deriv1, LEFT),
            self.camera.frame_center.shift, 2 * RIGHT,
        )
        self.wait()
        self.play(
            FadeInFrom(deriv2, UP)
        )
        self.wait()

        self.deriv1 = deriv1
        self.deriv2 = deriv2

    def show_curvature_matching_height(self):
        axes = self.axes
        graph = self.graph
        curve_segment = self.curve_segment
        curve_x_tracker = self.curve_x_tracker

        d2_graph = self.get_initial_state_graph(
            axes, lambda x: -np.sin(x),
        )
        dashed_d2_graph = DashedVMobject(d2_graph, num_dashes=50)
        dashed_d2_graph.color_using_background_image(None)
        dashed_d2_graph.set_stroke(RED, 2)

        vector, x_tracker = self.get_v_line_with_x_tracker(
            d2_graph,
            line_creator=lambda p1, p2: Arrow(
                p1, p2, color=RED, buff=0
            )
        )

        lil_vectors = self.get_many_lil_vectors(graph)
        lil_vector = always_redraw(
            lambda: self.get_lil_vector(
                graph, x_tracker.get_value()
            )
        )

        d2_rect = SurroundingRectangle(
            self.deriv2[-5:],
            color=RED,
        )
        self.play(ShowCreation(d2_rect))
        self.add(vector)
        self.add(lil_vector)
        self.add(curve_segment)
        curve_x_tracker.set_value(0)
        self.play(
            ShowCreation(dashed_d2_graph),
            x_tracker.set_value, TAU,
            curve_x_tracker.set_value, TAU,
            ShowIncreasingSubsets(lil_vectors[1:]),
            run_time=8,
            rate_func=linear,
        )
        self.remove(vector)
        self.remove(lil_vector)
        self.add(lil_vectors)
        self.play(
            FadeOut(curve_segment),
            FadeOut(d2_rect),
        )

        self.lil_vectors = lil_vectors
        self.dashed_d2_graph = dashed_d2_graph

    def show_time_step_scalings(self):
        axes = self.axes
        graph_label = self.graph_label
        dashed_d2_graph = self.dashed_d2_graph
        lil_vectors = self.lil_vectors
        graph = self.graph

        factor = 0.9

        new_label = TexMobject(
            "T({x}, \\Delta t) = c \\cdot \\sin\\left({x}\\right)",
            tex_to_color_map=self.tex_to_color_map,
        )
        final_label = TexMobject(
            "T({x}, {t}) = (\\text{something}) \\cdot \\sin\\left({x}\\right)",
            tex_to_color_map=self.tex_to_color_map,
        )
        for label in (new_label, final_label):
            label.shift(
                graph_label.get_part_by_tex("=").get_center() -
                label.get_part_by_tex("=").get_center()
            )
        final_label.shift(1.5 * LEFT)

        h_lines = VGroup(
            DashedLine(axes.c2p(0, 0, 1), axes.c2p(TAU, 0, 1)),
            DashedLine(axes.c2p(0, 0, -1), axes.c2p(TAU, 0, -1)),
        )

        lil_vectors.add_updater(lambda m: m.become(
            self.get_many_lil_vectors(graph)
        ))

        i = 4
        self.play(
            ReplacementTransform(
                graph_label[:i], new_label[:i],
            ),
            ReplacementTransform(
                graph_label[i + 1:i + 3],
                new_label[i + 1:i + 3],
            ),
            FadeOutAndShift(graph_label[i], UP),
            FadeInFrom(new_label[i], DOWN),
        )
        self.play(
            ReplacementTransform(
                graph_label[i + 3:],
                new_label[i + 4:]
            ),
            FadeInFromDown(new_label[i + 3])
        )
        self.play(
            FadeOut(dashed_d2_graph),
            FadeIn(h_lines),
        )
        self.play(
            graph.stretch, factor, 1,
            h_lines.stretch, factor, 1,
        )
        self.wait()

        # Repeat
        last_coef = None
        last_exp = None
        delta_T = new_label.get_part_by_tex("\\Delta t")
        c = new_label.get_part_by_tex("c")[0]
        prefix = new_label[:4]
        prefix.generate_target()
        for x in range(5):
            coef = Integer(x + 2)
            exp = coef.copy().scale(0.7)
            coef.next_to(
                delta_T, LEFT, SMALL_BUFF,
                aligned_edge=DOWN,
            )
            exp.move_to(c.get_corner(UR), DL)
            anims1 = [FadeInFrom(coef, 0.25 * DOWN)]
            anims2 = [FadeInFrom(exp, 0.25 * DOWN)]
            if last_coef:
                anims1.append(
                    FadeOutAndShift(last_coef, 0.25 * UP)
                )
                anims2.append(
                    FadeOutAndShift(last_exp, 0.25 * UP)
                )
            last_coef = coef
            last_exp = exp
            prefix.target.next_to(coef, LEFT, SMALL_BUFF)
            prefix.target.match_y(prefix)
            anims1.append(MoveToTarget(prefix))

            self.play(*anims1)
            self.play(
                graph.stretch, factor, 1,
                h_lines.stretch, factor, 1,
                *anims2,
            )
        self.play(
            ReplacementTransform(
                new_label[:4],
                final_label[:4],
            ),
            ReplacementTransform(
                VGroup(last_coef, delta_T),
                final_label.get_part_by_tex("{t}"),
            ),
            ReplacementTransform(
                last_exp,
                final_label.get_part_by_tex("something"),
            ),
            FadeOut(new_label.get_part_by_tex("\\cdot"), UP),
            ReplacementTransform(
                new_label[-4:],
                final_label[-4:],
            ),
            ReplacementTransform(
                new_label.get_part_by_tex("="),
                final_label.get_part_by_tex("="),
            ),
            ReplacementTransform(
                new_label.get_part_by_tex(")"),
                final_label.get_part_by_tex(")"),
            ),
        )
        final_label.add_background_rectangle(opacity=1)
        self.add(final_label)
        self.wait()

        group = VGroup(graph, h_lines)
        group.add_updater(lambda m, dt: m.stretch(
            (1 - 0.1 * dt), 1
        ))
        self.add(group)
        self.wait(10)

    def smooth_evolution(self):
        pass

    #
    def get_rod(self, temp_func):
        pass

    def get_v_line_with_x_tracker(self, graph, line_creator=DashedLine):
        axes = self.axes
        x_min = axes.x_axis.p2n(graph.get_start())
        x_max = axes.x_axis.p2n(graph.get_end())
        x_tracker = ValueTracker(x_min)
        get_x = x_tracker.get_value
        v_line = always_redraw(lambda: line_creator(
            axes.c2p(get_x(), 0, 0),
            graph.point_from_proportion(
                inverse_interpolate(
                    x_min, x_max, get_x()
                )
            ),
        ))
        return v_line, x_tracker

    def get_curve_segment_with_x_tracker(self, graph, delta_x=0.5):
        axes = self.axes
        x_min = axes.x_axis.p2n(graph.get_start())
        x_max = axes.x_axis.p2n(graph.get_end())
        x_tracker = ValueTracker(x_min)
        get_x = x_tracker.get_value

        def x2a(x):
            return inverse_interpolate(x_min, x_max, x)

        curve = VMobject(
            stroke_color=WHITE,
            stroke_width=5
        )
        curve.add_updater(lambda m: m.pointwise_become_partial(
            graph,
            max(x2a(get_x() - delta_x), 0),
            min(x2a(get_x() + delta_x), 1),
        ))
        return curve, x_tracker

    def get_lil_vector(self, graph, x):
        x_axis = self.axes.x_axis
        point = graph.point_from_proportion(x / TAU)
        x_axis_point = x_axis.n2p(x_axis.p2n(point))
        return Arrow(
            point,
            interpolate(
                point, x_axis_point, 0.5,
            ),
            buff=0,
            color=RED
        )

    def get_many_lil_vectors(self, graph, n=13):
        return VGroup(*[
            self.get_lil_vector(graph, x)
            for x in np.linspace(0, TAU, n)
        ])


class SineWaveScaledByExp(TemperatureGraphScene):
    CONFIG = {
        "axes_config": {
            "z_min": -1.5,
            "z_max": 1.5,
            "z_axis_config": {
                "unit_size": 2,
                "tick_frequency": 0.5,
                "label_direction": LEFT,
            },
            "y_axis_config": {
                "label_direction": RIGHT,
            },
        },
        "k": 0.3,
    }

    def construct(self):
        self.setup_axes()
        self.setup_camera()
        self.show_sine_wave()
        self.show_decay_surface()
        self.linger_at_end()

    def setup_axes(self):
        axes = self.get_three_d_axes()

        # Add number labels
        self.add_axes_numbers(axes)
        for axis in [axes.x_axis, axes.y_axis]:
            axis.numbers.rotate(
                90 * DEGREES,
                axis=axis.get_vector(),
                about_point=axis.point_from_proportion(0.5)
            )
            axis.numbers.set_shade_in_3d(True)
        axes.z_axis.add_numbers(*range(-1, 2))
        for number in axes.z_axis.numbers:
            number.rotate(90 * DEGREES, RIGHT)

        axes.z_axis.label.next_to(
            axes.z_axis.get_end(), OUT,
        )

        # Input plane
        axes.input_plane.set_opacity(0.25)
        self.add(axes.input_plane)

        # Shift into place
        # axes.shift(5 * LEFT)
        self.axes = axes
        self.add(axes)

    def setup_camera(self):
        self.set_camera_orientation(
            phi=80 * DEGREES,
            theta=-80 * DEGREES,
            distance=50,
        )
        self.camera.set_frame_center(
            2 * RIGHT,
        )

    def show_sine_wave(self):
        time_tracker = ValueTracker(0)
        graph = always_redraw(
            lambda: self.get_time_slice_graph(
                self.axes,
                self.sin_exp,
                t=time_tracker.get_value(),
            )
        )
        graph.suspend_updating()

        graph_label = TexMobject("\\sin(x)")
        graph_label.set_color(BLUE)
        graph_label.rotate(90 * DEGREES, RIGHT)
        graph_label.next_to(
            graph.point_from_proportion(0.25),
            OUT,
            SMALL_BUFF,
        )

        self.play(
            ShowCreation(graph),
            FadeInFrom(graph_label, IN)
        )
        self.wait()
        graph.resume_updating()

        self.time_tracker = time_tracker
        self.graph = graph

    def show_decay_surface(self):
        time_tracker = self.time_tracker
        axes = self.axes

        plane = Rectangle()
        plane.rotate(90 * DEGREES, RIGHT)
        plane.set_stroke(width=0)
        plane.set_fill(WHITE, 0.2)
        plane.match_depth(axes.z_axis)
        plane.match_width(axes.x_axis, stretch=True)
        plane.add_updater(
            lambda p: p.move_to(axes.c2p(
                0,
                time_tracker.get_value(),
                0,
            ), LEFT)
        )

        time_slices = VGroup(*[
            self.get_time_slice_graph(
                self.axes,
                self.sin_exp,
                t=t,
            )
            for t in range(0, 10)
        ])
        surface_t_tracker = ValueTracker(0)
        surface = always_redraw(
            lambda: self.get_surface(
                self.axes,
                self.sin_exp,
                v_max=surface_t_tracker.get_value(),
            ).set_stroke(opacity=0)
        )

        exp_graph = ParametricFunction(
            lambda t: axes.c2p(
                PI / 2,
                t,
                self.sin_exp(PI / 2, t)
            ),
            t_min=axes.y_min,
            t_max=axes.y_max,
        )
        exp_graph.set_stroke(RED, 3)
        exp_graph.set_shade_in_3d(True)

        exp_label = TexMobject("e^{-\\alpha t}")
        exp_label.scale(1.5)
        exp_label.set_color(RED)
        exp_label.rotate(90 * DEGREES, RIGHT)
        exp_label.rotate(90 * DEGREES, OUT)
        exp_label.next_to(
            exp_graph.point_from_proportion(0.3),
            OUT + UP,
        )

        self.move_camera(
            theta=-25 * DEGREES,
        )
        self.add(surface)
        self.add(plane)
        self.play(
            surface_t_tracker.set_value, axes.y_max,
            time_tracker.set_value, axes.y_max,
            ShowIncreasingSubsets(
                time_slices,
                int_func=np.ceil,
            ),
            run_time=5,
            rate_func=linear,
        )
        surface.clear_updaters()

        self.play(
            ShowCreation(exp_graph),
            FadeOut(plane),
            FadeInFrom(exp_label, IN),
            time_slices.set_stroke, {"width": 1},
        )

    def linger_at_end(self):
        self.wait()
        self.begin_ambient_camera_rotation(rate=-0.02)
        self.wait(20)

    #
    def sin_exp(self, x, t):
        return np.sin(x) * np.exp(-self.k * t)


class BoundaryConditionReference(ShowEvolvingTempGraphWithArrows):
    def construct(self):
        self.setup_axes()
        self.setup_graph()

        rod = self.get_rod(0, 10)
        self.color_rod_by_graph(rod)

        boundary_points = [
            rod.get_right(),
            rod.get_left(),
        ]
        boundary_dots = VGroup(*[
            Dot(point, radius=0.2)
            for point in boundary_points
        ])
        boundary_arrows = VGroup(*[
            Vector(2 * DOWN).next_to(dot, UP)
            for dot in boundary_dots
        ])
        boundary_arrows.set_stroke(YELLOW, 10)

        words = TextMobject(
            "Different rules\\\\",
            "at the boundary",
        )
        words.scale(1.5)
        words.to_edge(UP)

        # self.add(self.axes)
        # self.add(self.graph)
        self.add(rod)
        self.play(FadeInFromDown(words))
        self.play(
            LaggedStartMap(GrowArrow, boundary_arrows),
            LaggedStartMap(GrowFromCenter, boundary_dots),
            lag_ratio=0.3,
            run_time=1,
        )
        self.wait()


class SimulateRealSineCurve(ShowEvolvingTempGraphWithArrows):
    CONFIG = {
        "axes_config": {
            "x_min": 0,
            "x_max": TAU,
            "x_axis_config": {
                "unit_size": 1.5,
                "include_tip": False,
                "tick_frequency": PI / 4,
            },
            "y_min": -1.5,
            "y_max": 1.5,
            "y_axis_config": {
                "tick_frequency": 0.5,
                "unit_size": 2,
            },
        },
        "graph_x_min": 0,
        "graph_x_max": TAU,
        "arrow_xs": np.linspace(0, TAU, 13),
        "rod_opacity": 0.5,
        "wait_time": 30,
        "alpha": 0.5,
    }

    def construct(self):
        self.add_axes()
        self.add_graph()
        self.add_clock()
        self.add_rod()
        self.add_arrows()
        self.initialize_updaters()
        self.let_play()

    def add_labels_to_axes(self):
        x_axis = self.axes.x_axis
        x_axis.add(*[
            TexMobject(tex).scale(0.5).next_to(
                x_axis.n2p(n),
                DOWN,
                buff=MED_SMALL_BUFF
            )
            for tex, n in [
                ("\\tau \\over 4", TAU / 4),
                ("\\tau \\over 2", TAU / 2),
                ("3 \\tau \\over 4", 3 * TAU / 4),
                ("\\tau", TAU),
            ]
        ])

    def add_axes(self):
        super().add_axes()
        self.add_labels_to_axes()

    def add_rod(self):
        super().add_rod()
        self.rod.set_opacity(self.rod_opacity)
        self.rod.set_stroke(width=0)

    def initial_function(self, x):
        return np.sin(x)

    def y_to_color(self, y):
        return temperature_to_color(0.8 * y)


class StraightLine3DGraph(TemperatureGraphScene):
    CONFIG = {
        "axes_config": {
            "z_min": 0,
            "z_max": 10,
            "z_axis_config": {
                'unit_size': 0.5,
            }
        },
        "c": 1.2,
    }

    def construct(self):
        axes = self.get_three_d_axes()
        axes.add(axes.input_plane)
        axes.move_to(2 * IN + UP, IN)
        surface = self.get_surface(
            axes, self.func,
        )
        initial_graph = self.get_initial_state_graph(
            axes, lambda x: self.func(x, 0)
        )

        plane = self.get_const_time_plane(axes)
        initial_graph.add_updater(
            lambda m: m.move_to(plane, IN)
        )

        self.set_camera_orientation(
            phi=80 * DEGREES,
            theta=-100 * DEGREES,
        )
        self.begin_ambient_camera_rotation()

        self.add(axes)
        self.add(initial_graph)
        self.play(
            TransformFromCopy(initial_graph, surface)
        )
        self.add(surface, initial_graph)
        self.wait()

        self.play(
            FadeIn(plane),
            ApplyMethod(
                plane.t_tracker.set_value, 10,
                rate_func=linear,
                run_time=10,
            )
        )
        self.play(FadeOut(plane))
        self.wait(15)

    def func(self, x, t):
        return self.c * x


class SimulateLinearGraph(SimulateRealSineCurve):
    CONFIG = {
        "axes_config": {
            "y_min": 0,
            "y_max": 3,
            "y_axis_config": {
                "tick_frequency": 0.5,
                "unit_size": 2,
            },
        },
        "arrow_scale_factor": 2,
        "alpha": 1,
        "wait_time": 40,
        "step_size": 0.02,
    }

    # def let_play(self):
    #     pass

    def add_labels_to_axes(self):
        pass

    def y_to_color(self, y):
        return temperature_to_color(0.8 * (y - 1.5))

    def initial_function(self, x):
        axes = self.axes
        y_max = axes.y_max
        x_max = axes.x_max
        slope = y_max / x_max
        return slope * x


class EmphasizeBoundaryPoints(SimulateLinearGraph):
    CONFIG = {
        "wait_time": 30,
    }

    def let_play(self):
        rod = self.rod
        self.graph.update(0.01)
        self.arrows.update()

        to_update = VGroup(
            self.graph,
            self.arrows,
            self.time_label,
        )
        for mob in to_update:
            mob.suspend_updating()

        dots = VGroup(
            Dot(rod.get_left()),
            Dot(rod.get_right()),
        )
        for dot in dots:
            dot.set_height(0.2)
            dot.set_color(YELLOW)

        words = TextMobject(
            "Different rules\\\\"
            "at the boundary"
        )
        words.next_to(rod, UP)

        arrows = VGroup(*[
            Arrow(
                words.get_corner(corner),
                dot.get_top(),
                path_arc=u * 60 * DEGREES,
            )
            for corner, dot, u in zip(
                [LEFT, RIGHT], dots, [1, -1]
            )
        ])

        self.add(words)
        self.play(
            LaggedStartMap(
                FadeInFromLarge, dots,
                scale_factor=5,
            ),
            LaggedStartMap(
                ShowCreation, arrows,
            ),
            lag_ratio=0.4
        )
        self.wait()

        for mob in to_update:
            mob.resume_updating()

        super().let_play()


class FlatEdgesContinuousEvolution(ShowEvolvingTempGraphWithArrows):
    CONFIG = {
        "wait_time": 30,
        "freq_amplitude_pairs": [
            (1, 0.5),
            (2, 1),
            (3, 0.5),
            (4, 0.3),
        ],
    }

    def construct(self):
        self.add_axes()
        self.add_graph()
        self.add_clock()
        self.add_rod()
        self.initialize_updaters()
        self.add_boundary_lines()
        self.let_play()

    def add_boundary_lines(self):

        lines = VGroup(*[
            Line(LEFT, RIGHT)
            for x in range(2)
        ])
        lines.set_width(1.5)
        lines.set_stroke(WHITE, 5, opacity=0.5)
        lines.add_updater(self.update_lines)

        turn_animation_into_updater(
            ShowCreation(lines, run_time=2)
        )
        self.add(lines)

    def update_lines(self, lines):
        graph = self.graph
        lines[0].move_to(graph.get_start())
        lines[1].move_to(graph.get_end())

    def initial_function(self, x):
        return ShowEvolvingTempGraphWithArrows.initial_function(self, x)


class MoreAccurateTempFlowWithArrows(ShowEvolvingTempGraphWithArrows):
    CONFIG = {
        "arrow_scale_factor": 1,
        "max_magnitude": 1,
        "freq_amplitude_pairs": [
            (1, 0.5),
            (2, 1),
            (3, 0.5),
            (4, 0.3),
        ],
    }

    def setup_axes(self):
        super().setup_axes()
        y_axis = self.axes.y_axis
        y_axis.remove(y_axis.label)


class SlopeToHeatFlow(FlatEdgesContinuousEvolution):
    CONFIG = {
        "wait_time": 20,
        "xs": [1.75, 5.25, 7.8],
        "axes_config": {
            "x_min": 0,
            "x_max": 10,
            "x_axis_config": {
                "include_tip": False,
            }
        },
        "n_arrows": 10,
        "random_seed": 1,
    }

    def construct(self):
        self.add_axes()
        self.add_graph()
        self.add_rod()
        #
        self.show_slope_labels()
        self.show_heat_flow()

    def show_slope_labels(self):
        axes = self.axes
        # axes.x_axis.add_numbers()
        graph = self.graph
        xs = self.xs

        lines = VGroup(*[
            TangentLine(
                graph,
                inverse_interpolate(
                    axes.x_min,
                    axes.x_max,
                    x
                ),
                length=2,
                stroke_opacity=0.75,
            )
            for x in xs
        ])

        slope_words = VGroup()
        for line in lines:
            slope = line.get_slope()
            word = TextMobject(
                "Slope =",
                "${:.2}$".format(slope)
            )
            if slope > 0:
                word[1].set_color(GREEN)
            else:
                word[1].set_color(RED)

            word.set_width(line.get_length())
            word.next_to(ORIGIN, UP, SMALL_BUFF)
            word.rotate(
                line.get_angle(),
                about_point=ORIGIN,
            )
            word.shift(line.get_center())
            slope_words.add(word)

        self.play(
            LaggedStartMap(ShowCreation, lines),
            LaggedStartMap(Write, slope_words),
            lag_ratio=0.5,
            run_time=1,
        )
        self.wait()

        self.lines = lines
        self.slope_words = slope_words

    def show_heat_flow(self):
        axes = self.axes
        xs = self.xs
        slope_words = self.slope_words
        tan_lines = self.lines

        slopes = map(Line.get_slope, self.lines)
        flow_rates = [-s for s in slopes]

        points = list(map(axes.x_axis.n2p, xs))
        v_lines = VGroup(*[
            Line(
                line.get_center(), point,
                stroke_width=1,
            )
            for point, line in zip(points, tan_lines)
        ])

        flow_words = VGroup(*[
            TextMobject("Heat flow").next_to(
                point, DOWN
            ).scale(0.8)
            for point in points
        ])
        flow_mobjects = VGroup(*[
            self.get_flow(x, flow_rate)
            for x, flow_rate in zip(xs, flow_rates)
        ])

        self.add(flow_mobjects)
        self.wait()
        self.play(
            LaggedStart(*[
                TransformFromCopy(
                    sw[0], fw[0]
                )
                for sw, fw in zip(slope_words, flow_words)
            ]),
            LaggedStartMap(ShowCreation, v_lines),
            lag_ratio=0.4,
            run_time=2,
        )
        self.wait(self.wait_time)

    def get_flow(self, x, flow_rate):
        return VGroup(*[
            self.get_single_flow_arrow(
                x, flow_rate,
                t_offset=to
            )
            for to in np.linspace(0, 5, self.n_arrows)
        ])

    def get_single_flow_arrow(self, x, flow_rate, t_offset):
        axes = self.axes
        point = axes.x_axis.n2p(x)

        h_shift = 0.5
        v_shift = 0.4 * np.random.random() + 0.1

        arrow = Vector(0.5 * RIGHT * np.sign(flow_rate))
        arrow.move_to(point)
        arrow.shift(v_shift * UP)
        lp = arrow.get_center() + h_shift * LEFT
        rp = arrow.get_center() + h_shift * RIGHT
        lc = self.rod_point_to_color(lp)
        rc = self.rod_point_to_color(rp)

        run_time = 3 / flow_rate
        animation = UpdateFromAlphaFunc(
            arrow,
            lambda m, a: m.move_to(
                interpolate(lp, rp, a)
            ).set_color(
                interpolate_color(lc, rc, a)
            ).set_opacity(there_and_back(a)),
            run_time=run_time,
        )
        result = cycle_animation(animation)
        animation.total_time += t_offset
        return result


class CloserLookAtStraightLine(SimulateLinearGraph):
    def construct(self):
        self.add_axes()
        self.add_graph()
        self.add_clock()
        self.add_rod()
        # self.initialize_updaters()
        #
        self.show_t_eq_0_state()
        self.show_t_gt_0_state()

    def show_t_eq_0_state(self):
        t_eq = TexMobject("t", "=", "0")
        t_eq.next_to(self.time_label, DOWN)

        circles = VGroup(*[
            Circle(
                radius=0.25,
                stroke_color=YELLOW,
            )
            for x in range(2)
        ])
        circles.add_updater(self.attach_to_endpoints)

        self.play(Write(t_eq))
        self.play(ShowCreation(circles))
        self.wait()
        self.play(FadeOut(circles))

        self.circles = circles
        self.t_eq = t_eq

    def show_t_gt_0_state(self):
        # circles = self.circles
        t_eq = self.t_eq

        t_ineq = TexMobject("t", ">", "0")
        t_ineq.move_to(t_eq)

        slope_lines = VGroup(*[
            Line(LEFT, RIGHT)
            for x in range(2)
        ])
        slope_lines.set_opacity(0.5)
        slope_lines.add_updater(self.attach_to_endpoints)

        self.remove(t_eq)
        self.add(t_ineq)

        self.initialize_updaters()
        self.run_clock(0.1)
        for mob in self.mobjects:
            mob.suspend_updating()
        self.wait()

        self.add(slope_lines)
        self.add(self.clock, self.time_label, t_ineq)
        self.play(ShowCreation(slope_lines))
        for mob in self.mobjects:
            mob.resume_updating()

        self.run_clock(self.wait_time)

    #
    def attach_to_endpoints(self, mobs):
        points = [
            self.graph.get_start(),
            self.graph.get_end(),
        ]
        for mob, point in zip(mobs, points):
            mob.move_to(point)
        return mobs


class ManipulateSinExpSurface(TemperatureGraphScene):
    CONFIG = {
        "axes_config": {
            "z_max": 1.25,
            "z_min": -1.25,
            "z_axis_config": {
                "unit_size": 2.5,
                "tick_frequency": 0.5,
            },
            "x_axis_config": {
                # "unit_size": 1.5,
                "unit_size": 1.0,
                "tick_frequency": 1,
            },
            "x_max": 10,
            "y_max": 15,
        },
        "alpha": 0.2,
        "tex_mobject_config": {
            "tex_to_color_map": {
                "{x}": GREEN,
                "{t}": YELLOW,
                "\\omega": MAROON_B,
                "^2": WHITE,
            },
        },
        "graph_config": {},
        "initial_phi": -90 * DEGREES,
        "initial_omega": 1,
    }

    def construct(self):
        self.setup_axes()
        self.add_sine_wave()
        self.shift_sine_to_cosine()
        self.show_derivatives_of_cos()
        self.show_cos_exp_surface()
        self.change_frequency()
        self.talk_through_omega()
        self.show_cos_omega_derivatives()
        self.show_rebalanced_exp()

    def setup_axes(self):
        axes = self.get_three_d_axes(include_numbers=True)
        axes.x_axis.remove(axes.x_axis.numbers)
        L = TexMobject("L")
        L.rotate(90 * DEGREES, RIGHT)
        L.next_to(axes.x_axis.get_end(), IN)
        axes.x_axis.label = L
        axes.x_axis.add(L)

        axes.shift(5 * LEFT + 0.5 * IN)
        axes.z_axis.label[0].remove(
            *axes.z_axis.label[0][1:]
        )
        axes.z_axis.label.next_to(
            axes.z_axis.get_end(), OUT
        )
        axes.z_axis.add_numbers(
            *np.arange(-1, 1.5, 0.5),
            direction=LEFT,
            number_config={
                "num_decimal_places": 1,
            }
        )
        for number in axes.z_axis.numbers:
            number.rotate(90 * DEGREES, RIGHT)

        self.set_camera_orientation(
            phi=90 * DEGREES,
            theta=-90 * DEGREES,
            distance=100,
        )

        self.add(axes)
        self.remove(axes.y_axis)
        self.axes = axes

    def add_sine_wave(self):
        self.initialize_parameter_trackers()
        graph = self.get_graph()
        sin_label = TexMobject(
            "\\sin\\left({x}\\right)",
            **self.tex_mobject_config,
        )
        sin_label.shift(2 * LEFT + 2.75 * UP)

        self.add_fixed_in_frame_mobjects(sin_label)
        graph.suspend_updating()
        self.play(
            ShowCreation(graph),
            Write(sin_label),
        )
        graph.resume_updating()
        self.wait()

        self.sin_label = sin_label
        self.graph = graph

    def shift_sine_to_cosine(self):
        graph = self.graph
        sin_label = self.sin_label

        sin_cross = Cross(sin_label)
        sin_cross.add_updater(
            lambda m: m.move_to(sin_label)
        )
        cos_label = TexMobject(
            "\\cos\\left({x}\\right)",
            **self.tex_mobject_config,
        )
        cos_label.move_to(sin_label, LEFT)
        cos_label.shift(LEFT)
        # cos_label.shift(
        #     axes.c2p(0, 0) - axes.c2p(PI / 2, 0),
        # )

        left_tangent = Line(ORIGIN, RIGHT)
        left_tangent.set_stroke(WHITE, 5)

        self.add_fixed_in_frame_mobjects(cos_label)
        self.play(
            ApplyMethod(
                self.phi_tracker.set_value, 0,
            ),
            FadeOutAndShift(sin_label, LEFT),
            FadeInFrom(cos_label, RIGHT),
            run_time=2,
        )
        left_tangent.move_to(graph.get_start(), LEFT)
        self.play(ShowCreation(left_tangent))
        self.play(FadeOut(left_tangent))

        self.cos_label = cos_label

    def show_derivatives_of_cos(self):
        cos_label = self.cos_label
        cos_exp_label = TexMobject(
            "\\cos\\left({x}\\right)",
            "e^{-\\alpha {t}}",
            **self.tex_mobject_config
        )
        cos_exp_label.move_to(cos_label, LEFT)

        ddx_group, ddx_exp_group = [
            self.get_ddx_computation_group(
                label,
                *[
                    TexMobject(
                        s + "\\left({x}\\right)" + exp,
                        **self.tex_mobject_config,
                    )
                    for s in ["-\\sin", "-\\cos"]
                ]
            )
            for label, exp in [
                (cos_label, ""),
                (cos_exp_label, "e^{-\\alpha {t}}"),
            ]
        ]

        self.add_fixed_in_frame_mobjects(ddx_group)
        self.play(FadeIn(ddx_group))
        self.wait()

        # Cos exp
        transforms = [
            ReplacementTransform(
                cos_label, cos_exp_label,
            ),
            ReplacementTransform(
                ddx_group, ddx_exp_group,
            ),
        ]
        for trans in transforms:
            trans.begin()
            self.add_fixed_in_frame_mobjects(trans.mobject)
        self.play(*transforms)
        self.add_fixed_in_frame_mobjects(
            cos_exp_label, ddx_exp_group
        )
        self.remove_fixed_in_frame_mobjects(
            cos_label,
            *[
                trans.mobject
                for trans in transforms
            ]
        )

        self.cos_exp_label = cos_exp_label
        self.ddx_exp_group = ddx_exp_group

    def show_cos_exp_surface(self):
        axes = self.axes

        surface = self.get_cos_exp_surface()
        self.add(surface)
        surface.max_t_tracker.set_value(0)
        self.move_camera(
            phi=85 * DEGREES,
            theta=-80 * DEGREES,
            added_anims=[
                ApplyMethod(
                    surface.max_t_tracker.set_value,
                    axes.y_max,
                    run_time=4,
                ),
                Write(axes.y_axis),
            ]
        )
        self.wait()

        self.surface = surface

    def change_frequency(self):
        cos_exp_label = self.cos_exp_label
        ddx_exp_group = self.ddx_exp_group
        omega_tracker = self.omega_tracker

        cos_omega = TexMobject(
            "\\cos\\left(",
            "\\omega", "\\cdot", "{x}",
            "\\right)",
            **self.tex_mobject_config
        )
        cos_omega.move_to(cos_exp_label, LEFT)

        omega = cos_omega.get_part_by_tex("\\omega")
        brace = Brace(omega, UP, buff=SMALL_BUFF)
        omega_decimal = always_redraw(
            lambda: DecimalNumber(
                omega_tracker.get_value(),
                color=omega.get_color(),
            ).next_to(brace, UP, SMALL_BUFF)
        )

        self.add_fixed_in_frame_mobjects(
            cos_omega,
            brace,
            omega_decimal,
        )
        self.play(
            self.camera.phi_tracker.set_value, 90 * DEGREES,
            self.camera.theta_tracker.set_value, -90 * DEGREES,
            FadeOut(self.surface),
            FadeOut(self.axes.y_axis),
            FadeOut(cos_exp_label),
            FadeOut(ddx_exp_group),
            FadeIn(cos_omega),
            GrowFromCenter(brace),
            FadeInFromDown(omega_decimal)
        )
        for n in [2, 6, 1, 4]:
            freq = n * PI / self.axes.x_max
            self.play(
                omega_tracker.set_value, freq,
                run_time=2
            )
            self.wait()
        self.wait()

        self.cos_omega = cos_omega
        self.omega_brace = brace

    def talk_through_omega(self):
        axes = self.axes

        x_tracker = ValueTracker(0)
        get_x = x_tracker.get_value
        v_line = always_redraw(lambda: DashedLine(
            axes.c2p(get_x(), 0, 0),
            axes.c2p(get_x(), 0, self.func(get_x(), 0)),
        ))

        x = self.cos_omega.get_part_by_tex("{x}")
        brace = Brace(x, DOWN)
        x_decimal = always_redraw(
            lambda: DecimalNumber(
                get_x(),
                color=x.get_color()
            ).next_to(brace, DOWN, SMALL_BUFF)
        )

        self.add(v_line)
        self.add_fixed_in_frame_mobjects(brace, x_decimal)
        self.play(
            x_tracker.set_value, 5,
            run_time=5,
            rate_func=linear,
        )
        self.play(
            FadeOut(v_line),
            FadeOut(brace),
            FadeOut(x_decimal),
        )
        self.remove_fixed_in_frame_mobjects(
            brace, x_decimal
        )

    def show_cos_omega_derivatives(self):
        cos_omega = self.cos_omega
        ddx_omega_group = self.get_ddx_computation_group(
            cos_omega,
            *[
                TexMobject(
                    s + "\\left(\\omega \\cdot {x}\\right)",
                    **self.tex_mobject_config,
                )
                for s in ["-\\omega \\sin", "-\\omega^2 \\cos"]
            ]
        )

        omega_squared = ddx_omega_group[-1][1:3]
        rect = SurroundingRectangle(omega_squared)

        self.add_fixed_in_frame_mobjects(ddx_omega_group)
        self.play(FadeIn(ddx_omega_group))
        self.wait()
        self.add_fixed_in_frame_mobjects(rect)
        self.play(ShowCreationThenFadeOut(rect))
        self.wait()

        self.ddx_omega_group = ddx_omega_group

    def show_rebalanced_exp(self):
        cos_omega = self.cos_omega
        ddx_omega_group = self.ddx_omega_group

        cos_exp = TexMobject(
            "\\cos\\left(",
            "\\omega", "\\cdot", "{x}",
            "\\right)",
            "e^{-\\alpha \\omega^2 {t}}",
            **self.tex_mobject_config
        )
        cos_exp.move_to(cos_omega, DL)

        self.add_fixed_in_frame_mobjects(cos_exp)
        self.play(
            FadeOut(cos_omega),
            FadeOut(ddx_omega_group),
            FadeIn(cos_exp),
        )
        self.remove_fixed_in_frame_mobjects(
            cos_omega,
            ddx_omega_group,
        )

        self.play(
            FadeIn(self.surface),
            FadeIn(self.axes.y_axis),
            VGroup(
                cos_exp,
                self.omega_brace,
            ).shift, 4 * RIGHT,
            self.camera.phi_tracker.set_value, 80 * DEGREES,
            self.camera.theta_tracker.set_value, -80 * DEGREES,
        )
        self.wait()
        self.play(
            self.omega_tracker.set_value, TAU / 10,
            run_time=6,
        )

    #
    def initialize_parameter_trackers(self):
        self.phi_tracker = ValueTracker(
            self.initial_phi
        )
        self.omega_tracker = ValueTracker(
            self.initial_omega
        )
        self.t_tracker = ValueTracker(0)

    def get_graph(self):
        return always_redraw(
            lambda: self.get_time_slice_graph(
                self.axes, self.func,
                t=self.t_tracker.get_value(),
                **self.graph_config
            )
        )

    def get_cos_exp_surface(self):
        max_t_tracker = ValueTracker(self.axes.y_max)
        surface = always_redraw(
            lambda: self.get_surface(
                self.axes,
                self.func,
                v_max=max_t_tracker.get_value(),
            )
        )
        surface.max_t_tracker = max_t_tracker
        return surface

    def func(self, x, t):
        phi = self.phi_tracker.get_value()
        omega = self.omega_tracker.get_value()
        alpha = self.alpha
        return op.mul(
            np.cos(omega * (x + phi)),
            np.exp(-alpha * (omega**2) * t)
        )

    def get_ddx_computation_group(self, f, df, ddf):
        arrows = VGroup(*[
            Vector(0.5 * RIGHT) for x in range(2)
        ])
        group = VGroup(
            arrows[0], df, arrows[1], ddf
        )
        group.arrange(RIGHT)
        group.next_to(f, RIGHT)

        for arrow in arrows:
            label = TexMobject(
                "\\partial \\over \\partial {x}",
                **self.tex_mobject_config,
            )
            label.scale(0.5)
            label.next_to(arrow, UP, SMALL_BUFF)
            arrow.add(label)

        group.arrows = arrows
        group.funcs = VGroup(df, ddf)

        return group


class ShowFreq1CosExpDecay(ManipulateSinExpSurface):
    CONFIG = {
        "freq": 1,
        "alpha": 0.2,
    }

    def construct(self):
        self.setup_axes()
        self.add_back_y_axis()
        self.initialize_parameter_trackers()
        self.phi_tracker.set_value(0)
        self.omega_tracker.set_value(
            self.freq * TAU / 10,
        )
        #
        self.show_decay()

    def add_back_y_axis(self):
        axes = self.axes
        self.add(axes.y_axis)
        self.remove(axes.y_axis.numbers)
        self.remove(axes.y_axis.label)

    def show_decay(self):
        axes = self.axes
        t_tracker = self.t_tracker
        t_max = self.axes.y_max

        graph = always_redraw(
            lambda: self.get_time_slice_graph(
                axes,
                self.func,
                t=t_tracker.get_value(),
                stroke_width=5,
            )
        )

        surface = self.get_surface(
            self.axes, self.func,
        )
        plane = self.get_const_time_plane(axes)

        self.add(surface, plane, graph)

        self.set_camera_orientation(
            phi=80 * DEGREES,
            theta=-85 * DEGREES,
        )
        self.begin_ambient_camera_rotation(rate=0.01)
        self.play(
            t_tracker.set_value, t_max,
            plane.t_tracker.set_value, t_max,
            run_time=t_max,
            rate_func=linear,
        )


class ShowFreq2CosExpDecay(ShowFreq1CosExpDecay):
    CONFIG = {
        "freq": 2,
    }


class ShowFreq4CosExpDecay(ShowFreq1CosExpDecay):
    CONFIG = {
        "freq": 4,
    }


class ShowHarmonics(SimulateRealSineCurve):
    CONFIG = {
        "rod_opacity": 0.75,
        "initial_omega": 1.27,
        "default_n_rod_pieces": 32,
    }

    def construct(self):
        self.add_axes()
        self.add_graph()
        self.add_rod()
        self.rod.add_updater(self.color_rod_by_graph)
        #
        self.show_formula()

    def add_graph(self):
        omega_tracker = ValueTracker(self.initial_omega)
        get_omega = omega_tracker.get_value
        graph = always_redraw(
            lambda: self.axes.get_graph(
                lambda x: np.cos(get_omega() * x),
                x_min=self.graph_x_min,
                x_max=self.graph_x_max,
                step_size=self.step_size,
                discontinuities=[5],
            ).color_using_background_image("VerticalTempGradient")
        )

        self.add(graph)
        self.graph = graph
        self.omega_tracker = omega_tracker

    def show_formula(self):
        rod = self.rod
        graph = self.graph
        axes = self.axes
        omega_tracker = self.omega_tracker
        L = TAU

        formula = TexMobject(
            "=", "\\cos\\left(",
            "2(\\pi / L)", "\\cdot", "{x}",
            "\\right)",
            tex_to_color_map={
                "{x}": GREEN,
            }
        )
        formula.next_to(
            self.axes.y_axis.label, RIGHT, SMALL_BUFF
        )
        omega_part = formula.get_part_by_tex("\\pi")
        omega_brace = Brace(omega_part, DOWN)
        omega = TexMobject("\\omega")
        omega.set_color(MAROON_B)
        omega.next_to(omega_brace, DOWN, SMALL_BUFF)
        formula.remove(omega_part)

        pi_over_L = TexMobject("(\\pi / L)")
        pi_over_L.move_to(omega_part)
        pi_over_L.match_color(omega)

        self.add(formula)
        self.add(omega_brace)
        self.add(omega)

        self.remove(graph)
        self.play(GrowFromEdge(rod, LEFT))
        self.play(
            ShowCreationThenFadeAround(axes.x_axis.label)
        )
        self.wait()
        self.play(FadeIn(graph))
        self.play(FadeInFromDown(pi_over_L))
        self.play(
            omega_tracker.set_value, PI / L,
            run_time=2
        )
        self.wait()

        # Show x
        x_tracker = ValueTracker(0)
        tip = ArrowTip(
            start_angle=-90 * DEGREES,
            color=WHITE,
        )
        tip.add_updater(lambda m: m.move_to(
            axes.x_axis.n2p(x_tracker.get_value()),
            DOWN,
        ))
        x_sym = TexMobject("x")
        x_sym.set_color(GREEN)
        x_sym.add_background_rectangle(buff=SMALL_BUFF)
        x_sym.add_updater(lambda m: m.next_to(tip, UP, SMALL_BUFF))

        self.play(
            Write(tip),
            Write(x_sym),
        )
        self.play(
            x_tracker.set_value, L,
            run_time=3,
        )
        self.wait()
        self.play(TransformFromCopy(
            x_sym, formula.get_part_by_tex("{x}")
        ))
        self.play(
            FadeOut(tip),
            FadeOut(x_sym),
        )

        # Harmonics
        pi_over_L.generate_target()
        n_sym = Integer(2)
        n_sym.match_color(pi_over_L)
        group = VGroup(n_sym, pi_over_L.target)
        group.arrange(RIGHT, buff=SMALL_BUFF)
        group.move_to(pi_over_L)

        self.play(
            MoveToTarget(pi_over_L),
            FadeInFromDown(n_sym),
            ApplyMethod(
                omega_tracker.set_value, 2 * PI / L,
                run_time=2,
            )
        )
        self.wait()
        for n in [*range(3, 9), 0]:
            new_n_sym = Integer(n)
            new_n_sym.move_to(n_sym, DR)
            new_n_sym.match_style(n_sym)
            self.play(
                FadeOutAndShift(n_sym, UP),
                FadeInFrom(new_n_sym, DOWN),
                omega_tracker.set_value, n * PI / L,
            )
            self.wait()
            n_sym = new_n_sym

    #
    def add_labels_to_axes(self):
        x_axis = self.axes.x_axis
        L = TexMobject("L")
        L.next_to(x_axis.get_end(), DOWN)
        x_axis.add(L)
        x_axis.label = L


class ShowHarmonicSurfaces(ManipulateSinExpSurface):
    CONFIG = {
        "alpha": 0.2,
        "initial_phi": 0,
        "initial_omega": PI / 10,
        "n_iterations": 8,
        "default_surface_config": {
            "resolution": (40, 30),
            "surface_piece_config": {
                "stroke_width": 0.5,
            }
        }
    }

    def construct(self):
        self.setup_axes()
        self.initialize_parameter_trackers()
        self.add_surface()
        self.add_graph()
        self.show_all_harmonic_surfaces()

    def setup_axes(self):
        super().setup_axes()
        self.add(self.axes.y_axis)
        self.set_camera_orientation(
            phi=82 * DEGREES,
            theta=-80 * DEGREES,
        )

    def add_surface(self):
        self.surface = self.get_cos_exp_surface()
        self.add(self.surface)

    def add_graph(self):
        self.graph = self.get_graph()
        self.add(self.graph)

    def show_all_harmonic_surfaces(self):
        omega_tracker = self.omega_tracker
        formula = self.get_formula(str(1))
        L = self.axes.x_max

        self.begin_ambient_camera_rotation(rate=0.01)
        self.add_fixed_in_frame_mobjects(formula)
        self.wait(2)
        for n in range(2, self.n_iterations):
            if n > 5:
                n_str = "n"
            else:
                n_str = str(n)
            new_formula = self.get_formula(n_str)
            self.play(
                Transform(formula, new_formula),
                ApplyMethod(
                    omega_tracker.set_value,
                    n * PI / L
                ),
            )
            self.wait(3)

    #
    def get_formula(self, n_str):
        n_str = "{" + n_str + "}"
        result = TexMobject(
            "\\cos\\left(",
            n_str, "(", "\\pi / L", ")", "{x}"
            "\\right)"
            "e^{-\\alpha (", n_str, "\\pi / L", ")^2",
            "{t}}",
            tex_to_color_map={
                "{x}": GREEN,
                "{t}": YELLOW,
                "\\pi / L": MAROON_B,
                n_str: MAROON_B,
            }
        )
        result.to_edge(UP)
        return result


class Thumbnail(ShowHarmonicSurfaces):
    CONFIG = {
        "default_surface_config": {
            "resolution": (40, 30),
            # "resolution": (10, 10),
        },
        "graph_config": {
            "stroke_width": 8,
        },
    }

    def construct(self):
        self.setup_axes()
        self.initialize_parameter_trackers()
        self.add_surface()
        self.add_graph()
        #
        self.omega_tracker.set_value(3 * PI / 10)
        self.set_camera_orientation(
            theta=-70 * DEGREES,
        )

        axes = self.axes
        for axis in [axes.y_axis, axes.z_axis]:
            axis.numbers.set_opacity(0)
            axis.remove(*axis.numbers)
        axes.x_axis.label.set_opacity(0)
        axes.z_axis.label.set_opacity(0)

        for n in range(2, 16, 2):
            new_graph = self.get_time_slice_graph(
                axes, self.func, t=n,
                **self.graph_config
            )
            new_graph.set_shade_in_3d(True)
            new_graph.set_stroke(
                width=8 / np.sqrt(n),
                # opacity=1 / n**(1 / 4),
            )
            self.add(new_graph)

        words = TextMobject(
            "Sine waves + Linearity + Fourier = Solution"
        )
        words.set_width(FRAME_WIDTH - 1)
        words.to_edge(DOWN)
        words.shift(2 * DOWN)
        self.add_fixed_in_frame_mobjects(words)

        self.camera.frame_center.shift(DOWN)
        self.update_mobjects(0)
        self.surface.set_stroke(width=0.1)
        self.surface.set_fill(opacity=0.2)
