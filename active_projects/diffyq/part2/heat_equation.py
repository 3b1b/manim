from manimlib.imports import *
from active_projects.ode.part2.shared_constructs import *


class TwoDBodyWithManyTemperatures(ThreeDScene):
    CONFIG = {
        "cells_per_side": 20,
        "body_height": 6,
    }

    def construct(self):
        self.introduce_body()
        self.show_temperature_at_all_points()

    def introduce_body(self):
        height = self.body_height
        buff = 0.025
        rows = VGroup(*[
            VGroup(*[
                Dot(
                    # stroke_width=0.5,
                    stroke_width=0,
                    fill_opacity=1,
                )
                for x in range(self.cells_per_side)
            ]).arrange(RIGHT, buff=buff)
            for y in range(self.cells_per_side)
        ]).arrange(DOWN, buff=buff)
        for row in rows[1::2]:
            row.submobjects.reverse()

        body = self.body = VGroup(*it.chain(*rows))
        body.set_height(height)
        body.center()
        body.to_edge(LEFT)

        axes = self.axes = Axes(
            x_min=-5, x_max=5,
            y_min=-5, y_max=5,
        )
        axes.match_height(body)
        axes.move_to(body)

        for cell in body:
            self.color_cell(cell)
        # body.set_stroke(WHITE, 0.5)  # Do this?

        plate = Square(
            stroke_width=0,
            fill_color=DARK_GREY,
            sheen_direction=UL,
            sheen_factor=1,
            fill_opacity=1,
        )
        plate.replace(body)

        plate_words = TextMobject("Piece of \\\\ metal")
        plate_words.scale(2)
        plate_words.set_stroke(BLACK, 2, background=True)
        plate_words.set_color(BLACK)
        plate_words.move_to(plate)

        self.play(
            DrawBorderThenFill(plate),
            Write(
                plate_words,
                run_time=2,
                rate_func=squish_rate_func(smooth, 0.5, 1)
            )
        )
        self.wait()

        self.remove(plate_words)

    def show_temperature_at_all_points(self):
        body = self.body
        start_corner = body[0].get_center()

        dot = Dot(radius=0.01, color=WHITE)
        dot.move_to(start_corner)

        get_point = dot.get_center

        lhs = TexMobject("T = ")
        lhs.next_to(body, RIGHT, LARGE_BUFF)

        decimal = DecimalNumber(
            num_decimal_places=1,
            unit="^\\circ"
        )
        decimal.next_to(lhs, RIGHT, MED_SMALL_BUFF, DOWN)
        decimal.add_updater(
            lambda d: d.set_value(
                40 + 50 * self.point_to_temp(get_point())
            )
        )

        arrow = Arrow(color=YELLOW)
        arrow.set_stroke(BLACK, 8, background=True)
        arrow.tip.set_stroke(BLACK, 2, background=True)
        # arrow.add_to_back(arrow.copy().set_stroke(BLACK, 5))
        arrow.add_updater(lambda a: a.put_start_and_end_on(
            lhs.get_left() + MED_SMALL_BUFF * LEFT,
            get_point(),
        ))

        dot.add_updater(lambda p: p.move_to(
            body[-1] if (1 < len(body)) else start_corner
        ))
        self.add(body, dot, lhs, decimal, arrow)
        self.play(
            ShowIncreasingSubsets(
                body,
                run_time=10,
                rate_func=linear,
            )
        )
        self.wait()
        self.remove(dot)
        self.play(
            FadeOut(arrow),
            FadeOut(lhs),
            FadeOut(decimal),
        )

    #
    def point_to_temp(self, point, time=0):
        x, y = self.axes.point_to_coords(point)
        return two_d_temp_func(
            0.3 * x, 0.3 * y, t=time
        )

    def color_cell(self, cell, vect=RIGHT):
        p0 = cell.get_corner(-vect)
        p1 = cell.get_corner(vect)
        colors = []
        for point in p0, p1:
            temp = self.point_to_temp(point)
            color = temperature_to_color(temp)
            colors.append(color)
        cell.set_color(color=colors)
        cell.set_sheen_direction(vect)
        return cell


class TwoDBodyWithManyTemperaturesGraph(ExternallyAnimatedScene):
    pass


class TwoDBodyWithManyTemperaturesContour(ExternallyAnimatedScene):
    pass


class BringTwoRodsTogether(Scene):
    CONFIG = {
        "step_size": 0.05,
        "axes_config": {
            "x_min": -1,
            "x_max": 11,
            "y_min": -10,
            "y_max": 100,
            "y_axis_config": {
                "unit_size": 0.06,
                "tick_frequency": 10,
            },
        },
        "graph_x_min": 0,
        "graph_x_max": 10,
        "wait_time": 30,
        "default_n_rod_pieces": 20,
        "alpha": 1.0,
    }

    def construct(self):
        self.setup_axes()
        self.setup_graph()
        self.setup_clock()

        self.show_rods()
        self.show_equilibration()

    def setup_axes(self):
        axes = Axes(**self.axes_config)
        axes.center().to_edge(UP)

        y_label = axes.get_y_axis_label("\\text{Temperature}")
        y_label.to_edge(UP)
        axes.y_axis.label = y_label
        axes.y_axis.add(y_label)
        axes.y_axis.add_numbers(
            *range(20, 100, 20)
        )

        self.axes = axes
        self.y_label = y_label

    def setup_graph(self):
        graph = self.axes.get_graph(
            self.initial_function,
            x_min=self.graph_x_min,
            x_max=self.graph_x_max,
            step_size=self.step_size,
            discontinuities=[5],
        )
        graph.color_using_background_image("VerticalTempGradient")

        self.graph = graph

    def setup_clock(self):
        clock = Clock()
        clock.set_height(1)
        clock.to_corner(UR)
        clock.shift(MED_LARGE_BUFF * LEFT)

        time_lhs = TextMobject("Time: ")
        time_label = DecimalNumber(
            0, num_decimal_places=2,
        )
        time_rhs = TextMobject("s")
        time_group = VGroup(
            time_lhs,
            time_label,
            # time_rhs
        )
        time_group.arrange(RIGHT, aligned_edge=DOWN)
        time_rhs.shift(SMALL_BUFF * LEFT)
        time_group.next_to(clock, DOWN)

        self.time_group = time_group
        self.time_label = time_label
        self.clock = clock

    def show_rods(self):
        rod1, rod2 = rods = VGroup(
            self.get_rod(0, 5),
            self.get_rod(5, 10),
        )
        rod1.set_color(rod1[0].get_color())
        rod2.set_color(rod2[-1].get_color())

        rods.save_state()
        rods.space_out_submobjects(1.5)
        rods.center()

        labels = VGroup(
            TexMobject("90^\\circ"),
            TexMobject("10^\\circ"),
        )
        for rod, label in zip(rods, labels):
            label.next_to(rod, DOWN)
            rod.label = label

        self.play(
            FadeInFrom(rod1, UP),
            Write(rod1.label),
        )
        self.play(
            FadeInFrom(rod2, DOWN),
            Write(rod2.label)
        )
        self.wait()

        self.rods = rods
        self.rod_labels = labels

    def show_equilibration(self):
        rods = self.rods
        axes = self.axes
        graph = self.graph
        labels = self.rod_labels
        self.play(
            Write(axes),
            rods.restore,
            rods.space_out_submobjects, 1.1,
            FadeIn(self.time_group),
            FadeIn(self.clock),
            *[
                MaintainPositionRelativeTo(
                    rod.label, rod
                )
                for rod in rods
            ],
        )

        br1 = Rectangle(height=0.2, width=1)
        br1.set_stroke(width=0)
        br1.set_fill(BLACK, opacity=1)
        br2 = br1.copy()
        br1.add_updater(lambda b: b.move_to(axes.c2p(0, 90)))
        br1.add_updater(
            lambda b: b.align_to(rods[0].get_right(), LEFT)
        )
        br2.add_updater(lambda b: b.move_to(axes.c2p(0, 10)))
        br2.add_updater(
            lambda b: b.align_to(rods[1].get_left(), RIGHT)
        )

        self.add(graph, br1, br2)
        self.play(
            ShowCreation(graph),
            labels[0].align_to, axes.c2p(0, 87), UP,
            labels[1].align_to, axes.c2p(0, 13), DOWN,
        )
        self.play()
        self.play(
            rods.restore,
            rate_func=rush_into,
        )
        self.remove(br1, br2)

        graph.add_updater(self.update_graph)
        self.time_label.add_updater(
            lambda d, dt: d.increment_value(dt)
        )
        rods.add_updater(self.update_rods)

        self.play(
            ClockPassesTime(
                self.clock,
                run_time=self.wait_time,
                hours_passed=self.wait_time,
            ),
            FadeOut(labels)
        )

    #
    def initial_function(self, x):
        if x <= 5:
            return 90
        else:
            return 10

    def update_graph(self, graph, dt, alpha=None, n_mini_steps=500):
        if alpha is None:
            alpha = self.alpha
        points = np.append(
            graph.get_start_anchors(),
            [graph.get_last_point()],
            axis=0,
        )
        for k in range(n_mini_steps):
            y_change = np.zeros(points.shape[0])
            dx = points[1][0] - points[0][0]
            for i in range(len(points)):
                p = points[i]
                lp = points[max(i - 1, 0)]
                rp = points[min(i + 1, len(points) - 1)]
                d2y = (rp[1] - 2 * p[1] + lp[1])

                if (0 < i < len(points) - 1):
                    second_deriv = d2y / (dx**2)
                else:
                    second_deriv = 2 * d2y / (dx**2)
                    # second_deriv = 0

                y_change[i] = alpha * second_deriv * dt / n_mini_steps

            # y_change[0] = y_change[1]
            # y_change[-1] = y_change[-2]
            # y_change[0] = 0
            # y_change[-1] = 0
            # y_change -= np.mean(y_change)
            points[:, 1] += y_change
        graph.set_points_smoothly(points)
        return graph

    def get_second_derivative(self, x, dx=0.001):
        graph = self.graph
        x_min = self.graph_x_min
        x_max = self.graph_x_max

        ly, y, ry = [
            graph.point_from_proportion(
                inverse_interpolate(x_min, x_max, alt_x)
            )[1]
            for alt_x in (x - dx, x, x + dx)
        ]

        # At the boundary, don't return the second deriv,
        # but instead something matching the Neumann
        # boundary condition.
        if x == x_max:
            return (ly - y) / dx
        elif x == x_min:
            return (ry - y) / dx
        else:
            d2y = ry - 2 * y + ly
            return d2y / (dx**2)

    def get_rod(self, x_min, x_max, n_pieces=None):
        if n_pieces is None:
            n_pieces = self.default_n_rod_pieces
        axes = self.axes
        line = Line(axes.c2p(x_min, 0), axes.c2p(x_max, 0))
        rod = VGroup(*[
            Square()
            for n in range(n_pieces)
        ])
        rod.arrange(RIGHT, buff=0)
        rod.match_width(line)
        rod.set_height(0.2, stretch=True)
        rod.move_to(axes.c2p(x_min, 0), LEFT)
        rod.set_fill(opacity=1)
        rod.set_stroke(width=1)
        rod.set_sheen_direction(RIGHT)
        self.color_rod_by_graph(rod)
        return rod

    def update_rods(self, rods):
        for rod in rods:
            self.color_rod_by_graph(rod)

    def color_rod_by_graph(self, rod):
        for piece in rod:
            piece.set_color(color=[
                self.rod_point_to_color(piece.get_left()),
                self.rod_point_to_color(piece.get_right()),
            ])

    def rod_point_to_graph_y(self, point):
        axes = self.axes
        x = axes.x_axis.p2n(point)

        graph = self.graph
        alpha = inverse_interpolate(
            self.graph_x_min,
            self.graph_x_max,
            x,
        )
        return axes.y_axis.p2n(
            graph.point_from_proportion(alpha)
        )

    def y_to_color(self, y):
        return temperature_to_color((y - 45) / 45)

    def rod_point_to_color(self, point):
        return self.y_to_color(
            self.rod_point_to_graph_y(point)
        )


