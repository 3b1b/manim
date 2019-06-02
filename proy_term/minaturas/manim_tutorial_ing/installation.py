from big_ol_pile_of_manim_imports import *


class InstallWindows(Scene):
    def construct(self):
        texto=Texto("Installation on\\\\","\\sc Windows")\
             .scale(3.3).set_color_by_gradient(BLUE,GREEN)
        texto[1].scale(1.2)
        VGroup(texto[0],texto[1]).move_to(ORIGIN).scale(1.3)
        self.add(texto)


