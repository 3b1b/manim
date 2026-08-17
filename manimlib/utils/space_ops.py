from __future__ import annotations

import math

import numpy as np
from scipy.spatial.transform import Rotation

from manimlib.constants import DOWN, OUT, RIGHT, UP
from manimlib.constants import PI, TAU
from manimlib.utils.iterables import adjacent_pairs
from manimlib.utils.simple_functions import clip

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Sequence, List, Tuple
    from manimlib.typing import Vect2, Vect3, Vect4, VectN, Matrix3x3, Vect3Array, Vect2Array


def cross(
    v1: Vect3 | List[float],
    v2: Vect3 | List[float],
    out: np.ndarray | None = None
) -> Vect3 | Vect3Array:
    is2d = isinstance(v1, np.ndarray) and len(v1.shape) == 2
    if is2d:
        x1, y1, z1 = v1[:, 0], v1[:, 1], v1[:, 2]
        x2, y2, z2 = v2[:, 0], v2[:, 1], v2[:, 2]
    else:
        x1, y1, z1 = v1
        x2, y2, z2 = v2
    if out is None:
        out = np.empty(np.shape(v1))
    out.T[:] = [
        y1 * z2 - z1 * y2,
        z1 * x2 - x1 * z2,
        x1 * y2 - y1 * x2,
    ]
    return out


def get_norm(vect: VectN | List[float]) -> float:
    return sum((x**2 for x in vect))**0.5


def get_dist(vect1: VectN, vect2: VectN):
    return get_norm(vect2 - vect1)


def normalize(
    vect: VectN | List[float],
    fall_back: VectN | List[float] | None = None
) -> VectN:
    norm = get_norm(vect)
    if norm > 0:
        return np.array(vect) / norm
    elif fall_back is not None:
        return np.array(fall_back)
    else:
        return np.zeros(len(vect))


def poly_line_length(points):
    """
    Return the sum of the lengths between adjacent points
    """
    diffs = points[1:] - points[:-1]
    return np.sqrt((diffs**2).sum(1)).sum()

# Operations related to rotation


def quaternion_mult(*quats: Vect4) -> Vect4:
    """
    Inputs are treated as quaternions, where the real part is the
    last entry, so as to follow the scipy Rotation conventions.
    """
    if len(quats) == 0:
        return np.array([0, 0, 0, 1])
    result = np.array(quats[0])
    for next_quat in quats[1:]:
        x1, y1, z1, w1 = result
        x2, y2, z2, w2 = next_quat
        result[:] = [
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2,
            w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2,
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
        ]
    return result


def quaternion_from_angle_axis(
    angle: float,
    axis: Vect3,
) -> Vect4:
    return Rotation.from_rotvec(angle * normalize(axis)).as_quat()


def angle_axis_from_quaternion(quat: Vect4) -> Tuple[float, Vect3]:
    rot_vec = Rotation.from_quat(quat).as_rotvec()
    norm = get_norm(rot_vec)
    return norm, rot_vec / norm


def quaternion_conjugate(quaternion: Vect4) -> Vect4:
    result = np.array(quaternion)
    result[:3] *= -1
    return result


def rotate_vector(
    vector: Vect2 | Vect3 | Vect2Array | Vect3Array,
    angle: float,
    axis: Vect3 = OUT
) -> Vect2 | Vect3 | Vect2Array | Vect3Array:
    if np.shape(vector)[-1] == 2:
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        matrix = np.array([
            [cos_angle, -sin_angle],
            [sin_angle, cos_angle],
        ])
        return np.dot(vector, matrix.T)

    rot = Rotation.from_rotvec(angle * normalize(axis))
    return np.dot(vector, rot.as_matrix().T)


def rotate_vector_2d(vector: Vect2, angle: float) -> Vect2:
    # Use complex numbers...because why not
    z = complex(*vector) * np.exp(complex(0, angle))
    return np.array([z.real, z.imag])


def rotation_matrix_transpose_from_quaternion(quat: Vect4) -> Matrix3x3:
    return Rotation.from_quat(quat).as_matrix()


def rotation_matrix_from_quaternion(quat: Vect4) -> Matrix3x3:
    return np.transpose(rotation_matrix_transpose_from_quaternion(quat))


def rotation_matrix(angle: float, axis: Vect3) -> Matrix3x3:
    """
    Rotation in R^3 about a specified axis of rotation.
    """
    return Rotation.from_rotvec(angle * normalize(axis)).as_matrix()