class ShowEvolvingTempGraphWithArrows(BringTwoRodsTogether):
    CONFIG = {
        "alpha": 0.1,
        "arrow_xs": np.linspace(0, 10, 22)[1:-1],
        "arrow_scale_factor": 0.5,
        "max_magnitude": 1.5,
        "wait_time": 30,
        "freq_amplitude_pairs": [
            (1, 0.5),
            (2, 1),
            (3, 0.5),
            (4, 0.3),
            (5, 0.3),
            (7, 0.2),
            (21, 0.1),
            (41, 0.05),
        ],
    }

    def construct(self):
        self.add_axes()
        self.add_graph()
        self.add_clock()
        self.add_rod()
        self.add_arrows()
        self.initialize_updaters()
        self.let_play()

    def add_axes(self):
        self.setup_axes()
        self.add(self.axes)

    def add_graph(self):
        self.setup_graph()
        self.add(self.graph)

    def add_clock(self):
        self.setup_clock()
        self.add(self.clock)
        self.add(self.time_label)
        self.time_label.next_to(self.clock, DOWN)

    def add_rod(self):
        rod = self.rod = self.get_rod(
            self.graph_x_min,
            self.graph_x_max,
        )
        self.add(rod)

    def add_arrows(self):
        graph = self.graph
        x_min = self.graph_x_min
        x_max = self.graph_x_max

        xs = self.arrow_xs
        arrows = VGroup(*[Vector(DOWN) for x in xs])
        asf = self.arrow_scale_factor

        def update_arrows(arrows):
            for x, arrow in zip(xs, arrows):
                d2y_dx2 = self.get_second_derivative(x)
                mag = asf * np.sign(d2y_dx2) * abs(d2y_dx2)
                mag = np.clip(
                    mag,
                    -self.max_magnitude,
                    self.max_magnitude,
                )
                arrow.put_start_and_end_on(
                    ORIGIN, mag * UP
                )
                point = graph.point_from_proportion(
                    inverse_interpolate(x_min, x_max, x)
                )
                arrow.shift(point - arrow.get_start())
                arrow.set_color(
                    self.rod_point_to_color(point)
                )

        arrows.add_updater(update_arrows)

        self.add(arrows)
        self.arrows = arrows

    def initialize_updaters(self):
        if hasattr(self, "graph"):
            self.graph.add_updater(self.update_graph)
        if hasattr(self, "rod"):
            self.rod.add_updater(self.color_rod_by_graph)
        if hasattr(self, "time_label"):
            self.time_label.add_updater(
                lambda d, dt: d.increment_value(dt)
            )

    def let_play(self):
        self.run_clock(self.wait_time)

    def run_clock(self, time):
        self.play(
            ClockPassesTime(
                self.clock,
                run_time=time,
                hours_passed=time,
            ),
        )

    #
    def temp_func(self, x, t):
        new_x = TAU * x / 10
        return 50 + 20 * np.sum([
            amp * np.sin(freq * new_x) *
            np.exp(-(self.alpha * freq**2) * t)
            for freq, amp in self.freq_amplitude_pairs
        ])

    def initial_function(self, x, time=0):
        return self.temp_func(x, 0)


