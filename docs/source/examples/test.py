from manim import *


class Updater1Example(Scene):
    def construct(self):
        curve_reference = Line(ORIGIN, LEFT).set_color(GREEN)
        self.add(curve_reference)

        def update_curve(mob, dt):
            mob.rotate_about_origin(dt)

        curve2 = Line(ORIGIN, LEFT)
        curve2.add_updater(update_curve)
        self.add(curve_reference, curve2)
        self.wait(PI)


import os;
import sys
from pathlib import Path

if __name__ == "__main__":
    project_path = Path(sys.path[1]).parent
    script_name = f"{Path(__file__).resolve()}"
    os.system(
        f"manim  -l --custom_folders  --disable_caching  -p -c 'BLACK' --config_file '{project_path}/manim_settings.cfg' " + script_name)
