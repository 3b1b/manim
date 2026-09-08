"""Adapted from example_scenes.py's TexTransformExample, trimmed to one transform."""
from manimlib import *


class TexTransformExample(Scene):
    def construct(self):
        t2c = {"A": BLUE, "B": TEAL, "C": GREEN}
        kw = dict(font_size=72, t2c=t2c)
        lines = VGroup(
            Tex("A^2 + B^2 = C^2", **kw),
            Tex("A^2 = C^2 - B^2", **kw),
        )
        lines.arrange(DOWN, buff=LARGE_BUFF)

        self.add(lines[0])
        # TransformMatchingStrings lines up parts of the source and
        # target mobjects that share matching substrings.
        self.play(
            TransformMatchingStrings(
                lines[0].copy(),
                lines[1],
                matched_keys=["A^2", "B^2", "C^2"],
                key_map={"+": "-"},
                path_arc=90 * DEG,
            ),
        )
        self.wait()
