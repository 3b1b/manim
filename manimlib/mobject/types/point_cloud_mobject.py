from __future__ import annotations

import numpy as np

from manimlib.mobject.mobject import Mobject
from manimlib.utils.color import color_gradient
from manimlib.utils.color import color_to_rgba
from manimlib.utils.iterables import resize_with_interpolation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from manimlib.typing import ManimColor, Vect3, Vect3Array, Vect4Array, Self


class PMobject(Mobject):
    """
    A point-based mobject that stores per-point positions and RGBA colors.

    PMobject extends Mobject with utilities for adding, coloring, filtering,
    sorting, combining, and extracting points while keeping point data aligned
    with its associated color and opacity data.

    Methods
    -------
    set_points(points)
        Replace the point array and resize the underlying point data.

    add_points(points, rgbas=None, color=None, opacity=None)
        Append points and optionally assign their RGBA values or a uniform color.

    add_point(point, rgba=None, color=None, opacity=None)
        Append a single point with optional color and opacity.

    set_color_by_gradient(*colors)
        Apply a color gradient across all points.

    match_colors(pmobject)
        Resize and interpolate another PMobject's RGBA data to match this
        object's number of points.

    filter_out(condition)
        Remove points for which the condition returns True.

    sort_points(function)
        Sort point data according to a scalar key computed from each point.
        The default key sorts by the x-coordinate.

    ingest_submobjects()
        Combine the point data from the object's family into this object.

    point_from_proportion(alpha)
        Return the point at the specified normalized index proportion.

    pointwise_become_partial(pmobject, a, b)
        Replace this object's data with a slice of another PMobject's points,
        using normalized bounds a and b.

    Examples
    --------
    Example 1: Create a point-based mobject and add points.

        points = PMobject()
        points.add_points(
            np.array([
                [-1, 0, 0],
                [ 0, 1, 0],
                [ 1, 0, 0],
            ]),
            color=BLUE,
            opacity=0.8,
        )
        self.add(points)

    Example 2: Apply a color gradient.

        points.set_color_by_gradient(BLUE, GREEN, YELLOW)

    The gradient is assigned across the points in their current order.

    Example 3: Sort points by their x-coordinate.

        points.sort_points()

    Pass a custom function to sort by another scalar property, such as
    the y-coordinate:

        points.sort_points(lambda p: p[1])

    Example 4: Filter points using a condition.

        points.filter_out(lambda p: p[1] < 0)

    This removes points whose y-coordinate is negative.

    Example 5: Extract a partial point range.

        partial = PMobject()
        partial.pointwise_become_partial(points, 0.25, 0.75)

    This copies the data slice corresponding approximately to the middle
    half of the source object's points.

    Notes
    -----
    Point arrays must have shape (N, 3). RGBA arrays must have shape (N, 4).
    When a uniform color is provided to add_points(), it takes precedence
    over the supplied rgbas argument.

    filter_out() and sort_points() operate on every family member that
    contains points. point_from_proportion() uses integer indexing, so
    intermediate proportions select the point at the truncated index.

    Returns
    -------
    PMobject
        Most mutating methods return self to allow method chaining.
    """

    def set_points(self, points: Vect3Array):
        if len(points) == 0:
            points = np.zeros((0, 3))
        super().set_points(points)
        self.resize_points(len(points))
        return self

    def add_points(
        self,
        points: Vect3Array,
        rgbas: Vect4Array | None = None,
        color: ManimColor | None = None,
        opacity: float | None = None
    ) -> Self:
        """
        points must be a Nx3 numpy array, as must rgbas if it is not None
        """
        self.append_points(points)
        # rgbas array will have been resized with points
        if color is not None:
            if opacity is None:
                opacity = self.data["rgba"][-1, 3]
            rgbas = np.repeat(
                [color_to_rgba(color, opacity)],
                len(points),
                axis=0
            )
        if rgbas is not None:
            with self.data.being_written() as data:
                data["rgba"][-len(rgbas):] = rgbas
        return self

    def add_point(self, point: Vect3, rgba=None, color=None, opacity=None) -> Self:
        rgbas = None if rgba is None else [rgba]
        self.add_points([point], rgbas, color, opacity)
        return self

    def set_color_by_gradient(self, *colors: ManimColor) -> Self:
        self.data["rgba"] = np.array(list(map(
            color_to_rgba,
            color_gradient(colors, self.get_num_points())
        )))
        return self

    def match_colors(self, pmobject: PMobject) -> Self:
        self.data["rgba"] = resize_with_interpolation(
            pmobject.data["rgba"], self.get_num_points()
        )
        return self

    def filter_out(self, condition: Callable[[np.ndarray], bool]) -> Self:
        for mob in self.family_members_with_points():
            mob.set_data(mob.data[~np.apply_along_axis(condition, 1, mob.get_points())])
        return self

    def sort_points(self, function: Callable[[Vect3], None] = lambda p: p[0]) -> Self:
        """
        function is any map from R^3 to R
        """
        for mob in self.family_members_with_points():
            indices = np.argsort(
                np.apply_along_axis(function, 1, mob.get_points())
            )
            mob.data[:] = mob.data[indices]
        return self

    def ingest_submobjects(self) -> Self:
        self.set_data(np.hstack([
            sm.data.array for sm in self.get_family()
        ]))
        return self

    def point_from_proportion(self, alpha: float) -> np.ndarray:
        index = alpha * (self.get_num_points() - 1)
        return self.get_points()[int(index)]

    def pointwise_become_partial(self, pmobject: PMobject, a: float, b: float) -> Self:
        lower_index = int(a * pmobject.get_num_points())
        upper_index = int(b * pmobject.get_num_points())
        self.set_data(pmobject.data[lower_index:upper_index])
        return self


class PGroup(PMobject):
    """
    A group of :class:`PMobject` instances that combines their point-based data
    into a single object.

    `PGroup` inherits from :class:`PMobject` and accepts multiple PMobject
    instances as submobjects. It validates that every supplied object is a
    PMobject, initializes the parent class, and adds the supplied objects to
    the group.

    Parameters
    ----------
    *pmobs : PMobject
        Any number of PMobject instances to include in the group. If any
        argument is not a PMobject instance, an Exception is raised.
    **kwargs
        Additional keyword arguments forwarded to :class:`PMobject`.

    Raises
    ------
    Exception
        If any supplied submobject is not an instance of PMobject.

    Examples
    --------
    Create a group containing two point-based objects:

        dots = PMobject()
        points = PMobject()

        group = PGroup(dots, points)

    The group can also be initialized without any submobjects:

        group = PGroup()

    Pass keyword arguments to the parent PMobject constructor:

        group = PGroup(dots, points, color=RED)

    Notes
    -----
    PGroup does not independently merge the point data of its submobjects
    during initialization. It adds them using the inherited ``add`` method,
    so their data remains associated with the respective submobjects.

    The validation uses ``isinstance``, so subclasses of PMobject are also
    accepted.
    """

    def __init__(self, *pmobs: PMobject, **kwargs):
        if not all([isinstance(m, PMobject) for m in pmobs]):
            raise Exception("All submobjects must be of type PMobject")
        super().__init__(**kwargs)
        self.add(*pmobs)
