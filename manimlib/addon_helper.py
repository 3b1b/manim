import os
import glob
import importlib
import manimlib.constants
import manimlib.config


Addons = []
addons_read = False

def load_parser_args(parser):
    # TODO: Write a function that adds every addon's new cmd flags to the parser
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

def read_addons():
    global Addons
    global addons_read
    for filename in glob.glob(os.path.join(manimlib.constants.ADDON_DIR, "*", "*.py")):
        # Read each Python file in the addons directory and add the main class to Addons[]
        with open(filename, 'r') as content_file:
            addon = manimlib.config.get_module(filename)
            Addons.append(addon)
    addons_read = True
    for addon in Addons:
        if 'loaded' in dir(addon.Main):
            addon.Main.loaded()
    return Addons

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

def get_video_dir():
    return os.path.normpath(manimlib.constants.VIDEO_DIR)

def get_exported_video(config):
    return config['file_writer_config']['file_name'] or os.path.join(
        get_video_dir(), config['module'].__name__, config['scene_names'][0], str(config['camera_config']['pixel_height']) + 'p' + str(config['camera_config']['frame_rate']), config['scene_names'][0] + config['file_writer_config']['movie_file_extension']
    )

def log_line(text):
    with open(os.path.join(manimlib.constants.ADDON_DIR, 'addon_log.txt'), 'a') as the_file:
        the_file.write(text.__str__() + '\n')

def log_text(text):
    with open(os.path.join(manimlib.constants.ADDON_DIR, 'addon_log.txt'), 'a') as the_file:
        the_file.write(text)