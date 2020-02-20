from manimlib.imports import *
from from_3b1b.active.bayes.beta_helpers import *

OUTPUT_DIRECTORY = "bayes/beta"


class Histogram(Axes):
    CONFIG = {
        "x_min": 0,
        "x_max": 10,
        "y_min": 0,
        "y_max": 1,
        "axis_config": {
            "include_tip": False,
        },
        "y_axis_config": {
            "tick_frequency": 0.2,
        },
        "height": 5,
        "width": 10,
        "y_axis_numbers_to_show": range(20, 120, 20),
        "y_axis_label_height": 0.25,
        "include_h_lines": True,
        "h_line_style": {
            "stroke_width": 1,
            "stroke_color": LIGHT_GREY,
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resize()
        self.center()
        self.add_y_axis_labels()
        if self.include_h_lines:
            self.add_h_lines()
        self.add_bars()

    # Initializing methods
    def resize(self):
        self.x_axis.set_width(
            self.width,
            stretch=True,
            about_point=self.c2p(0, 0),
        )
        self.y_axis.set_height(
            self.height,
            stretch=True,
            about_point=self.c2p(0, 0),
        )

    def add_y_axis_labels(self):
        labels = VGroup()
        for value in self.y_axis_numbers_to_show:
            label = Integer(value, unit="\\%")
            label.set_height(self.y_axis_label_height)
            label.next_to(self.y_axis.n2p(0.01 * value), LEFT)
            labels.add(label)
        self.y_axis_labels = labels
        self.y_axis.add(labels)
        return self

    def add_h_lines(self):
        self.h_lines = VGroup()
        for tick in self.y_axis.tick_marks:
            line = Line(**self.h_line_style)
            line.match_width(self.x_axis)
            line.move_to(tick.get_center(), LEFT)
            self.h_lines.add(line)
        self.add(self.h_lines)

    def add_bars(self):
        pass

    # Bar manipulations


# Scenes
class BarChartTest(Scene):
    def construct(self):
        bar_chart = BarChart()
        bar_chart.to_edge(DOWN)
        self.add(bar_chart)


class Thumbnail(Scene):
    def construct(self):
        p1 = "$96\\%$"
        p2 = "$93\\%$"
        n1 = "50"
        n2 = "200"
        t2c = {
            p1: BLUE,
            p2: YELLOW,
            n1: BLUE_C,
            n2: YELLOW,
        }
        kw = {"tex_to_color_map": t2c}
        text = VGroup(
            TextMobject(f"{p1} with {n1} reviews", **kw),
            TextMobject("vs.", **kw),
            TextMobject(f"{p2} with {n2} reviews", **kw),
        )
        fix_percent(text[0].get_part_by_tex(p1)[-1])
        fix_percent(text[2].get_part_by_tex(p2)[-1])
        text.scale(2)
        text.arrange(DOWN, buff=LARGE_BUFF)
        text.set_width(FRAME_WIDTH - 1)
        self.add(text)


class ShowThreeCases(Scene):
    def construct(self):
        titles = self.get_titles()
        reviews = self.get_reviews(titles)

        # Introduce everything
        self.play(LaggedStartMap(
            FadeInFrom, titles,
            lambda m: (m, DOWN),
            lag_ratio=0.2
        ))
        self.play(LaggedStart(*[
            LaggedStartMap(
                FadeInFromLarge, review,
                lag_ratio=0.1
            )
            for review in reviews
        ], lag_ratio=0.1))
        self.wait()

        self.play(ShowCreationThenFadeAround(reviews[2]))
        self.wait()

        # Suspicious of 100%
        randy = Randolph(mode="sassy")
        randy.flip()
        randy.set_height(2)
        randy.next_to(
            reviews[0], RIGHT, LARGE_BUFF,
            aligned_edge=UP,
        )
        randy.look_at(reviews[0])
        self.play(FadeInFromDown(randy))
        self.play(Blink(randy))
        self.wait()
        self.play(FadeOut(randy))

        # Low number means it could be a fluke.

        # self.embed()

    def get_titles(self):
        titles = VGroup(
            TextMobject(
                "$100\\%$ \\\\",
                "10 reviews"
            ),
            TextMobject(
                "$96\\%$ \\\\",
                "50 reviews"
            ),
            TextMobject(
                "$93\\%$ \\\\",
                "200 reviews"
            ),
        )
        colors = [PINK, BLUE, YELLOW]
        for title, color in zip(titles, colors):
            fix_percent(title[0][-1])
            title[0].set_color(color)

        titles.scale(1.25)
        titles.arrange(DOWN, buff=1.5)
        titles.to_corner(UL)
        return titles

    def get_reviews(self, titles):
        return VGroup(
            self.get_plusses_and_minuses(
                titles[0], 5, 2, 0,
            ),
            self.get_plusses_and_minuses(
                titles[1], 5, 10, 2,
            ),
            self.get_plusses_and_minuses(
                titles[2], 8, 25, 14,
            ),
        )

    def get_plusses_and_minuses(self, title, n_rows, n_cols, n_minus):
        check = TexMobject("\\checkmark", color=GREEN)
        cross = TexMobject("\\times", color=RED)
        checks = VGroup(*[
            check.copy() for x in range(n_rows * n_cols)
        ])
        checks.arrange_in_grid(n_rows=n_rows, n_cols=n_cols)
        checks.scale(0.5)
        # if checks.get_height() > title.get_height():
        #     checks.match_height(title)
        checks.next_to(title, RIGHT, LARGE_BUFF)

        for check in random.sample(list(checks), n_minus):
            mob = cross.copy()
            mob.replace(check, dim_to_match=0)
            check.become(mob)

        return checks


class AskAboutUnknownProbabilities(Scene):
    def construct(self):
        # Setup
        unknown_title, prob_title = titles = self.get_titles()

        v_line = Line(UP, DOWN)
        v_line.set_height(FRAME_HEIGHT)
        v_line.set_stroke([WHITE, LIGHT_GREY], 3)
        h_line = Line(LEFT, RIGHT)
        h_line.set_width(FRAME_WIDTH)
        h_line.next_to(titles, DOWN)

        processes = VGroup(
            get_random_coin(shuffle_time=1),
            get_random_die(shuffle_time=1.20),
            get_random_card(shuffle_time=2),
        )
        processes.arrange(DOWN, buff=0.7)
        processes.next_to(unknown_title, DOWN, LARGE_BUFF)
        processes_rect = BackgroundRectangle(processes)
        processes_rect.set_fill(BLACK, 1)

        prob_labels = VGroup(
            TexMobject("P(", "00", ")", "=", "1 / 2"),
            TexMobject("P(", "00", ")", "=", "1 / 6}"),
            TexMobject("P(", "00", ")", "=", "1 / 52}"),
        )
        prob_labels.scale(1.5)
        prob_labels.arrange(DOWN, aligned_edge=LEFT)
        prob_labels.match_x(prob_title)
        for pl, pr in zip(prob_labels, processes):
            pl.match_y(pr)
            content = pr[1].copy()
            content.replace(pl[1], dim_to_match=0)
            pl.submobjects[1] = content

        # Putting numbers to the unknown
        number_rects = VGroup(*[
            SurroundingRectangle(pl[-1])
            for pl in prob_labels
        ])
        number_rects.set_stroke(YELLOW, 2)

        for pl in prob_labels:
            pl.save_state()
            pl[:3].match_x(prob_title)
            pl[3:].match_x(prob_title)
            pl.set_opacity(0)

        self.add(processes)
        self.play(
            LaggedStartMap(FadeInFromDown, titles),
            LaggedStart(
                ShowCreation(v_line),
                ShowCreation(h_line),
            ),
            run_time=1
        )
        self.wait(2)
        self.play(
            LaggedStartMap(Restore, prob_labels),
            run_time=3,
            lag_ratio=0.3,
        )
        self.play(
            LaggedStartMap(
                ShowCreationThenFadeOut,
                number_rects,
                run_time=3,
            )
        )
        self.wait(2)

        # Highlight coin flip
        fade_rect = BackgroundRectangle(
            VGroup(prob_labels[1:], processes[1:]),
            buff=MED_SMALL_BUFF,
        )
        fade_rect.set_width(FRAME_WIDTH, stretch=True)
        fade_rect.set_fill(BLACK, 0.8)

        prob_half = prob_labels[0]
        half = prob_half[-1]
        half_underline = Line(LEFT, RIGHT)
        half_underline.set_width(half.get_width() + MED_SMALL_BUFF)
        half_underline.next_to(half, DOWN, buff=SMALL_BUFF)
        half_underline.set_stroke(YELLOW, 3)

        self.add(fade_rect, v_line, prob_half)
        self.play(FadeIn(fade_rect))
        self.wait(2)
        self.play(
            ShowCreation(half_underline),
            half.set_color, YELLOW,
        )
        self.play(FadeOut(half_underline))
        self.wait(4)

        # Transition to question
        processes.suspend_updating()
        self.play(
            LaggedStart(
                FadeOutAndShift(unknown_title, UP),
                FadeOutAndShift(prob_title, UP),
                lag_ratio=0.2,
            ),
            FadeOutAndShift(h_line, UP, lag_ratio=0.1),
            FadeOutAndShift(processes, LEFT, lag_ratio=0.1),
            FadeOut(prob_labels[1]),
            FadeOut(prob_labels[2]),
            ApplyMethod(fade_rect.set_fill, BLACK, 1, remover=True),
            v_line.rotate, 90 * DEGREES,
            v_line.shift, 0.6 * FRAME_HEIGHT * UP,
            prob_half.center,
            prob_half.to_edge, UP,
            run_time=2,
        )
        self.clear()
        self.add(prob_half)

        arrow = Vector(UP)
        arrow.next_to(half, DOWN)
        question = TextMobject("What exactly does\\\\this mean?")
        question.next_to(arrow, DOWN)

        self.play(
            GrowArrow(arrow),
            FadeInFrom(question, UP),
        )
        self.wait(2)
        self.play(
            FadeOutAndShift(question, RIGHT),
            Rotate(arrow, 90 * DEGREES),
            VFadeOut(arrow),
        )

        # Show long run averages
        self.show_many_coins(20, 50)
        self.show_many_coins(40, 100)

        # Make probability itself unknown
        q_marks = TexMobject("???")
        q_marks.set_color(YELLOW)
        q_marks.replace(half, dim_to_match=0)

        randy = Randolph(mode="confused")
        randy.center()
        randy.look_at(prob_half)

        self.play(
            FadeOutAndShift(half, UP),
            FadeInFrom(q_marks, DOWN),
        )
        self.play(FadeIn(randy))
        self.play(Blink(randy))
        self.wait()

        # self.embed()

    def get_titles(self):
        unknown_label = TextMobject("Unknown event")
        prob_label = TextMobject("Probability")
        titles = VGroup(unknown_label, prob_label)
        titles.scale(1.5)

        unknown_label.move_to(FRAME_WIDTH * LEFT / 4)
        prob_label.move_to(FRAME_WIDTH * RIGHT / 4)
        titles.to_edge(UP, buff=MED_SMALL_BUFF)
        titles.set_color(BLUE)
        return titles

    def show_many_coins(self, n_rows, n_cols):
        coin_choices = VGroup(
            get_coin(BLUE_E, "H"),
            get_coin(RED_E, "T"),
        )
        coin_choices.set_stroke(width=0)
        coins = VGroup(*[
            random.choice(coin_choices).copy()
            for x in range(n_rows * n_cols)
        ])

        def organize_coins(coin_group):
            coin_group.scale(1 / coin_group[0].get_height())
            coin_group.arrange_in_grid(n_rows=n_rows)
            coin_group.set_width(FRAME_WIDTH - 1)
            coin_group.to_edge(DOWN, MED_LARGE_BUFF)

        organize_coins(coins)

        sorted_coins = VGroup()
        for coin in coins:
            coin.generate_target()
            sorted_coins.add(coin.target)
        sorted_coins.submobjects.sort(key=lambda m: m.symbol)
        organize_coins(sorted_coins)

        self.play(LaggedStartMap(
            FadeInFrom, coins,
            lambda m: (m, 0.2 * DOWN),
            run_time=3,
            rate_func=linear
        ))
        self.wait()
        self.play(LaggedStartMap(
            MoveToTarget, coins,
            path_arc=30 * DEGREES,
            run_time=2,
            lag_ratio=1 / len(coins),
        ))
        self.wait()
        self.play(FadeOut(coins))
