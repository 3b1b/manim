from big_ol_pile_of_manim_imports import *


def Celular():
    pad = SVGMobject(
        file_name = "mobile",
        fill_opacity = 1,
        stroke_width = 1,
        height = 8,
        stroke_color = WHITE,
    )
    pad[0].set_fill(WHITE)
    pad[1].set_fill(BLACK)
    pad[2].set_fill(None,0)
    pad[2].set_stroke(WHITE,0.5)
    pad[3].set_fill(BLACK)
    pad[4].set_fill(BLACK)
    pad[5].set_fill(BLACK)
    return pad

def Tu():
    dedo = SVGMobject(
            file_name = "tu",
            fill_opacity = 0,
            stroke_width = 0.2,
            height = 4,
            stroke_color = WHITE,
        )
    dedo[0].set_fill("#F4D7AB",1).set_stroke(None,3)
    dedo[1:].set_stroke(None,0.1)
    dedo[4:].set_fill("#EDCE9F",1)
    dedo[11:15].set_fill(WHITE,1)
    dedo[7].set_fill(BLACK,1)
    dedo[10].set_fill(BLACK,1)
    dedo[12:14].set_fill("#EDCE9F",1)
    return dedo


def MeGusta():
    MeGusta = SVGMobject(
    file_name = "like",
    fill_opacity = 1,
    stroke_width = 0,
    height = 3,
    stroke_color = WHITE,
    ).scale(0.8)
    MeGusta[0].set_fill("#0277bd",1)
    MeGusta[1].set_fill("#01579b",1)
    MeGusta[2].set_fill(WHITE,1)
    MeGusta[3].set_fill("#01579b",1)
    return MeGusta

def NoMeGusta():
    NoMeGusta=MeGusta().flip().rotate(np.pi)
    return NoMeGusta

def Dedo1():
    dedo=SVGMobject(
    file_name = "dedo",
    fill_opacity = 1,
    stroke_width = 0,
    height = 1,
    stroke_color = WHITE,
    )
    return dedo

def Dedo2():
    dedo=SVGMobject(
    file_name = "dedo2",
    fill_opacity = 1,
    stroke_width = 0,
    height = 1.3,
    stroke_color = WHITE,
    )
    return dedo


def Pin():
    pin=SVGMobject(
    file_name = "pin",
    fill_opacity = 1,
    stroke_width = 0,
    height = 3,
    stroke_color = WHITE,
    )
    pin[0].set_fill(RED_E,1)
    pin[1].set_fill(GRAY,1)
    pin[2].set_fill(RED,1)
    pin[3].set_fill(RED_E,1)
    pin[4].set_fill(RED_E,1)
    pin[5].set_fill(RED,1)
    pin.rotate(np.pi*0.1)
    return pin

def MP3():
    mp3=SVGMobject(file_name="mp3").scale(3)
    mp3[0].set_fill(RED,1)
    mp3[1].set_fill(BLUE,1)
    mp3[2].set_fill(WHITE,1)
    mp3[3].set_fill(WHITE,1)
    mp3[4:].set_fill(GRAY,1)
    return mp3
    
def TVA():
    return ImageMobject("tele1").scale(3)

def Cinta1():
    return ImageMobject("cinta1").scale()


def Nota1():
    return ImageMobject("nota1").scale()

def Audifonos():
    return SVGMobject(file_name="headphones").set_fill("#d1d5d5",1).scale(0.5)

def Avion():
    svg = SVGMobject(
            file_name = "avion1",
            fill_opacity = 1,
            stroke_width = 1.5,
            height = 1,
            stroke_color = TT_TEXTO,
        ).scale(2).set_fill(TT_TEXTO)
    return svg

def Palomitas():
    svg = SVGMobject(
            file_name = "palomitas",
            fill_opacity = 1,
            stroke_width = 0,
            height = 1,
            stroke_color = TT_TEXTO,
        ).scale(2)
    svg[0].set_fill("#efd35b")
    svg[1].set_fill("#f9e595")
    svg[2].set_fill("#f9e595").shift(RIGHT)
    svg[3:7].set_fill("#e2ba13")
    svg[7:11].set_fill("#f9e595")
    svg[15:23].set_fill(RED)
    svg[23].set_fill("#52a2e7")
    svg[24].set_fill("#ff6243")
    svg[25].set_fill("#3c66b1")
    svg[26].set_fill("#c6c3cb")
    svg[27].set_fill("#3c66b1",0.6)
    svg[28].set_fill("#9b2b00")
    return svg

