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
    """
    Apply a smoothed vectorized homotopy transformation to a Mobject.

    SmoothedVectorizedHomotopy is a subclass of Homotopy that applies a
    time-dependent geometric transformation to a Mobject while smoothing
    its vectorized point geometry.

    The class inherits the homotopy function and animation behavior from
    Homotopy, but overrides the apply_function_config dictionary to enable
    point smoothing during the transformation.

    This is useful when a homotopy modifies the geometry of vectorized
    objects and a smoother appearance is desired throughout the animation.

    Attributes
    ----------
    apply_function_config : dict
        Configuration passed to Mobject.apply_function during interpolation.
        The default configuration is:

            {"make_smooth": True}

        The make_smooth option requests that the transformed vectorized
        geometry be smoothed when the underlying Mobject supports it.

    Inherited Parameters
    --------------------
    homotopy : Callable[[float, float, float, float], Sequence[float]]
        A time-dependent function that maps a point (x, y, z) and animation
        time t to a transformed point (x', y', z').

    mobject : Mobject
        The object whose geometry is transformed by the homotopy.

    run_time : float, optional
        Duration of the animation in seconds. The default inherited from
        Homotopy is 3.0 seconds.

    **kwargs
        Additional keyword arguments forwarded through the parent Animation
        initialization.

    How It Works
    ------------
    1. The class inherits Homotopy's constructor and interpolation logic.
    2. During interpolation, Homotopy restores each submobject's original
       points and applies the homotopy function at the current animation
       time.
    3. The inherited implementation passes apply_function_config to
       Mobject.apply_function.
    4. Because make_smooth=True is configured here, the transformation
       requests smoothing of the resulting vectorized geometry.

    Example
    -------
    A simple homotopy that gradually shifts points upward:

        import numpy as np
        from manimlib import *

        def upward_homotopy(x, y, z, t):
            return np.array([x, y + t, z])

        square = Square()

        animation = SmoothedVectorizedHomotopy(
            upward_homotopy,
            square,
            run_time=2
        )

        self.play(animation)

    Example: Time-Dependent Horizontal Wave
    ---------------------------------------
    A homotopy can also displace points according to their horizontal
    position and the animation time:

        def wave_homotopy(x, y, z, t):
            return np.array([
                x,
                y + 0.3 * np.sin(2 * x + 2 * np.pi * t),
                z
            ])

        curve = Circle()

        self.play(
            SmoothedVectorizedHomotopy(
                wave_homotopy,
                curve,
                run_time=3
            )
        )

    Notes
    -----
    - This class does not define a new constructor; it inherits the
      constructor from Homotopy.
    - The homotopy function receives four scalar arguments: x, y, z, and t.
    - The time parameter supplied to the homotopy is the animation's
      interpolation alpha, which normally ranges from 0 to 1.
    - Smoothing depends on the behavior of Mobject.apply_function and
      whether the affected object supports vectorized point geometry.
    - The default configuration is defined at the class level. Subclasses
      can override it to customize how the transformation is applied.

    See Also
    --------
    Homotopy
    Mobject.apply_function
    Animation
    """

    apply_function_config: dict = dict(make_smooth=True)


