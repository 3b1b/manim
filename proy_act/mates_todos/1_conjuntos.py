from big_ol_pile_of_manim_imports import *

h_resulution=810
v_frame_rate=5
video_parameters=[
    ("pixel_height",h_resulution),
    ("pixel_width",int(h_resulution*16/9)),
    ("frame_rate",v_frame_rate)
]
for v_property,v_value in video_parameters:
    LOW_QUALITY_CAMERA_CONFIG[v_property]=v_value

# python -m manim proy_act\mates_todos\2_conjuntos.py -pl
class Texto1(CheckSVG):
    CONFIG={
    #"set_size":"height",
    "stroke_width":0.1,
    "svg_type":"text",
    "show_numbers":True
    }
    def import_text(self):
        return Texto("""   
\\textit{``Es un enunciado matemático,\\\\
que en ciertos contextos,\\\\
se considera como verdadero\\\\
sin necesidad de ser demostrado.''}
        	""")

class Texto2(CheckSVG):
    CONFIG={
    #"set_size":"height",
    "stroke_width":0.1,
    "svg_type":"text",
    "show_numbers":True
    }
    def import_text(self):
        return Texto("""
¡NO ES UN ENUNCIADO \\underline{TAN}\\\\
\\underline{EVIDENTE} QUE NO REQUIERE \\\\
DEMOSTRACIÓN!
        	""")

