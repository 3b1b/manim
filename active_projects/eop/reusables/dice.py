from mobject.svg.svg_mobject import *
from mobject.geometry import *
from mobject.numbers import *

class DieFace(SVGMobject):
    
    def __init__(self, value, **kwargs):

        self.value = value
        self.file_name = "Dice-" + str(value)
        self.ensure_valid_file()
        SVGMobject.__init__(self, file_name = self.file_name)
        
class RowOfDice(VGroup):
    CONFIG = {
        "values" : list(range(1,7)),
        "direction": RIGHT,
    }

    def generate_points(self):
        for value in self.values:
            new_die = DieFace(value)
            new_die.submobjects[0].set_fill(opacity = 0)
            new_die.submobjects[0].set_stroke(width = 7)
            new_die.next_to(self, self.direction)
            self.add(new_die)
        self.move_to(ORIGIN)


class TwoDiceTable(VMobject):
    CONFIG = {
        "cell_size" : 1,
        "label_scale": 0.7
    }

    def __init__(self, **kwargs):

        VMobject.__init__(self, **kwargs)
        colors = color_gradient([RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE], 13)

        self.cells = VGroup()
        self.labels = VGroup()
        for i in range(1,7):
            for j in range(1,7):
                cell = Square(side_length = self.cell_size)
                cell.set_fill(color = colors[i+j], opacity = 0.8)
                cell.move_to(i*self.cell_size*DOWN + j*self.cell_size*RIGHT)
                self.cells.add(cell)
                label = Integer(i+j).scale(self.label_scale)
                label.move_to(cell)
                self.labels.add(label)


        self.add(self.cells, self.labels)
        row1 = RowOfDice().match_width(self)
        row2 = row1.copy().rotate(-TAU/4)
        row1.next_to(self, UP)
        row2.next_to(self, LEFT)
        self.rows = VGroup(row1, row2)
        self.add(self.rows)
        self.center()















