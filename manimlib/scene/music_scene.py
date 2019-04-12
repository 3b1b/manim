from big_ol_pile_of_manim_imports import *

class MusicalScene(Scene):
    CONFIG={
        "prop": 1.32,
        "pos": ORIGIN,
        "grosor": 1,
        "camera_config":{"background_color":WHITE},
        "origen_do": ORIGIN,
        "octavas": 4,
        "color_soprano": RED,
        "color_contra": BLUE,
        "color_tenor": GREEN,
        "color_bajo": PURPLE,
    }
    def t_b(self,prop):
        return tecla_blanca().scale(prop).set_stroke(BLACK,self.grosor)
    def t_n(self,prop):
        return tecla_negra().scale(prop).set_stroke(BLACK,self.grosor)
    def tec_ref(self,prop,pos,opac):
        return self.t_b(prop).set_fill(WHITE, opacity = opac).move_to(pos)
    def tec_rel(self,prop,ref,opac):
        return self.t_b(prop).set_fill(WHITE, opacity = opac).next_to(ref,RIGHT,buff=0)
    def tec_sharp(self,prop,ref,opac):
        return self.t_n(prop).set_fill(BLACK, opacity = opac).move_to(ref.get_right()).shift(UP*(ref.get_height()-self.t_n(prop).get_height())/2)
    def intervalo_p(self,n1,n2,direccion,**kwargs):
        linea=Line(self.partitura[n1].get_center(),self.partitura[n2].get_center())
        return Parentheses(linea,direccion,**kwargs)

    def intervalo_b(self,n1,n2,direccion,**kwargs):
        linea=Line(self.partitura[n1].get_center(),self.partitura[n2].get_center())
        return Bracket(linea,direccion,**kwargs).set_stroke(None,0.1)

    def intervalo_brace(self,n1,n2,direccion,**kwargs):
        linea=Line(self.partitura[n1].get_center(),self.partitura[n2].get_center())
        return Brace(linea,direccion,**kwargs).set_stroke(None,0.1)

    def intervalo_v(self,n1,n2,texto,color_texto=BLACK,direccion=RIGHT,color_parentesis=TEAL,escala_texto=1,**kwargs):
        parentesis=self.intervalo_p(n1,n2,direccion,buff=SMALL_BUFF*2,parametro=6,width=7).set_color(color_parentesis)
        nombre=TexMobject("%s"%texto,color=color_texto).scale(escala_texto).next_to(parentesis,direccion,buff=SMALL_BUFF*1.5).add_background_rectangle(opacity=0.8,color=color_parentesis,buff=SMALL_BUFF)
        return VGroup(parentesis,nombre)

    def intervalo_h(self,n1,n2,texto,color_texto=BLACK,direccion=UP,color_flecha=ORANGE,escala_texto=0.7,buff_flecha=0.2,buff_texto=SMALL_BUFF*0.7,**kwargs):
        flecha=VFlecha(self.partitura[n1].get_right(),self.partitura[n2].get_left(),buff=buff_flecha).set_color(color_flecha)
        nombre=TexMobject("%s"%texto,color=color_texto).scale(escala_texto).next_to(flecha,direccion,buff=buff_texto).add_background_rectangle(opacity=0.85,color=color_flecha,buff=SMALL_BUFF)
        return VGroup(flecha,nombre)

    def ap_inter_v(self,interv):
        self.play(
            GrowFromCenter(interv[0]),
            GrowFromCenter(interv[1])
            )

    def ap_inter_h(self,interv):
        self.play(GrowArrow(interv[0]),
            GrowFromCenter(interv[1]))
    def setup(self):
        self.importar_partitura()
        self.definir_cifrado()
        self.definir_cambios_notas()

        self.colores=[self.color_bajo,self.color_tenor,self.color_contra,self.color_soprano]
        self.cambios_colores_teclas=[]
        for t in range(len(self.teclas)):
            self.cambios_colores_teclas.append(list(zip(self.teclas[t],self.colores)))

        self.definir_colores()

        for i_p,color in self.colores_notas:
            for i in i_p:
                self.partitura[i].set_color(color)



    def definir_teclado(self,octavas,prop,opac,pos=ORIGIN):
        teclado=VGroup()
        for i in range(octavas):
            if i==0:
                teclado.add(self.tec_ref(prop,pos,opac))
            else:
                teclado.add(self.tec_rel(prop,teclado[-1],opac))
            for tec in ["N","B","N","B","B0","N","B","N","B","N","B"]:
                if tec=="N":
                    teclado.add(self.tec_sharp(prop,teclado[-1],opac))
                if tec=="B":
                    teclado.add(self.tec_rel(prop,teclado[-2],opac))
                if tec=="B0":
                    teclado.add(self.tec_rel(prop,teclado[-1],opac))
        return teclado


    def definir_teclado_piano(self,octavas,prop,opac,pos=ORIGIN):
        octavas=7
        teclado=VGroup()
        teclado.add(self.tec_ref(prop,pos,opac))
        teclado.add(self.tec_sharp(prop,teclado[-1],opac))
        teclado.add(self.tec_rel(prop,teclado[-2],opac))

        for i in range(octavas):
            teclado.add(self.tec_rel(prop,teclado[-1],opac))
            for tec in ["N","B","N","B","B0","N","B","N","B","N","B"]:
                if tec=="N":
                    teclado.add(self.tec_sharp(prop,teclado[-1],opac))
                if tec=="B":
                    teclado.add(self.tec_rel(prop,teclado[-2],opac))
                if tec=="B0":
                    teclado.add(self.tec_rel(prop,teclado[-1],opac))

        teclado.add(self.tec_rel(prop,teclado[-1],opac))
        return teclado

    def definir_teclas(self,octavas):
        sost=[]
        tec_b=[]
        for cont in range(octavas):
            w=cont*12
            sost=sost+[1+w,3+w,6+w,8+w,10+w]
            tec_b=tec_b+[0+w,2+w,4+w,5+w,7+w,9+w,11+w]
        return [sost,tec_b]

    def definir_teclas_piano(self):
        sost=[1]
        tec_b=[0,2]
        for cont in range(7):
            w=cont*12
            sost=sost+[3+1+w,3+3+w,3+6+w,3+8+w,3+10+w]
            tec_b=tec_b+[3+0+w,3+2+w,3+4+w,3+5+w,3+7+w,3+9+w,3+11+w]
        return [sost,tec_b]

    def definir_notas_piano(self):
        octavas=7
        do=[*[3+12*n for n in range(octavas)]]
        do_s=[*[3+1+12*n for n in range(octavas)]]
        re=[*[3+2+12*n for n in range(octavas)]]
        re_s=[*[3+3+12*n for n in range(octavas)]]
        mi=[*[3+4+12*n for n in range(octavas)]]
        fa=[*[3+5+12*n for n in range(octavas)]]
        fa_s=[*[3+6+12*n for n in range(octavas)]]
        sol=[*[3+7+12*n for n in range(octavas)]]
        sol_s=[*[3+8+12*n for n in range(octavas)]]
        la=[0,*[3+9+12*n for n in range(octavas)]]
        la_s=[1,*[3+10+12*n for n in range(octavas)]]
        si=[2,*[3+11+12*n for n in range(octavas)]]
        return [do,do_s,re,re_s,mi,fa,fa_s,sol,sol_s,la,la_s,si]

    def definir_notas(self,octavas):
        do=[*[12*n for n in range(octavas)]]
        do_s=[*[1+12*n for n in range(octavas)]]
        re=[*[2+12*n for n in range(octavas)]]
        re_s=[*[3+12*n for n in range(octavas)]]
        mi=[*[4+12*n for n in range(octavas)]]
        fa=[*[5+12*n for n in range(octavas)]]
        fa_s=[*[6+12*n for n in range(octavas)]]
        sol=[*[7+12*n for n in range(octavas)]]
        sol_s=[*[8+12*n for n in range(octavas)]]
        la=[*[9+12*n for n in range(octavas)]]
        la_s=[*[10+12*n for n in range(octavas)]]
        si=[*[11+12*n for n in range(octavas)]]
        return [do,do_s,re,re_s,mi,fa,fa_s,sol,sol_s,la,la_s,si]


    def mandar_frente_sostenido(self,octavas,teclado):
        for i in self.definir_teclas(octavas)[0]:
            self.add_foreground_mobject(teclado[i])
        #for i in self.definir_teclas(octavas)[1]:
        #    self.bring_to_back(teclado[i])

    def mandar_frente_sostenido_parcial(self,octavas,teclado):
        for i in self.definir_teclas(octavas)[0]:
            self.add_foreground_mobject(teclado[i])
        #for i in self.definir_teclas(octavas)[1]:
        #    self.bring_to_back(teclado[i])

    def mandar_frente_sostenido_piano(self,teclado):
        for i in self.definir_teclas_piano()[0]:
            self.add_foreground_mobject(teclado[i])
        #for i in self.definir_teclas_piano()[1]:
        #    self.bring_to_back(teclado[i])

    def importar_partitura(self):
        pass

    def definir_cambios_notas(self):
        pass

    def definir_colores(self):
        pass


    def definir_cifrado(self):
        pass

    def progresion(self,paso,simbolos_faltantes=[],**kwargs):
        for pre_ind_n,post_ind_n in self.cambios_notas[paso]:
            self.play(*[
                ApplyMethod(
                    self.teclado_transparente[i].set_fill,None,0
                    )
                for i,color in self.cambios_colores_teclas[paso]
                ],
                *[
                ApplyMethod(
                    self.teclado_transparente[i].set_fill,color,1
                    )
                for i,color in self.cambios_colores_teclas[paso+1]
                ],
                *[
                ReplacementTransform(
                    self.partitura[i].copy(),self.partitura[j],
                    )
                for i,j in zip(pre_ind_n,post_ind_n)
                ],
                Write(self.cifrado[paso+1]),
                *[Write(self.partitura[w])for w in simbolos_faltantes],
                **kwargs
            )

    def progresion_con_desfase(self,paso,desfase,x1=0,y1=0,x2=0,y2=0,r_n=0,simbolos_faltantes=[],**kwargs):
        for pre_ind_n,post_ind_n in self.cambios_notas[r_n]:
            self.play(*[
                ApplyMethod(
                    self.teclado_transparente[i].set_fill,None,0
                    )
                for i,color in self.cambios_colores_teclas[paso]
                ],
                *[
                ApplyMethod(
                    self.teclado_transparente[i].set_fill,color,1
                    )
                for i,color in self.cambios_colores_teclas[paso+1]
                ],
                *[
                    ReplacementTransform(
                        self.partitura[i].copy(),self.partitura[j],
                        )
                    for i,j in zip(range(desfase+x1,desfase+y1),range(desfase+x2,desfase+y2))
                    ],
                Write(self.cifrado[paso+1]),
                *[Write(self.partitura[w])for w in simbolos_faltantes],
                **kwargs
            )   

    def primer_paso(self,paso=0,simbolos_faltantes=[],run_time=0.5,**kwargs):
        self.play(
                *[
                ApplyMethod(
                    self.teclado_transparente[i].set_fill,color,1
                    )
                for i,color in self.cambios_colores_teclas[paso]
                ],
            Write(self.cifrado[paso]),
            *[Write(self.partitura[w],run_time=2)for w in simbolos_faltantes],
            run_time=run_time,
            **kwargs
        )

