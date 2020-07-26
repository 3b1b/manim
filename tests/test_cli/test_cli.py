import subprocess
import os
from shutil import rmtree
import pytest


def capture(command,instream=None):
    proc = subprocess.Popen(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=instream
                            )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_help(python_version):
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    command = [python_version, "-m", "manim", "--help"]
    out, err, exitcode = capture(command)
    assert exitcode == 0, f"Manim has been installed incorrectly. Please refer to the troubleshooting section on the wiki. Error:\n{err.decode()}"

def test_basicScene(python_version):
    """ Simulate SquareToCircle. The cache will be saved in tests_caches/media_temp (temporary directory). This is mainly intended to test the partial-movies process. """
    path_basic_scene = os.path.join("tests", "tests_data", "basic_scenes.py")
    path_output = os.path.join("tests_cache", "media_temp")
    command = [python_version, "-m", "manim", path_basic_scene,
               "SquareToCircle", "-l", "--media_dir", path_output]
    out, err, exitcode = capture(command)
    assert exitcode == 0, err
    assert os.path.exists(os.path.join(
        path_output, "videos", "basic_scenes", "480p15", "SquareToCircle.mp4")), err
    rmtree(path_output)

def test_WriteStuff(python_version):
    """This is mainly intended to test the caching process of the tex objects"""
    path_basic_scene = os.path.join("tests", "tests_data", "basic_scenes.py")
    path_output = os.path.join("tests_cache", "media_temp")
    command = [python_version, "-m", "manim", path_basic_scene,
               "WriteStuff", "-l", "--media_dir", path_output]
    out, err, exitcode = capture(command)
    assert exitcode == 0, err
    assert os.path.exists(os.path.join(
        path_output, "videos", "basic_scenes", "480p15", "WriteStuff.mp4")), err
    rmtree(path_output)

def test_dash_as_name(python_version):
    """Simulate using - as a filename. Intended to test the feature that allows end users to type manim code on the spot."""
    path_output = os.path.join("tests_cache", "media_temp")
    command = [python_version, "-m", "manim", "-", "-l", "--media_dir", path_output]
    out, err, exitcode = capture(
        command,
        open(os.path.join(os.path.dirname(__file__), "dash_test_script.txt"))
        )
    assert exitcode == 0, err
    assert os.path.exists(os.path.join(
        path_output, "videos", "-", "480p15", "DashAsNameTest.mp4")), err
    rmtree(path_output)
