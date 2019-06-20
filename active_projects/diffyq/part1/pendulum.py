from manimlib.imports import *
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
        "set_theta_label_height_cap": False,
        "n_steps_per_frame": 100,
        "include_theta_label": True,
        "include_velocity_vector": False,
        "velocity_vector_multiple": 0.5,
        "max_velocity_vector_length_to_length_ratio": 0.5,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_fixed_point()
        self.create_rod()
        self.create_weight()
        self.rotating_group = VGroup(self.rod, self.weight)
        self.create_dashed_line()
        self.create_angle_arc()
        if self.include_theta_label:
            self.add_theta_label()
        if self.include_velocity_vector:
            self.add_velocity_vector()

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
        line.add_updater(
            lambda l: l.move_to(self.get_fixed_point(), UP)
        )
        self.add_to_back(line)

    def create_angle_arc(self):
        self.angle_arc = always_redraw(lambda: Arc(
            arc_center=self.get_fixed_point(),
            start_angle=-90 * DEGREES,
            angle=self.get_arc_angle_theta(),
            **self.angle_arc_config,
        ))
        self.add(self.angle_arc)

    def get_arc_angle_theta(self):
        # Might be changed in certain scenes
        return self.get_theta()

    def add_velocity_vector(self):
        def make_vector():
            omega = self.get_omega()
            theta = self.get_theta()
            mvlr = self.max_velocity_vector_length_to_length_ratio
            max_len = mvlr * self.rod.get_length()
            vvm = self.velocity_vector_multiple
            multiple = np.clip(
                vvm * omega, -max_len, max_len
            )
            vector = Vector(
                multiple * RIGHT,
                **self.velocity_vector_config,
            )
            vector.rotate(theta, about_point=ORIGIN)
            vector.shift(self.rod.get_end())
            return vector

        self.velocity_vector = always_redraw(make_vector)
        self.add(self.velocity_vector)
        return self

    def add_theta_label(self):
        self.theta_label = always_redraw(self.get_label)
        self.add(self.theta_label)

    def get_label(self):
        label = TexMobject("\\theta")
        label.set_height(self.theta_label_height)
        if self.set_theta_label_height_cap:
            max_height = self.angle_arc.get_width()
            if label.get_height() > max_height:
                label.set_height(max_height)
        top = self.get_fixed_point()
        arc_center = self.angle_arc.point_from_proportion(0.5)
        vect = arc_center - top
        norm = get_norm(vect)
        vect = normalize(vect) * (norm + self.theta_label_height)
        label.move_to(top + vect)
        return label

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

        self.y_axis_label = theta_label
        self.x_axis_label = t_label

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
            "gravity": 20,
        },
        "theta_vs_t_axes_config": {
            "y_max": PI / 4,
            "y_min": -PI / 4,
            "y_axis_config": {
                "tick_frequency": PI / 16,
                "unit_size": 2,
                "tip_length": 0.3,
            },
            "x_max": 12,
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
        # self.label_pi_creatures()
        self.label_pendulum()
        self.add_graph()
        self.label_function()
        self.show_graph_period()
        self.show_length_and_gravity()
        # self.tweak_length_and_gravity()

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
        self.wait(2)

    def label_pendulum(self):
        pendulum = self.pendulum
        randy, morty = self.pi_creatures
        label = pendulum.theta_label
        rect = SurroundingRectangle(label, buff=0.5 * SMALL_BUFF)
        rect.add_updater(lambda r: r.move_to(label))

        for pi in randy, morty:
            pi.add_updater(
                lambda m: m.look_at(pendulum.weight)
            )

        self.play(randy.change, "pondering")
        self.play(morty.change, "pondering")
        self.wait(3)
        randy.clear_updaters()
        morty.clear_updaters()
        self.play(
            ShowCreationThenFadeOut(rect),
        )
        self.wait()

    def add_graph(self):
        axes = self.axes = ThetaVsTAxes(**self.theta_vs_t_axes_config)
        axes.y_axis.label.next_to(axes.y_axis, UP, buff=0)
        axes.to_corner(UL)

        self.play(
            Restore(
                self.camera_frame,
                rate_func=squish_rate_func(smooth, 0, 0.9),
            ),
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

        self.wait(1.5)
        self.graph = axes.get_live_drawn_graph(self.pendulum)
        self.add(self.graph)

    def label_function(self):
        hm_word = TextMobject("Simple harmonic motion")
        hm_word.scale(1.25)
        hm_word.to_edge(UP)

        formula = TexMobject(
            "=\\theta_0 \\cos(\\sqrt{g / L} t)"
        )
        formula.next_to(
            self.axes.y_axis_label, RIGHT, SMALL_BUFF
        )
        formula.set_stroke(width=0, background=True)

        self.play(FadeInFrom(hm_word, DOWN))
        self.wait()
        self.play(
            Write(formula),
            hm_word.to_corner, UR
        )
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
        formula = get_period_formula()
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
        down_vectors = self.get_down_vectors()
        down_vectors.set_color(YELLOW)
        down_vectors.set_opacity(0.5)

        self.play(
            ShowCreationThenDestructionAround(L),
            ShowCreation(new_rod),
        )
        self.play(FadeOut(new_rod))

        self.play(
            ShowCreationThenDestructionAround(g),
            GrowArrow(g_vect),
        )
        self.play(self.get_down_vectors_animation(down_vectors))
        self.wait(6)

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

        down_vectors = self.get_down_vectors()

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
            self.get_down_vectors_animation(down_vectors)
        )
        self.play(
            FadeIn(graph3),
            brace.stretch, 0.5, 0, {"about_edge": LEFT},
        )
        self.wait(6)

    #
    def get_down_vectors(self):
        down_vectors = VGroup(*[
            Vector(0.5 * DOWN)
            for x in range(10 * 150)
        ])
        down_vectors.arrange_in_grid(10, 150, buff=MED_SMALL_BUFF)
        down_vectors.set_color_by_gradient(BLUE, RED)
        # for vect in down_vectors:
        #     vect.shift(0.1 * np.random.random(3))
        down_vectors.to_edge(RIGHT)
        return down_vectors

    def get_down_vectors_animation(self, down_vectors):
        return LaggedStart(
            *[
                GrowArrow(v, rate_func=there_and_back)
                for v in down_vectors
            ],
            lag_ratio=0.0005,
            run_time=2,
            remover=True
        )


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


class WherePendulumLeads(PiCreatureScene):
    def construct(self):
        pendulum = Pendulum(
            top_point=UP,
            length=3,
            gravity=20,
        )
        pendulum.start_swinging()

        l_title = TextMobject("Linearization")
        l_title.scale(1.5)
        l_title.to_corner(UL)
        c_title = TextMobject("Chaos")
        c_title.scale(1.5)
        c_title.move_to(l_title)
        c_title.move_to(
            c_title.get_center() * np.array([-1, 1, 1])
        )

        get_theta = pendulum.get_theta
        spring = always_redraw(
            lambda: ParametricFunction(
                lambda t: np.array([
                    np.cos(TAU * t) + (1.4 + get_theta()) * t,
                    np.sin(TAU * t) - 0.5,
                    0,
                ]),
                t_min=-0.5,
                t_max=7,
                color=GREY,
                sheen_factor=1,
                sheen_direction=UL,
            ).scale(0.2).to_edge(LEFT, buff=0)
        )
        spring_rect = SurroundingRectangle(
            spring, buff=MED_LARGE_BUFF,
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=0,
        )

        weight = Dot(radius=0.25)
        weight.add_updater(lambda m: m.move_to(
            spring.points[-1]
        ))
        weight.set_color(BLUE)
        weight.set_sheen(1, UL)
        spring_system = VGroup(spring, weight)

        linear_formula = TexMobject(
            "\\frac{d \\vec{\\textbf{x}}}{dt}="
            "A\\vec{\\textbf{x}}"
        )
        linear_formula.next_to(spring, UP, LARGE_BUFF)
        linear_formula.match_x(l_title)

        randy = self.pi_creature
        randy.set_height(2)
        randy.center()
        randy.to_edge(DOWN)
        randy.shift(3 * LEFT)
        q_marks = TexMobject("???")
        q_marks.next_to(randy, UP)

        self.add(pendulum, randy)
        self.play(
            randy.change, "pondering", pendulum,
            FadeInFromDown(q_marks, lag_ratio=0.3)
        )
        self.play(randy.look_at, pendulum)
        self.wait(5)
        self.play(
            Animation(VectorizedPoint(pendulum.get_top())),
            FadeOutAndShift(q_marks, UP, lag_ratio=0.3),
        )
        self.add(spring_system)
        self.play(
            FadeOut(spring_rect),
            FadeInFrom(linear_formula, UP),
            FadeInFromDown(l_title),
        )
        self.play(FadeInFromDown(c_title))
        self.wait(8)


class LongDoublePendulum(ExternallyAnimatedScene):
    pass


class AnalyzePendulumForce(MovingCameraScene):
    CONFIG = {
        "pendulum_config": {
            "length": 5,
            "top_point": 3.5 * UP,
            "initial_theta": 60 * DEGREES,
            "set_theta_label_height_cap": True,
        },
        "g_vect_config": {
            "length_multiple": 0.25,
        },
        "tan_line_color": BLUE,
        "perp_line_color": PINK,
    }

    def construct(self):
        self.add_pendulum()
        self.show_arc_length()
        self.add_g_vect()
        self.show_constraint()
        self.break_g_vect_into_components()
        self.show_angle_geometry()
        self.show_gsin_formula()
        self.show_sign()
        self.show_acceleration_formula()
        # self.ask_about_what_to_do()

        # self.emphasize_theta()
        # self.show_angular_velocity()
        # self.show_angular_acceleration()
        # self.circle_g_sin_formula()

    def add_pendulum(self):
        pendulum = Pendulum(**self.pendulum_config)
        theta_tracker = ValueTracker(pendulum.get_theta())
        pendulum.add_updater(lambda p: p.set_theta(
            theta_tracker.get_value()
        ))

        self.add(pendulum)
        self.pendulum = pendulum
        self.theta_tracker = theta_tracker

    def show_arc_length(self):
        pendulum = self.pendulum
        angle = pendulum.get_theta()
        height = pendulum.length
        top = pendulum.get_fixed_point()

        line = Line(UP, DOWN)
        line.set_height(height)
        line.move_to(top, UP)
        arc = always_redraw(lambda: Arc(
            start_angle=-90 * DEGREES,
            angle=pendulum.get_theta(),
            arc_center=pendulum.get_fixed_point(),
            radius=pendulum.length,
            stroke_color=GREEN,
        ))

        brace = Brace(Line(ORIGIN, 5 * UP), RIGHT)
        brace.point = VectorizedPoint(brace.get_right())
        brace.add(brace.point)
        brace.set_height(angle)
        brace.move_to(ORIGIN, DL)
        brace.apply_complex_function(np.exp)
        brace.scale(height)
        brace.rotate(-90 * DEGREES)
        brace.move_to(arc)
        brace.shift(MED_SMALL_BUFF * normalize(
            arc.point_from_proportion(0.5) - top
        ))
        x_sym = TexMobject("x")
        x_sym.set_color(GREEN)
        x_sym.next_to(brace.point, DR, buff=SMALL_BUFF)

        rhs = TexMobject("=", "L", "\\theta")
        rhs.set_color_by_tex("\\theta", BLUE)
        rhs.next_to(x_sym, RIGHT)
        rhs.shift(0.7 * SMALL_BUFF * UP)
        line_L = TexMobject("L")
        line_L.next_to(
            pendulum.rod.get_center(), UR, SMALL_BUFF,
        )

        self.play(
            ShowCreation(arc),
            Rotate(line, angle, about_point=top),
            UpdateFromAlphaFunc(
                line, lambda m, a: m.set_stroke(
                    width=2 * there_and_back(a)
                )
            ),
            GrowFromPoint(
                brace, line.get_bottom(),
                path_arc=angle
            ),
        )
        self.play(FadeInFrom(x_sym, UP))
        self.wait()

        # Show equation
        line.set_stroke(BLUE, 5)
        self.play(
            ShowCreationThenFadeOut(line),
            FadeInFromDown(line_L)
        )
        self.play(
            TransformFromCopy(
                line_L, rhs.get_part_by_tex("L")
            ),
            Write(rhs.get_part_by_tex("="))
        )
        self.play(
            TransformFromCopy(
                pendulum.theta_label,
                rhs.get_parts_by_tex("\\theta"),
            )
        )
        self.add(rhs)

        x_eq = VGroup(x_sym, rhs)

        self.play(
            FadeOut(brace),
            x_eq.rotate, angle / 2,
            x_eq.next_to, arc.point_from_proportion(0.5),
            UL, {"buff": -MED_SMALL_BUFF}
        )

        self.x_eq = x_eq
        self.arc = arc
        self.line_L = line_L

    def add_g_vect(self):
        pendulum = self.pendulum

        g_vect = self.g_vect = GravityVector(
            pendulum, **self.g_vect_config,
        )
        g_word = self.g_word = TextMobject("Gravity")
        g_word.rotate(-90 * DEGREES)
        g_word.scale(0.75)
        g_word.add_updater(lambda m: m.next_to(
            g_vect, RIGHT, buff=-SMALL_BUFF,
        ))

        self.play(
            GrowArrow(g_vect),
            FadeInFrom(g_word, UP, lag_ratio=0.1),
        )
        self.wait()

    def show_constraint(self):
        pendulum = self.pendulum

        arcs = VGroup()
        for u in [-1, 2, -1]:
            d_theta = 40 * DEGREES * u
            arc = Arc(
                start_angle=pendulum.get_theta() - 90 * DEGREES,
                angle=d_theta,
                radius=pendulum.length,
                arc_center=pendulum.get_fixed_point(),
                stroke_width=2,
                stroke_color=YELLOW,
                stroke_opacity=0.5,
            )
            self.play(
                self.theta_tracker.increment_value, d_theta,
                ShowCreation(arc)
            )
            arcs.add(arc)
        self.play(FadeOut(arcs))

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

        self.play(ShowCreation(g_vect.component_lines))
        self.play(GrowArrow(g_vect.tangent))
        self.wait()
        self.play(GrowArrow(g_vect.perp))
        self.wait()

    def show_angle_geometry(self):
        g_vect = self.g_vect

        arc = Arc(
            start_angle=90 * DEGREES,
            angle=self.pendulum.get_theta(),
            radius=0.5,
            arc_center=g_vect.get_end(),
        )
        q_mark = TexMobject("?")
        q_mark.next_to(arc.get_center(), UL, SMALL_BUFF)
        theta_label = TexMobject("\\theta")
        theta_label.move_to(q_mark)

        self.add(g_vect)
        self.play(
            ShowCreation(arc),
            Write(q_mark)
        )
        self.play(ShowCreationThenFadeAround(q_mark))
        self.wait()
        self.play(ShowCreationThenFadeAround(
            self.pendulum.theta_label
        ))
        self.play(
            TransformFromCopy(
                self.pendulum.theta_label,
                theta_label,
            ),
            FadeOut(q_mark)
        )
        self.wait()
        self.play(WiggleOutThenIn(g_vect.tangent))
        self.play(WiggleOutThenIn(
            Line(
                *g_vect.get_start_and_end(),
                buff=0,
            ).add_tip().match_style(g_vect),
            remover=True
        ))
        self.wait()
        self.play(
            FadeOut(arc),
            FadeOut(theta_label),
        )

    def show_gsin_formula(self):
        g_vect = self.g_vect
        g_word = self.g_word
        g_word.clear_updaters()

        g_term = self.g_term = TexMobject("-g")
        g_term.add_updater(lambda m: m.next_to(
            g_vect,
            RIGHT if self.pendulum.get_theta() >= 0 else LEFT,
            SMALL_BUFF
        ))

        def create_vect_label(vect, tex, direction):
            label = TexMobject(tex)
            label.set_stroke(width=0, background=True)
            label.add_background_rectangle()
            label.scale(0.7)
            max_width = 0.9 * vect.get_length()
            if label.get_width() > max_width:
                label.set_width(max_width)
            angle = vect.get_angle()
            angle = (angle + PI / 2) % PI - PI / 2
            label.next_to(ORIGIN, direction, SMALL_BUFF)
            label.rotate(angle, about_point=ORIGIN)
            label.shift(vect.get_center())
            return label

        g_sin_label = always_redraw(lambda: create_vect_label(
            g_vect.tangent, "-g\\sin(\\theta)", UP,
        ))
        g_cos_label = always_redraw(lambda: create_vect_label(
            g_vect.perp, "-g\\cos(\\theta)", DOWN,
        ))

        self.play(
            ReplacementTransform(g_word[0][0], g_term[0][1]),
            FadeOut(g_word[0][1:]),
            Write(g_term[0][0]),
        )
        self.add(g_term)
        self.wait()
        for label in g_sin_label, g_cos_label:
            self.play(
                GrowFromPoint(label[0], g_term.get_center()),
                TransformFromCopy(g_term, label[1][:2]),
                GrowFromPoint(label[1][2:], g_term.get_center()),
                remover=True
            )
            self.add(label)
            self.wait()

        self.g_sin_label = g_sin_label
        self.g_cos_label = g_cos_label

    def show_sign(self):
        get_theta = self.pendulum.get_theta
        theta_decimal = DecimalNumber(include_sign=True)
        theta_decimal.add_updater(lambda d: d.set_value(
            get_theta()
        ))
        theta_decimal.add_updater(lambda m: m.next_to(
            self.pendulum.theta_label, DOWN
        ))
        theta_decimal.add_updater(lambda m: m.set_color(
            GREEN if get_theta() > 0 else RED
        ))

        self.play(
            FadeInFrom(theta_decimal, UP),
            FadeOut(self.x_eq),
            FadeOut(self.line_L),
        )
        self.set_theta(-60 * DEGREES, run_time=4)
        self.set_theta(60 * DEGREES, run_time=4)
        self.play(
            FadeOut(theta_decimal),
            FadeIn(self.x_eq),
        )

    def show_acceleration_formula(self):
        x_eq = self.x_eq
        g_sin_theta = self.g_sin_label

        equation = TexMobject(
            "a", "=",
            "\\ddot", "x",
            "=",
            "-", "g", "\\sin\\big(", "\\theta", "\\big)",
        )
        equation.to_edge(LEFT)

        second_deriv = equation[2:4]
        x_part = equation.get_part_by_tex("x")
        x_part.set_color(GREEN)
        a_eq = equation[:2]
        eq2 = equation.get_parts_by_tex("=")[1]
        rhs = equation[5:]

        second_deriv_L_form = TexMobject(
            "L", "\\ddot", "\\theta"
        )
        second_deriv_L_form.move_to(second_deriv, DOWN)
        eq3 = TexMobject("=")
        eq3.rotate(90 * DEGREES)
        eq3.next_to(second_deriv_L_form, UP)

        g_L_frac = TexMobject(
            "-", "{g", "\\over", "L}"
        )
        g_L_frac.move_to(rhs[:2], LEFT)
        g_L_frac.shift(SMALL_BUFF * UP / 2)

        mu_term = TexMobject(
            "-\\mu", "\\dot", "\\theta",
        )
        mu_term.next_to(g_L_frac, LEFT)
        mu_term.shift(SMALL_BUFF * UP / 2)

        mu_brace = Brace(mu_term, UP)
        mu_word = mu_brace.get_text("Air resistance")

        for mob in equation, second_deriv_L_form, mu_term:
            mob.set_color_by_tex("\\theta", BLUE)

        self.play(
            TransformFromCopy(x_eq[0], x_part),
            Write(equation[:3]),
        )
        self.wait()
        self.play(
            Write(eq2),
            TransformFromCopy(g_sin_theta, rhs)
        )
        self.wait()
        #
        self.show_acceleration_at_different_angles()
        #
        self.play(
            FadeInFromDown(second_deriv_L_form),
            Write(eq3),
            second_deriv.next_to, eq3, UP,
            a_eq.shift, SMALL_BUFF * LEFT,
            eq2.shift, SMALL_BUFF * RIGHT,
            rhs.shift, SMALL_BUFF * RIGHT,
        )
        self.wait()
        self.wait()
        self.play(
            FadeOut(a_eq),
            FadeOut(second_deriv),
            FadeOut(eq3),
            ReplacementTransform(
                second_deriv_L_form.get_part_by_tex("L"),
                g_L_frac.get_part_by_tex("L"),
            ),
            ReplacementTransform(
                equation.get_part_by_tex("-"),
                g_L_frac.get_part_by_tex("-"),
            ),
            ReplacementTransform(
                equation.get_part_by_tex("g"),
                g_L_frac.get_part_by_tex("g"),
            ),
            Write(g_L_frac.get_part_by_tex("\\over")),
            rhs[2:].next_to, g_L_frac, RIGHT, {"buff": SMALL_BUFF},
        )
        self.wait()
        self.play(
            GrowFromCenter(mu_term),
            VGroup(eq2, second_deriv_L_form[1:]).next_to,
            mu_term, LEFT,
        )
        self.play(
            GrowFromCenter(mu_brace),
            FadeInFromDown(mu_word),
        )

    def show_acceleration_at_different_angles(self):
        to_fade = VGroup(
            self.g_cos_label,
            self.g_vect.perp,
        )
        new_comp_line_sytle = {
            "stroke_width": 0.5,
            "stroke_opacity": 0.25,
        }

        self.play(
            FadeOut(self.x_eq),
            to_fade.set_opacity, 0.25,
            self.g_vect.component_lines.set_style,
            new_comp_line_sytle
        )
        self.g_vect.component_lines.add_updater(
            lambda m: m.set_style(**new_comp_line_sytle)
        )
        for mob in to_fade:
            mob.add_updater(lambda m: m.set_opacity(0.25))

        self.set_theta(0)
        self.wait(2)
        self.set_theta(89.9 * DEGREES, run_time=3)
        self.wait(2)
        self.set_theta(
            60 * DEGREES,
            FadeIn(self.x_eq),
            run_time=2,
        )
        self.wait()

    def ask_about_what_to_do(self):
        g_vect = self.g_vect
        g_sin_label = self.g_sin_label
        angle = g_vect.tangent.get_angle()
        angle = (angle - PI) % TAU

        randy = You()
        randy.to_corner(DL)
        bubble = randy.get_bubble(
            height=2,
            width=3.5,
        )
        g_sin_copy = g_sin_label.copy()
        g_sin_copy.remove(g_sin_copy[0])
        g_sin_copy.generate_target()
        g_sin_copy.target.scale(1 / 0.75)
        g_sin_copy.target.rotate(-angle)
        a_eq = TexMobject("a=")
        thought_term = VGroup(a_eq, g_sin_copy.target)
        thought_term.arrange(RIGHT, buff=SMALL_BUFF)
        thought_term.move_to(bubble.get_bubble_center())

        rect = SurroundingRectangle(g_sin_copy.target)
        rect.rotate(angle)
        rect.move_to(g_sin_label)

        randy.save_state()
        randy.fade(1)
        self.play(randy.restore, randy.change, "pondering")
        self.play(ShowCreationThenFadeOut(rect))
        self.play(
            ShowCreation(bubble),
            Write(a_eq),
            MoveToTarget(g_sin_copy),
            randy.look_at, bubble,
        )
        thought_term.remove(g_sin_copy.target)
        thought_term.add(g_sin_copy)
        self.play(Blink(randy))
        self.wait()
        self.play(
            ShowCreationThenDestruction(
                thought_term.copy().set_style(
                    stroke_color=YELLOW,
                    stroke_width=2,
                    fill_opacity=0,
                ),
                run_time=2,
                lag_ratio=0.2,
            ),
            randy.change, "confused", thought_term,
        )
        self.play(Blink(randy))
        self.play(
            FadeOut(randy),
            FadeOut(bubble),
            thought_term.next_to, self.pendulum, DOWN, LARGE_BUFF
        )

        self.accleration_equation = thought_term

    def emphasize_theta(self):
        pendulum = self.pendulum

        self.play(FocusOn(pendulum.theta_label))
        self.play(Indicate(pendulum.theta_label))

        pendulum_copy = pendulum.deepcopy()
        pendulum_copy.clear_updaters()
        pendulum_copy.fade(1)
        pendulum_copy.start_swinging()

        def new_updater(p):
            p.set_theta(pendulum_copy.get_theta())
        pendulum.add_updater(new_updater)

        self.add(pendulum_copy)
        self.wait(5)
        pendulum_copy.end_swinging()
        self.remove(pendulum_copy)
        pendulum.remove_updater(new_updater)
        self.update_mobjects(0)

    def show_angular_velocity(self):
        pass

    def show_angular_acceleration(self):
        pass

    def circle_g_sin_formula(self):
        self.play(
            ShowCreationThenFadeAround(
                self.accleration_equation
            )
        )

    #
    def set_theta(self, value, *added_anims, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", 2)
        self.play(
            self.theta_tracker.set_value, value,
            *added_anims,
            **kwargs,
        )


class BuildUpEquation(Scene):
    CONFIG = {
        "tex_config": {
            "tex_to_color_map": {
                "{a}": YELLOW,
                "{v}": RED,
                "{x}": GREEN,
                "\\theta": BLUE,
                "{L}": WHITE,
            }
        }
    }

    def construct(self):
        # self.add_center_line()
        self.show_derivatives()
        self.show_theta_double_dot_equation()
        self.talk_about_sine_component()
        self.add_air_resistance()

    def add_center_line(self):
        line = Line(UP, DOWN)
        line.set_height(FRAME_HEIGHT)
        line.set_stroke(WHITE, 1)
        self.add(line)

    def show_derivatives(self):
        a_eq = TexMobject(
            "{a}", "=", "{d{v} \\over dt}",
            **self.tex_config,
        )
        v_eq = TexMobject(
            "{v}", "=", "{d{x} \\over dt}",
            **self.tex_config,
        )
        x_eq = TexMobject(
            "{x} = {L} \\theta",
            **self.tex_config,
        )
        eqs = VGroup(a_eq, v_eq, x_eq)
        eqs.arrange(DOWN, buff=LARGE_BUFF)
        eqs.to_corner(UL)

        v_rhs = TexMobject(
            "={L}{d\\theta \\over dt}",
            "=", "{L}\\dot{\\theta}",
            **self.tex_config,
        )

        v_rhs.next_to(v_eq, RIGHT, SMALL_BUFF)
        v_rhs.shift(
            UP * (v_eq[1].get_bottom()[1] - v_rhs[0].get_bottom()[1])
        )
        a_rhs = TexMobject(
            "={L}{d", "\\dot{\\theta}", "\\over dt}",
            "=", "{L}\\ddot{\\theta}",
            **self.tex_config,
        )
        a_rhs.next_to(a_eq, RIGHT, SMALL_BUFF)
        a_rhs.shift(
            UP * (a_eq[1].get_bottom()[1] - a_rhs[0].get_bottom()[1])
        )

        # a_eq
        self.play(Write(a_eq))
        self.wait()

        # v_eq
        self.play(
            TransformFromCopy(
                a_eq.get_part_by_tex("{v}"),
                v_eq.get_part_by_tex("{v}"),
            )
        )
        self.play(TransformFromCopy(v_eq[:1], v_eq[1:]))
        self.wait()

        # x_eq
        self.play(
            TransformFromCopy(
                v_eq.get_part_by_tex("{x}"),
                x_eq.get_part_by_tex("{x}"),
            )
        )
        self.play(Write(x_eq[1:]))
        self.wait()
        for tex in "L", "\\theta":
            self.play(ShowCreationThenFadeAround(
                x_eq.get_part_by_tex(tex)
            ))
        self.wait()

        # v_rhs
        self.play(*[
            TransformFromCopy(
                x_eq.get_part_by_tex(tex),
                v_rhs.get_part_by_tex(tex),
            )
            for tex in ("=", "{L}", "\\theta")
        ])
        self.play(
            TransformFromCopy(v_eq[-3], v_rhs[2]),
            TransformFromCopy(v_eq[-1], v_rhs[4]),
        )
        self.wait()
        self.play(
            Write(v_rhs[-5]),
            TransformFromCopy(*v_rhs.get_parts_by_tex("{L}")),
            TransformFromCopy(v_rhs[3:4], v_rhs[-3:])
        )
        self.wait()
        self.play(ShowCreationThenFadeAround(v_rhs[2:4]))
        self.play(ShowCreationThenFadeAround(v_rhs[4]))
        self.wait()

        # a_rhs
        self.play(*[
            TransformFromCopy(
                v_rhs.get_parts_by_tex(tex)[-1],
                a_rhs.get_part_by_tex(tex),
            )
            for tex in ("=", "{L}", "\\theta", "\\dot")
        ])
        self.play(
            TransformFromCopy(a_eq[-3], a_rhs[2]),
            TransformFromCopy(a_eq[-1], a_rhs[6]),
        )
        self.wait()
        self.play(
            Write(a_rhs[-5]),
            TransformFromCopy(*a_rhs.get_parts_by_tex("{L}")),
            TransformFromCopy(a_rhs[3:4], a_rhs[-3:]),
        )
        self.wait()

        self.equations = VGroup(
            a_eq, v_eq, x_eq,
            v_rhs, a_rhs,
        )

    def show_theta_double_dot_equation(self):
        equations = self.equations
        a_deriv = equations[0]
        a_rhs = equations[-1][-5:].copy()

        shift_vect = 1.5 * DOWN

        equals = TexMobject("=")
        equals.rotate(90 * DEGREES)
        equals.next_to(a_deriv[0], UP, MED_LARGE_BUFF)
        g_sin_eq = TexMobject(
            "-", "g", "\\sin", "(", "\\theta", ")",
            **self.tex_config,
        )
        g_sin_eq.next_to(
            equals, UP,
            buff=MED_LARGE_BUFF,
            aligned_edge=LEFT,
        )
        g_sin_eq.to_edge(LEFT)
        g_sin_eq.shift(shift_vect)

        shift_vect += (
            g_sin_eq[1].get_center() -
            a_deriv[0].get_center()
        )[0] * RIGHT

        equals.shift(shift_vect)
        a_rhs.shift(shift_vect)

        self.play(
            equations.shift, shift_vect,
            Write(equals),
            GrowFromPoint(
                g_sin_eq, 2 * RIGHT + 3 * DOWN
            )
        )
        self.wait()
        self.play(
            a_rhs.next_to, g_sin_eq, RIGHT,
            a_rhs.shift, SMALL_BUFF * UP,
        )
        self.wait()

        # Fade equations
        self.play(
            FadeOut(equals),
            equations.shift, DOWN,
            equations.fade, 0.5,
        )

        # Rotate sides
        equals, L, ddot, theta, junk = a_rhs
        L_dd_theta = VGroup(L, ddot, theta)
        minus, g, sin, lp, theta2, rp = g_sin_eq
        m2, g2, over, L2 = frac = TexMobject("-", "{g", "\\over", "L}")
        frac.next_to(equals, RIGHT)

        self.play(
            L_dd_theta.next_to, equals, LEFT,
            L_dd_theta.shift, SMALL_BUFF * UP,
            g_sin_eq.next_to, equals, RIGHT,
            path_arc=PI / 2,
        )
        self.play(
            ReplacementTransform(g, g2),
            ReplacementTransform(minus, m2),
            ReplacementTransform(L, L2),
            Write(over),
            g_sin_eq[2:].next_to, over, RIGHT, SMALL_BUFF,
        )
        self.wait()

        # Surround
        rect = SurroundingRectangle(VGroup(g_sin_eq, frac, ddot))
        rect.stretch(1.1, 0)
        dashed_rect = DashedVMobject(
            rect, num_dashes=50, positive_space_ratio=1,
        )
        dashed_rect.shuffle()
        dashed_rect.save_state()
        dashed_rect.space_out_submobjects(1.1)
        for piece in dashed_rect:
            piece.rotate(90 * DEGREES)
        dashed_rect.fade(1)
        self.play(Restore(dashed_rect, lag_ratio=0.05))
        dashed_rect.generate_target()
        dashed_rect.target.space_out_submobjects(0.9)
        dashed_rect.target.fade(1)
        for piece in dashed_rect.target:
            piece.rotate(90 * DEGREES)
        self.play(MoveToTarget(
            dashed_rect,
            lag_ratio=0.05,
            remover=True
        ))
        self.wait()

        self.main_equation = VGroup(
            ddot, theta, equals,
            m2, L2, over, g2,
            sin, lp, theta2, rp,
        )

    def talk_about_sine_component(self):
        main_equation = self.main_equation
        gL_part = main_equation[4:7]
        sin_part = main_equation[7:]
        sin = sin_part[0]

        morty = Mortimer(height=1.5)
        morty.next_to(sin, DR, buff=LARGE_BUFF)
        morty.add_updater(lambda m: m.look_at(sin))

        self.play(ShowCreationThenFadeAround(gL_part))
        self.wait()
        self.play(ShowCreationThenFadeAround(sin_part))
        self.wait()

        self.play(FadeIn(morty))
        sin.save_state()
        self.play(
            morty.change, "angry",
            sin.next_to, morty, LEFT, {"aligned_edge": UP},
        )
        self.play(Blink(morty))
        morty.clear_updaters()
        self.play(
            morty.change, "concerned_musician",
            morty.look, DR,
        )
        self.play(Restore(sin))
        self.play(FadeOut(morty))
        self.wait()

        # Emphasize theta as input
        theta = sin_part[2]
        arrow = Vector(0.5 * UP, color=WHITE)
        arrow.next_to(theta, DOWN, SMALL_BUFF)
        word = TextMobject("Input")
        word.next_to(arrow, DOWN)

        self.play(
            FadeInFrom(word, UP),
            GrowArrow(arrow)
        )
        self.play(
            ShowCreationThenDestruction(
                theta.copy().set_style(
                    fill_opacity=0,
                    stroke_width=2,
                    stroke_color=YELLOW,
                ),
                lag_ratio=0.1,
            )
        )
        self.play(FadeOut(arrow), FadeOut(word))

    def add_air_resistance(self):
        main_equation = self.main_equation
        tdd_eq = main_equation[:3]
        rhs = main_equation[3:]

        new_term = TexMobject(
            "-", "\\mu", "\\dot{", "\\theta}",
        )
        new_term.set_color_by_tex("\\theta", BLUE)
        new_term.move_to(main_equation)
        new_term.shift(0.5 * SMALL_BUFF * UP)
        new_term[0].align_to(rhs[0], UP)

        brace = Brace(new_term, DOWN)
        words = brace.get_text("Air resistance")

        self.play(
            FadeInFromDown(new_term),
            tdd_eq.next_to, new_term, LEFT,
            tdd_eq.align_to, tdd_eq, UP,
            rhs.next_to, new_term, RIGHT,
            rhs.align_to, rhs, UP,
        )
        self.play(
            GrowFromCenter(brace),
            Write(words)
        )
        self.wait()


class SimpleDampenedPendulum(Scene):
    def construct(self):
        pendulum = Pendulum(
            top_point=ORIGIN,
            initial_theta=150 * DEGREES,
            mu=0.5,
        )
        self.add(pendulum)
        pendulum.start_swinging()
        self.wait(20)


class NewSceneName(Scene):
    def construct(self):
        pass
