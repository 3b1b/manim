from big_ol_pile_of_manim_imports import *
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
        axes.y_axis.add(y_label)
        axes.y_axis.add_numbers(
            *range(20, 100, 20)
        )

        self.axes = axes

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

    def update_graph(self, graph, dt, alpha=None, n_mini_steps=100):
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
                    second_deriv = 0.5 * d2y / dx
                    second_deriv = 0

                y_change[i] = alpha * second_deriv * dt / n_mini_steps

            # y_change[0] = y_change[1]
            # y_change[-1] = y_change[-2]
            y_change[0] = 0
            y_change[-1] = 0
            y_change -= np.mean(y_change)
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

    def rod_point_to_color(self, point):
        axes = self.axes
        x = axes.x_axis.p2n(point)

        graph = self.graph
        alpha = inverse_interpolate(
            self.graph_x_min,
            self.graph_x_max,
            x,
        )
        y = axes.y_axis.p2n(
            graph.point_from_proportion(alpha)
        )
        return temperature_to_color(
            (y - 45) / 45
        )


class ShowEvolvingTempGraphWithArrows(BringTwoRodsTogether):
    CONFIG = {
        "alpha": 0.1,
        "n_arrows": 20,
        "wait_time": 30,
        "freq_amplitude_pairs": [
            (1, 1),
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

    def add_rod(self):
        rod = self.rod = self.get_rod(0, 10)
        self.add(rod)

    def add_arrows(self):
        graph = self.graph
        x_min = self.graph_x_min
        x_max = self.graph_x_max

        xs = np.linspace(x_min, x_max, self.n_arrows + 2)[1:-1]
        arrows = VGroup(*[Vector(DOWN) for x in xs])

        def update_arrows(arrows):
            for x, arrow in zip(xs, arrows):
                d2y_dx2 = self.get_second_derivative(x)
                mag = np.sign(d2y_dx2) * np.sqrt(abs(d2y_dx2))
                mag = np.clip(mag, -2, 2)
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

    def let_play(self):
        graph = self.graph
        rod = self.rod
        clock = self.clock
        time_label = self.time_label

        graph.add_updater(self.update_graph)
        time_label.add_updater(
            lambda d, dt: d.increment_value(dt)
        )
        rod.add_updater(self.color_rod_by_graph)

        # return
        self.play(
            ClockPassesTime(
                clock,
                run_time=self.wait_time,
                hours_passed=self.wait_time,
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
            (1, 0.7),
            (2, 1),
            (3, 0.5),
            (4, 0.3),
            (5, 0.3),
            (7, 0.2),
        ],
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
        original_axes = self.axes

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
        step = 0.25
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
            "resolution": 20,
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
            fill_opacity=0,
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
        self.play(
            ApplyMethod(t_tracker.set_value, 10, **kw),
            Transform(self.rod, final_rod, **kw),
            ApplyMethod(slicing_plane.shift, 10 * UP, **kw),
        )
        graph.clear_updaters()
        self.wait()

        self.set_variables_as_attrs(
            t_axis,
            input_plane,
            surface,
            graph_slices,
            slicing_plane,
        )
        self.axes = original_axes

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


class TransitionToTempVsTime(TalkThrough1DHeatGraph):
    def construct(self):
        self.force_skipping()

        # super().construct()
        self.add_axes()
        self.add_graph()
        self.add_rod()

        # self.emphasize_graph()
        # self.emphasize_rod()
        self.rod_word = Point()
        self.show_x_axis()
        # self.show_changes_over_time()
        self.show_surface()

        self.revert_to_original_skipping_status()

        axes = self.axes
        t_axis = self.t_axis
        y_axis = axes.y_axis
        x_axis = axes.x_axis

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
                )),
                self.camera.frame_center.shift, 5 * LEFT,
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


class ShowNewtonsLawGraph(Scene):
    CONFIG = {
        "k": 0.2,
        "initial_water_temp": 80,
        "room_temp": 20,
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
            "Initial water temperature"
        )
        water_words.next_to(water_arrow, RIGHT)

        room_words = TextMobject("Room temperature")
        room_words.next_to(room_line, DOWN, SMALL_BUFF)

        self.play(
            FadeInFrom(water_dot, RIGHT),
            GrowArrow(water_arrow),
            Write(water_words),
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
        brace = Brace(brace_line, RIGHT, SMALL_BUFF)
        brace.add_updater(lambda b: b.match_height(brace_line))
        brace.add_updater(lambda b: b.next_to(brace_line, RIGHT, SMALL_BUFF))

        self.add(graph)

    def show_equation(self):
        pass

    def talk_through_examples(self):
        pass
