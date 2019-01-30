from big_ol_pile_of_manim_imports import *

class Curvatura(MovingCameraScene):
    CONFIG={
    "fixed_dimension": 0,
    "default_frame_stroke_width": 1,
    }
    def construct(self):
        self.definir_objetos()
        self.add(self.graficos)
        self.graficos[3:].set_fill(opacity=0)
        self.graficos[3:].set_stroke(opacity=0)
        self.wait()
        cuadro=Square().scale(0.9)
        cuadro.move_to(self.puntos[0])
        self.graficos.save_state()
        self.graficos.generate_target()
        self.graficos.target.set_stroke(None,8)
        self.graficos.target.shift(-cuadro.get_center())
        self.graficos.target.scale(
                FRAME_WIDTH / cuadro.get_width(),
                about_point=ORIGIN,
            )
        self.graficos.target.shift(-LEFT*1.5-UP*1.5)
        self.play(MoveToTarget(self.graficos, run_time=3))
        #self.play(self.graficos[:4].set_stroke,None,8)
        texto=Texto("a+b").scale(3)
        self.graficos.target.shift(-LEFT*1.5-UP*1.5)
        #self.play(MoveToTarget(self.graficos, run_time=3))
        self.play(Escribe(texto),rate_func=linear)
        self.play(texto.move_to,self.puntos[0])
        self.graficos.add(texto)
        self.graficos.target.add(texto)
        self.graficos[3:].set_stroke(opacity=1)
        self.play(ShowCreation(self.graficos[3:]))
        #self.graficos.add(texto)
        self.graficos.target.shift(-LEFT*1.5-UP*1.5)
        self.play(MoveToTarget(self.graficos, run_time=3))

        self.wait()
        #self.play(Restore(self.graficos, run_time=3))

    def definir_objetos(self):
        img = SVGMobject(
            file_name = "luz_curva",
            fill_opacity = 0,
            stroke_width = 2,
        )
        img.set_height(FRAME_HEIGHT*0.731)
        img.shift(DOWN+LEFT*0.07)
        tierra=img[8].set_color(BLACK) #tierra
        capas=VGroup()
        for i in range(len(img[9:16])):
            capas.add(img[9+i])
        capas.set_submobject_colors_by_gradient(BLUE,WHITE)

        lineas=img[0:7].set_color(RED)#lineas proyectadas
        puntos=img[16:24].set_color(ORANGE)#puntos
        tangentes=img[24:30].set_color(GREEN)#tangentes
        normales=img[24:30].copy()
        for i in range(len(normales)):
            normales[i].rotate(PI/2)

        linea=img[7].set_color(TEAL).rotate(PI)#linea que no podemos ver
        tray_luz=img[31].set_color(YELLOW)#trayectoria de la luz

        self.tierra=tierra
        self.capas=capas
        self.lineas=lineas
        self.puntos=puntos
        self.tangentes=tangentes
        self.normales=normales
        self.linea=linea
        self.tray_luz=tray_luz
        self.graficos=VGroup(tierra,capas,lineas,puntos,tangentes,normales,linea,tray_luz)