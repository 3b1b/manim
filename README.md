from manim import *

class SampleScene(Scene):
    def construct(self):
        # एक लाल रंग की गोली (Pill) बनाना
        pill = Capsule(color=RED, fill_opacity=1).scale(1.5)
        label = Text("The Human Body & Drug Work", font_size=24).next_to(pill, DOWN)
        
        # स्क्रीन पर दिखाने का एनीमेशन
        self.play(Create(pill), Write(label))
        self.wait(1)
        
        # गोली को घुमाना (Rotate)
        self.play(pill.animate.rotate(PI/2).set_color(BLUE))
        self.wait(1)
        
        # गायब करना
        self.play(FadeOut(pill), FadeOut(label))
        
