from mobject.geometry import *
from active_projects.eop.reusables.eop_helpers import *
from active_projects.eop.reusables.eop_constants import *

class CoinFlipTree(VGroup):
    CONFIG = {
        "total_width": 12,
        "level_height": 0.8,
        "nb_levels": 4,
        "sort_until_level": 3
    }

    def __init__(self, **kwargs):

        VGroup.__init__(self, **kwargs)

        self.rows = []
        for n in range(self.nb_levels + 1):
            if n <= self.sort_until_level:
                self.create_row(n, sorted = True)
            else:
                self.create_row(n, sorted = False)
            

        for row in self.rows:
            for leaf in row:
                dot = Dot()
                dot.move_to(leaf[0])
                line = Line(leaf[2], leaf[0])
                if leaf[2][0] > leaf[0][0]:
                    line_color = COLOR_HEADS
                else:
                    line_color = COLOR_TAILS
                line.set_stroke(color = line_color)
                group = VGroup()
                group.add(dot)
                group.add_to_back(line)
                self.add(group)




    def create_row(self, level, sorted = True):

        if level == 0:
            new_row = [[ORIGIN,0,ORIGIN]] # is its own parent
            self.rows.append(new_row)
            return

        previous_row = self.rows[level - 1]
        new_row = []
        dx = float(self.total_width) / (2 ** level)
        x = - 0.5 * self.total_width + 0.5 * dx
        y = - self.level_height * level
        for root in previous_row:
            root_point = root[0]
            root_tally = root[1]
            for i in range(2): # 0 = heads = left, 1 = tails = right
                leaf = x * RIGHT + y * UP
                new_row.append([leaf, root_tally + i, root_point]) # leaf and its parent
                x += dx

        if sorted:
            # sort the new_row by its tallies
            sorted_row = []
            x = - 0.5 * self.total_width + 0.5 * dx
            for i in range(level + 1):
                for leaf in new_row:
                    if leaf[1] == i:
                        sorted_leaf = leaf
                        sorted_leaf[0][0] = x
                        x += dx
                        sorted_row.append(leaf)
            self.rows.append(sorted_row)
        else:
            self.rows.append(new_row)
