from big_ol_pile_of_manim_imports import *


class ReactionsToInitialHeatEquation(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature
        randy.set_color(BLUE_C)
        randy.center()

        point = VectorizedPoint().next_to(randy, UL, LARGE_BUFF)
        randy.add_updater(lambda r: r.look_at(point))

        self.play(randy.change, "horrified")
        self.wait()
        self.play(randy.change, "pondering")
        self.wait()
        self.play(
            randy.change, "confused",
            point.next_to, randy, UR, LARGE_BUFF,
        )
        self.wait(2)
        self.play(point.shift, 2 * DOWN)
        self.wait(3)
