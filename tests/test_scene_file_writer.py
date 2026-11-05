import manimlib.scene.scene_file_writer as scene_file_writer
from manimlib.scene.scene_file_writer import SceneFileWriter


def test_add_sound_to_video_exports_wav_format(tmp_path, monkeypatch):
    movie_file_path = tmp_path / "test.mp4"
    exported = {}
    moved = []
    removed = []
    commands_called = []

    class FakeAudioSegment:
        def export(self, file_path, **kwargs):
            exported["file_path"] = file_path
            exported["kwargs"] = kwargs

    writer = SceneFileWriter.__new__(SceneFileWriter)
    writer.get_movie_file_path = lambda: str(movie_file_path)
    writer.add_audio_segment = lambda segment: None
    writer.audio_segment = FakeAudioSegment()
    writer.ffmpeg_bin = "ffmpeg"

    monkeypatch.setattr(
        scene_file_writer.sp,
        "call",
        lambda commands: commands_called.append(commands),
    )
    monkeypatch.setattr(
        scene_file_writer.shutil,
        "move",
        lambda source, destination: moved.append((source, destination)),
    )
    monkeypatch.setattr(
        scene_file_writer.os,
        "remove",
        lambda path: removed.append(path),
    )

    writer.add_sound_to_video()

    wav_file_path = str(tmp_path / "test.wav")

    assert exported["file_path"] == wav_file_path
    assert exported["kwargs"] == {"format": "wav"}

    assert commands_called[0][4] == wav_file_path

    assert moved == [
        (str(tmp_path / "test_temp.mp4"), str(movie_file_path))
    ]
    assert removed == [wav_file_path]