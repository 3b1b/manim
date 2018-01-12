#!/usr/bin/env python

import sys
# import getopt
import argparse
import imp
import itertools as it
import inspect
import traceback
import imp
import os

from helpers import *
from scene import Scene
from camera import Camera

HELP_MESSAGE = """
   Usage:
   python extract_scene.py <module> [<scene name>]

   -p preview in low quality
   -s show and save picture of last frame
   -w write result to file [this is default if nothing else is stated]
   -l use low quality
   -m use medium quality
   -a run and save every scene in the script, or all args for the given scene
   -q don't print progress
   -f when writing to a movie file, export the frames in png sequence
   -t use transperency when exporting images
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
         "file", help = "path to file holding the python code for the scene"
      )
      parser.add_argument(
         "scene_name", help = "Name of the Scene class you want to see"
      )
      optional_args = [
         ("-p", "--preview"),
         ("-w", "--write_to_movie"),
         ("-s", "--show_last_frame"),
         ("-l", "--low_quality"),
         ("-m", "--medium_quality"),
         ("-f", "--save_pngs"),
         ("-t", "--transparent"),
         ("-q", "--quiet"),
         ("-a", "--write_all")
      ]
      for short_arg, long_arg in optional_args:
         parser.add_argument(short_arg, long_arg, action = "store_true")
      parser.add_argument("-o", "--output_name")
      args = parser.parse_args()
   except argparse.ArgumentError as err:
      print(str(err))
      sys.exit(2)
   config = {
      "file"            : args.file,
      "scene_name"      : args.scene_name,
      "camera_config"   : PRODUCTION_QUALITY_CAMERA_CONFIG, #TODO
      "frame_duration"  : PRODUCTION_QUALITY_FRAME_DURATION, #TODO
      "preview"         : args.preview,
      "write_to_movie"  : args.write_to_movie,
      "save_frames"     : args.preview, #Scenes only save frame when previewing
      "show_last_frame" : args.show_last_frame,
      "save_pngs"       : args.save_pngs,
      #If -t is passed in (for transparent), this will be RGBA
      "saved_image_mode": "RGBA" if args.transparent else "RGB",
      "quiet"           : args.quiet or args.write_all,
      "write_all"       : args.write_all,
      "output_name"     : args.output_name,
   }
   if args.low_quality or args.preview:
      config["camera_config"] = LOW_QUALITY_CAMERA_CONFIG
      config["frame_duration"] = LOW_QUALITY_FRAME_DURATION
   elif args.medium_quality:
      config["camera_config"] = MEDIUM_QUALITY_CAMERA_CONFIG
      config["frame_duration"] = MEDIUM_QUALITY_FRAME_DURATION
   else:
      config["camera_config"] = PRODUCTION_QUALITY_CAMERA_CONFIG
      config["frame_duration"] = PRODUCTION_QUALITY_FRAME_DURATION

   #By default, write to file
   actions = ["write_to_movie", "preview", "show_last_frame"]
   if not any([config[key] for key in actions]):
      config["write_to_movie"] = True
   config["skip_animations"] = config["show_last_frame"] and not config["write_to_movie"]

   return config

def handle_scene(scene, **config):
   if config["quiet"]:
      curr_stdout = sys.stdout
      sys.stdout = open(os.devnull, "w")

   if config["preview"]:
      scene.preview()
   if config["show_last_frame"]:
      if not config["write_all"]:
         scene.show_frame()
      scene.save_image(mode = config["saved_image_mode"])

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
      print("%d: %s"%(count, name))
      num_to_name[count] = name
   try:
      user_input = raw_input(CHOOSE_NUMBER_MESSAGE)
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
      return scene_names_to_classes.values()
   if config["scene_name"] in scene_names_to_classes:
      return [scene_names_to_classes[config["scene_name"]] ]
   if config["scene_name"] != "":
      print(SCENE_NOT_FOUND_MESSAGE)
      return []
   if config["write_all"]:
      return scene_names_to_classes.values()
   return prompt_user_for_choice(scene_names_to_classes)

def get_module_windows(file_name):
   module_name = file_name.replace(".py", "")
   last_module = imp.load_module("__init__", *imp.find_module("__init__", ['.']))
   for part in module_name.split(os.sep):
      load_args = imp.find_module(part, [os.path.dirname(last_module.__file__)])
      last_module = imp.load_module(part, *load_args)
   return last_module

def get_module_posix(file_name):
    module_name = file_name.replace(".py", "")
    last_module = imp.load_module(".", *imp.find_module("."))
    for part in module_name.split(os.sep):
        load_args = imp.find_module(part, last_module.__path__)
        last_module = imp.load_module(part, *load_args)
    return last_module

def get_module(file_name):
    if os.name == 'nt':
        return get_module_windows(file_name)
    return get_module_posix(file_name)


def main():
   config = get_configuration()
   module = get_module(config["file"])
   scene_names_to_classes = dict(
      inspect.getmembers(module, is_scene)
   )

   config["output_directory"] = os.path.join(
      ANIMATIONS_DIR,
      config["file"].replace(".py", "")
   )

   scene_kwargs = dict([
      (key, config[key])
      for key in [
         "camera_config",
         "frame_duration",
         "skip_animations",
         "write_to_movie",
         "save_frames",
         "output_directory",
         "save_pngs"
      ]
   ])
   
   scene_kwargs["name"] = config["output_name"]
   if config["save_pngs"]:
      print "We are going to save a PNG sequence as well..."
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
