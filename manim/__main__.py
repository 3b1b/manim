import inspect
import os
import platform
import subprocess as sp
import sys
import re
import traceback
import importlib.util
import types

from .config import file_writer_config,args
from .utils import cfg_file_utils
from .scene.scene import Scene
from .utils.sounds import play_error_sound
from .utils.sounds import play_finish_sound
from . import constants
from .logger import logger,console


def open_file_if_needed(file_writer):
    if file_writer_config["quiet"]:
        curr_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    open_file = any([
        file_writer_config["preview"],
        file_writer_config["show_file_in_finder"]
    ])
    if open_file:
        current_os = platform.system()
        file_paths = []

        if file_writer_config["save_last_frame"]:
            file_paths.append(file_writer.get_image_file_path())
        if file_writer_config["write_to_movie"]:
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

                if file_writer_config["show_file_in_finder"]:
                    commands.append("-R")

                commands.append(file_path)

                # commands.append("-g")
                FNULL = open(os.devnull, 'w')
                sp.call(commands, stdout=FNULL, stderr=sp.STDOUT)
                FNULL.close()

    if file_writer_config["quiet"]:
        sys.stdout.close()
        sys.stdout = curr_stdout


def is_child_scene(obj, module):
    return (inspect.isclass(obj)
            and issubclass(obj, Scene)
            and obj != Scene
            and obj.__module__.startswith(module.__name__))


def prompt_user_for_choice(scene_classes):
    num_to_class = {}
    for count, scene_class in enumerate(scene_classes):
        count += 1  # start with 1 instead of 0
        name = scene_class.__name__
        console.print(f"{count}: {name}", style="logging.level.info")
        num_to_class[count] = scene_class
    try:
        user_input = console.input(f"[log.message] {constants.CHOOSE_NUMBER_MESSAGE} [/log.message]")
        return [num_to_class[int(num_str)]
                for num_str in re.split(r"\s*,\s*", user_input.strip())]
    except KeyError:
        logger.error(constants.INVALID_NUMBER_MESSAGE)
        sys.exit(2)
    except EOFError:
        sys.exit(1)


def get_scenes_to_render(scene_classes):
    if not scene_classes:
        logger.error(constants.NO_SCENE_MESSAGE)
        return []
    if file_writer_config["write_all"]:
        return scene_classes
    result = []
    for scene_name in file_writer_config["scene_names"]:
        found = False
        for scene_class in scene_classes:
            if scene_class.__name__ == scene_name:
                result.append(scene_class)
                found = True
                break
        if not found and (scene_name != ""):
            logger.error(
                constants.SCENE_NOT_FOUND_MESSAGE.format(
                    scene_name
                )
            )
    if result:
        return result
    return [scene_classes[0]] if len(scene_classes) == 1 else prompt_user_for_choice(scene_classes)


def get_scene_classes_from_module(module):
    return [
        member[1]
        for member in inspect.getmembers(
            module,
            lambda x: is_child_scene(x, module)
        )
    ]


def get_module(file_name):
    if file_name == "-":
        module = types.ModuleType("input_scenes")
        logger.info("Enter the animation's code & end with an EOF (CTRL+D on Linux/Unix, CTRL+Z on Windows):")
        code = sys.stdin.read()
        if not code.startswith("from manim import"):
            logger.warn("Didn't find an import statement for Manim. Importing automatically...")
            code="from manim import *\n"+code
        logger.info("Rendering animation from typed code...")
        try:
            exec(code, module.__dict__)
            return module
        except Exception as e:
            logger.error(f"Failed to render scene: {str(e)}")
            sys.exit(2)
    else:
        if os.path.exists(file_name):
            if file_name[-3:] != ".py":
                raise Exception(f"{file_name} is not a valid Manim python script.")
            module_name = file_name[:-3].replace(os.sep, '.').split('.')[-1]
            spec = importlib.util.spec_from_file_location(module_name, file_name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        else:
            raise FileNotFoundError(f'{file_name} not found')


def main():
    if sys.argv[1:][0]=="cfg":
        try:
            subcommand = sys.argv[1:][1]
        except IndexError:
            raise Exception("No subcommand provided. Type manim cfg -h for a list of commands.")

        if subcommand == "write":
            cfg_file_utils.write(args.level)
        elif subcommand == "show":
            cfg_file_utils.show()
        elif subcommand == "export":
            cfg_file_utils.export(args.dir)

    else:
        module = get_module(file_writer_config["input_file"])
        all_scene_classes = get_scene_classes_from_module(module)
        scene_classes_to_render = get_scenes_to_render(all_scene_classes)
        sound_on = file_writer_config["sound"]
        for SceneClass in scene_classes_to_render:
            try:
                # By invoking, this renders the full scene
                scene = SceneClass()
                open_file_if_needed(scene.file_writer)
                if sound_on:
                    play_finish_sound()
            except Exception:
                print("\n\n")
                traceback.print_exc()
                print("\n\n")
                if sound_on:
                    play_error_sound()


if __name__ == "__main__":
    main()
