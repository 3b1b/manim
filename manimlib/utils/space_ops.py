from __future__ import annotations

import math
import operator as op
from functools import reduce
from typing import Callable, Iterable, Sequence

import numpy as np
from mapbox_earcut import triangulate_float32 as earcut

from manimlib.constants import RIGHT
from manimlib.constants import DOWN
from manimlib.constants import OUT
from manimlib.constants import PI
from manimlib.constants import TAU
from manimlib.utils.iterables import adjacent_pairs
from manimlib.utils.simple_functions import clip


def cross(v1: np.ndarray, v2: np.ndarray) -> list[np.ndarray]:
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]


def get_norm(vect: np.ndarray) -> np.flaoting:
    return sum((x**2 for x in vect))**0.5


# Quaternions
# TODO, implement quaternion type


def quaternion_mult(*quats: Sequence[float]) -> list[float]:
    if len(quats) == 0:
        return [1, 0, 0, 0]
    result = quats[0]
    for next_quat in quats[1:]:
        w1, x1, y1, z1 = result
        w2, x2, y2, z2 = next_quat
        result = [
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2,
            w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2,
        ]
    return result


def quaternion_from_angle_axis(
    angle: float,
    axis: np.ndarray,
    axis_normalized: bool = False
) -> list[float]:
    if not axis_normalized:
        axis = normalize(axis)
    return [math.cos(angle / 2), *(math.sin(angle / 2) * axis)]


def angle_axis_from_quaternion(
    quaternion: Sequence[float]
) -> tuple[float, np.ndarray]:
    axis = normalize(
        quaternion[1:],
        fall_back=[1, 0, 0]
    )
    angle = 2 * np.arccos(quaternion[0])
    if angle > TAU / 2:
        angle = TAU - angle
    return angle, axis


def quaternion_conjugate(quaternion: Iterable) -> list:
    result = list(quaternion)
    for i in range(1, len(result)):
        result[i] *= -1
    return result


def rotate_vector(
    vector: Iterable, 
    angle: float, 
    axis: np.ndarray = OUT
) -> np.ndarray | list[float]:
    if len(vector) == 2:
        # Use complex numbers...because why not
        z = complex(*vector) * np.exp(complex(0, angle))
        result = [z.real, z.imag]
    elif len(vector) == 3:
        # Use quaternions...because why not
        quat = quaternion_from_angle_axis(angle, axis)
        quat_inv = quaternion_conjugate(quat)
        product = quaternion_mult(quat, [0, *vector], quat_inv)
        result = product[1:]
    else:
        raise Exception("vector must be of dimension 2 or 3")

    if isinstance(vector, np.ndarray):
        return np.array(result)
    return result


def thick_diagonal(dim: int, thickness: int = 2) -> np.ndarray:
    row_indices = np.arange(dim).repeat(dim).reshape((dim, dim))
    col_indices = np.transpose(row_indices)
    return (np.abs(row_indices - col_indices) < thickness).astype('uint8')


def rotation_matrix_transpose_from_quaternion(quat: Iterable) -> list[list[float]]:
    quat_inv = quaternion_conjugate(quat)
    return [
        quaternion_mult(quat, [0, *basis], quat_inv)[1:]
        for basis in [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ]
    ]


def rotation_matrix_from_quaternion(quat: Iterable) -> np.ndarray:
    return np.transpose(rotation_matrix_transpose_from_quaternion(quat))


def rotation_matrix_transpose(angle: float, axis: np.ndarray) -> list[list[flaot]]:
    if axis[0] == 0 and axis[1] == 0:
        # axis = [0, 0, z] case is common enough it's worth
        # having a shortcut
        sgn = 1 if axis[2] > 0 else -1
        cos_a = math.cos(angle)
        sin_a = math.sin(angle) * sgn
        return [
            [cos_a, sin_a, 0],
            [-sin_a, cos_a, 0],
            [0, 0, 1],
        ]
    quat = quaternion_from_angle_axis(angle, axis)
    return rotation_matrix_transpose_from_quaternion(quat)


def rotation_matrix(angle: float, axis: np.ndarray) -> np.ndarray:
    """
    Rotation in R^3 about a specified axis of rotation.
    """
    return np.transpose(rotation_matrix_transpose(angle, axis))


