from manim import NumberLine, get_norm


def test_unit_vector():
    """Check if the magnitude of unit vector along
    the NumberLine is equal to its unit_size."""
    axis1 = NumberLine(unit_size=0.4)
    axis2 = NumberLine(width=12, x_min=-2, x_max=5)
    for axis in (axis1, axis2):
        assert get_norm(axis.get_unit_vector()) == axis.unit_size