def rotation_matrix_transpose(angle: float, axis: Vect3) -> Matrix3x3:
    return rotation_matrix(angle, axis).T


def rotation_about_z(angle: float) -> Matrix3x3:
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return np.array([
        [cos_a, -sin_a, 0],
        [sin_a, cos_a, 0],
        [0, 0, 1]
    ])


def rotation_between_vectors(v1: Vect3, v2: Vect3) -> Matrix3x3:
    atol = 1e-8
    if get_norm(v1 - v2) < atol:
        return np.identity(3)
    axis = cross(v1, v2)
    if get_norm(axis) < atol:
        # v1 and v2 align
        axis = cross(v1, RIGHT)
    if get_norm(axis) < atol:
        # v1 and v2 _and_ RIGHT all align
        axis = cross(v1, UP)
    return rotation_matrix(
        angle=angle_between_vectors(v1, v2),
        axis=axis,
    )


def z_to_vector(vector: Vect3) -> Matrix3x3:
    return rotation_between_vectors(OUT, vector)


def angle_of_vector(vector: Vect2 | Vect3) -> float:
    """
    Returns polar coordinate theta when vector is project on xy plane
    """
    return math.atan2(vector[1], vector[0])


def angle_between_vectors(v1: VectN, v2: VectN) -> float:
    """
    Returns the angle between two 3D vectors.
    This angle will always be btw 0 and pi
    """
    n1 = get_norm(v1)
    n2 = get_norm(v2)
    if n1 == 0 or n2 == 0:
        return 0
    cos_angle = np.dot(v1, v2) / np.float64(n1 * n2)
    return math.acos(clip(cos_angle, -1, 1))


def project_along_vector(point: Vect3, vector: Vect3) -> Vect3:
    matrix = np.identity(3) - np.outer(vector, vector)
    return np.dot(point, matrix.T)


def normalize_along_axis(
    array: np.ndarray,
    axis: int,
) -> np.ndarray:
    norms = np.sqrt((array * array).sum(axis))
    norms[norms == 0] = 1
    return array / norms[:, np.newaxis]


def get_unit_normal(
    v1: Vect3,
    v2: Vect3,
    tol: float = 1e-6
) -> Vect3:
    v1 = normalize(v1)
    v2 = normalize(v2)
    cp = cross(v1, v2)
    cp_norm = get_norm(cp)
    if cp_norm < tol:
        # Vectors align, so find a normal to them in the plane shared with the z-axis
        new_cp = cross(cross(v1, OUT), v1)
        new_cp_norm = get_norm(new_cp)
        if new_cp_norm < tol:
            return DOWN
        return new_cp / new_cp_norm
    return cp / cp_norm


###


def thick_diagonal(dim: int, thickness: int = 2) -> np.ndarray:
    row_indices = np.arange(dim).repeat(dim).reshape((dim, dim))
    col_indices = np.transpose(row_indices)
    return (np.abs(row_indices - col_indices) < thickness).astype('uint8')


def compass_directions(n: int = 4, start_vect: Vect3 = RIGHT) -> Vect3:
    angle = TAU / n
    return np.array([
        rotate_vector(start_vect, k * angle)
        for k in range(n)
    ])


def complex_to_R3(complex_num: complex) -> Vect3:
    return np.array((complex_num.real, complex_num.imag, 0))


def R3_to_complex(point: Vect3) -> complex:
    return complex(*point[:2])


def complex_func_to_R3_func(complex_func: Callable[[complex], complex]) -> Callable[[Vect3], Vect3]:
    def result(p: Vect3):
        return complex_to_R3(complex_func(R3_to_complex(p)))
    return result


def center_of_mass(points: Sequence[Vect3]) -> Vect3:
    return np.array(points).sum(0) / len(points)


def midpoint(point1: VectN, point2: VectN) -> VectN:
    return center_of_mass([point1, point2])


def line_intersection(
    line1: Tuple[Vect3, Vect3],
    line2: Tuple[Vect3, Vect3]
) -> Vect3:
    """
    return intersection point of two lines,
    each defined with a pair of vectors determining
    the end points
    """
    x_diff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    y_diff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(x_diff, y_diff)
    if div == 0:
        raise Exception("Lines do not intersect")
    d = (det(*line1), det(*line2))
    x = det(d, x_diff) / div
    y = det(d, y_diff) / div
    return np.array([x, y, 0])


