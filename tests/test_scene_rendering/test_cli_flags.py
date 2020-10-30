import pytest
import numpy as np
from PIL import Image
from pathlib import Path

from ..utils.video_tester import *


@pytest.mark.slow
@video_comparison(
    "SquareToCircleWithDefaultValues.json",
    "videos/simple_scenes/1080p60/SquareToCircle.mp4",
)
def test_basic_scene_with_default_values(tmp_path, manim_cfg_file, simple_scenes_path):
    scene_name = "SquareToCircle"
    command = [
        "python",
        "-m",
        "manim",
        simple_scenes_path,
        scene_name,
        "--media_dir",
        str(tmp_path),
    ]
    out, err, exit_code = capture(command)
    assert exit_code == 0, err


@pytest.mark.slow
@video_comparison(
    "SquareToCircleWithlFlag.json", "videos/simple_scenes/480p15/SquareToCircle.mp4"
)
def test_basic_scene_l_flag(tmp_path, manim_cfg_file, simple_scenes_path):
    scene_name = "SquareToCircle"
    command = [
        "python",
        "-m",
        "manim",
        simple_scenes_path,
        scene_name,
        "-ql",
        "--media_dir",
        str(tmp_path),
    ]
    out, err, exit_code = capture(command)
    assert exit_code == 0, err


@pytest.mark.slow
@video_comparison(
    "SceneWithMultipleCallsWithNFlag.json",
    "videos/simple_scenes/1080p60/SceneWithMultipleCalls.mp4",
)
def test_n_flag(tmp_path, simple_scenes_path):
    scene_name = "SceneWithMultipleCalls"
    command = [
        "python",
        "-m",
        "manim",
        simple_scenes_path,
        scene_name,
        "-n 3,6",
        "--media_dir",
        str(tmp_path),
    ]
    _, err, exit_code = capture(command)
    assert exit_code == 0, err


@pytest.mark.slow
def test_s_flag_no_animations(tmp_path, manim_cfg_file, simple_scenes_path):
    scene_name = "NoAnimations"
    command = [
        "python",
        "-m",
        "manim",
        simple_scenes_path,
        scene_name,
        "-ql",
        "-s",
        "--media_dir",
        str(tmp_path),
    ]
    out, err, exit_code = capture(command)
    assert exit_code == 0, err

    exists = (tmp_path / "videos").exists()
    assert not exists, "running manim with -s flag rendered a video"

    is_empty = not any((tmp_path / "images" / "simple_scenes").iterdir())
    assert not is_empty, "running manim with -s flag did not render an image"


@pytest.mark.slow
def test_s_flag(tmp_path, manim_cfg_file, simple_scenes_path):
    scene_name = "SquareToCircle"
    command = [
        "python",
        "-m",
        "manim",
        simple_scenes_path,
        scene_name,
        "-ql",
        "-s",
        "--media_dir",
        str(tmp_path),
    ]
    out, err, exit_code = capture(command)
    assert exit_code == 0, err

    exists = (tmp_path / "videos").exists()
    assert not exists, "running manim with -s flag rendered a video"

    is_empty = not any((tmp_path / "images" / "simple_scenes").iterdir())
    assert not is_empty, "running manim with -s flag did not render an image"


@pytest.mark.slow
def test_r_flag(tmp_path, manim_cfg_file, simple_scenes_path):
    scene_name = "SquareToCircle"
    command = [
        "python",
        "-m",
        "manim",
        simple_scenes_path,
        scene_name,
        "-ql",
        "-s",
        "--media_dir",
        str(tmp_path),
        "-r",
        "100, 200",
    ]
    out, err, exit_code = capture(command)
    assert exit_code == 0, err

    is_not_empty = any((tmp_path / "images").iterdir())
    assert is_not_empty, "running manim with -s, -r flag did not render a file"

    filename = tmp_path / "images" / "simple_scenes" / "SquareToCircle.png"
    assert np.asarray(Image.open(filename)).shape == (100, 200, 4)


@pytest.mark.slow
def test_custom_folders(tmp_path, manim_cfg_file, simple_scenes_path):
    scene_name = "SquareToCircle"
    command = [
        "python",
        "-m",
        "manim",
        simple_scenes_path,
        scene_name,
        "-ql",
        "-s",
        "--media_dir",
        str(tmp_path),
        "--custom_folders",
    ]
    out, err, exit_code = capture(command)
    assert exit_code == 0, err

    exists = (tmp_path / "videos").exists()
    assert not exists, "--custom_folders produced a 'videos/' dir"

    exists = (tmp_path / "SquareToCircle.png").exists()
    assert exists, "--custom_folders did not produce the output file"
