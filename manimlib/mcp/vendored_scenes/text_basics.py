"""Adapted from example_scenes.py's TextExample, trimmed to the font-independent parts."""
from manimlib import *


class TextExample(Scene):
    def construct(self):
        text = Text("Here is a text", font_size=90)
        difference = Text(
            "Text supports plain strings; Tex/TexText support LaTeX",
            font_size=32,
            # t2c is a dict that lets you choose color per substring
            t2c={"Text": BLUE, "Tex": BLUE, "TexText": BLUE, "LaTeX": ORANGE},
        )
        VGroup(text, difference).arrange(DOWN, buff=1)
        self.play(Write(text))
        self.play(FadeIn(difference, UP))
        self.wait()
