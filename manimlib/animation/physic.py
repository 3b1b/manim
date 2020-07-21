from manimlib.animation.animation import Animation
from manimlib.utils.rate_functions import linear
import numpy as np

class Simulate(Animation):
    CONFIG = {
        "rate_func" : linear
    }

    def __init__(self, scene, mobject, **kwargs):
        self.physic_object = mobject
        self.scene = mobject
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha):
        obj = self.physic_object
        if alpha < obj.show_alpha:
            return

        if not obj.is_added and alpha >= obj.show_alpha:
            obj.is_added = True
            self.scene.add(obj.mobject)
        
        n = len(obj.pos_and_rot) - 1
        pos, rot = obj.pos_and_rot[int(n * alpha)]
        x, y = pos
        obj.mobject.move_to(np.array([x, y, 0]))
        obj.mobject.rotate(rot - obj.angle)
        obj.angle = rot
