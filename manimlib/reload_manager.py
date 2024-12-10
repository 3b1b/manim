from __future__ import annotations

from typing import Any
from IPython.terminal.embed import KillEmbedded


import manimlib.config
import manimlib.extract_scene

from manimlib.window import Window


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from argparse import Namespace


class ReloadManager:
    """
    Manages the loading and running of scenes and is called directly from the
    main entry point of ManimGL.

    The name "reload" comes from the fact that this class handles the
    reinitialization of scenes when requested by the user via the `reload()`
    command in the IPython shell.
    """

    window = None
    is_reload = False

    """
    Whether to autoreload Python modules automatically for every command
    executed in the IPython shell. Also see the docs on the IPython autoreload
    extension.
    """
    should_autoreload = False

    def __init__(self, cli_args: Namespace):
        self.args = cli_args
        self.should_autoreload = self.args.autoreload

    def set_new_start_at_line(self, start_at_line):
        """
        Sets/Updates the line number to load the scene from when reloading.
        """
        self.args.embed = str(start_at_line)

    def run(self):
        """
        Runs the scenes in a loop and detects when a scene reload is requested.
        """
        while True:
            try:
                # blocking call since a scene will init an IPython shell()
                self.retrieve_scenes_and_run()
                return
            except KillEmbedded:
                # Requested via the `exit_raise` IPython runline magic
                # by means of our scene.reload() command
                self.note_reload()
            except KeyboardInterrupt:
                break

    def note_reload(self):
        self.is_reload = True
        print(" ".join([
            "Reloading interactive session for",
            f"\033[96m{self.args.scene_names[0]}\033[0m",
            f"at line \033[96m{self.args.embed}\033[0m"
        ]))

    def retrieve_scenes_and_run(self):
        """
        Creates a new configuration based on the CLI args and runs the scenes.
        """
        # Args to Config
        scene_config = manimlib.config.get_scene_config(self.args)
        scene_config.update(reload_manager=self)

        run_config = manimlib.config.get_run_config(self.args)
        run_config.update(is_reload=self.is_reload)

        # Create or reuse window
        if run_config["show_in_window"] and not self.window:
            self.window = Window(**run_config["window_config"])
        scene_config.update(window=self.window)

        # Scenes
        scenes = manimlib.extract_scene.main(scene_config, run_config)
        if len(scenes) == 0:
            print("No scenes found to run")

        for scene in scenes:
            scene.run()
