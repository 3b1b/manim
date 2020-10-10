"""Utilities for processing LaTeX templates."""

__all__ = [
    "TexTemplate",
    "TexTemplateFromFile",
    "BasicTexTemplate",
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

    def prepend_to_preamble(self, txt):
        """Adds txt to the TeX template preamble just after the \documentclass"""
        self.preamble = txt + "\n" + self.preamble
        self.rebuild()

    def add_to_preamble(self, txt):
        """Adds txt to the TeX template preamble just before \begin{document}"""
        self.preamble += "\n" + txt
        self.rebuild()

    def add_to_document(self, txt):
        """Adds txt to the TeX template just after \begin{document}"""
        self.post_doc_commands += "\n" + txt + "\n"
        self.rebuild()

    def get_texcode_for_expression(self, expression):
        """Inserts expression verbatim into TeX template."""
        return self.body.replace(self.placeholder_text, expression)

    def get_texcode_for_expression_in_env(self, expression, environment):
        """Inserts expression into TeX template wrapped in \begin{environemnt} and \end{environment}"""
        begin = r"\begin{" + environment + "}"
        end = r"\end{" + environment + "}"
        return self.body.replace(
            self.placeholder_text, "{0}\n{1}\n{2}".format(begin, expression, end)
        )


class BasicTexTemplate(TexTemplate):
    """A simple Tex Template with only basic AMS packages"""

    def __init__(self, *args, **kwargs):
        basic_headers = r"""
\usepackage[english]{babel}
\usepackage{amsmath}
\usepackage{amssymb}      
"""
        preamble = kwargs.pop("preamble", basic_headers)
        super().__init__(*args, preamble=preamble, **kwargs)


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

    def prepend_to_preamble(self, txt):
        self.file_not_mutable()

    def add_to_preamble(self, txt):
        self.file_not_mutable()

    def add_to_document(self, txt):
        self.file_not_mutable()
