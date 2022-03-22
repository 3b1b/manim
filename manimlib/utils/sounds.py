from manimlib.utils.file_ops import find_file
from manimlib.utils.directories import get_sound_dir


def get_full_sound_file_path(sound_file_name) -> str:
    return find_file(
        sound_file_name,
        directories=[get_sound_dir()],
        extensions=[".wav", ".mp3", ""]
    )
