import pytest

from pathlib import Path

from manim import file_writer_config


@pytest.fixture
def manim_cfg_file():
    return str(Path(__file__).parent / "manim.cfg")


@pytest.fixture
def simple_scenes_path():
    return str(Path(__file__).parent / "simple_scenes.py")
