from manim import *

# Test cases:
# 1. manim customtex.py ExampleFileScene -pl
#       --> should fail, because \vv is not defined
#
# 2. manim customtex.py ExampleFileScene --tex_template custom_template.tex -pl
#       --> should succeed as custom template includes package esvect (which defines \vv)
#
# 3. manim customtex.py ExampleClassScene -pl
#       --> should succeed as the package esvect is included in template object

class ExampleFileScene(Scene):
    def construct(self):
        text = TexMobject(r"\vv{vb}")
        #text=TextMobject(r"$\vv{vb}$")
        self.play(Write(text))


class ExampleClassScene(Scene):
    def construct(self):
        tpl = TexTemplate()
        tpl.append_package(["esvect", ["f"]])
        config['tex_template'] = tpl

        #text=TextMobject(r"$\vv{vb}$")
        text = TexMobject(r"\vv{vb}")
        self.play(Write(text))