def rotation_about_z(angle: float) -> list[list[float]]:
    return [
        [math.cos(angle), -math.sin(angle), 0],
        [math.sin(angle), math.cos(angle), 0],
        [0, 0, 1]
    ]


def z_to_vector(vector: np.ndarray) -> np.ndarray:
    """
    Returns some matrix in SO(3) which takes the z-axis to the
    (normalized) vector provided as an argument
    """
    axis = cross(OUT, vector)
    if get_norm(axis) == 0:
        if vector[2] > 0:
            return np.identity(3)
        else:
            return rotation_matrix(PI, RIGHT)
    angle = np.arccos(np.dot(OUT, normalize(vector)))
    return rotation_matrix(angle, axis=axis)


def rotation_between_vectors(v1, v2) -> np.ndarray:
    if np.all(np.isclose(v1, v2)):
        return np.identity(3)
    return rotation_matrix(
        angle=angle_between_vectors(v1, v2),
        axis=normalize(np.cross(v1, v2))
    )


def angle_of_vector(vector: Sequence[float]) -> float:
    """
    Returns polar coordinate theta when vector is project on xy plane
    """
    return np.angle(complex(*vector[:2]))


def angle_between_vectors(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Returns the angle between two 3D vectors.
    This angle will always be btw 0 and pi
    """
    return math.acos(clip(np.dot(normalize(v1), normalize(v2)), -1, 1))


def project_along_vector(point: np.ndarray, vector: np.ndarray) -> np.ndarray:
    matrix = np.identity(3) - np.outer(vector, vector)
    return np.dot(point, matrix.T)


def normalize(
    vect: np.ndarray,
    fall_back: np.ndarray | None = None
) -> np.ndarray:
    norm = get_norm(vect)
    if norm > 0:
        return np.array(vect) / norm
    elif fall_back is not None:
        return fall_back
    else:
        return np.zeros(len(vect))


def normalize_along_axis(
    array: np.ndarray,
    axis: np.ndarray,
) -> np.ndarray:
    norms = np.sqrt((array * array).sum(axis))
    norms[norms == 0] = 1
    buffed_norms = np.repeat(norms, array.shape[axis]).reshape(array.shape)
    array /= buffed_norms
    return array


def get_unit_normal(
    v1: np.ndarray,
    v2: np.ndarray,
    tol: float=1e-6
) -> np.ndarray:
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


def compass_directions(n: int = 4, start_vect: np.ndarray = RIGHT) -> np.ndarray:
    angle = TAU / n
    return np.array([
        rotate_vector(start_vect, k * angle)
        for k in range(n)
    ])


def complex_to_R3(complex_num: complex) -> np.ndarray:
    return np.array((complex_num.real, complex_num.imag, 0))


def R3_to_complex(point: Sequence[float]) -> complex:
    return complex(*point[:2])


def complex_func_to_R3_func(
    complex_func: Callable[[complex], complex]
) -> Callable[[np.ndarray], np.ndarray]:
    return lambda p: complex_to_R3(complex_func(R3_to_complex(p)))


def center_of_mass(points: Iterable[Sequence[float]]) -> np.ndarray:
    points = [np.array(point).astype("float") for point in points]
    return sum(points) / len(points)


def midpoint(
    point1: Sequence[float],
    point2: Sequence[float]
) -> np.ndarray:
    return center_of_mass([point1, point2])


def line_intersection(
    line1: Sequence[Sequence[float]],
    line2: Sequence[Sequence[float]]
) -> np.ndarray:
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
    p0: Iterable[float],
    v0: Iterable[float],
    p1: Iterable[float],
    v1: Iterable[float],
    threshold: float = 1e-5
) -> np.ndarray:
    """
    Return the intersection of a line passing through p0 in direction v0
    with one passing through p1 in direction v1.  (Or array of intersections
    from arrays of such points/directions).
    For 3d values, it returns the point on the ray p0 + v0 * t closest to the
    ray p1 + v1 * t
    """
    p0 = np.array(p0, ndmin=2)
    v0 = np.array(v0, ndmin=2)
    p1 = np.array(p1, ndmin=2)
    v1 = np.array(v1, ndmin=2)
    m, n = np.shape(p0)
    assert(n in [2, 3])

    numer = np.cross(v1, p1 - p0)
    denom = np.cross(v1, v0)
    if n == 3:
        d = len(np.shape(numer))
        new_numer = np.multiply(numer, numer).sum(d - 1)
        new_denom = np.multiply(denom, numer).sum(d - 1)
        numer, denom = new_numer, new_denom

    denom[abs(denom) < threshold] = np.inf  # So that ratio goes to 0 there
    ratio = numer / denom
    ratio = np.repeat(ratio, n).reshape((m, n))
    return p0 + ratio * v0


def get_closest_point_on_line(
    a: np.ndarray,
    b: np.ndarray,
    p: np.ndarray
) -> np.ndarray:
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


def get_winding_number(points: Iterable[float]) -> float:
    total_angle = 0
    for p1, p2 in adjacent_pairs(points):
        d_angle = angle_of_vector(p2) - angle_of_vector(p1)
        d_angle = ((d_angle + PI) % TAU) - PI
        total_angle += d_angle
    return total_angle / TAU


##

def cross2d(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if len(a.shape) == 2:
        return a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
    else:
        return a[0] * b[1] - b[0] * a[1]


def tri_area(
    a: Sequence[float],
    b: Sequence[float],
    c: Sequence[float]
) -> float:
    return 0.5 * abs(
        a[0] * (b[1] - c[1]) +
        b[0] * (c[1] - a[1]) +
        c[0] * (a[1] - b[1])
    )


def is_inside_triangle(
    p: np.ndarray,
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray
) -> bool:
    """
    Test if point p is inside triangle abc
    """
    crosses = np.array([
        cross2d(p - a, b - p),
        cross2d(p - b, c - p),
        cross2d(p - c, a - p),
    ])
    return np.all(crosses > 0) or np.all(crosses < 0)


def norm_squared(v: Sequence[float]) -> float:
    return v[0] * v[0] + v[1] * v[1] + v[2] * v[2]


# TODO, fails for polygons drawn over themselves
def earclip_triangulation(verts: np.ndarray, ring_ends: list[int]) -> list:
    """
    Returns a list of indices giving a triangulation
    of a polygon, potentially with holes

    - verts is a numpy array of points

    - ring_ends is a list of indices indicating where
    the ends of new paths are
    """

    rings = [
        list(range(e0, e1))
        for e0, e1 in zip([0, *ring_ends], ring_ends)
    ]

    def is_in(point, ring_id):
        return abs(abs(get_winding_number([i - point for i in verts[rings[ring_id]]])) - 1) < 1e-5

    def ring_area(ring_id):
        ring = rings[ring_id]
        s = 0
        for i, j in zip(ring[1:], ring):
            s += cross2d(verts[i], verts[j])
        return abs(s) / 2

    # Points at the same position may cause problems
    for i in rings:
        verts[i[0]] += (verts[i[1]] - verts[i[0]]) * 1e-6
        verts[i[-1]] += (verts[i[-2]] - verts[i[-1]]) * 1e-6

    # First, we should know which rings are directly contained in it for each ring

    right = [max(verts[rings[i], 0]) for i in range(len(rings))]
    left = [min(verts[rings[i], 0]) for i in range(len(rings))]
    top = [max(verts[rings[i], 1]) for i in range(len(rings))]
    bottom = [min(verts[rings[i], 1]) for i in range(len(rings))]
    area = [ring_area(i) for i in range(len(rings))]

    # The larger ring must be outside
    rings_sorted = list(range(len(rings)))
    rings_sorted.sort(key=lambda x: area[x], reverse=True)

    def is_in_fast(ring_a, ring_b):
        # Whether a is in b
        return reduce(op.and_, (
            left[ring_b] <= left[ring_a] <= right[ring_a] <= right[ring_b],
            bottom[ring_b] <= bottom[ring_a] <= top[ring_a] <= top[ring_b],
            is_in(verts[rings[ring_a][0]], ring_b)
        ))

    chilren = [[] for i in rings]
    for idx, i in enumerate(rings_sorted):
        for j in rings_sorted[:idx][::-1]:
            if is_in_fast(i, j):
                chilren[j].append(i)
                break

    res = []

    # Then, we can use earcut for each part
    used = [False] * len(rings)
    for i in rings_sorted:
        if used[i]:
            continue
        v = rings[i]
        ring_ends = [len(v)]
        for j in chilren[i]:
            used[j] = True
            v += rings[j]
            ring_ends.append(len(v))
        res += [v[i] for i in earcut(verts[v, :2], ring_ends)]

    return res
