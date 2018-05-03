from mobject.svg.svg_mobject import *

class DieFace(SVGMobject):
    
    def __init__(self, value, **kwargs):

        self.value = value
        self.file_name = "Dice-" + str(value)
        self.ensure_valid_file()
        SVGMobject.__init__(self, file_name = self.file_name)
        
class RowOfDice(VGroup):
    CONFIG = {
        "values" : range(1,7),
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

