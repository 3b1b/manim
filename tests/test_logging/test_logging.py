import os
import re

from ..utils.commands import capture
from ..utils.logging_tester import *


@logs_comparison(
    "BasicSceneLoggingTest.txt",
    os.path.join("logs", "basic_scenes_square_to_circle_SquareToCircle.log"),
)
def test_logging_to_file(tmp_path, python_version):
    path_basic_scene = os.path.join(
        "tests", "test_logging", "basic_scenes_square_to_circle.py"
    )
    command = [
        python_version,
        "-m",
        "manim",
        path_basic_scene,
        "SquareToCircle",
        "-ql",
        "--log_to_file",
        "-v",
        "DEBUG",
        "--media_dir",
        str(tmp_path),
    ]
    _, err, exitcode = capture(command)
    assert exitcode == 0, err


@logs_comparison(
    "BasicSceneLoggingTest.txt",
    os.path.join("logs", "basic_scenes_square_to_circle.log"),
)
def test_logging_when_scene_is_not_specified(tmp_path, python_version):
    path_basic_scene = os.path.join(
        "tests", "test_logging", "basic_scenes_square_to_circle.py"
    )
    command = [
        python_version,
        "-m",
        "manim",
        path_basic_scene,
        "-ql",
        "--log_to_file",
        "-v",
        "DEBUG",
        "--media_dir",
        str(tmp_path),
    ]
    _, err, exitcode = capture(command)
    assert exitcode == 0, err
