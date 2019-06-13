from manimlib.imports import *

test_text,test_tex=get_template_tex(
    "test",
    )

class TextTest(TexMobject):
    CONFIG={
    "template_tex_file_body":test_text
    }


class PruebaTest1(Scene):
    def construct(self):
        t=Group(
            TextTest("$\\to$"),
            TextTest("Álex")
            )
        t.arrange(DOWN)
        self.add(t)

class PruebaTest2(Scene):
    def construct(self):
        t=Text("ÁÉÍÓÚáéíóúÑñ")
        self.add(t)