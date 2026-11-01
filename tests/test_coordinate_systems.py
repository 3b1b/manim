import unittest

import numpy as np

from manimlib.mobject.coordinate_systems import Axes
from manimlib.mobject.coordinate_systems import CoordinateSystem
from manimlib.utils.simple_functions import binary_search


class StubCoordinateSystem(CoordinateSystem):
    def coords_to_point(self, *coords):
        return np.array([coords[0], coords[1], 0.0])

    def point_to_coords(self, point):
        return tuple(point[:2])

    def get_axes(self):
        return []

    def get_all_ranges(self):
        return []


class LineGraph:
    def quick_point_from_proportion(self, alpha):
        return np.array([2.0 + 4.0 * alpha, 3.0, 0.0])


class CoordinateSystemTests(unittest.TestCase):
    def test_binary_search_returns_input_at_endpoints(self):
        def function(value):
            return 2.0 + 4.0 * value

        self.assertEqual(binary_search(function, 2.0, 0.0, 1.0), 0.0)
        self.assertEqual(binary_search(function, 6.0, 0.0, 1.0), 1.0)

    def test_input_to_graph_point_searches_curve_proportion(self):
        axes = StubCoordinateSystem(x_range=(2.0, 6.0, 1.0), y_range=(0.0, 5.0, 1.0))
        graph = LineGraph()

        np.testing.assert_allclose(
            axes.input_to_graph_point(2.0, graph), [2.0, 3.0, 0.0]
        )
        np.testing.assert_allclose(
            axes.input_to_graph_point(4.0, graph), [4.0, 3.0, 0.0]
        )
        np.testing.assert_allclose(
            axes.input_to_graph_point(6.0, graph), [6.0, 3.0, 0.0]
        )

    def test_bound_graph_keeps_its_points_across_updates(self):
        axes = Axes(x_range=(-4.0, 4.0, 1.0), y_range=(-2.0, 2.0, 1.0))
        graph = axes.get_graph(np.sign)
        axes.bind_graph_to_func(graph, np.sign, get_discontinuities=lambda: [0.0])
        points = graph.get_points().copy()

        for _ in range(3):
            graph.update(1 / 30)
            np.testing.assert_allclose(graph.get_points(), points)

    def test_bound_graph_with_discontinuities_spans_its_x_range(self):
        axes = Axes(x_range=(-4.0, 4.0, 1.0), y_range=(-2.0, 2.0, 1.0))
        graph = axes.get_graph(np.sign)
        axes.bind_graph_to_func(graph, np.sign, get_discontinuities=lambda: [0.0])

        xs, ys = axes.p2c(graph.get_anchors())
        np.testing.assert_allclose([xs.min(), xs.max()], [-4.0, 4.0], atol=1e-5)
        # The jump is drawn between samples just either side of x = 0
        jump = np.argmax(np.abs(np.diff(ys)))
        self.assertLess(xs[jump + 1] - xs[jump], 1e-5)

    def test_bound_graph_does_not_stretch_to_discontinuities_outside_it(self):
        axes = Axes(x_range=(-4.0, 4.0, 1.0), y_range=(-2.0, 2.0, 1.0))
        graph = axes.get_graph(np.sin)
        axes.bind_graph_to_func(graph, np.sin, get_discontinuities=lambda: [-6.0, 6.0])

        xs = axes.x_axis.p2n(graph.get_anchors())
        np.testing.assert_allclose([xs.min(), xs.max()], [-4.0, 4.0], atol=1e-5)

    def test_bound_graph_keeps_its_point_count_as_discontinuities_move(self):
        axes = Axes(x_range=(-4.0, 4.0, 1.0), y_range=(-2.0, 2.0, 1.0))
        jumps = [0.0]
        graph = axes.get_graph(np.sign)
        axes.bind_graph_to_func(graph, np.sign, get_discontinuities=lambda: jumps)
        num_points = graph.get_num_points()

        for jump in [3.0, 6.0, -6.0, -1.0]:
            jumps[0] = jump
            graph.update()
            self.assertEqual(graph.get_num_points(), num_points)


if __name__ == "__main__":
    unittest.main()
