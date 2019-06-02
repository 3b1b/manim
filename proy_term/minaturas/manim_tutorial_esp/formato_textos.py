from big_ol_pile_of_manim_imports import *


class ElementosBasicos(Scene):
    def construct(self):
        texto=Texto("Tutorial de Manim\\\\","\\sc 1.1\\\\Elementos\\\\básicos")\
             .scale(3.3).set_color_by_gradient(RED,PURPLE)
        texto[1].scale(1.2)
        VGroup(texto[0],texto[1]).move_to(ORIGIN)
        self.add(texto)


class AnimacionesPausas(Scene):
    def construct(self):
        texto=Texto("Tutorial de Manim\\\\","\\sc 1.2\\\\Animaciones y \\\\pausas")\
             .scale(3.3).set_color_by_gradient(RED,PURPLE)
        texto[1].scale(1.2)
        VGroup(texto[0],texto[1]).move_to(ORIGIN)
        self.add(texto)

class PosicionesRotacionesFuentes(Scene):
    def construct(self):
        texto=Texto("Tutorial de Manim\\\\","\\sc 1.3\\\\","Posiciones, Rotaciones y \\\\ Fuentes")\
             .scale(3.3).set_color_by_gradient(RED,PURPLE)
        texto[1].scale(1.1)
        texto[2].scale(0.6)
        VGroup(texto[0],texto[1],texto[2]).move_to(ORIGIN)
        self.add(texto)


class AprendeManim(Scene):
    def construct(self):
        texto=VGroup(
            Texto("\\sc Aprende manim\\\\ por tu cuenta"),
            Texto("\\it Cómo renderizar los\\\\ archivos de\\\\ \\tt old\\_projects")
            ).arrange_submobjects(DOWN)
        texto.scale(2.8)
        texto.set_color_by_gradient(YELLOW,RED)
        
        self.add(texto)

class Arreglos(Scene):
    def construct(self):
        texto=Texto("Tutorial de Manim\\\\","\\sc 3\\\\","Arreglos")\
             .scale(3.3).set_color_by_gradient(N_CYAN_2,TT_PURPURAROYAL)
        texto[1].scale(1.1)
        texto[2].scale(1.2)
        VGroup(texto[0],texto[1],texto[2]).move_to(ORIGIN)
        self.add(texto)