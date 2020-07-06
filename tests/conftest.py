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
