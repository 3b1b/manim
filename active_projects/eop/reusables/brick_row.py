from manimlib.imports import *
from active_projects.eop.reusables.eop_helpers import *
from active_projects.eop.reusables.eop_constants import *
from active_projects.eop.reusables.upright_coins import *

class BrickRow(VMobject):

    CONFIG = {
        "left_color" : COLOR_HEADS,
        "right_color" : COLOR_TAILS,
        "height" : 1.0,
        "width" : 8.0,
        "outcome_shrinkage_factor_x" : 0.95,
        "outcome_shrinkage_factor_y" : 0.94
    }

    def __init__(self, n, **kwargs):
        self.subdiv_level = n
        self.coloring_level = n
        VMobject.__init__(self, **kwargs)


    def generate_points(self):

        self.submobjects = []
        self.rects = self.get_rects_for_level(self.coloring_level)
        self.add(self.rects)
        self.subdivs = self.get_subdivs_for_level(self.subdiv_level)
        self.add(self.subdivs)

        self.border = SurroundingRectangle(self,
            buff = 0, color = WHITE)
        self.add(self.border)



    def get_rects_for_level(self,r):
        rects = VGroup()
        for k in range(r + 1):
            proportion = float(choose(r,k)) / 2**r
            new_rect = Rectangle(
                width = proportion * self.width, 
                height = self.height,
                fill_color = graded_color(r,k),
                fill_opacity = 1,
                stroke_width = 0
            )
            if len(rects.submobjects) > 0:
                new_rect.next_to(rects,RIGHT,buff = 0)
            else:
                new_rect.next_to(self.get_center() + 0.5 * self.width * LEFT, RIGHT, buff = 0)
            rects.add(new_rect)
        return rects


    def get_subdivs_for_level(self,r):
        subdivs = VGroup()
        x = - 0.5 * self.width
        for k in range(0, r):
            proportion = float(choose(r,k)) / 2**r
            x += proportion * self.width
            subdiv = Line(
                x * RIGHT + 0.5 * self.height * UP,
                x * RIGHT + 0.5 * self.height * DOWN,
            )
            subdivs.add(subdiv)
        subdivs.move_to(self.get_center())
        return subdivs


    def get_sequence_subdivs_for_level(self,r):
        subdivs = VGroup()
        x = - 0.5 * self.width
        dx = 1.0 / 2**r
        for k in range(1, 2 ** r):
            proportion = dx
            x += proportion * self.width
            subdiv = DashedLine(
                x * RIGHT + 0.5 * self.height * UP,
                x * RIGHT + 0.5 * self.height * DOWN,
            )
            subdivs.add(subdiv)
        subdivs.move_to(self.get_center())
        return subdivs


    def get_outcome_centers_for_level(self,r):
        
        dpos = float(self.width) / (2 ** r) * RIGHT
        pos = 0.5 * self.width * LEFT + 0.5 * dpos
        centers = []
        for k in range(0, 2 ** r):
            centers.append(self.get_center() + pos + k * dpos)

        return centers

    def get_outcome_rects_for_level(self, r, inset = False, with_labels = False):

        centers = self.get_outcome_centers_for_level(r)
        if inset == True:
            outcome_width = self.outcome_shrinkage_factor_x * float(self.width) / (2 ** r)
            outcome_height = self.outcome_shrinkage_factor_y * self.height
        else:
            outcome_width = float(self.width) / (2 ** r)
            outcome_height = self.height
        
        corner_radius = 0.1 # max(0.1, 0.3 * min(outcome_width, outcome_height))
        # this scales down the corner radius for very narrow rects
        rect = RoundedRectangle(
            width = outcome_width,
            height = outcome_height,
            corner_radius = corner_radius,
            fill_color = OUTCOME_COLOR,
            fill_opacity = OUTCOME_OPACITY,
            stroke_width = 0
        )
        rects = VGroup()
        for center in centers:
            rects.add(rect.copy().move_to(center))

        rects.move_to(self.get_center())


        if with_labels == False:
            return rects

        # else
        sequences = self.get_coin_sequences_for_level(r)
        labels = VGroup()
        for (seq, rect) in zip(sequences, rects):
            coin_seq = CoinSequence(seq, direction = DOWN)
            coin_seq.shift(rect.get_center() - coin_seq.get_center())
            # not simply move_to bc coin_seq is not centered
            rect.add(coin_seq)
            rect.label = coin_seq

        return rects

    def get_coin_sequences_for_level(self,r):
        # array of arrays of characters
        if r < 0 or int(r) != r:
            raise Exception("Level must be a positive integer")
        if r == 0:
            return []
        if r == 1:
            return [["H"], ["T"]]

        previous_seq_array = self.get_coin_sequences_for_level(r - 1)
        subdiv_lengths = [choose(r - 1, k) for k in range(r)]

        seq_array = []
        index = 0
        for length in subdiv_lengths:
            
            for seq in previous_seq_array[index:index + length]:
                seq_copy = copy.copy(seq)
                seq_copy.append("H")
                seq_array.append(seq_copy)

            for seq in previous_seq_array[index:index + length]:
                seq_copy = copy.copy(seq)
                seq_copy.append("T")
                seq_array.append(seq_copy)
            index += length

        return seq_array


    def get_outcome_width_for_level(self,r):
        return self.width / (2**r)

    def get_rect_widths_for_level(self, r):
        ret_arr = []
        for k in range(0, r):
            proportion = float(choose(r,k)) / 2**r
            ret_arr.append(proportion * self.width)
        return ret_arr




class SplitRectsInBrickWall(AnimationGroup):

    def __init__(self, mobject, **kwargs):

        #print mobject.height, mobject.get_height()
        r = self.subdiv_level = mobject.subdiv_level + 1
        
        subdivs = VGroup()
        x = -0.5 * mobject.get_width()

        anims = []
        for k in range(0, r):
            proportion = float(choose(r,k)) / 2**r
            x += proportion * mobject.get_width()
            subdiv = DashedLine(
                mobject.get_top() + x * RIGHT,
                mobject.get_bottom() + x * RIGHT,
                dash_length = 0.05
            )
            subdivs.add(subdiv)
            anims.append(ShowCreation(subdiv))

        mobject.add(subdivs)
        AnimationGroup.__init__(self, *anims, **kwargs)



