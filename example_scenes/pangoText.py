from manim import *


class PangoRendering(Scene):
    CONFIG = {"font": "sans-serif"}

    def construct(self):
        morning = PangoText("வணக்கம்", font="sans-serif")
        self.play(Write(morning))
        self.wait(3)
        self.clear()
        chin = PangoText("見 角 言 谷  辛 辰 辵 邑 酉 釆 里!")
        self.play(Write(chin))
        self.wait(2)
        mess = PangoText("Multi-Language", style=BOLD)
        self.play(Transform(chin, mess))
        self.wait(2)
        self.clear()
        russ = PangoText("Здравствуйте मस नम म ", font="sans-serif")
        self.play(Write(russ))
        self.wait(2)
        self.clear()
        hin = PangoText("नमस्ते", font="sans-serif")
        self.play(Write(hin))
        self.wait(2)
        self.clear()
        arb = PangoText("صباح الخير  ", font="sans-serif")
        self.play(Write(arb))
        self.wait(3)
        self.clear()
        arb = PangoText(
            "صباح الخير \n تشرفت بمقابلتك", font="sans-serif"
        )  # don't mix RTL and LTR languages nothing shows up then ;-)
        self.play(Write(arb))
        self.wait(3)
        self.clear()