class ComplexHomotopy(Homotopy):
    """
    Animate a Mobject using a time-dependent complex-valued function.

    ComplexHomotopy is a subclass of Homotopy that represents a geometric
    transformation using complex numbers. Instead of directly defining a
    transformation from three-dimensional coordinates (x, y, z) and time t
    to new coordinates, the user supplies a function that maps a complex
    number and time to another complex number.

    The real and imaginary parts of the resulting complex number determine
    the transformed x and y coordinates, respectively. The original z
    coordinate is preserved.

    Parameters
    ----------
    complex_homotopy : Callable[[complex, float], complex]
        A function that accepts a complex number and a time parameter and
        returns a complex number representing the transformed position.

        Conceptually:

            (complex_number, time) -> transformed_complex_number

    mobject : Mobject
        The ManimGL object whose points will be transformed.

    **kwargs
        Additional keyword arguments passed to the parent Homotopy
        constructor, such as run_time and other animation configuration
        options.

    Implementation Details
    ----------------------
    1. The constructor defines an internal function named homotopy.
    2. For each point, its x and y coordinates are combined into a complex
       number using complex(x, y).
    3. The supplied complex_homotopy function transforms that complex
       number at time t.
    4. The real part of the result becomes the new x coordinate.
    5. The imaginary part of the result becomes the new y coordinate.
    6. The original z coordinate is returned unchanged.
    7. The resulting three-dimensional homotopy function is passed to the
       parent Homotopy constructor.

    This allows transformations from complex analysis to be expressed
    naturally as animations of vectorized ManimGL objects.

    Examples
    --------
    Example 1: Rotation in the Complex Plane
    ----------------------------------------
    Multiplication by a complex exponential rotates each point around the
    origin.

        import numpy as np
        from manimlib import *

        def rotate_complex(z, t):
            return z * np.exp(1j * np.pi * t)

        circle = Circle()

        self.play(
            ComplexHomotopy(
                rotate_complex,
                circle,
                run_time=2
            )
        )

    The transformation rotates points through an angle of pi radians
    over the course of the animation.

    Example 2: Scaling
    ------------------
    Multiplying a complex number by a time-dependent real factor changes
    its distance from the origin.

        def scale_complex(z, t):
            return z * (1 + t)

        square = Square()

        self.play(
            ComplexHomotopy(
                scale_complex,
                square,
                run_time=2
            )
        )

    Example 3: Translation in the Complex Plane
    -------------------------------------------
    Adding a complex constant translates points horizontally and vertically.

        def translate_complex(z, t):
            return z + t * (2 + 1j)

        dot = Dot()

        self.play(
            ComplexHomotopy(
                translate_complex,
                dot,
                run_time=2
            )
        )

    Example 4: Complex Conjugation Interpolation
    --------------------------------------------
    A time-dependent function can interpolate between the identity mapping
    and complex conjugation.

        def conjugate_interpolation(z, t):
            return (1 - t) * z + t * np.conjugate(z)

        circle = Circle()

        self.play(
            ComplexHomotopy(
                conjugate_interpolation,
                circle,
                run_time=3
            )
        )

    Notes
    -----
    - The complex plane corresponds to the x-y plane of the Mobject.
    - The z coordinate of every transformed point is preserved.
    - The complex_homotopy function receives the animation's time parameter,
      generally ranging from 0 to 1 during interpolation.
    - The supplied function should return a complex number.
    - This class inherits Homotopy's interpolation behavior and animation
      configuration.
    - The transformation is applied to the object's points, so the
      resulting visual effect depends on the geometry of the Mobject.
    - This class does not automatically guarantee that the transformation
      is invertible or that it preserves distances, angles, or shape.

    See Also
    --------
    Homotopy
    SmoothedVectorizedHomotopy
    Animation
    """

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
    """
    Animate a Mobject by moving its points along a vector field over time.

    PhaseFlow is an Animation subclass that evolves a Mobject according to
    a function representing a velocity field. At each interpolation step,
    the function is evaluated at the current position of each point, and
    the point is displaced by an amount proportional to the elapsed virtual
    time.

    Conceptually, the transformation follows the differential equation:

        dp/dt = function(p)

    where p represents a point and function(p) gives its instantaneous
    velocity vector.

    Parameters
    ----------
    function : Callable[[np.ndarray], np.ndarray]
        A function that accepts a point represented as a NumPy array and
        returns a velocity vector of compatible shape.

    mobject : Mobject
        The object whose points will move according to the vector field.

    virtual_time : float or None, optional
        The total virtual time over which the vector field is applied.
        If None, or if a falsy value such as 0 is supplied, it defaults to
        run_time because the implementation uses:

            self.virtual_time = virtual_time or run_time

    suspend_mobject_updating : bool, optional
        Whether to suspend the Mobject's regular updating during the
        animation. Defaults to False.

    rate_func : Callable[[float], float], optional
        A function that maps animation progress to interpolation progress.
        Defaults to linear.

    run_time : float, optional
        The animation duration in seconds. Defaults to 3.0.

    **kwargs
        Additional keyword arguments forwarded to the parent Animation
        constructor.

    Attributes
    ----------
    function
        The velocity field used to move the Mobject's points.

    virtual_time
        The effective duration of the simulated vector-field evolution.

    last_alpha
        The previous interpolation value recorded by interpolate_mobject.
        It is initialized during the first interpolation call.

    How It Works
    ------------
    1. The constructor stores the velocity field and determines the
       effective virtual time.
    2. The parent Animation constructor initializes the animation using
       the supplied rate function, runtime, and other configuration.
    3. During interpolation, the current alpha is compared with the
       previously recorded alpha.
    4. The difference is multiplied by virtual_time to calculate the
       virtual time increment, dt.
    5. Each point p is updated using the explicit Euler step:

           p_new = p + dt * function(p)

    6. The current alpha is stored as last_alpha for the next step.

    The first interpolation call only records last_alpha. No point
    displacement occurs on that call because the update is guarded by
    hasattr(self, "last_alpha").

    Examples
    --------
    Example 1: Uniform Translation
    ------------------------------
    A constant velocity field moves every point in the same direction.

        import numpy as np
        from manimlib import *

        def velocity(p):
            return np.array([1.0, 0.0, 0.0])

        square = Square()

        self.play(
            PhaseFlow(
                velocity,
                square,
                virtual_time=2,
                run_time=3
            )
        )

    The field points along the positive x-axis. The virtual time controls
    the accumulated displacement, while run_time controls the animation's
    duration.

    Example 2: Rotation Around the Origin
    ------------------------------------
    A rotational vector field moves points tangentially around the origin.

        def rotational_field(p):
            x, y, z = p
            return np.array([-y, x, 0.0])

        square = Square()

        self.play(
            PhaseFlow(
                rotational_field,
                square,
                virtual_time=2,
                run_time=3
            )
        )

    This field produces rotational motion. The numerical result depends on
    the discrete time steps used during animation.

    Example 3: Radial Expansion
    ---------------------------
    A field proportional to each point's position pushes points away from
    the origin.

        def radial_field(p):
            return p

        circle = Circle()

        self.play(
            PhaseFlow(
                radial_field,
                circle,
                virtual_time=1,
                run_time=2
            )
        )

    Example 4: A Two-Dimensional Swirling Field
    -------------------------------------------
    A position-dependent field can create more complex motion.

        def swirl_field(p):
            x, y, z = p
            return np.array([
                -0.5 * y,
                 0.5 * x,
                 0.0
            ])

        dots = VGroup(*[
            Dot(point)
            for point in [
                LEFT, RIGHT, UP, DOWN,
                2 * LEFT, 2 * RIGHT
            ]
        ])

        self.play(
            PhaseFlow(
                swirl_field,
                dots,
                virtual_time=2,
                run_time=4
            )
        )

    Notes
    -----
    - This implementation uses an explicit Euler-style update rather than
      solving the differential equation exactly.
    - The numerical accuracy depends on the interpolation step sizes and
      the behavior of the velocity field.
    - The field is evaluated at the points' current positions, so the
      transformation is incremental rather than recalculated from a
      stored original geometry at every frame.
    - The rate_func affects alpha progression and therefore influences the
      virtual time increments.
    - A decreasing alpha can produce a negative dt and reverse the
      direction of the incremental update.
    - The function should return a NumPy-compatible vector with a shape
      suitable for the points supplied by Mobject.apply_function.
    - If virtual_time is 0, the implementation falls back to run_time.
    - Because updates are incremental, repeated interpolation or unusual
      alpha sequences may affect the resulting geometry.

    See Also
    --------
    Animation
    Homotopy
    ComplexHomotopy
    Mobject.apply_function
    """

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
    """
    Animate a Mobject moving along a specified VMobject path.

    MoveAlongPath is an Animation subclass that moves a Mobject along the
    geometry of another VMobject. At each interpolation step, it calculates
    a point on the path using the animation's rate function and moves the
    animated Mobject to that position.

    The position is determined by the proportion of the path traversed,
    rather than by directly calculating a velocity or applying a
    transformation to each individual point of the animated Mobject.

    Parameters
    ----------
    mobject : Mobject
        The object that will move along the path. Its position is updated
        during interpolation using the move_to method.

    path : VMobject
        The vectorized Mobject defining the trajectory. The path's geometry
        determines the positions through which the animated Mobject moves.

    suspend_mobject_updating : bool, optional
        Whether to suspend the animated Mobject's regular updating during
        the animation. Defaults to False.

    **kwargs
        Additional keyword arguments passed to the parent Animation
        constructor. These may include run_time, rate_func, and other
        supported animation configuration options.

    Attributes
    ----------
    path : VMobject
        The path along which the animated Mobject moves.

    Inherited Attributes
    --------------------
    rate_func
        The rate function inherited from Animation. It maps the animation's
        interpolation alpha to the proportion used to sample the path.

    run_time
        The animation duration in seconds, configured through the parent
        Animation constructor.

    How It Works
    ------------
    1. The constructor stores the supplied path in self.path.
    2. It initializes the parent Animation with the animated Mobject and
       the suspend_mobject_updating setting.
    3. During interpolation, the current alpha is passed through rate_func.
    4. The resulting proportion is passed to
       path.quick_point_from_proportion().
    5. The returned point is supplied to mobject.move_to(), positioning
       the animated Mobject at that location.

    Mathematically, the target position can be represented as:

        position(alpha) = path.point(rate_func(alpha))

    Here, the path's point-sampling method determines the actual location
    for the requested proportion.

    Examples
    --------
    Example 1: Move a Dot Along a Circle
    -----------------------------------
    A Dot can follow the trajectory defined by a Circle.

        from manimlib import *

        path = Circle(radius=2)
        dot = Dot(path.get_start())

        self.add(path, dot)
        self.play(
            MoveAlongPath(
                dot,
                path,
                run_time=3
            )
        )

    The Dot moves along the circle's path over the animation duration.

    Example 2: Follow a Curved Path
    -------------------------------
    A custom VMobject can define a curved trajectory.

        from manimlib import *

        path = VMobject()
        path.set_points_as_corners([
            LEFT * 3,
            UP * 2,
            RIGHT * 3
        ])

        dot = Dot(path.get_start())

        self.add(path, dot)
        self.play(
            MoveAlongPath(
                dot,
                path,
                run_time=2
            )
        )

    The Dot follows the path through the positions defined by the VMobject.

    Example 3: Use a Nonlinear Rate Function
    ----------------------------------------
    A rate function changes how quickly the object progresses through
    the path's proportions.

        from manimlib import *

        path = Arc(
            angle=PI,
            radius=2
        )
        dot = Dot(path.get_start())

        self.add(path, dot)
        self.play(
            MoveAlongPath(
                dot,
                path,
                rate_func=smooth,
                run_time=3
            )
        )

    The smooth rate function changes the progression through the path:
    movement is slower near the beginning and end and faster around the
    middle.

    Example 4: Move a Label Along a Line
    ------------------------------------
    The animated Mobject does not have to be a Dot.

        from manimlib import *

        path = Line(LEFT * 3, RIGHT * 3)
        label = Text("Moving label")
        label.move_to(path.get_start())

        self.add(path, label)
        self.play(
            MoveAlongPath(
                label,
                path,
                run_time=2
            )
        )

    Notes
    -----
    - The path is used to determine the animated object's target position.
      The path itself is not transformed by this class.
    - The animated Mobject is repositioned using move_to(). Its internal
      geometry is translated rather than reshaped to match the path.
    - The animated Mobject does not automatically rotate to align with
      the direction of travel.
    - The rate function controls the proportion passed to the path
      sampling method, so nonlinear rate functions alter the timing
      of movement.
    - The path should provide a valid implementation of
      quick_point_from_proportion().
    - The path's own visibility is independent of its use as a trajectory.
      Add it to the scene separately if it should be visible.
    - The final position depends on the path's sampling behavior and the
      value returned by rate_func at the end of the animation.

    See Also
    --------
    Animation
    VMobject
    Mobject.move_to
    Homotopy
    PhaseFlow
    """

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
