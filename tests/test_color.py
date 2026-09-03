import numpy as np

from manimlib.utils.color import (
    color_to_rgb,
    hex_to_rgb,
    interpolate_color,
    rgb_to_hex,
)
from manimlib.utils.rate_functions import overshoot, running_start, wiggle


def test_rgb_to_hex_clips_to_gamut():
    """An out-of-gamut channel must not be written into the hex string.

    `rgb2hex` formats a negative channel as text, producing something like
    "#132-197F" that `hex_to_rgb` then refuses to read back.
    """
    assert rgb_to_hex(np.array([1.2, -0.1, 0.5])) == rgb_to_hex(np.array([1.0, 0.0, 0.5]))
    np.testing.assert_allclose(
        hex_to_rgb(rgb_to_hex(np.array([1.2, -0.1, 0.5]))),
        [1.0, 0.0, 0.498039],
        atol=1e-5,
    )
    # In-gamut values are untouched.
    assert rgb_to_hex(np.array([1.0, 0.0, 0.5])) == "#FF007F"


def test_interpolate_color_saturates_outside_the_unit_interval():
    """`overshoot`, `running_start` and `wiggle` leave [0, 1] by design.

    The squared interpolation then goes negative, `sqrt` yields nan, and the
    colour reads back white — losing the interpolation entirely.
    """
    for rate_func, t in ((overshoot, 0.8), (running_start, 0.2), (wiggle, 0.75)):
        alpha = rate_func(t)
        rgb = color_to_rgb(interpolate_color("#FF0000", "#0000FF", alpha))
        assert not np.isnan(rgb).any(), f"{rate_func.__name__} produced {rgb}"
        assert (rgb >= 0).all() and (rgb <= 1).all()

    # Past either end it saturates at that endpoint rather than going white.
    np.testing.assert_allclose(color_to_rgb(interpolate_color("#FF0000", "#0000FF", 1.5)), [0, 0, 1], atol=1e-6)
    np.testing.assert_allclose(color_to_rgb(interpolate_color("#FF0000", "#0000FF", -0.5)), [1, 0, 0], atol=1e-6)
    # Ordinary interpolation is unchanged.
    np.testing.assert_allclose(
        color_to_rgb(interpolate_color("#FF0000", "#0000FF", 0.5)),
        [np.sqrt(0.5), 0.0, np.sqrt(0.5)],
        atol=1e-6,
    )
