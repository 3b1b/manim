import inspect
import itertools as it
import os
import platform
import subprocess as sp
import sys
import traceback

from manimlib.scene.scene import Scene
from manimlib.utils.sounds import play_error_sound
from manimlib.utils.sounds import play_finish_sound
import manimlib.constants


def open_file_if_needed(file_writer, **config):
    if config["quiet"]:
        curr_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    open_file = any([
        config["open_video_upon_completion"],
        config["show_file_in_finder"]
    ])
    if open_file:
        current_os = platform.system()
        file_paths = []

        if config["file_writer_config"]["save_last_frame"]:
            file_paths.append(file_writer.get_image_file_path())
        if config["file_writer_config"]["write_to_movie"]:
            file_paths.append(file_writer.get_movie_file_path())

        for file_path in file_paths:
            if current_os == "Windows":
                os.startfile(file_path)
            else:
                commands = []
                if current_os == "Linux":
                    commands.append("xdg-open")
                elif current_os.startswith("CYGWIN"):
                    commands.append("cygstart")
                else:  # Assume macOS
                    commands.append("open")

                if config["show_file_in_finder"]:
                    commands.append("-R")

                commands.append(file_path)

                # commands.append("-g")
                FNULL = open(os.devnull, 'w')
                sp.call(commands, stdout=FNULL, stderr=sp.STDOUT)
                FNULL.close()

    if config["quiet"]:
        sys.stdout.close()
        sys.stdout = curr_stdout


def is_child_scene(obj, module):
    if not inspect.isclass(obj):
        return False
    if not issubclass(obj, Scene):
        return False
    if obj == Scene:
        return False
    if not obj.__module__.startswith(module.__name__):
        return False
    return True


def prompt_user_for_choice(scene_classes):
    num_to_class = {}
    for count, scene_class in zip(it.count(1), scene_classes):
        name = scene_class.__name__
        print("%d: %s" % (count, name))
        num_to_class[count] = scene_class
    try:
        user_input = input(manimlib.constants.CHOOSE_NUMBER_MESSAGE)
        return [
            num_to_class[int(num_str)]
            for num_str in user_input.split(",")
        ]
    except KeyError:
        print(manimlib.constants.INVALID_NUMBER_MESSAGE)
        sys.exit(2)
        user_input = input(manimlib.constants.CHOOSE_NUMBER_MESSAGE)
        return [
            num_to_class[int(num_str)]
            for num_str in user_input.split(",")
        ]
    except EOFError:
        sys.exit(1)


def get_scenes_to_render(scene_classes, config):
    if len(scene_classes) == 0:
        print(manimlib.constants.NO_SCENE_MESSAGE)
        return []
    if config["write_all"]:
        return scene_classes
    result = []
    for scene_name in config["scene_names"]:
        found = False
        for scene_class in scene_classes:
            if scene_class.__name__ == scene_name:
                result.append(scene_class)
                found = True
                break
        if not found and (scene_name != ""):
            print(
                manimlib.constants.SCENE_NOT_FOUND_MESSAGE.format(
                    scene_name
                ),
                file=sys.stderr
            )
    if result:
        return result
    return [scene_classes[0]] if len(scene_classes) == 1 else prompt_user_for_choice(scene_classes)


def get_scene_classes_from_module(module):
    if hasattr(module, "SCENES_IN_ORDER"):
        return module.SCENES_IN_ORDER
    else:
        return [
            member[1]
            for member in inspect.getmembers(
                module,
                lambda x: is_child_scene(x, module)
            )
        ]


def main(config):
    module = config["module"]
    all_scene_classes = get_scene_classes_from_module(module)
    scene_classes_to_render = get_scenes_to_render(all_scene_classes, config)

    scene_kwargs = dict([
        (key, config[key])
        for key in [
            "camera_config",
            "file_writer_config",
            "skip_animations",
            "start_at_animation_number",
            "end_at_animation_number",
            "leave_progress_bars",
        ]
    ])

    for SceneClass in scene_classes_to_render:
        try:
            # By invoking, this renders the full scene
            scene = SceneClass(**scene_kwargs)
            open_file_if_needed(scene.file_writer, **config)
            if config["sound"]:
                play_finish_sound()
        except Exception:
            print("\n\n")
            traceback.print_exc()
            print("\n\n")
            if config["sound"]:
                play_error_sound()


if __name__ == "__main__":
    main()