class TalkThrough1DHeatGraph(ShowEvolvingTempGraphWithArrows, SpecialThreeDScene):
    CONFIG = {
        "freq_amplitude_pairs": [
            (1, 0.5),
            (2, 1),
            (3, 0.5),
            (4, 0.3),
            (5, 0.3),
            (7, 0.2),
        ],
        "surface_resolution": 20,
        "graph_slice_step": 10 / 20,
    }

    def construct(self):
        self.add_axes()
        self.add_graph()
        self.add_rod()

        self.emphasize_graph()
        self.emphasize_rod()
        self.show_x_axis()
        self.show_changes_over_time()
        self.show_surface()

    def add_graph(self):
        self.graph = self.get_graph()
        self.add(self.graph)

    def emphasize_graph(self):
        graph = self.graph
        q_marks = VGroup(*[
            TexMobject("?").move_to(
                graph.point_from_proportion(a),
                UP,
            ).set_stroke(BLACK, 3, background=True)
            for a in np.linspace(0, 1, 20)
        ])

        self.play(LaggedStart(*[
            Succession(
                FadeInFromLarge(q_mark),
                FadeOutAndShift(q_mark, DOWN),
            )
            for q_mark in q_marks
        ]))
        self.wait()

    def emphasize_rod(self):
        alt_rod = self.get_rod(0, 10, 50)
        word = TextMobject("Rod")
        word.scale(2)
        word.next_to(alt_rod, UP, MED_SMALL_BUFF)

        self.play(
            LaggedStart(
                *[
                    Rotating(piece, rate_func=smooth)
                    for piece in alt_rod
                ],
                run_time=2,
                lag_ratio=0.01,
            ),
            Write(word)
        )
        self.remove(*alt_rod)
        self.wait()

        self.rod_word = word

    def show_x_axis(self):
        rod = self.rod
        axes = self.axes
        graph = self.graph
        x_axis = axes.x_axis
        x_numbers = x_axis.get_number_mobjects(*range(1, 11))
        x_axis_label = TexMobject("x")
        x_axis_label.next_to(x_axis.get_right(), UP)

        self.play(
            rod.set_opacity, 0.5,
            FadeInFrom(x_axis_label, UL),
            LaggedStartMap(
                FadeInFrom, x_numbers,
                lambda m: (m, UP),
            )
        )
        self.wait()

        # Show x-values
        triangle = ArrowTip(
            start_angle=-90 * DEGREES,
            color=LIGHT_GREY,
        )
        x_tracker = ValueTracker(PI)
        get_x = x_tracker.get_value

        def get_x_point():
            return x_axis.n2p(get_x())

        def get_graph_point():
            return graph.point_from_proportion(
                inverse_interpolate(
                    self.graph_x_min,
                    self.graph_x_max,
                    get_x(),
                )
            )

        triangle.add_updater(
            lambda t: t.next_to(get_x_point(), UP)
        )
        x_label = VGroup(
            TexMobject("x"),
            TexMobject("="),
            DecimalNumber(
                0,
                num_decimal_places=3,
                include_background_rectangle=True,
            ).scale(0.9)
        )
        x_label.set_stroke(BLACK, 5, background=True)
        x_label.add_updater(lambda m: m[-1].set_value(get_x()))
        x_label.add_updater(lambda m: m.arrange(RIGHT, buff=SMALL_BUFF))
        x_label.add_updater(lambda m: m[-1].align_to(m[0], DOWN))
        x_label.add_updater(lambda m: m.next_to(triangle, UP, SMALL_BUFF))
        x_label.add_updater(lambda m: m.shift(SMALL_BUFF * RIGHT))
        rod_piece = always_redraw(
            lambda: self.get_rod(
                get_x() - 0.05, get_x() + 0.05,
                n_pieces=1,
            )
        )

        self.play(
            FadeInFrom(triangle, UP),
            FadeIn(x_label),
            FadeIn(rod_piece),
            FadeOut(self.rod_word),
        )
        for value in [np.exp(2), (np.sqrt(5) + 1) / 2]:
            self.play(x_tracker.set_value, value, run_time=2)
            self.wait()

        # Show graph
        v_line = always_redraw(
            lambda: DashedLine(
                get_x_point(),
                get_graph_point(),
                color=self.rod_point_to_color(get_x_point()),
            )
        )
        graph_dot = Dot()
        graph_dot.add_updater(
            lambda m: m.set_color(
                self.rod_point_to_color(m.get_center())
            )
        )
        graph_dot.add_updater(
            lambda m: m.move_to(get_graph_point())
        )
        t_label = TexMobject("T(", "x", ")")
        t_label.set_stroke(BLACK, 3, background=True)
        t_label.add_updater(
            lambda m: m.next_to(graph_dot, UR, buff=0)
        )

        self.add(v_line, rod_piece, x_label, triangle)
        self.play(
            TransformFromCopy(x_label[0], t_label[1]),
            FadeIn(t_label[0::2]),
            ShowCreation(v_line),
            GrowFromPoint(graph_dot, get_x_point()),
        )
        self.add(t_label)
        self.wait()
        self.play(
            x_tracker.set_value, TAU,
            run_time=5,
        )

        self.x_tracker = x_tracker
        self.graph_label_group = VGroup(
            v_line, rod_piece, triangle, x_label,
            graph_dot, t_label,
        )
        self.set_variables_as_attrs(*self.graph_label_group)
        self.set_variables_as_attrs(x_numbers, x_axis_label)

    def show_changes_over_time(self):
        graph = self.graph
        t_label = self.t_label
        new_t_label = TexMobject("T(", "x", ",", "t", ")")
        new_t_label.set_color_by_tex("t", YELLOW)
        new_t_label.match_updaters(t_label)

        self.setup_clock()
        clock = self.clock
        time_label = self.time_label
        time_group = self.time_group

        time = 5
        self.play(
            FadeIn(clock),
            FadeIn(time_group),
        )
        self.play(
            self.get_graph_time_change_animation(
                graph, time
            ),
            ClockPassesTime(clock),
            ChangeDecimalToValue(
                time_label, time,
                rate_func=linear,
            ),
            ReplacementTransform(
                t_label,
                new_t_label,
                rate_func=squish_rate_func(smooth, 0.5, 0.7),
            ),
            run_time=time
        )
        self.play(
            ShowCreationThenFadeAround(
                new_t_label.get_part_by_tex("t")
            ),
        )
        self.wait()
        self.play(
            FadeOut(clock),
            ChangeDecimalToValue(time_label, 0),
            VFadeOut(time_group),
            self.get_graph_time_change_animation(
                graph,
                new_time=0,
            ),
            run_time=1,
            rate_func=smooth,
        )

        self.graph_label_group.remove(t_label)
        self.graph_label_group.add(new_t_label)

    def show_surface(self):
        axes = self.axes
        graph = self.graph
        t_min = 0
        t_max = 10

        axes_copy = axes.deepcopy()
        self.original_axes = self.axes

        # Set rod final state
        final_graph = self.get_graph(t_max)
        curr_graph = self.graph
        self.graph = final_graph
        final_rod = self.rod.copy()
        final_rod.set_opacity(1)
        self.color_rod_by_graph(final_rod)
        self.graph = curr_graph

        # Time axis
        t_axis = NumberLine(
            x_min=t_min,
            x_max=t_max,
        )
        origin = axes.c2p(0, 0)
        t_axis.shift(origin - t_axis.n2p(0))
        t_axis.add_numbers(
            *range(1, t_max + 1),
            direction=UP,
        )
        time_label = TextMobject("Time")
        time_label.scale(1.5)
        time_label.next_to(t_axis, UP)
        t_axis.time_label = time_label
        t_axis.add(time_label)
        # t_axis.rotate(90 * DEGREES, LEFT, about_point=origin)
        t_axis.rotate(90 * DEGREES, UP, about_point=origin)

        # New parts of graph
        step = self.graph_slice_step
        graph_slices = VGroup(*[
            self.get_graph(time=t).shift(
                t * IN
            )
            for t in np.arange(0, t_max + step, step)
        ])
        graph_slices.set_stroke(width=1)
        graph_slices.set_shade_in_3d(True)

        # Input plane
        x_axis = self.axes.x_axis
        y = axes.c2p(0, 0)[1]
        surface_config = {
            "u_min": self.graph_x_min,
            "u_max": self.graph_x_max,
            "v_min": t_min,
            "v_max": t_max,
            "resolution": self.surface_resolution,
        }
        input_plane = ParametricSurface(
            lambda x, t: np.array([
                x_axis.n2p(x)[0],
                y,
                t_axis.n2p(t)[2],
            ]),
            **surface_config,
        )
        input_plane.set_style(
            fill_opacity=0.5,
            fill_color=BLUE_B,
            stroke_width=0.5,
            stroke_color=WHITE,
        )

        # Surface
        y_axis = axes.y_axis
        surface = ParametricSurface(
            lambda x, t: np.array([
                x_axis.n2p(x)[0],
                y_axis.n2p(self.temp_func(x, t))[1],
                t_axis.n2p(t)[2],
            ]),
            **surface_config,
        )
        surface.set_style(
            fill_opacity=0.1,
            fill_color=LIGHT_GREY,
            stroke_width=0.5,
            stroke_color=WHITE,
            stroke_opacity=0.5,
        )

        # Rotate everything on screen and move camera
        # in such a way that it looks the same
        curr_group = Group(*self.get_mobjects())
        curr_group.clear_updaters()
        self.set_camera_orientation(
            phi=90 * DEGREES,
        )
        mobs = [
            curr_group,
            graph_slices,
            t_axis,
            input_plane,
            surface,
        ]
        for mob in mobs:
            self.orient_mobject_for_3d(mob)

        # Clean current mobjects
        self.x_label.set_stroke(BLACK, 2, background=True)
        self.x_label[-1][0].fade(1)

        self.move_camera(
            phi=80 * DEGREES,
            theta=-85 * DEGREES,
            added_anims=[
                Write(input_plane),
                Write(t_axis),
                FadeOut(self.graph_label_group),
                self.rod.set_opacity, 1,
            ]
        )
        self.begin_ambient_camera_rotation()
        self.add(*graph_slices, *self.get_mobjects())
        self.play(
            FadeIn(surface),
            LaggedStart(*[
                TransformFromCopy(graph, graph_slice)
                for graph_slice in graph_slices
            ], lag_ratio=0.02)
        )
        self.wait(4)

        # Show slices
        self.axes = axes_copy  # So get_graph works...
        slicing_plane = Rectangle(
            stroke_width=0,
            fill_color=WHITE,
            fill_opacity=0.2,
        )
        slicing_plane.set_shade_in_3d(True)
        slicing_plane.replace(
            Line(axes_copy.c2p(0, 0), axes_copy.c2p(10, 100)),
            stretch=True
        )
        self.orient_mobject_for_3d(slicing_plane)

        def get_time_slice(t):
            new_slice = self.get_graph(t)
            new_slice.set_shade_in_3d(True)
            self.orient_mobject_for_3d(new_slice)
            new_slice.shift(t * UP)
            return new_slice

        graph.set_shade_in_3d(True)
        t_tracker = ValueTracker(0)
        graph.add_updater(lambda g: g.become(
            get_time_slice(t_tracker.get_value())
        ))

        self.orient_mobject_for_3d(final_rod)
        final_rod.shift(10 * UP)
        kw = {"run_time": 10, "rate_func": linear}
        self.rod.save_state()
        self.play(
            ApplyMethod(t_tracker.set_value, 10, **kw),
            Transform(self.rod, final_rod, **kw),
            ApplyMethod(slicing_plane.shift, 10 * UP, **kw),
        )
        self.wait()

        self.set_variables_as_attrs(
            t_axis,
            input_plane,
            surface,
            graph_slices,
            slicing_plane,
            t_tracker,
        )

    #
    def get_graph(self, time=0):
        graph = self.axes.get_graph(
            lambda x: self.temp_func(x, time),
            x_min=self.graph_x_min,
            x_max=self.graph_x_max,
            step_size=self.step_size,
        )
        graph.time = time
        graph.color_using_background_image("VerticalTempGradient")
        return graph

    def get_graph_time_change_animation(self, graph, new_time, **kwargs):
        old_time = graph.time
        graph.time = new_time
        config = {
            "run_time": abs(new_time - old_time),
            "rate_func": linear,
        }
        config.update(kwargs)

        return UpdateFromAlphaFunc(
            graph,
            lambda g, a: g.become(
                self.get_graph(interpolate(
                    old_time, new_time, a
                ))
            ),
            **config
        )

    def orient_mobject_for_3d(self, mob):
        mob.rotate(
            90 * DEGREES,
            axis=RIGHT,
            about_point=ORIGIN
        )
        return mob


class ContrastXChangesToTChanges(TalkThrough1DHeatGraph):
    CONFIG = {
        # "surface_resolution": 5,
        # "graph_slice_step": 1,
    }

    def construct(self):
        self.catchup_with_last_scene()
        self.emphasize_dimensions_of_input_space()
        self.reset_time_to_zero()

        self.show_changes_with_x()
        self.show_changes_with_t()

    def catchup_with_last_scene(self):
        self.force_skipping()

        self.add_axes()
        self.add_graph()
        self.add_rod()

        self.rod_word = Point()
        self.show_x_axis()
        self.show_surface()

        self.revert_to_original_skipping_status()

    def emphasize_dimensions_of_input_space(self):
        plane = self.input_plane
        plane_copy = plane.copy()
        plane_copy.set_color(BLUE_E)
        plane_copy.shift(SMALL_BUFF * 0.5 * OUT)

        plane_copy1 = plane_copy.copy()
        plane_copy1.stretch(0.01, 1, about_edge=DOWN)
        plane_copy0 = plane_copy1.copy()
        plane_copy0.stretch(0, 0, about_edge=LEFT)

        words = TextMobject("2d input\\\\space")
        words.scale(2)
        words.move_to(plane.get_center() + SMALL_BUFF * OUT)

        self.play(
            Write(words),
            self.camera.phi_tracker.set_value, 60 * DEGREES,
            self.camera.theta_tracker.set_value, -90 * DEGREES,
            run_time=1
        )
        self.play(
            ReplacementTransform(plane_copy0, plane_copy1)
        )
        self.play(
            ReplacementTransform(plane_copy1, plane_copy)
        )
        self.wait(2)
        self.play(FadeOut(plane_copy))

        self.input_plane_words = words

    def reset_time_to_zero(self):
        self.play(
            self.t_tracker.set_value, 0,
            VFadeOut(self.slicing_plane),
            Restore(self.rod),
        )

    def show_changes_with_x(self):
        alpha_tracker = ValueTracker(0)
        line = always_redraw(
            lambda: self.get_tangent_line(
                self.graph, alpha_tracker.get_value(),
            )
        )

        self.stop_ambient_camera_rotation()
        self.play(
            ShowCreation(line),
            FadeOut(self.input_plane_words),
            self.camera.phi_tracker.set_value, 80 * DEGREES,
            self.camera.theta_tracker.set_value, -90 * DEGREES,
        )
        self.play(
            alpha_tracker.set_value, 0.425,
            run_time=5,
            rate_func=bezier([0, 0, 1, 1]),
        )

        # Show dx and dT
        p0 = line.point_from_proportion(0.3)
        p2 = line.point_from_proportion(0.7)
        p1 = np.array([p2[0], *p0[1:]])
        dx_line = DashedLine(p0, p1)
        dT_line = DashedLine(p1, p2)
        dx = TexMobject("dx")
        dT = TexMobject("dT")
        VGroup(dx, dT).scale(0.7)
        VGroup(dx, dT).rotate(90 * DEGREES, RIGHT)
        dx.next_to(dx_line, IN, SMALL_BUFF)
        dT.next_to(dT_line, RIGHT, SMALL_BUFF)

        self.play(
            ShowCreation(dx_line),
            FadeInFrom(dx, LEFT)
        )
        self.wait()
        self.play(
            ShowCreation(dT_line),
            FadeInFrom(dT, IN)
        )
        self.wait()
        self.play(*map(FadeOut, [
            line, dx_line, dT_line, dx, dT,
        ]))

    def show_changes_with_t(self):
        slices = self.graph_slices
        slice_alpha = 0.075
        graph = VMobject()
        graph.set_points_smoothly([
            gs.point_from_proportion(slice_alpha)
            for gs in slices
        ])
        graph.color_using_background_image("VerticalTempGradient")
        graph.set_shade_in_3d(True)

        alpha_tracker = ValueTracker(0)
        line = always_redraw(
            lambda: self.get_tangent_line(
                graph, alpha_tracker.get_value(),
            )
        )

        plane = Square()
        plane.set_stroke(width=0)
        plane.set_fill(WHITE, 0.1)
        plane.set_shade_in_3d(True)
        plane.rotate(90 * DEGREES, RIGHT)
        plane.rotate(90 * DEGREES, OUT)
        plane.set_height(10)
        plane.set_depth(8, stretch=True)
        plane.move_to(self.t_axis.n2p(0), IN + DOWN)
        plane.shift(RIGHT)

        self.play(
            self.camera.theta_tracker.set_value, -20 * DEGREES,
            self.camera.frame_center.shift, 4 * LEFT,
        )

        self.play(
            ShowCreation(
                graph.copy(),
                remover=True
            ),
            FadeInFrom(plane, 6 * DOWN, run_time=2),
            VFadeIn(line),
            ApplyMethod(
                alpha_tracker.set_value, 1,
                run_time=8,
            ),
        )
        self.add(graph)

        self.begin_ambient_camera_rotation(-0.02)
        self.camera.frame_center.add_updater(
            lambda m, dt: m.shift(0.05 * dt * RIGHT)
        )

        self.play(
            FadeOut(line),
            FadeOut(plane),
        )
        self.wait(30)  # Let rotate

        self.t_graph = graph

    #
    def get_tangent_line(self, graph, alpha, d_alpha=0.001, length=2):
        if alpha < 1 - d_alpha:
            a1 = alpha
            a2 = alpha + d_alpha
        else:
            a1 = alpha - d_alpha
            a2 = alpha

        p1 = graph.point_from_proportion(a1)
        p2 = graph.point_from_proportion(a2)
        line = Line(p1, p2, color=WHITE)
        line.scale(
            length / line.get_length()
        )
        line.move_to(p1)
        return line


