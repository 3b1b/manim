from big_ol_pile_of_manim_imports import *

class SeleccionTexto(Scene):
    CONFIG = {"include_sound": True}
    def construct(self):
        texto=TextMobject("Texto",color=WHITE).scale(3)
        self.play(Escribe(texto,rate_func=linear))
        seleccion_texto(self,texto)
        self.play(mostrar_seleccion_texto(self,texto))
        self.wait()
        self.play(texto.rect.fade,1)
        self.wait()

class SeleccionTextoGrande(Scene):
    def construct(self):
        texto1=TextMobject("Texto 1",color=WHITE).scale(3)
        texto2=TextMobject("Texto 2",color=WHITE).scale(3)
        VGroup(texto1,texto2).arrange_submobjects(DOWN,buff=0.5)
        self.play(Escribe(texto1),Escribe(texto2))
        seleccion=seleccion_grande_texto(self,texto1)
        self.play(FadeIn(seleccion))
        mueve_seleccion(self,seleccion,texto2)
        self.wait()
        mueve_seleccion(self,seleccion,texto1)
        self.wait()

class RemplazoTexto(Scene):
    def construct(self):
        texto=Texto("Teoría de la gravedad").to_corner(UL)
        texto2=Texto("Contradicción con la ciencia")
        texto3=Texto("Eso no es verdad")
        
        texto=escribe_texto(self,texto)
        self.wait()
        texto2=reescribe_texto(self,texto,texto2)
        self.wait()
        texto3=reescribe_texto(self,texto2,texto3)
        self.play(texto3.shift,RIGHT)
        self.play(texto3[2].set_color,RED)
        self.wait(2)

class GrillaEscena(Scene):
    def construct(self):
        grilla=Grilla()
        p1=Dot(coord(3.05,-1))
        self.play(ShowCreation(grilla),DrawBorderThenFill(p1))
        self.wait()

class Dimensiones2(Scene):
    def construct(self):
        rectangulo=Rectangle(width=5,height=3)
        rectangulo.rotate(30*DEGREES)
        linea=Line(LEFT*1.5,RIGHT*1.5)
        linea.rotate(20*DEGREES)
        linea.shift(LEFT*2)
        v_medicion=Medicion(linea).add_tips().add_letter("x",buff=2)
        self.play(ShowCreation(linea))
        self.play(GrowFromCenter(v_medicion))
        def update(grupo):
            nueva_medicion=Medicion(linea).add_tips().add_letter("x",buff=2)
            for i in range(len(grupo)-1):
                grupo[i].put_start_and_end_on(nueva_medicion[i].get_start(),nueva_medicion[i].get_end())
            grupo[-1].move_to(nueva_medicion[-1])


        self.play(linea.scale,2,linea.rotate,PI/8,linea.shift,RIGHT*3,
            UpdateFromFunc(
            v_medicion,update))
        self.wait(2)
        
class Dimensiones3(Scene):
    def construct(self):
        rectangulo=Rectangle(width=5,height=3)
        rectangulo.rotate(30*DEGREES)
        linea=Line(LEFT*1.5,RIGHT*1.5)
        linea.rotate(20*DEGREES)
        linea.shift(LEFT*2)
        v_medicion=Medicion(linea,color=BLUE,dashed=True).add_tips().add_tex("x",buff=1)
        self.play(ShowCreation(linea))
        self.play(GrowFromCenter(v_medicion))
        def update_f(grupo):
            nuevo_grupo=Medicion(linea,dashed=True,color=BLUE).add_tips().add_tex("x",buff=1)
            Transform(grupo,nuevo_grupo).update(1)
            return grupo


        self.play(linea.scale,2,linea.rotate,PI/8,linea.shift,RIGHT*3,
            UpdateFromFunc(
            v_medicion,update_f))
        self.wait(2)
        
