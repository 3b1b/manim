import pymunk

from manimlib.scene.scene import Scene
from manimlib.mobject.physic import PhysicMobject
from manimlib.animation.physic import Simulate

class PhysicScene(Scene):
    def __init__(self, **kwargs):
        self.space = pymunk.Space()
        self.physic_objs = []
        super().__init__(**kwargs)

    def set_gravity(self, gravity):
        x = gravity[0]
        y = gravity[1]
        self.space.gravity = x, y

    def add_physic_obj(self, *mobjects):
        for i in mobjects:
            if isinstance(i, PhysicMobject):
                self.physic_objs.append(i)

    def add_static_obj(self, *mobjects):
        for obj in mobjects:
            self.space.add(obj.shape)
            self.add(obj.mobject)

    def bake(self, time=1.0):
        step = 1 / self.camera.frame_rate
        for obj in self.physic_objs:
            obj.show_alpha = obj.add_time / time

        for t in range(int(time / step)):
            for i, obj in enumerate(self.physic_objs):
                obj.append_act()
                if t * step >= obj.add_time:
                    if obj.body.space != self.space:
                        self.space.add(obj.body)
                        self.space.add(obj.shape)
            self.space.step(step)

    def clear(self):
        for i in self.physic_objs:
            i.clear()
    
    def simulate(self, time=1.0):
        self.bake(time)
        self.play(*[Simulate(self, obj)\
            for obj in self.physic_objs],
            run_time = time)
        self.clear()