class TransitionToTempVsTime(ContrastXChangesToTChanges):
    CONFIG = {
        # "surface_resolution": 5,
        # "graph_slice_step": 1,
    }

    def construct(self):
        self.catchup_with_last_scene()

        axes = self.original_axes
        t_axis = self.t_axis
        y_axis = axes.y_axis
        x_axis = axes.x_axis

        for mob in self.get_mobjects():
            mob.clear_updaters()
        self.stop_ambient_camera_rotation()
        self.move_camera(
            phi=90 * DEGREES,
            theta=0 * DEGREES,
            added_anims=[
                Rotate(
                    y_axis, 90 * DEGREES,
                    axis=OUT,
                    about_point=y_axis.n2p(0),
                ),
                FadeOut(VGroup(
                    self.graph_slices,
                    self.surface,
                    self.slicing_plane,
                    self.rod,
                    self.graph,
                    self.x_numbers,
                    self.x_axis_label,
                    self.t_graph,
                )),
                self.camera.frame_center.move_to, 5 * LEFT,
            ]
        )
        self.play(
            VGroup(x_axis, self.input_plane).stretch,
            0, 0, {"about_point": y_axis.n2p(0)},
        )
        self.play(
            t_axis.time_label.scale, 1 / 1.5,
            t_axis.time_label.next_to, t_axis, IN, MED_LARGE_BUFF,
            t_axis.numbers.shift, 0.7 * IN,
        )
        self.wait()

    def catchup_with_last_scene(self):
        self.force_skipping()

        self.add_axes()
        self.add_graph()
        self.add_rod()

        self.rod_word = Point()
        self.show_x_axis()
        self.show_surface()

        self.emphasize_dimensions_of_input_space()
        self.reset_time_to_zero()

        self.show_changes_with_x()
        self.show_changes_with_t()

        self.revert_to_original_skipping_status()


class ShowDelTermsAsTinyNudges(TransitionToTempVsTime):
    CONFIG = {
        # "surface_resolution": 5,
        # "graph_slice_step": 1,
        "tangent_line_length": 4,
    }

    def construct(self):
        self.catchup_with_last_scene()
        self.stop_camera()
        self.show_del_t()
        self.show_del_x()

    def stop_camera(self):
        self.stop_ambient_camera_rotation()
        for mob in self.get_mobjects():
            mob.clear_updaters()

    def show_del_x(self):
        x_tracker = ValueTracker(3)
        dx_tracker = ValueTracker(0.5)

        line_group = self.get_line_group(
            self.graph,
            x_tracker,
            dx_tracker,
            corner_index=0,
        )
        dx_line, dT_line, tan_line = line_group

        del_x = TexMobject("\\partial x")
        del_x.set_color(GREEN)
        del_x.line = dx_line
        del_x.direction = OUT
        del_T = TexMobject("\\partial T")
        del_T.line = dT_line
        del_T.direction = RIGHT
        syms = VGroup(del_T, del_x)
        for sym in syms:
            sym.add_updater(lambda m: m.set_width(
                dx_line.get_length()
            ))
            sym.rect = SurroundingRectangle(sym)
            group = VGroup(sym, sym.rect)
            group.rotate(90 * DEGREES, RIGHT)

        for sym in syms:
            sym.add_updater(lambda m: m.next_to(
                m.line, m.direction, SMALL_BUFF,
            ))
            sym.rect.move_to(sym)

        self.move_camera(
            phi=80 * DEGREES,
            theta=-90 * DEGREES,
            added_anims=[
                self.camera.frame_center.move_to, ORIGIN,
            ],
        )
        for sym in reversed(syms):
            self.play(
                FadeInFrom(sym, -sym.direction),
                ShowCreation(
                    sym.line.copy(),
                    remover=True
                ),
            )
            self.add(sym.line)
        self.play(ShowCreation(tan_line))
        for sym in syms:
            self.play(
                ShowCreationThenDestruction(sym.rect)
            )
            self.wait()
        self.wait()
        self.add(line_group)
        self.play(
            dx_tracker.set_value, 0.01,
            run_time=5,
        )
        self.play(
            FadeOut(syms),
            FadeOut(line_group),
        )

    def show_del_t(self):
        # Largely copy pasted from above.
        # Reconsolidate if any of this will actually
        # be used later.
        t_tracker = ValueTracker(1)
        dt_tracker = ValueTracker(1)

        line_group = self.get_line_group(
            self.t_graph, t_tracker, dt_tracker,
            corner_index=1,
        )
        dt_line, dT_line, tan_line = line_group

        del_t = TexMobject("\\partial t")
        del_t.set_color(YELLOW)
        del_t.line = dt_line
        del_t.direction = OUT
        del_T = TexMobject("\\partial T")
        del_T.line = dT_line
        del_T.direction = UP
        syms = VGroup(del_T, del_t)
        for sym in syms:
            sym.rect = SurroundingRectangle(sym)
            group = VGroup(sym, sym.rect)
            group.rotate(90 * DEGREES, RIGHT)
            group.rotate(90 * DEGREES, OUT)
            sym.add_updater(lambda m: m.set_height(
                0.8 * dT_line.get_length()
            ))

        del_t.add_updater(lambda m: m.set_height(
            min(0.5, m.line.get_length())
        ))
        del_T.add_updater(lambda m: m.set_depth(
            min(0.5, m.line.get_length())
        ))
        for sym in syms:
            sym.add_updater(lambda m: m.next_to(
                m.line, m.direction, SMALL_BUFF,
            ))
            sym.rect.move_to(sym)

        self.move_camera(
            phi=80 * DEGREES,
            theta=-10 * DEGREES,
            added_anims=[
                self.camera.frame_center.move_to, 5 * LEFT,
            ],
        )
        for sym in reversed(syms):
            self.play(
                FadeInFrom(sym, -sym.direction),
                ShowCreation(
                    sym.line.copy(),
                    remover=True
                ),
            )
            self.add(sym.line)
        self.play(ShowCreation(tan_line))
        for sym in syms:
            self.play(
                ShowCreationThenDestruction(sym.rect)
            )
            self.wait()
        self.wait()
        self.add(line_group)
        self.play(
            dt_tracker.set_value, 0.01,
            run_time=5,
        )
        self.play(
            FadeOut(syms),
            FadeOut(line_group),
        )

    #
    def get_line_group(self, graph, input_tracker, nudge_tracker, corner_index):
        get_x = input_tracker.get_value
        get_dx = nudge_tracker.get_value

        def get_graph_point(x):
            return graph.point_from_proportion(
                inverse_interpolate(
                    self.graph_x_min,
                    self.graph_x_max,
                    x,
                )
            )

        def get_corner(p1, p2):
            result = np.array(p1)
            result[corner_index] = p2[corner_index]
            return result

        line_group = VGroup(
            Line(color=WHITE),
            Line(color=RED),
            Line(color=WHITE, stroke_width=2),
        )

        def update_line_group(group):
            dxl, dTl, tl = group
            p0 = get_graph_point(get_x())
            p2 = get_graph_point(get_x() + get_dx())
            p1 = get_corner(p0, p2)

            dxl.set_points_as_corners([p0, p1])
            dTl.set_points_as_corners([p1, p2])
            tl.set_points_as_corners([p0, p2])
            tl.scale(
                self.tangent_line_length / tl.get_length()
            )
        line_group.add_updater(update_line_group)
        return line_group


