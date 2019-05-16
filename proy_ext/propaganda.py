from big_ol_pile_of_manim_imports import *
from proy_ext.formulas_txt.formulas import formulas
from proy_ext.formulas_txt.formulas import CheckFormulaByTXT

class BielaManivelaCorredera(Scene):
	CONFIG={
		"a":2,
		"b":-6.5,
		"c":1.7,
		"theta_in":70,
		"theta_fin":70-2.5*360,
		"biela_color":RED,
		"manivela_color":BLUE,
		"piston_color":GREEN,
		"ancla_color":PURPLE,
		"grosor_linea":10
	}
	def construct(self):
		O2=Dot().shift(LEFT*4+DOWN*1.5)
		a=self.a
		b=self.b
		c=self.c
		theta_in=self.theta_in
		theta_fin=self.theta_fin
		biela_color=self.biela_color
		piston_color=self.piston_color
		radio=0.08

		base_down=Patron(8,0.3,direccion="U",agregar_base=True,grosor=0.1,color=WHITE)
		base_up=Patron(8,0.3,direccion="D",agregar_base=True,grosor=0.1,color=WHITE)
		base_down[0:-1].shift(0.1*DOWN)
		base_up[0:-1].shift(0.1*UP)
		punto_ancla=Dot(O2.get_center(),radius=radio)
		semi_circulo_ancla=Dot(O2.get_center(),radius=0.2,color=self.ancla_color)
		rect_ancla=Square(side_length=0.4).set_stroke(None,0).set_fill(self.ancla_color,1).move_to(O2.get_center()+DOWN*semi_circulo_ancla.get_width()/2)
		patron_ancla=Patron(0.6,0.15,color=self.ancla_color,separacion=0.1,direccion="U",agregar_base=True,grosor=0.1).next_to(rect_ancla,DOWN,buff=0)
		patron_ancla[-1].shift(0.1*UP)
		ancla=VGroup(semi_circulo_ancla,rect_ancla,patron_ancla)

		titulo=Texto("\\sc Animaciones de mecanismos.",color=WHITE).scale(1.5).to_corner(UL).shift(RIGHT)
		underline=Line(titulo.get_corner(DL),titulo.get_corner(DR)).shift(DOWN*0.1)

		biela 		=self.posicion_biela(O2.get_center(),theta_in,a,biela_color)
		theta_3		=np.arcsin((a*np.sin(theta_in*DEGREES)-c)/b)*180/PI
		piston  	=self.posicion_piston(O2.get_center(),theta_in,theta_3,a,b,c,piston_color)
		manivela  	=Line(biela.get_end(),piston.get_center()).set_stroke(self.manivela_color,self.grosor_linea)
		punto_bm	=Dot(biela.get_end(),radius=radio)
		punto_mp	=Dot(manivela.get_end(),radius=radio)
		grupo   	=VGroup(biela,piston,manivela,punto_mp,punto_bm)

		base_down.next_to(piston,DOWN,buff=0).shift(LEFT)
		base_up.next_to(piston,UP,buff=0).shift(LEFT)
		self.play(Escribe(titulo),ShowCreation(underline),run_time=1)
		self.play(*[FadeIn(objeto)for objeto in [ancla,base_up,base_down]],
					ShowCreation(biela),DrawBorderThenFill(piston),ShowCreation(manivela),
					GrowFromCenter(punto_mp),GrowFromCenter(punto_bm),GrowFromCenter(punto_ancla),
					)
		self.add_foreground_mobject(punto_ancla)

		def update(grupo,alpha):
			dx 			=interpolate(theta_in, theta_fin, alpha)
			biela 		=self.posicion_biela(O2.get_center(),dx,self.a,self.biela_color)

			theta_3=np.arcsin(np.sign(dx)*((self.a*np.sin(dx*DEGREES)-self.c)/self.b))

			piston 		=self.posicion_piston(O2.get_center(),dx,theta_3*180/PI,self.a,self.b,self.c,self.piston_color)
			manivela 	=Line(biela.get_end(),piston.get_center()).set_stroke(self.manivela_color,self.grosor_linea)
			punto_bm	=Dot(biela.get_end(),radius=radio)
			punto_mp	=Dot(manivela.get_end(),radius=radio)

			nuevo_grupo =VGroup(biela,piston,manivela,punto_mp,punto_bm)
			grupo.become(nuevo_grupo)
			return grupo

		self.play(UpdateFromAlphaFunc(grupo,update),run_time=8,rate_func=double_smooth)
		self.wait()
		cuadro_blanco=Rectangle(width=FRAME_WIDTH,height=FRAME_HEIGHT).set_fill(WHITE,0).set_stroke(WHITE,1)
		self.add_foreground_mobject(cuadro_blanco)
		self.play(cuadro_blanco.set_fill,None,1)
		self.wait()

	def posicion_biela(self,origen,theta_2,longitud,color):
		punto_final_x=longitud*np.cos(theta_2*DEGREES)
		punto_final_y=longitud*np.sin(theta_2*DEGREES)
		punto_final=origen+np.array([punto_final_x,punto_final_y,0])
		biela=Line(origen,punto_final,color=color).set_stroke(None,self.grosor_linea)
		return biela

	def posicion_piston(self,origen,theta_2,theta_3,a,b,c,color):
		d=a*np.cos(theta_2*DEGREES)-b*np.cos(theta_3*DEGREES)
		punto_final=origen+RIGHT*d+UP*c
		piston=Rectangle(color=color,height=1,witdh=1.5).set_fill(color,0.7).scale(0.7).move_to(origen+RIGHT*d+UP*c)
		return piston

class PatronHexagonos(Scene):
	CONFIG={
	"color_hexagonos":BLUE_C,
	}
	def construct(self):
		hexagonos1=self.conjunto_hexagonos(6).scale(2)
		hexagonos2=self.conjunto_hexagonos(6).scale(2)
		hexagonos3=self.conjunto_hexagonos(6).scale(2)
		hexagonos4=self.conjunto_hexagonos(6).scale(2)
		VGroup(hexagonos1,hexagonos2).arrange_submobjects(RIGHT).move_to(ORIGIN)
		VGroup(hexagonos3,hexagonos4).arrange_submobjects(DOWN).move_to(ORIGIN)
		hexagonos3.shift(UP)
		hexagonos4.shift(DOWN)
		h1=VGroup(hexagonos1,hexagonos2,hexagonos3,hexagonos4).set_stroke(opacity=0.5)
		h2=h1.copy().set_stroke(opacity=0.5)
		VGroup(h1,h2).arrange_submobjects(RIGHT)

		titulo=Texto("\\sc Que esta animación\\\\\\sc no te engañe",color=WHITE,background_stroke_width=2).scale(2.5)



		self.play(
		*[LaggedStart(ShowCreationThenDestruction,
			h,
			run_time=4.5,
			lag_ratio=0.7,
			rate_func=lambda t:smooth(t*1.3,inflection=11))for h in h1],
		*[LaggedStart(ShowCreationThenDestruction,
			h,
			run_time=4.5,
			lag_ratio=0.7,
			rate_func=lambda t:smooth(t*1.3,inflection=11))for h in h2],
		Escribe_y_desvanece(titulo,run_time=7,rate_func=lambda t:there_and_back(1.1*t))
		)

	def conjunto_hexagonos(self,particiones,rotacion=PI/2,grosor_inicial=1,grosor_final=25):
		hexagonos=VGroup()
		for part in range(1,particiones+1):
			hexagono=RegularPolygon(n=6,color=self.color_hexagonos).scale(part/particiones).rotate(rotacion)
			gradiente_grosor=(grosor_inicial-grosor_final)/part
			hexagono.set_stroke(None,grosor_inicial-gradiente_grosor)
			hexagono.move_to(ORIGIN)
			hexagonos.add(hexagono)
		return hexagonos

