from big_ol_pile_of_manim_imports import *


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

		titulo=Texto("\\sc Animar mecanismos",color=WHITE).scale(1.5).to_corner(UL).shift(RIGHT)
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
		cuadro_negro=Rectangle(width=FRAME_WIDTH,height=FRAME_HEIGHT).set_fill(BLACK,0).set_stroke(None,0)
		self.add_foreground_mobject(cuadro_negro)
		self.play(cuadro_negro.set_fill,None,1)
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

class EscenaMusica(MusicalScene):
    def construct(self):
        self.teclado_transparente=self.definir_teclado(4,self.prop,0).set_stroke(None,0)
        self.teclado_base=self.definir_teclado(4,self.prop,1)
        self.teclado_base.move_to(ORIGIN+DOWN*3)
        self.teclado_transparente.move_to(ORIGIN+DOWN*3)

        self.wait(0.3)
        self.agregar_escenario()

        self.primer_paso(simbolos_faltantes=[14,15,16,17,18,19,20,21])
        self.wait()
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
            LaggedStart(DrawBorderThenFill,self.teclado_base),LaggedStart(DrawBorderThenFill,self.teclado_transparente)
            )
        self.play(*[GrowFromCenter(x)for x in self.grupoA])



    def intervalos(self):
        i6m_v=self.intervalo_v(21,15,"8\\rm J")
        i5J_v=self.intervalo_v(25,29,"3-",direccion=RIGHT)

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
            run_time=1
        )
        self.remove_foreground_mobjects(self.teclado_transparente)
        self.remove_foreground_mobjects(self.teclado_base)
        self.remove(self.teclado_transparente)
        self.mandar_frente_sostenido_parcial(4,self.teclado_base)
        self.play(
            LaggedStart(FadeOutAndShiftDown,self.teclado_base,run_time=1),
            )

class Ejemplo1(Scene):
    def construct(self):
        titulo=Texto("Se especializa en animaciones de car\\'acter matem\\'atico.").to_edge(UP)
        ul=underline(titulo)

        tr1=Polygon(LEFT*2,ORIGIN,UP*2)
        tr1.move_to(Dot())
        med=Medicion(Line(tr1.points[0],tr1.points[3]),invertir=True,dashed=True).add_tips().add_letter("x",buff=-3.2)
        med2=Medicion(Line(tr1.points[3],tr1.points[6]),invertir=True,dashed=True).add_tips().add_letter("y",buff=-2.6)
        med3=Medicion(Line(tr1.points[0],tr1.points[6]),dashed=True).add_tips().add_letter("z",buff=1.2)
        ang_alpha=np.arctan(Line(tr1.points[3],tr1.points[6]).get_length()/Line(tr1.points[0],tr1.points[3]).get_length())
        arco=Arc(ang_alpha,arc_center=tr1.points[0])
        arco2=Arc(np.arctan(Line(tr1.points[0],tr1.points[3]).get_length()/Line(tr1.points[3],tr1.points[6]).get_length()),arc_center=tr1.points[6],start_angle=ang_alpha)
        arco2.rotate(180*DEGREES,about_point=tr1.points[6],about_edge=tr1.points[6])
        self.add(tr1,med,med2,med3,arco,arco2)
        def updatef(self):
            sub_med=Medicion(Line(tr1.points[0],tr1.points[3]),invertir=True,dashed=True).add_tips().add_letter("x",buff=-3.2)
            sub_med2=Medicion(Line(tr1.points[3],tr1.points[6]),invertir=True,dashed=True).add_tips().add_letter("y",buff=-2.6)
            sub_med3=Medicion(Line(tr1.points[0],tr1.points[6]),dashed=True).add_tips().add_letter("z",buff=1.2)
            new_arco=Arc(np.arctan(Line(tr1.points[3],tr1.points[6]).get_length()/Line(tr1.points[0],tr1.points[3]).get_length()),arc_center=tr1.points[0])
            new_ang_alpha=np.arctan(Line(tr1.points[3],tr1.points[6]).get_length()/Line(tr1.points[0],tr1.points[3]).get_length())
            arco2b=Arc(np.arctan(Line(tr1.points[0],tr1.points[3]).get_length()/Line(tr1.points[3],tr1.points[6]).get_length()),arc_center=tr1.points[6],start_angle=new_ang_alpha)
            arco2b.rotate(180*DEGREES,about_point=tr1.points[6],about_edge=tr1.points[6])
            med.become(sub_med)
            med2.become(sub_med2)
            med3.become(sub_med3)
            arco.become(new_arco)
            arco2.become(arco2b)
            tr1.move_to(ORIGIN)
        self.wait()
        self.play(
            tr1.stretch_to_fit_width,6,
            tr1.stretch_to_fit_height,3.5,
            UpdateFromFunc(med,updatef))
        tmz=med3[-1].copy()
        tmy=med2[-1].copy()
        tmx=med[-1].copy()
        formula=Formula("z","^2=","x","^2+","y","^2")
        formula.next_to(tr1,DOWN,buff=1)
        self.play(
            Escribe(titulo),
            ShowCreation(ul)
            )
        self.play(
            ReplacementTransform(tmx[:],formula[2]),
            ReplacementTransform(tmy[:],formula[4]),
            ReplacementTransform(tmz[:],formula[0]),
            run_time=2
            )
        self.play(
            *[Escribe(formula[i][:])for i in [1,3,5]]
            )
        #self.add(formula)
        todos_objetos=VGroup(*self.mobjects)
        self.play(
            todos_objetos.shift,LEFT*FRAME_WIDTH)
        self.wait()

