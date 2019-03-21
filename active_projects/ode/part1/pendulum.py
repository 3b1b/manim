from big_ol_pile_of_manim_imports import *
from active_projects.ode.part1.shared_constructs import *


class Pendulum(VGroup):
    CONFIG = {
        "length": 3,
        "gravity": 9.8,
        "weight_diameter": 0.5,
        "initial_theta": 0.3,
        "omega": 0,
        "damping": 0.1,
        "top_point": 2 * UP,
        "rod_style": {
            "stroke_width": 3,
            "stroke_color": LIGHT_GREY,
            "sheen_direction": UP,
            "sheen_factor": 1,
        },
        "weight_style": {
            "stroke_width": 0,
            "fill_opacity": 1,
            "fill_color": GREY_BROWN,
            "sheen_direction": UL,
            "sheen_factor": 0.5,
            "background_stroke_color": BLACK,
            "background_stroke_width": 3,
            "background_stroke_opacity": 0.5,
        },
        "dashed_line_config": {
            "num_dashes": 25,
            "stroke_color": WHITE,
            "stroke_width": 2,
        },
        "angle_arc_config": {
            "radius": 1,
            "stroke_color": WHITE,
            "stroke_width": 2,
        },
        "velocity_vector_config": {
            "color": RED,
        },
        "theta_label_height": 0.25,
        "n_steps_per_frame": 100,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_fixed_point()
        self.create_rod()
        self.create_weight()
        self.rotating_group = VGroup(self.rod, self.weight)
        self.create_dashed_line()
        self.create_angle_arc()
        self.add_theta_label()

        self.set_theta(self.initial_theta)
        self.update()

    def create_fixed_point(self):
        self.fixed_point_tracker = VectorizedPoint(self.top_point)
        self.add(self.fixed_point_tracker)
        return self

    def create_rod(self):
        rod = self.rod = Line(UP, DOWN)
        rod.set_height(self.length)
        rod.set_style(**self.rod_style)
        rod.move_to(self.get_fixed_point(), UP)
        self.add(rod)

    def create_weight(self):
        weight = self.weight = Circle()
        weight.set_width(self.weight_diameter)
        weight.set_style(**self.weight_style)
        weight.move_to(self.rod.get_end())
        self.add(weight)

    def create_dashed_line(self):
        line = self.dashed_line = DashedLine(
            self.get_fixed_point(),
            self.get_fixed_point() + self.length * DOWN,
            **self.dashed_line_config
        )
        self.add_to_back(line)

    def create_angle_arc(self):
        self.angle_arc = always_redraw(lambda: Arc(
            arc_center=self.get_fixed_point(),
            start_angle=-90 * DEGREES,
            angle=self.get_theta(),
            **self.angle_arc_config,
        ))
        self.add(self.angle_arc)

    def add_velocity_vector(self):
        def make_vector():
            omega = self.get_omega()
            theta = self.get_theta()
            vector = Vector(
                0.5 * omega * RIGHT,
                **self.velocity_vector_config,
            )
            vector.rotate(theta, about_point=ORIGIN)
            vector.shift(self.rod.get_end())
            return vector

        self.velocity_vector = always_redraw(make_vector)
        self.add(self.velocity_vector)
        return self

    def add_theta_label(self):
        label = self.theta_label = TexMobject("\\theta")
        label.set_height(self.theta_label_height)

        def update_label(l):
            top = self.get_fixed_point()
            arc_center = self.angle_arc.point_from_proportion(0.5)
            vect = arc_center - top
            vect = normalize(vect) * (1 + self.theta_label_height)
            l.move_to(top + vect)
        label.add_updater(update_label)
        self.add(label)

    #
    def get_theta(self):
        theta = self.rod.get_angle() - self.dashed_line.get_angle()
        theta = (theta + PI) % TAU - PI
        return theta

    def set_theta(self, theta):
        self.rotating_group.rotate(
            theta - self.get_theta()
        )
        self.rotating_group.shift(
            self.get_fixed_point() - self.rod.get_start(),
        )
        return self

    def get_omega(self):
        return self.omega

    def set_omega(self, omega):
        self.omega = omega
        return self

    def get_fixed_point(self):
        return self.fixed_point_tracker.get_location()

    #
    def start_swinging(self):
        self.add_updater(Pendulum.update_by_gravity)

    def end_swinging(self):
        self.remove_updater(Pendulum.update_by_gravity)

    def update_by_gravity(self, dt):
        theta = self.get_theta()
        omega = self.get_omega()
        nspf = self.n_steps_per_frame
        for x in range(nspf):
            d_theta = omega * dt / nspf
            d_omega = op.add(
                -self.damping * omega,
                -(self.gravity / self.length) * np.sin(theta),
            ) * dt / nspf
            theta += d_theta
            omega += d_omega
        self.set_theta(theta)
        self.set_omega(omega)
        return self


class GravityVector(Vector):
    CONFIG = {
        "color": YELLOW,
        "length_multiple": 1 / 9.8,
        # TODO, continually update the length based
        # on the pendulum's gravity?
    }

    def __init__(self, pendulum, **kwargs):
        super().__init__(DOWN, **kwargs)
        self.pendulum = pendulum
        self.scale(self.length_multiple * pendulum.gravity)
        self.attach_to_pendulum(pendulum)

    def attach_to_pendulum(self, pendulum):
        self.add_updater(lambda m: m.shift(
            pendulum.weight.get_center() - self.get_start(),
        ))

    def add_component_lines(self):
        self.component_lines = always_redraw(self.create_component_lines)
        self.add(self.component_lines)

    def create_component_lines(self):
        theta = self.pendulum.get_theta()
        x_new = rotate(RIGHT, theta)
        base = self.get_start()
        tip = self.get_end()
        vect = tip - base
        corner = base + x_new * np.dot(vect, x_new)
        kw = {"dash_length": 0.025}
        return VGroup(
            DashedLine(base, corner, **kw),
            DashedLine(corner, tip, **kw),
        )


class ThetaValueDisplay(VGroup):
    CONFIG = {

    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ThetaVsTAxes(Axes):
    CONFIG = {
        "x_min": 0,
        "x_max": 8,
        "y_min": -PI / 2,
        "y_max": PI / 2,
        "y_axis_config": {
            "tick_frequency": PI / 8,
            "unit_size": 1.5,
        },
        "number_line_config": {
            "color": "#EEEEEE",
            "stroke_width": 2,
            "include_tip": False,
        },
        "graph_style": {
            "stroke_color": GREEN,
            "stroke_width": 3,
            "fill_opacity": 0,
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_labels()

    def add_axes(self):
        self.axes = Axes(**self.axes_config)
        self.add(self.axes)

    def add_labels(self):
        x_axis = self.get_x_axis()
        y_axis = self.get_y_axis()

        t_label = self.t_label = TexMobject("t")
        t_label.next_to(x_axis.get_right(), UP, MED_SMALL_BUFF)
        x_axis.label = t_label
        x_axis.add(t_label)
        theta_label = self.theta_label = TexMobject("\\theta(t)")
        theta_label.next_to(y_axis.get_top(), UP, SMALL_BUFF)
        y_axis.label = theta_label
        y_axis.add(theta_label)

        x_axis.add_numbers()
        y_axis.add(self.get_y_axis_coordinates(y_axis))

    def get_y_axis_coordinates(self, y_axis):
        texs = [
            # "\\pi \\over 4",
            # "\\pi \\over 2",
            # "3 \\pi \\over 4",
            # "\\pi",
            "\\pi / 4",
            "\\pi / 2",
            "3 \\pi / 4",
            "\\pi",
        ]
        values = np.arange(1, 5) * PI / 4
        labels = VGroup()
        for pos_tex, pos_value in zip(texs, values):
            neg_tex = "-" + pos_tex
            neg_value = -1 * pos_value
            for tex, value in (pos_tex, pos_value), (neg_tex, neg_value):
                if value > self.y_max or value < self.y_min:
                    continue
                symbol = TexMobject(tex)
                symbol.scale(0.5)
                point = y_axis.number_to_point(value)
                symbol.next_to(point, LEFT, MED_SMALL_BUFF)
                labels.add(symbol)
        return labels

    def get_live_drawn_graph(self, pendulum,
                             t_max=None,
                             t_step=1.0 / 60,
                             **style):
        style = merge_dicts_recursively(self.graph_style, style)
        if t_max is None:
            t_max = self.x_max

        graph = VMobject()
        graph.set_style(**style)

        graph.all_coords = [(0, pendulum.get_theta())]
        graph.time = 0
        graph.time_of_last_addition = 0

        def update_graph(graph, dt):
            graph.time += dt
            if graph.time > t_max:
                graph.remove_updater(update_graph)
                return
            new_coords = (graph.time, pendulum.get_theta())
            if graph.time - graph.time_of_last_addition >= t_step:
                graph.all_coords.append(new_coords)
                graph.time_of_last_addition = graph.time
            points = [
                self.coords_to_point(*coords)
                for coords in [*graph.all_coords, new_coords]
            ]
            graph.set_points_smoothly(points)

        graph.add_updater(update_graph)
        return graph


# Scenes
class IntroducePendulum(PiCreatureScene, MovingCameraScene):
    CONFIG = {
        "pendulum_config": {
            "length": 3,
            "top_point": 4 * RIGHT,
            "weight_diameter": 0.35,
        },
        "theta_vs_t_axes_config": {
            "y_max": PI / 4,
            "y_min": -PI / 4,
            "y_axis_config": {
                "tick_frequency": PI / 16,
                "unit_size": 2,
                "tip_length": 0.3,
            },
            "number_line_config": {
                "stroke_width": 2,
            }
        },
    }

    def setup(self):
        MovingCameraScene.setup(self)
        PiCreatureScene.setup(self)

    def construct(self):
        self.add_pendulum()
        self.label_pi_creatures()
        self.label_pendulum()
        self.add_graph()
        self.show_graph_period()
        self.show_length_and_gravity()
        self.tweak_length_and_gravity()

    def create_pi_creatures(self):
        randy = Randolph(color=BLUE_C)
        morty = Mortimer(color=MAROON_E)
        creatures = VGroup(randy, morty)
        creatures.scale(0.5)
        creatures.arrange(RIGHT, buff=2.5)
        creatures.to_corner(DR)
        return creatures

    def add_pendulum(self):
        pendulum = self.pendulum = Pendulum(**self.pendulum_config)
        pendulum.start_swinging()
        frame = self.camera_frame
        frame.save_state()
        frame.scale(0.5)
        frame.move_to(pendulum.dashed_line)

        self.add(pendulum, frame)

    def label_pi_creatures(self):
        randy, morty = self.pi_creatures
        randy_label = TextMobject("Physics\\\\", "student")
        morty_label = TextMobject("Physics\\\\", "teacher")
        labels = VGroup(randy_label, morty_label)
        labels.scale(0.5)
        randy_label.next_to(randy, UP, LARGE_BUFF)
        morty_label.next_to(morty, UP, LARGE_BUFF)

        for label, pi in zip(labels, self.pi_creatures):
            label.arrow = Arrow(
                label.get_bottom(), pi.eyes.get_top()
            )
            label.arrow.set_color(WHITE)
            label.arrow.set_stroke(width=5)

        morty.labels = VGroup(
            morty_label,
            morty_label.arrow,
        )

        self.play(
            FadeInFromDown(randy_label),
            GrowArrow(randy_label.arrow),
            randy.change, "hooray",
        )
        self.play(
            Animation(self.pendulum.fixed_point_tracker),
            TransformFromCopy(randy_label[0], morty_label[0]),
            FadeIn(morty_label[1]),
            GrowArrow(morty_label.arrow),
            morty.change, "raise_right_hand",
        )
        self.wait()

    def label_pendulum(self):
        pendulum = self.pendulum
        randy, morty = self.pi_creatures
        label = pendulum.theta_label
        rect = SurroundingRectangle(label, buff=0.5 * SMALL_BUFF)
        rect.add_updater(lambda r: r.move_to(label))

        self.add(rect)
        self.play(
            ShowCreationThenFadeOut(rect),
            ShowCreationThenDestruction(
                label.copy().set_style(
                    fill_opacity=0,
                    stroke_color=PINK,
                    stroke_width=2,
                )
            ),
            randy.change, "pondering",
            morty.change, "pondering",
        )
        self.wait()

    def add_graph(self):
        axes = self.axes = ThetaVsTAxes(**self.theta_vs_t_axes_config)
        axes.y_axis.label.next_to(axes.y_axis, UP, buff=0)
        axes.to_corner(UL)

        self.play(
            Restore(self.camera_frame),
            DrawBorderThenFill(
                axes,
                rate_func=squish_rate_func(smooth, 0.5, 1),
                lag_ratio=0.9,
            ),
            Transform(
                self.pendulum.theta_label.copy().clear_updaters(),
                axes.y_axis.label.copy(),
                remover=True,
                rate_func=squish_rate_func(smooth, 0, 0.8),
            ),
            run_time=3,
        )
        self.wait(2)
        self.graph = axes.get_live_drawn_graph(self.pendulum)

        self.add(self.graph)
        self.wait(4)

    def show_graph_period(self):
        pendulum = self.pendulum
        axes = self.axes

        period = self.period = TAU * np.sqrt(
            pendulum.length / pendulum.gravity
        )
        amplitude = pendulum.initial_theta

        line = Line(
            axes.coords_to_point(0, amplitude),
            axes.coords_to_point(period, amplitude),
        )
        line.shift(SMALL_BUFF * RIGHT)
        brace = Brace(line, UP, buff=SMALL_BUFF)
        brace.add_to_back(brace.copy().set_style(BLACK, 10))
        formula = TexMobject(
            "\\sqrt{\\,", "2\\pi", "L", "/", "g", "}",
            tex_to_color_map={
                "L": BLUE,
                "g": YELLOW,
            }
        )
        formula.next_to(brace, UP, SMALL_BUFF)

        self.period_formula = formula
        self.period_brace = brace

        self.play(
            GrowFromCenter(brace),
            FadeInFromDown(formula),
        )
        self.wait(2)

    def show_length_and_gravity(self):
        formula = self.period_formula
        L = formula.get_part_by_tex("L")
        g = formula.get_part_by_tex("g")

        rod = self.pendulum.rod
        new_rod = rod.copy()
        new_rod.set_stroke(BLUE, 7)
        new_rod.add_updater(lambda r: r.put_start_and_end_on(
            *rod.get_start_and_end()
        ))

        g_vect = GravityVector(
            self.pendulum,
            length_multiple=0.5 / 9.8,
        )

        self.play(ShowCreationThenDestructionAround(L))
        dot = Dot(fill_opacity=0.25)
        dot.move_to(L)
        self.play(
            ShowCreation(new_rod),
            dot.move_to, new_rod,
            dot.fade, 1,
        )
        self.remove(dot)
        self.play(FadeOut(new_rod))
        self.wait()

        self.play(ShowCreationThenDestructionAround(g))
        dot.move_to(g)
        dot.set_fill(opacity=0.5)
        self.play(
            GrowArrow(g_vect),
            dot.move_to, g_vect,
            dot.fade, 1,
        )
        self.remove(dot)
        self.wait(2)

        self.gravity_vector = g_vect

    def tweak_length_and_gravity(self):
        pendulum = self.pendulum
        axes = self.axes
        graph = self.graph
        brace = self.period_brace
        formula = self.period_formula
        g_vect = self.gravity_vector
        randy, morty = self.pi_creatures

        graph.clear_updaters()
        period2 = self.period * np.sqrt(2)
        period3 = self.period / np.sqrt(2)
        amplitude = pendulum.initial_theta
        graph2, graph3 = [
            axes.get_graph(
                lambda t: amplitude * np.cos(TAU * t / p),
                color=RED,
            )
            for p in (period2, period3)
        ]
        formula.add_updater(lambda m: m.next_to(
            brace, UP, SMALL_BUFF
        ))

        new_pendulum_config = dict(self.pendulum_config)
        new_pendulum_config["length"] *= 2
        new_pendulum_config["top_point"] += 3.5 * UP
        # new_pendulum_config["initial_theta"] = pendulum.get_theta()
        new_pendulum = Pendulum(**new_pendulum_config)

        down_vectors = VGroup(*[
            Vector(0.5 * DOWN)
            for x in range(10 * 150)
        ])
        down_vectors.arrange_in_grid(10, 150, buff=MED_SMALL_BUFF)
        down_vectors.set_color_by_gradient(BLUE, RED)
        # for vect in down_vectors:
        #     vect.shift(0.1 * np.random.random(3))
        down_vectors.to_edge(RIGHT)

        self.play(randy.change, "happy")
        self.play(
            ReplacementTransform(pendulum, new_pendulum),
            morty.change, "horrified",
            morty.shift, 3 * RIGHT,
            morty.labels.shift, 3 * RIGHT,
        )
        self.remove(morty, morty.labels)
        g_vect.attach_to_pendulum(new_pendulum)
        new_pendulum.start_swinging()
        self.play(
            ReplacementTransform(graph, graph2),
            brace.stretch, np.sqrt(2), 0, {"about_edge": LEFT},
        )
        self.add(g_vect)
        self.wait(3)

        new_pendulum.gravity *= 4
        g_vect.scale(2)
        self.play(
            FadeOut(graph2),
            LaggedStart(*[
                GrowArrow(v, rate_func=there_and_back)
                for v in down_vectors
            ], lag_ratio=0.0005, run_time=2, remover=True)
        )
        self.play(
            FadeIn(graph3),
            brace.stretch, 0.5, 0, {"about_edge": LEFT},
        )
        self.wait(6)


class MultiplePendulumsOverlayed(Scene):
    CONFIG = {
        "initial_thetas": [
            150 * DEGREES,
            90 * DEGREES,
            60 * DEGREES,
            30 * DEGREES,
            10 * DEGREES,
        ],
        "weight_colors": [
            PINK, RED, GREEN, BLUE, GREY,
        ],
        "pendulum_config": {
            "top_point": ORIGIN,
            "length": 3,
        },
    }

    def construct(self):
        pendulums = VGroup(*[
            Pendulum(
                initial_theta=theta,
                weight_style={
                    "fill_color": wc,
                    "fill_opacity": 0.5,
                },
                **self.pendulum_config,
            )
            for theta, wc in zip(
                self.initial_thetas,
                self.weight_colors,
            )
        ])
        for pendulum in pendulums:
            pendulum.start_swinging()
            pendulum.remove(pendulum.theta_label)

        randy = Randolph(color=BLUE_C)
        randy.to_corner(DL)
        randy.add_updater(lambda r: r.look_at(pendulums[0].weight))

        axes = ThetaVsTAxes(
            x_max=20,
            y_axis_config={
                "unit_size": 0.5,
                "tip_length": 0.3,
            },
        )
        axes.to_corner(UL)
        graphs = VGroup(*[
            axes.get_live_drawn_graph(
                pendulum,
                stroke_color=pendulum.weight.get_color(),
                stroke_width=1,
            )
            for pendulum in pendulums
        ])

        self.add(pendulums)
        self.add(axes, *graphs)
        self.play(randy.change, "sassy")
        self.wait(2)
        self.play(Blink(randy))
        self.wait(5)
        self.play(randy.change, "angry")
        self.play(Blink(randy))
        self.wait(10)


class LowAnglePendulum(Scene):
    CONFIG = {
        "pendulum_config": {
            "initial_theta": 20 * DEGREES,
            "length": 2.0,
            "damping": 0,
            "top_point": ORIGIN,
        },
        "axes_config": {
            "y_axis_config": {"unit_size": 0.75},
            "x_axis_config": {
                "unit_size": 0.5,
                "numbers_to_show": range(2, 25, 2),
                "number_scale_val": 0.5,
            },
            "x_max": 25,
            "number_line_config": {
                "tip_length": 0.3,
                "stroke_width": 2,
            }
        },
        "axes_corner": UL,
    }

    def construct(self):
        pendulum = Pendulum(**self.pendulum_config)
        axes = ThetaVsTAxes(**self.axes_config)
        axes.center()
        axes.to_corner(self.axes_corner, buff=LARGE_BUFF)
        graph = axes.get_live_drawn_graph(pendulum)

        L = pendulum.length
        g = pendulum.gravity
        theta0 = pendulum.initial_theta
        prediction = axes.get_graph(
            lambda t: theta0 * np.cos(t * np.sqrt(g / L))
        )
        dashed_prediction = DashedVMobject(prediction, num_dashes=300)
        dashed_prediction.set_stroke(WHITE, 1)
        prediction_formula = TexMobject(
            "\\theta_0", "\\cos(\\sqrt{g / L} \\cdot t)"
        )
        prediction_formula.scale(0.75)
        prediction_formula.next_to(
            dashed_prediction, UP, SMALL_BUFF,
        )

        theta0 = prediction_formula.get_part_by_tex("\\theta_0")
        theta0_brace = Brace(theta0, UP, buff=SMALL_BUFF)
        theta0_brace.stretch(0.5, 1, about_edge=DOWN)
        theta0_label = Integer(
            pendulum.initial_theta * 180 / PI,
            unit="^\\circ"
        )
        theta0_label.scale(0.75)
        theta0_label.next_to(theta0_brace, UP, SMALL_BUFF)

        group = VGroup(theta0_brace, theta0_label, prediction_formula)
        group.shift_onto_screen(buff=MED_SMALL_BUFF)

        self.add(axes, dashed_prediction, pendulum)
        self.play(
            ShowCreation(dashed_prediction, run_time=2),
            FadeInFromDown(prediction_formula),
            FadeInFromDown(theta0_brace),
            FadeInFromDown(theta0_label),
        )
        self.play(
            ShowCreationThenFadeAround(theta0_label),
            ShowCreationThenFadeAround(pendulum.theta_label),
        )
        self.wait()

        pendulum.start_swinging()
        self.add(graph)
        self.wait(30)


class ApproxWordsLowAnglePendulum(Scene):
    def construct(self):
        period = TexMobject(
            "\\text{Period}", "\\approx",
            "2\\pi \\sqrt{\\,{L} / {g}}",
            **Lg_formula_config
        )
        checkmark = TexMobject("\\checkmark")
        checkmark.set_color(GREEN)
        checkmark.scale(2)
        checkmark.next_to(period, RIGHT, MED_LARGE_BUFF)

        self.add(period, checkmark)


class MediumAnglePendulum(LowAnglePendulum):
    CONFIG = {
        "pendulum_config": {
            "initial_theta": 50 * DEGREES,
            "n_steps_per_frame": 1000,
        },
        "axes_config": {
            "y_axis_config": {"unit_size": 0.75},
            "y_max": PI / 2,
            "y_min": -PI / 2,
            "number_line_config": {
                "tip_length": 0.3,
                "stroke_width": 2,
            }
        },
        "pendulum_shift_vect": 1 * RIGHT,
    }


class MediumHighAnglePendulum(MediumAnglePendulum):
    CONFIG = {
        "pendulum_config": {
            "initial_theta": 90 * DEGREES,
            "n_steps_per_frame": 1000,
        },
    }


class HighAnglePendulum(LowAnglePendulum):
    CONFIG = {
        "pendulum_config": {
            "initial_theta": 175 * DEGREES,
            "n_steps_per_frame": 1000,
            "top_point": 1.5 * DOWN,
            "length": 2,
        },
        "axes_config": {
            "y_axis_config": {"unit_size": 0.5},
            "y_max": PI,
            "y_min": -PI,
            "number_line_config": {
                "tip_length": 0.3,
                "stroke_width": 2,
            }
        },
        "pendulum_shift_vect": 1 * RIGHT,
    }


class VeryLowAnglePendulum(LowAnglePendulum):
    CONFIG = {
        "pendulum_config": {
            "initial_theta": 10 * DEGREES,
            "n_steps_per_frame": 1000,
            "top_point": ORIGIN,
            "length": 3,
        },
        "axes_config": {
            "y_axis_config": {"unit_size": 2},
            "y_max": PI / 4,
            "y_min": -PI / 4,
            "number_line_config": {
                "tip_length": 0.3,
                "stroke_width": 2,
            }
        },
        "pendulum_shift_vect": 1 * RIGHT,
    }


class BuildUpEquation(MovingCameraScene):
    CONFIG = {
        "pendulum_config": {
            "length": 5,
            "top_point": 3 * UP,
            "initial_theta": 45 * DEGREES,
        },
        "g_vect_config": {
            "length_multiple": 0.25,
        },
        "tan_line_color": BLUE,
        "perp_line_color": PINK,
    }

    def construct(self):
        self.add_pendulum()
        self.show_constraint()
        self.break_g_vect_into_components()
        self.show_angle_geometry()
        self.show_gsin_formula()
        self.show_acceleration_at_different_angles()
        self.ask_about_what_to_do()
        self.show_velocity_and_position()
        self.show_derivatives()
        self.show_equation()
        self.talk_about_sine_component()
        self.add_air_resistance()

    def add_pendulum(self):
        self.pendulum = Pendulum(**self.pendulum_config)
        self.add(self.pendulum)

    def show_constraint(self):
        pendulum = self.pendulum
        weight = pendulum.weight

        g_vect = self.g_vect = GravityVector(
            pendulum, **self.g_vect_config,
        )
        g_word = self.g_word = TextMobject("Gravity")
        g_word.rotate(-90 * DEGREES)
        g_word.scale(0.75)
        g_word.add_updater(lambda m: m.next_to(
            g_vect, RIGHT, buff=-SMALL_BUFF,
        ))

        theta_tracker = ValueTracker(pendulum.get_theta())

        p = weight.get_center()
        path = CubicBezier([p, p + 3 * DOWN, p + 3 * UP, p])

        g_word.suspend_updating()
        self.play(
            GrowArrow(g_vect),
            FadeInFrom(g_word, UP, lag_ratio=0.1),
        )
        g_word.resume_updating()

        self.play(MoveAlongPath(weight, path, run_time=2))
        self.wait()

        pendulum.add_updater(lambda p: p.set_theta(
            theta_tracker.get_value()
        ))
        arcs = VGroup()
        for u in [-1, 2, -1]:
            d_theta = 40 * DEGREES * u
            arc = Arc(
                start_angle=pendulum.get_theta() - 90 * DEGREES,
                angle=d_theta,
                radius=pendulum.length,
                arc_center=pendulum.get_fixed_point(),
                stroke_width=2,
                stroke_color=RED,
                stroke_opacity=0.5,
            )
            self.play(
                theta_tracker.increment_value, d_theta,
                ShowCreation(arc)
            )
            arcs.add(arc)
        pendulum.clear_updaters()
        self.wait()
        self.play(FadeOut(arc))

    def break_g_vect_into_components(self):
        g_vect = self.g_vect
        g_vect.component_lines = always_redraw(
            g_vect.create_component_lines
        )
        tan_line, perp_line = g_vect.component_lines
        g_vect.tangent = always_redraw(lambda: Arrow(
            tan_line.get_start(),
            tan_line.get_end(),
            buff=0,
            color=self.tan_line_color,
        ))
        g_vect.perp = always_redraw(lambda: Arrow(
            perp_line.get_start(),
            perp_line.get_end(),
            buff=0,
            color=self.perp_line_color,
        ))

        self.play(
            ShowCreation(g_vect.component_lines),
        )
        self.play(GrowArrow(g_vect.tangent))
        self.wait()
        self.play(GrowArrow(g_vect.perp))
        self.wait()

    def show_angle_geometry(self):
        g_vect = self.g_vect

    def show_gsin_formula(self):
        pass

    def show_acceleration_at_different_angles(self):
        pass

    def ask_about_what_to_do(self):
        pass

    def show_velocity_and_position(self):
        pass

    def show_derivatives(self):
        pass

    def show_equation(self):
        pass

    def talk_about_sine_component(self):
        pass

    def add_air_resistance(self):
        pass


class NewSceneName(Scene):
    def construct(self):
        pass
