from manim import *


class TexTemplateFromCLI(Scene):
    """This scene uses a custom TexTemplate file.
    The path of the TexTemplate _must_ be passed with the command line
    argument `--tex_template <path to template>`.
    For this scene, you can use the custom_template.tex file next to it.
    This scene will fail to render if a tex_template.tex that doesn't
    import esvect is passed, and will throw a LaTeX error in that case.
    """

    def construct(self):
        text = MathTex(r"\vv{vb}")
        self.play(Write(text))
        self.wait(1)


class InCodeTexTemplate(Scene):
    """This example scene demonstrates how to modify the tex template
    for a particular scene from the code for the scene itself.
    """

    def construct(self):
        # Create a new template
        myTemplate = TexTemplate()

        # Add packages to the template
        myTemplate.add_to_preamble(r"\usepackage{esvect}")

        # Set the compiler and output format (default: latex and .dvi)
        # possible tex compilers: "latex", "pdflatex", "xelatex", "lualatex", "luatex"
        # possible output formats: ".dvi",  ".pdf", and ".xdv"
        myTemplate.tex_compiler = "pdflatex"
        myTemplate.output_format = ".pdf"

        # To use this template in a Tex() or MathTex() object
        # use the keyword argument tex_template
        text = MathTex(r"\vv{vb}", tex_template=myTemplate)
        self.play(Write(text))
        self.wait(1)
