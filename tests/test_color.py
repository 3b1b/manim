import pytest

from manimlib.constants import BLUE, GREEN, RED
from manimlib.utils.color import color_gradient


def test_single_reference_color_repeats_instead_of_raising():
    # floors[-1] became -1 while the earlier entries stayed 0, so
    # reference_colors[i + 1] indexed past the end and raised IndexError.
    assert [str(c) for c in color_gradient([RED], 3)] == [str(RED).lower()] * 3


def test_single_reference_color_accepts_a_tuple():
    assert len(color_gradient((RED,), 5)) == 5


def test_one_sample_takes_the_first_reference_color():
    # linspace(0, n - 1, 1) samples alpha 0, i.e. the first color. Forcing the
    # end edge case unconditionally returned the last one.
    assert [str(c) for c in color_gradient([RED, GREEN, BLUE], 1)] == [str(RED).lower()]


def test_multi_sample_gradient_still_spans_both_ends():
    result = [str(c) for c in color_gradient([RED, BLUE], 3)]

    assert result[0] == str(RED).lower()
    assert result[-1] == str(BLUE).lower()
    assert len(result) == 3


@pytest.mark.parametrize("colors", [[RED], [RED, BLUE], [RED, GREEN, BLUE]])
def test_zero_length_output_is_empty(colors):
    assert color_gradient(colors, 0) == []
