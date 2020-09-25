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
        # Create a template
        template = TexTemplate()
        # Other options include
        # BasicTexTemplate()
        # ThreeBlueOneBrownTexTemplate()
        # ThreeBlueOneBrownCTEXTemplate()

        # Add packages to the template
        template.add_to_preamble(r"\usepackage{esvect}")

        # Set the compiler and output format (default: latex and .dvi)
        template.tex_compiler = "pdflatex"
        # Alternatives are "latex", "pdflatex", "xelatex", "lualatex", "luatex"
        template.output_format = ".pdf"
        # alternatives are ".dvi",  ".pdf", and ".xdv"

        # To use this as the default template for all Tex:
        config["tex_template"] = template

        text = MathTex(r"\vv{vb}")
        self.play(Write(text))

        # To use this template for a single Tex() or MathTex() object only
        text2 = MathTex(r"f:A\rightarrow B", tex_template=template)
        text2.shift(DOWN)
        self.play(Write(text2))
