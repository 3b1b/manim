from manim import __version__
import pkg_resources


def test_version():
    assert __version__ == pkg_resources.get_distribution("manim").version
