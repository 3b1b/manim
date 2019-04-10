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

    def get_rod(self, x_min, x_max, n_pieces=20):
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
    def initial_function(self, x):
        new_x = TAU * x / 10
        return 50 + 20 * np.sum([
            np.sin(new_x),
            np.sin(2 * new_x),
            0.5 * np.sin(3 * new_x),
            0.3 * np.sin(4 * new_x),
            0.3 * np.sin(5 * new_x),
            0.2 * np.sin(7 * new_x),
            0.1 * np.sin(21 * new_x),
            0.05 * np.sin(41 * new_x),
        ])


class TalkThrough1DHeatGraph(ShowEvolvingTempGraphWithArrows):
    def construct(self):
        self.add_axes()
        self.add_graph()
        self.add_rod()

    #
    def initial_function(self, x):
        new_x = TAU * x / 10
        return 50 + 20 * np.sum([
            np.sin(new_x),
            np.sin(2 * new_x),
            0.5 * np.sin(3 * new_x),
            0.3 * np.sin(4 * new_x),
            0.3 * np.sin(5 * new_x),
            0.2 * np.sin(7 * new_x),
        ])
