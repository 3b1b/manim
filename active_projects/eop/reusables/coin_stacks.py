from mobject.geometry import *
from mobject.svg.tex_mobject import *
from active_projects.eop.reusables.upright_coins import *


class CoinStack(VGroup):
    CONFIG = {
        "coin_thickness": COIN_THICKNESS,
        "size": 5,
        "face": FlatCoin,
    }

    def generate_points(self):
        for n in range(self.size):
            coin = self.face(thickness = self.coin_thickness)
            coin.shift(n * self.coin_thickness * UP)
            self.add(coin)
        if self.size == 0:
            point = VectorizedPoint()
            self.add(point)

class HeadsStack(CoinStack):
    CONFIG = {
        "face": FlatHeads
    }

class TailsStack(CoinStack):
    CONFIG = {
        "face": FlatTails
    }



class DecimalTally(TextMobject):

    def __init__(self, heads, tails, **kwargs):

        TextMobject.__init__(self, str(heads), "\\textemdash\,", str(tails), **kwargs)
        self[0].set_color(COLOR_HEADS)
        self[-1].set_color(COLOR_TAILS)
        # this only works for single-digit tallies




class TallyStack(VGroup):
    CONFIG = {
        "coin_thickness": COIN_THICKNESS,
        "show_decimals": True
    }

    def __init__(self, h, t, anchor = ORIGIN, **kwargs):
        self.nb_heads = h
        self.nb_tails = t
        self.anchor = anchor
        VGroup.__init__(self,**kwargs)

    def generate_points(self):
        stack1 = HeadsStack(size = self.nb_heads, coin_thickness = self.coin_thickness)
        stack2 = TailsStack(size = self.nb_tails, coin_thickness = self.coin_thickness)
        stack1.next_to(self.anchor, LEFT, buff = 0.5 * SMALL_BUFF)
        stack2.next_to(self.anchor, RIGHT, buff = 0.5 * SMALL_BUFF)
        stack1.align_to(self.anchor, DOWN)
        stack2.align_to(self.anchor, DOWN)
        self.heads_stack = stack1
        self.tails_stack = stack2
        self.add(stack1, stack2)
        self.background_rect = background_rect = RoundedRectangle(
            width = TALLY_BACKGROUND_WIDTH,
            height = TALLY_BACKGROUND_WIDTH,
            corner_radius = 0.1,
            fill_color = TALLY_BACKGROUND_COLOR,
            fill_opacity = 1.0,
            stroke_width = 3
        ).align_to(self.anchor, DOWN).shift(0.1 * DOWN)
        self.add_to_back(background_rect)

        self.decimal_tally = DecimalTally(self.nb_heads, self.nb_tails)
        self.position_decimal_tally(self.decimal_tally)
        if self.show_decimals:
            self.add(self.decimal_tally)

    def position_decimal_tally(self, decimal_tally):
        decimal_tally.match_width(self.background_rect)
        decimal_tally.scale(0.6)
        decimal_tally.next_to(self.background_rect.get_top(), DOWN, buff = 0.15)
        return decimal_tally


    def move_anchor_to(self, new_anchor):
        for submob in self.submobjects:
            submob.shift(new_anchor - self.anchor)

        self.anchor = new_anchor
        self.position_decimal_tally(self.decimal_tally)

        return self














