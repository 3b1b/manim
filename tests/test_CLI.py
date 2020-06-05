import subprocess
import os
from shutil import rmtree


def capture(command):
    proc = subprocess.Popen(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_help():
    command = ["python", "-m", "manim", "--help"]
    out, err, exitcode = capture(command)
    assert exitcode == 0, "Manim is not correcly installed. Please refer to the troubleshooting section on the wiki. Error : {}".format(
        err)


def test_basicScene():
    """ Simulate SquareToCircle. The cache will be saved in tests_caches/media_temp (temporary directory). This is mainly intended to test the partial-movies process. """
    path_basic_scene = os.path.join("tests", "tests_data", "basic_scenes.py")
    path_output = os.path.join("tests", "tests_cache", "media_temp")
    command = ["python", "-m", "manim", path_basic_scene,
               "SquareToCircle", "-l", "--media_dir", path_output]
    out, err, exitcode = capture(command)
    assert exitcode == 0, err
    assert os.path.exists(os.path.join(
        path_output, "videos", "basic_scenes", "480p15", "SquareToCircle.mp4")), err # "Error in the file generation. Please ignore if it was intended"
    rmtree(path_output)


def test_WriteStuff():
    """Simulate WriteStuff. This is mainly intended to test the caching process of the tex objects"""
    path_basic_scene = os.path.join("tests", "tests_data", "basic_scenes.py")
    path_output = os.path.join("tests", "tests_cache", "media_temp")
    command = ["python", "-m", "manim", path_basic_scene,
               "WriteStuff", "-l", "--media_dir", path_output]
    out, err, exitcode = capture(command)
    assert exitcode == 0, err
    assert os.path.exists(os.path.join(
        path_output, "videos", "basic_scenes", "480p15", "WriteStuff.mp4")), err# "Error in the file generation. Please ignore if it was intended"
    rmtree(path_output)
