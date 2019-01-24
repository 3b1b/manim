from big_ol_pile_of_manim_imports import *

class SVG1(PruebaSVG):
    CONFIG={
    "file":"pruebas/mus1",
    "escala":1.8,
    "grosor": 1,
    "mostrar_todos_numeros":True,
    "remover":[19,46,1],
    "direccion_numeros":RIGHT,
    "muestra_elementos":[19,46,1]
    }

class SVG2(PruebaSVG):
    CONFIG={
    "tipo_svg": "texto",
    "escala":3,
    "mostrar_todos_numeros":True,
    "remover":[7],
    "grosor":0,
    "direccion_numeros":RIGHT,
    "muestra_elementos":[8]
    }
    def importa_texto(self):
        return TexMobject("a+b+c+d=\\sqrt{x}")

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

	
class ImagenE(Scene):
    def construct(self):
        nota=Nota1()
        cinta=Cinta1()
        self.play(GrowFromCenter(nota))
        self.wait()
        self.play(GrowFromCenter(cinta))
        self.wait()
	
class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        square.flip(RIGHT)
        square.rotate(-3 * TAU / 8)
        circle.set_fill(PINK, opacity=0.5)

        self.play(ShowCreation(square))
        self.play(Transform(square, circle))
        self.play(FadeOut(square))


class WarpSquare(Scene):
    def construct(self):
        square = Square()
        self.play(ApplyPointwiseFunction(
            lambda point: complex_to_R3(np.exp(R3_to_complex(point))),
            square
        ))
        self.wait()


class WriteStuff(Scene):
    def construct(self):
        example_text = TextMobject(
            "This is a some text",color=WHITE,
            tex_to_color_map={"text": YELLOW}
        )
        example_tex = TexMobject(
            "\\sum_{k=1}^\\infty {1 \\over k^2} = {\\pi^2 \\over 6}",
        )
        group = VGroup(example_text, example_tex)
        group.arrange_submobjects(DOWN)
        group.set_width(FRAME_WIDTH - 2 * LARGE_BUFF)

        self.play(Write(example_text))
        self.play(Write(example_tex))
        self.wait()


class UdatersExample(Scene):
    def construct(self):
        decimal = DecimalNumber(
            0,
            show_ellipsis=True,
            num_decimal_places=3,
            include_sign=True,
        )
        square = Square().to_edge(UP)

        decimal.add_updater(lambda d: d.next_to(square, RIGHT))
        decimal.add_updater(lambda d: d.set_value(square.get_center()[1]))
        self.add(square, decimal)
        self.play(
            square.to_edge, DOWN,
            rate_func=there_and_back,
            run_time=5,
        )
        self.wait()
	
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
        
class Acentos(Scene):
    def construct(self):
        acentos_tradicional=TextMobject("Acento tradicional: \\'a \\~n").scale(2).to_edge(DOWN)
        acentos_moderno=TextMobject("Acento moderno: á ñ").scale(2).to_edge(UP)
        self.play(Write(acentos_tradicional))
        self.play(Write(acentos_moderno))
        self.wait()

class Cancel(Scene):
    def construct(self):
        example_text = TexMobject(
            "\\cancel{x^2}"
        ).scale(3)
        example_text[0:2].set_color(RED)
        self.play(Write(example_text[2:]))
        self.play(Write(example_text[0:2]))
        self.wait()
        
#Probar \\ECFAugie si puedes usar emerald
class AnimacionEscribe(Scene):
    def construct(self):
        esc_desv=TextMobject("Escribe y luego \\\\ se desvanece").scale(2)
        esc=TextMobject("Escribe").scale(3)
        self.play(Escribe_y_desvanece(esc_desv,color_orilla=GREEN_B,stroke_width=2,factor_desvanecimiento=8.5),run_time=4.5)
        self.play(Escribe(esc,color_orilla=YELLOW_B,stroke_width=1,factor_desvanecimiento=6))
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


class Dedo(Scene):
    def construct(self):
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

        self.play(DrawBorderThenFill(dedo))
        self.wait()
        self.play(ApplyMethod(dedo.scale, 1.5,rate_func=there_and_back))
        self.wait()


class Dedo2(Scene):
    def construct(self):
        ecuation=TexMobject("ax+b=0").scale(1)
        dedo = SVGMobject(
            file_name = "dedo",
            fill_opacity = 0,
            stroke_width = 1.5,
            height = 1,
            stroke_color = TT_TEXTO,
        ).flip()
        dedo.next_to(ecuation,RIGHT,buff=0.5)
        senhalar=ApplyMethod(dedo.shift, np.array([-0.3,0,0]),rate_func=there_and_back,run_time=0.7)
        self.play(Write(ecuation))
        self.play(LaggedStart(Write,dedo,submobject_mode = "lagged_start",rate_func=lambda t : smooth(t)),run_time=1.5)
        self.play(senhalar)

        self.wait()
        