def Luna():
    svg = SVGMobject(
            file_name = "moon",
            fill_opacity = 1,
            stroke_width = 0,
            height = 1,
            stroke_color = TT_TEXTO,
        ).scale(5)
    svg[3:6].set_fill("#999999")
    svg[6].set_fill("#ececec")
    svg[2].set_fill("#cccccc")
    return svg

def Planeta():
    svg = SVGMobject(
            file_name = "planeta1",
            fill_opacity = 1,
            stroke_width = 0,
            height = 1,
            stroke_color = TT_TEXTO,
        ).scale(5)
    svg[0].set_fill(BLUE)
    svg[1:].set_fill(GREEN)
    return svg

def Pad():
    svg = SVGMobject(
            file_name = "pad",
            fill_opacity = 1,
            stroke_width = 1.5,
            height = 1,
            color=TT_TEXTO,
            stroke_color = TT_TEXTO,
        ).scale(11)
    svg[1].set_fill(BLACK)
    return svg


def Pila():
    svg = SVGMobject(
            file_name = "battery",
            fill_opacity = 1,
            stroke_width = 1,
            height = 4,
            stroke_color = WHITE,
        )
    return svg

def Camara():
    svg = SVGMobject(
            file_name = "camera",
            fill_opacity = 1,
            stroke_width = 1,
            height = 4,
            stroke_color = WHITE,
        )
    return svg

def Reloj():
    svg = SVGMobject(
            file_name = "clock",
            fill_opacity = 1,
            stroke_width = 1,
            height = 4,
            stroke_color = WHITE,
        )
    return svg

def Cursor():
    svg = SVGMobject(
            file_name = "cursor",
            fill_opacity = 1,
            stroke_width = 1,
            height = 4,
            stroke_color = WHITE,
        )
    return svg

def Facebook():
    svg = SVGMobject(
            file_name = "facebook",
            fill_opacity = 1,
            stroke_width = 1,
            height = 4,
            stroke_color = WHITE,
        )
    return svg

def Ubicacion():
    svg = SVGMobject(
            file_name = "placeholder",
            fill_opacity = 1,
            stroke_width = 1,
            height = 4,
            stroke_color = WHITE,
        )
    return svg

def Twitter():
    svg = SVGMobject(
            file_name = "twitter",
            fill_opacity = 1,
            stroke_width = 1,
            height = 4,
            stroke_color = WHITE,
        )
    return svg

def YouTube():
    svg = SVGMobject(
            file_name = "youtube",
            fill_opacity = 1,
            stroke_width = 1,
            height = 4,
            stroke_color = WHITE,
        )
    return svg

def Basura():
    svg = SVGMobject(
            file_name = "trash",
            fill_opacity = 1,
            stroke_width = 1,
            height = 4,
            stroke_color = WHITE,
        )
    return svg

def GitHub():
    svg = SVGMobject(
            file_name = "github",
            fill_opacity = 1,
            stroke_width = 1,
            height = 4,
            stroke_color = WHITE,
        )
    return svg


def tecla_blanca():
    svg = SVGMobject(
            file_name = "tecla_blanca",
            fill_opacity = 1,
            stroke_width = 4,
            height = 1.37,
            stroke_color = BLACK,
        )
    svg.set_fill(WHITE,1)
    return svg

def tecla_negra():
    svg = SVGMobject(
            file_name = "tecla_negra",
            fill_opacity = 1,
            stroke_width = 4,
            height = 0.87,
            stroke_color = BLACK,
        )
    svg.set_fill(BLACK,1)
    return svg

class Caja(VMobject):
    def __init__(self,ancho=3,alto=2,tapas=0.95,**kwargs):
        digest_config(self, kwargs)
        VMobject.__init__(self, **kwargs)
        self.set_anchor_points([UP*alto+LEFT*ancho/2,
                                LEFT*ancho/2,
                                RIGHT*ancho/2,
                                UP*alto+RIGHT*ancho/2],mode="corners")
        tapaI=VMobject().set_anchor_points([self.points[0],self.points[0]+RIGHT*ancho*tapas/2],mode="corners")
        tapaD=VMobject().set_anchor_points([self.points[-1],self.points[-1]+LEFT*ancho*tapas/2],mode="corners")
        self.add(tapaI,tapaD)
        self.set_fill("#D2B48C",0)
        self.set_stroke("#D2B48C",6)

    def tapa_derecha(self):
        return self[2]

    def tapa_izquierda(self):
        return self[1]

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