class Teclado(Scene):
    CONFIG = {"include_sound": True,
    "camera_config":{"background_color":BLACK}}
    def construct(self):
        self.wait()
        texto=Texto("""
     		\\tt No fué creada en \\\\
     		{\\sc After Effects}\\\\
     		\\tt ni similares.
            """).set_stroke(None,0).set_fill(WHITE,0).scale(2).move_to(ORIGIN).set_color_by_gradient(WHITE,BLUE,PURPLE)
        self.add(texto)
        #'''
        KeyBoard(self,texto,p=0.0656,time_random=0.0656)
        self.wait(0.1)
        self.play(Write(texto,rate_func=lambda t:smooth(1-t)))
        self.wait()

class CreadaPython3(Scene):
	def construct(self):
		texto=Texto("\\sc Fué hecha en\\\\ {\\tt PYTHON 3.7}!!!!\\\\ Con \\underline{\\it software libre}",
			color=WHITE).scale(2.5)
		texto[-14:].set_color(RED)
		texto[-30:-17].set_color(GREEN)
		self.play(
			LaggedStart(GrowFromCenter,texto)
			)
		self.wait(1.7)
		#'''
		self.play(
			LaggedStart(FadeOutAndShiftDown,texto)
			)
		#'''
		self.wait(0.3)

class CreadoPor(Scene):
	def construct(self):
		texto=Texto("\\sc Esta herramienta fue creada por:",color=WHITE).to_edge(UP)
		grant=ImageMobject("grant",height=5)
		i3b1b=ImageMobject("3b1b",height=5)
		imagenes=Mobject(grant,i3b1b).arrange_submobjects(RIGHT).next_to(texto,DOWN)
		t_grant=Texto("Grant Sanderson / 3Blue1Brown",color=WHITE).next_to(imagenes,DOWN)

		self.play(Write(texto),FadeIn(imagenes),Write(t_grant))
		self.wait(1.5)
		cuadro_negro=Rectangle(width=FRAME_WIDTH,height=FRAME_HEIGHT).set_fill(BLACK,0).set_stroke(None,0)
		self.add_foreground_mobject(cuadro_negro)
		self.play(cuadro_negro.set_fill,None,1)

class QuePuedoHacer(Scene):
	def construct(self):
		texto=VGroup(
			Texto("\\sc ¿Qué animaciones",color=WHITE),
			Texto("\\sc se pueden hacer?",color=WHITE)
			).arrange_submobjects(DOWN).scale(2.5).fade(1)
		textoc=texto.copy()
		textoc[0].shift(FRAME_WIDTH*LEFT+textoc[0].get_width()*LEFT)
		textoc[1].shift(FRAME_WIDTH*RIGHT+textoc[1].get_width()*RIGHT)
		self.play(
			textoc[0].fade,0,
			textoc[0].move_to,texto[0],
			textoc[1].fade,0,
			textoc[1].move_to,texto[1],
			run_time=1.8
			)
		self.wait(1.3)
		self.play(
			textoc[0].fade,1,
			textoc[0].shift,FRAME_WIDTH*RIGHT+textoc[1].get_width()*RIGHT,
			textoc[1].fade,1,
			textoc[1].shift,FRAME_WIDTH*LEFT+textoc[0].get_width()*LEFT,
			run_time=1.8
			)

