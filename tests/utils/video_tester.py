import subprocess
import json
from functools import wraps
import os

from ..utils.commands import capture


def _get_config_from_video(path_to_video):
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
    return json.loads(config)["streams"][0]


def _load_video_data(path_to_data):
    return json.load(open(path_to_data, "r"))


def _check_video_data(path_control_data, path_to_video_generated):
    control_data = _load_video_data(path_control_data)
    config_generated = _get_config_from_video(path_to_video_generated)
    config_expected = control_data["config"]
    diff_keys = [
        d1[0]
        for d1, d2 in zip(config_expected.items(), config_generated.items())
        if d1[1] != d2[1]
    ]
    # \n does not work in f-strings.
    newline = "\n"
    assert (
        len(diff_keys) == 0
    ), f"Config don't match. : \n{newline.join([f'For {key}, got {config_generated[key]}, expected : {config_expected[key]}.' for key in diff_keys])}"


def video_comparison(control_data_file, scene_path_from_media_dir):
    """Decorator used for any test that needs to check a rendered scene/video.

    Parameters
    ----------
    control_data_file : :class:`str`
        Name of the control data file, i.e. the .json containing all the pre-rendered references of the scene tested.
        .. warning:: You don't have to pass the path here.

    scene_path_from_media_dir : :class:`str`
        The path of the scene generated, from the media dir. Example: /videos/1080p60/SquareToCircle.mp4.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # NOTE : Every args goes seemingly in kwargs instead of args; this is perhaps Pytest.
            result = f(*args, **kwargs)
            tmp_path = kwargs["tmp_path"]
            tests_directory = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
            path_control_data = os.path.join(
                tests_directory, "control_data", "videos_data", control_data_file
            )
            path_video_generated = tmp_path / scene_path_from_media_dir
            if not os.path.exists(path_video_generated):
                for parent in reversed(path_video_generated.parents):
                    if not parent.exists():
                        assert (
                            False
                        ), f"'{parent.name}' does not exist in '{parent.parent}' (which exists). "
                        break
            _check_video_data(path_control_data, str(path_video_generated))
            return result

        return wrapper

    return decorator
