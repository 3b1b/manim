from scipy import integrate

from manimlib.imports import *


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
        "default_surface_style": {
            "fill_opacity": 0.1,
            "checkerboard_colors": [LIGHT_GREY],
            "stroke_width": 0.5,
            "stroke_color": WHITE,
            "stroke_opacity": 0.5,
        },
    }

    def get_three_d_axes(self, include_labels=True, **kwargs):
        config = dict(self.axes_config)
        config.update(kwargs)
        axes = ThreeDAxes(**config)
        axes.set_stroke(width=2)

        # Add number labels
        # TODO?

        # Add axis labels
        if include_labels:
            x_label = TexMobject("x")
            x_label.next_to(axes.x_axis.get_right(), DOWN)
            axes.x_axis.label = x_label

            t_label = TextMobject("Time")
            t_label.rotate(90 * DEGREES, OUT)
            t_label.next_to(axes.y_axis.get_top(), DL)
            axes.y_axis.label = t_label

            temp_label = TextMobject("Temperature")
            temp_label.rotate(90 * DEGREES, RIGHT)
            temp_label.next_to(axes.z_axis.get_zenith(), RIGHT)
            axes.z_axis.label = temp_label
            for axis in axes:
                axis.add(axis.label)

        # Adjust axis orinetations
        axes.x_axis.rotate(
            90 * DEGREES, RIGHT,
            about_point=axes.c2p(0, 0, 0),
        )
        axes.y_axis.rotate(
            90 * DEGREES, UP,
            about_point=axes.c2p(0, 0, 0),
        )

        # Add xy-plane
        surface_config = {
            "u_min": 0,
            "u_max": axes.x_max,
            "v_min": 0,
            "v_max": axes.y_max,
            "resolution": (16, 10),
        }
        axes.surface_config = surface_config
        input_plane = ParametricSurface(
            lambda x, t: axes.c2p(x, t, 0),
            # lambda x, t: np.array([x, t, 0]),
            **surface_config,
        )
        input_plane.set_style(
            fill_opacity=0.5,
            fill_color=BLUE_B,
            stroke_width=0.5,
            stroke_color=WHITE,
        )

        axes.input_plane = input_plane

        return axes

    def get_time_slice_graph(self, axes, func, t, **kwargs):
        config = dict()
        config.update(self.default_graph_style)
        config.update(kwargs)
        return ParametricFunction(
            lambda x: axes.c2p(
                x, t, func(x)
            ),
            t_min=axes.x_min,
            t_max=axes.x_max,
            **config,
        )

    def get_initial_state_graph(self, axes, func, **kwargs):
        return self.get_time_slice_graph(
            axes, func, t=0, **kwargs
        )

    def get_surface(self, axes, func, **kwargs):
        config = dict()
        config.update(axes.surface_config)
        config.update(self.default_surface_style)
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
            "z_min": 0,
        },
        "n_low_axes": 4,
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

        fourier_terms = self.get_fourier_cosine_terms(
            self.initial_func
        )

        low_graphs = VGroup(*[
            self.get_initial_state_graph(
                axes,
                lambda x: A * np.cos(n * x / 2)
            )
            for n, axes, A in zip(
                it.count(0, 2),
                low_axes_group,
                fourier_terms[::2],
            )
        ])
        k = 0.1
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
                it.count(0, 2),
                low_axes_group,
                fourier_terms[::2],
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
                    it.count(0, 2),
                    fourier_terms[::2]
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
                RIGHT, MED_LARGE_BUFF
            )
            for axes in low_axes_group
        ])
        dots = TexMobject("\\cdots")
        dots.next_to(plusses, RIGHT, MED_SMALL_BUFF)
        arrow = Arrow(
            dots.get_right(),
            top_axes.get_right(),
            path_arc=110 * DEGREES,
        )

        top_words = TextMobject("Arbitrary\\\\function")
        top_words.next_to(top_axes, LEFT, MED_LARGE_BUFF)
        top_words.set_color(YELLOW)
        top_arrow = Arrow(
            top_words.get_right(),
            top_graph.get_center() + LEFT,
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
            *[
                TransformFromCopy(top_graph, low_graph)
                for low_graph in low_graphs
            ]
        )
        self.play(FadeInFrom(low_words, UP))
        self.wait()
        self.play(
            LaggedStartMap(FadeInFromDown, plusses),
            Write(dots)
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
        anims2 = []
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
                    surface.copy().fade(1),
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
        self.play(TransformFromCopy(
            low_checkmarks, VGroup(top_checkmark)
        ))
        self.wait()

    #
    def initial_func(self, x):
        return 3 * np.exp(-(x - PI)**2)

        x1 = TAU / 4 - 0.1
        x2 = TAU / 4 + 0.1
        x3 = 3 * TAU / 4 - 0.1
        x4 = 3 * TAU / 4 + 0.1

        T0 = -2
        T1 = 2

        if x < x1:
            return T0
        elif x < x2:
            return interpolate(
                T0, T1,
                inverse_interpolate(x1, x2, x)
            )
        elif x < x3:
            return T1
        elif x < x4:
            return interpolate(
                T1, T0,
                inverse_interpolate(x3, x4, x)
            )
        else:
            return T0

    def get_initial_func_discontinuities(self):
        # return [TAU / 4, 3 * TAU / 4]
        return []

    def get_fourier_cosine_terms(self, func, n_terms=20):
        result = [
            integrate.quad(
                lambda x: (1 / PI) * func(x) * np.cos(n * x / 2),
                0, TAU
            )[0]
            for n in range(n_terms)
        ]
        result[0] = result[0] / 2
        return result
