import os
import numpy as np

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
    return guarantee_existance(os.path.join(
        VIDEO_DIR,
        scene_class.__module__.replace(".", os.path.sep)
    ))


def get_movie_output_directory(scene_class, camera_config, frame_duration):
    directory = get_scene_output_directory(scene_class)
    sub_dir = "%dp%d" % (
        camera_config["pixel_height"],
        int(1.0 / frame_duration)
    )
    return guarantee_existance(os.path.join(directory, sub_dir))


def get_partial_movie_output_directory(scene_class, camera_config, frame_duration):
    directory = get_movie_output_directory(scene_class, camera_config, frame_duration)
    return guarantee_existance(
        os.path.join(directory, scene_class.__name__)
    )


def get_image_output_directory(scene_class, sub_dir="images"):
    directory = get_scene_output_directory(scene_class)
    return guarantee_existance(os.path.join(directory, sub_dir))


def get_sorted_integer_files(directory,
                             min_index=0,
                             max_index=np.inf,
                             remove_non_integer_files=False,
                             remove_indices_greater_than=None):
    indexed_files = []
    for file in os.listdir(directory):
        if '.' in file:
            index_str = file[:file.index('.')]
        else:
            index_str = file

        full_path = os.path.join(directory, file)
        if index_str.isdigit():
            index = int(index_str)
            if remove_indices_greater_than is not None:
                if index > remove_indices_greater_than:
                    os.remove(full_path)
                    continue
            if index >= min_index and index < max_index:
                indexed_files.append((index, file))
        elif remove_non_integer_files:
            os.remove(full_path)
    indexed_files.sort(key=lambda p: p[0])
    return map(lambda p: p[1], indexed_files)
