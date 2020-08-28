import pytest
from manim import Camera, tempconfig, config


def test_camera():
    """Test that Camera instances initialize to the correct config."""
    # by default, use the config
    assert Camera().frame_width == config["frame_width"]
    # init args override config
    assert Camera(frame_width=10).frame_width == 10

    # if config changes, reflect those changes
    with tempconfig({"frame_width": 100}):
        assert Camera().frame_width == 100
        # ..init args still override new config
        assert Camera(frame_width=10).frame_width == 10
