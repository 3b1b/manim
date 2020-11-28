import os
import pytest
import subprocess

from ..utils.commands import capture
from ..utils.video_tester import *


@pytest.mark.slow
@video_comparison(
    "SceneWithMultipleWaitCallsWithNFlag.json",
    "videos/simple_scenes/480p15/SceneWithMultipleWaitCalls.mp4",
)
def test_wait_skip(tmp_path, manim_cfg_file, simple_scenes_path):
    # Test for PR #468. Intended to test if wait calls are correctly skipped.
    scene_name = "SceneWithMultipleWaitCalls"
    command = [
        "python",
        "-m",
        "manim",
        simple_scenes_path,
        scene_name,
        "-l",
        "--media_dir",
        str(tmp_path),
        "-n",
        "3",
    ]
    out, err, exit_code = capture(command)
    assert exit_code == 0, err


@pytest.mark.slow
@video_comparison(
    "SceneWithMultiplePlayCallsWithNFlag.json",
    "videos/simple_scenes/480p15/SceneWithMultipleCalls.mp4",
)
def test_play_skip(tmp_path, manim_cfg_file, simple_scenes_path):
    # Intended to test if play calls are correctly skipped.
    scene_name = "SceneWithMultipleCalls"
    command = [
        "python",
        "-m",
        "manim",
        simple_scenes_path,
        scene_name,
        "-l",
        "--media_dir",
        str(tmp_path),
        "-n",
        "3",
    ]
    out, err, exit_code = capture(command)
    assert exit_code == 0, err
