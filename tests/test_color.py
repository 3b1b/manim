import pytest
import numpy as np

from manim import Mobject, VMobject, Camera, Scene, tempconfig, config, WHITE, BLACK


def test_import_color():
    import manim.utils.color as C

    C.WHITE


def test_background_color():
    S = Scene()
    S.camera.background_color = "#ff0000"
    S.renderer.update_frame(S)
    assert np.all(S.renderer.get_frame()[0, 0] == np.array([255, 0, 0, 255]))

    S.camera.background_color = "#436f80"
    S.renderer.update_frame(S)
    assert np.all(S.renderer.get_frame()[0, 0] == np.array([67, 111, 128, 255]))

    S.camera.background_color = "#bbffbb"
    S.camera.background_opacity = 0.5
    S.renderer.update_frame(S)
    assert np.all(S.renderer.get_frame()[0, 0] == np.array([187, 255, 187, 127]))


def test_set_color():
    m = Mobject()
    assert m.color.hex == "#fff"
    m.set_color(BLACK)
    assert m.color.hex == "#000"

    m = VMobject()
    assert m.color.hex == "#fff"
    m.set_color(BLACK)
    assert m.color.hex == "#000"
