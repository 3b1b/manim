#!/usr/bin/python3

from constants import *
from scene.scene import Scene


class Manim():

    def __new__(cls):
        kwargs = {
            "file": "example_file.py",
            "scene_name": "LiveStream",
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
            "name": "LiveStream",
            "start_at_animation_number": 0,
            "end_at_animation_number": None,
            "skip_animations": False,
            "camera_config": HIGH_QUALITY_CAMERA_CONFIG,
            "frame_duration": PRODUCTION_QUALITY_FRAME_DURATION,
            "is_live_streaming": True,
        }
        return Scene(**kwargs)
