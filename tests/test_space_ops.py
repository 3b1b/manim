import numpy as np

from manimlib.constants import OUT
from manimlib.utils.space_ops import rotate_vector


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
