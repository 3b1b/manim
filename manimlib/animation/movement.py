from __future__ import annotations

from manimlib.animation.animation import Animation
from manimlib.utils.rate_functions import linear

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Sequence

    import numpy as np

    from manimlib.mobject.mobject import Mobject
    from manimlib.mobject.types.vectorized_mobject import VMobject


class Homotopy(Animation):
    """
    Animate a Mobject using a time-dependent homotopy transformation.

    Homotopy is a subclass of Animation that deforms a Mobject by applying
    a function that maps each point (x, y, z) to a new position (x', y', z')
    depending on the animation time t.

    Unlike a simple transformation between two fixed shapes, a homotopy can
    define a continuous deformation using a mathematical function. This makes
    it useful for wave effects, nonlinear distortions, coordinate mappings,
    and other animations in which points move according to a custom rule.

    Parameters
    ----------
    homotopy : Callable[[float, float, float, float], Sequence[float]]
        A function accepting four arguments: x, y, z, and t. It must return
        a sequence containing the transformed coordinates (x', y', z').

    mobject : Mobject
        The object whose points will be transformed by the homotopy.

    run_time : float, default=3.0
        Duration of the animation in seconds.

    **kwargs
        Additional keyword arguments forwarded to the Animation constructor,
        such as rate_func and other supported animation settings.

    Class Attributes
    ----------------
    apply_function_config : dict
        Configuration dictionary passed to Mobject.apply_function().
        Subclasses can override this dictionary to customize how the
        homotopy transformation is applied.

    Attributes
    ----------
    homotopy
        The supplied four-argument transformation function.

    Methods
    -------
    function_at_time_t(t)
        Returns a function that accepts a point and applies the homotopy
        using the specified time t.

    interpolate_submobject(submob, start, alpha)
        Restores the submobject's points from its starting state and applies
        the homotopy evaluated at the current animation progress alpha.

    Implementation Details
    ----------------------
    1. The constructor stores the supplied homotopy function.
    2. The Animation constructor initializes the target Mobject and duration.
    3. During interpolation, match_points(start) resets the submobject's
       geometry to its starting points.
    4. function_at_time_t(alpha) creates a point-transformation function
       using the current animation progress.
    5. apply_function() applies that function to the submobject, using the
       options specified by apply_function_config.

    Mathematical Idea
    -----------------
    A homotopy can be represented as a time-dependent mapping:

        H(x, y, z, t) = (x', y', z')

    Here, (x, y, z) is an original point, t represents animation progress,
    and (x', y', z') is the point's position after applying the deformation.

    For example, a homotopy might move every point upward by an amount
    that depends on its horizontal coordinate and the current time.

    Examples
    --------
    Example 1: Apply a vertical deformation.

        def vertical_homotopy(x, y, z, t):
            return np.array([
                x,
                y + 0.5 * np.sin(PI * t),
                z
            ])

        circle = Circle()
        self.add(circle)

        self.play(
            Homotopy(vertical_homotopy, circle)
        )

    The circle's points move vertically during the animation and return
    toward their original positions as the sine term returns to zero.

    Example 2: Create a horizontal wave.

        def wave_homotopy(x, y, z, t):
            return np.array([
                x + 0.3 * np.sin(2 * PI * y) * np.sin(PI * t),
                y,
                z
            ])

        square = Square()
        self.add(square)

        self.play(
            Homotopy(wave_homotopy, square)
        )

    Each point moves horizontally according to its y-coordinate, creating
    a wave-like deformation.

    Example 3: Scale points outward over time.

        def expansion_homotopy(x, y, z, t):
            factor = 1 + 0.5 * t
            return np.array([
                factor * x,
                factor * y,
                factor * z
            ])

        circle = Circle()
        self.add(circle)

        self.play(
            Homotopy(
                expansion_homotopy,
                circle,
                run_time=2
            )
        )

    The points move progressively farther from the origin as t increases.

    Example 4: Rotate points around the z-axis.

        def rotation_homotopy(x, y, z, t):
            angle = PI * t
            return np.array([
                x * np.cos(angle) - y * np.sin(angle),
                x * np.sin(angle) + y * np.cos(angle),
                z
            ])

        square = Square()
        self.add(square)

        self.play(
            Homotopy(rotation_homotopy, square)
        )

    The homotopy rotates each point around the z-axis as the animation
    progresses.

    Notes
    -----
    - The homotopy function receives four scalar arguments: x, y, z, and t.
    - The animation progress alpha is passed as t by this implementation.
    - The returned coordinates should be compatible with the point
      transformation expected by Mobject.apply_function().
    - match_points(start) restores the original point geometry before
      applying each frame's deformation, preventing transformations from
      accumulating across frames.
    - The actual deformation depends entirely on the supplied homotopy.
    - apply_function_config can be overridden by subclasses to customize
      the behavior of apply_function().

    See Also
    --------
    Animation
        Base class for time-dependent animations.
    Mobject.apply_function
        Applies a coordinate transformation to a Mobject.
    ApplyWave
        Uses a homotopy to create a traveling wave-like deformation.
    """

    apply_function_config: dict = dict()

    def __init__(
        self,
        homotopy: Callable[[float, float, float, float], Sequence[float]],
        mobject: Mobject,
        run_time: float = 3.0,
        **kwargs
    ):
        """
        Homotopy is a function from
        (x, y, z, t) to (x', y', z')
        """
        self.homotopy = homotopy
        super().__init__(mobject, run_time=run_time, **kwargs)

    def function_at_time_t(self, t: float) -> Callable[[np.ndarray], Sequence[float]]:
        def result(p):
            return self.homotopy(*p, t)
        return result

    def interpolate_submobject(
        self,
        submob: Mobject,
        start: Mobject,
        alpha: float
    ) -> None:
        submob.match_points(start)
        submob.apply_function(
            self.function_at_time_t(alpha),
            **self.apply_function_config
        )


