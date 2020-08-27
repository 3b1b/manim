from manimlib.imports import *


def get_factors(n):
    return filter(
        lambda k: (n % k) == 0,
        range(1, n)
    )


class AmicableNumbers(Scene):
    CONFIG = {
        "n1": 28,
        "n2": 284,
        "colors": [
            BLUE_C,
            BLUE_B,
            BLUE_D,
            GREY_BROWN,
            GREEN_C,
            GREEN_B,
            GREEN_D,
            GREY,
        ]
    }

    def construct(self):
        self.show_n1()
        self.show_n1_factors()
        self.show_n1_factor_sum()
        self.show_n2_factors()
        self.show_n2_factor_sum()

    def show_n1(self):
        dots = VGroup(*[Dot() for x in range(self.n1)])
        dots.set_color(BLUE)
        dots.set_sheen(0.2, UL)
        dots.arrange(RIGHT, buff=SMALL_BUFF)
        dots.set_width(FRAME_WIDTH - 1)

        rects = self.get_all_factor_rectangles(dots)
        rects.rotate(90 * DEGREES)
        rects.arrange(RIGHT, buff=MED_SMALL_BUFF, aligned_edge=DOWN)
        for rect in rects:
            rect.first_col.set_stroke(WHITE, 3)
        rects.set_height(FRAME_HEIGHT - 1)

        self.add(rects)

    def show_n1_factors(self):
        pass

    def show_n1_factor_sum(self):
        pass

    def show_n2_factors(self):
        pass

    def show_n2_factor_sum(self):
        pass

    #
    def show_factors(self, dot_group):
        pass

    def get_all_factor_rectangles(self, dot_group):
        n = len(dot_group)
        factors = get_factors(n)
        colors = it.cycle(self.colors)
        result = VGroup()
        for k, color in zip(factors, colors):
            group = dot_group.copy()
            group.set_color(color)
            group.arrange_in_grid(n_rows=k, buff=SMALL_BUFF)
            group.first_col = group[::(n // k)]
            result.add(group)
        return result
