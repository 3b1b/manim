"""Utilities for processing LaTeX templates."""

__all__ = [
    "TexTemplate",
    "TexTemplateFromFile",
    "BasicTexTemplate",
    "ThreeBlueOneBrownTexTemplate",
    "ThreeBlueOneBrownCTEXTemplate",
]


import os

threeblueonebrown_tex_template_body = r"""
\documentclass[preview]{standalone}

\usepackage[english]{babel}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{dsfont}
\usepackage{setspace}
\usepackage{tipa}
\usepackage{relsize}
\usepackage{textcomp}
\usepackage{mathrsfs}
\usepackage{calligra}
\usepackage{wasysym}
\usepackage{ragged2e}
\usepackage{physics}
\usepackage{xcolor}
\usepackage{microtype}
\DisableLigatures{encoding = *, family = * }
\linespread{1}

\begin{document}

YourTextHere

\end{document}       
"""


class TexTemplate:
    """
    Class representing a TeX template to be used for creating Tex() and MathTex() objects.
    """

    tex_compiler = None
    output_format = None
    body = None
    has_environment = False

    def __init__(self, **kwargs):
        if self.tex_compiler is None:
            self.tex_compiler = kwargs.pop("tex_compiler", "latex")
        if self.output_format is None:
            self.output_format = kwargs.pop("output_format", ".dvi")
        self.prepare_template_body()

    def prepare_template_body(self):
        self.body = threeblueonebrown_tex_template_body

    def add_to_preamble(self, txt):
        # Adds txt to the TeX template preamble just before \begin{document}
        self.body = self.body.replace("\\begin{document}", txt + "\n\\begin{document}")

    def add_to_document(self, txt):
        # Adds txt to the TeX template just after \begin{document}
        self.body = self.body.replace(
            "\\begin{document}", "\\begin{document}\n" + txt + "\n"
        )

    def get_texcode_for_expression(self, expression):
        # Inserts expression verbatim into TeX template.
        return self.body.replace("YourTextHere", expression)

    def get_texcode_for_expression_in_env(self, expression, environment):
        # Inserts expression into TeX template wrapped in \begin{environemnt} and \end{environment}
        begin = r"\begin{" + environment + "}"
        end = r"\end{" + environment + "}"
        return self.body.replace(
            "YourTextHere", "{0}\n{1}\n{2}".format(begin, expression, end)
        )


class BasicTexTemplate(TexTemplate):
    def prepare_template_body(self):
        self.body = r"""
\documentclass[preview]{standalone}

\usepackage[english]{babel}
\usepackage{amsmath}
\usepackage{amssymb}

\begin{document}

YourTextHere

\end{document}        
"""


class ThreeBlueOneBrownTexTemplate(TexTemplate):
    """
    The default TeX template from the 3b1b version of manim
    """

    def prepare_template_body(self):
        self.body = threeblueonebrown_tex_template_body


class ThreeBlueOneBrownCTEXTemplate(ThreeBlueOneBrownTexTemplate):
    """
    The default TeX template from the 3b1b version of manim with the use_ctex option
    """

    def __init__(self, **kwargs):
        self.tex_compiler = kwargs.pop("tex_compiler", "xelatex")
        self.output_format = kwargs.pop("output_format", ".xdv")
        super().__init__(**kwargs)

    def prepare_template_body(self):
        self.body = threeblueonebrown_tex_template_body.replace(
            r"\DisableLigatures{encoding = *, family = * }", r"\usepackage[UTF8]{ctex}"
        )


class TexTemplateFromFile(TexTemplate):
    def __init__(self, **kwargs):
        self.template_file = kwargs.pop("filename", "tex_template.tex")
        super().__init__(**kwargs)

    def prepare_template_body(self):
        with open(self.template_file, "r") as infile:
            self.body = infile.read()
