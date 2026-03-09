from __future__ import annotations

import math

import numpy as np

from manimlib.constants import OUT
from manimlib.utils.bezier import interpolate
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import rotation_matrix_transpose

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from manimlib.typing import Vect3, Vect3Array


STRAIGHT_PATH_THRESHOLD = 0.01


def straight_path(
    start_points: np.ndarray,
    end_points: np.ndarray,
    alpha: float
) -> np.ndarray:
    """
    Same function as interpolate, but renamed to reflect
    intent of being used to determine how a set of points move
    to another set.  For instance, it should be a specific case
    of path_along_arc
    """
    return interpolate(start_points, end_points, alpha)


def path_along_arc(
    arc_angle: float | Tuple[float, float] | np.ndarray,
    axis: Vect3 = OUT
) -> Callable[[Vect3Array, Vect3Array, float], Vect3Array]:
    """
    arc_angle can be a single angle, or a pair of angles, in which case
    the range of all angles between that pair will be used.

    If vect is vector from start to end, [vect[:,1], -vect[:,0]] is
    perpendicular to vect in the left direction.
    """
    if isinstance(arc_angle, float | int) and abs(arc_angle) < STRAIGHT_PATH_THRESHOLD:
        return straight_path
    if get_norm(axis) == 0:
        axis = OUT
    unit_axis = axis / get_norm(axis)

    def path(start_points, end_points, alpha):
        if isinstance(arc_angle, float | int):
            theta = arc_angle
        else:
            if isinstance(arc_angle, np.ndarray) and len(arc_angle) == len(start_points):
                theta_range = arc_angle
            else:
                theta_range = np.linspace(arc_angle[0], arc_angle[-1], len(start_points))
            # Avoid zero, mildly hacky
            theta_range[np.abs(theta_range) < STRAIGHT_PATH_THRESHOLD] = STRAIGHT_PATH_THRESHOLD
            # Get shape to match
            theta = theta_range[:, np.newaxis] * np.ones(start_points.shape[1])
        start_to_end = end_points - start_points

        with np.errstate(divide='ignore', invalid='ignore'):
            adjustments = np.nan_to_num(np.cross(unit_axis, start_to_end / 2.0) / np.tan(theta / 2))
            arc_centers = start_points + 0.5 * start_to_end + adjustments

        c_to_start = start_points - arc_centers
        c_to_perp = np.cross(unit_axis, c_to_start)
        return arc_centers + np.cos(alpha * theta) * c_to_start + np.sin(alpha * theta) * c_to_perp

    return path


def clockwise_path() -> Callable[[Vect3Array, Vect3Array, float], Vect3Array]:
    return path_along_arc(-np.pi)


def counterclockwise_path() -> Callable[[Vect3Array, Vect3Array, float], Vect3Array]:
    return path_along_arc(np.pi)