def find_intersection(
    p0: Vect3 | Vect3Array,
    v0: Vect3 | Vect3Array,
    p1: Vect3 | Vect3Array,
    v1: Vect3 | Vect3Array,
    threshold: float = 1e-5,
) -> Vect3:
    """
    Return the intersection of a line passing through p0 in direction v0
    with one passing through p1 in direction v1.  (Or array of intersections
    from arrays of such points/directions).

    For 3d values, it returns the point on the ray p0 + v0 * t closest to the
    ray p1 + v1 * t
    """
    d = len(p0.shape)
    if d == 1:
        is_3d = any(arr[2] for arr in (p0, v0, p1, v1))
    else:
        is_3d = any(z for arr in (p0, v0, p1, v1) for z in arr.T[2])
    if not is_3d:
        numer = np.array(cross2d(v1, p1 - p0))
        denom = np.array(cross2d(v1, v0))
    else:
        cp1 = cross(v1, p1 - p0)
        cp2 = cross(v1, v0)
        numer = np.array((cp1 * cp1).sum(d - 1))
        denom = np.array((cp1 * cp2).sum(d - 1))
    denom[abs(denom) < threshold] = np.inf
    ratio = numer / denom
    return p0 + (ratio * v0.T).T


def line_intersects_path(
    start: Vect2 | Vect3,
    end: Vect2 | Vect3,
    path: Vect2Array | Vect3Array,
) -> bool:
    """
    Tests whether the line (start, end) intersects
    a polygonal path defined by its vertices
    """
    n = len(path) - 1
    p1 = np.empty((n, 2))
    q1 = np.empty((n, 2))
    p1[:] = start[:2]
    q1[:] = end[:2]
    p2 = path[:-1, :2]
    q2 = path[1:, :2]

    v1 = q1 - p1
    v2 = q2 - p2

    mis1 = cross2d(v1, p2 - p1) * cross2d(v1, q2 - p1) < 0
    mis2 = cross2d(v2, p1 - p2) * cross2d(v2, q1 - p2) < 0
    return bool((mis1 * mis2).any())


def get_closest_point_on_line(a: VectN, b: VectN, p: VectN) -> VectN:
    """
        It returns point x such that
        x is on line ab and xp is perpendicular to ab.
        If x lies beyond ab line, then it returns nearest edge(a or b).
    """
    # x = b + t*(a-b) = t*a + (1-t)*b
    t = np.dot(p - b, a - b) / np.dot(a - b, a - b)
    if t < 0:
        t = 0
    if t > 1:
        t = 1
    return ((t * a) + ((1 - t) * b))


def boxes_are_disjoint(mins: Vect3Array, maxs: Vect3Array) -> bool:
    """
    Whether no two of the boxes with these lower and upper corners share any of their
    insides, two which meet along a face counting as apart.

    Rather than ask it of every pair, the boxes are swept along the axis they are most
    spread out on: sorted by where each begins, it is compared only with those which
    have begun and not yet ended. For a row of things laid out side by side, which is
    mostly what this is asked about, that is a couple of neighbors each where all pairs
    would be the whole row.
    """
    if len(mins) < 2:
        return True
    spread = maxs.max(0) - mins.min(0)
    # A flat shape has no thickness at all in some direction, and two of them sharing
    # nothing there are not thereby apart, so any such direction is given a little and
    # what is compared is where the two lie in their own plane
    thickness = 1e-6 * max(spread.max(), 1.0)
    maxs = np.where(maxs - mins < thickness, mins + thickness, maxs)

    axis = int(spread.argmax())
    order = np.argsort(mins[:, axis])
    mins, maxs = mins[order], maxs[order]
    # Where the run of boxes still to compare against begins. Since one which ends before
    # the sweep has reached this box ends before every box after it too, the run only ever
    # moves forward, and its first box always reaches past the sweep, so it stops in time
    first = 0
    for index, (low, high) in enumerate(zip(mins, maxs)):
        while maxs[first, axis] <= low[axis]:
            first += 1
        others = slice(first, index)
        if ((mins[others] < high) & (maxs[others] > low)).all(1).any():
            return False
    return True


def get_winding_number(points: Sequence[Vect2 | Vect3]) -> float:
    total_angle = 0
    for p1, p2 in adjacent_pairs(points):
        d_angle = angle_of_vector(p2) - angle_of_vector(p1)
        d_angle = ((d_angle + PI) % TAU) - PI
        total_angle += d_angle
    return total_angle / TAU


##

def cross2d(a: Vect2 | Vect2Array, b: Vect2 | Vect2Array) -> Vect2 | Vect2Array:
    if len(a.shape) == 2:
        return a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
    else:
        return a[0] * b[1] - b[0] * a[1]
