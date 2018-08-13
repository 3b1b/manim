# !/usr/bin/env python2

import sys
import argparse
# import imp
import importlib
import inspect
import itertools as it
import os
import subprocess as sp
import traceback

from constants import *

from scene.scene import Scene
from utils.sounds import play_error_sound
from utils.sounds import play_finish_sound

HELP_MESSAGE = """
   Usage:
   python extract_scene.py <module> [<scene name>]
   -p preview in low quality
   -s show and save picture of last frame
   -w write result to file [this is default if nothing else is stated]
   -o <file_name> write to a different file_name
   -l use low quality
   -m use medium quality
   -a run and save every scene in the script, or all args for the given scene
   -q don't print progress
   -f when writing to a movie file, export the frames in png sequence
   -t use transperency when exporting images
   -n specify the number of the animation to start from
   -r specify a resolution
"""
SCENE_NOT_FOUND_MESSAGE = """
   That scene is not in the script
"""
CHOOSE_NUMBER_MESSAGE = """
Choose number corresponding to desired scene/arguments.
(Use comma separated list for multiple entries)
Choice(s): """
INVALID_NUMBER_MESSAGE = "Fine then, if you don't want to give a valid number I'll just quit"

NO_SCENE_MESSAGE = """
   There are no scenes inside that module
"""


def get_configuration():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "file", help="path to file holding the python code for the scene"
        )
        parser.add_argument(
            "scene_name", help="Name of the Scene class you want to see"
        )
        optional_args = [
            ("-p", "--preview"),
            ("-w", "--write_to_movie"),
            ("-s", "--show_last_frame"),
            ("-l", "--low_quality"),
            ("-m", "--medium_quality"),
            ("-g", "--save_pngs"),
            ("-f", "--show_file_in_finder"),
            ("-t", "--transparent"),
            ("-q", "--quiet"),
            ("-a", "--write_all")
        ]
        for short_arg, long_arg in optional_args:
            parser.add_argument(short_arg, long_arg, action="store_true")
        parser.add_argument("-o", "--output_name")
        parser.add_argument("-n", "--start_at_animation_number")
        parser.add_argument("-r", "--resolution")
        args = parser.parse_args()
        if args.output_name is not None:
            output_name_root, output_name_ext = os.path.splitext(
                args.output_name)
            expected_ext = '.png' if args.show_last_frame else '.mp4'
            if output_name_ext not in ['', expected_ext]:
                print("WARNING: The output will be to (doubly-dotted) %s%s" %
                      output_name_root % expected_ext)
                output_name = args.output_name
            else:
                # If anyone wants .mp4.mp4 and is surprised to only get .mp4, or such... Well, too bad.
                output_name = output_name_root
        else:
            output_name = args.output_name
    except argparse.ArgumentError as err:
        print(str(err))
        sys.exit(2)
    config = {
        "file": args.file,
        "scene_name": args.scene_name,
        "open_video_upon_completion": args.preview,
        "show_file_in_finder": args.show_file_in_finder,
        # By default, write to file
        "write_to_movie": args.write_to_movie or not args.show_last_frame,
        "show_last_frame": args.show_last_frame,
        "save_pngs": args.save_pngs,
        # If -t is passed in (for transparent), this will be RGBA
        "saved_image_mode": "RGBA" if args.transparent else "RGB",
        "movie_file_extension": ".mov" if args.transparent else ".mp4",
        "quiet": args.quiet or args.write_all,
        "ignore_waits": args.preview,
        "write_all": args.write_all,
        "output_name": output_name,
        "start_at_animation_number": args.start_at_animation_number,
        "end_at_animation_number": None,
    }

    # Camera configuration
    config["camera_config"] = {}
    if args.low_quality:
        config["camera_config"].update(LOW_QUALITY_CAMERA_CONFIG)
        config["frame_duration"] = LOW_QUALITY_FRAME_DURATION
    elif args.medium_quality:
        config["camera_config"].update(MEDIUM_QUALITY_CAMERA_CONFIG)
        config["frame_duration"] = MEDIUM_QUALITY_FRAME_DURATION
    else:
        config["camera_config"].update(PRODUCTION_QUALITY_CAMERA_CONFIG)
        config["frame_duration"] = PRODUCTION_QUALITY_FRAME_DURATION

    # If the resolution was passed in via -r
    if args.resolution:
        if "," in args.resolution:
            height_str, width_str = args.resolution.split(",")
            height = int(height_str)
            width = int(width_str)
        else:
            height = int(args.resolution)
            width = int(16 * height / 9)
        config["camera_config"].update({
            "pixel_height": height,
            "pixel_width": width,
        })

    # If rendering a transparent image/move, make sure the
    # scene has a background opacity of 0
    if args.transparent:
        config["camera_config"]["background_opacity"] = 0

    # Arguments related to skipping
    stan = config["start_at_animation_number"]
    if stan is not None:
        if "," in stan:
            start, end = stan.split(",")
            config["start_at_animation_number"] = int(start)
            config["end_at_animation_number"] = int(end)
        else:
            config["start_at_animation_number"] = int(stan)

    config["skip_animations"] = any([
        config["show_last_frame"] and not config["write_to_movie"],
        config["start_at_animation_number"],
    ])
    return config


