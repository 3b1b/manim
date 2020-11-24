from manimlib.imports import *


def get_value_grid(n_rows=10, n_cols=10):
    boxes = VGroup(*[Square() for x in range(n_rows * n_cols)])
    boxes.arrange_in_grid(n_rows, n_cols, buff=0)
    boxes.set_height(6)
    boxes.set_style(GREY_B, 2)
    for box in boxes:
        value = DecimalNumber(random.random(), num_decimal_places=1)
        box.value = value
        value.set_height(0.7 * box.get_height())
        value.move_to(box)
        box.add(value)
    return boxes


class GreedyAlgorithm(Scene):
    def construct(self):
        value_grid = get_value_grid()

        self.add(value_grid)


class RecrusiveExhaustiveSearch(Scene):
    def construct(self):
        pass


class DynamicProgrammingApproachSearch(Scene):
    def construct(self):
        pass
