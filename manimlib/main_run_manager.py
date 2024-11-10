from IPython.terminal.embed import KillEmbedded
from typing import Any


class MainRunManager:

    def __init__(self):
        # Command line arguments
        self.args: Any = None

        # Last interactive window spawned
        self.window = None

        self.start_at_line = None

    def set_new_start_at_line(self, start_at_line):
        self.start_at_line = start_at_line

    def run(self):
        while True:
            try:
                self.retrieve_scenes_and_run(self.start_at_line)
            except KillEmbedded:
                print("KillEmbedded detected. Reloading scenes...")
                continue
            except KeyboardInterrupt:
                break

    def retrieve_scenes_and_run(self, overwrite_start_at_line: int | None = None):
        """
        Generates a configuration and runs the scenes.
        """
        import manimlib.config
        import manimlib.extract_scene

        # Args
        if overwrite_start_at_line is not None:
            self.args.embed = str(overwrite_start_at_line)  # type: ignore
        if self.args is None:
            raise RuntimeError("Fatal error: No args were passed to the MainRunManager")

        # Args to Config
        config = manimlib.config.get_configuration(self.args)
        if self.window:
            config["existing_window"] = self.window

        # Scenes
        scenes = manimlib.extract_scene.main(config)
        if len(scenes) > 0:
            first_window = scenes[0].window
            if first_window:
                self.window = first_window

        for scene in scenes:
            scene.run()


manager = MainRunManager()
