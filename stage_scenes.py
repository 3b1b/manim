import sys
import inspect
import os
import shutil
import itertools as it
from extract_scene import is_scene, get_module
from constants import MOVIE_DIR, STAGED_SCENES_DIR


def get_sorted_scene_names(module_name):
    module = get_module(module_name)
    line_to_scene = {}
    for name, scene_class in inspect.getmembers(module, is_scene):
        lines, line_no = inspect.getsourcelines(scene_class)
        line_to_scene[line_no] = name
    return [
        line_to_scene[line_no]
        for line_no in sorted(line_to_scene.keys())
    ]



def stage_animaions(module_name):
    scene_names = get_sorted_scene_names(module_name)
    movie_dir = os.path.join(
        MOVIE_DIR, module_name.replace(".py", "")
    )
    files = os.listdir(movie_dir)
    sorted_files = []
    for scene in scene_names:
        for clip in filter(lambda f : f.startswith(scene), files):
            sorted_files.append(
                os.path.join(movie_dir, clip)
            )
    for f in os.listdir(STAGED_SCENES_DIR):
        os.remove(os.path.join(STAGED_SCENES_DIR, f))
    for f, count in zip(sorted_files, it.count()):
        symlink_name = os.path.join(
            STAGED_SCENES_DIR,
            "Scene_%03d"%count + f.split(os.sep)[-1]
        )
        os.symlink(f, symlink_name)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("No module given.")
    module_name = sys.argv[1]
    stage_animaions(module_name)