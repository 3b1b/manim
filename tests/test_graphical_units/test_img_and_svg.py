import sys
from pathlib import Path

import pytest
from manim import *
from ..helpers.path_utils import get_project_root
from ..utils.testing_utils import get_scenes_to_test
from ..utils.GraphicalUnitTester import GraphicalUnitTester

# Tests for the modules image_mobject and svg_mobject


class SVGMobjectTest(Scene):
    def construct(self):
        path = (
            get_project_root()
            / "tests/test_graphical_units/img_svg_resources/weight.svg"
        )
        svg_obj = SVGMobject(str(path))
        self.add(svg_obj)
        self.wait()


class ImageMobjectTest(Scene):
    def construct(self):
        file_path = (
            get_project_root()
            / "tests/test_graphical_units/img_svg_resources/tree_img_640x351.png"
        )
        im1 = ImageMobject(file_path).shift(4 * LEFT + UP)
        im2 = ImageMobject(file_path, scale_to_resolution=1080).shift(
            4 * LEFT + 2 * DOWN
        )
        im3 = ImageMobject(file_path, scale_to_resolution=540).shift(4 * RIGHT)
        self.add(im1, im2, im3)
        self.wait(1)


MODULE_NAME = "img_and_svg"


@pytest.mark.parametrize("scene_to_test", get_scenes_to_test(__name__), indirect=False)
def test_scene(scene_to_test, tmpdir, show_diff):
    GraphicalUnitTester(scene_to_test[1], MODULE_NAME, tmpdir).test(show_diff=show_diff)
