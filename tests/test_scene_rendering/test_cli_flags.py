import os
import pytest
import subprocess
from manim import file_writer_config

from ..utils.commands import capture
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
        "-l",
        "--media_dir",
        str(tmp_path),
    ]
    out, err, exit_code = capture(command)
    assert exit_code == 0, err
