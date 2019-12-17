
from mobject.geometry import *
from mobject.svg.tex_mobject import *
from utils.color import *

from active_projects.eop.reusables.eop_helpers import *
from active_projects.eop.reusables.eop_constants import *

class UprightCoin(Circle):
# For use in coin sequences
    CONFIG = {
        "radius": COIN_RADIUS,
        "stroke_width": COIN_STROKE_WIDTH,
        "stroke_color": WHITE,
        "fill_opacity": 1,
        "symbol": "\euro"
    }

    def __init__(self, **kwargs):
        Circle.__init__(self,**kwargs)
        self.symbol_mob = TextMobject(self.symbol, stroke_color = self.stroke_color)
        self.symbol_mob.set_height(0.5*self.get_height()).move_to(self)
        self.add(self.symbol_mob)

class UprightHeads(UprightCoin):
    CONFIG = {
        "fill_color": COLOR_HEADS_COIN,
        "symbol": "H",
    }

class UprightTails(UprightCoin):
    CONFIG = {
        "fill_color": COLOR_TAILS_COIN,
        "symbol": "T",
    }

class CoinSequence(VGroup):
    CONFIG = {
        "sequence": [],
        "radius" : COIN_RADIUS,
        "spacing": COIN_SEQUENCE_SPACING,
        "direction": RIGHT
    }

    def __init__(self, sequence, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.sequence = sequence
        offset = 0
        for symbol in self.sequence:
            if symbol == "H":
                new_coin = UprightHeads(radius = self.radius)
            elif symbol == "T":
                new_coin = UprightTails(radius = self.radius)
            else:
                new_coin = UprightCoin(symbol = symbol, radius = self.radius)
            new_coin.shift(offset * self.direction)
            self.add(new_coin)
            offset += self.spacing


class FlatCoin(UprightCoin):
# For use in coin stacks
    CONFIG = {
        "thickness": COIN_THICKNESS,
        "foreshortening": COIN_FORESHORTENING,
        "nb_ridges": COIN_NB_RIDGES
    }

    def __init__(self, **kwargs):
        UprightCoin.__init__(self, **kwargs)
        self.symbol_mob.rotate(TAU/8)
        self.stretch_in_place(self.foreshortening, 1)
        
        # draw the edge
        control_points1 = self.points[12:25].tolist()
        control_points2 = self.copy().shift(self.thickness * DOWN).points[12:25].tolist()
        edge_anchors_and_handles = control_points1
        edge_anchors_and_handles.append(edge_anchors_and_handles[-1] + self.thickness * DOWN)
        edge_anchors_and_handles.append(edge_anchors_and_handles[-1] + self.thickness * UP)
        edge_anchors_and_handles += control_points2[::-1] # list concatenation
        edge_anchors_and_handles.append(edge_anchors_and_handles[-1] + self.thickness * UP)
        edge_anchors_and_handles.append(edge_anchors_and_handles[-1] + self.thickness * DOWN)
        edge_anchors_and_handles.append(control_points1[0])
        #edge_anchors_and_handles = edge_anchors_and_handles[::-1]
        edge = VMobject()
        edge.set_points(edge_anchors_and_handles)
        edge.set_fill(
            color = self.fill_color,
            opacity = self.fill_opacity
        )
        edge.set_stroke(width = self.stroke_width)
        self.add(edge)

        # draw the ridges
        PI = TAU/2
        dtheta = PI/self.nb_ridges
        ridge_angles = np.arange(dtheta,PI,dtheta)
        # add a twist onto each coin
        ridge_angles += np.random.rand(1) * dtheta
        # crop the angles that overshoot on either side
        ridge_angles = ridge_angles[(ridge_angles > 0) * (ridge_angles < PI)]
        ridge_positions = 0.5 * 2 * self.radius * np.array([
            np.cos(theta) for theta in ridge_angles
        ])
        ridge_color = interpolate_color(self.stroke_color, self.fill_color, 0.7)
        for x in ridge_positions:
            y = -(1 - (x/self.radius)**2)**0.5 * self.foreshortening * self.radius
            ridge = Line(
                x * RIGHT + y * UP,
                x * RIGHT + y * UP + self.thickness * DOWN,
                stroke_color = ridge_color,
                stroke_width = self.stroke_width
            )
            self.add(ridge)

        # redraw the unfilled edge to cover the ridge ends
        empty_edge = edge.copy()
        empty_edge.set_fill(opacity = 0)
        self.add(empty_edge)

class FlatHeads(FlatCoin):
    CONFIG = {
        "fill_color": COLOR_HEADS_COIN,
        "symbol": "H",
    }
    
class FlatTails(FlatCoin):
    CONFIG = {
        "fill_color": COLOR_TAILS_COIN,
        "symbol": "T",
    }
    