class Redes(Scene):
    def construct(self):
        twitter = Twitter().set_fill("#12C0FF").set_stroke("#12C0FF").scale(0.6)
        facebook = Facebook().set_fill("#3C5A9A").set_stroke("#3C5A9A").scale(0.6)
        github = GitHub()
        youtube=YouTube().set_fill("#FE0000").set_stroke("#FE0000").scale(0.6)
        facebook.shift(LEFT*2)
        github.set_height(facebook.get_height()).scale(0.96)
        twitter.next_to(facebook,LEFT,buff=1)
        youtube.next_to(facebook,RIGHT,buff=1)
        github.next_to(youtube,RIGHT,buff=1)
        redes_s=VGroup(twitter,facebook,youtube,github)
        redes_s.move_to(ORIGIN)
        redes_f=redes_s.copy()
        redes_f.arrange_submobjects(
            DOWN, aligned_edge=LEFT, buff=0.4
            )
        texto=VGroup(
            TextMobject("\\tt twitter").match_color(twitter),
            TextMobject("\\tt facebook").match_color(facebook),
            TextMobject("\\tt youtube").match_color(youtube),
            TextMobject("\\tt github").match_color(github)
            )
        redes_f.to_edge(LEFT).scale(0.7).shift(LEFT*0.7)
        for i in range(len(texto)):
            texto[i].next_to(redes_f[i],RIGHT,buff=0.8)


        self.play(DrawBorderThenFill(redes_s),run_time=3)
        self.play(ReplacementTransform(redes_s,redes_f))
        self.wait(0.1)
        self.add_foreground_mobject(redes_f)
        circles=VGroup(*[Dot(redes_f[i].get_center(),color=WHITE,radius=twitter.get_width()*0.5).scale(0.9)for i in range(len(redes_f)-1)])
        texto.shift(RIGHT*2)
        punto=Dot(redes_f.get_center()).shift(RIGHT*2)
        vector=punto.get_center()[0]-redes_f.get_center()[0]
        circles.set_fill(None,0)
        self.add(circles)
        def update(grupo):
            for i in range(len(grupo)):
                grupo[i].move_to(redes_f[i].get_center())
                dif=(punto.get_center()[0]-grupo.get_center()[0])
                grupo.set_fill(WHITE,smooth(1-dif/vector))
            return grupo
        

        #self.play(FadeIn(circles))
        self.play(redes_f.shift,RIGHT*2,
            UpdateFromFunc(circles,update),
            *[Escribe(texto[i],color_orilla=texto[i].get_color(),factor_desvanecimiento=8,stroke_width=0.7)for i in range(len(texto))])
        circles.set_fill(WHITE,1)
        self.add(circles)
        redes_fc=redes_f.copy()
        redes_fc.set_fill(opacity=0)
        redes_fc.set_stroke(WHITE,3)
        redes_fc[-1].set_stroke(BLACK,1.5)
        
        
        for x in range(2):
            self.play(
                ShowPassingFlash(
                    redes_fc, 
                    time_width = 0.5,
                    run_time = 2,
                    rate_func=linear
                )
            )
        
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
        

#-------Funciones para Circuito
def imprimir_formula_paso_1(self,texto,escala,escala_inversa,direccion,excepcion,separacion):
    excepcion=0
    self.add(texto.scale(escala))
    contador = 0
    for j in range(len(texto)):
        elemento = TexMobject("%d" %contador)
        texto[j].set_color(RED)
        self.add(texto[j])
        elemento.set_fill(opacity=1)
        elemento.to_edge(UP)
        self.add(elemento)
        self.wait(0.02)
        elemento.set_fill(opacity=0)
        texto[j].set_color(WHITE)
        contador = contador + 1 

#exporta -s
def imprimir_formula_paso_2(self,texto,escala,escala_inversa,direccion,excepcion,separacion):
    texto.scale(escala).set_color(RED)
    self.add(texto)
    contador = 0
    for j in range(len(texto)):
        permiso_imprimir=True
        for w in excepcion:
            if j==w:
                permiso_imprimir=False
        if permiso_imprimir:
            self.add(texto[j].set_color("#808080"))
        contador = contador + 1

    contador=0
    for j in range(len(texto)):
        permiso_imprimir=True
        elemento = TexMobject("%d" %contador,color=WHITE)
        elemento.scale(escala_inversa)
        elemento.next_to(texto[j],direccion,buff=separacion)
        for w in excepcion:
            if j==w:
                permiso_imprimir=False
        if permiso_imprimir:
            self.add(elemento)
        contador = contador + 1 