class QueEsTeoriaConjuntos(Scene):
    def construct(self):
        self.importar_objetos()
        self.no_hay_una_sola_teoria()
        self.teoria_nbg_extensionalidad()
        self.teoria_nbg_conjunto()


    def importar_objetos(self):
        self.estrella=SVGMobject("estrella").set_height(0.5).set_fill(YELLOW).set_stroke(None,0)
        self.cuadrado=Square().set_height(0.5).set_fill(BLUE,1).set_stroke(None,0)
        self.circulo=Circle().set_height(0.5).set_fill(ORANGE,1).set_stroke(None,0)

    def no_hay_una_sola_teoria(self):
        print("Inicia: no_hay_una_sola_teoria")
        vt=2
        #-----------------Textos-------------------------
        ##Titulo.........................................
        titulo=Tikz("""
            \\begin{tikzpicture}[pencildraw/.style={decorate,
            decoration={random steps,segment length=0.8pt,amplitude=0.3pt}}]
                \\node[pencildraw,draw] {\\sc Teoría de Conjuntos};
            \\end{tikzpicture}
              """).scale(2)
        #tit=TikzMobject(tikz,stroke_width=2,fill_opacity=.1)
        titulo[1:].set_stroke(None,0).set_fill(WHITE,1)
        ##................................................
        texto1a=Texto("\\ECFAugie No existe una sóla teoría de conjuntos.")
        texto1b=VGroup(
        		Texto("$\\blacktriangleright$ \\ECFAugie Zermelo-Fraenkel"),
        		Texto("$\\blacktriangleright$ \\ECFAugie Neumann-Bernays-Gödel"),
        		Texto("$\\blacktriangleright$ \\ECFAugie Morse-Kelley"),
        		Texto("$\\blacktriangleright$ \\ECFAugie Kaye-Foster"),
        		Texto("$\\blacktriangleright$ \\ECFAugie Mac Lane"),
        		Texto("$\\blacktriangleright$ \\ECFAugie Kripke-Platek"),
        		Formula("\\vdots")
        	).arrange_submobjects(DOWN,aligned_edge=LEFT).next_to(texto1a,DOWN,buff=0.2).shift(UP*2)
        c=0
        for i in texto1b:
            cont=len(texto1b)
            if c==cont-1:
                break
            i[0].set_color(YELLOW_B)
            c+=1
        texto1c=Texto("\\sc ¿{\\ECFAugie Teorías axiomáticas}?").scale(2)
        pc1=texto1c[0].fade(1)
        pc2=texto1c[-1].fade(1)
        texto1d=VGroup(
        				Texto("$\\bullet$ \\ECFAugie Axioma 1"),
        				Texto("$\\bullet$ \\ECFAugie Axioma 2"),
        				Texto("$\\bullet$ \\ECFAugie Axioma 3"),
        				Texto("$\\bullet$ \\ECFAugie Axioma 4"),
        				Formula("\\vdots")
        			).arrange_submobjects(DOWN,aligned_edge=LEFT)
        c=0
        for i in texto1d:
            cont=len(texto1d)
            if c==cont-1:
                break
            i[0].set_color(PURPLE)
            c+=1
        lista_elementos=VGroup(
        				Texto("$\\bullet$ \\ECFAugie Enunciado 1"),
        				Texto("$\\bullet$ \\ECFAugie Enunciado 2"),
        				Texto("$\\bullet$ \\ECFAugie Enunciado 3"),
        				Texto("$\\bullet$ \\ECFAugie Enunciado 4"),
        				Formula("\\vdots")
        			).arrange_submobjects(DOWN,aligned_edge=LEFT)
        c=0
        for i in lista_elementos:
            cont=len(lista_elementos)
            if c==cont-1:
                break
            i[0].set_color(PURPLE)
            c+=1
        texto1e=Texto("\\sc ¿{\\ECFAugie Axioma}?")
        texto1f=Texto("\\sc ¿{\\ECFAugie Qué es un Axioma}?").scale(1.5).to_edge(UP)
        texto1g=Texto("""   
\\textit{``Es un enunciado matemático,\\\\
que en ciertos contextos,\\\\
se considera como verdadero\\\\
sin necesidad de ser demostrado.''}
        	""").scale(1.3)
        texto1g[6:15].set_color(RED)
        texto1g[48:59].set_color(RED_B)
        texto1h=Texto("""
¡NO ES UN ENUNCIADO \\underline{TAN}\\\\
\\underline{EVIDENTE} QUE NO REQUIERE \\\\
DEMOSTRACIÓN!
        	""").scale(1.4).shift(LEFT*13)
        texto1h[1:5].set_color(RED)
        texto1h[16:29].set_color(BLUE)
        #
        #-------------------Objetos auxiliares
        cuadro_negro=Rectangle(width=self.camera.get_pixel_width(),height=self.camera.get_pixel_height(),color=BLACK).fade(0.1)
        cuadro_negro.move_to(ORIGIN)
        #---------------------------------------------------------
        self.play(Escribe(titulo[1:]),Write(titulo[0]),run_time=3)
        self.wait(vt)
        self.play(titulo.scale,0.4,titulo.to_corner,UL)
        self.wait(vt)

        self.play(Escribe(texto1a))
        self.wait(vt)
        self.play(texto1a.shift,UP*2,
        		  LaggedStart(FadeIn,texto1b))
        self.wait(vt)
        self.play(*[ReplacementTransform(texto[:],texto1c[1:-1])for texto in texto1b])
        self.wait(vt)
        pc1.fade(0)
        pc2.fade(0)
        self.play(texto1a.fade,1,
        			Write(pc1),Write(pc2))
        self.wait(vt)
        self.play(texto1c.shift,UP*2,texto1c[0].fade,1,texto1c[-1].fade,1)
        self.wait(vt)
        texto1d.next_to(texto1c[1:-1],DOWN)
        self.play(LaggedStart(Escribe,texto1d))
        self.wait(vt)
        self.play(FadeIn(cuadro_negro))
        self.wait(vt)
        self.play(Escribe(texto1f))
        self.play(Escribe(texto1g))
        self.wait(vt)
        self.play(texto1g.shift,RIGHT*13,texto1h.shift,RIGHT*13)
        self.wait(vt)
        self.play(
        		texto1g.fade,1,
        		texto1h.fade,1,
        		texto1f.fade,1,
        		cuadro_negro.fade,1,
        		#texto1d.fade,1,
        		#texto1c.fade,1
        	)
        self.wait(vt)
        for i in range(len(lista_elementos)):
            lista_elementos[i].move_to(texto1d[i])
        self.play(*[
            ReplacementTransform(texto1d[i],lista_elementos[i])
            for i in range(len(lista_elementos))
        ])
        self.wait(vt)
        self.texto1c=texto1c
        self.lista_elementos=lista_elementos
        self.titulo=titulo
        print("Termina: no_hay_una_sola_teoria")

    def teoria_nbg_extensionalidad(self):
        print("Empieza: teoria_nbg_extensionalidad")
        grilla=Grilla().fade(0.5)
        #self.add_foreground_mobject(grilla)
        vt=2
        #Textos---------------------------------------------------------
        texto2a=Texto("\\sc Teoría Neumann-Bernays-Gödel (NBG)")
        nombra_elementos=Texto("\\ECFAugie Elementos de\\\\\\ECFAugie la Clase $A$")
        claseA=Texto("\\ECFAugie Clase $A$")
        e_cA=Formula("A",color=BLACK).set_height(0.6)
        e_cB=Formula("B",color=BLACK).set_height(0.6)
        A_igual_B=Formula("A","=","B").scale(1.5)
        A_igual_B_copy=A_igual_B.copy()
        axioma_1=Formula("\\text{\\ECFAugie Axioma de Extensionalidad:}","A","=","B","\\Leftrightarrow \\forall x: x\\in A \\syx x\\in B")
        #Objetos--------------------------------------------------------
        cA=Caja(ancho=4).move_to(ORIGIN)
        cA.nota=Nota1().set_height(1).move_to(cA)
        cB=Caja(ancho=4,stroke_color=BLUE_B,fill_color=BLUE_B).move_to(ORIGIN-LEFT*3.2+DOWN*2)
        cB.nota=Nota1().set_height(1).move_to(cB)
        #Animaciones----------------------------------------------------
        self.play(
        		self.texto1c.fade,1,
        		self.lista_elementos.fade,1
        	)
        texto2a=escribe_texto(self,texto2a)
        self.wait(vt)
        self.play(texto2a.scale,0.8,texto2a.to_corner,UL,texto2a.shift,UP*0.25,texto2a.set_fill,None,0.3,
                    self.titulo.shift,UP*2)
        self.wait(vt)
        self.play(DrawBorderThenFill(cA))
        self.play(FadeInFrom(cA.nota,UP))

        e_cA.move_to(cA.nota)
        claseA.next_to(cA,UP,buff=0.2)
        cA.estrella=self.estrella.copy().move_to(cA).shift(LEFT+UP*0.5).scale(1.2)
        cA.circulo=self.circulo.copy().move_to(cA).shift(RIGHT+UP*0.5).scale(1.2)
        cA.cuadrado=self.cuadrado.copy().move_to(cA).shift(-UP*0.5).scale(1.2)
        cA.elementos=VGroup(cA.estrella,cA.circulo,cA.cuadrado)

        self.play(Write(e_cA),Escribe(claseA))

        cA.add(cA.nota,e_cA)
        self.add_foreground_mobject(cA)
        self.add(cA.elementos)
        #cA.add(cA.elementos)

        self.play(abrir_caja(cA),FadeOut(claseA))
        self.play(cA.elementos.shift,UP*2)
        self.wait(vt)
        nombra_elementos.next_to(cA.elementos,RIGHT)
        self.play(Escribe(nombra_elementos))
        self.wait(vt)
        self.play(Escribe(nombra_elementos),rate_func=lambda t: smooth(1-t))
        self.play(cA.elementos.shift,-UP*2)
        self.play(VGroup(cA,cA.elementos).shift,LEFT*3.2+DOWN*2)

        cB.elementos=cA.elementos.copy().move_to(cB)
        self.add(cB)
        cB.generate_target()
        cB.shift(RIGHT*8)

        self.play(MoveToTarget(cB))
        self.play(FadeInFrom(cB.nota,UP))
        e_cB.move_to(cB.nota)
        self.play(Write(e_cB))
        self.wait()

        cB.add(cB.nota,e_cB)
        self.add_foreground_mobject(cB)
        self.add(cB.elementos)

        self.play(abrir_caja(cB))
        self.wait(vt)
        self.play(
            cA.elementos.shift,UP*3,
            cB.elementos.shift,UP*3
        )
        self.wait(vt)
        for i in range(len(cA.elementos)):
            self.play(
                cA.elementos[i].scale,2,
                cB.elementos[i].scale,2,
                rate_func=there_and_back,
                #run_time=3
            ) 
            self.wait(0.5)  #--------------------Espera
        e_cA_copy=e_cA.copy()
        e_cB_copy=e_cB.copy()
        self.add_foreground_mobjects(e_cA_copy,e_cB_copy)
        self.play(
            ReplacementTransform(e_cA_copy[:],A_igual_B[0]),
            ReplacementTransform(e_cB_copy[:],A_igual_B[2]),
            Write(A_igual_B[1]),run_time=3
        )
        self.remove_foreground_mobjects(e_cA_copy,e_cB_copy)
        self.remove(e_cA_copy,e_cB_copy)
        self.remove_foreground_mobjects(A_igual_B[0],A_igual_B[2])
        self.wait(vt)
        

        axioma_1.next_to(texto2a,DOWN,buff=0.2,aligned_edge=LEFT)
        axioma_1[1:].shift(RIGHT*0.2)

        self.play(
            ReplacementTransform(A_igual_B[0],axioma_1[1]),
            ReplacementTransform(A_igual_B[1],axioma_1[2]),
            ReplacementTransform(A_igual_B[2],axioma_1[3]),
            )
        self.play(Escribe(axioma_1[0]),Escribe(axioma_1[4]))
        self.remove(A_igual_B)
        self.add(axioma_1[1][0:3])
        self.wait(vt)
        self.play(
            cB.elementos.shift,DOWN*3
        )
        self.play(cerrar_caja(cB))
        self.play(
            cB.shift,RIGHT*7,
            cB.elementos.shift,RIGHT*7,
        )

        self.wait(vt)
        self.play(
            cB.shift,-RIGHT*7,
        )
        cB.estrella1=self.estrella.copy().shift(LEFT+UP*0.5).scale(1.2)
        cB.estrella2=self.estrella.copy().shift(LEFT+DOWN*0.5).scale(1.2)
        cB.circulo=self.circulo.copy().shift(RIGHT+UP*0.5).scale(1.2)
        cB.cuadrado=self.cuadrado.copy().shift(RIGHT+DOWN*0.5).scale(1.2)
        cB.elementos2=VGroup(cB.estrella1,cB.estrella2,cB.circulo,cB.cuadrado)
        cB.elementos2.move_to(cB.nota)
        
        self.play(abrir_caja(cB))
        self.play(cB.elementos2.shift,UP*3)
        self.wait(vt)
        self.play(
            cB.estrella1.scale,1.8,
            cB.estrella2.scale,1.8,
            cA.estrella.scale,1.8,
            rate_func=there_and_back
        )
        self.wait(vt)

        e_cA_copy=e_cA.copy()
        e_cB_copy=e_cB.copy()
        self.add_foreground_mobjects(e_cA_copy,e_cB_copy)
        self.play(
            ReplacementTransform(e_cA_copy[:],A_igual_B_copy[0]),
            ReplacementTransform(e_cB_copy[:],A_igual_B_copy[2]),
            Write(A_igual_B_copy[1]),run_time=3
        )
        self.remove_foreground_mobjects(e_cA_copy,e_cB_copy)
        self.remove(e_cA_copy,e_cB_copy)
        self.remove_foreground_mobjects(A_igual_B_copy[0],A_igual_B_copy[2])
        self.wait(vt)

        linea_ramark=Line(axioma_1[4][1].get_corner(DL),axioma_1[4].get_corner(DR)).shift(DOWN*0.1).set_color(RED)

        self.play(GrowFromCenter(linea_ramark))
        self.wait(vt)


        c1=cB.cuadrado.copy()
        c2=cB.circulo.copy()
        c3=cB.estrella2.copy()
        c4=cB.cuadrado.copy()
        c5=cB.cuadrado.copy()
        self.play(
            c1.shift,LEFT,
            c2.shift,LEFT,
            c3.shift,DOWN,
            c4.shift,DOWN,
            c5.shift,DOWN+LEFT,
            )
        self.wait(vt)
        self.play(Indicate(A_igual_B_copy))
        self.wait(vt)
        self.play(
            *[
            Flash(objeto)
            for objeto in [c1,c2,c3,c4,c5,cB.estrella1,cB.estrella2,cB.circulo,cB.cuadrado]
            ],
            *[
                FadeOut(objeto,run_time=0.1)
                for objeto in [c1,c2,c3,c4,c5,cB.estrella1,cB.estrella2,cB.circulo,cB.cuadrado]
            ],
            FadeOut(A_igual_B_copy),
            FadeOut(axioma_1),
            FadeOut(linea_ramark),
            cerrar_caja(cB)
        )
        self.wait(vt)
        self.play(
            cB.shift,RIGHT*7,
            cA.shift,RIGHT*3.5,
            cA.elementos.shift,RIGHT*3.5,
        )
        self.wait(vt)

        cA.remove(cA.nota,e_cA)
        self.cA=cA
        self.cA.elementos=cA.elementos
        self.cA.nota=cA.nota
        self.e_cA=e_cA
        print("Termina: teoria_nbg_extensionalidad")

    def teoria_nbg_conjunto(self):
        print("Empieza: teoria_nbg_conjunto")
        grilla=Grilla().fade(0.5)
        #self.add_foreground_mobject(grilla)
        vt=2
        #Pre definiciones-----------------------------------------------
        cA=self.cA
        cA.etiqueta=self.e_cA
        cA.nota=self.cA.nota
        cA.elementos=self.cA.elementos
        #Textos---------------------------------------------------------
        cC=Caja(ancho=5,alto=3,stroke_color=GREEN_B,fill_color=GREEN_B).move_to(cA)
        cC.etiqueta=Formula("C",color=BLACK).set_height(0.6)
        A_conjunto=Formula("A","\\text{ \\ECFAugie es un conjunto}")
        definicion=Formula("\\text{Definición: }","{\\rm cto}","A","\\equiv\\exists C: A\\in C").shift(UP*2).scale(1.5)
        #Objetos--------------------------------------------------------
        cC.nota=Nota1().set_height(1).move_to(cC.get_corner(UL))
        dx_c=cC.nota.get_height()*DOWN*1.1/2
        dy_c=cC.nota.get_width()*RIGHT*1.1/2
        cC.nota.shift(dx_c+dy_c)
        g_cA=VGroup(cA,cA.nota,cA.etiqueta)
        g_cC=VGroup(cC,cC.nota,cC.etiqueta)
        #Animaciones----------------------------------------------------
        cC.etiqueta.move_to(cC.nota)
        
        self.add_foreground_mobjects(cA,cA.nota,cA.etiqueta)
        self.play(cA.elementos.shift,DOWN*3)
        self.remove_foreground_mobjects(cA,cA.nota,cA.etiqueta)
        self.remove(cA.elementos)
        self.play(cerrar_caja(cA))
        self.play(DrawBorderThenFill(cC))
        self.play(FadeInFrom(cC.nota,UP))
        self.play(Write(cC.etiqueta))
        self.add_foreground_mobjects(cC,cC.nota,cC.etiqueta)
        self.play(cC.set_fill,None,0.5)
        self.wait(vt)

        self.play(
            ReplacementTransform(
                cA.etiqueta.copy()[:],A_conjunto[0]
            ),
            Escribe(A_conjunto[1])
        )
        self.wait(vt)
        self.play(
            ReplacementTransform(A_conjunto[0],definicion[2]),
            ReplacementTransform(A_conjunto[1],definicion[1]),
            Escribe(definicion[0]),
            Escribe(definicion[3]),
        )
        self.wait(vt)

