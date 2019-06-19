from manimlib.imports import *
from active_projects.ode.part2.heat_equation import *


class ShowNewRuleAtDiscreteBoundary(DiscreteSetup):
    CONFIG = {
        "axes_config": {
            "x_min": 0,
            "stroke_width": 1,
            "x_axis_config": {
                "include_tip": False,
            },
        },
        "freq_amplitude_pairs": [
            (1, 0.5),
            (2, 1),
            (3, 0.5),
            (4, 0.3),
        ],
        "v_line_class": DashedLine,
        "v_line_config": {

        },
        "step_size": 1,
        "wait_time": 15,
        "alpha": 0.25,
    }

    def construct(self):
        self.add_axes()
        self.set_points()
        self.show_boundary_point_influenced_by_neighbor()
        self.add_clock()
        self.let_evolve()

    def set_points(self):
        axes = self.axes
        for mob in axes.family_members_with_points():
            if isinstance(mob, Line):
                mob.set_stroke(width=1)

        step_size = self.step_size
        xs = np.arange(
            axes.x_min,
            axes.x_max + step_size,
            step_size
        )

        dots = self.dots = self.get_dots(axes, xs)
        self.v_lines = self.get_v_lines(dots)
        self.rod_pieces = self.get_rod_pieces(dots)

        # rod_pieces

        self.add(self.dots)
        self.add(self.v_lines)
        self.add(self.rod_pieces)

    def show_boundary_point_influenced_by_neighbor(self):
        dots = self.dots
        ld = dots[0]
        ld_in = dots[1]
        rd = dots[-1]
        rd_in = dots[-2]
        v_len = 0.75
        l_arrow = Vector(v_len * LEFT)
        l_arrow.move_to(ld.get_left(), RIGHT)
        r_arrow = Vector(v_len * RIGHT)
        r_arrow.move_to(rd.get_right(), LEFT)
        arrows = VGroup(l_arrow, r_arrow)
        q_marks = VGroup(*[
            TexMobject("?").scale(1.5).next_to(
                arrow, arrow.get_vector()
            )
            for arrow in arrows
        ])

        arrows.set_color(YELLOW)
        q_marks.set_color(YELLOW)

        blocking_rects = VGroup(*[
            BackgroundRectangle(VGroup(
                *dots[i:-i],
                *self.rod_pieces[i:-i]
            ))
            for i in [1, 2]
        ])
        for rect in blocking_rects:
            rect.stretch(1.1, dim=1, about_edge=UP)

        self.play(FadeIn(blocking_rects[0]))
        self.play(
            LaggedStartMap(ShowCreation, arrows),
            LaggedStart(*[
                FadeInFrom(q_mark, -arrow.get_vector())
                for q_mark, arrow in zip(q_marks, arrows)
            ]),
            run_time=1.5
        )
        self.wait()

        # Point to inward neighbor
        new_arrows = VGroup(*[
            Arrow(
                d1.get_center(),
                VGroup(d1, d2).get_center(),
                buff=0,
            ).match_style(l_arrow)
            for d1, d2 in [(ld, ld_in), (rd, rd_in)]
        ])
        new_arrows.match_style(arrows)

        l_brace = Brace(VGroup(ld, ld_in), DOWN)
        r_brace = Brace(VGroup(rd, rd_in), DOWN)
        braces = VGroup(l_brace, r_brace)
        for brace in braces:
            brace.align_to(
                self.axes.x_axis.get_center(), UP
            )
            brace.shift(SMALL_BUFF * DOWN)
            brace.add(brace.get_tex("\\Delta x"))

        self.play(
            ReplacementTransform(arrows, new_arrows),
            FadeOut(q_marks),
            ReplacementTransform(*blocking_rects)
        )
        self.wait()
        self.play(FadeInFrom(braces, UP))
        self.wait()
        self.play(
            FadeOut(new_arrows),
            FadeOut(blocking_rects[1]),
            FadeOut(braces),
        )

    def add_clock(self):
        super().add_clock()
        self.time_label.add_updater(
            lambda d, dt: d.increment_value(dt)
        )
        VGroup(
            self.clock,
            self.time_label
        ).shift(2 * LEFT)

    def let_evolve(self):
        dots = self.dots
        dots.add_updater(self.update_dots)

        wait_time = self.wait_time
        self.play(
            ClockPassesTime(
                self.clock,
                run_time=wait_time,
                hours_passed=wait_time,
            ),
        )

    #

    def get_dots(self, axes, xs):
        dots = VGroup(*[
            Dot(axes.c2p(x, self.temp_func(x, 0)))
            for x in xs
        ])

        max_width = 0.8 * self.step_size
        for dot in dots:
            dot.add_updater(self.update_dot_color)
            if dot.get_width() > max_width:
                dot.set_width(max_width)

        return dots

    def get_v_lines(self, dots):
        return always_redraw(lambda: VGroup(*[
            self.get_v_line(dot)
            for dot in dots
        ]))

    def get_v_line(self, dot):
        x_axis = self.axes.x_axis
        bottom = dot.get_bottom()
        x = x_axis.p2n(bottom)
        proj_point = x_axis.n2p(x)
        return self.v_line_class(
            proj_point, bottom,
            **self.v_line_config,
        )

    def get_rod_pieces(self, dots):
        axis = self.axes.x_axis
        factor = 1 - np.exp(-(0.8 / self.step_size)**2)
        width = factor * self.step_size

        pieces = VGroup()
        for dot in dots:
            piece = Line(ORIGIN, width * RIGHT)
            piece.set_stroke(width=5)
            piece.move_to(dot)
            piece.set_y(axis.get_center()[1])
            piece.dot = dot
            piece.add_updater(
                lambda p: p.match_color(p.dot)
            )
            pieces.add(piece)
        return pieces

    def update_dot_color(self, dot):
        y = self.axes.y_axis.p2n(dot.get_center())
        dot.set_color(self.y_to_color(y))

    def update_dots(self, dots, dt):
        for ds in zip(dots, dots[1:], dots[2:]):
            points = [d.get_center() for d in ds]
            x0, x1, x2 = [p[0] for p in points]
            dx = x1 - x0
            y0, y1, y2 = [p[1] for p in points]
            
            self.update_dot(
                dot=ds[1],
                dt=dt,
                mean_diff=0.5 * (y2 - 2 * y1 + y0) / dx
            )
            if ds[0] is dots[0]:
                self.update_dot(
                    dot=ds[0],
                    dt=dt,
                    mean_diff=(y1 - y0) / dx
                )
            elif ds[-1] is dots[-1]:
                self.update_dot(
                    dot=ds[-1],
                    dt=dt,
                    mean_diff=(y1 - y2) / dx
                )

    def update_dot(self, dot, dt, mean_diff):
        dot.shift(mean_diff * self.alpha * dt * UP)


class DiscreteEvolutionPoint25(ShowNewRuleAtDiscreteBoundary):
    CONFIG = {
        "step_size": 0.25,
        "alpha": 0.5,
        "wait_time": 30,
    }

    def construct(self):
        self.add_axes()
        self.set_points()
        self.add_clock()
        self.let_evolve()


class DiscreteEvolutionPoint1(DiscreteEvolutionPoint25):
    CONFIG = {
        "step_size": 0.1,
        "v_line_config": {
            "stroke_width": 1,
        },
        "wait_time": 30,
    }


class FlatEdgesForDiscreteEvolution(DiscreteEvolutionPoint1):
    CONFIG = {
        "wait_time": 20,
        "step_size": 0.1,
    }

    def let_evolve(self):
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

        super().let_evolve()

    def update_lines(self, lines):
        dots = self.dots
        for line, dot in zip(lines, [dots[0], dots[-1]]):
            line.move_to(dot)


class FlatEdgesForDiscreteEvolutionTinySteps(FlatEdgesForDiscreteEvolution):
    CONFIG = {
        "step_size": 0.025,
        "wait_time": 10,
        "v_line_class": Line,
        "v_line_config": {
            "stroke_opacity": 0.5,
        }
    }