class CambioArco(Scene):
    def construct(self):
        flecha=Arc(0)
        self.add(flecha)
        def update(grupo,alpha):
            dx = interpolate(0, 45*DEGREES, alpha)
            nuevo_grupo=Arc(dx)
            Transform(grupo,nuevo_grupo).update(1)
            return grupo
        self.wait(0.5)
        self.play(UpdateFromAlphaFunc(flecha,update))
        self.wait(0.5)
        def update2(grupo,alpha):
            dx = interpolate(45*DEGREES, 80*DEGREES, alpha)
            nuevo_grupo=Arc(dx)
            Transform(grupo,nuevo_grupo).update(1)
            return grupo
        self.play(UpdateFromAlphaFunc(flecha,update2))
        linea=Line(LEFT,UL)
        self.play(Transform(flecha,linea))
        self.wait(0.5)

class Teclado(Scene):
    CONFIG = {"include_sound": True,
    "camera_config":{"background_color":FONDO_ST}}
    def construct(self):
        self.wait()
        texto=TikzMobject("""
\\begin{lstlisting}[language=Python,style=basic,numbers=none]
<contenido>
    <tema1>
    Tema 1
        <tema1.1>
            Subtema 1
        </tema1.1>
    </tema1>
    <tema2> 
    Tema 2 
        <tema2.1>
            Subtema 2
        </tema2.1>
    </tema2>
</contenido>
\\end{lstlisting}
            """).set_stroke(None,0).set_fill(WHITE,0).scale(2).to_corner(UL)
        for i in list(range(0,11))+list(range(105,117)):
            texto[i].set_color(ROSA_ST)
        for i in list(range(11,18))+list(range(50,65))+list(range(97,105)):
            texto[i].set_color(VERDE_ST)
        for i in list(range(23,32))+list(range(40,50))+list(range(70,79))+list(range(87,97)):
            texto[i].set_color(AMARILLO_ST)
        self.add(texto)
        #'''
        KeyBoard(self,texto[0:40],p=0.037,time_random=0.037)
        self.wait()
        self.play(texto.move_to,np.array([0,2,0])+texto.get_center())
        KeyBoard(self,texto[40:87],p=0.037,time_random=0.037)
        self.wait()
        self.play(texto.move_to,np.array([0,4,0])+texto.get_center())
        KeyBoard(self,texto[87:],p=0.037,time_random=0.037)
        #'''
        #self.play(texto.move_to,np.array([0,2,0])+texto.get_center())

class Soporte(Scene):
    def construct(self):
        pat1=Patron(width=4,height=7,grosor=0.5,agregar_base=True,direccion="R",stroke_width=5)
        pat1[-1].scale(1.007).shift(RIGHT*0.02)
        pat2=Patron(width=2,height=7,grosor=0.5,agregar_base=True,direccion="R",stroke_width=5)
        pat2[-1].scale(1.007).shift(RIGHT*0.02)
        pat1.shift(LEFT*4)
        pat2.shift(LEFT*4)
        self.play(*[LaggedStart(ShowCreation,pat1[i],rate_func=linear)for i in range(len(pat1))])
        self.play(Transform(pat1,pat2))
        self.wait()

class Indice(EscenaContenido):
    CONFIG={
    "escala":0.7
    }
    def setup(self):
        self.contenido=[
            "Tema de lo que \\\\ sea - (6:20)",
                "Sub tema",
                "Sub tema",
            "--",
            "Tema - (6:12)",
                "Sub tema",
                "Sub tema",
            "--",
            "Tema",
                "Sub tema",
                "Sub tema",
                "Sub tema",
            "--",
            "Tema",
                "Sub tema",
            "--",]


class ObjetoCaja(Scene):
    def construct(self):
        objeto=Caja(ancho=4)
        cinta=Nota1()
        cinta.move_to(objeto)
        objeto_etiqueta=Formula("A",color=BLACK).move_to(objeto)
        cinta.set_height(objeto_etiqueta.get_height()*2)
        self.play(ShowCreation(objeto))
        self.play(objeto.set_fill,None,0.85)

        def update(imagen):
            imagen.move_to(objeto_etiqueta)
            return imagen
        self.play(FadeInFrom(cinta,UP))
        self.wait()

        self.play(Escribe(objeto_etiqueta))
        objeto.add(objeto_etiqueta)
        self.play(objeto.shift,DOWN*3+LEFT*2,UpdateFromFunc(cinta,update),path_arc=PI/4)
        self.wait()
        self.play(objeto_etiqueta.move_to,objeto.get_corner(UL),objeto_etiqueta.shift,cinta.get_width()*RIGHT*1.3/2+cinta.get_height()*DOWN*1.3/2,UpdateFromFunc(cinta,update))
        self.play(abrir_caja(objeto))

        self.play(objeto.shift,UP*4.5+RIGHT*4,UpdateFromFunc(cinta,update),path_arc=PI/4)
        self.wait()
        self.play(cerrar_caja(objeto))
        self.wait()

