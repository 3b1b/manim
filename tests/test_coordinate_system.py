import pytest
import numpy as np
from manim import CoordinateSystem as CS
from manim import Axes, ThreeDAxes, NumberPlane, ComplexPlane
from manim import config, tempconfig, ORIGIN, LEFT


def test_initial_config():
    """Check that all attributes are defined properly from the config."""
    cs = CS()
    assert cs.x_min == -config["frame_x_radius"]
    assert cs.x_max == config["frame_x_radius"]
    assert cs.y_min == -config["frame_y_radius"]
    assert cs.y_max == config["frame_y_radius"]

    ax = Axes()
    assert np.allclose(ax.center_point, ORIGIN)
    assert np.allclose(ax.y_axis_config["label_direction"], LEFT)

    with tempconfig({"frame_x_radius": 100, "frame_y_radius": 200}):
        cs = CS()
        assert cs.x_min == -100
        assert cs.x_max == 100
        assert cs.y_min == -200
        assert cs.y_max == 200


def test_dimension():
    """Check that objects have the correct dimension."""
    assert Axes().dimension == 2
    assert NumberPlane().dimension == 2
    assert ComplexPlane().dimension == 2
    assert ThreeDAxes().dimension == 3


def test_abstract_base_class():
    """Check that CoordinateSystem has some abstract methods."""
    with pytest.raises(Exception):
        CS().get_axes()
