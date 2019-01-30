from big_ol_pile_of_manim_imports import *


class LastVideoWrapper(Scene):
    def construct(self):
        title = TextMobject("Last time...")
        title.scale(1.5)
        title.to_edge(UP)
        rect = ScreenRectangle(height=6)
        rect.next_to(title, DOWN)
        self.play(
            FadeInFromDown(title),
            ShowCreation(rect)
        )
        self.wait()
