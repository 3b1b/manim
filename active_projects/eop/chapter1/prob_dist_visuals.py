from manimlib.imports import *
from active_projects.eop.reusable_imports import *


class ProbabilityDistributions(PiCreatureScene):

    CONFIG = {
        "default_pi_creature_kwargs": {
        "color": MAROON_E,
        "flip_at_start": False,
        },
    }

    def construct(self):

        lag_ratio = 0.2
        run_time = 3
        

# WEATHER FORECAST

    
        unit_rect = Rectangle(
            height = 3, width = 3
        ).shift(DOWN)

        p_rain = 0.23
        p_sun = 1 - p_rain
        opacity = 0.7

        rain_rect = unit_rect.copy().stretch(p_rain, 0)
        rain_rect.align_to(unit_rect, LEFT)
        rain_rect.set_fill(color = BLUE, opacity = opacity)
        rain_rect.set_stroke(width = 0)

        sun_rect = unit_rect.copy().stretch(p_sun, 0)
        sun_rect.next_to(rain_rect, RIGHT, buff = 0)
        sun_rect.set_fill(color = YELLOW, opacity = opacity)
        sun_rect.set_stroke(width = 0)

        self.add(unit_rect, rain_rect, sun_rect)

        rain = SVGMobject(file_name = "rain").scale(0.25)
        sun = SVGMobject(file_name = "sun").scale(0.35)

        rain.flip().move_to(rain_rect)
        sun.move_to(sun_rect)

        self.add(rain, sun)


        text_scale =  0.7

        brace_rain = Brace(rain_rect, UP)
        p_rain_label = TextMobject("$P($rain$)=$").scale(text_scale)
        p_rain_decimal = DecimalNumber(p_rain).scale(text_scale)
        p_rain_decimal.next_to(p_rain_label)
        p_rain_whole_label = VGroup(p_rain_label, p_rain_decimal)
        p_rain_whole_label.next_to(brace_rain, UP)

        brace_sun = Brace(sun_rect, DOWN)
        p_sun_label = TextMobject("$P($sunshine$)=$").scale(text_scale)
        p_sun_decimal = DecimalNumber(p_sun).scale(text_scale)
        p_sun_decimal.next_to(p_sun_label)
        p_sun_whole_label = VGroup(p_sun_label, p_sun_decimal)
        p_sun_whole_label.next_to(brace_sun, DOWN)

        self.add(brace_rain, p_rain_whole_label, brace_sun, p_sun_whole_label)

        self.wait(6)



        # new_p_rain = 0.68
        # new_p_sun = 1 - new_p_rain

        # new_rain_rect = unit_rect.copy().stretch(new_p_rain, 0)
        # new_rain_rect.align_to(unit_rect, LEFT)
        # new_rain_rect.set_fill(color = BLUE, opacity = opacity)
        # new_rain_rect.set_stroke(width = 0)

        # new_sun_rect = unit_rect.copy().stretch(new_p_sun, 0)
        # new_sun_rect.next_to(new_rain_rect, RIGHT, buff = 0)
        # new_sun_rect.set_fill(color = YELLOW, opacity = opacity)
        # new_sun_rect.set_stroke(width = 0)

        # new_rain = SVGMobject(file_name = "rain").scale(0.35)
        # new_sun = SVGMobject(file_name = "sun").scale(0.35)

        # new_rain.flip().move_to(new_rain_rect)
        # new_sun.move_to(new_sun_rect)

        # new_brace_rain = Brace(new_rain_rect, UP)
        # new_p_rain_label = TextMobject("$P($rain$)=$").scale(text_scale)
        # new_p_rain_decimal = DecimalNumber(new_p_rain).scale(text_scale)
        # new_p_rain_decimal.next_to(new_p_rain_label)
        # new_p_rain_whole_label = VGroup(new_p_rain_label, new_p_rain_decimal)
        # new_p_rain_whole_label.next_to(new_brace_rain, UP)

        
        # new_brace_sun = Brace(new_sun_rect, DOWN)
        # new_p_sun_label = TextMobject("$P($sunshine$)=$").scale(text_scale)
        # new_p_sun_decimal = DecimalNumber(new_p_sun).scale(text_scale)
        # new_p_sun_decimal.next_to(new_p_sun_label)
        # new_p_sun_whole_label = VGroup(new_p_sun_label, new_p_sun_decimal)
        # new_p_sun_whole_label.next_to(new_brace_sun, DOWN)

        # def rain_update_func(alpha):
        #     return alpha * new_p_rain + (1 - alpha) * p_rain

        # def sun_update_func(alpha):
        #     return 1 - rain_update_func(alpha)

        # update_p_rain = ChangingDecimal(
        #     p_rain_decimal, rain_update_func,
        #     tracked_mobject = p_rain_label,
        #     run_time = run_time
        # )
        # update_p_sun = ChangingDecimal(
        #     p_sun_decimal, sun_update_func,
        #     tracked_mobject = p_sun_label,
        #     run_time = run_time
        # )

        # self.play(
        #     Transform(rain_rect, new_rain_rect, run_time = run_time),
        #     Transform(sun_rect, new_sun_rect, run_time = run_time),
        #     Transform(rain, new_rain, run_time = run_time),
        #     Transform(sun, new_sun, run_time = run_time),
        #     Transform(brace_rain, new_brace_rain, run_time = run_time),
        #     Transform(brace_sun, new_brace_sun, run_time = run_time),
        #     Transform(p_rain_label, new_p_rain_label, run_time = run_time),
        #     Transform(p_sun_label, new_p_sun_label, run_time = run_time),
        #     update_p_rain,
        #     update_p_sun
        # )



        # move the forecast into a corner

        forecast = VGroup(
            rain_rect, sun_rect, rain, sun, brace_rain, brace_sun,
            p_rain_whole_label, p_sun_whole_label, unit_rect
        )

        forecast.target = forecast.copy().scale(0.5)
        forecast.target.to_corner(UL)

        self.play(MoveToTarget(forecast))

        self.play(
            FadeOut(brace_rain),
            FadeOut(brace_sun),
            FadeOut(p_rain_whole_label),
            FadeOut(p_sun_whole_label),
        )

        self.wait(3)


