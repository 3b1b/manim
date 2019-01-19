from big_ol_pile_of_manim_imports import *


class Dedo(Scene):
    def construct(self):
        dedo = Tu()

        self.play(DrawBorderThenFill(dedo))
        self.wait()
        self.play(ApplyMethod(dedo.scale, 1.5,rate_func=there_and_back))
        self.wait()


class Pad(Scene):
    CONFIG={"camera_config":{"background_color":TT_FONDO_T}}
    def construct(self):
        pad = Celular()

        self.play(DrawBorderThenFill(pad))
        self.play(pad.rotate,np.pi/2,
            pad.scale,1.6,
            pad.shift,UP*0.7
            )
        propietario="Propietario del video"
        subtexto=TextMobject("Propietario:",propietario).to_edge(DL).shift(DOWN*0.3)
        texto=TextMobject("Video: Titulo del video").next_to(subtexto,UP).align_to(subtexto,LEFT)
        #leyenda=VGroup(texto,subtexto).arrange_submobjects(LEFT)
        self.play(Write(texto),Write(subtexto))
        self.wait()

class Pad2(Scene):
    CONFIG={"camera_config":{"background_color":TT_FONDO_T}}
    def construct(self):
        pad = Celular().shift(LEFT*10)

        self.add(pad)
        self.play(pad.rotate,np.pi/2,
            pad.scale,1.6,
            pad.move_to,UP*0.7
            )
        propietario="Propietario del video"
        subtexto=TextMobject("Propietario:",propietario).to_edge(DL).shift(DOWN*0.3)
        texto=TextMobject("Video: Titulo del video").next_to(subtexto,UP).align_to(subtexto,LEFT)
        #leyenda=VGroup(texto,subtexto).arrange_submobjects(LEFT)
        self.play(Write(texto),Write(subtexto))
        self.wait()
        self.play(FadeOut(texto),FadeOut(subtexto))
        self.play(pad.rotate,-np.pi/2,
            #pad.scale,1/1.6,
            pad.move_to,LEFT*12
            )
        self.wait()


class Me_gusta(Scene):
    CONFIG={"camera_config":{"background_color":TT_FONDO_T}}
    def construct(self):
        mg = MeGusta()

        self.play(DrawBorderThenFill(mg))

        #leyenda=VGroup(texto,subtexto).arrange_submobjects(LEFT)
        self.wait(3)

class No_me_gusta(Scene):
    CONFIG={"camera_config":{"background_color":TT_FONDO_T}}
    def construct(self):
        nmg = NoMeGusta()

        self.play(DrawBorderThenFill(nmg))

        #leyenda=VGroup(texto,subtexto).arrange_submobjects(LEFT)
        self.wait(3)

class Dedin1(Scene):
    CONFIG={"camera_config":{"background_color":TT_FONDO_T}}
    def construct(self):
        dedo=Dedo1().flip()
        ecu=TexMobject("ax+b=c").scale(1.5)
        dedo.next_to(ecu,RIGHT,buff=1)
        self.play(Write(ecu))
        self.play(LaggedStart(Write,dedo,submobject_mode = "lagged_start",rate_func=bezier([0, 0, 1, 1]),run_time=3),run_time=3)
        self.play(dedo.shift,LEFT*0.6,rate_func=there_and_back)
        self.wait()


class Dedin2(Scene):
    CONFIG={"camera_config":{"background_color":TT_FONDO_T}}
    def construct(self):
        dedo=Dedo2()
        ecu=TexMobject("ax+b=c").scale(1.5)
        dedo.next_to(ecu,RIGHT,buff=0.6).shift(DOWN)
        self.play(Write(ecu))
        self.play(FadeIn(dedo))
        self.play(dedo.shift,np.array([-0.4,0.3,0]),rate_func=there_and_back)
        self.wait()


class Sujetador(Scene):
    CONFIG={"camera_config":{"background_color":TT_FONDO_T}}
    def construct(self):
        pin=Pin()
        self.play(DrawBorderThenFill(pin))
        self.wait()
