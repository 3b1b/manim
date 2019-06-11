from manimlib.imports import *

class abrir_caja(Rotating):
    CONFIG={
        "run_time":0.75,
        "rate_func":smooth
    }    
    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        sobre_izq=self.mobject.points[0]
        sobre_der=self.mobject.points[-1]
        self.mobject[1].rotate(
            alpha * PI*2.3/2,
            about_point=sobre_izq,
            about_edge=sobre_izq,
        )
        self.mobject[2].rotate(
            -alpha * PI*2.3/2,
            about_point=sobre_der,
            about_edge=sobre_der,
        )

class cerrar_caja(Rotating):
    CONFIG={
        "run_time":0.75,
        "rate_func":smooth
    }    
    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        sobre_izq=self.mobject.points[0]
        sobre_der=self.mobject.points[-1]
        self.mobject[1].rotate(
            -alpha * PI*2.3/2,
            about_point=sobre_izq,
            about_edge=sobre_izq,
        )
        self.mobject[2].rotate(
            alpha * PI*2.3/2,
            about_point=sobre_der,
            about_edge=sobre_der,
        )

class girar_cuerda(Rotating):
    CONFIG={
        "run_time":3,
        "rate_func":there_and_back,
        "axis":DOWN
    }    
    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        origen=self.mobject.get_end()
        self.mobject.rotate(
            alpha * 30*DEGREES,
            about_point=origen,
            about_edge=origen,
            axis=self.axis
        )

class girar_sistema(Rotating):
    CONFIG={
        "run_time":3,
        "rate_func":there_and_back,
        "axis":UP,
        "origen":ORIGIN
    }    
    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        self.mobject.rotate(
            alpha * 45*DEGREES,
            about_point=self.origen,
            about_edge=self.origen,
            axis=self.axis
        )
