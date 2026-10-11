from __future__ import annotations

from manimlib.animation.transform import Transform

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

    from manimlib.mobject.geometry import Arrow
    from manimlib.mobject.mobject import Mobject
    from manimlib.typing import ManimColor


class GrowFromPoint(Transform):
    """
    Animate a mobject growing from a specified point into its original shape.

    GrowFromPoint is a subclass of Transform that creates a starting version
    of the mobject by scaling a copy down to zero size and moving it to a
    specified point. The animation then transforms this collapsed starting
    mobject into the original mobject.

    Optionally, a different color can be applied to the starting mobject.
    This allows the object to grow from a point with one color and transition
    toward its original appearance during the transformation.

    Parameters
    ----------
    mobject : Mobject
        The object to animate. It grows from the specified point into its
        original shape and appearance.

    point : np.ndarray
        The position in space from which the object grows. The starting
        mobject is moved to this point after being scaled to zero.

    point_color : ManimColor, optional
        An optional color applied to the starting mobject. If None, the
        starting mobject retains the color inherited from its copy of the
        original mobject. Defaults to None.

    **kwargs
        Additional keyword arguments forwarded to Transform, such as
        ``run_time`` and other supported transformation settings.

    Methods
    -------
    create_target() -> Mobject
        Return a copy of the original mobject to serve as the transformation
        target.

    create_starting_mobject() -> Mobject
        Create the starting state for the animation by calling the parent
        implementation, scaling the resulting mobject to zero size, moving it
        to ``self.point``, and optionally applying ``self.point_color``.

    Notes
    -----
    - The original mobject is used as the transformation source passed to
      Transform, while ``create_target()`` returns a copy for the target.
    - The starting mobject is scaled to zero before being moved to the
      specified point.
    - ``point_color`` is applied only when it is not None.
    - The animation's interpolation and cleanup behavior are inherited from
      Transform and its parent animation classes.
    - The exact visual result depends on the mobject's geometry, color, and
      the interpolation settings passed through ``kwargs``.

    Examples
    --------
    Example 1: Grow a circle from the origin.

    >>> circle = Circle()
    >>> scene.play(GrowFromPoint(circle, ORIGIN))

    The circle begins collapsed at the origin and transforms into its
    original shape.

    Example 2: Grow a square from a specific position.

    >>> square = Square()
    >>> point = LEFT * 3 + DOWN
    >>> scene.play(GrowFromPoint(square, point))

    The square starts at the specified point and grows into its target shape.
    Here, ``LEFT * 3 + DOWN`` represents a position three units to the left
    and one unit downward from the origin.

    Example 3: Specify the starting color.

    >>> triangle = Triangle(color=BLUE)
    >>> scene.play(
    ...     GrowFromPoint(
    ...         triangle,
    ...         ORIGIN,
    ...         point_color=YELLOW,
    ...     )
    ... )

    The starting mobject is assigned yellow before the transformation begins.
    The target is a copy of the original triangle, so the animation can
    transition from the starting state toward the target's appearance.

    Example 4: Customize the animation duration.

    >>> dot = Dot()
    >>> scene.play(
    ...     GrowFromPoint(
    ...         dot,
    ...         RIGHT * 2,
    ...         run_time=2,
    ...     )
    ... )

    The dot grows from the point two units to the right of the origin over
    two seconds.

    See Also
    --------
    Transform
    GrowFromCenter
    GrowFromEdge
    SpinInFromNothing
    Mobject.scale
    Mobject.move_to
    """

    def __init__(
        self,
        mobject: Mobject,
        point: np.ndarray,
        point_color: ManimColor = None,
        **kwargs
    ):
        self.point = point
        self.point_color = point_color
        super().__init__(mobject, **kwargs)

    def create_target(self) -> Mobject:
        return self.mobject.copy()

    def create_starting_mobject(self) -> Mobject:
        start = super().create_starting_mobject()
        start.scale(0)
        start.move_to(self.point)
        if self.point_color is not None:
            start.set_color(self.point_color)
        return start


