"""Animations related to movement."""

__all__ = [
    "Homotopy",
    "SmoothedVectorizedHomotopy",
    "ComplexHomotopy",
    "PhaseFlow",
    "MoveAlongPath",
]


from ..animation.animation import Animation
from ..utils.rate_functions import linear


class Homotopy(Animation):
    def __init__(
        self, homotopy, mobject, run_time=3, apply_function_kwargs={}, **kwargs
    ):
        """
        Homotopy is a function from
        (x, y, z, t) to (x', y', z')
        """
        self.homotopy = homotopy
        self.apply_function_kwargs = apply_function_kwargs
        super().__init__(mobject, run_time=run_time, **kwargs)

    def function_at_time_t(self, t):
        return lambda p: self.homotopy(*p, t)

    def interpolate_submobject(self, submob, start, alpha):
        submob.points = start.points
        submob.apply_function(
            self.function_at_time_t(alpha), **self.apply_function_kwargs
        )


class SmoothedVectorizedHomotopy(Homotopy):
    def interpolate_submobject(self, submob, start, alpha):
        Homotopy.interpolate_submobject(self, submob, start, alpha)
        submob.make_smooth()


class ComplexHomotopy(Homotopy):
    def __init__(self, complex_homotopy, mobject, **kwargs):
        """
        Complex Hootopy a function Cx[0, 1] to C
        """

        def homotopy(x, y, z, t):
            c = complex_homotopy(complex(x, y), t)
            return (c.real, c.imag, z)

        Homotopy.__init__(self, homotopy, mobject, **kwargs)


class PhaseFlow(Animation):
    def __init__(
        self,
        function,
        mobject,
        virtual_time=1,
        suspend_mobject_updating=False,
        rate_func=linear,
        **kwargs
    ):
        self.virtual_time = virtual_time
        self.function = function
        super().__init__(
            mobject,
            suspend_mobject_updating=suspend_mobject_updating,
            rate_func=rate_func,
            **kwargs
        )

    def interpolate_mobject(self, alpha):
        if hasattr(self, "last_alpha"):
            dt = self.virtual_time * (alpha - self.last_alpha)
            self.mobject.apply_function(lambda p: p + dt * self.function(p))
        self.last_alpha = alpha


class MoveAlongPath(Animation):
    def __init__(self, mobject, path, suspend_mobject_updating=False, **kwargs):
        self.path = path
        super().__init__(
            mobject, suspend_mobject_updating=suspend_mobject_updating, **kwargs
        )

    def interpolate_mobject(self, alpha):
        point = self.path.point_from_proportion(alpha)
        self.mobject.move_to(point)
