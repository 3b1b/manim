from __future__ import annotations

import numpy as np
import pathops

from manimlib.mobject.types.vectorized_mobject import VMobject


# Boolean operations between 2D mobjects
# Borrowed from https://github.com/ManimCommunity/manim/

def _convert_vmobject_to_skia_path(vmobject: VMobject) -> pathops.Path:
    path = pathops.Path()
    for submob in vmobject.family_members_with_points():
        for subpath in submob.get_subpaths():
            quads = vmobject.get_bezier_tuples_from_points(subpath)
            start = subpath[0]
            path.moveTo(*start[:2])
            for p0, p1, p2 in quads:
                path.quadTo(*p1[:2], *p2[:2])
            if vmobject.consider_points_equal(subpath[0], subpath[-1]):
                path.close()
    return path


def _convert_skia_path_to_vmobject(
    path: pathops.Path,
    vmobject: VMobject
) -> VMobject:
    PathVerb = pathops.PathVerb
    current_path_start = np.array([0.0, 0.0, 0.0])
    for path_verb, points in path:
        if path_verb == PathVerb.CLOSE:
            vmobject.add_line_to(current_path_start)
        else:
            points = np.hstack((np.array(points), np.zeros((len(points), 1))))
            if path_verb == PathVerb.MOVE:
                for point in points:
                    current_path_start = point
                    vmobject.start_new_path(point)
            elif path_verb == PathVerb.CUBIC:
                vmobject.add_cubic_bezier_curve_to(*points)
            elif path_verb == PathVerb.LINE:
                vmobject.add_line_to(points[0])
            elif path_verb == PathVerb.QUAD:
                vmobject.add_quadratic_bezier_curve_to(*points)
            else:
                raise Exception(f"Unsupported: {path_verb}")
    return vmobject.reverse_points()


class Union(VMobject):
    """
    Create a vectorized shape representing the union of multiple VMobjects.

    The union combines the filled regions of the input VMobjects into
    a single VMobject using path Boolean operations. Overlapping regions
    are merged, and the resulting geometry is stored in the new object.

    At least two VMobjects must be provided. The input objects are
    converted to Skia paths, which are combined using a union operation,
    and the resulting path is converted back into a VMobject.

    Parameters
    ----------
    *vmobjects : VMobject
        Two or more VMobjects whose filled regions are to be combined.
        Their paths are used to compute the geometric union.
    **kwargs
        Additional keyword arguments passed to the parent ``VMobject``
        constructor. These may include supported styling options such
        as ``color``, ``stroke_width``, ``fill_color``, and
        ``fill_opacity``.

    Raises
    ------
    ValueError
        If fewer than two VMobjects are provided.

    Examples
    --------
    Combine two overlapping circles::

        circle1 = Circle().shift(LEFT * 0.5)
        circle2 = Circle().shift(RIGHT * 0.5)
        union = Union(circle1, circle2)

    Combine multiple shapes::

        union = Union(
            Circle(),
            Square(),
            Triangle(),
            color=BLUE,
        )

    Use the resulting shape in a scene::

        union = Union(
            Circle().shift(LEFT),
            Square().shift(RIGHT),
        )
        self.add(union)

    Notes
    -----
    The union operates on the paths of the input VMobjects. The result
    is a new VMobject containing the combined geometry rather than a
    group of the original objects.

    The appearance of the resulting object depends on its geometry
    and the styling applied to the resulting VMobject.

    See Also
    --------
    VMobject
        Base class for vectorized objects.
    Intersection
        Boolean operation that retains the overlapping regions.
    Difference
        Boolean operation that subtracts one shape from another.
    """

    def __init__(self, *vmobjects: VMobject, **kwargs):
        if len(vmobjects) < 2:
            raise ValueError("At least 2 mobjects needed for Union.")
        super().__init__(**kwargs)
        outpen = pathops.Path()
        paths = [
            _convert_vmobject_to_skia_path(vmobject)
            for vmobject in vmobjects
        ]
        pathops.union(paths, outpen.getPen())
        _convert_skia_path_to_vmobject(outpen, self)


class Difference(VMobject):
    """
    Create a VMobject representing the difference between two shapes.

    The difference operation subtracts the region covered by ``clip``
    from the region covered by ``subject``. The resulting VMobject
    contains the portions of the subject that remain outside the clip.

    Parameters
    ----------
    subject : VMobject
        The VMobject whose region forms the starting shape. The portions
        of this shape that are not covered by ``clip`` are retained.
    clip : VMobject
        The VMobject whose region is subtracted from ``subject``.
    **kwargs
        Additional keyword arguments passed to the parent ``VMobject``
        constructor, such as supported styling options.

    Examples
    --------
    Subtract a circle from a square::

        subject = Square()
        clip = Circle()
        difference = Difference(subject, clip)

    Subtract an overlapping shape::

        subject = Circle().shift(LEFT * 0.5)
        clip = Square().shift(RIGHT * 0.5)
        difference = Difference(subject, clip, color=BLUE)

    Notes
    -----
    The operation uses the paths of the input VMobjects to compute
    the geometric difference. The resulting geometry is stored in
    the new VMobject.

    The order of the arguments matters: ``Difference(subject, clip)``
    is generally not equivalent to ``Difference(clip, subject)``.

    See Also
    --------
    Union
        Combines the regions of multiple VMobjects.
    Intersection
        Retains the regions shared by two VMobjects.
    VMobject
        Base class for vectorized objects.
    """

    def __init__(self, subject: VMobject, clip: VMobject, **kwargs):
        super().__init__(**kwargs)
        outpen = pathops.Path()
        pathops.difference(
            [_convert_vmobject_to_skia_path(subject)],
            [_convert_vmobject_to_skia_path(clip)],
            outpen.getPen(),
        )
        _convert_skia_path_to_vmobject(outpen, self)


