import unittest
from unittest.mock import Mock, patch

from addict import Dict

from manimlib.animation.animation import Animation
from manimlib.camera.camera_frame import CameraFrame
from manimlib.config import get_animations_numbers, manim_config, parse_cli
from manimlib.extract_scene import scene_from_class
from manimlib.mobject.mobject import Point
from manimlib.scene.scene import Scene


class IndexedScene(Scene):
    def setup(self):
        self.rendered_indices = []

    def construct(self):
        self.wait(0.2)
        for _ in range(2):
            self.play(Animation(Point(), run_time=0.2))
            self.wait(0.2)

    def post_play(self):
        if not self.skip_animations:
            self.rendered_indices.append(self.num_plays)
        super().post_play()


class ShortScene(IndexedScene):
    def construct(self):
        self.wait(0.2)
        self.wait(0.2)


class AnimationIndexTests(unittest.TestCase):
    def setUp(self):
        camera = patch(
            "manimlib.scene.scene.Camera",
            side_effect=lambda **kwargs: Mock(frame=CameraFrame(), fps=10),
        )
        writer = patch("manimlib.scene.scene.SceneFileWriter")
        camera.start()
        self.writer = writer.start()
        self.writer.return_value.has_progress_display.return_value = False
        self.addCleanup(camera.stop)
        self.addCleanup(writer.stop)

    def config(self, start=None, end=None):
        return Dict(
            start_at_animation_number=start,
            end_at_animation_number=end,
            file_writer_config={},
        )

    def test_cli_accepts_negative_indices_and_ranges(self):
        for flags, expected in [
            (["-n", "-1"], (-1, None)),
            (["-n=-3,-1"], (-3, -1)),
            (["-n", "0,-1"], (0, -1)),
        ]:
            with self.subTest(flags=flags), patch("sys.argv", ["manimgl", *flags]):
                self.assertEqual(get_animations_numbers(parse_cli()), expected)

    def test_selected_plays_and_waits(self):
        for start, end, expected in [
            (-1, None, [4]),
            (-3, None, [2, 3, 4]),
            (-5, None, [0, 1, 2, 3, 4]),
            (-3, -1, [2, 3]),
            (0, -1, [0, 1, 2, 3]),
            (None, -1, [0, 1, 2, 3]),
            (-3, 4, [2, 3]),
            (-1, -3, []),
            (1, 3, [1, 2]),
            (None, None, [0, 1, 2, 3, 4]),
        ]:
            with self.subTest(start=start, end=end):
                scene = scene_from_class(IndexedScene, self.config(start, end), Dict(prerun=False))
                scene.run()
                self.assertEqual(scene.rendered_indices, expected)

    def test_indices_resolve_separately_for_each_scene(self):
        config = self.config(-1)
        for scene_class, expected in [(IndexedScene, 4), (ShortScene, 1)]:
            scene = scene_from_class(scene_class, config, Dict(prerun=False))
            scene.run()
            self.assertEqual(scene.rendered_indices, [expected])
        self.assertEqual(config.start_at_animation_number, -1)
        self.assertEqual(config.file_writer_config, {})

    def test_out_of_range_and_empty_scenes(self):
        for scene_class, start, end in [(IndexedScene, -6, None), (IndexedScene, 0, -6), (Scene, -1, None)]:
            with self.subTest(scene=scene_class, start=start, end=end):
                with self.assertRaisesRegex(ValueError, "out of range"):
                    scene_from_class(scene_class, self.config(start, end), Dict(prerun=False))

    def test_counting_does_not_use_preview_window_or_write_output(self):
        window = Mock()
        window.__deepcopy__ = Mock(side_effect=AssertionError("Window copied"))
        config = self.config(-1)
        config.window = window
        config.presenter_mode = True
        scene_from_class(IndexedScene, config, Dict(prerun=False))
        pre_scene = self.writer.call_args_list[0].args[0]
        self.assertIsNone(pre_scene.window)
        self.assertFalse(pre_scene.presenter_mode)
        self.assertEqual(pre_scene.rendered_indices, [])
        for flag in ["write_to_movie", "save_last_frame"]:
            self.assertFalse(self.writer.call_args_list[0].kwargs[flag])
        window.init_for_scene.assert_called_once()
        window.destroy.assert_not_called()

    def test_prerun_counts_only_selected_frames(self):
        config = self.config(-3, -1)
        with patch.dict(manim_config.file_writer, write_to_movie=True), patch.dict(manim_config.camera, fps=10):
            scene = scene_from_class(IndexedScene, config, Dict(prerun=True))
        self.assertEqual(scene.file_writer_config["total_frames"], 4)
        self.assertEqual(config.file_writer_config, {})

    def test_positive_indices_do_not_require_counting_pass(self):
        scene_from_class(IndexedScene, self.config(1, 3), Dict(prerun=False))
        self.assertEqual(self.writer.call_count, 1)


if __name__ == "__main__":
    unittest.main()
