import shutil
import textwrap
from pathlib import Path

import pytest

from ..utils.commands import capture

plugin_pyproject_template = textwrap.dedent(
    """
        [tool.poetry]
        name = "{plugin_name}"
        authors = ["ManimCE"]
        version = "0.1.0"
        description = ""

        [tool.poetry.dependencies]
        python = "^3.6"

        [tool.poetry.plugins."manim.plugins"]
        "{plugin_name}" = "{plugin_entrypoint}"

        [build-system]
        requires = ["poetry-core>=1.0.0"]
        build-backend = "poetry.core.masonry.api"
        """
)

plugin_init_template = textwrap.dedent(
    """
    from manim import *
    class {class_name}(VMobject):
        def __init__(self):
            super().__init__()
            dot1 = Dot(fill_color=GREEN).shift(LEFT)
            dot2 = Dot(fill_color=BLUE)
            dot3 = Dot(fill_color=RED).shift(RIGHT)
            self.dotgrid = VGroup(dot1, dot2, dot3)
            self.add(self.dotgrid)

        def update_dot(self):
            self.dotgrid.become(self.dotgrid.shift(UP))
    def {function_name}():
        return [{class_name}]
    """
)

cfg_file_contents = textwrap.dedent(
    """
        [CLI]
        plugins = test_plugin
    """
)


def simple_scenes_path():
    return str(Path(__file__).parent / "simple_scenes.py")


def cfg_file_create(cfg_file_contents, path):
    file_loc = (path / "manim.cfg").absolute()
    with open(file_loc, "w") as f:
        f.write(cfg_file_contents)
    return file_loc


def test_plugin_warning(tmp_path, python_version):
    cfg_file_contents = textwrap.dedent(
        """
        [CLI]
        plugins = DNEPlugin
    """
    )
    cfg_file = cfg_file_create(cfg_file_contents, tmp_path)
    scene_name = "SquareToCircle"
    command = [
        python_version,
        "-m",
        "manim",
        simple_scenes_path(),
        scene_name,
        "-ql",
        "--media_dir",
        str(cfg_file.parent),
        "--config_file",
        str(cfg_file),
    ]
    out, err, exit_code = capture(command, cwd=str(cfg_file.parent))
    assert exit_code == 0, err
    assert "Missing Plugins" in out, "Missing Plugins isn't in Output."


@pytest.fixture
def function_like_plugin(tmp_path, python_version):
    plugin_name = "test_plugin"
    entry_point = f"{plugin_name}.__init__:import_all"
    plugin_dir = tmp_path / "function_entrypoint"
    module_dir = plugin_dir / plugin_name
    module_dir.mkdir(parents=True)
    with open(module_dir / "__init__.py", "w") as f:
        f.write(
            plugin_init_template.format(
                class_name="FunctionLike",
                function_name="import_all",
            )
        )
    with open(plugin_dir / "pyproject.toml", "w") as f:
        f.write(
            plugin_pyproject_template.format(
                plugin_name=plugin_name,
                plugin_entrypoint=entry_point,
            )
        )
    command = [
        python_version,
        "-m",
        "pip",
        "install",
        str(plugin_dir.absolute()),
    ]
    out, err, exit_code = capture(command, cwd=str(plugin_dir))
    print(out)
    assert exit_code == 0, err
    yield module_dir
    shutil.rmtree(plugin_dir)
    command = [python_version, "-m", "pip", "uninstall", plugin_name, "-y"]
    out, err, exit_code = capture(command)
    print(out)
    assert exit_code == 0, err


@pytest.mark.slow
def test_plugin_function_like(tmp_path, function_like_plugin, python_version):
    cfg_file = cfg_file_create(cfg_file_contents, tmp_path)
    scene_name = "FunctionLikeTest"
    command = [
        python_version,
        "-m",
        "manim",
        simple_scenes_path(),
        scene_name,
        "-ql",
        "--media_dir",
        str(cfg_file.parent),
        "--config_file",
        str(cfg_file),
    ]
    out, err, exit_code = capture(command, cwd=str(cfg_file.parent))
    print(out)
    assert exit_code == 0, err


@pytest.fixture
def module_no_all_plugin(tmp_path, python_version):
    plugin_name = "test_plugin"
    entry_point = f"{plugin_name}"
    plugin_dir = tmp_path / "module_entrypoint_no_all"
    module_dir = plugin_dir / plugin_name
    module_dir.mkdir(parents=True)
    with open(module_dir / "__init__.py", "w") as f:
        f.write(
            plugin_init_template.format(
                class_name="NoAll",
                function_name="import_all",
            )
        )
    with open(plugin_dir / "pyproject.toml", "w") as f:
        f.write(
            plugin_pyproject_template.format(
                plugin_name=plugin_name,
                plugin_entrypoint=entry_point,
            )
        )
    command = [
        python_version,
        "-m",
        "pip",
        "install",
        str(plugin_dir.absolute()),
    ]
    out, err, exit_code = capture(command, cwd=str(plugin_dir))
    print(out)
    assert exit_code == 0, err
    yield module_dir
    shutil.rmtree(plugin_dir)
    command = [python_version, "-m", "pip", "uninstall", plugin_name, "-y"]
    out, err, exit_code = capture(command)
    print(out)
    assert exit_code == 0, err


@pytest.mark.slow
def test_plugin_no_all(tmp_path, module_no_all_plugin, python_version):
    cfg_file = cfg_file_create(cfg_file_contents, tmp_path)
    scene_name = "NoAllTest"
    command = [
        python_version,
        "-m",
        "manim",
        simple_scenes_path(),
        scene_name,
        "-ql",
        "--media_dir",
        str(cfg_file.parent),
        "--config_file",
        str(cfg_file),
    ]
    out, err, exit_code = capture(command, cwd=str(cfg_file.parent))
    print(out)
    print(err)
    assert exit_code == 0, err


@pytest.fixture
def module_with_all_plugin(tmp_path, python_version):
    plugin_name = "test_plugin"
    entry_point = f"{plugin_name}"
    plugin_dir = tmp_path / "module_entrypoint_with_all"
    module_dir = plugin_dir / plugin_name
    module_dir.mkdir(parents=True)
    with open(module_dir / "__init__.py", "w") as f:
        f.write("__all__=['WithAll']\n")
        f.write(
            plugin_init_template.format(
                class_name="WithAll",
                function_name="import_all",
            )
        )
    with open(plugin_dir / "pyproject.toml", "w") as f:
        f.write(
            plugin_pyproject_template.format(
                plugin_name=plugin_name,
                plugin_entrypoint=entry_point,
            )
        )
    command = [
        python_version,
        "-m",
        "pip",
        "install",
        str(plugin_dir.absolute()),
    ]
    out, err, exit_code = capture(command, cwd=str(plugin_dir))
    print(out)
    assert exit_code == 0, err
    yield module_dir
    shutil.rmtree(plugin_dir)
    command = [python_version, "-m", "pip", "uninstall", plugin_name, "-y"]
    out, err, exit_code = capture(command)
    print(out)
    assert exit_code == 0, err


@pytest.mark.slow
def test_plugin_with_all(tmp_path, module_with_all_plugin, python_version):
    cfg_file = cfg_file_create(cfg_file_contents, tmp_path)
    scene_name = "WithAllTest"
    command = [
        python_version,
        "-m",
        "manim",
        simple_scenes_path(),
        scene_name,
        "-ql",
        "--media_dir",
        str(cfg_file.parent),
        "--config_file",
        str(cfg_file),
    ]
    out, err, exit_code = capture(command, cwd=str(cfg_file.parent))
    print(out)
    print(err)
    assert exit_code == 0, err
