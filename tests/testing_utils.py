import numpy as np
import os
import sys
import inspect
import logging
import pytest

from manim import logger
from manim import dirs
from manim import config


class SceneTester:
    """Class used to test the animations.

    Parameters 
    ----------
    scene_object: : class:`Scene`
        The scene to be tested
    config_scene : :class:`Dict`
        The configuration of the scene
    module_tested: :class:`str`
        The name of the module tested. i.e if we are testing functions of creation.py, the module will be "creation"

    Attributes
    -----------
    path_tests_medias : : class:`str`
        self-explanatory
    path_tests_data : : class:`str`
        self-explanatory
    scene : :class:`Scene`
        The scene tested
    """

    def __init__(self, scene_object, config_scene, module_tested, caching_needed=False):
        # Disable the the logs, (--quiet is broken) TODO
        logging.disable(logging.CRITICAL)
        self.path_tests_media = os.path.join(
            'tests', 'tests_cache', module_tested)
        self.path_tests_data = os.path.join(
            'tests', 'tests_data', module_tested)

        tex_dir, text_dir = None, None
        if caching_needed:
            text_dir = os.path.join(
                self.path_tests_media, scene_object.__name__, 'Text')
            tex_dir = os.path.join(self.path_tests_media,
                                   scene_object.__name__, 'Tex')
        conf_dirs = {'media_dir': None,
                     'video_dir': None,
                     'tex_dir': tex_dir,
                     'text_dir': text_dir,
                     }
        # PROVISIONAL. To change when #98 is merged. TODO
        config.initialize_directories(conf_dirs)
        # By invoking this, the scene is rendered.
        self.scene = scene_object(**config_scene)

    def load_data(self):
        """Load the np.array of the last frame of a pre-rendered scene. If not found, throw FileNotFoundError."""
        with pytest.raises(FileNotFoundError) as e_info:
            data_loaded = np.load(os.path.join(
                self.path_tests_data, "{}.npy".format(str(self.scene))))
            raise FileNotFoundError('test_data not found !')
        assert (str(e_info.value) ==
                'test_data not found !'), f"{str(self.scene).replace('Test', '')} does not seem have a pre-rendered frame for testing, or it has not been found."
        return data_loaded

    def test(self):
        # self.scene.get_frame() gets the last frame of the animation (under the form of an numpy array).
        test_result = np.array_equal(self.scene.get_frame(), self.load_data())
        assert(
            test_result), f"The frames don't match. {str(self.scene).replace('Test', '')} has been modified. Please ignore if it was intended"


def get_scenes_to_test(module_name):
    """Get all Test classes of the module from which it is called."""
    return inspect.getmembers(sys.modules[module_name], lambda m: inspect.isclass(m) and m.__module__ == module_name)


def utils_test_scenes(scenes_to_test, CONFIG, module_name, caching_needed=False):
    for _, scene_tested in scenes_to_test:
        SceneTester(scene_tested, CONFIG, module_name,
                    caching_needed=caching_needed).test()


def set_test_scene(scene_object, module_name):
    """Function used to set up the test data for a new feature. Please refer to the wiki."""

    CONFIG_TEST = {
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

    scene = scene_object(**CONFIG_TEST)
    data = scene.get_frame()
    path = os.path.join("manim", "tests", "tests_data",
                        "{}".format(module_name))
    if not os.path.isdir(path):
        os.makedirs(path)
    np.save(os.path.join(path, str(scene)), data)
    logger.info('Test data saved in ' + path + '\n')
