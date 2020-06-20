from manim import dirs
from manim import config

import pytest
import numpy as np
import os
import sys
import logging


def pytest_addoption(parser):
    parser.addoption("--skip_end_to_end", action="store_true", default=False,
                     help="Will skip all the end-to-end tests. Useful when ffmpeg is not installed, e.g. on Windows jobs.")


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "skip_end_to_end: mark test as end_to_end test")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--skip_end_to_end"):
        return
    else:
        skip_end_to_end = pytest.mark.skip(
            reason="End to end test skipped due to --skip_end_to_end flag")
        for item in items:
            if "skip_end_to_end" in item.keywords:
                item.add_marker(skip_end_to_end)


@pytest.fixture(scope="module")
def python_version():
    return "python3" if sys.platform == "darwin" else "python"


@pytest.fixture
def get_config_test():
    """Function used internally by pytest as a fixture. Return the Configuration for the scenes rendered. The config is the one used when 
        calling the flags -s -l -dry_run
    """
    CONFIG = {
        'camera_config': {
            'frame_rate': 15,
            'pixel_height': 480,
            'pixel_width': 854
        },
        'end_at_animation_number': None,
        'file_writer_config': {
            'file_name': None,
            'input_file_path': 'test.py',
            'movie_file_extension': '.mp4',
            'png_mode': 'RGB',
            'save_as_gif': False,
            'save_last_frame': False,
            'save_pngs': False,
            'write_to_movie': False
        },
        'leave_progress_bars': False,
        'skip_animations': True,
        'start_at_animation_number': None
    }
    return CONFIG
