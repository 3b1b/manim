
from manimlib.imports import *
from active_projects.eop.reusable_imports import *

class JustFlipping(Scene):

    def construct(self):

        randy = CoinFlippingPiCreature(color = MAROON_E, flip_height = 1).shift(2 * DOWN)
        self.add(randy)

        self.wait(2)

        for i in range(10):
            self.wait()
            self.play(FlipCoin(randy))



class JustFlippingWithResults(Scene):

    def construct(self):

        randy = CoinFlippingPiCreature(color = MAROON_E, flip_height = 1).shift(2 * DOWN)
        self.add(randy)

        self.wait(2)

        for i in range(10):
            self.wait()
            self.play(FlipCoin(randy))
            result = random.choice(["H", "T"])
            if result == "H":
                coin = UprightHeads().scale(3)
            else:
                coin = UprightTails().scale(3)
            coin.move_to(2 * UP + 2.5 * LEFT + i * 0.6 * RIGHT)
            self.play(FadeIn(coin))

