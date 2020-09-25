from manim import *


class TexTemplateFrenchCursive(TexTemplate):
    def prepare_template_body(self):
        # For more LaTeX font examples from http://jf.burnol.free.fr/showcase.html
        self.body = r"""
\documentclass[preview]{standalone}
\usepackage[english]{babel}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage[T1]{fontenc}
\usepackage[default]{frcursive}
\usepackage[eulergreek,noplusnominus,noequal,nohbar,%
nolessnomore,noasterisk]{mathastext}

\begin{document}

YourTextHere

\end{document}
"""


class FrenchCursive(Tex):
    def __init__(self, *tex_strings, **kwargs):
        super().__init__(
            *tex_strings, tex_template=TexTemplateFrenchCursive(), **kwargs
        )


class AdvancedTexFontExample(Scene):
    def construct(self):
        self.add(Tex("Tex Font Example").to_edge(UL))
        self.play(ShowCreation(FrenchCursive("$f: A \\longrightarrow B$").shift(UP)))
        self.play(
            ShowCreation(FrenchCursive("Behold! We can write math in French Cursive"))
        )
        self.wait(1)
        self.play(
            ShowCreation(
                Tex(
                    "See more font templates at \\\\ http://jf.burnol.free.fr/showcase.html"
                ).shift(2 * DOWN)
            )
        )
        self.wait(2)
