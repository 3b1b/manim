import subprocess
import os
import sys
import pytest
import re


def capture(command, instream=None, use_shell=False):
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=instream,
        shell=use_shell,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_logging_to_file(tmp_path, python_version):
    """Test logging Terminal output to a log file.
    As some data will differ with each log (the timestamps, file paths, line nums etc)
    a regex substitution has been employed to replace the strings that may change with
    whitespace.
    """
    path_basic_scene = os.path.join("tests", "test_logging", "basic_scenes.py")
    path_output = os.path.join(tmp_path, "media_temp")
    os.makedirs(tmp_path, exist_ok=True)
    command = " ".join(
        [
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
            "-v",
            "DEBUG",
            "--config_file",
            os.path.join("tests", "test_logging", "testloggingconfig.cfg"),
        ]
    )
    out, err, exitcode = capture(command, use_shell=True)
    log_file_path = os.path.join(path_output, "logs", "SquareToCircle.log")
    assert exitcode == 0, err.decode()
    assert os.path.exists(log_file_path), err.decode()
    if sys.platform.startswith("win32") or sys.platform.startswith("cygwin"):
        enc = "Windows-1252"
    else:
        enc = "utf-8"
    with open(log_file_path, encoding=enc) as logfile:
        logs = logfile.read()
    # The following regex pattern selects file paths and all numbers.
    pattern = r"(\['[A-Z]?:?[\/\\].*cfg'])|([A-Z]?:?[\/\\].*mp4)|(\d+)"

    logs = re.sub(pattern, lambda m: " " * len((m.group(0))), logs)
    with open(
        os.path.join(os.path.dirname(__file__), "expected.txt"), "r"
    ) as expectedfile:
        expected = re.sub(
            pattern, lambda m: " " * len((m.group(0))), expectedfile.read()
        )
    assert logs == expected, logs