class ShowCurvatureToRateOfChangeIntuition(ShowEvolvingTempGraphWithArrows):
    CONFIG = {
        "freq_amplitude_pairs": [
            (1, 0.7),
            (2, 1),
            (3, 0.5),
            (4, 0.3),
            (5, 0.3),
            (7, 0.2),
        ],
        "arrow_xs": [0.7, 3.8, 4.6, 5.4, 6.2, 9.3],
        "arrow_scale_factor": 0.2,
        "max_magnitude": 1.0,
        "wait_time": 20,
    }

    def let_play(self):
        arrows = self.arrows
        curves = VGroup(*[
            self.get_mini_curve(
                inverse_interpolate(
                    self.graph_x_min,
                    self.graph_x_max,
                    x,
                )
            )
            for x in self.arrow_xs
        ])
        curves.set_stroke(WHITE, 5)

        curve_words = VGroup()
        for curve, arrow in zip(curves, arrows):
            word = TextMobject("curve")
            word.scale(0.7)
            word.next_to(curve, arrow.get_vector()[1] * DOWN, SMALL_BUFF)
            curve_words.add(word)

        self.remove(arrows)

        self.play(
            ShowCreation(curves),
            LaggedStartMap(FadeIn, curve_words),
            self.y_label.set_fill, {"opacity": 0},
        )
        self.wait()
        self.add(*arrows, curves)
        self.play(LaggedStartMap(GrowArrow, arrows))
        self.wait()

        self.play(FadeOut(VGroup(curves, curve_words)))
        self.add(arrows)
        super().let_play()

    def get_mini_curve(self, alpha, d_alpha=0.02):
        result = VMobject()
        result.pointwise_become_partial(
            self.graph,
            alpha - d_alpha,
            alpha + d_alpha,
        )
        return result