class Titulo(Scene):
    def construct(self):
        tikz="""
            \\begin{tikzpicture}[pencildraw/.style={decorate,
            decoration={random steps,segment length=0.8pt,amplitude=0.3pt}}]
                \\node[pencildraw,draw] {\\sc Derivada};
            \\end{tikzpicture} 
              """
        tit=TikzMobject(tikz,stroke_width=2,fill_opacity=.1).scale(3)
        tit[1:].set_stroke(None,0).set_fill(WHITE,1)
        self.play(Write(tit),run_time=3)
        self.wait()

class OmegaDice(Scene):
    def construct(self):
        Ale=Alex()
        palabras_ale = TextMobject("Yo soy OmegaCreature")
        self.play(FadeIn(Ale.to_edge(DL)))
        self.play(Blink(Ale))
        self.play(OmegaCreatureDice(
            Ale, palabras_ale, 
            bubble_kwargs = {"height" : 3, "width" : 4},
            target_mode="speaking"
        ))
        self.wait()
        self.play(Blink(Ale))
        self.play(RemueveDialogo(Ale))
        self.play(
            Ale.change_mode, "participa"
        )
        self.play(OmegaCreatureDice(
            Ale, palabras_ale, 
            bubble_kwargs = {"height" : 3, "width" : 4},
            target_mode="participa"
        ))
        self.wait()
        self.play(Blink(Ale))
        self.play(RemueveDialogo(Ale))       
        self.play(FadeOut(Ale))
        self.wait(0.5)

class Conversacion(Scene):
    def construct(self):
        conversation = Conversation(self)
        conversation.add_bubble("Hola!")
        self.wait(2)
        conversation.add_bubble("Hola, qué tal?")
        self.wait(2)
        conversation.add_bubble("Esta es mi primera animación de\\\\ conversación.")
        self.wait(3) # 41
        conversation.add_bubble("Está muy bien!")
        self.wait(2) # 48
        conversation.add_bubble("Gracias! :D")
        self.wait(2)
        self.play(FadeOut(conversation.dialog[:]))
        self.wait()

