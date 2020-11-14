import pytest
import numpy as np

from manim.scene.graph_scene import GraphScene


def test_axes_without_shift():
    """Test whether axes are not shifted when origin is in plot range."""
    G = GraphScene(
        x_min=-1, x_max=2, x_axis_label="", y_min=-2, y_max=5, y_axis_label=""
    )
    G.setup_axes()
    assert all(np.isclose(G.graph_origin, G.x_axis.n2p(0)))
    assert all(np.isclose(G.graph_origin, G.y_axis.n2p(0)))


def test_axes_with_x_shift():
    """Test whether x-axis is shifted when 0 is not in plot range of x-axis."""
    G = GraphScene(
        x_min=2, x_max=8, x_axis_label="", y_min=-2, y_max=5, y_axis_label=""
    )
    G.setup_axes()
    assert all(np.isclose(G.graph_origin, G.x_axis.n2p(2)))
    assert all(np.isclose(G.graph_origin, G.y_axis.n2p(0)))


def test_axes_with_y_shift():
    """Test whether y-axis is shifted when 0 is not in plot range of y-axis."""
    G = GraphScene(
        x_min=-1, x_max=2, x_axis_label="", y_min=1, y_max=5, y_axis_label=""
    )
    G.setup_axes()
    assert all(np.isclose(G.graph_origin, G.x_axis.n2p(0)))
    assert all(np.isclose(G.graph_origin, G.y_axis.n2p(1)))


def test_axes_with_xy_shift():
    """Test whether both axes are shifted when origin is not in plot range."""
    G = GraphScene(
        x_min=1, x_max=5, x_axis_label="", y_min=-5, y_max=-1, y_axis_label=""
    )
    G.setup_axes()
    assert all(np.isclose(G.graph_origin, G.x_axis.n2p(1)))
    assert all(np.isclose(G.graph_origin, G.y_axis.n2p(-5)))
