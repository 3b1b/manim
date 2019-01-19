from big_ol_pile_of_manim_imports import *

grosor_linea=1
h_tb=13.7
b_tb=2.5
h_tn=8.7
b_tn=1.1
proporcion=2.5
origen_do=ORIGIN

color_soprano=RED
color_contra=BLUE
color_tenor=GREEN
color_bajo=PURPLE

octavas=4

class MusicalScene(Scene):
    CONFIG={"camera_config":{"background_color":WHITE}}
    def tecla_origen(self,h,b,p,posicion):
        return RoundedRectangle(height = h/p, width = b/p,corner_radius=0.15).set_stroke(BLACK,grosor_linea).shift(posicion)

    def tecla_relativa_blanca(self,h,b,p,tecla_referencia):
        return RoundedRectangle(height = h/p, width = b/p,corner_radius=0.15).set_stroke(BLACK,grosor_linea).shift(tecla_referencia.get_right()+RIGHT*tecla_referencia.get_width()/2)

    def tecla_sostenido(self,h,b,p,tecla_referencia):
        return RoundedRectangle(height = h/p, width = b/p,corner_radius=0.07).set_stroke(BLACK,grosor_linea).set_fill(BLACK, opacity = 1).shift(tecla_referencia.get_right()+UP*(tecla_referencia.get_height()-h/p)/2)

    def tecla_sostenido_transp(self,h,b,p,tecla_referencia):
        return RoundedRectangle(height = h/p, width = b/p,corner_radius=0.07).set_stroke(BLACK,grosor_linea).shift(tecla_referencia.get_right()+UP*(tecla_referencia.get_height()-h/p)/2)

    def intervalo_p(self,n1,n2,direccion,**kwargs):
        linea=Line(self.partitura[n1].get_center(),self.partitura[n2].get_center())
        return Parentheses(linea,direccion,**kwargs)

    def intervalo_b(self,n1,n2,direccion,**kwargs):
        linea=Line(self.partitura[n1].get_center(),self.partitura[n2].get_center())
        return Bracket(linea,direccion,**kwargs).set_stroke(None,0.1)

    def intervalo_brace(self,n1,n2,direccion,**kwargs):
        linea=Line(self.partitura[n1].get_center(),self.partitura[n2].get_center())
        return Brace(linea,direccion,**kwargs).set_stroke(None,0.1)

    def setup(self):
        self.definir_teclados(octavas,ORIGIN,0.2)
        self.definir_teclas(octavas)

    def definir_octava_back(self,octavas):
        oct_1=[]
        for cont in range(octavas):
            w=cont*12
            if w==0:
                oct_1.append(self.tecla_origen(h_tb,b_tb,proporcion,origen_do)) #0 do
            else:
                oct_1.append(self.tecla_relativa_blanca(h_tb,b_tb,proporcion,oct_1[w+0-1])) #0 do
            oct_1.append(self.tecla_sostenido(h_tn,b_tn,proporcion,oct_1[w+0])) #1 do#
            oct_1.append(self.tecla_relativa_blanca(h_tb,b_tb,proporcion,oct_1[w+0])) #2 re
            oct_1.append(self.tecla_sostenido(h_tn,b_tn,proporcion,oct_1[w+2])) #3 re#
            oct_1.append(self.tecla_relativa_blanca(h_tb,b_tb,proporcion,oct_1[w+2])) #4 mi
            oct_1.append(self.tecla_relativa_blanca(h_tb,b_tb,proporcion,oct_1[w+4])) #5 fa
            oct_1.append(self.tecla_sostenido(h_tn,b_tn,proporcion,oct_1[w+5])) #6 fa #
            oct_1.append(self.tecla_relativa_blanca(h_tb,b_tb,proporcion,oct_1[w+5])) #7 sol
            oct_1.append(self.tecla_sostenido(h_tn,b_tn,proporcion,oct_1[w+7])) #8 sol#
            oct_1.append(self.tecla_relativa_blanca(h_tb,b_tb,proporcion,oct_1[w+7])) #9 La
            oct_1.append(self.tecla_sostenido(h_tn,b_tn,proporcion,oct_1[w+9])) #10 La#
            oct_1.append(self.tecla_relativa_blanca(h_tb,b_tb,proporcion,oct_1[w+9])) #11 si

        return VGroup(*[oct_1[i]for i in range(len(oct_1))])

    def definir_octava_trans(self,octavas):
        oct_1=[]
        for cont in range(octavas):
            w=cont*12
            if w==0:
                oct_1.append(self.tecla_origen(h_tb,b_tb,proporcion,origen_do)) #0 do
            else:
                oct_1.append(self.tecla_relativa_blanca(h_tb,b_tb,proporcion,oct_1[w+0-1])) #0 do
            oct_1.append(self.tecla_sostenido_transp(h_tn,b_tn,proporcion,oct_1[w+0])) #1 do#
            oct_1.append(self.tecla_relativa_blanca(h_tb,b_tb,proporcion,oct_1[w+0])) #2 re
            oct_1.append(self.tecla_sostenido_transp(h_tn,b_tn,proporcion,oct_1[w+2])) #3 re#
            oct_1.append(self.tecla_relativa_blanca(h_tb,b_tb,proporcion,oct_1[w+2])) #4 mi
            oct_1.append(self.tecla_relativa_blanca(h_tb,b_tb,proporcion,oct_1[w+4])) #5 fa
            oct_1.append(self.tecla_sostenido_transp(h_tn,b_tn,proporcion,oct_1[w+5])) #6 fa #
            oct_1.append(self.tecla_relativa_blanca(h_tb,b_tb,proporcion,oct_1[w+5])) #7 sol
            oct_1.append(self.tecla_sostenido_transp(h_tn,b_tn,proporcion,oct_1[w+7])) #8 sol#
            oct_1.append(self.tecla_relativa_blanca(h_tb,b_tb,proporcion,oct_1[w+7])) #9 La
            oct_1.append(self.tecla_sostenido_transp(h_tn,b_tn,proporcion,oct_1[w+9])) #10 La#
            oct_1.append(self.tecla_relativa_blanca(h_tb,b_tb,proporcion,oct_1[w+9])) #11 si

        return VGroup(*[oct_1[i]for i in range(len(oct_1))])

    def definir_teclados(self,octavas,posicion_teclados,escala):
        self.teclado_base=self.definir_octava_back(octavas).scale(escala).move_to(posicion_teclados)
        self.teclado_transparente=self.definir_octava_trans(octavas).scale(escala).move_to(posicion_teclados)

    def definir_teclas(self,octavas):
        self.sost=[]
        self.tec_b=[]
        for cont in range(octavas):
            w=cont*12
            self.sost=self.sost+[1+w,3+w,6+w,8+w,10+w]
            self.tec_b=self.tec_b+[0+w,2+w,4+w,5+w,7+w,9+w,11+w]

        self.do=[]
        self.do_s=[]
        self.re=[]
        self.re_s=[]
        self.mi=[]
        self.fa=[]
        self.fa_s=[]
        self.sol=[]
        self.sol_s=[]
        self.la=[]
        self.la_s=[]
        self.si=[]
        for n in range(octavas):
            self.do.append(0+12*n)
            self.do_s.append(1+12*n)
            self.re.append(2+12*n)
            self.re_s.append(3+12*n)
            self.mi.append(4+12*n)
            self.fa.append(5+12*n)
            self.fa_s.append(6+12*n)
            self.sol.append(7+12*n)
            self.sol_s.append(8+12*n)
            self.la.append(9+12*n)
            self.la_s.append(10+12*n)
            self.si.append(11+12*n)

    def mandar_frente_sostenido(self):
        for i in self.sost:
            self.add_foreground_mobject(self.teclado_base[i])

        for i in self.sost:
            self.add_foreground_mobject(self.teclado_transparente[i])


    def mostrar_notas(self,teclado):
        for i in self.tec_b:
            nota=TexMobject("%d"%i,color=RED).next_to(teclado[i],DOWN,buff=0.01).scale(0.5)
            self.add(nota)
        for i in self.sost:
            nota=TexMobject("%d"%i,color=RED).next_to(teclado[i],UP,buff=0.01).scale(0.5)
            self.add(nota)