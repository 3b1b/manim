import pytest
import os
import shutil

from test_cli import capture

def test_cfg_help(python_version):
    os.chdir(os.path.dirname(__file__))
    command = [python_version, "-m", "manim", "cfg", "--help"]
    out, err, exitcode = capture(command)
    assert exitcode == 0, f"The cfg subcommand is not working as intended."

def test_cfg_show(python_version):
    command = [python_version, "-m", "manim", "cfg", "show"]
    out, err, exitcode = capture(command)
    assert exitcode == 0
    assert f"{os.path.sep}tests{os.path.sep}".encode("utf-8") in out, err

def test_cfg_export(python_version):
    command = [python_version, "-m", "manim", "cfg", "export", "--dir", "temp"]
    out, err, exitcode = capture(command)
    assert exitcode == 0
    assert os.path.exists(os.path.join("temp","manim.cfg"))
    with open(os.path.join("temp","manim.cfg"),"r") as writtencfg:
        assert "sound = True" in writtencfg.read(), err
    shutil.rmtree("temp")