class Intersection(VMobject):
    """
    Create a VMobject representing the intersection of multiple shapes.

    The intersection operation retains the regions shared by all the
    provided VMobjects. When more than two VMobjects are supplied,
    their intersections are computed successively to obtain the final
    result.

    At least two VMobjects must be provided. The resulting geometry
    is stored in the new VMobject.

    Parameters
    ----------
    *vmobjects : VMobject
        Two or more VMobjects whose common regions are to be retained.
        The intersection is computed between the first two objects,
        then successively with each remaining object.
    **kwargs
        Additional keyword arguments passed to the parent ``VMobject``
        constructor, including supported styling options.

    Raises
    ------
    ValueError
        If fewer than two VMobjects are provided.

    Examples
    --------
    Find the overlapping region of two circles::

        circle1 = Circle().shift(LEFT * 0.5)
        circle2 = Circle().shift(RIGHT * 0.5)
        intersection = Intersection(circle1, circle2)

    Find the common region of multiple shapes::

        intersection = Intersection(
            Circle(),
            Square(),
            Triangle(),
            color=BLUE,
        )

    Notes
    -----
    The order of the input objects does not change the mathematical
    intersection, although the operation is evaluated successively.

    The resulting VMobject contains the common geometry rather than
    a group of the original input objects.

    See Also
    --------
    Union
        Combines the regions covered by multiple VMobjects.
    Difference
        Subtracts one VMobject's region from another.
    VMobject
        Base class for vectorized objects.
    """

    def __init__(self, *vmobjects: VMobject, **kwargs):
        if len(vmobjects) < 2:
            raise ValueError("At least 2 mobjects needed for Intersection.")
        super().__init__(**kwargs)
        outpen = pathops.Path()
        pathops.intersection(
            [_convert_vmobject_to_skia_path(vmobjects[0])],
            [_convert_vmobject_to_skia_path(vmobjects[1])],
            outpen.getPen(),
        )
        new_outpen = outpen
        for _i in range(2, len(vmobjects)):
            new_outpen = pathops.Path()
            pathops.intersection(
                [outpen],
                [_convert_vmobject_to_skia_path(vmobjects[_i])],
                new_outpen.getPen(),
            )
            outpen = new_outpen
        _convert_skia_path_to_vmobject(outpen, self)


class Exclusion(VMobject):
    """
    Create a VMobject representing the symmetric difference of multiple shapes.

    The exclusion operation retains the regions covered by an odd
    number of the input VMobjects. For two shapes, this means retaining
    the regions belonging to either shape but not to both.

    When more than two VMobjects are provided, the operation is
    applied successively using the exclusive OR (XOR) of their paths.

    At least two VMobjects must be provided. The resulting geometry
    is stored in the new VMobject.

    Parameters
    ----------
    *vmobjects : VMobject
        Two or more VMobjects whose paths are combined using the
        symmetric difference operation. Regions shared by an even
        number of input shapes are excluded from the final result.
    **kwargs
        Additional keyword arguments passed to the parent ``VMobject``
        constructor, including supported styling options.

    Raises
    ------
    ValueError
        If fewer than two VMobjects are provided.

    Examples
    --------
    Exclude the overlapping region of two circles::

        circle1 = Circle().shift(LEFT * 0.5)
        circle2 = Circle().shift(RIGHT * 0.5)
        exclusion = Exclusion(circle1, circle2)

    Apply exclusion to multiple shapes::

        exclusion = Exclusion(
            Circle(),
            Square(),
            Triangle(),
            color=BLUE,
        )

    Notes
    -----
    For two input shapes, the result contains the regions belonging
    to either shape but not to their intersection.

    For multiple shapes, the XOR operation is applied successively.
    Consequently, the final result depends on whether a point belongs
    to an odd or even number of input regions.

    See Also
    --------
    Union
        Combines the regions covered by multiple VMobjects.
    Intersection
        Retains the regions shared by all input VMobjects.
    Difference
        Subtracts one VMobject's region from another.
    VMobject
        Base class for vectorized objects.
    """

    def __init__(self, *vmobjects: VMobject, **kwargs):
        if len(vmobjects) < 2:
            raise ValueError("At least 2 mobjects needed for Exclusion.")
        super().__init__(**kwargs)
        outpen = pathops.Path()
        pathops.xor(
            [_convert_vmobject_to_skia_path(vmobjects[0])],
            [_convert_vmobject_to_skia_path(vmobjects[1])],
            outpen.getPen(),
        )
        new_outpen = outpen
        for _i in range(2, len(vmobjects)):
            new_outpen = pathops.Path()
            pathops.xor(
                [outpen],
                [_convert_vmobject_to_skia_path(vmobjects[_i])],
                new_outpen.getPen(),
            )
            outpen = new_outpen
        _convert_skia_path_to_vmobject(outpen, self)
