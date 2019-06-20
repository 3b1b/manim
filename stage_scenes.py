#!/usr/bin/env python
import inspect
import os
import sys
import importlib

import manimlib.constants as consts
from manimlib.constants import PRODUCTION_QUALITY_CAMERA_CONFIG
from manimlib.config import get_module
from manimlib.extract_scene import is_child_scene


def get_sorted_scene_classes(module_name):
    module = get_module(module_name)
    if hasattr(module, "SCENES_IN_ORDER"):
        return module.SCENES_IN_ORDER
    # Otherwise, deduce from the order in which
    # they're defined in a file
    importlib.import_module(module.__name__)
    line_to_scene = {}
    name_scene_list = inspect.getmembers(
        module,
        lambda obj: is_child_scene(obj, module)
    )
    for name, scene_class in name_scene_list:
        if inspect.getmodule(scene_class).__name__ != module.__name__:
            continue
        lines, line_no = inspect.getsourcelines(scene_class)
        line_to_scene[line_no] = scene_class
    return [
        line_to_scene[index]
        for index in sorted(line_to_scene.keys())
    ]


def stage_scenes(module_name):
    scene_classes = get_sorted_scene_classes(module_name)
    if len(scene_classes) == 0:
        print("There are no rendered animations from this module")
        return
    # output_directory_kwargs = {
    #     "camera_config": PRODUCTION_QUALITY_CAMERA_CONFIG,
    # }
    # TODO, fix this
    animation_dir = os.path.join(
        consts.VIDEO_DIR, "ode", "part3", "1440p60"
    )
    # 
    files = os.listdir(animation_dir)
    sorted_files = []
    for scene_class in scene_classes:
        scene_name = scene_class.__name__
        clips = [f for f in files if f.startswith(scene_name + ".")]
        for clip in clips:
            sorted_files.append(os.path.join(animation_dir, clip))
        # Partial movie file directory
        # movie_dir = get_movie_output_directory(
        #     scene_class, **output_directory_kwargs
        # )
        # if os.path.exists(movie_dir):
        #     for extension in [".mov", ".mp4"]:
        #         int_files = get_sorted_integer_files(
        #             pmf_dir, extension=extension
        #         )
        #         for file in int_files:
        #             sorted_files.append(os.path.join(pmf_dir, file))
        # else:

    # animation_subdir = os.path.dirname(animation_dir)
    count = 0
    while True:
        staged_scenes_dir = os.path.join(
            animation_dir,
            os.pardir,
            "staged_scenes_{}".format(count)
        )
        if not os.path.exists(staged_scenes_dir):
            os.makedirs(staged_scenes_dir)
            break
        # Otherwise, keep trying new names until
        # there is a free one
        count += 1
    for count, f in reversed(list(enumerate(sorted_files))):
        # Going in reversed order means that when finder
        # sorts by date modified, it shows up in the
        # correct order
        symlink_name = os.path.join(
            staged_scenes_dir,
            "Scene_{:03}_{}".format(
                count, f.split(os.sep)[-1]
            )
        )
        os.symlink(f, symlink_name)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("No module given.")
    module_name = sys.argv[1]
    stage_scenes(module_name)
