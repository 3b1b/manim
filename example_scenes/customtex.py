from manim import *

class ExampleFileScene(Scene):
    def construct(self):
        text=TexMobject(r"\vv{vb}")
        #text=TextMobject(r"$\vv{vb}$")
        self.play(Write(text))

class ExampleScene(Scene):
    def construct(self):
        tpl=TexTemplate()
        tpl.append_package(["esvect",["f"]])
        config.register_tex_template(tpl)

        #text=TextMobject(r"$\vv{vb}$")
        text=TexMobject(r"\vv{vb}")
        self.play(Write(text))
