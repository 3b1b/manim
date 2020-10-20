"""Helpers functions for devs to set up new graphical-units data."""


import os
import tempfile
import numpy as np

import manim
from manim import config, file_writer_config, logger


def set_test_scene(scene_object, module_name):
    """Function used to set up the test data for a new feature. This will basically set up a pre-rendered frame for a scene. This is meant to be used only
    when setting up tests. Please refer to the wiki.

    Parameters
    ----------
    scene_object : :class:`~.Scene`
        The scene with wich we want to set up a new test.
    module_name : :class:`str`
        The name of the module in which the functionnality tested is contained. For example, 'Write' is contained in the module 'creation'. This will be used in the folder architecture
        of '/tests_data'.

    Examples
    --------
    Normal usage::

        set_test_scene(DotTest, "geometry")
    """

    file_writer_config["skip_animations"] = True
    file_writer_config["write_to_movie"] = False
    file_writer_config["disable_caching"] = True
    config["pixel_height"] = 480
    config["pixel_width"] = 854
    config["frame_rate"] = 15

    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "tex"))
        file_writer_config["text_dir"] = os.path.join(tmpdir, "text")
        file_writer_config["tex_dir"] = os.path.join(tmpdir, "tex")
        scene = scene_object()
        scene.render()
        data = scene.renderer.get_frame()

    tests_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path_control_data = os.path.join(
        tests_directory, "control_data", "graphical_units_data"
    )
    print(path_control_data)
    path = os.path.join(path_control_data, module_name)
    if not os.path.isdir(path):
        os.makedirs(path)
    np.save(os.path.join(path, str(scene)), data)
    logger.info(f"Test data for {str(scene)} saved in {path}\n")
