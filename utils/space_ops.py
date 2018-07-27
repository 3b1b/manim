import numpy as np

from constants import OUT
from constants import RIGHT
from functools import reduce

# Matrix operations


def thick_diagonal(dim, thickness=2):
    row_indices = np.arange(dim).repeat(dim).reshape((dim, dim))
    col_indices = np.transpose(row_indices)
    return (np.abs(row_indices - col_indices) < thickness).astype('uint8')


def rotation_matrix(angle, axis):
    """
    Rotation in R^3 about a specified axis of rotation.
    """
    about_z = rotation_about_z(angle)
    z_to_axis = z_to_vector(axis)
    axis_to_z = np.linalg.inv(z_to_axis)
    return reduce(np.dot, [z_to_axis, about_z, axis_to_z])


def rotation_about_z(angle):
    return [
        [np.cos(angle), -np.sin(angle), 0],
        [np.sin(angle), np.cos(angle), 0],
        [0, 0, 1]
    ]


def z_to_vector(vector):
    """
    Returns some matrix in SO(3) which takes the z-axis to the
    (normalized) vector provided as an argument
    """
    norm = np.linalg.norm(vector)
    if norm == 0:
        return np.identity(3)
    v = np.array(vector) / norm
    phi = np.arccos(v[2])
    if any(v[:2]):
        # projection of vector to unit circle
        axis_proj = v[:2] / np.linalg.norm(v[:2])
        theta = np.arccos(axis_proj[0])
        if axis_proj[1] < 0:
            theta = -theta
    else:
        theta = 0
    phi_down = np.array([
        [np.cos(phi), 0, np.sin(phi)],
        [0, 1, 0],
        [-np.sin(phi), 0, np.cos(phi)]
    ])
    return np.dot(rotation_about_z(theta), phi_down)


def rotate_vector(vector, angle, axis=OUT):
    return np.dot(rotation_matrix(angle, axis), vector)


def angle_between(v1, v2):
    return np.arccos(np.dot(
        v1 / np.linalg.norm(v1),
        v2 / np.linalg.norm(v2)
    ))


def angle_of_vector(vector):
    """
    Returns polar coordinate theta when vector is project on xy plane
    """
    z = complex(*vector[:2])
    if z == 0:
        return 0
    return np.angle(complex(*vector[:2]))


def angle_between_vectors(v1, v2):
    """
    Returns the angle between two 3D vectors.
    This angle will always be btw 0 and TAU/2.
    """
    l1 = np.linalg.norm(v1)
    l2 = np.linalg.norm(v2)
    return np.arccos(np.dot(v1, v2) / (l1 * l2))


def project_along_vector(point, vector):
    matrix = np.identity(3) - np.outer(vector, vector)
    return np.dot(point, matrix.T)

###


def compass_directions(n=4, start_vect=RIGHT):
    angle = 2 * np.pi / n
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
