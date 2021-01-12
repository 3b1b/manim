import pytest
from manim import config, X_AXIS, Y_AXIS, Z_AXIS, PI
from manim.utils.unit import Pixels, Degrees, Munits, Percent
import numpy as np


def test_units():
    # make sure we are using the right frame geometry
    assert config.pixel_width == 1920
    assert np.isclose(config.frame_height, 8.0)

    # Munits should be equivalent to the internal logical units
    assert np.isclose(8.0 * Munits, config.frame_height)

    # Pixels should convert from pixels to Munits
    assert np.isclose(1920 * Pixels, config.frame_width)

    # Percent should give the fractional length of the frame
    assert np.isclose(50 * Percent(X_AXIS), config.frame_width / 2)
    assert np.isclose(50 * Percent(Y_AXIS), config.frame_height / 2)

    # The length of the Z axis is not defined
    with pytest.raises(NotImplementedError):
        Percent(Z_AXIS)

    # Degrees should convert from degrees to radians
    assert np.isclose(180 * Degrees, PI)
