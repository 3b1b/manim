from scene.scene import Scene
from time import sleep
import code
import constants
import os
import subprocess


def start_livestream(to_twitch=False):
    class Manim():

        def __new__(cls):
            kwargs = {
                "scene_name": constants.LIVE_STREAM_NAME,
                "open_video_upon_completion": False,
                "show_file_in_finder": False,
                # By default, write to file
                "write_to_movie": True,
                "show_last_frame": False,
                "save_pngs": False,
                # If -t is passed in (for transparent), this will be RGBA
                "saved_image_mode": "RGB",
                "movie_file_extension": ".mp4",
                "quiet": True,
                "ignore_waits": False,
                "write_all": False,
                "name": constants.LIVE_STREAM_NAME,
                "start_at_animation_number": 0,
                "end_at_animation_number": None,
                "skip_animations": False,
                "camera_config": constants.HIGH_QUALITY_CAMERA_CONFIG,
                "frame_duration": constants.MEDIUM_QUALITY_FRAME_DURATION,
                "livestreaming": True,
                "to_twitch": to_twitch,
            }
            return Scene(**kwargs)

    if not to_twitch:
        FNULL = open(os.devnull, 'w')
        subprocess.Popen(
            [constants.STREAMING_CLIENT, constants.STREAMING_URL],
            stdout=FNULL,
            stderr=FNULL)
        sleep(3)

    manim = Manim()
    print("YOUR STREAM IS READY!")
    variables = globals().copy()
    variables.update(locals())
    shell = code.InteractiveConsole(variables)
    shell.push("from big_ol_pile_of_manim_imports import *")
    shell.interact()
