import sys
import getopt
import imp
import itertools as it
import inspect
import traceback
from helpers import cammel_case_initials
from scene import Scene

from constants import *

HELP_MESSAGE = """
   <script name> [<scene name or initials>] [<arg_string>]
   -p preview in low quality
   -s show and save picture of last frame
   -l use low quality
   -a run and save every scene in the script
   -q don't pring progress
"""
SCENE_NOT_FOUND_MESSAGE = """
   That scene is not in the script
"""
CHOOSE_NUMBER_MESSAGE = "Choose number corresponding to desired scene arguments: "
INVALID_NUMBER_MESSAGE = "Fine then, if you don't want to give a valid number I'll just quit"


def get_configuration(sys_argv):
   try:
      opts, args = getopt.getopt(sys_argv[1:], 'hlpwsqa')
   except getopt.GetoptError as err:
      print str(err)
      sys.exit(2)
   config = {
      "scene_name"     : "",
      "args_extension" : "",
      "display_config" : PRODUCTION_QUALITY_DISPLAY_CONFIG,
      "preview"        : False,
      "write"          : False,
      "save_image"     : False,
      "quiet"          : False,
      "write_all"      : False,
   }
   for opt, arg in opts:
      if opt == '-h':
         print HELP_MESSAGE
         return
      elif opt == '-l':
         config["display_config"] = LOW_QUALITY_DISPLAY_CONFIG
      elif opt == '-p':
         config["display_config"] = LOW_QUALITY_DISPLAY_CONFIG
         config["preview"] = True
      elif opt == '-w':
         config["write"] = True
      elif opt == '-s':
         config["save_image"] = True
      elif opt == '-q':
         config["quiet"] = True
      elif opt == '-a':
         config["write_all"] = True
         config["quiet"] = True
   #By default, write to file
   actions = ["write", "preview", "save_image"]
   if not any([config[key] for key in actions]):
      config["write"] = True

   if len(args) > 0:
      config["scene_name"] = args[0]
   if len(args) > 1:
      config["args_extension"] = " ".join(args[1:])
   return config

def handle_scene(scene, **config):
   name = str(scene)
   if config["quiet"]:
      curr_stdout = sys.stdout
      sys.stdout = open(os.devnull, "w")
   if config["preview"]:
      scene.preview()
   if config["write"]:
      scene.write_to_movie(os.path.join(config["movie_prefix"], name))
   if config["save_image"]:
      if not config["write_all"]:
         scene.show_frame()
      path = os.path.join(MOVIE_DIR, config["movie_prefix"], "images")
      if not os.path.exists(path):
         os.mkdir(path)
      scene.save_image(path, name)

   if config["quiet"]:
      sys.stdout.close()
      sys.stdout = curr_stdout

def prompt_user_for_args(SceneClass):
   num_to_args = {}
   for count, args in zip(it.count(1), SceneClass.args_list):
      print "%d: %s"%(count, SceneClass.args_to_string(*args))
      num_to_args[count] = args
   try:
      return num_to_args[input(CHOOSE_NUMBER_MESSAGE)]
   except:
      print INVALID_NUMBER_MESSAGE
      sys.exit()

def is_scene(obj):
   if not inspect.isclass(obj):
      return False
   if not issubclass(obj, Scene):
      return False
   if obj == Scene:
      return False
   return True

def command_line_create_scene(movie_prefix = ""):
   script = sys.modules["__main__"]
   scene_names_to_classes = dict(inspect.getmembers(script, is_scene))
   config = get_configuration(sys.argv)
   config["movie_prefix"] = movie_prefix
   if config["scene_name"] in scene_names_to_classes:
      scene_classes = [scene_names_to_classes[config["scene_name"]] ]
   elif config["scene_name"] == "" and config["write_all"]:
      scene_classes = scene_names_to_classes.values()
   else:
      print SCENE_NOT_FOUND_MESSAGE
      return

   scene_kwargs = {
      "display_config" : config["display_config"],
      "announce_construction" : True
   }
   for SceneClass in scene_classes:
      args_list = SceneClass.args_list
      preset_extensions = [
         SceneClass.args_to_string(*args)
         for args in args_list
      ]
      if config["write_all"]:
         args_to_run = args_list or [()]
      elif config["args_extension"] in preset_extensions:
         index = preset_extensions.index(config["args_extension"])
         args_to_run = [args_list[index]]
      elif config["args_extension"] == "":
         args_to_run = [prompt_user_for_args(SceneClass)]
      else:
         args_to_run = [SceneClass.string_to_args(config["args_extension"])]
      for args in args_to_run:
         if type(args) is not tuple:
            args = (args,)
         scene_kwargs["construct_args"] = args
         try:
            handle_scene(SceneClass(**scene_kwargs), **config)
         except:
            print "\n\n"
            traceback.print_exc()
            print "\n\n"







