"""Sound-related utility functions."""

__all__ = [
    "get_full_sound_file_path",
]


from pathlib import Path
from ..utils.file_ops import seek_full_path_from_defaults


# Still in use by add_sound() function in scene_file_writer.py
def get_full_sound_file_path(sound_file_name):
    return seek_full_path_from_defaults(
        sound_file_name,
        default_dir=Path("assets") / "sounds",
        extensions=[".wav", ".mp3"],
    )
