from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.vectorized_mobject import VMobject

class PhysicMobject(Mobject):
    def __init__(self, body, shape, mobject, **kwargs):
        self.angle = body.angle
        self.mobject = mobject
        self.mobject.rotate(body.angle)
        self.pos_and_rot = []
        self.body = body
        self.shape = shape
        self.add_time = 0
        self.is_added = False
        self.show_alpha = 0
        super().__init__(**kwargs)

    def set_add_time(self, time):
        self.add_time = time
        if time > 0:
            self.is_added = False

    def append_act(self):
        pos = self.body.position
        rot = self.body.angle
        self.pos_and_rot.append((pos, rot))

    def clear(self):
        self.pos_and_rot = []
