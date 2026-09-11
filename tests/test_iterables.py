import numpy as np

from manimlib.utils.iterables import (
    resize_array,
    resize_preserving_order,
    resize_with_interpolation,
)


def test_resize_of_empty_array_keeps_trailing_shape():
    """All three resizers agree on an empty input: zeros of the asked-for length.

    An empty array reaches these through the ordinary mobject paths — a
    PMobject with no points yet, or `set_radii([])` — and each resizer is used
    interchangeably on the same data arrays, so they cannot disagree about it.
    """
    empty = np.zeros((0, 4))

    for resize in (resize_array, resize_preserving_order, resize_with_interpolation):
        result = resize(empty, 3)
        assert result.shape == (3, 4), f"{resize.__name__} returned {result.shape}"
        assert not result.any()


def test_resize_to_zero_length():
    arr = np.arange(12, dtype=float).reshape((4, 3))

    for resize in (resize_array, resize_preserving_order, resize_with_interpolation):
        assert resize(arr, 0).shape == (0, 3), resize.__name__


def test_resize_with_interpolation_still_interpolates():
    arr = np.array([[0.0, 0.0], [1.0, 2.0]])

    np.testing.assert_allclose(
        resize_with_interpolation(arr, 3),
        [[0.0, 0.0], [0.5, 1.0], [1.0, 2.0]],
    )
    np.testing.assert_allclose(resize_with_interpolation(arr, 2), arr)