class EjemploGrafica(GraphScene):
    CONFIG = {
        "y_max": 8,
        "y_axis_height": 5,
    }

    def construct(self):
        self.add_title()
        self.show_function_graph()
        #self.otra_definicion()

    def add_title(self):
        title = self.title = TextMobject("\\underline{\\sc Visualizaci\\'on de la Derivada}")
        title.to_edge(UP)
        self.add_foreground_mobject(title)
        h_line = Line(LEFT, RIGHT)
        h_line.set_height(FRAME_WIDTH - 2 * LARGE_BUFF)
        h_line.next_to(title, DOWN)
        h_line.set_stroke(WHITE,3)
        title.to_edge(UP+LEFT)
        title.shift(RIGHT)

        self.add(title)
        self.lin_h = h_line

    def show_function_graph(self):
        self.setup_axes()

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
        self.play(
            DrawBorderThenFill(input_triangle_p1),
            Write(x_label_p1),
            ShowCreation(v_line_p1),
            GrowFromCenter(graph_dot_p1),
            run_time=0.5
        )
        self.add_foreground_mobject(graph_dot_p1)
        self.play(
            ShowCreation(h_line_p1),
            Write(output_label_p1),
            DrawBorderThenFill(output_triangle_p1),
            run_time=0.5
        )
        # Animacion del punto b
        self.play(
            DrawBorderThenFill(input_triangle_p2),
            Write(x_label_p2),
            ShowCreation(v_line_p2),
            GrowFromCenter(graph_dot_p2),
            run_time=0.5
        )
        self.add_foreground_mobject(graph_dot_p2)
        self.play(
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
        grupo_secantep = self.get_secant_slope_group(
            1.5, graph, dx = 2,
            df_label = None,
            dx_label = None,
            dx_line_color = PURPLE,
            df_line_color=ORANGE,
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

        self.play(FadeIn(grupo_secante))
        self.add(
            input_triangle_update_p2,
            graph_dot_update_p2,
            v_line_update_p2,
            h_line_update_p2,
            output_triangle_update_p2,
        )
        self.play(
                
                )
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
        self.wait()


        kwargs = {
            "x_min" : 2,
            "x_max" : 8,
            "fill_opacity" : 0.75,
            "stroke_width" : 0.25,
        }
        self.graph=graph
        iteraciones=6


        self.rect_list = self.get_riemann_rectangles_list(
            graph, iteraciones, **kwargs
        )
        flat_rects = self.get_riemann_rectangles(
            self.get_graph(lambda x : 0), dx = 0.5, **kwargs
        )
        rects = self.rect_list[0]
        rects.save_state()
        self.transform_between_riemann_rects(
            flat_rects, rects, 
            replace_mobject_with_target_in_scene = True,
        )
        for j in range(1,6):
            self.transform_between_riemann_rects(
            self.rect_list[j-1], self.rect_list[j], dx=1,
            replace_mobject_with_target_in_scene = True,
            )
        self.wait()
        cuadro_negro=Rectangle(width=FRAME_WIDTH,height=FRAME_HEIGHT).set_fill(BLACK,0).set_stroke(None,0)
        self.add_foreground_mobject(cuadro_negro)
        self.play(cuadro_negro.set_fill,None,1)
        self.wait()
