import inspect
import os

from manimlib.constants import THIS_DIR
from manimlib.constants import VIDEO_DIR


def add_extension_if_not_present(file_name, extension):
    # This could conceivably be smarter about handling existing differing extensions
    if(file_name[-len(extension):] != extension):
        return file_name + extension
    else:
        return file_name


def guarantee_existance(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_scene_output_directory(scene_class):
    return guarantee_existance(os.path.join(VIDEO_DIR, scene_class.__module__))


def get_movie_output_directory(scene_class, camera_config, frame_duration):
    directory = get_scene_output_directory(scene_class)
    sub_dir = "%dp%d" % (
        camera_config["pixel_height"],
        int(1.0 / frame_duration)
    )
    return guarantee_existance(os.path.join(directory, sub_dir))


def get_image_output_directory(scene_class, sub_dir="images"):
    directory = get_scene_output_directory(scene_class)
    return guarantee_existance(os.path.join(directory, sub_dir))