class EscenaMusica(MusicalScene):
    def construct(self):
        self.teclado_transparente=self.definir_teclado(4,self.prop,0).set_stroke(None,0)
        self.teclado_base=self.definir_teclado(4,self.prop,1)
        self.teclado_base.move_to(ORIGIN+DOWN*3)
        self.teclado_transparente.move_to(ORIGIN+DOWN*3)

        self.wait(0.3)
        self.agregar_escenario()
        self.mandar_frente_sostenido(4,self.teclado_base)
        self.mandar_frente_sostenido(4,self.teclado_transparente)

        self.primer_paso(simbolos_faltantes=[14,15,16,17,18,19,20,21])
        self.progresion(0,run_time=2)
        self.progresion_con_desfase(paso=1,desfase=22,y1=8,x2=8,y2=16,run_time=2)
        self.progresion_con_desfase(paso=2,desfase=30,y1=8,x2=10,y2=18,simbolos_faltantes=[38,39],run_time=2)

        self.intervalos()

        self.salida_teclado()
        
        self.wait(2)


    def importar_partitura(self):
        self.partitura=TextMobject("""
                \\begin{music}
                \\parindent10mm
                \\instrumentnumber{1}
                \\setname1{} 
                \\setstaffs1{2}
                \\setclef16
                \\startextract
                \\NOTEs\\zql{'C}\\qu G|\\zql{e}\\qu j\\en
                \\NOTEs\\zql{F}\\qu{''A}|\\zql{f}\\qu{'c}\\en
                \\NOTEs\\zql{G}\\qu{'G}|\\zql{d}\\qu{'b}\\en
                \\NOTEs\\zhl{C}\\hu{'G}|\\zhl{e}\\hu{'c}\\en
                \\endextract
                \\end{music}
            """,color=BLACK).shift(UP)

    def definir_cambios_notas(self):
        self.cambios_notas=[[[
                (   14, 15, 17, 16, 18, 19, 21, 20, ),
                (   22, 23, 25, 24, 26, 27, 29, 28, )
        ]]]

        self.teclas=[[29,37,28,36],
                    [30,35,29,36],
                    [27,36,26,35],
                    [1,20,28,36]]

    def definir_colores(self):
        
        self.colores_notas=[
                       ([21,20,29,28,36,37,47,46],self.colores[3]),
                       ([18,19,26,27,34,35,44,45],self.colores[2]),
                       ([17,16,25,24,33,32,43,42],self.colores[1]),
                       ([14,15,22,23,30,31,40,41,38,39],self.colores[0])
                      ]


    def definir_cifrado(self):
        cifrado=VGroup(
            TexMobject("\\mbox{I}_3^6",color=BLACK),
            TexMobject("\\mbox{IV}_3^4",color=BLACK),
            TexMobject("\\mbox{V}",color=BLACK),
            TexMobject("\\mbox{I}",color=BLACK)
            )
        bajo=[15,23,31,41]
        cifrado[0].next_to(self.partitura[15],DOWN,buff=1.3)
        cords_x=[*[self.partitura[w].get_center()[0]for w in bajo]]
        
        for i in range(1,4):
            cifrado[i].move_to(cifrado[i-1])
            dis=cords_x[i]-cords_x[i-1]
            cifrado[i].shift(np.array([dis,0,0]))

        self.cifrado=cifrado        

    def agregar_escenario(self):
        self.grupoA=VGroup(*[self.partitura[cont]for cont in [12,13]])
        self.linea=Line(self.teclado_transparente[0].get_top(),self.teclado_transparente[-1].get_top()).set_stroke(BLACK,width=1.5)
        self.play(*[LaggedStart(GrowFromCenter, self.partitura[i],run_time=2)for i in range(1,11)],
            LaggedStart(DrawBorderThenFill,self.teclado_transparente),LaggedStart(DrawBorderThenFill,self.teclado_base)
            )
        self.play(*[GrowFromCenter(x)for x in self.grupoA],FadeIn(self.linea))



    def intervalos(self):
        i6m_v=self.intervalo_v(21,15,"6-")
        i5J_v=self.intervalo_v(25,29,"5\\rm J",direccion=RIGHT)

        i2m_h=self.intervalo_h(17,25,"2+")
        i5J_h=self.intervalo_h(15,23,"5\\rm J")

        self.ap_inter_v(i6m_v)
        self.wait()
        self.play(ReplacementTransform(i6m_v.copy(),i5J_v))
        self.wait()
        self.ap_inter_h(i2m_h)
        self.wait()
        self.play(ReplacementTransform(i2m_h,i5J_h))
        self.wait()
        
    def salida_teclado(self):
        self.play(*[
                ApplyMethod(
                    self.teclado_transparente[i].set_fill,None,0
                    )
                for i,color in self.cambios_colores_teclas[3]
                ],
                FadeOut(self.linea),
            run_time=1
        )
        for i in range(len(self.teclado_transparente)):
            self.remove(self.teclado_transparente[i])
        for i in range(len(self.teclado_base)):
            self.remove(self.teclado_base[i])
        self.play(
            LaggedStart(FadeOutAndShiftDown,self.teclado_base,lambda m: (m, DOWN),run_time=1),
            LaggedStart(FadeOutAndShiftDown,self.teclado_transparente,lambda m: (m, DOWN),run_time=1)
            )

