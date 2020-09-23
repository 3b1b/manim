from manim import *


class PangoRendering(Scene):
    CONFIG = {"font": "sans-serif"}

    def construct(self):
        text = PangoText("見 角 言 谷  辛 辰 辵 邑 酉 釆 里!")
        self.play(Write(text))
        self.wait(2)
        mess = PangoText("Multi-Language", style=ITALIC)
        self.play(Transform(text, mess))
        self.wait(2)
        self.clear()
        arb = PangoText("Здравствуйте मस नम म ", font="sans-serif")
        self.play(Write(arb))
        self.wait(2)
        self.clear()
        arb = PangoText("नमस्ते", font="sans-serif")
        self.play(Write(arb))
        self.wait(3)
