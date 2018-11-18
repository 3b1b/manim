import inspect
import os

from constants import THIS_DIR
from constants import VIDEO_DIR


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
    file_path = os.path.abspath(inspect.getfile(scene_class))

    file_path = os.path.relpath(file_path, THIS_DIR)
    file_path = file_path.replace(".pyc", "")
    file_path = file_path.replace(".py", "")
    return guarantee_existance(os.path.join(VIDEO_DIR, file_path))


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