class GrowFromCenter(GrowFromPoint):
    """
    Animate a mobject growing from its own center into its original shape.

    GrowFromCenter is a subclass of GrowFromPoint that automatically chooses
    the center of the supplied mobject as the starting point. Instead of
    requiring the caller to provide a position explicitly, it obtains the
    center using ``mobject.get_center()`` and passes that point to
    GrowFromPoint.

    The inherited animation creates a starting mobject by scaling it to zero,
    moving it to the chosen point, and transforming it into the target
    mobject. As a result, the object appears to expand outward from its
    center.

    Parameters
    ----------
    mobject : Mobject
        The object to animate. Its center is used as the point from which
        the animation begins.

    **kwargs
        Additional keyword arguments forwarded to GrowFromPoint and then
        to Transform. These may include options such as ``run_time`` and
        ``point_color``.

    Methods
    -------
    __init__(mobject: Mobject, **kwargs)
        Obtain the center of ``mobject`` using ``get_center()`` and initialize
        the parent GrowFromPoint animation with that center as its starting
        point.

    Inherited Behavior
    ------------------
    GrowFromCenter inherits the following behavior from GrowFromPoint:

    - Creates a copy of the original mobject as the transformation target.
    - Creates a starting mobject scaled to zero size.
    - Moves the starting mobject to the chosen center point.
    - Optionally applies ``point_color`` to the starting mobject.
    - Uses Transform's interpolation and cleanup behavior.

    Notes
    -----
    - The starting point is calculated when the GrowFromCenter constructor
      runs. It is not continuously recalculated during the animation.
    - ``get_center()`` returns the center according to the mobject's
      geometry and bounding box.
    - Unlike GrowFromPoint, this class does not require an explicit point
      argument.
    - Since ``kwargs`` are forwarded to GrowFromPoint, supported options
      from that class can also be supplied here.

    Examples
    --------
    Example 1: Grow a circle from its center.

    >>> circle = Circle()
    >>> scene.play(GrowFromCenter(circle))

    The circle begins collapsed at its center and expands into its original
    shape.

    Example 2: Grow a square from its current position.

    >>> square = Square().shift(RIGHT * 3 + UP)
    >>> scene.play(GrowFromCenter(square))

    The square grows from its own center, even though it has been shifted
    away from the origin.

    Example 3: Set a custom duration.

    >>> triangle = Triangle()
    >>> scene.play(GrowFromCenter(triangle, run_time=2))

    The triangle grows from its center over two seconds.

    Example 4: Specify the starting color.

    >>> circle = Circle(color=BLUE)
    >>> scene.play(
    ...     GrowFromCenter(
    ...         circle,
    ...         point_color=YELLOW,
    ...     )
    ... )

    The starting mobject is assigned yellow, while the target is a copy of
    the original blue circle. The transformation interpolates between the
    starting and target states.

    See Also
    --------
    GrowFromPoint
    Transform
    Mobject.get_center
    Mobject.scale
    Mobject.move_to
    """

    def __init__(self, mobject: Mobject, **kwargs):
        point = mobject.get_center()
        super().__init__(mobject, point, **kwargs)


class GrowFromEdge(GrowFromPoint):
    """
    Animate a mobject growing from one of its bounding-box edges.

    GrowFromEdge is a subclass of GrowFromPoint that automatically determines
    the starting point from a specified direction relative to the mobject.
    It uses ``mobject.get_bounding_box_point(edge)`` to find the point on the
    mobject's bounding box corresponding to the given direction, then passes
    that point to GrowFromPoint.

    The inherited animation creates a starting version of the mobject, scales
    it to zero size, moves it to the selected edge point, and transforms it
    into the original target. This makes the object appear to expand outward
    from the specified side.

    Parameters
    ----------
    mobject : Mobject
        The object to animate. Its bounding box is used to determine the
        starting point.

    edge : np.ndarray
        A direction vector that identifies the bounding-box point from which
        the object should grow. Common directions include ``UP``, ``DOWN``,
        ``LEFT``, and ``RIGHT``. Diagonal directions can also be used.

    **kwargs
        Additional keyword arguments forwarded to GrowFromPoint and then
        to Transform. These may include ``run_time`` and ``point_color``.

    Methods
    -------
    __init__(mobject: Mobject, edge: np.ndarray, **kwargs)
        Determine the starting point by calling
        ``mobject.get_bounding_box_point(edge)`` and initialize the parent
        GrowFromPoint animation with that point.

    Inherited Behavior
    ------------------
    GrowFromEdge inherits the transformation setup from GrowFromPoint:

    - Creates a copy of the original mobject as the target.
    - Creates a starting mobject scaled to zero size.
    - Moves the starting mobject to the calculated bounding-box point.
    - Optionally applies ``point_color`` to the starting mobject.
    - Uses the interpolation and cleanup behavior inherited from Transform.

    Notes
    -----
    - The ``edge`` argument is a direction, not a literal coordinate.
    - ``get_bounding_box_point(edge)`` selects a point on the bounding box
      in the specified direction.
    - For a typical rectangular object, ``RIGHT`` selects the middle of its
      right side, while ``UP`` selects the middle of its top side.
    - The starting point is calculated when the constructor runs.
    - The precise location depends on the object's bounding box and the
      direction supplied.

    Examples
    --------
    Example 1: Grow a square from its left edge.

    >>> square = Square()
    >>> scene.play(GrowFromEdge(square, LEFT))

    The square starts collapsed at the midpoint of its left bounding-box
    edge and grows into its original shape.

    Example 2: Grow a circle from the top.

    >>> circle = Circle()
    >>> scene.play(GrowFromEdge(circle, UP))

    The circle grows from the topmost point of its bounding box.

    Example 3: Grow an object from its bottom edge.

    >>> triangle = Triangle()
    >>> scene.play(GrowFromEdge(triangle, DOWN, run_time=2))

    The triangle grows from the bottom of its bounding box over two seconds.

    Example 4: Use a diagonal direction.

    >>> square = Square()
    >>> scene.play(GrowFromEdge(square, UR))

    The starting point is selected from the upper-right direction of the
    square's bounding box, so the square grows from that corner region.

    Example 5: Customize the starting color.

    >>> circle = Circle(color=BLUE)
    >>> scene.play(
    ...     GrowFromEdge(
    ...         circle,
    ...         RIGHT,
    ...         point_color=YELLOW,
    ...     )
    ... )

    The starting mobject is assigned yellow, while the target is a copy of
    the original blue circle.

    See Also
    --------
    GrowFromPoint
    GrowFromCenter
    Transform
    Mobject.get_bounding_box_point
    """

    def __init__(self, mobject: Mobject, edge: np.ndarray, **kwargs):
        point = mobject.get_bounding_box_point(edge)
        super().__init__(mobject, point, **kwargs)