class DiscreteSetup(ShowEvolvingTempGraphWithArrows):
    CONFIG = {
        "step_size": 1,
        "rod_piece_size_ratio": 1 / 3,
        "dashed_line_stroke_opacity": 1.0,
        "dot_radius": DEFAULT_DOT_RADIUS,
        "freq_amplitude_pairs": [
            (1, 0.5),
            (2, 1),
            (3, 0.5),
            (4, 0.3),
            (5, 0.3),
            (7, 0.2),
            (21, 0.1),
            # (41, 0.05),
        ],
    }

    def construct(self):
        self.add_axes()
        self.add_graph()
        self.discretize()
        self.let_time_pass()
        self.show_nieghbor_rule()
        self.focus_on_three_points()
        self.show_difference_formula()
        self.gut_check_new_interpretation()
        self.write_second_difference()
        self.emphasize_final_expression()

    def add_axes(self):
        super().add_axes()
        self.axes.shift(MED_SMALL_BUFF * LEFT)

    def add_graph(self):
        points = self.get_points(time=0)
        graph = VMobject()
        graph.set_points_smoothly(points)
        graph.color_using_background_image("VerticalTempGradient")

        self.add(graph)

        self.graph = graph
        self.points = points

    def discretize(self):
        axes = self.axes
        x_axis = axes.x_axis
        graph = self.graph

        piecewise_graph = CurvesAsSubmobjects(graph)
        dots = self.get_dots()
        v_lines = VGroup(*map(self.get_v_line, dots))

        rod_pieces = VGroup()
        for x in self.get_sample_inputs():
            piece = Line(LEFT, RIGHT)
            piece.set_width(
                self.step_size * self.rod_piece_size_ratio
            )
            piece.move_to(axes.c2p(x, 0))
            piece.set_color(
                self.rod_point_to_color(piece.get_center())
            )
            rod_pieces.add(piece)

        word = TextMobject("Discrete version")
        word.scale(1.5)
        word.next_to(x_axis, UP)
        word.set_stroke(BLACK, 3, background=True)

        self.remove(graph)
        self.play(
            ReplacementTransform(
                piecewise_graph, dots,
            ),
            Write(word, run_time=1)
        )
        self.add(v_lines, word)
        self.play(
            x_axis.fade, 0.8,
            TransformFromCopy(
                x_axis.tick_marks[1:],
                rod_pieces,
            ),
            LaggedStartMap(ShowCreation, v_lines)
        )
        self.play(FadeOut(word))
        self.wait()

        self.rod_pieces = rod_pieces
        self.dots = dots
        self.v_lines = v_lines

    def let_time_pass(self):
        dots = self.dots

        t_tracker = ValueTracker(0)
        t_tracker.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(t_tracker)

        self.add_clock()
        self.time_label.next_to(self.clock, DOWN)
        self.time_label.add_updater(
            lambda m: m.set_value(t_tracker.get_value())
        )
        dots.add_updater(lambda d: d.become(
            self.get_dots(t_tracker.get_value())
        ))
        run_time = 5
        self.play(
            ClockPassesTime(
                self.clock,
                run_time=run_time,
                hours_passed=run_time,
            ),
        )
        t_tracker.clear_updaters()
        t_tracker.set_value(run_time)
        self.wait()
        self.play(
            t_tracker.set_value, 0,
            FadeOut(self.clock),
            FadeOut(self.time_label),
        )
        self.remove(t_tracker)
        dots.clear_updaters()

    def show_nieghbor_rule(self):
        dots = self.dots
        rod_pieces = self.rod_pieces
        index = self.index = 2

        p1, p2, p3 = rod_pieces[index:index + 3]
        d1, d2, d3 = dots[index:index + 3]
        point_label = TextMobject("Point")
        neighbors_label = TextMobject("Neighbors")
        words = VGroup(point_label, neighbors_label)
        for word in words:
            word.scale(0.7)
            word.add_background_rectangle()

        point_label.next_to(p2, DOWN)
        neighbors_label.next_to(p2, UP, buff=1)
        bottom = neighbors_label.get_bottom()
        kw = {
            "buff": 0.1,
            "stroke_width": 2,
            "tip_length": 0.15
        }
        arrows = VGroup(
            Arrow(bottom, p1.get_center(), **kw),
            Arrow(bottom, p3.get_center(), **kw),
        )
        arrows.set_color(WHITE)

        dot = Dot()
        dot.set_fill(GREY, opacity=0.2)
        dot.replace(p2)
        dot.scale(3)

        self.play(
            dot.scale, 0,
            dot.set_opacity, 0,
            FadeInFrom(point_label, DOWN)
        )
        self.play(
            FadeInFrom(neighbors_label, DOWN),
            *map(GrowArrow, arrows)
        )
        self.wait()

        # Let d2 change
        self.play(
            d1.set_y, 3,
            d3.set_y, 3,
        )

        def get_v():
            return 0.25 * np.sum([
                d1.get_y(),
                -2 * d2.get_y(),
                + d3.get_y(),
            ])
        v_vect_fader = ValueTracker(0)
        v_vect = always_redraw(
            lambda: Vector(
                get_v() * UP,
                color=temperature_to_color(
                    get_v(), -2, 2,
                ),
            ).shift(d2.get_center()).set_opacity(
                v_vect_fader.get_value(),
            )
        )
        d2.add_updater(
            lambda d, dt: d.shift(
                get_v() * dt * UP,
            )
        )

        self.add(v_vect)
        self.play(v_vect_fader.set_value, 1)
        self.wait(3)
        self.play(
            d1.set_y, 0,
            d3.set_y, 0,
        )
        self.wait(4)
        self.play(FadeOut(VGroup(
            point_label,
            neighbors_label,
            arrows
        )))

        self.v_vect = v_vect
        self.example_pieces = VGroup(p1, p2, p3)
        self.example_dots = VGroup(d1, d2, d3)

    def focus_on_three_points(self):
        dots = self.example_dots
        d1, d2, d3 = dots
        pieces = self.example_pieces
        y_axis = self.axes.y_axis

        x_labels, T_labels = [
            VGroup(*[
                TexMobject("{}_{}".format(s, i))
                for i in [1, 2, 3]
            ]).scale(0.8)
            for s in ("x", "T")
        ]
        for xl, piece in zip(x_labels, pieces):
            xl.next_to(piece, DOWN)
            xl.add_background_rectangle()
        for Tl, dot in zip(T_labels, dots):
            Tl.dot = dot
            Tl.add_updater(lambda m: m.next_to(
                m.dot, RIGHT, SMALL_BUFF
            ))
            Tl.add_background_rectangle()
        T1, T2, T3 = T_labels

        d2.movement_updater = d2.get_updaters()[0]
        dots.clear_updaters()
        self.remove(self.v_vect)

        self.play(
            ShowCreationThenFadeAround(pieces),
            FadeOut(self.dots[:self.index]),
            FadeOut(self.v_lines[:self.index]),
            FadeOut(self.rod_pieces[:self.index]),
            FadeOut(self.dots[self.index + 3:]),
            FadeOut(self.v_lines[self.index + 3:]),
            FadeOut(self.rod_pieces[self.index + 3:]),
        )
        self.play(LaggedStartMap(
            FadeInFrom, x_labels,
            lambda m: (m, LEFT),
            lag_ratio=0.3,
            run_time=2,
        ))
        self.play(
            d3.set_y, 1,
            d2.set_y, 0.25,
            d1.set_y, 0,
        )
        self.wait()
        self.play(LaggedStart(*[
            TransformFromCopy(xl, Tl)
            for xl, Tl in zip(x_labels, T_labels)
        ], lag_ratio=0.3, run_time=2))
        self.wait()

        # Show lines
        h_lines = VGroup(*map(self.get_h_line, dots))
        hl1, hl2, hl3 = h_lines

        average_pointer = ArrowTip(
            start_angle=0,
            length=0.2,
        )
        average_pointer.set_color(YELLOW)
        average_pointer.stretch(0.25, 1)
        average_pointer.add_updater(
            lambda m: m.move_to(
                0.5 * (hl1.get_start() + hl3.get_start()),
                RIGHT
            )
        )
        average_arrows = always_redraw(lambda: VGroup(*[
            Arrow(
                hl.get_start(),
                average_pointer.get_right(),
                color=WHITE,
                buff=0.0,
            )
            for hl in [hl1, hl3]
        ]))
        average_label = TexMobject(
            "{T_1", "+", "T_3", "\\over", "2}"
        )
        average_label.scale(0.5)
        average_label.add_updater(lambda m: m.next_to(
            average_pointer, LEFT, SMALL_BUFF
        ))

        average_rect = SurroundingRectangle(average_label)
        average_rect.add_updater(
            lambda m: m.move_to(average_label)
        )
        average_words = TextMobject("Neighbor\\\\average")
        average_words.match_width(average_rect)
        average_words.match_color(average_rect)
        average_words.add_updater(
            lambda m: m.next_to(average_rect, UP, SMALL_BUFF)
        )

        mini_T1 = average_label.get_part_by_tex("T_1")
        mini_T3 = average_label.get_part_by_tex("T_3")
        for mini, line in (mini_T1, hl1), (mini_T3, hl3):
            mini.save_state()
            mini.next_to(line, LEFT, SMALL_BUFF)

        self.add(hl1, hl3, T_labels)
        y_axis.remove(y_axis.numbers)
        self.play(
            GrowFromPoint(hl1, hl1.get_end()),
            GrowFromPoint(hl3, hl3.get_end()),
            TransformFromCopy(
                T1, mini_T1,
            ),
            TransformFromCopy(
                T3, mini_T3,
            ),
            FadeOut(y_axis.numbers),
            y_axis.set_stroke, {"width": 1},
        )
        self.play(
            FadeIn(average_pointer),
            Restore(mini_T1),
            Restore(mini_T3),
            FadeIn(average_label[1]),
            FadeIn(average_label[3:]),
            *map(GrowArrow, average_arrows)
        )
        self.add(average_arrows, average_label)
        self.play(
            ShowCreation(average_rect),
            FadeIn(average_words),
        )
        self.play(
            GrowFromPoint(hl2, hl2.get_end())
        )
        self.wait()

        # Show formula
        formula = TexMobject(
            "\\left(",
            "{T_1", "+", "T_3", "\\over", "2}",
            "-", "T_2",
            "\\right)"
        )
        formula.to_corner(UR, buff=MED_LARGE_BUFF)
        formula.shift(1.7 * LEFT)
        brace = Brace(formula, DOWN)
        diff_value = DecimalNumber(include_sign=True)
        diff_value.add_updater(lambda m: m.set_value(
            y_axis.p2n(average_pointer.get_right()) -
            y_axis.p2n(d2.get_center())
        ))
        diff_value.next_to(brace, DOWN)

        self.play(
            ReplacementTransform(
                average_label.deepcopy(),
                formula[1:1 + len(average_label)]
            ),
            TransformFromCopy(T2, formula[-2]),
            FadeIn(formula[-3]),
            FadeIn(formula[-1]),
            FadeIn(formula[0]),
            GrowFromCenter(brace),
            FadeIn(diff_value)
        )
        self.wait()

        # Changes
        self.play(FadeIn(self.v_vect))
        d2.add_updater(d2.movement_updater)
        self.wait(5)

        self.play(
            d3.set_y, 3,
            d1.set_y, 2.5,
            d2.set_y, -2,
        )
        self.wait(5)
        self.play(
            d3.set_y, 1,
            d1.set_y, -1,
        )
        self.wait(8)

        # Show derivative
        lhs = TexMobject(
            "{dT_2", "\\over", "dt}", "=", "\\alpha"
        )
        dt = lhs.get_part_by_tex("dt")
        alpha = lhs.get_part_by_tex("\\alpha")
        lhs.next_to(formula, LEFT, SMALL_BUFF)

        self.play(Write(lhs))
        self.play(ShowCreationThenFadeAround(dt))
        self.wait()
        self.play(ShowCreationThenFadeAround(alpha))
        self.wait()
        self.play(
            FadeOut(brace),
            FadeOut(diff_value),
        )

        self.lhs = lhs
        self.rhs = formula

    def show_difference_formula(self):
        lhs = self.lhs
        rhs = self.rhs
        d1, d2, d3 = self.example_dots

        new_rhs = TexMobject(
            "=",
            "{\\alpha", "\\over", "2}",
            "\\left(",
            "(", "T_3", "-", "T_2", ")",
            "-",
            "(", "T_2", "-", "T_1", ")",
            "\\right)"
        )
        big_parens = VGroup(
            new_rhs.get_part_by_tex("\\left("),
            new_rhs.get_part_by_tex("\\right)"),
        )
        for paren in big_parens:
            paren.scale(2)
        new_rhs.next_to(rhs, DOWN)
        new_rhs.align_to(lhs.get_part_by_tex("="), LEFT)

        def p2p_anim(mob1, mob2, tex, index=0):
            return TransformFromCopy(
                mob1.get_parts_by_tex(tex)[index],
                mob2.get_parts_by_tex(tex)[index],
            )

        self.play(
            p2p_anim(lhs, new_rhs, "="),
            p2p_anim(rhs, new_rhs, "\\left("),
            p2p_anim(rhs, new_rhs, "\\right)"),
            p2p_anim(lhs, new_rhs, "\\alpha"),
            p2p_anim(rhs, new_rhs, "\\over"),
            p2p_anim(rhs, new_rhs, "2"),
        )
        self.play(
            p2p_anim(rhs, new_rhs, "T_3"),
            p2p_anim(rhs, new_rhs, "-"),
            p2p_anim(rhs, new_rhs, "T_2"),
            FadeIn(new_rhs.get_parts_by_tex("(")[1]),
            FadeIn(new_rhs.get_parts_by_tex(")")[0]),
        )
        self.play(
            p2p_anim(rhs, new_rhs, "T_2", -1),
            p2p_anim(rhs, new_rhs, "-", -1),
            p2p_anim(rhs, new_rhs, "T_1"),
            FadeIn(new_rhs.get_parts_by_tex("-")[1]),
            FadeIn(new_rhs.get_parts_by_tex("(")[2]),
            FadeIn(new_rhs.get_parts_by_tex(")")[1]),
        )
        self.wait()

        self.rhs2 = new_rhs

        # Show deltas
        T1_index = new_rhs.index_of_part_by_tex("T_1")
        T3_index = new_rhs.index_of_part_by_tex("T_3")
        diff1 = new_rhs[T1_index - 2:T1_index + 1]
        diff2 = new_rhs[T3_index:T3_index + 3]
        brace1 = Brace(diff1, DOWN, buff=SMALL_BUFF)
        brace2 = Brace(diff2, DOWN, buff=SMALL_BUFF)
        delta_T1 = TexMobject("\\Delta T_1")
        delta_T1.next_to(brace1, DOWN, SMALL_BUFF)
        delta_T2 = TexMobject("\\Delta T_2")
        delta_T2.next_to(brace2, DOWN, SMALL_BUFF)
        minus = TexMobject("-")
        minus.move_to(Line(
            delta_T1.get_right(),
            delta_T2.get_left(),
        ))
        braces = VGroup(brace1, brace2)
        deltas = VGroup(delta_T1, delta_T2)

        kw = {
            "direction": LEFT,
            "buff": SMALL_BUFF,
            "min_num_quads": 2,
        }
        lil_brace1 = always_redraw(lambda: Brace(
            Line(d1.get_left(), d2.get_left()), **kw
        ))
        lil_brace2 = always_redraw(lambda: Brace(
            Line(d2.get_left(), d3.get_left()), **kw
        ))
        lil_braces = VGroup(lil_brace1, lil_brace2)
        lil_delta_T1 = delta_T1.copy()
        lil_delta_T2 = delta_T2.copy()
        lil_deltas = VGroup(lil_delta_T1, lil_delta_T2)
        for brace, delta in zip(lil_braces, lil_deltas):
            delta.brace = brace
            delta.add_updater(lambda d: d.next_to(
                d.brace, LEFT, SMALL_BUFF,
            ))

        delta_T1.set_color(BLUE)
        lil_delta_T1.set_color(BLUE)
        delta_T2.set_color(RED)
        lil_delta_T2.set_color(RED)

        double_difference_brace = Brace(deltas, DOWN)
        double_difference_words = TextMobject(
            "Difference of differences"
        )
        double_difference_words.next_to(
            double_difference_brace, DOWN
        )

        self.play(
            GrowFromCenter(brace1),
            GrowFromCenter(lil_brace1),
            FadeIn(delta_T1),
            FadeIn(lil_delta_T1),
        )
        self.wait()
        self.play(
            GrowFromCenter(brace2),
            GrowFromCenter(lil_brace2),
            FadeIn(delta_T2),
            FadeIn(lil_delta_T2),
        )
        self.wait()
        self.play(
            Write(minus),
            GrowFromCenter(double_difference_brace),
            Write(double_difference_words),
        )
        self.wait()

        self.braces = braces
        self.deltas = deltas
        self.delta_minus = minus
        self.lil_braces = lil_braces
        self.lil_deltas = lil_deltas
        self.double_difference_brace = double_difference_brace
        self.double_difference_words = double_difference_words

    def gut_check_new_interpretation(self):
        lil_deltas = self.lil_deltas
        d1, d2, d3 = self.example_dots

        self.play(ShowCreationThenFadeAround(lil_deltas[0]))
        self.play(ShowCreationThenFadeAround(lil_deltas[1]))
        self.wait()
        self.play(
            d2.shift, MED_SMALL_BUFF * UP,
            rate_func=there_and_back,
        )
        self.wait()
        self.play(
            d3.set_y, 3,
            d1.set_y, -0.5,
        )
        self.wait(5)
        self.play(
            d3.set_y, 1.5,
            d1.set_y, -2,
        )
        self.wait(5)

    def write_second_difference(self):
        dd_word = self.double_difference_words

        delta_delta = TexMobject("\\Delta \\Delta T_1")
        delta_delta.set_color(MAROON_B)

        delta_delta.move_to(dd_word, UP)

        second_difference_word = TextMobject(
            "``Second difference''"
        )
        second_difference_word.next_to(delta_delta, DOWN)

        self.play(
            FadeOutAndShift(dd_word, UP),
            FadeInFrom(delta_delta, UP),
        )
        self.wait()
        self.play(
            Write(second_difference_word),
        )
        self.wait()

        # Random play
        d1, d2, d3 = self.example_dots
        self.play(
            d3.set_y, 3,
            d1.set_y, -0.5,
        )
        self.wait(5)
        self.play(
            d3.set_y, 1.5,
            d1.set_y, -2,
        )
        self.wait(5)

        self.delta_delta = delta_delta
        self.second_difference_word = second_difference_word

    def emphasize_final_expression(self):
        lhs = self.lhs
        rhs = self.rhs
        rhs2 = self.rhs2
        old_dd = self.delta_delta
        dd = old_dd.copy()
        old_ao2 = rhs2[1:4]
        ao2 = old_ao2.copy()

        new_lhs = lhs[:-1]
        full_rhs = VGroup(
            lhs[-1],
            lhs[-2].copy(),
            rhs,
            rhs2,
            self.braces,
            self.deltas,
            self.delta_minus,
            self.double_difference_brace,
            old_dd,
            self.second_difference_word,
        )
        new_rhs = VGroup(ao2, dd)
        new_rhs.arrange(RIGHT, buff=SMALL_BUFF)
        new_rhs.next_to(new_lhs, RIGHT)

        self.play(
            full_rhs.to_edge, DOWN, {"buff": LARGE_BUFF},
        )
        self.play(
            TransformFromCopy(old_ao2, ao2),
            TransformFromCopy(old_dd, dd),
        )
        self.play(
            ShowCreationThenFadeAround(
                VGroup(new_lhs, new_rhs)
            )
        )
        self.wait()

    #
    def get_sample_inputs(self):
        return np.arange(
            self.graph_x_min,
            self.graph_x_max + self.step_size,
            self.step_size,
        )

    def get_points(self, time=0):
        return [
            self.axes.c2p(x, self.temp_func(x, t=time))
            for x in self.get_sample_inputs()
        ]

    def get_dots(self, time=0):
        points = self.get_points(time)
        dots = VGroup(*[
            Dot(
                point,
                radius=self.dot_radius
            )
            for point in points
        ])
        dots.color_using_background_image("VerticalTempGradient")
        return dots

    def get_dot_dashed_line(self, dot, index, color=False):
        direction = np.zeros(3)
        direction[index] = -1

        def get_line():
            p1 = dot.get_edge_center(direction)
            p0 = np.array(p1)
            p0[index] = self.axes.c2p(0, 0)[index]
            result = DashedLine(
                p0, p1,
                stroke_width=2,
                color=WHITE,
                stroke_opacity=self.dashed_line_stroke_opacity,
            )
            if color:
                result.color_using_background_image(
                    "VerticalTempGradient"
                )
            return result
        return always_redraw(get_line)

    def get_h_line(self, dot):
        return self.get_dot_dashed_line(dot, 0, True)

    def get_v_line(self, dot):
        return self.get_dot_dashed_line(dot, 1)