class Escala2(MusicalScene2):
    def setup(self):
        self.definir_teclados(1,ORIGIN,0.6)
        self.definir_teclas(1)

    def construct(self):
        self.agregar_escenario()
        self.mover_teclas()
        self.copiar_teclado()
        self.wait()
        #self.mostrar_notas(self.teclado_base)


    def agregar_escenario(self):
        #self.linea=Line(self.teclado_transparente[0].get_top(),self.teclado_transparente[-1].get_top()).set_stroke(BLACK,width=1.5)
        self.play(
            LaggedStart(FadeInFromDown,self.teclado_base)
            )
        self.wait()
        #self.play(FadeIn(self.linea))

    def mover_teclas(self):
        self.teclado_base2=self.teclado_base.copy()
        for i in range(1,len(self.teclado_base2)):
            self.teclado_base2[i].next_to(self.teclado_base2[i-1],RIGHT,buff=0)
        self.teclado_base2.move_to(ORIGIN)

        self.play(ReplacementTransform(self.teclado_base,self.teclado_base2),run_time=3.4)
        self.teclado_base3=self.teclado_base2.copy()
        self.wait()

        self.teclado_base3.move_to(np.array([0,-1.65,0]))
        for i in range(1,len(self.teclado_base3)):
            if i in [1,3,6,8,10]:
                self.teclado_base3[i].shift(UP*abs(self.teclado_base3[i].get_height()-self.teclado_base3[i-1].get_height())/2+UP*0.3*i)
            else:
                self.teclado_base3[i].shift(UP*0.3*i)

        self.play(ReplacementTransform(self.teclado_base2,self.teclado_base3),run_time=3)
        self.teclado_base=self.teclado_base3
        
        #self.teclado_base.move_to(ORIGIN)
        #self.add(Texto("%f\\\\%f"%(self.teclado_base[0].get_center()[0],self.teclado_base[0].get_center()[1]),color=RED))

    def copiar_teclado(self):
        self.play(self.teclado_base.scale,0.5)
        self.teclado_superior1=self.teclado_base.copy()
        self.teclado_superior1.next_to(self.teclado_base,RIGHT,buff=0).shift(UP*(self.teclado_base.get_height()/2+0.2))
        self.teclado_inferior1=self.teclado_base.copy()
        self.teclado_inferior1.next_to(self.teclado_base,LEFT,buff=0).shift(DOWN*(self.teclado_base.get_height()/2+0.2))
        self.play(ReplacementTransform(self.teclado_base.copy(),self.teclado_superior1,path_arc=PI),
            ReplacementTransform(self.teclado_base.copy(),self.teclado_inferior1,path_arc=PI),run_time=2.5)
        self.teclado_superior2=self.teclado_superior1.copy()
        self.teclado_inferior2=self.teclado_inferior1.copy()
        self.teclado_superior2.next_to(self.teclado_superior1,RIGHT,buff=0).shift(UP*(self.teclado_base.get_height()/2+0.2))
        self.teclado_inferior2.next_to(self.teclado_inferior1,LEFT,buff=0).shift(DOWN*(self.teclado_base.get_height()/2+0.2))
        self.play(ReplacementTransform(self.teclado_inferior1.copy(),self.teclado_inferior2,path_arc=PI),
            ReplacementTransform(self.teclado_superior1.copy(),self.teclado_superior2,path_arc=PI),run_time=2.5)

        self.teclado_superior3=self.teclado_superior2.copy()
        self.teclado_inferior3=self.teclado_inferior2.copy()
        self.teclado_superior3.next_to(self.teclado_superior2,RIGHT,buff=0).shift(UP*(self.teclado_base.get_height()/2+0.2))
        self.teclado_inferior3.next_to(self.teclado_inferior2,LEFT,buff=0).shift(DOWN*(self.teclado_base.get_height()/2+0.2))
        self.play(ReplacementTransform(self.teclado_inferior2.copy(),self.teclado_inferior3,path_arc=PI),
            ReplacementTransform(self.teclado_superior2.copy(),self.teclado_superior3,path_arc=PI),run_time=2.5)


        self.teclado_superior4=self.teclado_superior3.copy()
        self.teclado_inferior4=self.teclado_inferior3.copy()
        self.teclado_superior4.next_to(self.teclado_superior3,RIGHT,buff=0).shift(UP*(self.teclado_base.get_height()/2+0.2))
        self.teclado_inferior4.next_to(self.teclado_inferior3,LEFT,buff=0).shift(DOWN*(self.teclado_base.get_height()/2+0.2))
        self.play(ReplacementTransform(self.teclado_inferior3.copy(),self.teclado_inferior4,path_arc=PI),
            ReplacementTransform(self.teclado_superior3.copy(),self.teclado_superior4,path_arc=PI),run_time=2.5)

        self.teclado_escala=VGroup(self.teclado_base,
            self.teclado_superior1,
            self.teclado_superior2,
            self.teclado_superior3,
            self.teclado_superior4,
            self.teclado_inferior1,
            self.teclado_inferior2,
            self.teclado_inferior3,
            self.teclado_inferior4)

        self.play(self.teclado_escala.shift,np.array([2,1.8,0]),rate_func=there_and_back,run_time=3)
        self.play(self.teclado_escala.shift,np.array([-2,-1.8,0]),rate_func=there_and_back,run_time=3)




        self.teclado_3octavas=self.definir_octava_back(9).move_to(ORIGIN).scale(0.4)
        self.wait()

        
        self.play(
            *[ReplacementTransform(self.teclado_inferior4[i4],self.teclado_3octavas[i4])for i4 in range(len(self.teclado_inferior1))],
            *[ReplacementTransform(self.teclado_inferior3[i3],self.teclado_3octavas[i3+12])for i3 in range(len(self.teclado_inferior1))],
            *[ReplacementTransform(self.teclado_inferior2[i2],self.teclado_3octavas[i2+24])for i2 in range(len(self.teclado_inferior1))],
            *[ReplacementTransform(self.teclado_inferior1[i1],self.teclado_3octavas[i1+36])for i1 in range(len(self.teclado_inferior1))],
            *[ReplacementTransform(self.teclado_base[j],self.teclado_3octavas[j+48])for j in range(len(self.teclado_base))],
            *[ReplacementTransform(self.teclado_superior1[k1],self.teclado_3octavas[k1+60])for k1 in range(len(self.teclado_superior1))],
            *[ReplacementTransform(self.teclado_superior2[k2],self.teclado_3octavas[k2+72])for k2 in range(len(self.teclado_superior1))],
            *[ReplacementTransform(self.teclado_superior3[k3],self.teclado_3octavas[k3+84])for k3 in range(len(self.teclado_superior1))],
            *[ReplacementTransform(self.teclado_superior4[k4],self.teclado_3octavas[k4+96])for k4 in range(len(self.teclado_superior1))])
            #'''

        self.play(self.teclado_3octavas.shift,LEFT*3,rate_func=there_and_back,run_time=3)
        self.play(self.teclado_3octavas.shift,RIGHT*3,rate_func=there_and_back,run_time=3)

