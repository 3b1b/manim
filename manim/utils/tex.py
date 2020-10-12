"""Utilities for processing LaTeX templates."""

__all__ = [
    "TexTemplate",
    "TexTemplateFromFile",
]


import os


class TexTemplate:
    """TeX templates are used for creating Tex() and MathTex() objects."""

    default_documentclass = r"\documentclass[preview]{standalone}"
    default_preamble = r"""
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
"""
    default_placeholder_text = "YourTextHere"
    default_tex_compiler = "latex"
    default_output_format = ".dvi"
    default_post_doc_commands = ""

    def __init__(
        self,
        tex_compiler=None,
        output_format=None,
        documentclass=None,
        preamble=None,
        placeholder_text=None,
        post_doc_commands=None,
        **kwargs
    ):
        self.tex_compiler = (
            tex_compiler
            if tex_compiler is not None
            else TexTemplate.default_tex_compiler
        )
        self.output_format = (
            output_format
            if output_format is not None
            else TexTemplate.default_output_format
        )
        self.documentclass = (
            documentclass
            if documentclass is not None
            else TexTemplate.default_documentclass
        )
        self.preamble = (
            preamble if preamble is not None else TexTemplate.default_preamble
        )
        self.placeholder_text = (
            placeholder_text
            if placeholder_text is not None
            else TexTemplate.default_placeholder_text
        )
        self.post_doc_commands = (
            post_doc_commands
            if post_doc_commands is not None
            else TexTemplate.default_post_doc_commands
        )
        self.rebuild()

    def rebuild(self):
        self.body = (
            self.documentclass
            + "\n"
            + self.preamble
            + "\n"
            + r"\begin{document}"
            + "\n"
            + self.post_doc_commands
            + "\n"
            + self.placeholder_text
            + "\n"
            + r"\end{document}"
            + "\n"
        )

    def add_to_preamble(self, txt, prepend=False):
        """Adds stuff to the TeX template's preamble (e.g. definitions, packages). Text can be inserted at the beginning or at the end of the preamble.
        Parameters
        ----------
        txt : :class:`str`
            String containing the text to be added, e.g. ``\\usepackage{hyperref}``
        prepend : Optional[:class:`bool`], optional
            Whether the text should be added at the beginning of the preample, i.e. right after ``\\documentclass``. Default is to add it at the end of the preample, i.e. right before ``\\begin{document}``
        """
        if prepend:
            self.preamble = txt + "\n" + self.preamble
        else:
            self.preamble += "\n" + txt
        self.rebuild()

    def add_to_document(self, txt):
        """Adds txt to the TeX template just after \\begin{document}, e.g. ``\\boldmath``

        Parameters
        ----------
        txt : :class:`str`
            String containing the text to be added.
        """
        self.post_doc_commands += "\n" + txt + "\n"
        self.rebuild()

    def get_texcode_for_expression(self, expression):
        """Inserts expression verbatim into TeX template.

        Parameters
        ----------
        expression : :class:`str`
            The string containing the expression to be typeset, e.g. ``$\\sqrt{2}$``

        Returns
        -------
        :class:`str`
            LaTeX code based on template, containing the given expression and ready for typesetting
        """
        return self.body.replace(self.placeholder_text, expression)

    def get_texcode_for_expression_in_env(self, expression, environment):
        """Inserts expression into TeX template wrapped in \begin{environemnt} and \end{environment}

        Parameters
        ----------
        expression : :class:`str`
            The string containing the expression to be typeset, e.g. ``$\\sqrt{2}$``
        environment : :class:`str`
            The string containing the environment in which the expression should be typeset, e.g. ``align*``

        Returns
        -------
        :class:`str`
            LaTeX code based on template, containing the given expression inside its environment, ready for typesetting
        """
        begin = r"\begin{" + environment + "}"
        end = r"\end{" + environment + "}"
        return self.body.replace(
            self.placeholder_text, "{0}\n{1}\n{2}".format(begin, expression, end)
        )


class TexTemplateFromFile(TexTemplate):
    """A TexTemplate object created from a template file (default: tex_template.tex)"""

    def __init__(self, **kwargs):
        self.template_file = kwargs.pop("filename", "tex_template.tex")
        super().__init__(**kwargs)

    def rebuild(self):
        with open(self.template_file, "r") as infile:
            self.body = infile.read()

    def file_not_mutable():
        raise Exception("Cannot modify TexTemplate when using a template file.")

    def add_to_preamble(self, txt, prepend=False):
        self.file_not_mutable()

    def add_to_document(self, txt):
        self.file_not_mutable()
