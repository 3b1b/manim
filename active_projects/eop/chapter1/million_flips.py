from manimlib.imports import *
from active_projects.eop.reusable_imports import *


class MillionFlips(Scene):
    def construct(self):
        title = TextMobject("1{,}000{,}000 flips")
        title.to_edge(UP)
        self.add(title)

        small_wait_time = 1.0 / 15  # Um...

        n_flips_label = TextMobject("\\# Flips: ")
        n_heads_label = TextMobject("\\# Heads: ")
        n_flips_count = Integer(0)
        n_heads_count = Integer(0)
        n_heads_label.to_edge(RIGHT, buff=2 * LARGE_BUFF)
        n_flips_label.next_to(n_heads_label, DOWN, aligned_edge=LEFT)
        n_flips_count.next_to(n_flips_label[-1], RIGHT)
        n_heads_count.next_to(n_heads_label[-1], RIGHT)
        VGroup(n_flips_count, n_heads_count).shift(0.5 * SMALL_BUFF * UP)
        self.add(n_flips_label, n_heads_label, n_flips_count, n_heads_count)

        coins = VGroup(*[
            FlatHeads() if random.random() < 0.5 else FlatTails()
            for x in range(100)
        ])
        self.organize_group(coins)

        proportions = np.random.normal(0.5, 0.5 * 0.1, 100)
        hundred_boxes = VGroup(*[
            Square(
                stroke_width=1,
                stroke_color=WHITE,
                fill_opacity=1,
                fill_color=interpolate_color(COLOR_HEADS, COLOR_TAILS, prop)
            )
            for prop in proportions
        ])
        self.organize_group(hundred_boxes)

        ten_k_proportions = np.random.normal(0.5, 0.5 * 0.01, 100)
        ten_k_boxes = VGroup(*[
            Square(
                stroke_width=1,
                stroke_color=WHITE,
                fill_opacity=1,
                fill_color=interpolate_color(COLOR_HEADS, COLOR_TAILS, prop)
            )
            for prop in ten_k_proportions
        ])
        self.organize_group(ten_k_boxes)

        # Animations
        for coin in coins:
            self.add(coin)
            self.increment(n_flips_count)
            if isinstance(coin, FlatHeads):
                self.increment(n_heads_count)
            self.wait(small_wait_time)

        self.play(
            FadeIn(hundred_boxes[0]),
            coins.set_stroke, {"width": 0},
            coins.replace, hundred_boxes[0]
        )
        hundred_boxes[0].add(coins)
        for box, prop in list(zip(hundred_boxes, proportions))[1:]:
            self.add(box)
            self.increment(n_flips_count, 100)
            self.increment(n_heads_count, int(np.round(prop * 100)))
            self.wait(small_wait_time)

        self.play(
            FadeIn(ten_k_boxes[0]),
            hundred_boxes.set_stroke, {"width": 0},
            hundred_boxes.replace, ten_k_boxes[0]
        )
        ten_k_boxes[0].add(hundred_boxes)
        for box, prop in list(zip(ten_k_boxes, ten_k_proportions))[1:]:
            self.add(box)
            self.increment(n_flips_count, 10000)
            self.increment(n_heads_count, int(np.round(prop * 10000)))
            self.wait(small_wait_time)
        self.wait()

    def organize_group(self, group):
        group.arrange_in_grid(10)
        group.set_height(5)
        group.shift(DOWN + 2 * LEFT)

    def increment(self, integer_mob, value=1):
        new_int = Integer(integer_mob.number + value)
        new_int.move_to(integer_mob, DL)
        integer_mob.number += value
        integer_mob.submobjects = new_int.submobjects


class PropHeadsWithinThousandth(Scene):
    def construct(self):
        prob = TexMobject(
            "P(499{,}000 \\le", "\\# \\text{H}", "\\le 501{,}000)",
            "\\approx", "0.9545",
        )
        prob[1].set_color(RED)
        prob[-1].set_color(YELLOW)
        self.add(prob)


class PropHeadsWithinHundredth(Scene):
    def construct(self):
        prob = TexMobject(
            "P(490{,}000 \\le", "\\# \\text{H}", "\\le 510{,}000)",
            "\\approx", "0.99999999\\dots",
        )
        prob[1].set_color(RED)
        prob[-1].set_color(YELLOW)
        self.add(prob)