class MusicalScene2(Scene):
    CONFIG={
        "camera_config":{"background_color":WHITE},
        "grosor_linea_teclado": 1,
        "h_tb": 13.7,
        "b_tb": 2.5,
        "h_tn": 8.7,
        "b_tn": 1.1,
        "proporcion_tecla": 2.5,
        "origen_do": ORIGIN,
        "octavas": 4,
        "color_soprano": RED,
        "color_contra": BLUE,
        "color_tenor": GREEN,
        "color_bajo": PURPLE,
        }
    def tecla_origen(self,h,b,p,posicion):
        return RoundedRectangle(height = h/p, width = b/p,corner_radius=0.15).set_stroke(BLACK,self.grosor_linea_teclado).shift(posicion)

    def tecla_relativa_blanca(self,h,b,p,tecla_referencia):
        return RoundedRectangle(height = h/p, width = b/p,corner_radius=0.15).set_stroke(BLACK,self.grosor_linea_teclado).shift(tecla_referencia.get_right()+RIGHT*tecla_referencia.get_width()/2)

    def tecla_sostenido(self,h,b,p,tecla_referencia):
        return RoundedRectangle(height = h/p, width = b/p,corner_radius=0.07).set_stroke(BLACK,self.grosor_linea_teclado).set_fill(BLACK, opacity = 1).shift(tecla_referencia.get_right()+UP*(tecla_referencia.get_height()-h/p)/2)

    def tecla_sostenido_transp(self,h,b,p,tecla_referencia):
        return RoundedRectangle(height = h/p, width = b/p,corner_radius=0.07).set_stroke(BLACK,self.grosor_linea_teclado).shift(tecla_referencia.get_right()+UP*(tecla_referencia.get_height()-h/p)/2)

    def intervalo_p(self,n1,n2,direccion,**kwargs):
        linea=Line(self.partitura[n1].get_center(),self.partitura[n2].get_center())
        return Parentheses(linea,direccion,**kwargs)

    def intervalo_b(self,n1,n2,direccion,**kwargs):
        linea=Line(self.partitura[n1].get_center(),self.partitura[n2].get_center())
        return Bracket(linea,direccion,**kwargs).set_stroke(None,0.1)

    def intervalo_brace(self,n1,n2,direccion,**kwargs):
        linea=Line(self.partitura[n1].get_center(),self.partitura[n2].get_center())
        return Brace(linea,direccion,**kwargs).set_stroke(None,0.1)

    def intervalo_v(self,n1,n2,texto,color_texto=BLACK,direccion=RIGHT,color_parentesis=TEAL,escala_texto=1,**kwargs):
        parentesis=self.intervalo_p(n1,n2,direccion,buff=SMALL_BUFF*2,parametro=6,width=7).set_color(color_parentesis)
        nombre=TexMobject("%s"%texto,color=color_texto).scale(escala_texto).next_to(parentesis,direccion,buff=SMALL_BUFF*1.5).add_background_rectangle(opacity=0.8,color=color_parentesis,buff=SMALL_BUFF)
        return VGroup(parentesis,nombre)

    def intervalo_h(self,n1,n2,texto,color_texto=BLACK,direccion=UP,color_flecha=ORANGE,escala_texto=0.7,buff_flecha=0.2,buff_texto=SMALL_BUFF*0.7,**kwargs):
        flecha=Flecha(self.partitura[n1].get_right(),self.partitura[n2].get_left(),buff=buff_flecha).set_color(color_flecha)
        nombre=TexMobject("%s"%texto,color=color_texto).scale(escala_texto).next_to(flecha,direccion,buff=buff_texto).add_background_rectangle(opacity=0.85,color=color_flecha,buff=SMALL_BUFF)
        return VGroup(flecha,nombre)

    def ap_inter_v(self,interv):
        self.play(
            GrowFromCenter(interv[0]),
            GrowFromCenter(interv[1])
            )

    def ap_inter_h(self,interv):
        self.play(GrowArrow(interv[0]),
            GrowFromCenter(interv[1]))


    def setup(self):
        self.importar_partitura()
        self.definir_cifrado()
        self.definir_cambios_notas()

        self.colores=[self.color_bajo,self.color_tenor,self.color_contra,self.color_soprano]
        self.cambios_colores_teclas=[]
        for t in range(len(self.teclas)):
            self.cambios_colores_teclas.append(list(zip(self.teclas[t],self.colores)))

        self.definir_colores()

        for i_p,color in self.colores_notas:
            for i in i_p:
                self.partitura[i].set_color(color)
        

    def definir_octava_back(self,octavas):
        oct_1=[]
        for cont in range(octavas):
            w=cont*12
            if w==0:
                oct_1.append(self.tecla_origen(self.h_tb,self.b_tb,self.proporcion_tecla,self.origen_do)) #0 do
            else:
                oct_1.append(self.tecla_relativa_blanca(self.h_tb,self.b_tb,self.proporcion_tecla,oct_1[w+0-1])) #0 do
            oct_1.append(self.tecla_sostenido(self.h_tn,self.b_tn,self.proporcion_tecla,oct_1[w+0])) #1 do#
            oct_1.append(self.tecla_relativa_blanca(self.h_tb,self.b_tb,self.proporcion_tecla,oct_1[w+0])) #2 re
            oct_1.append(self.tecla_sostenido(self.h_tn,self.b_tn,self.proporcion_tecla,oct_1[w+2])) #3 re#
            oct_1.append(self.tecla_relativa_blanca(self.h_tb,self.b_tb,self.proporcion_tecla,oct_1[w+2])) #4 mi
            oct_1.append(self.tecla_relativa_blanca(self.h_tb,self.b_tb,self.proporcion_tecla,oct_1[w+4])) #5 fa
            oct_1.append(self.tecla_sostenido(self.h_tn,self.b_tn,self.proporcion_tecla,oct_1[w+5])) #6 fa #
            oct_1.append(self.tecla_relativa_blanca(self.h_tb,self.b_tb,self.proporcion_tecla,oct_1[w+5])) #7 sol
            oct_1.append(self.tecla_sostenido(self.h_tn,self.b_tn,self.proporcion_tecla,oct_1[w+7])) #8 sol#
            oct_1.append(self.tecla_relativa_blanca(self.h_tb,self.b_tb,self.proporcion_tecla,oct_1[w+7])) #9 La
            oct_1.append(self.tecla_sostenido(self.h_tn,self.b_tn,self.proporcion_tecla,oct_1[w+9])) #10 La#
            oct_1.append(self.tecla_relativa_blanca(self.h_tb,self.b_tb,self.proporcion_tecla,oct_1[w+9])) #11 si

        return VGroup(*[oct_1[i]for i in range(len(oct_1))])

    def definir_octava_trans(self,octavas):
        oct_1=[]
        for cont in range(octavas):
            w=cont*12
            if w==0:
                oct_1.append(self.tecla_origen(self.h_tb,self.b_tb,self.proporcion_tecla,self.origen_do)) #0 do
            else:
                oct_1.append(self.tecla_relativa_blanca(self.h_tb,self.b_tb,self.proporcion_tecla,oct_1[w+0-1])) #0 do
            oct_1.append(self.tecla_sostenido_transp(self.h_tn,self.b_tn,self.proporcion_tecla,oct_1[w+0])) #1 do#
            oct_1.append(self.tecla_relativa_blanca(self.h_tb,self.b_tb,self.proporcion_tecla,oct_1[w+0])) #2 re
            oct_1.append(self.tecla_sostenido_transp(self.h_tn,self.b_tn,self.proporcion_tecla,oct_1[w+2])) #3 re#
            oct_1.append(self.tecla_relativa_blanca(self.h_tb,self.b_tb,self.proporcion_tecla,oct_1[w+2])) #4 mi
            oct_1.append(self.tecla_relativa_blanca(self.h_tb,self.b_tb,self.proporcion_tecla,oct_1[w+4])) #5 fa
            oct_1.append(self.tecla_sostenido_transp(self.h_tn,self.b_tn,self.proporcion_tecla,oct_1[w+5])) #6 fa #
            oct_1.append(self.tecla_relativa_blanca(self.h_tb,self.b_tb,self.proporcion_tecla,oct_1[w+5])) #7 sol
            oct_1.append(self.tecla_sostenido_transp(self.h_tn,self.b_tn,self.proporcion_tecla,oct_1[w+7])) #8 sol#
            oct_1.append(self.tecla_relativa_blanca(self.h_tb,self.b_tb,self.proporcion_tecla,oct_1[w+7])) #9 La
            oct_1.append(self.tecla_sostenido_transp(self.h_tn,self.b_tn,self.proporcion_tecla,oct_1[w+9])) #10 La#
            oct_1.append(self.tecla_relativa_blanca(self.h_tb,self.b_tb,self.proporcion_tecla,oct_1[w+9])) #11 si

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

    def importar_partitura(self):
        pass

    def definir_cifrado(self):
        pass

    def definir_cambios_notas(self):
        pass

    def definir_colores(self):
        pass 

    def progresion(self,paso,simbolos_faltantes=[],**kwargs):

        for pre_ind_n,post_ind_n in self.cambios_notas[paso]:
            self.play(*[
                ApplyMethod(
                    self.teclado_transparente[i].set_fill,None,0
                    )
                for i,color in self.cambios_colores_teclas[paso]
                ],
                *[
                ApplyMethod(
                    self.teclado_transparente[i].set_fill,color,1
                    )
                for i,color in self.cambios_colores_teclas[paso+1]
                ],
                *[
                ReplacementTransform(
                    self.partitura[i].copy(),self.partitura[j],
                    )
                for i,j in zip(pre_ind_n,post_ind_n)
                ],
                Write(self.cifrado[paso+1]),
                *[Write(self.partitura[w])for w in simbolos_faltantes],
                **kwargs
            )

    def progresion_con_desfase(self,paso,desfase,x1=0,y1=0,x2=0,y2=0,r_n=0,simbolos_faltantes=[],**kwargs):

        for pre_ind_n,post_ind_n in self.cambios_notas[r_n]:
            self.play(*[
                ApplyMethod(
                    self.teclado_transparente[i].set_fill,None,0
                    )
                for i,color in self.cambios_colores_teclas[paso]
                ],
                *[
                ApplyMethod(
                    self.teclado_transparente[i].set_fill,color,1
                    )
                for i,color in self.cambios_colores_teclas[paso+1]
                ],
                *[
                    ReplacementTransform(
                        self.partitura[i].copy(),self.partitura[j],
                        )
                    for i,j in zip(range(desfase+x1,desfase+y1),range(desfase+x2,desfase+y2))
                    ],
                Write(self.cifrado[paso+1]),
                *[Write(self.partitura[w])for w in simbolos_faltantes],
                **kwargs
            )   

    def primer_paso(self,paso=0,simbolos_faltantes=[],run_time=0.5,**kwargs):
        self.play(
                *[
                ApplyMethod(
                    self.teclado_transparente[i].set_fill,color,1
                    )
                for i,color in self.cambios_colores_teclas[paso]
                ],
            Write(self.cifrado[paso]),
            *[Write(self.partitura[w],run_time=2)for w in simbolos_faltantes],
            run_time=run_time,
            **kwargs
        )
