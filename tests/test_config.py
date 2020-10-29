import tempfile
from pathlib import Path
import numpy as np

from manim import config, tempconfig, Scene, Square, WHITE


def test_tempconfig():
    """Test the tempconfig context manager."""
    original = config.copy()

    with tempconfig({"frame_width": 100, "frame_height": 42}):
        # check that config was modified correctly
        assert config["frame_width"] == 100
        assert config["frame_height"] == 42

        # check that no keys are missing and no new keys were added
        assert set(original.keys()) == set(config.keys())

    # check that the keys are still untouched
    assert set(original.keys()) == set(config.keys())

    # check that config is correctly restored
    for k, v in original.items():
        if isinstance(v, np.ndarray):
            assert np.allclose(config[k], v)
        else:
            assert config[k] == v


class MyScene(Scene):
    def construct(self):
        self.add(Square())
        self.wait(1)


def test_transparent():
    """Test the 'transparent' config option."""
    orig_verbosity = config["verbosity"]
    config["verbosity"] = "ERROR"

    with tempconfig({"dry_run": True}):
        scene = MyScene()
        scene.render()
        frame = scene.renderer.get_frame()
    assert np.allclose(frame[0, 0], [0, 0, 0, 255])

    with tempconfig({"transparent": True, "dry_run": True}):
        scene = MyScene()
        scene.render()
        frame = scene.renderer.get_frame()
        assert np.allclose(frame[0, 0], [0, 0, 0, 0])

    config["verbosity"] = orig_verbosity


def test_background_color():
    """Test the 'background_color' config option."""
    with tempconfig({"background_color": WHITE, "verbosity": "ERROR", "dry_run": True}):
        scene = MyScene()
        scene.render()
        frame = scene.renderer.get_frame()
        assert np.allclose(frame[0, 0], [255, 255, 255, 255])


def test_digest_file(tmp_path):
    """Test that a config file can be digested programatically."""
    with tempconfig({}):
        tmp_cfg = tempfile.NamedTemporaryFile("w", dir=tmp_path, delete=False)
        tmp_cfg.write(
            """
            [CLI]
            media_dir = this_is_my_favorite_path
            video_dir = {media_dir}/videos
            """
        )
        tmp_cfg.close()
        config.digest_file(tmp_cfg.name)

        assert config.get_dir("media_dir") == Path("this_is_my_favorite_path")
        assert config.get_dir("video_dir") == Path("this_is_my_favorite_path/videos")


def test_temporary_dry_run():
    """Test that tempconfig correctly restores after setting dry_run."""
    assert config["write_to_movie"]
    assert not config["save_last_frame"]

    with tempconfig({"dry_run": True}):
        assert not config["write_to_movie"]
        assert not config["save_last_frame"]

    assert config["write_to_movie"]
    assert not config["save_last_frame"]
