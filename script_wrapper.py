import sys
import getopt
import imp
import itertools as it
import inspect
from helpers import cammel_case_initials
from scene import Scene

from constants import *

HELP_MESSAGE = """
   <script name> [<scene name or initials>] [<arg_string>]
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

def command_line_create_scene(movie_prefix = ""):
   scene_classes = [
        pair[1]
        for pair in inspect.getmembers(
            sys.modules["__main__"], 
            lambda obj : inspect.isclass(obj) and \
                         issubclass(obj, Scene) and \
                         obj != Scene
        )
   ]
   try:
      opts, args = getopt.getopt(sys.argv[1:], 'hlps')
   except getopt.GetoptError as err:
      print str(err)
      sys.exit(2)

   scene_string = ""
   args_extension = ""
   display_config = PRODUCTION_QUALITY_DISPLAY_CONFIG
   action = "write"

   for opt, arg in opts:
      if opt == '-h':
         print HELP_MESSAGE
         return
      elif opt == '-l':
         display_config = LOW_QUALITY_DISPLAY_CONFIG
      elif opt == '-p':
         display_config = LOW_QUALITY_DISPLAY_CONFIG
         action = "preview"
      elif opt == '-s':
         action = "save_image"
   if len(args) > 0:
      scene_string = args[0]
   if len(args) > 1:
      args_extension = args[1]
   SceneClass, args = find_scene_class_and_args(
      scene_string,
      args_extension,
      scene_classes
   )
   name = SceneClass.__name__ + SceneClass.args_to_string(*args)
   print "Constructing %s..."%name
   scene = SceneClass(*args, display_config = display_config)
   if action == "write":
      scene.write_to_movie(os.path.join(movie_prefix, name))
   elif action == "preview":
      scene.preview()
   elif action == "save_image":
      scene.show_frame()
      path = os.path.join(MOVIE_DIR, movie_prefix, "images")
      if not os.path.exists(path):
         os.mkdir(path)
      scene.save_image(path, name)

      










