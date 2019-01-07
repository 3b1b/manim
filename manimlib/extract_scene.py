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


def handle_scene(scene, **config):
    if config["quiet"]:
        curr_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    if config["show_last_frame"]:
        scene.save_image(mode=config["saved_image_mode"])
    open_file = any([
        config["show_last_frame"],
        config["open_video_upon_completion"],
        config["show_file_in_finder"]
    ])
    if open_file:
        current_os = platform.system()
        file_path = None

        if config["show_last_frame"]:
            file_path = scene.get_image_file_path()
        else:
            file_path = scene.get_movie_file_path()

        if current_os == "Windows":
            os.startfile(file_path)
        else:
            commands = []

            if (current_os == "Linux"):
                commands.append("xdg-open")
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


def prompt_user_for_choice(name_to_obj):
    num_to_name = {}
    names = sorted(name_to_obj.keys())
    for count, name in zip(it.count(1), names):
        print("%d: %s" % (count, name))
        num_to_name[count] = name
    try:
        user_input = input(manimlib.constants.CHOOSE_NUMBER_MESSAGE)
        return [
            name_to_obj[num_to_name[int(num_str)]]
            for num_str in user_input.split(",")
        ]
    except KeyError:
        print(manimlib.constants.INVALID_NUMBER_MESSAGE)
        sys.exit(2)
        user_input = input(manimlib.constants.CHOOSE_NUMBER_MESSAGE)
        return [
            name_to_obj[num_to_name[int(num_str)]]
            for num_str in user_input.split(",")
        ]
    except EOFError:
        sys.exit(1)


def get_scene_classes(scene_names_to_classes, config):
    if len(scene_names_to_classes) == 0:
        print(manimlib.constants.NO_SCENE_MESSAGE)
        return []
    if config["scene_name"] in scene_names_to_classes:
        return [scene_names_to_classes[config["scene_name"]]]
    if config["scene_name"] != "":
        print(manimlib.constants.SCENE_NOT_FOUND_MESSAGE, file=sys.stderr)
        sys.exit(2)
    if config["write_all"]:
        return list(scene_names_to_classes.values())
    return prompt_user_for_choice(scene_names_to_classes)


def main(config):
    module = config["module"]
    scene_names_to_classes = dict(
        inspect.getmembers(module, lambda x: is_child_scene(x, module)))

    scene_kwargs = dict([
        (key, config[key])
        for key in [
            "camera_config",
            "frame_duration",
            "skip_animations",
            "write_to_movie",
            "save_pngs",
            "movie_file_extension",
            "start_at_animation_number",
            "end_at_animation_number",
        ]
    ])

    scene_kwargs["name"] = config["output_name"]
    if config["save_pngs"]:
        print("We are going to save a PNG sequence as well...")
        scene_kwargs["save_pngs"] = True
        scene_kwargs["pngs_mode"] = config["saved_image_mode"]

    for SceneClass in get_scene_classes(scene_names_to_classes, config):
        try:
            handle_scene(SceneClass(**scene_kwargs), **config)
            if config["sound"]:
                play_finish_sound()
            sys.exit(0)
        except Exception:
            print("\n\n")
            traceback.print_exc()
            print("\n\n")
            if config["sound"]:
                play_error_sound()
            sys.exit(2)


if __name__ == "__main__":
    main()
