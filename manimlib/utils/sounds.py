from __future__ import annotations

import subprocess
import threading
import platform

from manimlib.utils.directories import get_sound_dir
from manimlib.utils.file_ops import find_file


def get_full_sound_file_path(sound_file_name: str) -> str:
    return find_file(
        sound_file_name,
        directories=[get_sound_dir()],
        extensions=[".wav", ".mp3", ""]
    )


def play_sound(sound_file):
    """Play a sound file using the system's audio player"""
    full_path = get_full_sound_file_path(sound_file)
    system = platform.system()

    if system == "Windows":
        import winsound
        winsound.PlaySound(full_path, winsound.SND_FILENAME)
    elif system == "Darwin":
        # macOS
        subprocess.Popen(
            ["afplay", full_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    else:
        subprocess.Popen(
            ["aplay", full_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
