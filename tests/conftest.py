from manim import dirs
from manim import config

import pytest
import numpy as np
import os
import sys
import logging


class SceneTester:
    """Class used to test the animations.
    
    Parameters 
    ----------
    scene_object: : class:`Scene`
        The scene to be tested
    config_scene : :class:`Dict`
        The configuration of the scene
    module_tested: :class: `str`
        The name of the module tested. i.e if we are testing functions of creation.py, the module will be "creation"
    
    Attributes
    -----------
    path_tests_medias : : class: `str`
        self-explanatory
    path_tests_data : : class: `str`
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
            text_dir = os.path.join(self.path_tests_media, scene_object.__name__, 'Text')
            tex_dir = os.path.join(self.path_tests_media, scene_object.__name__, 'Tex')
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
                'test_data not found !'), '{} does not seem have a pre-rendered frame for testing.'.format(str(self.scene).replace('Test', ''))
        return data_loaded

    def test(self):
        # self.scene.get_frame() gets the last frame of the animation (under the form of an numpy array).
        test_result = np.array_equal(self.scene.get_frame(), self.load_data())
        assert(test_result), "The frames don't match. {} has been modified. Please ignore if it was intended".format(
            str(self.scene).replace('Test', ''))

def pytest_addoption(parser):
    parser.addoption("--skip_end_to_end", action="store_true", default=False, help = "Will skip all the end-to-end tests. Useful when ffmpeg is not installed.")

def pytest_configure(config):
    config.addinivalue_line("markers", "skip_end_to_end: mark test as end_to_end test")

def pytest_collection_modifyitems(config, items):
    if config.getoption("--skip_end_to_end") == False:
        return
    else: 
        skip_end_to_end = pytest.mark.skip(reason="End to end test skipped due to --skip_end_to_end flag")
        for item in items:
            if "skip_end_to_end" in item.keywords:
                item.add_marker(skip_end_to_end)

@pytest.fixture
def Tester():
    return SceneTester

@pytest.fixture(scope= "module")
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