def devolver_formula_excepcion(formula,excepcion):
    form=VGroup()
    for i in range(len(formula)):
        vt=True
        for e in excepcion:
            if i==e:
                vt=False
        if vt:
            form.add(formula[i])
    return form

def devolver_formula_adicion(formula,adicion):
    form=VGroup()
    for i in range(len(formula)):
        vt=False
        for e in adicion:
            if i==e:
                vt=True
        if vt:
            form.add(formula[i])
    return form

#------------

class Circuito(Scene):
    def construct(self):
        p_tex="""  \\begin{circuitikz}[american]
                    \\draw[ultra thin](-2,-2) to [vsourcesin,invert,f<=$5\\un{A}$,o-,l=$V$] (-2,2); 
                    \\draw[ultra thin](-2,2) to [R,v^=$ $,l_=$8\\un{k\\Omega}$,o-*] (0,2) to [cute inductor,v_=$ $,l^=$7\\un{H}$,*-*] (2,2);
                    \\draw[ultra thin](2,2) to [C,i<=$5\\un{A}$,l^=$8\\un{\\mu F}$] (2,-2) to[lamp,*-] (-2,-2);
                    \\draw[-stealth] ([shift=(20:1cm)]0,0) arc (20:300:1cm) node [above] {$i=5\\un{A}$};
                    \\end{circuitikz}"""
        tex_a=TikzMobject(p_tex,stroke_width=2,fill_opacity=0)
        tex_b=TikzMobject(p_tex,stroke_width=0,fill_opacity=1)
        tex_c=TikzMobject(p_tex,stroke_width=0,fill_opacity=1)
        excepcion=[
                        3,15,27,28,30,44,45,18,9,10,11,12,7,8,19,20,21,22,23,31,32,33,34,46,47,78,49,39,40,41,42,43,53,54,55,56,57,6,48,58,51,59,60
                    ]
        adicion1=[35,36,25,24]
        adicion2=[16,17,4,29]
        circ1=devolver_formula_excepcion(tex_a,excepcion)
        circ2=devolver_formula_adicion(tex_b,adicion1)
        circ3=devolver_formula_adicion(tex_c,adicion2)
        circ1.add(circ2).add(circ3)
        dots_black=VGroup(
            *[Dot(circ1[i].get_center(),radius = 0.07,color=BLACK)for i in [12,8,18]]
            )
        self.add_foreground_mobject(dots_black)
        ################
        light = AmbientLight(
                source_point=VectorizedPoint(tex_a[50].get_center()),
                num_levels=100,
            )
        corriente1=DashedLine(circ1[3].get_center()+UP*2.8,circ1[7].get_center(),
            dashed_segment_length=0.05,
            color = YELLOW,stroke_width = 5,
            stroke_color = YELLOW)
        corriente2=DashedLine(circ1[7].get_center(),circ1[12].get_center(),
            dashed_segment_length=0.05,
            color = YELLOW,stroke_width = 5,
            stroke_color = YELLOW)
        corriente3=DashedLine(circ1[12].get_center(),circ1[18].get_center(),
            dashed_segment_length=0.05,
            color = YELLOW,stroke_width = 5,
            stroke_color = YELLOW)
        corriente4=DashedLine(circ1[18].get_center(),circ1[3].get_center(),
            dashed_segment_length=0.05,
            color = YELLOW,stroke_width = 5,
            stroke_color = YELLOW)
        corriente5=DashedLine(circ1[3].get_center(),circ1[3].get_center()+UP*2.8,
            dashed_segment_length=0.05,
            color = YELLOW,stroke_width = 5,
            stroke_color = YELLOW)
        
        ################
        self.play(Write(circ1))
        self.play(  Succession(Animation, Mobject(), {"run_time" : 0.0001},
                    ShowCreationThenDestruction,corriente1,{"submobject_mode":"lagged_start","run_time" : 3}),
                    Succession(Animation, Mobject(), {"run_time" : 1},
                    ShowCreationThenDestruction,corriente2,{"submobject_mode":"lagged_start","run_time" : 3}),
                    Succession(Animation, Mobject(), {"run_time" : 2},
                    ShowCreationThenDestruction,corriente3,{"submobject_mode":"lagged_start","run_time" : 3}),
                    Succession(Animation, Mobject(), {"run_time" : 3},
                    ShowCreationThenDestruction,corriente4,{"submobject_mode":"lagged_start","run_time" : 3}),
                    Succession(Animation, Mobject(), {"run_time" : 4.2},
                    SwitchOn, light,{"submobject_mode":"lagged_start","run_time" : 0.2}),
                    Succession(Animation, Mobject(), {"run_time" : 4},
                    ShowCreationThenDestruction,corriente5,{"submobject_mode":"lagged_start","run_time" : 3})
                )

        
