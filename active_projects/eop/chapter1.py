from big_ol_pile_of_manim_imports import *

class Coin(VMobject):
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

    def __init__(self, **kwargs):

        coin = Coin() # Line(ORIGIN, 0.4 * RIGHT, stroke_width = 15, color = YELLOW)
        PiCreature.__init__(self,**kwargs)
        self.coin = coin
        self.add(coin)
        right_arm = self.get_arm_copies()[1]
        coin.next_to(right_arm, RIGHT+UP, buff = 0)
        coin.shift(0.15 * self.get_width() * LEFT)

    def flip_coin_up(self):
        self.change("raise_right_hand")


class FlipUpAndDown(Animation):
    CONFIG = {
        "vector" : UP,
        "nb_turns" : 1
    }

    def update(self,t):
        self.mobject.shift(4 * t * (1 - t) * self.vector)
        self.mobject.rotate(t * self.nb_turns * TAU)


class FlipCoin(AnimationGroup):
    CONFIG = {
        "rate_func" : there_and_back
    }
    def __init__(self, pi_creature, **kwargs):
        digest_config(self, kwargs)
        pi_creature_motion = ApplyMethod(
            pi_creature.flip_coin_up,
            rate_func = self.rate_func,
            **kwargs
        )
        coin_motion = FlipUpAndDown(
            pi_creature.coin, 
            vector = UP,
            nb_turns = 5,
            rate_func = self.rate_func,
            **kwargs
        )
        AnimationGroup.__init__(self,pi_creature_motion, coin_motion)




class CoinFlipScene(Scene):

    def construct(self):

        randy = CoinFlippingPiCreature()
        self.add(randy)
        self.play(FlipCoin(randy, run_time = 3))





























