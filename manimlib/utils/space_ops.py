import numpy as np
import math
from mapbox_earcut import triangulate_float32 as earcut

from manimlib.constants import RIGHT
from manimlib.constants import DOWN
from manimlib.constants import OUT
from manimlib.constants import PI
from manimlib.constants import TAU
from manimlib.utils.iterables import adjacent_pairs


def get_norm(vect):
    return sum([x**2 for x in vect])**0.5


# Quaternions
# TODO, implement quaternion type


def quaternion_mult(*quats):
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


def quaternion_from_angle_axis(angle, axis, axis_normalized=False):
    if not axis_normalized:
        axis = normalize(axis)
    return [math.cos(angle / 2), *(math.sin(angle / 2) * axis)]


def angle_axis_from_quaternion(quaternion):
    axis = normalize(
        quaternion[1:],
        fall_back=[1, 0, 0]
    )
    angle = 2 * np.arccos(quaternion[0])
    if angle > TAU / 2:
        angle = TAU - angle
    return angle, axis


def quaternion_conjugate(quaternion):
    result = list(quaternion)
    for i in range(1, len(result)):
        result[i] *= -1
    return result


def rotate_vector(vector, angle, axis=OUT):
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


def thick_diagonal(dim, thickness=2):
    row_indices = np.arange(dim).repeat(dim).reshape((dim, dim))
    col_indices = np.transpose(row_indices)
    return (np.abs(row_indices - col_indices) < thickness).astype('uint8')


def rotation_matrix_transpose_from_quaternion(quat):
    quat_inv = quaternion_conjugate(quat)
    return [
        quaternion_mult(quat, [0, *basis], quat_inv)[1:]
        for basis in [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ]
    ]


def rotation_matrix_from_quaternion(quat):
    return np.transpose(rotation_matrix_transpose_from_quaternion(quat))


def rotation_matrix_transpose(angle, axis):
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


def rotation_matrix(angle, axis):
    """
    Rotation in R^3 about a specified axis of rotation.
    """
    return np.transpose(rotation_matrix_transpose(angle, axis))


def rotation_about_z(angle):
    return [
        [math.cos(angle), -math.sin(angle), 0],
        [math.sin(angle), math.cos(angle), 0],
        [0, 0, 1]
    ]


def z_to_vector(vector):
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


def angle_of_vector(vector):
    """
    Returns polar coordinate theta when vector is project on xy plane
    """
    return np.angle(complex(*vector[:2]))


def angle_between_vectors(v1, v2):
    """
    Returns the angle between two 3D vectors.
    This angle will always be btw 0 and pi
    """
    diff = (angle_of_vector(v2) - angle_of_vector(v1)) % TAU
    return min(diff, TAU - diff)


def project_along_vector(point, vector):
    matrix = np.identity(3) - np.outer(vector, vector)
    return np.dot(point, matrix.T)


def normalize(vect, fall_back=None):
    norm = get_norm(vect)
    if norm > 0:
        return np.array(vect) / norm
    elif fall_back is not None:
        return fall_back
    else:
        return np.zeros(len(vect))


def normalize_along_axis(array, axis, fall_back=None):
    norms = np.sqrt((array * array).sum(axis))
    norms[norms == 0] = 1
    buffed_norms = np.repeat(norms, array.shape[axis]).reshape(array.shape)
    array /= buffed_norms
    return array


def cross(v1, v2):
    return np.array([
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ])


def get_unit_normal(v1, v2, tol=1e-6):
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


def compass_directions(n=4, start_vect=RIGHT):
    angle = TAU / n
    return np.array([
        rotate_vector(start_vect, k * angle)
        for k in range(n)
    ])


def complex_to_R3(complex_num):
    return np.array((complex_num.real, complex_num.imag, 0))


def R3_to_complex(point):
    return complex(*point[:2])


def complex_func_to_R3_func(complex_func):
    return lambda p: complex_to_R3(complex_func(R3_to_complex(p)))


def center_of_mass(points):
    points = [np.array(point).astype("float") for point in points]
    return sum(points) / len(points)


def midpoint(point1, point2):
    return center_of_mass([point1, point2])


def line_intersection(line1, line2):
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


def find_intersection(p0, v0, p1, v1, threshold=1e-5):
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


def get_closest_point_on_line(a, b, p):
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


def get_winding_number(points):
    total_angle = 0
    for p1, p2 in adjacent_pairs(points):
        d_angle = angle_of_vector(p2) - angle_of_vector(p1)
        d_angle = ((d_angle + PI) % TAU) - PI
        total_angle += d_angle
    return total_angle / TAU


##

def cross2d(a, b):
    if len(a.shape) == 2:
        return a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
    else:
        return a[0] * b[1] - b[0] * a[1]


def tri_area(a, b, c):
    return 0.5 * abs(
        a[0] * (b[1] - c[1]) +
        b[0] * (c[1] - a[1]) +
        c[0] * (a[1] - b[1])
    )


def is_inside_triangle(p, a, b, c):
    """
    Test if point p is inside triangle abc
    """
    crosses = np.array([
        cross2d(p - a, b - p),
        cross2d(p - b, c - p),
        cross2d(p - c, a - p),
    ])
    return np.all(crosses > 0) or np.all(crosses < 0)


def norm_squared(v):
    return sum(v * v)


# TODO, fails for polygons drawn over themselves
def earclip_triangulation(verts, rings):
    """
    Returns a list of indices giving a triangulation
    of a polygon, potentially with holes

    - verts is an NxM numpy array of points with M > 2

    - rings is a list of indices indicating where
    the ends of new paths are
    """
    n = len(verts)
    # Establish where loop indices should be connected
    loop_connections = dict()
    end0 = rings[0]
    for end1 in rings[1:]:
        # Find the closet pair of points with the first
        # from the current ring, and the second from the
        # next ring
        filtered_i, filtered_j = [
            list(filter(
                lambda i: i not in loop_connections,
                indices
            ))
            for indices in (range(0, end0), range(end0, end1))
        ]

        i = filtered_i[np.argmin([
            # It's slightly faster to use L-infinity norm
            norm_squared(verts[i] - verts[end0])
            for i in filtered_i
        ])]
        j = filtered_j[np.argmin([
            norm_squared(verts[i] - verts[j])
            for j in filtered_j
        ])]

        # Connect the polygon at these points so that
        # it's treated as a single highly-convex ring
        loop_connections[i] = j
        loop_connections[j] = i
        end0 = end1

    # Setup linked list
    after = []
    end0 = 0
    for end1 in rings:
        after.extend(range(end0 + 1, end1))
        after.append(end0)
        end0 = end1

    # Find an ordering of indices walking around the polygon
    indices = []
    i = 0
    for x in range(n + len(rings) - 1):
        # starting = False
        if i in loop_connections:
            j = loop_connections[i]
            indices.extend([i, j])
            i = after[j]
        else:
            indices.append(i)
            i = after[i]
        if i == 0:
            break

    meta_indices = earcut(verts[indices, :2], [len(indices)])
    return [indices[mi] for mi in meta_indices]
