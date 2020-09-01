from manim import config
import pytest
import numpy as np
import os
import sys
import logging


def pytest_addoption(parser):
    parser.addoption(
        "--skip_slow",
        action="store_true",
        default=False,
        help="Will skip all the slow marked tests. Slow tests are arbitrarly marked as such.",
    )
    parser.addoption(
        "--show_diff",
        action="store_true",
        default=False,
        help="Will show a visual comparison if a graphical unit test fails.",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "skip_end_to_end: mark test as end_to_end test")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--skip_slow"):
        return
    else:
        slow_skip = pytest.mark.skip(
            reason="Slow test skipped due to --disable_slow flag."
        )
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(slow_skip)


@pytest.fixture(scope="session")
def python_version():
    return "python3" if sys.platform == "darwin" else "python"


@pytest.fixture
def reset_cfg_file():
    cfgfilepath = os.path.join(os.path.dirname(__file__), "test_cli", "manim.cfg")
    with open(cfgfilepath) as cfgfile:
        original = cfgfile.read()
    yield
    with open(cfgfilepath, "w") as cfgfile:
        cfgfile.write(original)
