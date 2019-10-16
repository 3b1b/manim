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

class Demo(Scene):
    def construct(self):
        text1 = FontText('Hello, world!')
        text2 = FontText('Hello, world!',font='Cambria')
        text2[2].set_color(ORANGE)
        text3 = Text("Hello world!")[0]
        texts = VGroup(text1,text2).arrange(DOWN,aligned_edge=LEFT)
        text3.move_to(texts[-1])

        self.Oldplay(Escribe(texts))
        self.play(Transform(text2,text1))
        self.wait()
        self.play(FadeOut(texts))

class JustifyScene(Scene):
    def construct(self):
        text = TextJustify(r"""\ECFAugie
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
            """,j_width=6,tex_template="tex_template_fonts.tex").scale(0.5)
        self.add(text)