class ShowFinitelyManyX(DiscreteSetup):
    def construct(self):
        self.setup_axes()
        axes = self.axes
        axes.fade(1)
        points = [
            axes.c2p(x, 0)
            for x in self.get_sample_inputs()[1:]
        ]
        x_labels = VGroup(*[
            TexMobject("x_{}".format(i)).next_to(
                p, DOWN
            )
            for i, p in enumerate(points)
        ])

        self.play(LaggedStartMap(
            FadeInFromLarge, x_labels
        ))
        self.play(LaggedStartMap(FadeOut, x_labels))
        self.wait()


class DiscreteGraphStillImage1(DiscreteSetup):
    CONFIG = {
        "step_size": 1,
    }

    def construct(self):
        self.add_axes()
        self.add_graph()
        self.discretize()


class DiscreteGraphStillImageFourth(DiscreteGraphStillImage1):
    CONFIG = {
        "step_size": 0.25,
    }


class DiscreteGraphStillImageTenth(DiscreteGraphStillImage1):
    CONFIG = {
        "step_size": 0.1,
        "dashed_line_stroke_opacity": 0.25,
        "dot_radius": 0.04,
    }


class DiscreteGraphStillImageHundredth(DiscreteGraphStillImage1):
    CONFIG = {
        "step_size": 0.01,
        "dashed_line_stroke_opacity": 0.1,
        "dot_radius": 0.01,
    }


class TransitionToContinuousCase(DiscreteSetup):
    CONFIG = {
        "step_size": 0.1,
        "tangent_line_length": 3,
        "wait_time": 30,
    }

    def construct(self):
        self.add_axes()
        self.add_graph()
        self.show_temperature_difference()
        self.show_second_derivative()
        self.show_curvature_examples()
        self.show_time_changes()

    def add_graph(self):
        self.setup_graph()
        self.play(
            ShowCreation(
                self.graph,
                run_time=3,
            )
        )
        self.wait()

    def show_temperature_difference(self):
        x_tracker = ValueTracker(2)
        dx_tracker = ValueTracker(1)

        line_group = self.get_line_group(
            x_tracker,
            dx_tracker,
        )
        dx_line, dT_line, tan_line, dx_sym, dT_sym = line_group
        tan_line.set_stroke(width=0)

        brace = Brace(dx_line, UP)
        fixed_distance = TextMobject("Fixed\\\\distance")
        fixed_distance.scale(0.7)
        fixed_distance.next_to(brace, UP)
        delta_T = TexMobject("\\Delta T")
        delta_T.move_to(dT_sym, LEFT)

        self.play(
            ShowCreation(VGroup(dx_line, dT_line)),
            FadeInFrom(delta_T, LEFT)
        )
        self.play(
            GrowFromCenter(brace),
            FadeInFromDown(fixed_distance),
        )
        self.wait()
        self.play(
            FadeOut(delta_T, UP),
            FadeIn(dT_sym, DOWN),
            FadeOut(brace, UP),
            FadeOut(fixed_distance, UP),
            FadeIn(dx_sym, DOWN),
        )
        self.add(line_group)
        self.play(
            dx_tracker.set_value, 0.01,
            run_time=5
        )
        self.wait()
        self.play(
            dx_tracker.set_value, 0.3,
        )

        # Show rate of change
        to_zero = TexMobject("\\rightarrow 0")
        to_zero.match_height(dT_sym)
        to_zero.next_to(dT_sym, buff=SMALL_BUFF)

        ratio = TexMobject(
            "{\\partial T", "\\over", "\\partial x}"
        )
        ratio[0].match_style(dT_sym)
        ratio.to_edge(UP)

        self.play(ShowCreationThenFadeAround(
            dT_sym,
            surrounding_rectangle_config={
                "buff": 0.05,
                "stroke_width": 1,
            }
        ))
        self.play(GrowFromPoint(to_zero, dT_sym.get_right()))
        self.wait()
        self.play(
            TransformFromCopy(
                dT_sym,
                ratio.get_part_by_tex("\\partial T")
            ),
            TransformFromCopy(
                dx_sym,
                ratio.get_part_by_tex("\\partial x")
            ),
            Write(ratio.get_part_by_tex("\\over"))
        )
        self.play(
            ShowCreation(
                tan_line.copy().set_stroke(width=2),
                remover=True
            ),
            FadeOut(to_zero),
        )
        tan_line.set_stroke(width=2)
        self.wait()

        # Look at neighbors
        x0 = x_tracker.get_value()
        dx = dx_tracker.get_value()
        v_line, lv_line, rv_line = v_lines = VGroup(*[
            self.get_v_line(x)
            for x in [x0, x0 - dx, x0 + dx]
        ])
        v_lines[1:].set_color(BLUE)

        self.play(ShowCreation(v_line))
        self.play(
            TransformFromCopy(v_line, lv_line),
            TransformFromCopy(v_line, rv_line),
        )
        self.wait()
        self.play(
            FadeOut(v_lines[1:]),
            ApplyMethod(
                dx_tracker.set_value, 0.01,
                run_time=2
            ),
        )

        self.line_group = line_group
        self.deriv = ratio
        self.x_tracker = x_tracker
        self.dx_tracker = dx_tracker
        self.v_line = v_line

    def show_second_derivative(self):
        x_tracker = self.x_tracker
        deriv = self.deriv
        v_line = self.v_line

        deriv_of_deriv = TexMobject(
            "{\\partial",
            "\\left(",
            "{\\partial T", "\\over", "\\partial x}",
            "\\right)",
            "\\over",
            "\\partial x}"
        )
        deriv_of_deriv.set_color_by_tex("\\partial T", RED)

        deriv_of_deriv.to_edge(UP)
        dT_index = deriv_of_deriv.index_of_part_by_tex("\\partial T")
        inner_deriv = deriv_of_deriv[dT_index:dT_index + 3]

        self.play(
            ReplacementTransform(deriv, inner_deriv),
            Write(VGroup(*filter(
                lambda m: m not in inner_deriv,
                deriv_of_deriv,
            )))
        )
        v_line.add_updater(lambda m: m.become(
            self.get_v_line(x_tracker.get_value())
        ))
        for change in [-0.1, 0.1]:
            self.play(
                x_tracker.increment_value, change,
                run_time=3
            )

        # Write second deriv
        second_deriv = TexMobject(
            "{\\partial^2 T", "\\over", "\\partial x^2}"
        )
        second_deriv[0].set_color(RED)
        eq = TexMobject("=")
        eq.next_to(deriv_of_deriv, RIGHT)
        second_deriv.next_to(eq, RIGHT)
        second_deriv.align_to(deriv_of_deriv, DOWN)
        eq.match_y(second_deriv.get_part_by_tex("\\over"))

        self.play(Write(eq))
        self.play(
            TransformFromCopy(
                deriv_of_deriv.get_parts_by_tex("\\partial")[:2],
                second_deriv.get_parts_by_tex("\\partial^2 T"),
            ),
        )
        self.play(
            Write(second_deriv.get_part_by_tex("\\over")),
            TransformFromCopy(
                deriv_of_deriv.get_parts_by_tex("\\partial x"),
                second_deriv.get_parts_by_tex("\\partial x"),
            ),
        )
        self.wait()

    def show_curvature_examples(self):
        x_tracker = self.x_tracker
        v_line = self.v_line
        line_group = self.line_group

        x_tracker.set_value(3.6)
        self.wait()
        self.play(
            x_tracker.set_value, 3.8,
            run_time=4,
        )
        self.wait()
        x_tracker.set_value(6.2)
        self.wait()
        self.play(
            x_tracker.set_value, 6.4,
            run_time=4,
        )
        self.wait()

        #
        dx = 0.2
        neighbor_lines = always_redraw(lambda: VGroup(*[
            self.get_v_line(
                x_tracker.get_value() + u * dx,
                line_class=Line,
            )
            for u in [-1, 1]
        ]))
        neighbor_lines.set_color(BLUE)

        self.play(FadeOut(line_group))
        self.play(*[
            TransformFromCopy(v_line, nl)
            for nl in neighbor_lines
        ])
        self.add(neighbor_lines)
        self.play(
            x_tracker.set_value, 5,
            run_time=5,
            rate_func=lambda t: smooth(t, 3)
        )
        v_line.clear_updaters()
        self.play(
            FadeOut(v_line),
            FadeOut(neighbor_lines),
        )
        self.wait()

    def show_time_changes(self):
        self.setup_clock()
        graph = self.graph

        time_label = self.time_label
        clock = self.clock
        time_label.next_to(clock, DOWN)

        graph.add_updater(self.update_graph)
        time_label.add_updater(
            lambda d, dt: d.increment_value(dt)
        )

        self.add(time_label)
        self.add_arrows()
        self.play(
            ClockPassesTime(
                clock,
                run_time=self.wait_time,
                hours_passed=self.wait_time,
            ),
        )

    #
    def get_v_line(self, x, line_class=DashedLine, stroke_width=2):
        axes = self.axes
        graph = self.graph
        line = line_class(
            axes.c2p(x, 0),
            graph.point_from_proportion(
                inverse_interpolate(
                    self.graph_x_min,
                    self.graph_x_max,
                    x,
                )
            ),
            stroke_width=stroke_width,
        )
        return line

    def get_line_group(self,
                       x_tracker,
                       dx_tracker,
                       dx_tex="\\partial x",
                       dT_tex="\\partial T",
                       max_sym_width=0.5,
                       ):
        graph = self.graph
        get_x = x_tracker.get_value
        get_dx = dx_tracker.get_value

        dx_line = Line(color=WHITE)
        dT_line = Line(color=RED)
        tan_line = Line(color=WHITE)
        lines = VGroup(dx_line, dT_line, tan_line)
        lines.set_stroke(width=2)
        dx_sym = TexMobject(dx_tex)
        dT_sym = TexMobject(dT_tex)
        dT_sym.match_color(dT_line)
        syms = VGroup(dx_sym, dT_sym)

        group = VGroup(*lines, *syms)

        def update_group(group):
            dxl, dTl, tanl, dxs, dTs = group
            x = get_x()
            dx = get_dx()
            p0, p2 = [
                graph.point_from_proportion(
                    inverse_interpolate(
                        self.graph_x_min,
                        self.graph_x_max,
                        x
                    )
                )
                for x in [x, x + dx]
            ]
            p1 = np.array([p2[0], *p0[1:]])
            dxl.put_start_and_end_on(p0, p1)
            dTl.put_start_and_end_on(p1, p2)
            tanl.put_start_and_end_on(p0, p2)
            tanl.scale(
                self.tangent_line_length /
                tanl.get_length()
            )
            dxs.match_width(dxl)
            dTs.set_height(0.7 * dTl.get_height())
            for sym in dxs, dTs:
                if sym.get_width() > max_sym_width:
                    sym.set_width(max_sym_width)
            dxs.next_to(
                dxl, -dTl.get_vector(), SMALL_BUFF,
            )
            dTs.next_to(
                dTl, dxl.get_vector(), SMALL_BUFF,
            )

        group.add_updater(update_group)
        return group


