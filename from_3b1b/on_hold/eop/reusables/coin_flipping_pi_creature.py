from mobject.types.vectorized_mobject import *
from animation.animation import *
from animation.composition import *
from mobject.geometry import Rectangle, Line
from utils.rate_functions import *
from for_3b1b_videos.pi_creature_scene import *
from active_projects.eop.reusables.eop_helpers import *
from active_projects.eop.reusables.eop_constants import *
from active_projects.eop.reusables.coin_flipping_pi_creature import *


class PiCreatureCoin(VMobject):
    CONFIG = {
        "diameter": 0.8,
        "thickness": 0.2,
        "nb_ridges" : 7,
        "stroke_color": YELLOW,
        "stroke_width": 3,
        "fill_color": YELLOW,
        "fill_opacity": 0.7,
    }

    def generate_points(self):
        outer_rect = Rectangle(
            width = self.diameter,
            height = self.thickness,
            fill_color  = self.fill_color,
            fill_opacity = self.fill_opacity,
            stroke_color = self.stroke_color,
            stroke_width = 0, #self.stroke_width
        )
        self.add(outer_rect)
        PI = TAU/2
        ridge_angles = np.arange(PI/self.nb_ridges,PI,PI/self.nb_ridges)
        ridge_positions = 0.5 * self.diameter * np.array([
            np.cos(theta) for theta in ridge_angles
        ])
        ridge_color = interpolate_color(BLACK,self.stroke_color,0.5)
        for x in ridge_positions:
            ridge = Line(
                x * RIGHT + 0.5 * self.thickness * DOWN,
                x * RIGHT + 0.5 * self.thickness * UP,
                stroke_color = ridge_color,
                stroke_width = self.stroke_width
            )
            self.add(ridge)

class CoinFlippingPiCreature(PiCreature):
    CONFIG = {
        "flip_height": 3
    }

    def __init__(self, mode = "coin_flip_1", **kwargs):

        coin = PiCreatureCoin()
        PiCreature.__init__(self, mode = mode, **kwargs)
        self.coin = coin
        self.add(coin)
        right_arm = self.get_arm_copies()[1]
        coin.rotate(-TAU/24)
        coin.next_to(right_arm, RIGHT+UP, buff = 0)
        coin.shift(0.1 * self.get_width() * LEFT)
        coin.shift(0.2 * DOWN)

    def flip_coin_up(self):
        self.change("coin_flip_2")



class FlipUpAndDown(Animation):
    CONFIG = {
        "vector" : UP,
        "height" : 3,
        "nb_turns" : 1
    }

    def update(self,t):
        self.mobject.shift(self.height * 4 * t * (1 - t) * self.vector)
        self.mobject.rotate(t * self.nb_turns * TAU)

class FlipCoin(AnimationGroup):
    CONFIG = {
        "coin_rate_func" : there_and_back,
        "pi_rate_func" : lambda t : there_and_back_with_pause(t, 1./4)
    }
    def __init__(self, pi_creature, **kwargs):
        digest_config(self, kwargs)
        pi_creature_motion = ApplyMethod(
            pi_creature.flip_coin_up,
            rate_func = self.pi_rate_func,
            **kwargs
        )
        coin_motion = Succession(
            EmptyAnimation(run_time = 1.0),
            FlipUpAndDown(
                pi_creature.coin, 
                vector = UP,
                nb_turns = 5,
                height = pi_creature.flip_height * pi_creature.get_height(),
                rate_func = self.coin_rate_func,
                **kwargs
            )
        )
        AnimationGroup.__init__(self,pi_creature_motion, coin_motion)

class CoinFlippingPiCreatureScene(Scene):

    def construct(self):

        randy = CoinFlippingPiCreature(color = MAROON_E)
        self.add(randy)
        self.play(FlipCoin(randy, run_time = 3))
