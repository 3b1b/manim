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
        # text=Tex(r"$\vv{vb}$")
        self.play(Write(text))


class InCodeTexTemplate(Scene):
    """This example scene demonstrates how to modify the tex template
    for a particular scene from the code for the scene itself.
    """

    def construct(self):
        # Create a new template
        template = TexTemplate()

        # Add packages to the template
        template.add_to_preamble(r"\usepackage{esvect}")

        # Set the compiler and output format (default: latex and .dvi)
        # possible tex compilers: "latex", "pdflatex", "xelatex", "lualatex", "luatex"
        # possible output formats: ".dvi",  ".pdf", and ".xdv"
        template.tex_compiler = "pdflatex"
        template.output_format = ".pdf"

        # To use this as the default template for all Tex:
        # config["tex_template"] = template
        # To use this template only for specific Tex() objects
        # use the keyword argument tex_template

        text = MathTex(r"f:A\rightarrow B", tex_template=template)
        text.shift(DOWN)
        self.play(Write(text))
