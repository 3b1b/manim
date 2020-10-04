import pytest
from manim import Camera, tempconfig, config


def test_import_color():
    import manim.utils.color as C

    C.WHITE
