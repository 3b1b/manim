import sys
import getopt
import imp
import itertools as it
from helpers import initials, to_cammel_case

def print_help_message():
   print '<script name> -f <function name or initials>'

def get_scene_and_name(function_string, args_string, 
                       function_tuples):
   possible_func_args = []
   for func, args_list, args_to_string in function_tuples:
      if function_string in ("", func.__name__, initials(func.__name__)):
         for args in args_list:
            if not isinstance(args, tuple):
               args = (args,)
            if not args_to_string:
               args_to_string = lambda x : ""
            this_args_string = args_to_string(args)
            if args_string in ("", this_args_string):
               possible_func_args.append(
                  (func, args, this_args_string)
               )
   if len(possible_func_args) == 0:
      print "No function_string arg_string pair \
             matching \"%s\" and \"%s\""%(function_string, args_string)
      sys.exit(0)
   elif len(possible_func_args) == 1:
      index = 0

   else:
      print "Multiple functions/arg pairs satisfying this " + \
            "description, choose from the following list:"
      count = 0
      for func, args, args_string in possible_func_args:
         print "%d: %s%s"%(
            count, 
            to_cammel_case(func.__name__), 
            args_string
         )
         count += 1
      index = int(raw_input("Choose a number from above: "))
   function, args, args_string = possible_func_args[index]
   scene_name = to_cammel_case(function.__name__) + args_string
   print "Writing %s..."%scene_name
   scene = function(*args)
   return scene, scene_name


def create_scene(sys_argv, function_tuples, movie_prefix = ""):
   try:
      opts, args = getopt.getopt(sys_argv, "ho:vf:v")#TODO, Learn about this
   except getopt.GetoptError as err:
      print str(err)
      sys.exit(2)
   function_string = ""
   args_extension = ""
   for opt, arg in opts:
      if opt == '-h':
         print_help_message()
         return
      elif opt == '-f':
         function_string = arg
      elif opt == "-a":
         args_extension = arg
   scene, name = get_scene_and_name(
      function_string,
      args_extension,
      function_tuples
   )
   print name

