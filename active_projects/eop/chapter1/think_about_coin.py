
from manimlib.imports import *
from active_projects.eop.reusable_imports import *

class RandyThinksAboutCoin(PiCreatureScene):

    def construct(self):

        randy = self.get_primary_pi_creature()
        randy.center()
        self.add(randy)
        self.wait()
        h_or_t = BinaryOption(UprightHeads().scale(3), UprightTails().scale(3),
            text_scale = 1.5)
        self.think(h_or_t, direction = LEFT)

        v = 0.3
        self.play(
            h_or_t[0].shift,v*UP,
            h_or_t[2].shift,v*DOWN,
        )
        self.play(
            h_or_t[0].shift,2*v*DOWN,
            h_or_t[2].shift,2*v*UP,
        )
        self.play(
            h_or_t[0].shift,v*UP,
            h_or_t[2].shift,v*DOWN,
        )

        self.wait()
