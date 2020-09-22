from manim import *

class Demo(Scene):
    CONFIG = {
        'font' : 'sans-serif'
    }
    def construct(self):
        text = PangoText('見 角 言 谷 豆 豕 豸 貝 赤 走 足 身 車 辛 辰 辵 邑 酉 釆 里!')
        self.play(Write(text))
        self.wait(2)
        mess=PangoText('multi-language',style=ITALIC)
        self.play(Transform(text,mess))
        self.clear()
        #arb=PangoText('नमस्ते',font='sans-serif')
        arb=PangoText("Здравствуйте")
        self.play(Write(arb))
        self.wait(4)