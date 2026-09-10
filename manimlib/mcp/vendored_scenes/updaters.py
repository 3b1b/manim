"""Adapted from example_scenes.py's UpdatersExample, trimmed to the core updater patterns."""
from manimlib import *


class UpdatersExample(Scene):
    def construct(self):
        square = Square()
        square.set_fill(BLUE_E, 1)

        # always_redraw reconstructs its argument on every frame, so the
        # brace tracks the square as it changes.
        brace = always_redraw(Brace, square, UP)

        label = TexText("Width = 0.00")
        number = label.make_number_changeable("0.00")

        # label.always.next_to(...) is equivalent to
        # label.add_updater(lambda m: m.next_to(brace, UP))
        label.always.next_to(brace, UP)
        # number.f_always.set_value(square.get_width) is equivalent to
        # number.add_updater(lambda m: m.set_value(square.get_width()))
        number.f_always.set_value(square.get_width)

        self.add(square, brace, label)

        self.play(
            square.animate.set_width(3, stretch=True),
            run_time=2,
        )
        self.wait()
        self.play(square.animate.set_width(2), run_time=2)
        self.wait()
