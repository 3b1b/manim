import os
import glob
import manimlib.constants
import manimlib.config


Addons = []
addons_read = False
movie_paths = []

def load_parser_args(parser):
    # Adds every addon's new cmd flags to the parser
    if addons_read == False:
        read_addons()
    for addon in Addons:
        # TODO: Check if parser_args() exists in the module. If so, add it to the current parser
        if 'parser_args' in dir(addon.Main):
            new_args = addon.Main.parser_args()
            for arg in new_args:
                parser.add_argument(
                    arg['flag'],
                    action=arg['action'],
                    help=arg['help'],
                )
    return parser

def read_addons(remove_last_line=False):
    global Addons
    global addons_read
    global movie_paths
    # Read each Python file in the addons directory
    for filename in glob.glob(os.path.join(manimlib.constants.ADDON_DIR, "*", "*.py")):
        # Open the file and add the module to Addons[]
        with open(filename, 'r') as content_file:
            addon = import_addon(filename)
            Addons.append(addon)
    addons_read = True
    addon_names = []
    for addon in Addons:
        if 'loaded' in dir(addon.Main):
            if addon.Main.loaded():
                try:
                    addon_names.append(addon.Main.addon_info()['name'])
                except:
                    addon_names.append(str(addon.__name__).rsplit(".", 1)[1])
            else:
                Addons.remove(addon)
    if remove_last_line:  print("                             ")
    else: print("\n")
    print_string = "Loaded addons: "
    loaded_addons_string = print_string + '%s' % ', '.join(map(str, addon_names))
    if loaded_addons_string == print_string: print("No addons loaded")
    else: print(print_string + '%s' % ', '.join(map(str, addon_names)) + "\n")
    return Addons

def import_addon(filename):
    import importlib.util
    module_name = filename.replace(os.sep, ".").replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def pass_config_to_addons(config):
    for addon in Addons:
        if 'set_config' in dir(addon.Main):
            addon.Main.set_config(config)

def run_on_rendered():
    for addon in Addons:
        if 'on_rendered' in dir(addon.Main):
            addon.Main.on_rendered()

def run_on_render_ready():
    for addon in Addons:
        if 'on_render_ready' in dir(addon.Main):
            addon.Main.on_render_ready()

def get_video_dir(i = 0):
    video = os.path.abspath(manimlib.constants.VIDEO_DIR)
    return os.path.normpath(video)

def get_exported_video(config):
    return config['file_writer_config']['file_name'] or os.path.join(
        get_video_dir(), config['module'].__name__, config['scene_names'][0], str(config['camera_config']['pixel_height']) + 'p' + str(config['camera_config']['frame_rate']), config['scene_names'][0] + config['file_writer_config']['movie_file_extension']
    )

def log_line(text):
    log_text(text.__str__() + "\n")

def log_text(text):
    with open(os.path.join(manimlib.constants.ADDON_DIR, 'addon_log.txt'), 'a') as the_file:
        the_file.write(text.__str__())

def print_addon_info():
    for addon in Addons:
        info = addon.Main.addon_info()
        print(info['name'] + " v." + info['version'] + " by " + info['author'])
        print("   " + info['desc'])