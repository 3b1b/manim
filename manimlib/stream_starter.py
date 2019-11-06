from time import sleep
import code
import os
import readline
import subprocess

from manimlib.scene.scene import Scene
import manimlib.constants

def start_livestream(to_twitch=False, twitch_key=None):
    class Manim():
        STREAMING_CONFIG = {
            "scene_name": manimlib.constants.LIVE_STREAM_NAME,
            "open_video_upon_completion": False,
            "show_file_in_finder": False,
            # By default, write to file
            "file_writer_config": {
                "write_to_movie": True,
                "save_pngs": False,
                "movie_file_extension": ".mp4",
                "to_twitch": to_twitch,
                "twitch_key": twitch_key,
                "livestreaming": True,
                "output_directory": "livestream"
            },
            "show_last_frame": False,
            # If -t is passed in (for transparent), this will be RGBA
            "saved_image_mode": "RGB",
            "quiet": True,
            "ignore_waits": False,
            "write_all": False,
            "name": manimlib.constants.LIVE_STREAM_NAME,
            "start_at_animation_number": 0,
            "end_at_animation_number": None,
            "skip_animations": False,
            "camera_config": manimlib.constants.HIGH_QUALITY_CAMERA_CONFIG,
        }
        def __new__(cls):
            manimlib.constants.initialize_directories(cls.STREAMING_CONFIG)
            return Scene(**cls.STREAMING_CONFIG)

    if not to_twitch:
        FNULL = open(os.devnull, 'w')
        subprocess.Popen(
            [manimlib.constants.STREAMING_CLIENT, manimlib.constants.STREAMING_URL],
            stdout=FNULL,
            stderr=FNULL)
        sleep(3)

    variables = globals().copy()
    variables.update(locals())
    shell = code.InteractiveConsole(variables)
    shell.push("manim = Manim()")
    shell.push("from manimlib.imports import *")
    shell.interact(banner=manimlib.constants.STREAMING_CONSOLE_BANNER)
