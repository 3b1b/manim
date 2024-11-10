from IPython.terminal.embed import KillEmbedded
from typing import Any


class ReloadManager:
    """
    Manages the loading and running of scenes and serves is called directly
    from the main entry point of ManimGL.

    The name "reload" comes from the fact that this class handles the
    reinitialization of scenes when requested by the user via the `reload()`
    command in the IPython shell.
    """

    args: Any = None
    scenes: list[Any] = []
    window = None

    # The line number to load the scene from when reloading
    start_at_line = None

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
                print("Reloading...")

                for scene in self.scenes:
                    scene.tear_down()

                self.scenes = []

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
        config = manimlib.config.get_configuration(self.args)
        if self.window:
            config["existing_window"] = self.window  # see scene initialization

        # Scenes
        self.scenes = manimlib.extract_scene.main(config)
        if len(self.scenes) > 0:
            for scene in self.scenes:
                # Find first available window
                if scene.window is not None:
                    self.window = scene.window
                    break

        for scene in self.scenes:
            scene.run()


reload_manager = ReloadManager()
