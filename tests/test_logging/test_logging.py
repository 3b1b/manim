import subprocess
import os
import sys
from shutil import rmtree
import pytest
import re


def capture(command, instream=None):
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=instream
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_logging_to_file(python_version):
    """Test logging Terminal output to a log file.
    As some data will differ with each log (the timestamps, file paths, line nums etc)
    a regex substitution has been employed to replace the strings that may change with
    whitespace.
    """
    path_basic_scene = os.path.join("tests", "tests_data", "basic_scenes.py")
    path_output = os.path.join("tests_cache", "media_temp")
    command = [
        python_version,
        "-m",
        "manim",
        path_basic_scene,
        "SquareToCircle",
        "-l",
        "--log_to_file",
        "--log_dir",
        os.path.join(path_output, "logs"),
        "--media_dir",
        path_output,
    ]
    out, err, exitcode = capture(command)
    log_file_path = os.path.join(path_output, "logs", "SquareToCircle.log")
    assert exitcode == 0, err
    assert os.path.exists(log_file_path), err
    if sys.platform.startswith("win32") or sys.platform.startswith("cygwin"):
        enc = "Windows-1252"
    else:
        enc = "utf-8"
    with open(log_file_path, encoding=enc) as logfile:
        logs = logfile.read()
    # The following regex pattern selects timestamps, file paths and all numbers..
    pattern = r"(\[?\d+:?]?)|(\['[A-Z]?:?[\/\\].*cfg'])|([A-Z]?:?[\/\\].*mp4)"

    logs = re.sub(pattern, lambda m: " " * len((m.group(0))), logs)
    with open(
        os.path.join(os.path.dirname(__file__), "expected.txt"), "r"
    ) as expectedfile:
        expected = re.sub(
            pattern, lambda m: " " * len((m.group(0))), expectedfile.read()
        )
    assert logs == expected, logs
