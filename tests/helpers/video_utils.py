"""Helpers for dev to set up new tests that use videos."""

import os
import subprocess
import json

from manim import logger


def capture(command):
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf8",
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def get_config_from_video(path_to_video):
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,nb_frames,duration,avg_frame_rate,codec_name",
        "-print_format",
        "json",
        path_to_video,
    ]
    config, err, exitcode = capture(command)
    assert exitcode == 0, err
    return config


def save_control_data_from_video(path_to_video, name):
    """Helper used to set up a new test that will compare videos. This will create a new .json file in control_data/videos_data that contains
    informations tested of the video, including its hash. Refer to the wiki for more informations.

    Parameters
    ----------
    path_to_video : :class:`str`
        Path to the video to extract information from.
    name : :class:`str`
        Name of the test. The .json file will be named with it.
    """
    tests_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path_control_data = os.path.join(tests_directory, "control_data", "videos_data")
    config_video = get_config_from_video(path_to_video)
    data = {
        "name": name,
        "config": json.loads(config_video)["streams"][0],
    }
    path_saved = os.path.join(path_control_data, f"{name}.json")
    json.dump(data, open(path_saved, "w"), indent=4)
    logger.info(f"Data for {name} saved in {path_saved}")