class EscenaMusica(MusicalScene):
    CONFIG = {"include_sound": True}
    def construct(self):
        self.teclado_transparente=self.definir_teclado(4,self.prop,0).set_stroke(None,0)
        self.teclado_base=self.definir_teclado(4,self.prop,1)
        self.teclado_base.move_to(ORIGIN+DOWN*3)
        self.teclado_transparente.move_to(ORIGIN+DOWN*3)

        self.agregar_escenario()
        self.primer_paso(simbolos_faltantes=[14,15,16,17,18,19,20,21])
        self.add_sound("armonicos/pI",gain=-12)
        self.progresion(0,run_time=2)
        self.add_sound("armonicos/pIV",gain=-12)
        self.progresion_con_desfase(paso=1,desfase=22,y1=8,x2=8,y2=16,run_time=2)
        self.add_sound("armonicos/pV",gain=-12)
        self.progresion_con_desfase(paso=2,desfase=30,y1=8,x2=10,y2=18,simbolos_faltantes=[38,39],run_time=2)
        self.add_sound("armonicos/pI2",gain=-12)

        self.intervalos()

        self.salida_teclado()
        


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
        titulo=Texto("\\sc Y en general, hasta donde tu imaginación te deje.",color=BLACK).to_corner(UL)
        ul=underline(titulo,color=BLACK)

        self.mandar_frente_sostenido(4,self.teclado_base)
        self.mandar_frente_sostenido(4,self.teclado_transparente)

        self.play(*[LaggedStart(GrowFromCenter, self.partitura[i],run_time=2)for i in range(1,11)],
            LaggedStart(DrawBorderThenFill,self.teclado_base),LaggedStart(DrawBorderThenFill,self.teclado_transparente),
            Write(titulo),ShowCreation(ul),*[GrowFromCenter(x)for x in self.grupoA]
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

class EjemploGrafica(GraphScene):
    CONFIG = {
        "y_max": 8,
        "y_axis_height": 5,
        "default_riemann_start_color": PINK,
        "default_riemann_end_color": PINK,
    }

    def construct(self):
        self.add_title()
        self.show_function_graph()
        #self.otra_definicion()

    def add_title(self):
        title = self.title = TextMobject("\\sc Animar gráficas en 2D.")
        title.to_edge(UP)
        
        h_line = Line(LEFT, RIGHT)
        h_line.set_height(FRAME_WIDTH - 2 * LARGE_BUFF)
        h_line.next_to(title, DOWN)
        h_line.set_stroke(WHITE,3)
        title.to_edge(UP+LEFT)
        title.shift(RIGHT)
        self.title=title
        self.lin_h = h_line

    def show_function_graph(self):
        ul=underline(self.title)
        self.setup_axes(animate=True,add_anims=[Escribe(self.title),ShowCreation(ul)])
        self.add_foreground_mobjects(self.title,ul)
        def func(x):
            return 0.1 * (x + 3-5) * (x - 3-5) * (x-5) + 5

        def rect(x):
            return 2.775*(x-1.5)+3.862
        recta = self.get_graph(rect,x_min=-1,x_max=5)
        graph = self.get_graph(func,x_min=0.2,x_max=9)
        graph.set_color(TT_AZUL_T)
        input_tracker_p1 = ValueTracker(1.5)
        input_tracker_p2 = ValueTracker(3.5)

        def get_x_value_p1():
            return input_tracker_p1.get_value()

        def get_x_value_p2():
            return input_tracker_p2.get_value()

        def get_y_value_p1():
            return graph.underlying_function(get_x_value_p1())

        def get_y_value_p2():
            return graph.underlying_function(get_x_value_p2())

        def get_x_point_p1():
            return self.coords_to_point(get_x_value_p1(), 0)

        def get_x_point_p2():
            return self.coords_to_point(get_x_value_p2(), 0)

        def get_y_point_p1():
            return self.coords_to_point(0, get_y_value_p1())

        def get_y_point_p2():
            return self.coords_to_point(0, get_y_value_p2())

        def get_graph_point_p1():
            return self.coords_to_point(get_x_value_p1(), get_y_value_p1())

        def get_graph_point_p2():
            return self.coords_to_point(get_x_value_p2(), get_y_value_p2())

        def get_v_line_p1():
            return DashedLine(get_x_point_p1(), get_graph_point_p1(), stroke_width=2)

        def get_v_line_p2():
            return DashedLine(get_x_point_p2(), get_graph_point_p2(), stroke_width=2)

        def get_h_line_p1():
            return DashedLine(get_graph_point_p1(), get_y_point_p1(), stroke_width=2)

        def get_h_line_p2():
            return DashedLine(get_graph_point_p2(), get_y_point_p2(), stroke_width=2)
        # Triangulo a
        input_triangle_p1 = RegularPolygon(n=3, start_angle=TAU / 4)
        output_triangle_p1 = RegularPolygon(n=3, start_angle=0)
        for triangle in input_triangle_p1, output_triangle_p1:
            triangle.set_fill(WHITE, 1)
            triangle.set_stroke(width=0)
            triangle.scale(0.1)
        # Triangulo b
        input_triangle_p2 = RegularPolygon(n=3, start_angle=TAU / 4)
        output_triangle_p2 = RegularPolygon(n=3, start_angle=0)
        for triangle in input_triangle_p2, output_triangle_p2:
            triangle.set_fill(WHITE, 1)
            triangle.set_stroke(width=0)
            triangle.scale(0.1)
        # Entradas y salidas del triangulo a
        input_triangle_update_p1 = ContinualUpdate(
            input_triangle_p1, lambda m: m.move_to(get_x_point_p1(), DOWN)
        )
        output_triangle_update_p1 = ContinualUpdate(
            output_triangle_p1, lambda m: m.move_to(get_y_point_p1(), LEFT)
        )
        # Entradas y salidas del triangulo b
        input_triangle_update_p2 = ContinualUpdate(
            input_triangle_p2, lambda m: m.move_to(get_x_point_p2(), DOWN)
        )
        output_triangle_update_p2 = ContinualUpdate(
            output_triangle_p2, lambda m: m.move_to(get_y_point_p2(), LEFT)
        )
        # Etiqueas y salidas del punto a
        x_label_p1 = TexMobject("a")
        x_label_update_p1 = ContinualUpdate(
            x_label_p1, lambda ma: ma.next_to(input_triangle_p1, DOWN, SMALL_BUFF)
        )

        output_label_p1 = TexMobject("f(a)")
        output_label_update_p1 = ContinualUpdate(
            output_label_p1, lambda ma: ma.next_to(
                output_triangle_p1, LEFT, SMALL_BUFF)
        )
        # Etiqueas y salidas del punto b
        x_label_p2 = TexMobject("b")
        x_label_update_p2 = ContinualUpdate(
            x_label_p2, lambda mb: mb.next_to(input_triangle_p2, DOWN, SMALL_BUFF)
        )

        output_label_p2 = TexMobject("f(b)")
        output_label_update_p2 = ContinualUpdate(
            output_label_p2, lambda mb: mb.next_to(
                output_triangle_p2, LEFT, SMALL_BUFF)
        )
        # V_lines de a
        v_line_p1 = get_v_line_p1()
        v_line_update_p1 = ContinualUpdate(
            v_line_p1, lambda vla: Transform(vla, get_v_line_p1()).update(1)
        )
        # V_lines de b
        v_line_p2 = get_v_line_p2()
        v_line_update_p2 = ContinualUpdate(
            v_line_p2, lambda vlb: Transform(vlb, get_v_line_p2()).update(1)
        )
        # h_lines de a
        h_line_p1 = get_h_line_p1()
        h_line_update_p1 = ContinualUpdate(
            h_line_p1, lambda hla: Transform(hla, get_h_line_p1()).update(1)
        )
        # h_lines de b
        h_line_p2 = get_h_line_p2()
        h_line_update_p2 = ContinualUpdate(
            h_line_p2, lambda hlb: Transform(hlb, get_h_line_p2()).update(1)
        )
        # Animacion del punto a
        graph_dot_p1 = Dot(color=TT_SIMBOLO)
        graph_dot_update_p1 = ContinualUpdate(
            graph_dot_p1, lambda ma: ma.move_to(get_graph_point_p1())
        )
        # Animacion del punto b
        graph_dot_p2 = Dot(color=TT_SIMBOLO)
        graph_dot_update_p2 = ContinualUpdate(
            graph_dot_p2, lambda mb: mb.move_to(get_graph_point_p2())
        )
        #
        self.play(
            ShowCreation(graph),
        )
        # Animacion del punto a
        self.add_foreground_mobject(graph_dot_p1)
        self.add_foreground_mobject(graph_dot_p2)
        self.play(
            DrawBorderThenFill(input_triangle_p1),
            Write(x_label_p1),
            ShowCreation(v_line_p1),
            GrowFromCenter(graph_dot_p1),
            ShowCreation(h_line_p1),
            Write(output_label_p1),
            DrawBorderThenFill(output_triangle_p1),
            DrawBorderThenFill(input_triangle_p2),
            Write(x_label_p2),
            ShowCreation(v_line_p2),
            GrowFromCenter(graph_dot_p2),
            ShowCreation(h_line_p2),
            Write(output_label_p2),
            DrawBorderThenFill(output_triangle_p2),
            run_time=0.5
        )
        self.add(
            input_triangle_update_p2,
            x_label_update_p2,
            graph_dot_update_p2,
            v_line_update_p2,
            h_line_update_p2,
            output_triangle_update_p2,
            output_label_update_p2,
        )
        ###################
        pendiente_recta = self.get_secant_slope_group(
            1.9, recta, dx = 1.4,
            df_label = None,
            dx_label = None,
            dx_line_color = PURPLE,
            df_line_color= ORANGE,
            )
        grupo_secante = self.get_secant_slope_group(
            1.5, graph, dx = 2,
            df_label = None,
            dx_label = None,
            dx_line_color = TT_FONDO_ROSA,
            df_line_color= TT_FONDO_VERDE,
            secant_line_color = RED,
        )
        start_dx = grupo_secante.kwargs["dx"]
        start_x = grupo_secante.kwargs["x"]
        def update_func_0(group, alpha):
            dx = interpolate(start_dx, 4, alpha)
            x = interpolate(start_x, 1.5, alpha)
            kwargs = dict(grupo_secante.kwargs)
            kwargs["dx"] = dx
            kwargs["x"] = x
            new_group = self.get_secant_slope_group(**kwargs)
            Transform(group, new_group).update(1)
            return group
        def update_func_1(group, alpha):
            dx = interpolate(start_dx, 0.001, alpha)
            x = interpolate(start_x, 1.5, alpha)
            kwargs = dict(grupo_secante.kwargs)
            kwargs["dx"] = dx
            kwargs["x"] = x
            new_group = self.get_secant_slope_group(**kwargs)
            Transform(group, new_group).update(1)
            return group

        self.add(
            input_triangle_update_p2,
            graph_dot_update_p2,
            v_line_update_p2,
            h_line_update_p2,
            output_triangle_update_p2,
        )
        self.play(FadeIn(grupo_secante))

        self.play(
            UpdateFromAlphaFunc(
                grupo_secante, update_func_1,
                run_time=2
            ),
            input_tracker_p2.set_value, 1.5,
            output_label_p1.set_fill,None,0,
            x_label_p2.set_fill,None,0,
            x_label_p1.set_fill,None,0,
            output_label_p2.set_fill,None,0,
            run_time=2
        )
        self.remove(
            input_triangle_update_p2,
            x_label_update_p2,
            graph_dot_update_p2,
            v_line_update_p2,
            h_line_update_p2,
            output_triangle_update_p2,
            output_label_update_p2,
            input_triangle_update_p1,
            x_label_update_p1,
            graph_dot_update_p1,
            v_line_update_p1,
            h_line_update_p1,
            output_triangle_update_p1,
            output_label_update_p1,
        )
        self.add(
            input_triangle_p2,
            x_label_p2,
            graph_dot_p2,
            v_line_p2,
            h_line_p2,
            output_triangle_p2,
            output_label_p2,
            input_triangle_p1,
            x_label_p1,
            graph_dot_p1,
            v_line_p1,
            h_line_p1,
            output_triangle_p1,
            output_label_p1,
        )

        kwargs = {
            "x_min" : 2,
            "x_max" : 8,
            "fill_opacity" : 0.75,
            "stroke_width" : 0.25,
            #"start_color":PURPLE,
            #"end_color":ORANGE,
        }
        self.graph=graph
        iteraciones=6


        self.rect_list = self.get_riemann_rectangles_list(
            graph, iteraciones,start_color=PURPLE,end_color=ORANGE, **kwargs
        )
        flat_rects = self.get_riemann_rectangles(
            self.get_graph(lambda x : 0), dx = 0.5,start_color=invert_color(PURPLE),end_color=invert_color(ORANGE),**kwargs
        )
        rects = self.rect_list[0]
        self.transform_between_riemann_rects(
            flat_rects, rects, 
            replace_mobject_with_target_in_scene = True,
            run_time=0.9
        )
        for j in range(4,6):
            for w in self.rect_list[j]:
                    color=w.get_color()
                    w.set_stroke(color,1.5)
        for j in range(1,6):
            self.transform_between_riemann_rects(
            self.rect_list[j-1], self.rect_list[j], dx=1,
            replace_mobject_with_target_in_scene = True,
            run_time=0.9
            )
        self.wait()
        cuadro_negro=Rectangle(width=FRAME_WIDTH,height=FRAME_HEIGHT).set_fill(BLACK,0).set_stroke(None,0)
        self.add_foreground_mobject(cuadro_negro)
        self.play(cuadro_negro.set_fill,None,1)
        self.wait()

class ProcesosMatematicos(Scene):
	def construct(self):
		self.importar_formulas()
		self.imprime_formula()
		self.configurar_cambios()
		self.conversion_formulas(n_paso=1,
			cambios=self.conjunto_cambios[0],
			fade=[10],
			arco=-PI/2
			)
		self.conversion_formulas(n_paso=2,
			cambios=self.conjunto_cambios[1],
			write=[6,14],
			pre_copias=[0],
			pos_copias=[15]
			)
		self.conversion_formulas(n_paso=3,
			cambios=self.conjunto_cambios[2],
			pos_write=[10,	11,	13,	14,	15,	16,	18,	20,	28,	29,	31,	32,	33,	34,	36,	38],
			)
		self.conversion_formulas(n_paso=4,
			cambios=self.conjunto_cambios[3],
			)
		self.conversion_formulas(n_paso=5,
			cambios=self.conjunto_cambios[4],
			fade=[20,27],
			pre_copias=[29],
			pos_copias=[28]
			)
		self.conversion_formulas(n_paso=6,
			cambios=self.conjunto_cambios[5],
			fade=[19],
			)
		self.conversion_formulas(n_paso=7,
			cambios=self.conjunto_cambios[6],
			pos_write=[25,28],
			run_time=0.2,
			)
		self.conversion_formulas(n_paso=8,
			cambios=self.conjunto_cambios[7],
			pos_write=[32,26],
			run_time=0.2,
			)
		self.conversion_formulas(n_paso=9,
			cambios=self.conjunto_cambios[8],
			)
		self.conversion_formulas(n_paso=10,
			cambios=self.conjunto_cambios[9],
			pos_write=[0,	1,	16,	18,	20],
			)
		self.conversion_formulas(n_paso=11,
			cambios=self.conjunto_cambios[10],
			fade=[0,	1,	2,	12,	14]
			)
		self.conversion_formulas(n_paso=12,
			cambios=self.conjunto_cambios[11],
			)
		self.conversion_formulas(n_paso=13,
			cambios=self.conjunto_cambios[12],
			fade=[25]
			)
		self.conversion_formulas(n_paso=14,
			cambios=self.conjunto_cambios[13],
			)
		#
		c1=SurroundingRectangle(self.formulas[14],buff=0.2)
		c2=SurroundingRectangle(self.formulas[14],buff=0.2)
		c2.rotate(PI)
		self.play(ShowCreationThenDestruction(c1),ShowCreationThenDestruction(c2))
		todos_objetos=VGroup(*self.mobjects)
		self.play(todos_objetos.shift,RIGHT*FRAME_WIDTH)
		self.wait()

	def importar_formulas(self):
		self.formulas=formulas


	def imprime_formula(self):
		titulo=Texto("\\sc Animaciones de carácter matemático.",color=WHITE).to_corner(UL)
		ul=underline(titulo)
		formulas_tex=Texto("Fórmulas escritas en \\LaTeX",color=TEAL).to_edge(DOWN)
		self.play(Escribe(self.formulas[0]),Escribe(titulo),ShowCreation(ul),Escribe(formulas_tex),run_time=1.5)

	def configurar_cambios(self):
		self.conjunto_cambios=[
		#1
		[[
						(	0,	1,	3,	4,	5,	6,	7,	8,	9	),
						(	0,	1,	3,	4,	5,	6,	8,	9,	7	)
		]],
		#2
		[[
						(	0,		1,	3,	4,	5,	6,	7,	8,	9	),
						(	7,		0,	2,	3,	5,	9,	10,	11,	13	)
		]],
		#3
		[[
			(	0,	2,	3,	5,	6,	7,	9,	10,	11,	13,	14,	15	),
			(	0,	2,	3,	5,	6,	7,	9,	21,	22,	24,	25,	26	)
		]],
		#4
		[[
				(	0,	2,	10,	11,	13,	14,	15,	16,	18,	20,	21,	22,	24,	25,	26,	28,	29,	31,	32,	33,	34,	36,	38	,5,6,7,9,3),
				(	1,	11,	2,	0,	4,	5,	6,	7,	9,	11,	12,	13,	15,	16,	17,	19,	20,	22,	23,	24,	25,	27,	29	,4,5,7,1,2)
		]],
		#5
		[[
		(	0,	1,	2,	4,	5,	6,	7,	9,	11,	12,	13,	15,	16,	17,	19,	22,	23,	24,	25,	29),
		(	0,	1,	2,	4,	5,	6,	7,	9,	11,	12,	13,	15,	16,	17,	19,	21,	24,	25,	26,	23)
		]],
		#6
		[[
			(	0,	1,	2,	4,	5,	6,	7,	9,	11,	12,	13,	15,	16,	17,	21,	23,	24,	25,	26,	28	),
			(	0,	1,	2,	4,	5,	6,	7,	9,	11,	12,	23,	25,	26,	27,	14,	16,	17,	18,	19,	21	)
		]],
		#7
		[[
			(	0,	1,	2,		4,	5,	6,	7,		9,		11,	12,		14,		16,	17,	18,	19,		21,		23,		25,	26,	27	),
			(	0,	1,	2,		4,	5,	6,	7,		9,		11,	12,		14,		16,	17,	18,	19,		21,		23,		26,	27,	29	)
		]],
		#8
		[[
			(	0,	1,	2,		4,	5,	6,	7,		9,		11,	12,		14,		16,	17,	18,	19,		21,		23,		25,	26,	27,	28,	29,	),
			(	0,	1,	2,		4,	5,	6,	7,		9,		11,	12,		14,		16,	17,	18,	19,		21,		23,		25,	27,	28,	29,	30,	)
		]],
		#9
		[[
			(	0,	1,	2,		4,	5,	6,	7,		9,		11,	12,		14,		16,	17,	18,	19,		21,		23,		25,	26,	27,	28,	29,	30,		32,	),
			(	0,	1,	2,		4,	5,	6,	7,		9,		11,	12,		14,		16,	21,	22,	23,		25,		17,		18,	19,	20,	21,	22,	23,		25,	)
		]],
		#10
		[[
			(	0,	1,	2,		4,	5,	6,	7,		9,		11,	12,		14,		16,	17,	18,	19,	20,	21,	22,	23,		25,	),
			(	2,	3,	5,		6,	7,	8,	10,		12,		14,	15,		21,		22,	23,	24,	25,	26,	27,	30,	31,		32,	)
		]],
		#11
		[[
			(				3,		5,	6,	7,	8,		10,					15,	16,		18,		20,	21,	22,	23,	24,	25,	26,	27,			30,	31,	32,	),
			(				0,		1,	3,	4,	5,		6,					8,	9,		10,		12,	14,	15,	16,	17,	18,	19,	20,			21,	24,	25,	)
		]],
		#12
		[[
			(	0,	1,		3,	4,	5,	6,		8,	9,	10,		12,		14,	15,	16,	17,	18,	19,	20,	21,			24,	25,	),
			(	0,	2,		4,	5,	6,	7,		1,	9,	10,		12,		14,	15,	16,	17,	18,	19,	20,	21,			24,	25,	)
		]],
		#13
		[[
			(	0,	1,	2,		4,	5,	6,	7,		9,	10,		12,		14,	15,	16,	17,	18,	19,	20,	21,			24,	),
			(	0,	1,	2,		4,	5,	6,	7,		9,	11,		12,		14,	15,	16,	17,	18,	20,	21,	22,			23,	)
		]],
		#14
		[[
			(	0,	1,	2,		4,	5,	6,	7,		9,		11,	12,		14,	15,	16,	17,	18,		20,	21,	22,	23,	),
			(	0,	1,	3,		4,	16,	17,	18,		5,		6,	7,		9,	10,	11,	12,	13,		15,	16,	17,	18,	)
		]]
		]

	def conversion_formulas(self,
							pre_write=[],
							pos_write=[],
							pre_fade=[],
							pos_fade=[],
							fade=[],
							write=[],
							cambios=[[]],
							arco=0,
							n_paso=0,
							pre_copias=[],
							pos_copias=[],
							tiempo_pre_cambios=0,
							tiempo_cambios_final=0,
							run_time=0.9,
							rate_func=linear,
							tiempo_final=0,
							pre_orden=["w","f"],
							pos_orden=["w","f"]
							):
		formula_copia=[]
		for c in pre_copias:
			formula_copia.append(self.formulas[n_paso-1][c].copy())

		for ani_ in pre_orden:
			if len(pre_write)>0 and ani_=="w":
				self.play(*[Write(self.formulas[n_paso-1][w])for w in pre_write],rate_func=rate_func)
			if len(pre_fade)>0 and ani_=="f":
				self.play(*[FadeOut(self.formulas[n_paso-1][w])for w in pre_fade],rate_func=rate_func)

		self.wait(tiempo_pre_cambios)

		for pre_ind,post_ind in cambios:
			self.play(*[
				ReplacementTransform(
					self.formulas[n_paso-1][i],self.formulas[n_paso][j],
					path_arc=arco,rate_func=rate_func
					)
				for i,j in zip(pre_ind,post_ind)
				],
				*[FadeOut(self.formulas[n_paso-1][f],rate_func=rate_func)for f in fade if len(fade)>0],
				*[Write(self.formulas[n_paso][w],rate_func=rate_func)for w in write if len(write)>0],
				*[ReplacementTransform(formula_copia[j],self.formulas[n_paso][f],rate_func=rate_func)
				for j,f in zip(range(len(pos_copias)),pos_copias) if len(pre_copias)>0
				],
				run_time=run_time,rate_func=rate_func
			)

		self.wait(tiempo_cambios_final)

		for ani_ in pos_orden:
			if len(pos_write)>0 and ani_=="w":
				self.play(*[Write(self.formulas[n_paso][w])for w in pos_write],rate_func=rate_func)
			if len(pos_fade)>0 and ani_=="f":
				self.play(*[FadeOut(self.formulas[n_paso][w])for w in pos_fade],rate_func=rate_func)

		self.wait(tiempo_final)

class TeoremaPitagoras(Scene):
	CONFIG={
	"color_triangulos":YELLOW,
	"color_rect_c":RED,
	"color_rect_b":ORANGE,
	"color_rect_a":ORANGE,
	"color_cuadrado_c":ORANGE,
	"opacidad_triangulos":0.6,
	"opacidad_cuadradro_a":0.6,
	"opacidad_cuadradro_b":0.6,
	"opacidad_cuadradro_c":0.6,
	"grosor_lineas":1,
	"l_a":5/5,
	"l_b":12/5,
	"l_c":13/5,
	}
	def construct(self):
		self.pre_cuadrado()
		self.pos_cuadrado()
		self.tran_pre_pos_cuadrado()

	def pre_cuadrado(self):
		cuadro=Square(side_length=self.l_a+self.l_b)
		coordenadas_esquinas=[]
		for punto in [DL,DR,UL,UR]:
			coordenadas_esquinas.append(cuadro.get_corner(punto))
		eii,eid,esi,esd=coordenadas_esquinas
		p_eii=Dot(eii)
		p_eid=Dot(eid)
		p_esi=Dot(esi)
		p_esd=Dot(esd)
		puntos_esquinas=VGroup(p_eii,p_eid,p_esi,p_esd)

		coordenadas_lados=[]
		#               lin 			liz					ls 				   ld
		for punto in [eid+LEFT*self.l_b,eii+UP*self.l_b,esi+RIGHT*self.l_b,esd+DOWN*self.l_b]:
			coordenadas_lados.append(punto)
		lin,liz,ls,ld=coordenadas_lados
		p_lin=Dot(lin)
		p_liz=Dot(liz)
		p_ls=Dot(ls)
		p_ld=Dot(ld)
		puntos_lados=VGroup(p_lin,p_liz,p_ls,p_ld)

		t1=Polygon(lin,eid,ld,color=self.color_triangulos).set_fill(self.color_triangulos,self.opacidad_triangulos).set_stroke(None,self.grosor_lineas)
		t2=Polygon(lin,eii,liz,color=self.color_triangulos).set_fill(self.color_triangulos,self.opacidad_triangulos).set_stroke(None,self.grosor_lineas)
		t3=Polygon(liz,esi,ls,color=self.color_triangulos).set_fill(self.color_triangulos,self.opacidad_triangulos).set_stroke(None,self.grosor_lineas)
		t4=Polygon(ld,esd,ls,color=self.color_triangulos).set_fill(self.color_triangulos,self.opacidad_triangulos).set_stroke(None,self.grosor_lineas)
		cuadrado_c=Polygon(*coordenadas_lados,color=self.color_cuadrado_c).set_fill(self.color_cuadrado_c,self.opacidad_cuadradro_c)

		self.cuadrado_c=cuadrado_c

		med_ia=Medicion(Line(eii,lin),invertir=True,dashed=True,buff=0.5).add_tips().add_tex("a",buff=-3.7,color=WHITE)
		med_ib=Medicion(Line(lin,eid),invertir=True,dashed=True,buff=0.5).add_tips().add_tex("b",buff=-2.7,color=WHITE)
		med_izb=Medicion(Line(eii,liz),invertir=False,dashed=True,buff=0.5).add_tips().add_tex("b",buff=1,color=WHITE)
		med_iza=Medicion(Line(liz,esi),invertir=False,dashed=True,buff=0.5).add_tips().add_tex("a",buff=2,color=WHITE)
		med_iza[-1].rotate(-PI/2)
		med_izb[-1].rotate(-PI/2)
		mediciones_1=VGroup(med_ia,med_ib,med_iza,med_izb)
		
		
		titulo=Texto("\\sc Animaciones de demostraciones gráficas.",color=WHITE).to_corner(UL)
		ul=underline(titulo)
		self.titulo=VGroup(titulo,ul)
		self.play(Escribe(titulo,run_time=1),ShowCreation(ul,run_time=1),ShowCreation(cuadro,run_time=1),
			*[DrawBorderThenFill(triangulo)for triangulo in [t1,t2,t3,t4]],
			*[GrowFromCenter(objeto)for objeto in [*mediciones_1]],run_time=1
			)

		conjunto_pre_cuadrado=VGroup(cuadro,t1,t2,t3,t4)
		#self.add(cuadro,t1,t2,t3,t4,cuadrado_c)
		self.conjunto_pre_cuadrado=conjunto_pre_cuadrado
		self.conjunto_pre_cuadrado.add(med_ia,med_ib,med_iza,med_izb)
		self.play(conjunto_pre_cuadrado.to_edge,LEFT,{"buff":1.7})
		cuadrado_c.move_to(cuadro)

	def pos_cuadrado(self):
		cuadro=Square(side_length=self.l_a+self.l_b)
		coordenadas_esquinas=[]
		for punto in [DL,DR,UL,UR]:
			coordenadas_esquinas.append(cuadro.get_corner(punto))
		eii,eid,esi,esd=coordenadas_esquinas
		p_eii=Dot(eii)
		p_eid=Dot(eid)
		p_esi=Dot(esi)
		p_esd=Dot(esd)
		puntos_esquinas=VGroup(p_eii,p_eid,p_esi,p_esd)

		coordenadas_lados=[]
		#               lin 				liz					ls 				   ld
		for punto in [eid+LEFT*self.l_b,eii+UP*self.l_a,esi+RIGHT*self.l_a,esd+DOWN*self.l_b,eii+self.l_a*(UP+RIGHT)]:
			coordenadas_lados.append(punto)
		lin,liz,ls,ld,centro=coordenadas_lados
		p_lin=Dot(lin)
		p_liz=Dot(liz)
		p_ls=Dot(ls)
		p_ld=Dot(ld)
		p_centro=Dot(centro)
		puntos_lados=VGroup(p_lin,p_liz,p_ls,p_ld,p_centro)

		t1=Polygon(lin,eid,ld,color=self.color_triangulos).set_fill(self.color_triangulos,self.opacidad_triangulos).set_stroke(None,self.grosor_lineas)
		t2=Polygon(lin,centro,ld,color=self.color_triangulos).set_fill(self.color_triangulos,self.opacidad_triangulos).set_stroke(None,self.grosor_lineas)
		t3=Polygon(esi,liz,centro,color=self.color_triangulos).set_fill(self.color_triangulos,self.opacidad_triangulos).set_stroke(None,self.grosor_lineas)
		t4=Polygon(centro,ls,esi,color=self.color_triangulos).set_fill(self.color_triangulos,self.opacidad_triangulos).set_stroke(None,self.grosor_lineas)
		cuadrado_a=Polygon(*[eii,liz,centro,lin],color=self.color_rect_a).set_fill(self.color_rect_a,self.opacidad_cuadradro_a)
		cuadrado_b=Polygon(*[centro,ls,esd,ld],color=self.color_rect_b).set_fill(self.color_rect_b,self.opacidad_cuadradro_b)

		med_ia=Medicion(Line(eii,lin),invertir=True,dashed=True,buff=0.5).add_tips().add_tex("a",buff=-3.7,color=WHITE)
		med_ib=Medicion(Line(lin,eid),invertir=True,dashed=True,buff=0.5).add_tips().add_tex("b",buff=-2.7,color=WHITE)
		med_iza=Medicion(Line(eii,liz),invertir=False,dashed=True,buff=0.5).add_tips().add_tex("a",buff=1.8,color=WHITE)
		med_izb=Medicion(Line(liz,esi),invertir=False,dashed=True,buff=0.5).add_tips().add_tex("b",buff=1,color=WHITE)
		med_iza[-1].rotate(-PI/2)
		med_izb[-1].rotate(-PI/2)
		mediciones_2=VGroup(med_ia,med_ib,med_iza,med_izb)

		conjunto_pos_cuadrado=VGroup(cuadro,t1,t2,t3,t4,cuadrado_a,cuadrado_b,mediciones_2)
		conjunto_pos_cuadrado.to_edge(RIGHT,buff=1.7)
		self.conjunto_pos_cuadrado=conjunto_pos_cuadrado

		self.mediciones_2=mediciones_2

		self.cuadrado_a=cuadrado_a
		self.cuadrado_b=cuadrado_b

	def tran_pre_pos_cuadrado(self):
		self.play(
			ReplacementTransform(
					self.conjunto_pre_cuadrado[0].copy(),self.conjunto_pos_cuadrado[0],
				),run_time=1
			)
		self.play(
					*[ReplacementTransform(
						self.conjunto_pre_cuadrado[i].copy(),self.conjunto_pos_cuadrado[i],
						)for i in range(1,5)],run_time=1
				)
		self.play(*[GrowFromCenter(objeto)for objeto in [*self.mediciones_2]],run_time=1)
		self.play(DrawBorderThenFill(self.cuadrado_c),DrawBorderThenFill(self.conjunto_pos_cuadrado[-3]),DrawBorderThenFill(self.conjunto_pos_cuadrado[-2]),run_time=1)


		t_a2=Formula("a^2",color=WHITE).move_to(self.cuadrado_a)
		t_b2=Formula("b^2",color=WHITE).move_to(self.cuadrado_b)
		t_c2=Formula("c^2",color=WHITE).move_to(self.cuadrado_c)

		self.play(*[Write(t_)for t_ in [t_a2,t_b2,t_c2]])

		teorema=Formula("c^2","=","a^2","+","b^2",color=BLUE).to_edge(DOWN)
		self.play(
					*[ReplacementTransform(
						t_.copy()[:],r_
						)for t_,r_ in zip([t_a2,t_b2,t_c2],[teorema[2],teorema[-1],teorema[0]])],
					Write(teorema[1]),Write(teorema[-2]),run_time=1
				)
		self.wait()
		self.play(
			self.titulo.shift,UP*3,
			teorema.shift,DOWN*3,
			self.conjunto_pos_cuadrado.shift,RIGHT*7,
			self.conjunto_pre_cuadrado.shift,LEFT*7,
			VGroup(t_a2,t_b2).shift,RIGHT*7,
			t_c2.shift,LEFT*5,
			self.cuadrado_c.shift,LEFT*7,
			)

class Chat(Scene):
    CONFIG = {"include_sound": True}
    def construct(self):
        conversation = Conversation(self)
        self.add_sound("efectos_sonido/send_message",gain=-5)
        conversation.add_bubble("Qué ventajas tiene?")
        self.wait(1.5)
        self.add_sound("efectos_sonido/notification1",gain=-20)
        conversation.add_bubble("$-$Es software libre.\\\\ $-$Funciona en computadoras antiguas.\\\\ $-$Aprendes a programar.\\\\ $-$Funciona en Windows, Mac y GNU/Linux.")
        self.wait(3)
        self.add_sound("efectos_sonido/send_message",gain=-5)
        conversation.add_bubble("Donde puedo aprender gratis?")
        self.wait(1.5) 
        self.add_sound("efectos_sonido/notification1",gain=-20)
        conversation.add_bubble("En youtube busca\\\\``{\\tt tutorial de manim en español}''")
        self.wait(2) 
        self.add_sound("efectos_sonido/send_message",gain=-5)
        conversation.add_bubble("Hay clases particulares?")
        self.wait(1.5)
        self.add_sound("efectos_sonido/notification1",gain=-20)
        conversation.add_bubble("Sí, manda inbox a {\\tt Alexander VZ} o\\\\ Whatsapp: 5513374414\\\\ Envía mensaje para más info.")
        self.wait(3)
        self.add_sound("efectos_sonido/send_message",gain=-5)
        conversation.add_bubble("Gracias! :D")
        self.wait(1.5)
        self.play(FadeOut(conversation.dialog[:]))
        self.wait()

class Superficies(ThreeDScene):
	def construct(self):
		self.axes = ThreeDAxes()
		cylinder = ParametricSurface(
		    lambda u, v: np.array([
		        np.cos(TAU * v),
		        np.sin(TAU * v),
		        2 * (1 - u)
		    ]),
		    resolution=(6, 32)).fade(0.5)
		paraboloide = ParametricSurface(
		    lambda u, v: np.array([
		        np.cos(v)*u,
		        np.sin(v)*u,
		        u**2
		    ]),v_max=TAU,
		    checkerboard_colors=[PURPLE_D, PURPLE_E],
		    resolution=(10, 32)).scale(2)
		phi=2
		hiper_para = ParametricSurface(
		    lambda u, v: np.array([
		        u,
		        v,
		        u**2-v**2
		    ]),v_min=-phi,v_max=phi,u_min=-phi,u_max=phi,checkerboard_colors=[BLUE_D, BLUE_E],
		    resolution=(15, 32)).scale(1)
		phi=2
		cono = ParametricSurface(
		    lambda u, v: np.array([
		        u*np.cos(v),
		        u*np.sin(v),
		        u
		    ]),v_min=0,v_max=TAU,u_min=-phi,u_max=phi,checkerboard_colors=[GREEN_D, GREEN_E],
		    resolution=(15, 32)).scale(1)
		phi=2
		hip_una_hoja = ParametricSurface(
		    lambda u, v: np.array([
		        np.cosh(u)*np.cos(v),
		        np.cosh(u)*np.sin(v),
		        np.sinh(u)
		    ]),v_min=0,v_max=TAU,u_min=-phi,u_max=phi,checkerboard_colors=[YELLOW_D, YELLOW_E],
		    resolution=(15, 32)).scale(1)
		elipsoide=ParametricSurface(
		    lambda u, v: np.array([
		        1*np.cos(u)*np.cos(v),
		        2*np.cos(u)*np.sin(v),
		        0.5*np.sin(u)
		    ]),v_min=0,v_max=TAU,u_min=-PI/2,u_max=PI/2,checkerboard_colors=[TEAL_D, TEAL_E],
		    resolution=(15, 32)).scale(2)
		sphere = ParametricSurface(
		    lambda u, v: np.array([
		        1.5*np.cos(u)*np.cos(v),
		        1.5*np.cos(u)*np.sin(v),
		        1.5*np.sin(u)
		    ]),v_min=0,v_max=TAU,u_min=-PI/2,u_max=PI/2,checkerboard_colors=[RED_D, RED_E],
		    resolution=(15, 32)).scale(2)
		curva1=ParametricFunction(
                lambda u : np.array([
		        1.2*np.cos(u),
		        1.2*np.sin(u),
		        u/2
		    ]),color=RED,t_min=-TAU,t_max=TAU,
            )
		curva2=ParametricFunction(
                lambda u : np.array([
		        1.2*np.cos(u),
		        1.2*np.sin(u),
		        u
		    ]),color=RED,t_min=-TAU,t_max=TAU,
            )
		#sphere.shift(IN)
		question = TextMobject("Animaciones con funciones 3D.",color=WHITE)
		question.set_width(FRAME_WIDTH - 3)
		self.set_camera_orientation(phi=75 * DEGREES)
		self.begin_ambient_camera_rotation()
		self.add_fixed_in_frame_mobjects(question.scale(0.6))
		question.to_corner(UL)
		ul=underline(question)
		self.add_fixed_in_frame_mobjects(ul)
		self.play(Write(self.axes),Write(question),ShowCreation(ul))
		ghost_sphere = sphere.copy()
		pieces = self.get_ghost_surface(sphere)
		random.shuffle(pieces.submobjects)
		for piece in pieces:
		    piece.save_state()
		pieces.space_out_submobjects(2)
		pieces.fade(1)

		#self.add(ghost_sphere)
		self.play(LaggedStart(Restore, pieces))
		self.remove(pieces)
		self.add(sphere)
		self.wait(0.3)
		#self.play(ReplacementTransform(pieces,sphere))
		#self.wait()
		#'''
		self.play(ReplacementTransform(sphere,elipsoide))
		self.wait()
		self.play(ReplacementTransform(elipsoide,cono))
		self.wait()
		'''
		self.play(ReplacementTransform(cono,hip_una_hoja))
		self.wait()
		self.play(ReplacementTransform(hip_una_hoja,hiper_para))
		self.wait()
		self.play(ReplacementTransform(hiper_para,paraboloide))
		self.wait()
		self.play(FadeOut(paraboloide))
		self.add_foreground_mobjects(self.axes,question)
		self.play(ShowCreation(curva1))
		self.play(Transform(curva1,curva2,rate_func=there_and_back))
		self.play(FadeOut(curva1))
		#self.play(Transform(curva2,curva1))
		
		#'''

	def get_ghost_surface(self, surface):
		result = surface.copy()
		#result.set_fill(RED_D, opacity=0.5)
		#result.set_stroke(RED_E, width=0.5, opacity=0.5)
		return result

class Thumbnail(GraphScene):
    CONFIG = {
        "y_max": 8,
        "y_axis_height": 5,
        "default_riemann_start_color": PINK,
        "default_riemann_end_color": PINK,
    }

    def construct(self):
        self.add_title()
        self.show_function_graph()
        #self.otra_definicion()

    def add_title(self):
        title = self.title = TextMobject("\\sc Tutorial de Manim").scale(2.3)
        title.to_edge(UP)
        
        h_line = Line(LEFT, RIGHT)
        h_line.set_height(FRAME_WIDTH - 2 * LARGE_BUFF)
        h_line.next_to(title, DOWN)
        h_line.set_stroke(WHITE,3)
        title.to_edge(UP+LEFT)
        title.shift(RIGHT)
        self.title=title
        self.lin_h = h_line

    def show_function_graph(self):
        ul=underline(self.title)
        self.setup_axes(animate=True,add_anims=[Escribe(self.title),ShowCreation(ul)])
        self.add_foreground_mobjects(self.title,ul)
        def func(x):
            return 0.1 * (x + 3-5) * (x - 3-5) * (x-5) + 5

        def rect(x):
            return 2.775*(x-1.5)+3.862
        recta = self.get_graph(rect,x_min=-1,x_max=5)
        graph = self.get_graph(func,x_min=0.2,x_max=9)
        graph.set_color(TT_AZUL_T)
        input_tracker_p1 = ValueTracker(1.5)
        input_tracker_p2 = ValueTracker(3.5)

        def get_x_value_p1():
            return input_tracker_p1.get_value()

        def get_x_value_p2():
            return input_tracker_p2.get_value()

        def get_y_value_p1():
            return graph.underlying_function(get_x_value_p1())

        def get_y_value_p2():
            return graph.underlying_function(get_x_value_p2())

        def get_x_point_p1():
            return self.coords_to_point(get_x_value_p1(), 0)

        def get_x_point_p2():
            return self.coords_to_point(get_x_value_p2(), 0)

        def get_y_point_p1():
            return self.coords_to_point(0, get_y_value_p1())

        def get_y_point_p2():
            return self.coords_to_point(0, get_y_value_p2())

        def get_graph_point_p1():
            return self.coords_to_point(get_x_value_p1(), get_y_value_p1())

        def get_graph_point_p2():
            return self.coords_to_point(get_x_value_p2(), get_y_value_p2())

        def get_v_line_p1():
            return DashedLine(get_x_point_p1(), get_graph_point_p1(), stroke_width=2)

        def get_v_line_p2():
            return DashedLine(get_x_point_p2(), get_graph_point_p2(), stroke_width=2)

        def get_h_line_p1():
            return DashedLine(get_graph_point_p1(), get_y_point_p1(), stroke_width=2)

        def get_h_line_p2():
            return DashedLine(get_graph_point_p2(), get_y_point_p2(), stroke_width=2)
        # Triangulo a
        input_triangle_p1 = RegularPolygon(n=3, start_angle=TAU / 4)
        output_triangle_p1 = RegularPolygon(n=3, start_angle=0)
        for triangle in input_triangle_p1, output_triangle_p1:
            triangle.set_fill(WHITE, 1)
            triangle.set_stroke(width=0)
            triangle.scale(0.1)
        # Triangulo b
        input_triangle_p2 = RegularPolygon(n=3, start_angle=TAU / 4)
        output_triangle_p2 = RegularPolygon(n=3, start_angle=0)
        for triangle in input_triangle_p2, output_triangle_p2:
            triangle.set_fill(WHITE, 1)
            triangle.set_stroke(width=0)
            triangle.scale(0.1)
        # Entradas y salidas del triangulo a
        input_triangle_update_p1 = ContinualUpdate(
            input_triangle_p1, lambda m: m.move_to(get_x_point_p1(), DOWN)
        )
        output_triangle_update_p1 = ContinualUpdate(
            output_triangle_p1, lambda m: m.move_to(get_y_point_p1(), LEFT)
        )
        # Entradas y salidas del triangulo b
        input_triangle_update_p2 = ContinualUpdate(
            input_triangle_p2, lambda m: m.move_to(get_x_point_p2(), DOWN)
        )
        output_triangle_update_p2 = ContinualUpdate(
            output_triangle_p2, lambda m: m.move_to(get_y_point_p2(), LEFT)
        )
        # Etiqueas y salidas del punto a
        x_label_p1 = TexMobject("a")
        x_label_update_p1 = ContinualUpdate(
            x_label_p1, lambda ma: ma.next_to(input_triangle_p1, DOWN, SMALL_BUFF)
        )

        output_label_p1 = TexMobject("f(a)")
        output_label_update_p1 = ContinualUpdate(
            output_label_p1, lambda ma: ma.next_to(
                output_triangle_p1, LEFT, SMALL_BUFF)
        )
        # Etiqueas y salidas del punto b
        x_label_p2 = TexMobject("b")
        x_label_update_p2 = ContinualUpdate(
            x_label_p2, lambda mb: mb.next_to(input_triangle_p2, DOWN, SMALL_BUFF)
        )

        output_label_p2 = TexMobject("f(b)")
        output_label_update_p2 = ContinualUpdate(
            output_label_p2, lambda mb: mb.next_to(
                output_triangle_p2, LEFT, SMALL_BUFF)
        )
        # V_lines de a
        v_line_p1 = get_v_line_p1()
        v_line_update_p1 = ContinualUpdate(
            v_line_p1, lambda vla: Transform(vla, get_v_line_p1()).update(1)
        )
        # V_lines de b
        v_line_p2 = get_v_line_p2()
        v_line_update_p2 = ContinualUpdate(
            v_line_p2, lambda vlb: Transform(vlb, get_v_line_p2()).update(1)
        )
        # h_lines de a
        h_line_p1 = get_h_line_p1()
        h_line_update_p1 = ContinualUpdate(
            h_line_p1, lambda hla: Transform(hla, get_h_line_p1()).update(1)
        )
        # h_lines de b
        h_line_p2 = get_h_line_p2()
        h_line_update_p2 = ContinualUpdate(
            h_line_p2, lambda hlb: Transform(hlb, get_h_line_p2()).update(1)
        )
        # Animacion del punto a
        graph_dot_p1 = Dot(color=TT_SIMBOLO)
        graph_dot_update_p1 = ContinualUpdate(
            graph_dot_p1, lambda ma: ma.move_to(get_graph_point_p1())
        )
        # Animacion del punto b
        graph_dot_p2 = Dot(color=TT_SIMBOLO)
        graph_dot_update_p2 = ContinualUpdate(
            graph_dot_p2, lambda mb: mb.move_to(get_graph_point_p2())
        )
        #
        self.play(
            ShowCreation(graph),
        )
        # Animacion del punto a
        self.add_foreground_mobject(graph_dot_p1)
        self.add_foreground_mobject(graph_dot_p2)
        self.play(
            DrawBorderThenFill(input_triangle_p1),
            Write(x_label_p1),
            ShowCreation(v_line_p1),
            GrowFromCenter(graph_dot_p1),
            ShowCreation(h_line_p1),
            Write(output_label_p1),
            DrawBorderThenFill(output_triangle_p1),
            DrawBorderThenFill(input_triangle_p2),
            Write(x_label_p2),
            ShowCreation(v_line_p2),
            GrowFromCenter(graph_dot_p2),
            ShowCreation(h_line_p2),
            Write(output_label_p2),
            DrawBorderThenFill(output_triangle_p2),
            run_time=0.5
        )
        self.add(
            input_triangle_update_p2,
            x_label_update_p2,
            graph_dot_update_p2,
            v_line_update_p2,
            h_line_update_p2,
            output_triangle_update_p2,
            output_label_update_p2,
        )
        ###################
        pendiente_recta = self.get_secant_slope_group(
            1.9, recta, dx = 1.4,
            df_label = None,
            dx_label = None,
            dx_line_color = PURPLE,
            df_line_color= ORANGE,
            )
        grupo_secante = self.get_secant_slope_group(
            1.5, graph, dx = 2,
            df_label = None,
            dx_label = None,
            dx_line_color = TT_FONDO_ROSA,
            df_line_color= TT_FONDO_VERDE,
            secant_line_color = RED,
        )
        start_dx = grupo_secante.kwargs["dx"]
        start_x = grupo_secante.kwargs["x"]
        def update_func_0(group, alpha):
            dx = interpolate(start_dx, 4, alpha)
            x = interpolate(start_x, 1.5, alpha)
            kwargs = dict(grupo_secante.kwargs)
            kwargs["dx"] = dx
            kwargs["x"] = x
            new_group = self.get_secant_slope_group(**kwargs)
            Transform(group, new_group).update(1)
            return group
        def update_func_1(group, alpha):
            dx = interpolate(start_dx, 0.001, alpha)
            x = interpolate(start_x, 1.5, alpha)
            kwargs = dict(grupo_secante.kwargs)
            kwargs["dx"] = dx
            kwargs["x"] = x
            new_group = self.get_secant_slope_group(**kwargs)
            Transform(group, new_group).update(1)
            return group

        self.add(
            input_triangle_update_p2,
            graph_dot_update_p2,
            v_line_update_p2,
            h_line_update_p2,
            output_triangle_update_p2,
        )
        self.play(FadeIn(grupo_secante))

        kwargs = {
            "x_min" : 4,
            "x_max" : 9,
            "fill_opacity" : 0.75,
            "stroke_width" : 0.25,
            #"start_color":PURPLE,
            #"end_color":ORANGE,
        }
        self.graph=graph
        iteraciones=6


        self.rect_list = self.get_riemann_rectangles_list(
            graph, iteraciones,start_color=PURPLE,end_color=ORANGE, **kwargs
        )
        flat_rects = self.get_riemann_rectangles(
            self.get_graph(lambda x : 0), dx = 0.5,start_color=invert_color(PURPLE),end_color=invert_color(ORANGE),**kwargs
        )
        rects = self.rect_list[0]
        self.transform_between_riemann_rects(
            flat_rects, rects, 
            replace_mobject_with_target_in_scene = True,
            run_time=0.9
        )
