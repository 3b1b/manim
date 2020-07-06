import subprocess
import os
from shutil import rmtree
import pytest


def capture(command):
    proc = subprocess.Popen(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_help(python_version):
    command = [python_version, "-m", "manim", "--help"]
    out, err, exitcode = capture(command)
    assert exitcode == 0, f"Manim has been installed incorrectly. Please refer to the troubleshooting section on the wiki. Error:\n{err}"


@pytest.mark.skip_end_to_end
def test_basicScene(python_version):
    """ Simulate SquareToCircle. The cache will be saved in tests_caches/media_temp (temporary directory). This is mainly intended to test the partial-movies process. """
    path_basic_scene = os.path.join("tests_data", "basic_scenes.py")
    path_output = os.path.join("tests_cache", "media_temp")
    command = [python_version, "-m", "manim", path_basic_scene,
               "SquareToCircle", "-l", "--media_dir", path_output]
    out, err, exitcode = capture(command)
    assert exitcode == 0, err
    assert os.path.exists(os.path.join(
        path_output, "videos", "basic_scenes", "480p15", "SquareToCircle.mp4")), err
    rmtree(path_output)

@pytest.mark.skip_end_to_end
def test_WriteStuff(python_version):
    """This is mainly intended to test the caching process of the tex objects"""
    path_basic_scene = os.path.join("tests_data", "basic_scenes.py")
    path_output = os.path.join("tests_cache", "media_temp")
    command = [python_version, "-m", "manim", path_basic_scene,
               "WriteStuff", "-l", "--media_dir", path_output]
    out, err, exitcode = capture(command)
    assert exitcode == 0, err
    assert os.path.exists(os.path.join(
        path_output, "videos", "basic_scenes", "480p15", "WriteStuff.mp4")), err
    rmtree(path_output)
