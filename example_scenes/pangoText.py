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
        russ = PangoText("Здравствуйте मस नम म ")
        self.play(Write(russ))
        self.wait(2)
        self.clear()
        hin = PangoText("नमस्ते")
        self.play(Write(hin))
        self.wait(2)
        self.clear()
        arb = PangoText("السَّلام عليكُم",font="sans-serif")
        self.play(Write(arb))
        self.wait(3)