def handle_scene(scene, **config):
    import platform
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
        commands = ["open"]
        if (platform.system() == "Linux"):
            commands = ["xdg-open"]
        elif (platform.system() == "Windows"):
            commands = ["start"]

        if config["show_file_in_finder"]:
            commands.append("-R")

        if config["show_last_frame"]:
            commands.append(scene.get_image_file_path())
        else:
            commands.append(scene.get_movie_file_path())
        # commands.append("-g")
        FNULL = open(os.devnull, 'w')
        sp.call(commands, stdout=FNULL, stderr=sp.STDOUT)
        FNULL.close()

    if config["quiet"]:
        sys.stdout.close()
        sys.stdout = curr_stdout


def is_scene(obj):
    if not inspect.isclass(obj):
        return False
    if not issubclass(obj, Scene):
        return False
    if obj == Scene:
        return False
    return True


def prompt_user_for_choice(name_to_obj):
    num_to_name = {}
    names = sorted(name_to_obj.keys())
    for count, name in zip(it.count(1), names):
        print("%d: %s" % (count, name))
        num_to_name[count] = name
    try:
        user_input = input(CHOOSE_NUMBER_MESSAGE)
        return [
            name_to_obj[num_to_name[int(num_str)]]
            for num_str in user_input.split(",")
        ]
    except:
        print(INVALID_NUMBER_MESSAGE)
        sys.exit()


def get_scene_classes(scene_names_to_classes, config):
    if len(scene_names_to_classes) == 0:
        print(NO_SCENE_MESSAGE)
        return []
    if len(scene_names_to_classes) == 1:
        return list(scene_names_to_classes.values())
    if config["scene_name"] in scene_names_to_classes:
        return [scene_names_to_classes[config["scene_name"]]]
    if config["scene_name"] != "":
        print(SCENE_NOT_FOUND_MESSAGE)
        return []
    if config["write_all"]:
        return list(scene_names_to_classes.values())
    return prompt_user_for_choice(scene_names_to_classes)


def get_module(file_name):
    module_name = file_name.replace(".py", "").replace(os.sep, ".")
    return importlib.import_module(module_name)


def main():
    config = get_configuration()
    module = get_module(config["file"])
    scene_names_to_classes = dict(inspect.getmembers(module, is_scene))

    # config["output_directory"] = os.path.join(
    #     ANIMATIONS_DIR,
    #     config["file"].replace(".py", "")
    # )

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
            play_finish_sound()
        except:
            print("\n\n")
            traceback.print_exc()
            print("\n\n")
            play_error_sound()


if __name__ == "__main__":
    main()
