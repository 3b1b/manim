from typing import Any
from IPython.terminal.embed import KillEmbedded


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
        self.args.is_reload = self.is_reload
        scene_config = manimlib.config.get_scene_config(self.args)
        if self.window:
            scene_config["existing_window"] = self.window  # see scene initialization

        run_config = manimlib.config.get_run_config(self.args)

        # Scenes
        self.scenes = manimlib.extract_scene.main(scene_config, run_config)
        if len(self.scenes) == 0:
            print("No scenes found to run")
            return

        # Find first available window
        for scene in self.scenes:
            if scene.window is not None:
                self.window = scene.window
                break

        for scene in self.scenes:
            if self.args.embed:
                print(" ".join([
                    "Loading interactive session for",
                    f"\033[96m{self.args.scene_names[0]}\033[0m",
                    f"in \033[96m{self.args.file}\033[0m",
                    f"at line \033[96m{self.args.embed}\033[0m"
                ]))
            scene.run()

reload_manager = ReloadManager()
