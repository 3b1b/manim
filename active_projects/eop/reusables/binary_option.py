from mobject.types.vectorized_mobject import *

class BinaryOption(VMobject):

    def __init__(self, mob1, mob2, **kwargs):

        VMobject.__init__(self, **kwargs)
        text = TextMobject("or").scale(0.5)
        mob1.next_to(text, LEFT)
        mob2.next_to(text, RIGHT)
        self.add(mob1, text, mob2)
