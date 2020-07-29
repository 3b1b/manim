import pytest
import os
import shutil

from test_cli import capture
this_folder = os.path.dirname(__file__)

def test_cfg_help(python_version):
    """Test if Manim successfully adds configparsers when a subcommand is invoked."""
    command = f"cd {this_folder} && {python_version} -m manim cfg --help"
    out, err, exitcode = capture(command, use_shell=True)
    assert exitcode == 0, f"The cfg subcommand help is not working as intended.\nError : {err}"

def test_cfg_show(python_version):
    """Test if the `manim cfg show` command works as intended."""
    command = f"cd {this_folder} && {python_version} -m manim cfg show"
    out, err, exitcode = capture(command, use_shell=True)
    assert exitcode == 0
    assert f"{os.path.sep}tests{os.path.sep}".encode("utf-8") in out, err

def test_cfg_export(python_version):
    """Test if the `manim cfg export` command works as intended."""
    command = f"cd {this_folder} && {python_version} -m manim cfg export --dir temp"
    out, err, exitcode = capture(command, use_shell=True)
    assert exitcode == 0, f"The cfg subcommand export is not working as intended.\nError : {err}"
    assert os.path.exists(os.path.join(this_folder,"temp","manim.cfg"))
    with open(os.path.join(this_folder,"temp","manim.cfg"),"r") as writtencfg:
        assert "sound = True" in writtencfg.read(), err
    shutil.rmtree(os.path.join(this_folder,"temp"))

@pytest.mark.usefixtures("reset_config")
def test_cfg_write(python_version):
    """Simulate using the command `manim cfg write`"""
    cfgfilepath = os.path.join(this_folder, "manim.cfg")
    command = f"cd {this_folder} && {python_version} -m manim cfg write --level cwd"

    """As the number of config values that `manim cfg write` can modify increases, so
    must the number of newlines and/or values written in write_cfg_sbcmd_input increase."""
    out, err, exitcode = capture(
        command,
        instream=open(os.path.join(this_folder, "write_cfg_sbcmd_input.txt")),
        use_shell=True
        )
    assert exitcode == 0, f"The cfg subcommand write is not working as intended.\nError : {err}"

    with open(cfgfilepath,"r") as cfgfile:
        assert "sound = False" in cfgfile.read()
