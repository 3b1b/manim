import unittest

import numpy as np

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


if __name__ == "__main__":
    unittest.main()