class ShowManyVLines(TransitionToContinuousCase):
    CONFIG = {
        "wait_time": 20,
        "max_denom": 10,
        "x_step": 0.025,
    }

    def construct(self):
        self.add_axes()
        self.add_graph()
        self.add_v_lines()
        self.show_time_changes()

    def add_arrows(self):
        pass

    def add_v_lines(self):
        axes = self.axes

        v_lines = always_redraw(lambda: VGroup(*[
            self.get_v_line(
                x,
                line_class=Line,
                stroke_width=0.5,
            )
            for x in np.arange(0, 10, self.x_step)
        ]))
        group = VGroup(*v_lines)

        x_pointer = ArrowTip(start_angle=PI / 2)
        x_pointer.set_color(WHITE)
        x_pointer.next_to(axes.c2p(0, 0), DOWN, buff=0)
        x_eq = VGroup(
            TexMobject("x="),
            DecimalNumber(0)
        )
        x_eq.add_updater(
            lambda m: m.arrange(RIGHT, buff=SMALL_BUFF)
        )
        x_eq.add_updater(
            lambda m: m[1].set_value(axes.x_axis.p2n(x_pointer.get_top()))
        )
        x_eq.add_updater(lambda m: m.next_to(
            x_pointer, DOWN, SMALL_BUFF,
            submobject_to_align=x_eq[0]
        ))

        self.add(x_pointer, x_eq)
        self.play(
            Write(
                group,
                remover=True,
                lag_ratio=self.x_step / 2,
                run_time=6,
            ),
            ApplyMethod(
                x_pointer.next_to,
                axes.c2p(10, 0),
                DOWN, {"buff": 0},
                rate_func=linear,
                run_time=5,
            ),
        )
        self.add(v_lines)
        x_eq.clear_updaters()
        self.play(
            FadeOut(x_eq),
            FadeOut(x_pointer),
        )


class ShowNewtonsLawGraph(Scene):
    CONFIG = {
        "k": 0.2,
        "initial_water_temp": 80,
        "room_temp": 20,
        "delta_T_color": YELLOW,
    }

    def construct(self):
        self.setup_axes()
        self.show_temperatures()
        self.show_graph()
        self.show_equation()
        self.talk_through_examples()

    def setup_axes(self):
        axes = Axes(
            x_min=0,
            x_max=10,
            y_min=0,
            y_max=100,
            y_axis_config={
                "unit_size": 0.06,
                "tick_frequency": 10,
            },
            center_point=5 * LEFT + 2.5 * DOWN
        )
        x_axis = axes.x_axis
        y_axis = axes.y_axis
        y_axis.add_numbers(*range(20, 100, 20))
        x_axis.add_numbers(*range(1, 11))

        x_axis.label = TextMobject("Time")
        x_axis.label.next_to(x_axis, DOWN, MED_SMALL_BUFF)

        y_axis.label = TexMobject("\\text{Temperature}")
        y_axis.label.next_to(y_axis, RIGHT, buff=SMALL_BUFF)
        y_axis.label.align_to(axes, UP)
        for axis in [x_axis, y_axis]:
            axis.add(axis.label)

        self.add(axes)
        self.axes = axes

    def show_temperatures(self):
        axes = self.axes

        water_dot = Dot()
        water_dot.color_using_background_image("VerticalTempGradient")
        water_dot.move_to(axes.c2p(0, self.initial_water_temp))
        room_line = DashedLine(
            axes.c2p(0, self.room_temp),
            axes.c2p(10, self.room_temp),
        )
        room_line.set_color(BLUE)
        room_line.color_using_background_image("VerticalTempGradient")

        water_arrow = Vector(LEFT, color=WHITE)
        water_arrow.next_to(water_dot, RIGHT, SMALL_BUFF)
        water_words = TextMobject(
            "Initial water\\\\temperature"
        )
        water_words.scale(0.7)
        water_words.next_to(water_arrow, RIGHT)

        room_words = TextMobject("Room temperature")
        room_words.scale(0.7)
        room_words.next_to(room_line, DOWN, SMALL_BUFF)

        self.play(
            FadeInFrom(water_dot, RIGHT),
            GrowArrow(water_arrow),
            Write(water_words),
            run_time=1,
        )
        self.play(ShowCreation(room_line))
        self.play(FadeInFromDown(room_words))
        self.wait()

        self.set_variables_as_attrs(
            water_dot,
            water_arrow,
            water_words,
            room_line,
            room_words,
        )

    def show_graph(self):
        axes = self.axes
        water_dot = self.water_dot

        k = self.k
        rt = self.room_temp
        t0 = self.initial_water_temp
        graph = axes.get_graph(
            lambda t: rt + (t0 - rt) * np.exp(-k * t)
        )
        graph.color_using_background_image("VerticalTempGradient")

        def get_x():
            return axes.x_axis.p2n(water_dot.get_center())

        brace_line = always_redraw(lambda: Line(
            axes.c2p(get_x(), rt),
            water_dot.get_center(),
            stroke_width=0,
        ))
        brace = always_redraw(
            lambda: Brace(
                brace_line, RIGHT, buff=SMALL_BUFF
            )
        )

        delta_T = TexMobject("\\Delta T")
        delta_T.set_color(self.delta_T_color)
        delta_T.add_updater(lambda m: m.next_to(
            brace, RIGHT, SMALL_BUFF
        ))

        self.add(brace_line)
        self.play(
            GrowFromCenter(brace),
            Write(delta_T),
        )
        self.play(
            ShowCreation(graph),
            UpdateFromFunc(
                water_dot,
                lambda m: m.move_to(graph.get_end())
            ),
            run_time=10,
            rate_func=linear,
        )
        self.wait()

        self.graph = graph
        self.brace = brace
        self.delta_T = delta_T

    def show_equation(self):
        delta_T = self.delta_T

        equation = TexMobject(
            "{d ({\\Delta T}) \\over dt} = -k \\cdot {\\Delta T}",
            tex_to_color_map={
                "{\\Delta T}": self.delta_T_color,
                "-k": WHITE,
                "=": WHITE,
            }
        )
        equation.to_corner(UR)
        equation.shift(LEFT)

        delta_T_parts = equation.get_parts_by_tex("\\Delta T")
        eq_i = equation.index_of_part_by_tex("=")
        deriv = equation[:eq_i]
        prop_to = equation.get_part_by_tex("-k")
        parts = VGroup(deriv, prop_to, delta_T_parts[1])

        words = TextMobject(
            "Rate of change",
            "is proportional to",
            "itself",
        )
        words.scale(0.7)
        words.next_to(equation, DOWN)
        colors = [BLUE, WHITE, YELLOW]
        for part, word, color in zip(parts, words, colors):
            part.word = word
            word.set_color(color)
            word.save_state()
        words[0].next_to(parts[0], DOWN)

        self.play(
            TransformFromCopy(
                VGroup(delta_T),
                delta_T_parts,
            ),
            Write(VGroup(*filter(
                lambda p: p not in delta_T_parts,
                equation
            )))
        )

        rects = VGroup()
        for part in parts:
            rect = SurroundingRectangle(
                part,
                color=part.word.get_color(),
                buff=SMALL_BUFF,
                stroke_width=2,
            )
            anims = [
                ShowCreation(rect),
                FadeIn(part.word),
            ]
            if part is parts[1]:
                anims.append(Restore(words[0]))
            self.play(*anims)
            rects.add(rect)

        self.play(FadeOut(rects, lag_ratio=0.2))

        self.equation = equation
        self.equation_words = words

    def talk_through_examples(self):
        dot = self.water_dot
        graph = self.graph

        self.play(
            MoveAlongPath(
                dot, graph,
                rate_func=lambda t: smooth(1 - t),
                run_time=2,
            )
        )

    #
    def get_slope_line(self, graph, x):
        pass
