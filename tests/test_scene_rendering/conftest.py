import pytest
import os


@pytest.fixture
def manim_cfg_file():
    return os.path.join(os.path.dirname(__file__), "manim.cfg")


@pytest.fixture
def simple_scenes_path():
    return os.path.join(os.path.dirname(__file__), "simple_scenes.py")
