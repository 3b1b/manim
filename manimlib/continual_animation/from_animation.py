from manimlib.continual_animation.continual_animation import ContinualAnimation


class NormalAnimationAsContinualAnimation(ContinualAnimation):
    CONFIG = {
        "start_up_time": 0,
        "wind_down_time": 0,
    }

    def __init__(self, animation, **kwargs):
        self.animation = animation
        ContinualAnimation.__init__(self, animation.mobject, **kwargs)

    def update_mobject(self, dt):
        self.animation.update(
            min(float(self.internal_time) / self.animation.run_time, 1)
        )


class CycleAnimation(ContinualAnimation):
    def __init__(self, animation, **kwargs):
        self.animation = animation
        ContinualAnimation.__init__(self, animation.mobject, **kwargs)

    def update_mobject(self, dt):
        mod_value = self.internal_time % self.animation.run_time
        alpha = mod_value / float(self.animation.run_time)
        self.animation.update(alpha)
