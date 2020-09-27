import pytest
import numpy as np
from manim import Sector, ORIGIN


def test_get_arc_center():
    assert np.all(Sector().get_arc_center() == ORIGIN)
