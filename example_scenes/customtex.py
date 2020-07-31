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
        text = TexMobject(r"\vv{vb}")
        # text=TextMobject(r"$\vv{vb}$")
        self.play(Write(text))


class InCodeTexTemplate(Scene):
    """This example scene demonstrates how to modify the tex template
    for a particular scene from the code for the scene itself.
    """

    def construct(self):
        tpl = TexTemplate()
        tpl.append_package(["esvect", ["f"]])
        config["tex_template"] = tpl

        # text=TextMobject(r"$\vv{vb}$")
        text = TexMobject(r"\vv{vb}")
        self.play(Write(text))
