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
    def construct(self):
        pass
