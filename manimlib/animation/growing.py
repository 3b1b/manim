from manimlib.animation.transform import Transform
from manimlib.utils.config_ops import digest_config
from manimlib.utils.paths import counterclockwise_path


class GrowFromPoint(Transform):
    CONFIG = {
        "point_color": None,
    }

    def __init__(self, mobject, point, **kwargs):
        digest_config(self, kwargs)
        target = mobject.copy()
        mobject.scale(0)
        mobject.move_to(point)
        if self.point_color:
            mobject.set_color(self.point_color)
        Transform.__init__(self, mobject, target, **kwargs)


class GrowFromCenter(GrowFromPoint):
    def __init__(self, mobject, **kwargs):
        GrowFromPoint.__init__(self, mobject, mobject.get_center(), **kwargs)


class GrowFromEdge(GrowFromPoint):
    def __init__(self, mobject, edge, **kwargs):
        GrowFromPoint.__init__(
            self, mobject, mobject.get_critical_point(edge), **kwargs
        )


class GrowArrow(GrowFromPoint):
    def __init__(self, arrow, **kwargs):
        GrowFromPoint.__init__(self, arrow, arrow.get_start(), **kwargs)


class SpinInFromNothing(GrowFromCenter):
    CONFIG = {
        "path_func": counterclockwise_path()
    }


class ShrinkToCenter(Transform):
    def __init__(self, mobject, **kwargs):
        Transform.__init__(
            self, mobject, mobject.get_point_mobject(), **kwargs
        )
