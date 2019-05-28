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

    def get_three_d_axes(self, include_labels=True):
        axes = ThreeDAxes(**self.axes_config)
        axes.set_stroke(width=2)

        # Add number labels
        # TODO?

        # Add axis labels
        if include_labels:
            x_label = TexMobject("x")
            x_label.next_to(axes.x_axis.get_right(), DOWN)
            axes.x_axis.add(x_label)

            t_label = TextMobject("Time")
            t_label.rotate(90 * DEGREES, OUT)
            t_label.next_to(axes.y_axis.get_top(), DL)
            axes.y_axis.add(t_label)

            temp_label = TextMobject("Temperature")
            temp_label.rotate(90 * DEGREES, RIGHT)
            temp_label.next_to(axes.z_axis.get_zenith(), RIGHT)
            axes.z_axis.add(temp_label)

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

    def get_initial_state_graph(self, axes, func, **kwargs):
        config = dict()
        config.update(self.default_graph_style)
        config.update(kwargs)
        return ParametricFunction(
            lambda x: axes.c2p(
                x, 0, func(x)
            ),
            t_min=axes.x_min,
            t_max=axes.x_max,
            **config,
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


class SimpleSinExpGraph(TemperatureGraphScene):
    def construct(self):
        axes = self.get_three_d_axes()
        sine_graph = self.get_sine_graph(axes)
        sine_exp_surface = self.get_sine_exp_surface(axes)

        self.set_camera_orientation(
            phi=80 * DEGREES,
            theta=-80 * DEGREES,
        )
        self.camera.frame_center.shift(3 * RIGHT)
        self.begin_ambient_camera_rotation(rate=0.01)

        self.add(axes)
        self.play(ShowCreation(sine_graph))
        self.play(UpdateFromAlphaFunc(
            sine_exp_surface,
            lambda m, a: m.become(
                self.get_sine_exp_surface(axes, v_max=a * 10)
            ),
            run_time=3
        ))
        self.wait(20)

    #
    def sin_exp(self, x, t, A=2, omega=1, k=0.25):
        return A * np.sin(omega * x) * np.exp(-k * (omega**2) * t)

    def get_sine_graph(self, axes, **config):
        return self.get_initial_state_graph(
            axes,
            lambda x: self.sin_exp(x, 0),
            **config
        )

    def get_sine_exp_surface(self, axes, **config):
        return self.get_surface(
            axes,
            lambda x, t: self.sin_exp(x, t),
            **config
        )


class AddMultipleSolutions(SimpleSinExpGraph):
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
        omegas = [1, 2]
        ks = [0.25, 0.01]
        quads = [
            (axes1, [As[0]], [omegas[0]], [ks[0]]),
            (axes2, [As[1]], [omegas[1]], [ks[1]]),
            (axes3, As, omegas, ks),
        ]

        for axes, As, omegas, ks in quads:
            graph = self.get_initial_state_graph(
                axes,
                lambda x: np.sum([
                    self.sin_exp(x, 0, A, omega, k)
                    for A, omega, k in zip(As, omegas, ks)
                ])
            )
            surface = self.get_surface(
                axes,
                lambda x, t: np.sum([
                    self.sin_exp(x, t, A, omega)
                    for A, omega in zip(As, omegas)
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
