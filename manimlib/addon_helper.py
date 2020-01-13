import os
import importlib
import manimlib.constants
import manimlib.config

# The addon helper provides convenient
# functionality to addons.

movie_paths = []

def get_video_dir(n=0):
    video = os.path.abspath(manimlib.constants.VIDEO_DIR)
    return os.path.normpath(video)

def get_exported_video(config, n=0):
    return config['file_writer_config']['file_name'] or os.path.join(
        get_video_dir(), config['module'].__name__, config['scene_names'][n], str(config['camera_config']['pixel_height']) + 'p' + str(config['camera_config']['frame_rate']), config['scene_names'][n] + config['file_writer_config']['movie_file_extension']
    )

def log_line(text):
    ''' Appends a line to the global addon log. '''
    log_text(text.__str__() + "\n")

def log_text(text):
    ''' Appends text to the global addon log. '''
    with open(os.path.join(manimlib.constants.ADDON_DIR, 'addon_log.txt'), 'a') as the_file:
        the_file.write(text.__str__())
