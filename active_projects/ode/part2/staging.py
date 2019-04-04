from big_ol_pile_of_manim_imports import *


class FourierSeriesIntro(Scene):
    def construct(self):
        title = TextMobject(
            "Fourier ", "Series", ":",
            " An origin story",
            arg_separator="",
        )
        title.scale(2)
        title.to_edge(UP)
        image = ImageMobject("Joseph Fourier")
        image.set_height(5)
        image.next_to(title, DOWN, MED_LARGE_BUFF)
        image.to_edge(LEFT)
        name = TextMobject("Joseph", "Fourier")
        name.next_to(image, DOWN)

        self.add(title)
        self.add(image)
        self.add(name)
