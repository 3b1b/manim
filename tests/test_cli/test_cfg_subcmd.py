import pytest
import os
import shutil

from test_cli import capture

def test_cfg_help(python_version):
    """Test if Manim successfully adds configparsers when a subcommand is invoked."""
    os.chdir(os.path.dirname(__file__))
    command = [python_version, "-m", "manim", "cfg", "--help"]
    out, err, exitcode = capture(command)
    assert exitcode == 0, f"The cfg subcommand is not working as intended."

def test_cfg_show(python_version):
    """Test if the `manim cfg show` command works as intended."""
    command = [python_version, "-m", "manim", "cfg", "show"]
    out, err, exitcode = capture(command)
    assert exitcode == 0
    assert f"{os.path.sep}tests{os.path.sep}".encode("utf-8") in out, err

def test_cfg_export(python_version):
    """Test if the `manim cfg export` command works as intended."""
    command = [python_version, "-m", "manim", "cfg", "export", "--dir", "temp"]
    out, err, exitcode = capture(command)
    assert exitcode == 0
    assert os.path.exists(os.path.join("temp","manim.cfg"))
    with open(os.path.join("temp","manim.cfg"),"r") as writtencfg:
        assert "sound = True" in writtencfg.read(), err
    shutil.rmtree("temp")

def test_cfg_write(python_version):
    """Simulate using the command `manim cfg write`"""
    command = [python_version, "-m", "manim","cfg","write","--level","cwd"]

    """As the number of config values that `manim cfg write` increases, so must the
    number of newlines and/or values written in write_cfg_sbcmd_input increase."""

    out, err, exitcode = capture(
        command,
        open(os.path.join(os.path.dirname(__file__), "write_cfg_sbcmd_input.txt"))
        )
    assert exitcode == 0, err
    with open(os.path.join(os.path.dirname(__file__), "manim.cfg")) as cfgfile:
        assert "sound = False" in cfgfile.read()
