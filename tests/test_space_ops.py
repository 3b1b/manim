import numpy as np
import pytest

from manimlib.constants import OUT
from manimlib.utils.space_ops import find_intersection, rotate_vector


def test_rotate_single_2d_vector():
    result = rotate_vector(np.array([1.0, 0.0]), np.pi / 2)

    np.testing.assert_allclose(result, [0.0, 1.0], atol=1e-8)


def test_rotate_batch_of_2d_vectors():
    vectors = np.array([
        [1.0, 0.0],
        [0.0, 1.0],
    ])

    result = rotate_vector(vectors, np.pi / 2)

    np.testing.assert_allclose(result, [[0.0, 1.0], [-1.0, 0.0]], atol=1e-8)


def test_rotate_single_3d_vector():
    result = rotate_vector(np.array([1.0, 0.0, 0.0]), np.pi / 2, OUT)

    np.testing.assert_allclose(result, [0.0, 1.0, 0.0], atol=1e-8)


def test_rotate_batch_of_3d_vectors():
    vectors = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ])

    result = rotate_vector(vectors, np.pi / 2, OUT)

    np.testing.assert_allclose(
        result,
        [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]],
        atol=1e-8,
    )


@pytest.mark.parametrize("p0,v0,p1,v1,expected", [
    ([1, 0, 0], [1, 1, 0], [0, 1, 1], [1, 0, 0], [2, 1, 0]),
    ([0, 0, 0], [1, 0, 0], [-2, 1, 1], [0, 1, 0], [-2, 0, 0]),
    ([1, 2, 3], [1, 1, 1], [3, 4, 5], [1, -1, 0], [3, 4, 5]),
    ([0, 0, 0], [1, 1, 0], [0, 2, 0], [1, -1, 0], [1, 1, 0]),
    ([1, 2, 3], [1, 0, 0], [0, 1, 4], [2, 0, 0], [1, 2, 3]),
    ([0, 0, 0], [1, 0, 0], [0, 1, 1], [1, 1e-8, 0], [0, 0, 0]),
])
def test_find_intersection(p0, v0, p1, v1, expected):
    result = find_intersection(*(np.array(v, dtype=float) for v in (p0, v0, p1, v1)))

    np.testing.assert_allclose(result, expected, atol=1e-10)


def test_find_intersection_batch_matches_least_squares():
    rng = np.random.default_rng(0)
    p0, v0, p1, v1 = rng.normal(size=(4, 32, 3))
    expected = []
    for a, u, b, v in zip(p0, v0, p1, v1):
        t, _ = np.linalg.lstsq(np.column_stack((u, -v)), b - a, rcond=None)[0]
        expected.append(a + t * u)

    result = find_intersection(p0, v0, p1, v1)

    np.testing.assert_allclose(result, expected, atol=1e-10)