class EscenaMusica2(MusicalScene):
    CONFIG = {"include_sound": True}
    def construct(self):
        self.teclado_transparente=self.definir_teclado(4,self.prop,0).set_stroke(None,0)
        self.teclado_base=self.definir_teclado(4,self.prop,1)
        self.teclado_base.move_to(ORIGIN+DOWN*3)
        self.teclado_transparente.move_to(ORIGIN+DOWN*3)

        self.agregar_escenario()
        self.primer_paso(simbolos_faltantes=[14,15,16,17,18,19,20,21])
        self.progresion(0,run_time=1)
        self.progresion_con_desfase(paso=1,desfase=22,y1=8,x2=8,y2=16,run_time=1)
        self.progresion_con_desfase(paso=2,desfase=30,y1=8,x2=10,y2=18,simbolos_faltantes=[38,39],run_time=1)

        self.intervalos()
        


    def importar_partitura(self):
        self.partitura=TextMobject("""
                \\begin{music}
                \\parindent10mm
                \\instrumentnumber{1}
                \\setname1{} 
                \\setstaffs1{2}
                \\setclef16
                \\startextract
                \\NOTEs\\zql{'C}\\qu G|\\zql{e}\\qu j\\en
                \\NOTEs\\zql{F}\\qu{''A}|\\zql{f}\\qu{'c}\\en
                \\NOTEs\\zql{G}\\qu{'G}|\\zql{d}\\qu{'b}\\en
                \\NOTEs\\zhl{C}\\hu{'G}|\\zhl{e}\\hu{'c}\\en
                \\endextract
                \\end{music}
            """,color=BLACK).shift(UP).scale(0.8)

    def definir_cambios_notas(self):
        self.cambios_notas=[[[
                (   14, 15, 17, 16, 18, 19, 21, 20, ),
                (   22, 23, 25, 24, 26, 27, 29, 28, )
        ]]]
        tt=self.definir_notas(4)
        self.teclas=[[tt[0][1],tt[7][1],28,36],
                    [tt[5][0],tt[9][1],tt[5][2],tt[0][3]],
                    [tt[7][0],tt[7][1],tt[2][2],tt[11][2]],
                    [tt[0][0],tt[7][1],28,36]]

    def definir_colores(self):
        
        self.colores_notas=[
                       ([21,20,29,28,36,37,47,46],self.colores[3]),
                       ([18,19,26,27,34,35,44,45],self.colores[2]),
                       ([17,16,25,24,33,32,43,42],self.colores[1]),
                       ([14,15,22,23,30,31,40,41,38,39],self.colores[0])
                      ]


    def definir_cifrado(self):
        cifrado=VGroup(
            TexMobject("\\mbox{I}",color=BLACK),
            TexMobject("\\mbox{IV}",color=BLACK),
            TexMobject("\\mbox{V}",color=BLACK),
            TexMobject("\\mbox{I}",color=BLACK)
            )
        bajo=[15,23,31,41]
        cifrado[0].next_to(self.partitura[15],DOWN,buff=1.3)
        cords_x=[*[self.partitura[w].get_center()[0]for w in bajo]]
        
        for i in range(1,4):
            cifrado[i].move_to(cifrado[i-1])
            dis=cords_x[i]-cords_x[i-1]
            cifrado[i].shift(np.array([dis,0,0]))

        self.cifrado=cifrado        

    def agregar_escenario(self):
        self.grupoA=VGroup(*[self.partitura[cont]for cont in [12,13]])


        self.mandar_frente_sostenido(4,self.teclado_base)
        self.mandar_frente_sostenido(4,self.teclado_transparente)

        self.play(*[LaggedStart(GrowFromCenter, self.partitura[i],run_time=2)for i in range(1,11)],
            LaggedStart(DrawBorderThenFill,self.teclado_base),LaggedStart(DrawBorderThenFill,self.teclado_transparente),
            *[GrowFromCenter(x)for x in self.grupoA]
            )



    def intervalos(self):
        i6m_v=self.intervalo_v(21,15,"8\\rm J")
        i5J_v=self.intervalo_v(25,29,"3-",direccion=RIGHT)

        i2m_h=self.intervalo_h(17,25,"2+")
        i5J_h=self.intervalo_h(15,23,"5\\rm J")

        self.ap_inter_v(i6m_v)
        self.play(ReplacementTransform(i6m_v.copy(),i5J_v))
        self.ap_inter_h(i2m_h)
        self.play(ReplacementTransform(i2m_h,i5J_h))
        
    def salida_teclado(self):
        self.play(*[
                ApplyMethod(
                    self.teclado_transparente[i].set_fill,None,0
                    )
                for i,color in self.cambios_colores_teclas[3]
                ],
            run_time=1
        )
        self.remove_foreground_mobjects(self.teclado_transparente)
        self.remove_foreground_mobjects(self.teclado_base)
        self.remove(self.teclado_transparente)
        self.mandar_frente_sostenido_parcial(4,self.teclado_base)
        self.play(
            *[LaggedStart(FadeOutAndShiftDown,objeto,run_time=1)for objeto in self.mobjects],
            )
        cuadro_negro=Rectangle(width=FRAME_WIDTH,height=FRAME_HEIGHT).set_fill(BLACK,0).set_stroke(None,0)
        self.add_foreground_mobject(cuadro_negro)
        self.play(cuadro_negro.set_fill,None,1)
