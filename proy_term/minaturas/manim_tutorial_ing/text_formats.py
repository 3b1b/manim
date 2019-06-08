from big_ol_pile_of_manim_imports import *


class BasicElements(Scene):
    def construct(self):
        texto=Texto("Manim tutorial\\\\","\\sc 1.1\\\\Basic\\\\elements")\
             .scale(3.3).set_color_by_gradient(RED,PURPLE)
        texto[1].scale(1.2)
        VGroup(texto[0],texto[1]).move_to(ORIGIN)
        self.add(texto)

class AnimationsPauses(Scene):
    def construct(self):
        texto=Texto("Manim tutorial\\\\","\\sc 1.2\\\\Animations \\&\\\\pauses")\
             .scale(3.3).set_color_by_gradient(RED,PURPLE)
        texto[1].scale(1.2)
        VGroup(texto[0],texto[1]).move_to(ORIGIN)
        self.add(texto)


class manimAnimations(Scene):
    def construct(self):
        texto=Texto("\\sc mA")\
             .scale(16).set_color_by_gradient(RED,PURPLE)
        self.add(texto)

class PositionsRotationsFonts(Scene):
    def construct(self):
        texto=Texto("Manim tutorial\\\\","\\sc 1.3\\\\","Positions, Rotations \\& \\\\ Fonts")\
             .scale(3.3).set_color_by_gradient(RED,PURPLE)
        texto[1].scale(1.1)
        texto[2].scale(0.7).shift(UP*0.3)
        VGroup(texto[0],texto[1],texto[2]).move_to(ORIGIN)
        self.add(texto)

class RenderingSettings(Scene):
    def construct(self):
        texto=Texto("Manim tutorial\\\\","\\sc - Settings -\\\\","Rendering Settings")\
             .scale(3.3).set_color_by_gradient(YELLOW,TEAL)
        texto[1].scale(1.1)
        texto[2].scale(0.85).shift(UP*0.3)
        VGroup(texto[0],texto[1],texto[2]).move_to(ORIGIN)
        self.add(texto)

class LeaveProgressBarsByDefault(Scene):
    def construct(self):
        texto=Texto("Manim tutorial\\\\","\\sc - Settings -\\\\","Leave the progress\\\\ bars by default")\
             .scale(3.3).set_color_by_gradient(YELLOW,TEAL)
        texto[1].scale(1.1)
        texto[2].scale(0.8).shift(UP*0.3)
        VGroup(texto[0],texto[1],texto[2]).move_to(ORIGIN)
        self.add(texto)

class TeXFormulas(Scene):
    def construct(self):
        texto=Texto("Manim tutorial\\\\","\\sc 2\\\\ \\TeX\\ Formulas")\
             .scale(3.3).set_color_by_gradient(ORANGE,GOLD)
        texto[1].scale(1.2)
        VGroup(texto[0],texto[1]).move_to(ORIGIN)
        self.add(texto)


class ChangeMediaDirectory(Scene):
    def construct(self):
        texto=Texto("Manim tutorial\\\\","\\sc - Settings -\\\\","Change media\\\\ directory")\
             .scale(3.3).set_color_by_gradient(YELLOW,TEAL)
        texto[1].scale(0.9)
        texto[2].scale(0.9).shift(UP*0.3)
        VGroup(texto[0],texto[1],texto[2]).move_to(ORIGIN)
        self.add(texto)

class LearnManim(Scene):
    def construct(self):
        texto=VGroup(
            Texto("\\sc Learn Manim by\\\\ yourself"),
            Texto("\\it How to render most\\\\ files in \\tt old\\_projects")
            ).arrange_submobjects(DOWN)
        texto.scale(2.8)
        texto.set_color_by_gradient(YELLOW,RED)
        
        self.add(texto)

class Arrays(Scene):
    def construct(self):
        texto=Texto("Manim tutorial\\\\","\\sc 3\\\\","Arrays")\
             .scale(3.7).set_color_by_gradient(N_CYAN_2,TT_PURPURAROYAL)
        texto[1].scale(1.1)
        texto[2].scale(1.2)
        VGroup(texto[0],texto[1],texto[2]).move_to(ORIGIN)
        self.add(texto)

class NumberCreatureScene(Scene):
    def construct(self):
        texto=Texto("Manim tutorial\\\\","How to create your\\\\ own Number Creature")\
             .scale(3.7)
        texto[1].scale(0.78)
        VGroup(texto[0],texto[1]).move_to(ORIGIN)
        ul=underline(texto[0]).shift(DOWN*0.5).scale(1.1)

        VGroup(texto).set_color_by_gradient(YELLOW,RED)
        ul.set_color(ORANGE)
        self.add(texto,ul)