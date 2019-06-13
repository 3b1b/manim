from big_ol_pile_of_manim_imports import *


class FormulasTeX(Scene):
    def construct(self):
        texto=Texto("Tutorial de Manim\\\\","\\sc 2\\\\ Fórmulas \\TeX")\
             .scale(3.3).set_color_by_gradient(ORANGE,GOLD)
        texto[1].scale(1.2)
        VGroup(texto[0],texto[1]).move_to(ORIGIN)
        self.add(texto)



class OpcionesDeRenderizado(Scene):
    def construct(self):
        texto=Texto("Tutorial de Manim\\\\","\\sc - Configuración -\\\\","Opciones de\\\\renderizado")\
             .scale(3.3).set_color_by_gradient(YELLOW,TEAL)
        texto[1].scale(0.9)
        texto[2].scale(0.8).shift(UP*0.3)
        VGroup(texto[0],texto[1],texto[2]).move_to(ORIGIN)
        self.add(texto)

class DejarLaBarraDeProgreso(Scene):
    def construct(self):
        texto=Texto("Tutorial de Manim\\\\","\\sc - Configuración -\\\\","Dejar las barras\\\\ de progreso")\
             .scale(3.3).set_color_by_gradient(YELLOW,TEAL)
        texto[1].scale(0.9)
        texto[2].scale(0.8).shift(UP*0.3)
        VGroup(texto[0],texto[1],texto[2]).move_to(ORIGIN)
        self.add(texto)

class CambiarDirectorioMedia(Scene):
    def construct(self):
        texto=Texto("Tutorial de Manim\\\\","\\sc - Configuración -\\\\","Cambiar directorio\\\\ de la carpeta media")\
             .scale(3.3).set_color_by_gradient(YELLOW,TEAL)
        texto[1].scale(0.9)
        texto[2].scale(0.8).shift(UP*0.3)
        VGroup(texto[0],texto[1],texto[2]).move_to(ORIGIN)
        self.add(texto)