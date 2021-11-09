import numpy as np
import pathops

from manimlib.mobject.types.vectorized_mobject import VMobject


# Boolean operations between 2D mobjects
# Borrowed from from https://github.com/ManimCommunity/manim/

def _convert_vmobject_to_skia_path(vmobject):
    path = pathops.Path()
    subpaths = vmobject.get_subpaths_from_points(vmobject.get_all_points())
    for subpath in subpaths:
        quads = vmobject.get_bezier_tuples_from_points(subpath)
        start = subpath[0]
        path.moveTo(*start[:2])
        for p0, p1, p2 in quads:
            path.quadTo(*p1[:2], *p2[:2])
        if vmobject.consider_points_equals(subpath[0], subpath[-1]):
            path.close()
    return path


def _convert_skia_path_to_vmobject(path, vmobject):
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
    return vmobject


class Union(VMobject):
    def __init__(self, *vmobjects, **kwargs):
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
    def __init__(self, subject, clip, **kwargs):
        super().__init__(**kwargs)
        outpen = pathops.Path()
        pathops.difference(
            [_convert_vmobject_to_skia_path(subject)],
            [_convert_vmobject_to_skia_path(clip)],
            outpen.getPen(),
        )
        _convert_skia_path_to_vmobject(outpen, self)


class Intersection(VMobject):
    def __init__(self, *vmobjects, **kwargs):
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
    def __init__(self, *vmobjects, **kwargs):
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