# DOUBLE DICE THROW

        cell_size = 0.5
        dice_table = TwoDiceTable(cell_size = cell_size, label_scale = 0.7)
        dice_table.shift(0.8 * DOWN)
        dice_unit_rect = SurroundingRectangle(
            dice_table.cells, buff = 0,
            stroke_color=WHITE
        )

        dice_table_grouped_cells = VGroup()

        for i in range(6):
            dice_table_grouped_cells.add(VGroup(*[
                VGroup(
                    dice_table.cells[6 * i - 5 * k],
                    dice_table.labels[6 * i - 5 * k],
                )
                for k in range(i + 1)
            ]))

        for i in range(5):
            dice_table_grouped_cells.add(VGroup(*[
                VGroup(
                    dice_table.cells[31 + i - 5 * k],
                    dice_table.labels[31 + i - 5 * k],
                )
                for k in range(5 - i)
            ]))

        # self.play(
        #     FadeIn(dice_unit_rect),
        #     FadeIn(dice_table.rows)
        # )

        # for (cell, label) in zip(dice_table.cells, dice_table.labels):
        #     cell.add(label)

        # self.play(
        #     LaggedStartMap(FadeIn, dice_table_grouped_cells,
        #         lag_ratio = lag_ratio, run_time = run_time)
        # )
        self.play(
            FadeIn(dice_table_grouped_cells),
            FadeIn(dice_unit_rect),
            FadeIn(dice_table.rows)
        )

        self.wait(3)


        self.play(
            dice_table_grouped_cells.space_out_submobjects, {"factor" : 1.5},
            rate_func=there_and_back_with_pause,
            run_time=run_time
        )

        dice_table.add(dice_unit_rect)
        dice_table_target = dice_table.deepcopy()
        dice_table_target.scale(0.5)
        dice_table_target.to_corner(UR, buff=LARGE_BUFF)
        dice_table_target.shift(0.4 * UP)

        self.play(Transform(dice_table, dice_table_target))

        self.play(
            FadeOut(dice_table.rows),
            FadeOut(dice_unit_rect),
        )

        self.wait(3)

# TITLE

        text = TextMobject("Probability distributions")
        text.to_edge(UP)
        text_rect = SurroundingRectangle(text, buff=MED_SMALL_BUFF)
        text_rect.match_color(text)

        self.play(
            FadeIn(text),
            ShowCreation(text_rect)
        )

        self.wait(3)


# COIN FLIP


        brick_row = BrickRow(3, height = 2, width = 10)
        coin_flip_rect = VGroup(brick_row)

        tallies = VGroup()
        for (i, brick) in enumerate(brick_row.rects):
            tally = TallyStack(3 - i, i)
            tally.move_to(brick)
            tallies.add(tally)
        coin_flip_rect.add(tallies)

        coin_flip_rect.scale(0.65).shift(RIGHT)
        self.play(FadeIn(coin_flip_rect))

        counts = [1, 3, 3, 1]
        braces = VGroup()
        labels = VGroup()
        for (rect, count) in zip(brick_row.rects, counts):
            label = TexMobject("{" + str(count) + "\\over 8}").scale(0.5)
            brace = Brace(rect, DOWN)
            label.next_to(brace, DOWN)
            braces.add(brace)
            labels.add(label)

        self.play(
            FadeIn(braces),
            FadeIn(labels)
        )

        coin_flip_rect.add(braces, labels)


        self.wait(6)

        outcomes = brick_row.get_outcome_rects_for_level(3, with_labels = True,
            inset = True)
        outcomes.scale(0.65)
        outcomes.move_to(brick_row.get_center())
        outcome_braces = VGroup(*[
            Brace(outcome, DOWN) for outcome in outcomes
        ])
        outcome_labels = VGroup(*[
            TexMobject("{1\over 8}").scale(0.5).next_to(brace, DOWN)
            for brace in outcome_braces
        ])

        self.play(
            FadeOut(tallies),
            FadeIn(outcomes),
            FadeOut(braces),
            FadeOut(labels),
            FadeIn(outcome_braces),
            FadeIn(outcome_labels)
        )


        self.wait(10)














