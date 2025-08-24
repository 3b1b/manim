from __future__ import annotations

import numpy as np
import pathops
import warnings
from typing import Iterable

from manimlib.mobject.types.vectorized_mobject import VMobject


def _convert_vmobject_to_skia_path(vmobject: VMobject) -> pathops.Path:
    """Convert a VMobject to a Skia Path with proper error handling."""
    path = pathops.Path()
    
    if vmobject.has_no_points():
        return path
    
    try:
        for submob in vmobject.family_members_with_points():
            for subpath in submob.get_subpaths():
                if len(subpath) == 0:
                    continue
                    
                quads = vmobject.get_bezier_tuples_from_points(subpath)
                start = subpath[0]
                path.moveTo(*start[:2])
                
                for p0, p1, p2 in quads:
                    path.quadTo(*p1[:2], *p2[:2])
                    
                if vmobject.consider_points_equal(subpath[0], subpath[-1]):
                    path.close()
    except Exception as e:
        warnings.warn(f"Failed to convert VMobject to Skia path: {e}")
    
    return path


def _convert_skia_path_to_vmobject(
    path: pathops.Path,
    vmobject: VMobject
) -> VMobject:
    """Convert a Skia Path back to a VMobject with proper error handling."""
    PathVerb = pathops.PathVerb
    current_path_start = np.array([0.0, 0.0, 0.0])
    points_list = []
    
    try:
        for path_verb, points in path:
            if path_verb == PathVerb.CLOSE:
                if len(points_list) > 0:
                    # Add line to close the path
                    points_list.append(current_path_start)
            else:
                points = np.hstack((np.array(points), np.zeros((len(points), 1))))
                if path_verb == PathVerb.MOVE:
                    if len(points_list) > 0:
                        # Finish the current path
                        vmobject.add_points(points_list)
                        points_list = []
                    current_path_start = points[0]
                    points_list.append(points[0])
                elif path_verb == PathVerb.CUBIC:
                    if len(points) == 3:  # Cubic bezier has 3 control points
                        points_list.extend(points)
                elif path_verb == PathVerb.LINE:
                    points_list.append(points[0])
                elif path_verb == PathVerb.QUAD:
                    if len(points) == 2:  # Quadratic bezier has 2 control points
                        points_list.extend(points)
        
        # Add any remaining points
        if len(points_list) > 0:
            vmobject.add_points(points_list)
            
    except Exception as e:
        warnings.warn(f"Failed to convert Skia path to VMobject: {e}")
        # Ensure we have a valid VMobject even if conversion fails
        if vmobject.has_no_points():
            vmobject.set_points(np.zeros((1, 3)))
    
    return vmobject


class BooleanOperation(VMobject):
    """Base class for boolean operations between VMobjects."""
    
    def __init__(self, *vmobjects: VMobject, operation: str = "union", **kwargs):
        if len(vmobjects) < 2:
            raise ValueError(f"At least 2 VMobjects needed for {operation}.")
            
        super().__init__(**kwargs)
        
        # Convert all VMobjects to Skia paths
        paths = []
        for vmobj in vmobjects:
            path = _convert_vmobject_to_skia_path(vmobj)
            if not path.is_empty():
                paths.append(path)
        
        # Handle cases with insufficient valid paths
        if len(paths) < 2:
            if len(paths) == 1:
                _convert_skia_path_to_vmobject(paths[0], self)
            return
        
        # Perform the boolean operation
        result_path = pathops.Path()
        try:
            if operation == "union":
                pathops.union(paths, result_path.getPen())
            elif operation == "difference":
                if len(vmobjects) != 2:
                    raise ValueError("Difference operation requires exactly 2 VMobjects.")
                pathops.difference([paths[0]], [paths[1]], result_path.getPen())
            elif operation == "intersection":
                self._apply_sequential_operation(paths, pathops.intersection, result_path)
            elif operation == "exclusion":
                self._apply_sequential_operation(paths, pathops.xor, result_path)
            else:
                raise ValueError(f"Unknown boolean operation: {operation}")
        except Exception as e:
            warnings.warn(f"Boolean operation failed: {e}")
            # Fallback to the first path
            _convert_skia_path_to_vmobject(paths[0], self)
            return
        
        # Convert the result back to a VMobject
        if not result_path.is_empty():
            _convert_skia_path_to_vmobject(result_path, self)
    
    def _apply_sequential_operation(self, paths, operation_func, result_path):
        """Apply a boolean operation sequentially to multiple paths."""
        if len(paths) < 2:
            return
        
        # Start with the first two paths
        temp_path = pathops.Path()
        operation_func([paths[0]], [paths[1]], temp_path.getPen())
        
        # Apply to remaining paths
        for i in range(2, len(paths)):
            next_temp = pathops.Path()
            operation_func([temp_path], [paths[i]], next_temp.getPen())
            temp_path = next_temp
        
        # Copy the final result
        for verb, points in temp_path:
            result_path.addVerb(verb, points)


class Union(BooleanOperation):
    """A VMobject representing the union of multiple VMobjects."""
    
    def __init__(self, *vmobjects: VMobject, **kwargs):
        super().__init__(*vmobjects, operation="union", **kwargs)


class Difference(BooleanOperation):
    """A VMobject representing the difference between two VMobjects (subject - clip)."""
    
    def __init__(self, subject: VMobject, clip: VMobject, **kwargs):
        super().__init__(subject, clip, operation="difference", **kwargs)


class Intersection(BooleanOperation):
    """A VMobject representing the intersection of multiple VMobjects."""
    
    def __init__(self, *vmobjects: VMobject, **kwargs):
        super().__init__(*vmobjects, operation="intersection", **kwargs)


class Exclusion(BooleanOperation):
    """A VMobject representing the exclusion (XOR) of multiple VMobjects."""
    
    def __init__(self, *vmobjects: VMobject, **kwargs):
        super().__init__(*vmobjects, operation="exclusion", **kwargs)