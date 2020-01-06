from mobject.types.vectorized_mobject import *
from mobject.svg.tex_mobject import *

class BinaryOption(VMobject):
    CONFIG = {
    "text_scale" : 0.5
    }

    def __init__(self, mob1, mob2, **kwargs):

        VMobject.__init__(self, **kwargs)
        text = TextMobject("or").scale(self.text_scale)
        mob1.next_to(text, LEFT)
        mob2.next_to(text, RIGHT)
        self.add(mob1, text, mob2)
