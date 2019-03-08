from big_ol_pile_of_manim_imports import *

class QueEsTeoriaConjuntos(Scene):
    def construct(self):
        self.importar_objetos()
        self.no_hay_una_sola_teoria()
        #self.teoria_nbg()


    def importar_objetos(self):
        self.estrella=SVGMobject("estrella").set_height(0.5).set_fill(YELLOW).set_stroke(None,0)
        self.cuadrado=Square().set_height(0.5).set_fill(BLUE,1).set_stroke(None,0)
        self.circulo=Circle().set_height(0.5).set_fill(ORANGE,1).set_stroke(None,0)

    def no_hay_una_sola_teoria(self):
        print("Inicia: no_hay_una_sola_teoria")
        vt=1
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
        texto1a=Texto("No existe una sóla teoría de conjuntos...")
        texto1b=VGroup(
        		Texto("$\\blacktriangleright$ Zermelo-Fraenkel"),
        		Texto("$\\blacktriangleright$ Neumann-Bernays-Gödel"),
        		Texto("$\\blacktriangleright$ Morse-Kelley"),
        		Texto("$\\blacktriangleright$ Kaye-Foster"),
        		Texto("$\\blacktriangleright$ Mac Lane"),
        		Texto("$\\blacktriangleright$ Kripke-Platek"),
        		Formula("\\vdots")
        	).arrange_submobjects(DOWN,aligned_edge=LEFT).next_to(texto1a,DOWN,buff=0.2).shift(UP*2)
        texto1c=Texto("\\sc ¿Teorías axiomáticas?").scale(2)
        pc1=texto1c[0].fade(1)
        pc2=texto1c[-1].fade(1)
        texto1d=VGroup(
        				Texto("$\\bullet$ Axioma 1"),
        				Texto("$\\bullet$ Axioma 2"),
        				Texto("$\\bullet$ Axioma 3"),
        				Texto("$\\bullet$ Axioma 4"),
        				Formula("\\vdots")
        			).arrange_submobjects(DOWN,aligned_edge=LEFT)
        lista_elementos=VGroup(
        				Texto("$\\bullet$ Elemento 1"),
        				Texto("$\\bullet$ Elemento 2"),
        				Texto("$\\bullet$ Elemento 3"),
        				Texto("$\\bullet$ Elemento 4"),
        				Formula("\\vdots")
        			).arrange_submobjects(DOWN,aligned_edge=LEFT)
        texto1e=Texto("\\sc ¿Axioma?")
        texto1f=Texto("\\sc ¿Qué es un Axioma?").scale(1.5).to_edge(UP)
        texto1g=Texto("""   
\\textit{``Es un enunciado matemático,\\\\
que en ciertos contextos,\\\\
se considera como verdadero\\\\
sin necesidad de ser demostrado.''}
        	""").scale(1.3)
        texto1h=Texto("""
¡NO ES UN ENUNCIADO \\underline{TAN}\\\\
EVIDENTE QUE NO REQUIERE \\\\
DEMOSTRACIÓN!
        	""").scale(1.4).shift(LEFT*13)
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
        self.play(*[
            ReplacementTransform(texto1c[i],lista_elementos[i])
            for i in range(len(lista_elementos))
        ])
        self.titulo=titulo
        print("Termina: no_hay_una_sola_teoria")

    def teoria_nbg(self):
        print("Empieza: teoria_nbg")
        grilla=Grilla().fade(0.5)
        self.add_foreground_mobject(grilla)
        vt=1
        #Textos---------------------------------------------------------
        texto2a=Texto("\\sc Teoría Neumann-Bernays-Gödel (NBG)")
        texto2b=Texto("{\\it Clases} = Cajas")
        e_cA=Formula("A")
        #Objetos--------------------------------------------------------
        cA=Caja()
        cA.nota=Nota1().set_height(1)
        #Animaciones----------------------------------------------------
        texto2a=escribe_texto(self,texto2a)
        self.wait(vt)
        self.play(texto2a.scale,0.8,texto2a.to_corner,UL,self.titulo.shift,UP*2)
        self.wait(vt)
        self.play(ShowCreation(cA))
        self.play(FadeInFrom(cA.nota,UP))
        self.wait(vt)

