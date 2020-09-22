from manim import *

class Demo(Scene):
    CONFIG = {
        'font' : 'sans-serif'
    }
    def construct(self):
        text = PangoText('見 角 言 谷  辛 辰 辵 邑 酉 釆 里!')
        self.play(Write(text))
        self.wait(2)
        mess=PangoText('multi-language',style=ITALIC)
        self.play(Transform(text,mess))
        self.clear()
        #arb=PangoText('hi नमस्ते.',font='sans-serif')
        print(len("नमस्ते"))
        arb=PangoText("Здравствуйте मस नम म ",font='sans-serif')
        self.play(Write(arb))
        self.wait(4)
class Demo1(Scene):
    CONFIG = {
        'font' : 'sans-serif'
    }
    def construct(self):
        text = PangoText('Hello, world!', t2c={'world':BLUE})
        self.play(Write(text))