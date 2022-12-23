from __future__ import annotations

from functools import reduce
import math
import operator as op
import platform

from mapbox_earcut import triangulate_float32 as earcut
import numpy as np
from scipy.spatial.transform import Rotation
from tqdm import tqdm as ProgressDisplay

from manimlib.constants import DOWN, OUT, RIGHT, UP
from manimlib.constants import PI, TAU
from manimlib.utils.iterables import adjacent_pairs
from manimlib.utils.simple_functions import clip

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Sequence, List, Tuple
    from manimlib.typing import Vect2, Vect3, Vect4, VectN, Matrix3x3, Vect3Array, Vect2Array


def cross(v1: Vect3 | List[float], v2: Vect3 | List[float]) -> Vect3:
    return np.array([
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ])


def get_norm(vect: VectN | List[float]) -> float:
    return sum((x**2 for x in vect))**0.5


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
    vector: Vect3,
    angle: float,
    axis: Vect3 = OUT
) -> Vect3:
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
    if np.isclose(v1, v2).all():
        return np.identity(3)
    axis = np.cross(v1, v2)
    if np.isclose(axis, [0, 0, 0]).all():
        # v1 and v2 align
        axis = np.cross(v1, RIGHT)
    if np.isclose(axis, [0, 0, 0]).all():
        # v1 and v2 _and_ RIGHT all align
        axis = np.cross(v1, UP)
    return rotation_matrix(
        angle=angle_between_vectors(v1, v2),
        axis=np.cross(v1, v2)
    )


def z_to_vector(vector: Vect3) -> Matrix3x3:
    return rotation_between_vectors(OUT, vector)


def angle_of_vector(vector: Vect2 | Vect3) -> float:
    """
    Returns polar coordinate theta when vector is project on xy plane
    """
    return np.angle(complex(*vector[:2]))


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
    buffed_norms = np.repeat(norms, array.shape[axis]).reshape(array.shape)
    return array / buffed_norms


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
    p0: Vect3,
    v0: Vect3,
    p1: Vect3,
    v1: Vect3,
    threshold: float = 1e-5
) -> Vect3:
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
    result = p0 + ratio * v0
    if m == 1:
        return result[0]
    return result


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


def get_winding_number(points: Sequence[Vect2 | Vect3]) -> float:
    total_angle = 0
    for p1, p2 in adjacent_pairs(points):
        d_angle = angle_of_vector(p2) - angle_of_vector(p1)
        d_angle = ((d_angle + PI) % TAU) - PI
        total_angle += d_angle
    return total_angle / TAU


##

def cross2d(a: Vect2, b: Vect2) -> Vect2:
    if len(a.shape) == 2:
        return a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
    else:
        return a[0] * b[1] - b[0] * a[1]


def tri_area(
    a: Vect2,
    b: Vect2,
    c: Vect2
) -> float:
    return 0.5 * abs(
        a[0] * (b[1] - c[1]) +
        b[0] * (c[1] - a[1]) +
        c[0] * (a[1] - b[1])
    )


def is_inside_triangle(
    p: Vect2,
    a: Vect2,
    b: Vect2,
    c: Vect2
) -> bool:
    """
    Test if point p is inside triangle abc
    """
    crosses = np.array([
        cross2d(p - a, b - p),
        cross2d(p - b, c - p),
        cross2d(p - c, a - p),
    ])
    return bool(np.all(crosses > 0) or np.all(crosses < 0))


def norm_squared(v: VectN | List[float]) -> float:
    return sum(x * x for x in v)


# TODO, fails for polygons drawn over themselves
def earclip_triangulation(verts: Vect3Array | Vect2Array, ring_ends: list[int]) -> list[int]:
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
    epsilon = 1e-6

    def is_in(point, ring_id):
        return abs(abs(get_winding_number([i - point for i in verts[rings[ring_id]]])) - 1) < epsilon

    def ring_area(ring_id):
        ring = rings[ring_id]
        s = 0
        for i, j in zip(ring[1:], ring):
            s += cross2d(verts[i], verts[j])
        return abs(s) / 2

    # Points at the same position may cause problems
    for i in rings:
        verts[i[0]] += (verts[i[1]] - verts[i[0]]) * epsilon
        verts[i[-1]] += (verts[i[-2]] - verts[i[-1]]) * epsilon

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
    ringenum = ProgressDisplay(
        enumerate(rings_sorted),
        total=len(rings),
        leave=False,
        ascii=True if platform.system() == 'Windows' else None,
        dynamic_ncols=True,
        desc="SVG Triangulation",
        delay=3,
    )
    for idx, i in ringenum:
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
