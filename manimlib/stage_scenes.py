import inspect
import os
import sys

from manimlib.constants import PRODUCTION_QUALITY_CAMERA_CONFIG
from manimlib.constants import PRODUCTION_QUALITY_FRAME_DURATION
from manimlib.extract_scene import get_module
from manimlib.extract_scene import is_scene
from manimlib.utils.output_directory_getters import get_movie_output_directory


def get_sorted_scene_classes(module_name):
    module = get_module(module_name)
    line_to_scene = {}
    for name, scene_class in inspect.getmembers(module, is_scene):
        if inspect.getmodule(scene_class) != module:
            continue
        lines, line_no = inspect.getsourcelines(scene_class)
        line_to_scene[line_no] = scene_class
    return [
        line_to_scene[index]
        for index in sorted(line_to_scene.keys())
    ]


def stage_animations(module_name):
    scene_classes = get_sorted_scene_classes(module_name)
    if len(scene_classes) == 0:
        print("There are no rendered animations from this module")
        return
    animation_dir = get_movie_output_directory(
        scene_classes[0],
        PRODUCTION_QUALITY_CAMERA_CONFIG,
        PRODUCTION_QUALITY_FRAME_DURATION,
    )
    files = os.listdir(animation_dir)
    sorted_files = []
    for scene_class in scene_classes:
        scene_name = scene_class.__name__
        for clip in [f for f in files if f.startswith(scene_name + ".")]:
            sorted_files.append(os.path.join(animation_dir, clip))

    animation_subdir = os.path.dirname(animation_dir)
    count = 0
    while True:
        staged_scenes_dir = os.path.join(
            animation_subdir, "staged_scenes_%d" % count
        )
        if not os.path.exists(staged_scenes_dir):
            os.makedirs(staged_scenes_dir)
            break
        # Otherwise, keep trying new names until
        # there is a free one
        count += 1
    for count, f in enumerate(sorted_files):
        symlink_name = os.path.join(
            staged_scenes_dir,
            "Scene_%03d" % count + f.split(os.sep)[-1]
        )
        os.symlink(f, symlink_name)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("No module given.")
    module_name = sys.argv[1]
    stage_animations(module_name)
