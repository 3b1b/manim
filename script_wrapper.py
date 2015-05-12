import sys
import getopt
import imp
import itertools as it
from helpers import cammel_case_initials

from constants import *

HELP_MESSAGE = """
   <script name> [-s <scene name or initials> -a <arg_string>]
"""
SCENE_NOT_FOUND_MESSAGE = """
   No scene name or ititials \"%s\" and arg string \"%s\"
"""
MULTIPE_SCENES_FOUND_MESSAGE = """
   Multiple Scene/arg pairs satisfying this
   description, choose from the following list:
"""
CHOOSE_NUMBER_MESSAGE = "Choose a number from above: "
INVALID_NUMBER_MESSAGE = "Invalid number!"

def find_scene_class_and_args(scene_string, args_extension, 
                              scene_classes):
   possible_results = []
   for SceneClass in scene_classes:
      possible_names = map(str.lower, (
         "", 
         SceneClass.__name__, 
         cammel_case_initials(SceneClass.__name__)
      ))
      if scene_string.lower() in possible_names:
         if len(SceneClass.args_list) == 0:
            possible_results.append((SceneClass, ()))
         for args in SceneClass.args_list:
            assert(isinstance(args, tuple))
            this_args_extension = SceneClass.args_to_string(*args)
            if args_extension.lower() in ("", this_args_extension.lower()):
               possible_results.append((SceneClass, args))
   num_matches = len(possible_results)
   if num_matches == 0:
      print SCENE_NOT_FOUND_MESSAGE%(scene_string, args_extension)
      sys.exit(0)
   elif num_matches == 1:
      index = 0
   else:
      print MULTIPE_SCENES_FOUND_MESSAGE
      count = 0
      for SceneClass, args in possible_results:
         print "%d: %s%s"%( 
            count, 
            SceneClass.__name__,
            SceneClass.args_to_string(*args),
         )
         count += 1
      try:
         index = input(CHOOSE_NUMBER_MESSAGE)
         assert(type(index) == int)
         assert(index in range(num_matches))
      except:
         print INVALID_NUMBER_MESSAGE
         sys.exit(0)
   return possible_results[index]

def command_line_create_scene(sys_argv, scene_classes, movie_prefix = ""):
   try:
      opts, args = getopt.getopt(sys_argv, "ho:s:a:l")
   except getopt.GetoptError as err:
      print str(err)
      sys.exit(2)
   scene_string = ""
   args_extension = ""
   display_config = PRODUCTION_QUALITY_DISPLAY_CONFIG
   for opt, arg in opts:
      if opt == '-h':
         print HELP_MESSAGE
         return
      elif opt == '-s':
         scene_string = arg
      elif opt == '-a':
         args_extension = arg
      elif opt == '-l':
         display_config = LOW_QUALITY_DISPLAY_CONFIG
   SceneClass, args = find_scene_class_and_args(
      scene_string,
      args_extension,
      scene_classes
   )
   name = SceneClass.__name__ + SceneClass.args_to_string(*args)
   print "Constructing %s..."%name
   scene = SceneClass(*args, display_config = display_config)
   scene.write_to_movie(movie_prefix + name)










