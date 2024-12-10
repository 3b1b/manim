from __future__ import annotations

from typing import Any
from IPython.terminal.embed import KillEmbedded


from manimlib.config import get_global_config
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

    def retrieve_scenes_and_run(self):
        """
        Take the global configuration, which is based on CLI arguments,
        modify it based on reloading status, then extract and run scenes
        accordingly
        """
        global_config = get_global_config()
        scene_config = global_config["scene"]
        run_config = global_config["run"]

        # Create or reuse window
        if run_config["show_in_window"] and not self.window:
            self.window = Window(**global_config["window"])
        scene_config.update(window=self.window)

        # Scenes
        scenes = manimlib.extract_scene.main(scene_config, run_config)
        if len(scenes) == 0:
            print("No scenes found to run")

        for scene in scenes:
            scene.run()