class SmoothedVectorizedHomotopy(Homotopy):
    apply_function_config: dict = dict(make_smooth=True)


class ComplexHomotopy(Homotopy):
    def __init__(
        self,
        complex_homotopy: Callable[[complex, float], complex],
        mobject: Mobject,
        **kwargs
    ):
        """
        Given a function form (z, t) -> w, where z and w
        are complex numbers and t is time, this animates
        the state over time
        """
        def homotopy(x, y, z, t):
            c = complex_homotopy(complex(x, y), t)
            return (c.real, c.imag, z)

        super().__init__(homotopy, mobject, **kwargs)


class PhaseFlow(Animation):
    def __init__(
        self,
        function: Callable[[np.ndarray], np.ndarray],
        mobject: Mobject,
        virtual_time: float | None = None,
        suspend_mobject_updating: bool = False,
        rate_func: Callable[[float], float] = linear,
        run_time: float =3.0,
        **kwargs
    ):
        self.function = function
        self.virtual_time = virtual_time or run_time
        super().__init__(
            mobject,
            rate_func=rate_func,
            run_time=run_time,
            suspend_mobject_updating=suspend_mobject_updating,
            **kwargs
        )

    def interpolate_mobject(self, alpha: float) -> None:
        if hasattr(self, "last_alpha"):
            dt = self.virtual_time * (alpha - self.last_alpha)
            self.mobject.apply_function(
                lambda p: p + dt * self.function(p)
            )
        self.last_alpha = alpha


class MoveAlongPath(Animation):
    def __init__(
        self,
        mobject: Mobject,
        path: VMobject,
        suspend_mobject_updating: bool = False,
        **kwargs
    ):
        self.path = path
        super().__init__(mobject, suspend_mobject_updating=suspend_mobject_updating, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        point = self.path.quick_point_from_proportion(self.rate_func(alpha))
        self.mobject.move_to(point)
