import pytest
from manim import CairoRenderer, Camera, tempconfig, config


def test_renderer():
    """Test that CairoRenderer instances initialize to the correct config."""
    # by default, use the config
    assert (
        CairoRenderer(Camera).video_quality_config["frame_width"]
        == config["frame_width"]
    )
    # init args override config
    assert (
        CairoRenderer(Camera, frame_width=10).video_quality_config["frame_width"] == 10
    )

    # if config changes, reflect those changes
    with tempconfig({"frame_width": 100}):
        assert CairoRenderer(Camera).video_quality_config["frame_width"] == 100
        # ..init args still override new config
        assert (
            CairoRenderer(Camera, frame_width=10).video_quality_config["frame_width"]
            == 10
        )