'''
Codigo y Speach.svg de Conversacion por Miroslav Olsak
https://github.com/mkoconnor
https://www.youtube.com/user/procdalsinazev/feed
'''
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




#Escenas de musica
class Percusion(Scene):
    def construct(self):
        tikz="""
            \\begin{music}
            \\instrumentnumber{1}
            \\generalmeter{\\meterfrac44}
            \\setclefsymbol1\\drumclef
            \\parindent0pt\\startpiece
            \\Notes\\zql f\\rlap\\qp\\ibu0m0\\xqb0{nn}\\en
            \\Notes\\kzq d\\zql f\\zq j\\xqb0n\\tbu0\\xqb0n\\en
            \\Notes\\zql f\\rlap\\qp\\ibu0m0\\xqb0{nn}\\en
            \\Notes\\kzq d\\zql f\\zq j\\xqb0n\\tbu0\\xqb0n\\en
            \\bar
            \\Notes\\zql f\\rlap\\qp\\ibu0m0\\kqb0{nn}\\en
            \\Notes\\xzq d\\zql f\\zq j\\kqb0n\\tbu0\\kqb0n\\en
            \\Notes\\zql f\\rlap\\qp\\ibu0m0\\kqb0{nn}\\en
            \\Notes\\xzq d\\zql f\\zq j\\kqb0n\\tbu0\\kqb0n\\en
            \\endpiece
            \\end{music}
              """
        perc=TikzMobject(tikz,stroke_width=0,fill_opacity=1).scale(0.6)
        self.play(Write(perc),run_time=3)
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

class Armonicos(Scene):
    def construct(self):
        conjunto_lineas=self.Armonics(10,tamanho=12)
        lineas_planas=conjunto_lineas[2]
        lineas_down=conjunto_lineas[1]
        lineas_up=conjunto_lineas[0]
        

        self.play(ShowCreation(lineas_planas[0]))
        for i in range(3):
            lpr=lineas_planas[i].copy()
            for w in range(2):
                self.play(Transform(lineas_planas[i],lineas_up[i]))
                self.play(Transform(lineas_planas[i],lineas_down[i]))
            self.play(ReplacementTransform(lineas_planas[i],lpr),run_time=0.7)
            self.remove(lpr)
            self.add(lineas_planas[i+1])

        self.wait()

    def Armonics(self,numero_armonicos,disminucion=False,amplitud=5,tamanho=12):
        conjunto_lineas=VGroup()
        lineas_up=VMobject()
        lineas_down=VMobject()
        lineas_planas=VMobject()
        punto_referencia=ORIGIN+LEFT*tamanho/2
        for linea_v in [lineas_up,lineas_down,lineas_planas]:
            for i in range(numero_armonicos):
                cuerda=VGroup()
                for j in range(i+1):
                    particion=tamanho/(i+1)
                    punto_inicio=punto_referencia+RIGHT*j*particion
                    punto_final=punto_referencia+RIGHT*(j+1)*particion
                    linea=Line(punto_inicio,punto_final,buff=0)
                    for k in range(3):
                        linea.points[0]=linea.get_start()
                        if linea_v==lineas_up:
                            if disminucion==True:
                                linea.points[1]=linea.points[0]+RIGHT*linea.get_length()/2+np.array([0,amplitud*np.sin(PI/2+PI*j)*0.5**i,0])
                            else:
                                linea.points[1]=linea.points[0]+RIGHT*linea.get_length()/2+np.array([0,amplitud*np.sin(PI/2+PI*j),0])
                        if linea_v==lineas_down:
                            if disminucion==True:
                                linea.points[1]=linea.points[0]+RIGHT*linea.get_length()/2+np.array([0,-amplitud*np.sin(PI/2+PI*j)*0.5**i,0])
                            else:
                                linea.points[1]=linea.points[0]+RIGHT*linea.get_length()/2+np.array([0,-amplitud*np.sin(PI/2+PI*j),0])
                        if linea_v==lineas_planas:
                            linea.points[1]=linea.points[0]+RIGHT*linea.get_length()/2
                        linea.points[2]=linea.get_end()
                    cuerda.add(linea)
                linea_v.add(cuerda)
            conjunto_lineas.add(linea_v)
        return conjunto_lineas
