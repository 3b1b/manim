from typing import Any
from IPython.terminal.embed import KillEmbedded

from manimlib.window import Window


class ReloadManager:
    """
    Manages the loading and running of scenes and is called directly from the
    main entry point of ManimGL.

    The name "reload" comes from the fact that this class handles the
    reinitialization of scenes when requested by the user via the `reload()`
    command in the IPython shell.
    """

    args: Any = None
    scenes: list[Any] = []
    window = None

    # The line number to load the scene from when reloading
    start_at_line = None

    is_reload = False

    def set_new_start_at_line(self, start_at_line):
        """
        Sets/Updates the line number to load the scene from when reloading.
        """
        self.start_at_line = start_at_line

    def run(self):
        """
        Runs the scenes in a loop and detects when a scene reload is requested.
        """
        while True:
            try:
                # blocking call since a scene will init an IPython shell()
                self.retrieve_scenes_and_run(self.start_at_line)
                return
            except KillEmbedded:
                # Requested via the `exit_raise` IPython runline magic
                # by means of our scene.reload() command
                for scene in self.scenes:
                    scene.tear_down()

                self.scenes = []
                self.is_reload = True

            except KeyboardInterrupt:
                break

    def retrieve_scenes_and_run(self, overwrite_start_at_line: int | None = None):
        """
        Creates a new configuration based on the CLI args and runs the scenes.
        """
        import manimlib.config
        import manimlib.extract_scene

        # Args
        if self.args is None:
            raise RuntimeError("Fatal error: No args were passed to the ReloadManager")
        if overwrite_start_at_line is not None:
            self.args.embed = str(overwrite_start_at_line)

        # Args to Config
        scene_config = manimlib.config.get_scene_config(self.args)
        run_config = manimlib.config.get_run_config(self.args)

        # Create or reuse window
        if run_config["show_in_window"] and not self.window:
            self.window = Window(**run_config["window_config"])
        scene_config["window"] = self.window

        # Scenes
        self.scenes = manimlib.extract_scene.main(scene_config, run_config)
        if len(self.scenes) == 0:
            print("No scenes found to run")
            return

        for scene in self.scenes:
            if self.args.embed and self.is_reload:
                print(" ".join([
                    "Reloading interactive session for",
                    f"\033[96m{self.args.scene_names[0]}\033[0m",
                    f"in \033[96m{self.args.file}\033[0m",
                    f"at line \033[96m{self.args.embed}\033[0m"
                ]))
            scene.run()

reload_manager = ReloadManager()