class GrowArrow(GrowFromPoint):
    """
    Animate an Arrow growing outward from its starting point.

    GrowArrow is a subclass of GrowFromPoint specialized for Arrow objects.
    Instead of requiring an explicit starting position, it obtains the
    arrow's start point using ``arrow.get_start()`` and passes that point
    to GrowFromPoint.

    The inherited animation creates a starting version of the arrow, scales
    it to zero size, moves it to the arrow's starting point, and transforms
    it into the original arrow. This makes the arrow appear to extend
    outward from its tail toward its tip.

    Parameters
    ----------
    arrow : Arrow
        The arrow to animate. Its starting point determines where the
        animation begins.

    **kwargs
        Additional keyword arguments forwarded to GrowFromPoint and then
        to Transform. These may include ``run_time`` and ``point_color``.

    Methods
    -------
    __init__(arrow: Arrow, **kwargs)
        Get the arrow's starting point with ``arrow.get_start()`` and
        initialize GrowFromPoint using that point.

    Inherited Behavior
    ------------------
    GrowArrow inherits the animation setup from GrowFromPoint:

    - Creates a copy of the arrow as the transformation target.
    - Creates a starting mobject scaled to zero size.
    - Moves the starting mobject to the arrow's starting point.
    - Optionally applies ``point_color`` to the starting mobject.
    - Uses the interpolation and cleanup behavior inherited from Transform.

    Notes
    -----
    - This class is intended for Arrow objects.
    - The starting point is obtained when the constructor runs.
    - The arrow's start point is the tail of the arrow; the tip is its
      endpoint.
    - The actual appearance during interpolation depends on the arrow's
      geometry and the behavior inherited from Transform.

    Examples
    --------
    Example 1: Grow an arrow from its tail.

    >>> arrow = Arrow(LEFT, RIGHT)
    >>> scene.play(GrowArrow(arrow))

    The arrow begins at its tail and grows toward its tip.

    Example 2: Grow an upward arrow.

    >>> arrow = Arrow(DOWN, UP)
    >>> scene.play(GrowArrow(arrow, run_time=2))

    The arrow extends upward from its starting point over two seconds.

    Example 3: Grow an arrow at a shifted position.

    >>> arrow = Arrow(LEFT, RIGHT).shift(UP * 2)
    >>> scene.play(GrowArrow(arrow))

    The arrow grows from its own start point, even though it has been
    shifted away from its original position.

    Example 4: Specify the starting color.

    >>> arrow = Arrow(LEFT, RIGHT, color=BLUE)
    >>> scene.play(
    ...     GrowArrow(
    ...         arrow,
    ...         point_color=YELLOW,
    ...     )
    ... )

    The starting mobject is assigned yellow, while the target is a copy of
    the original blue arrow. The transformation interpolates between the
    starting and target states.

    See Also
    --------
    GrowFromPoint
    GrowFromCenter
    GrowFromEdge
    Arrow
    Arrow.get_start
    """

    def __init__(self, arrow: Arrow, **kwargs):
        point = arrow.get_start()
        super().__init__(arrow, point, **kwargs)
