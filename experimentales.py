from big_ol_pile_of_manim_imports import *

class TestArco(Scene):
    def construct(self):
        arco=Arc(PI/2,radius=3)
        linea_arco=Line(arco.points[-2],arco.points[-1],color=RED)
        puntas_flecha=self.add_tips(linea_arco)
        poligono=VMobject().set_points_as_corners([puntas_flecha[0].get_start(),
                                                   #puntas_flecha[2].get_end(),
                                                   puntas_flecha[1].get_start(),
                                                   puntas_flecha[1].get_end(),
                                                   puntas_flecha[0].get_start()]).set_fill(WHITE,1)
        linea_base=DashedLine(LEFT*4,RIGHT*4)
        linea_tope=Line(LEFT*0.15,RIGHT*0.15).rotate(arco.get_angle()).move_to(arco.points[-1])
        conjunto=VGroup(DashedMobject(arco),puntas_flecha,linea_tope).set_stroke(width=2.2)
        self.add(conjunto)

    def add_tips(self,linea,ang_flechas=30*DEGREES,tam_flechas=0.3):
        linea_referencia=Line(linea.get_start(),linea.get_end())
        vector_unitario=linea_referencia.get_unit_vector()

        punto_final1=linea.get_end()
        punto_inicial1=punto_final1-vector_unitario*tam_flechas
        punto_intermedio=punto_final1-vector_unitario*tam_flechas*0.6

        punto_inicial2=linea.get_start()
        punto_final2=punto_inicial2+vector_unitario*tam_flechas

        lin1_1=Line(punto_inicial1,punto_final1)
        lin1_2=lin1_1.copy()
        lin2_1=Line(punto_inicial2,punto_final2)
        lin2_2=lin2_1.copy()

        lin_int=Line(linea.get_end(),punto_final1-vector_unitario*tam_flechas*0.6)

        lin1_1.rotate(ang_flechas,about_point=punto_final1,about_edge=punto_final1)
        lin1_2.rotate(-ang_flechas,about_point=punto_final1,about_edge=punto_final1)

        lin2_1.rotate(ang_flechas,about_point=punto_inicial2,about_edge=punto_inicial2)
        lin2_2.rotate(-ang_flechas,about_point=punto_inicial2,about_edge=punto_inicial2)

        return VMobject(lin1_1,lin1_2)

class TestPlot(PlotScene):
    CONFIG = {
        "y_max" : 10,
        "y_min" : 0,
        "x_max" : 5,
        "x_min" : 0,
        "y_tick_frequency" : 1, 
        "x_tick_frequency" : 0.5, 
        "axes_color" : PURPLE_E, 
        "num_graph_anchor_points": 300,
        "y_labeled_nums":rango(0,10),
        "x_labeled_nums":rango(0,5,0.5),
        "x_label_decimal":1,
        "x_tick_size":0.035,
        "y_tick_size":0.035,
    }
    def construct(self):
        self.setup_axes(animate=False)
        graph =self.get_graph(lambda x : 1/x,
                                    color = TT_AZUL_T,
                                    x_min = 0.1,
                                    x_max = 5,
                                    ).set_stroke(None,2)
        self.play(
            ShowCreation(graph),
            run_time = 1
        )
        self.wait()

    def pre_setup(self):
        lineas1=VMobject()
        lineas2=VMobject()
        self.x_axis[:2].set_stroke(None,2)
        self.y_axis_label_mob.next_to(self.y_axis[1][-1],UP+RIGHT,buff=0.1)
        self.y_axis[:2].set_stroke(None,2)
        self.x_axis_label_mob.set_color(ORANGE)
        self.y_axis_label_mob.set_color(BLUE_D)
        self.y_axis[2].set_color(TEAL)
        for i in list(np.arange(self.x_min,self.x_max+self.x_tick_frequency,self.x_tick_frequency)):
            if i!=0:
                lin1=DashedLine(self.coords_to_point(i,self.y_min),self.coords_to_point(i,self.y_max))
                #lin1=DashedMobject(lin1)
                lineas1.add(lin1)
        for i in list(np.arange(self.y_min,self.y_max+self.y_tick_frequency,self.y_tick_frequency)):
            if i!=0:
                lin2=DashedLine(self.coords_to_point(self.x_min,i),self.coords_to_point(self.x_max,i))
                lineas2.add(lin2)
        self.lineas_punteadas=VMobject(lineas1,lineas2).set_color(GRAY).fade(0.5).set_stroke(None,1.5)

        self.play(Write(self.axes),
            *[GrowFromCenter(self.lineas_punteadas[i][j])for i in [0,1] 
                for j in range(len(self.lineas_punteadas[i]))],)

class Triangulo4(Scene):
    def construct(self):
        tr1=Polygon(LEFT*2,ORIGIN,UP*2)
        tr1.points[0:3]=LEFT*2
        tr1.points[3:6]=ORIGIN
        tr1.points[6:9]=UP*2
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
            Transform(med,sub_med).update(1)
            Transform(med2,sub_med2).update(1)
            Transform(med3,sub_med3).update(1)
            Transform(arco,new_arco).update(1)
            Transform(arco2,arco2b).update(1)

        def updatef2(grupo,alpha):
            new_tr1=Polygon(LEFT*2,ORIGIN,UP*2)
            dx = interpolate(0, 3, alpha)
            new_tr1.points[0:3]=LEFT*2
            new_tr1.points[3:6]=ORIGIN+RIGHT*dx
            new_tr1.points[6:9]=UP*2+RIGHT*dx
            Transform(grupo,new_tr1).update(1)

        self.wait()
        self.play(UpdateFromAlphaFunc(tr1,updatef2),
            UpdateFromFunc(med,updatef))
        #tr1.stretch_to_fit_width(1)
        #self.wait()
        #tr1.stretch_to_fit_height(3)
        self.wait()

class Triangulo2(Scene):
	def construct(self):
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
			Transform(med,sub_med).update(1)
			Transform(med2,sub_med2).update(1)
			Transform(med3,sub_med3).update(1)
			Transform(arco,new_arco).update(1)
			Transform(arco2,arco2b).update(1)
		self.wait()
		self.play(tr1.stretch_to_fit_width,4,tr1.stretch_to_fit_height,2,
			UpdateFromFunc(med,updatef))
		#tr1.stretch_to_fit_width(1)
		#self.wait()
		#tr1.stretch_to_fit_height(3)
		self.wait()

class PTexto(Scene):
    def construct(self):
        flecha=Arc(PI/2).add_tip()
        self.add(flecha)
        def update(grupo,alpha):
            dx = interpolate(0, 360*DEGREES, alpha)
            nuevo_grupo=Arc(PI/2).add_tip().rotate(dx,about_point=ORIGIN,
            about_edge=ORIGIN)
            Transform(grupo,nuevo_grupo).update(1)
            return grupo
        self.wait(0.5)
        self.play(UpdateFromAlphaFunc(flecha,update),run_time=5)
        self.wait(0.5)

class Perturbacion(ContinualAnimation):
    CONFIG = {
        "amplitude": 0.4,
        "jiggles_per_second": 1,
    }

    def __init__(self, group, **kwargs):
        for submob in group.submobjects:
            submob.jiggling_direction = rotate_vector(
                RIGHT, np.random.random() * TAU *1.5,
            )
            submob.jiggling_phase = np.random.random() * TAU *1.5
        ContinualAnimation.__init__(self, group, **kwargs)

    def update_mobject(self, dt):
        for submob in self.mobject.submobjects:
            submob.jiggling_phase += dt * self.jiggles_per_second * TAU
            submob.shift(
                self.amplitude *
                submob.jiggling_direction *
                np.sin(submob.jiggling_phase) * dt
            )

class Particula(Scene):
    def construct(self):
        punto=VGroup(Dot(radius=0.6).shift(LEFT+UP),Dot(radius=0.6).shift(RIGHT+DOWN),Dot(radius=0.6))
        punto2=punto.copy().shift(LEFT*2)
        self.play(GrowFromCenter(punto),GrowFromCenter(punto2))
        self.add(Perturbacion(punto),Perturbacion(punto2))
        self.wait(5)
        self.remove(Perturbacion(punto),Perturbacion(punto2))
        self.add(Perturbacion(punto,amplitude=0.6),Perturbacion(punto2,amplitude=0.6))
        self.wait(5)
        self.remove(Perturbacion(punto),Perturbacion(punto2))
        self.add(Perturbacion(punto,amplitude=0.8),Perturbacion(punto2,amplitude=0.8))
        self.wait(5)
        self.remove(Perturbacion(punto),Perturbacion(punto2))
        self.add(punto,punto2)
        self.wait(5)

class PerTexto(Scene):
    def construct(self):
        texto=Texto("Q","u","é","\\_","o","n","d","a","\\_","g","e","n","t","e")
        for i in [3,8]:
            texto[i].fade(1)
        texto_base=Texto("Qué\\_onda\\_gente")
        for i in range(len(texto)):
            texto[i].move_to(texto_base[i])
        self.play(Escribe(texto))
        self.add(*[Perturbacion(texto[i])for i in range(len(texto))])
        self.wait(5)

class TextoTemporal(Scene):
    def construct(self):
        texto=Texto("Aparente").scale(2.5)
        self.play(Escribe_y_desvanece(texto),run_time=3)
        self.wait()

class Dimensiones(Scene):
    def construct(self):
        rectangulo=Rectangle(width=5,height=3)
        rectangulo.rotate(30*DEGREES)
        linea=Line(LEFT*1.5,RIGHT*1.5)
        linea.rotate(20*DEGREES)
        linea.shift(LEFT*2)
        v_medicion=Medicion(linea,color=BLUE,dashed=False)
        self.play(ShowCreation(linea))
        self.play(GrowFromCenter(v_medicion))
        def update(grupo):
            angulo=linea.get_angle()
            tam_med=grupo[1].get_length()/2
            vu=linea.get_unit_vector()
            mr=rotation_matrix(PI/2,OUT)
            #grupo.rotate(angulo)
            grupo[0].put_start_and_end_on(linea.get_start(),linea.get_end())
            direccion=np.matmul(mr,vu)
            grupo[0].shift(direccion*0.3)
            origen1=grupo[0].get_end()
            fin1_1=origen1+direccion*tam_med
            fin1_2=origen1-direccion*tam_med
            grupo[1].put_start_and_end_on(fin1_1,fin1_2)

            origen2=grupo[0].get_start()
            fin2_1=origen2+direccion*tam_med
            fin2_2=origen2-direccion*tam_med
            grupo[2].put_start_and_end_on(fin2_1,fin2_2)


        self.play(linea.scale,2,linea.rotate,PI/8,linea.shift,RIGHT*3,
            UpdateFromFunc(
            v_medicion,update))
        self.wait(2)

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

class Temperatura(GraphScene):
    CONFIG = {
        "x_min" : 0,
        "x_axis_label" : "$t$",
        "y_axis_label" : "Temperature",
        "T_room" : 4,
        "include_solution" : False,
    }
    def construct(self):
        self.setup_axes()
        graph = self.get_graph(
            lambda t : 3*np.exp(-0.3*t) + self.T_room,
            color = RED
        )
        h_line = DashedLine(*[
            self.coords_to_point(x, self.T_room)
            for x in (self.x_min, self.x_max)
        ])
        T_room_label = TexMobject("T_{\\text{room}}")
        T_room_label.next_to(h_line, LEFT)

        ode = TexMobject(
            "\\frac{d\\Delta T}{dt} = -k \\Delta T"
        )
        ode.to_corner(UP+RIGHT)

        solution = TexMobject(
            "\\Delta T(", "t", ") = e", "^{-k", "t}"
        )
        solution.next_to(ode, DOWN, MED_LARGE_BUFF)
        solution.set_color_by_tex("t", YELLOW)
        solution.set_color_by_tex("Delta", WHITE)

        delta_T_brace = Brace(graph, RIGHT)
        delta_T_label = TexMobject("\\Delta T")
        delta_T_group = VGroup(delta_T_brace, delta_T_label)
        def update_delta_T_group(group):
            brace, label = group
            v_line = Line(
                graph.points[-1],
                graph.points[-1][0]*RIGHT + h_line.get_center()[1]*UP
            )
            brace.set_height(v_line.get_height())
            brace.next_to(v_line, RIGHT, SMALL_BUFF)
            label.set_height(min(
                label.get_height(),
                brace.get_height()
            ))
            label.next_to(brace, RIGHT, SMALL_BUFF)

        self.add(ode)
        self.play(
            Write(T_room_label),
            ShowCreation(h_line, run_time = 2)
        )
        if self.include_solution:
            self.play(Write(solution))
        graph_growth = ShowCreation(graph, rate_func = None)
        delta_T_group_update = UpdateFromFunc(
            delta_T_group, update_delta_T_group
        )
        self.play(
            GrowFromCenter(delta_T_brace),
            Write(delta_T_label),
        )
        self.play(graph_growth, delta_T_group_update, run_time = 15)
        self.wait(2)

class Layer(Scene):
    def construct(self):
        capa0=Square(color=RED,fill_opacity=0.5).scale(1.5)
        capa1=Square(color=BLUE,fill_opacity=0.5).scale(1.3)
        capa2=Circle(radius=1.5,fill_opacity=0.5,color=ORANGE)
        self.add(capa0,capa1,capa2)
        self.wait(3)
        self.bring_to_front(capa1) 
        self.wait()
        self.bring_to_front(capa0)
        self.wait()
        self.bring_to_back(capa0)
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
		question = TextMobject("Funciones 3D")
		question.set_width(FRAME_WIDTH - 3)
		question.to_edge(UP)
		self.set_camera_orientation(phi=75 * DEGREES)
		self.begin_ambient_camera_rotation()
		self.add_fixed_in_frame_mobjects(question.scale(0.4))
		self.play(Write(self.axes),Write(question))
		self.play(
		    Write(sphere),
		    #
		)
		self.wait()
		#'''
		self.play(ReplacementTransform(sphere,elipsoide))
		self.wait()
		self.play(ReplacementTransform(elipsoide,cono))
		self.wait()
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

class Superficies2(ThreeDScene):
    def construct(self):
        def esfera(radio,r_a=15,r_b=32):
            sphere = ParametricSurface(
            lambda u, v: np.array([
                radio*np.cos(u)*np.cos(v),
                radio*np.cos(u)*np.sin(v),
                radio*np.sin(u)
            ]),v_min=0,v_max=TAU,u_min=-PI/2,u_max=PI/2,checkerboard_colors=[RED_D, RED_E],
            resolution=(15, 32)).set_stroke(None,0)
            return sphere
        def sist_referencia(ORIGEN,dir_x=RIGHT,dir_y=UP,dir_z=OUT,ang_x=0,ang_y=0,ang_z=0):
            eje_x=Arrow(ORIGEN,ORIGEN+dir_x,buff=0).set_color(BLUE)
            eje_y=Arrow(ORIGEN,ORIGEN+dir_y,buff=0).set_color(RED)
            eje_z=Arrow(ORIGEN,ORIGEN+dir_z,buff=0).set_color(GREEN)
            vector_x=Line(ORIGEN,ORIGEN+dir_x).get_unit_vector()
            vector_y=Line(ORIGEN,ORIGEN+dir_y).get_unit_vector()
            vector_z=Line(ORIGEN,ORIGEN+dir_z).get_unit_vector()
            eje_x.rotate(ang_x,axis=vector_x)
            eje_y.rotate(ang_y,axis=vector_y)
            eje_z.rotate(ang_z,axis=vector_z)
            return VGroup(eje_x,eje_y,eje_z)

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
        semisphere = ParametricSurface(
            lambda u, v: np.array([
                3*np.cos(u)*np.cos(v),
                3*np.cos(u)*np.sin(v),
                3*np.sin(u)
            ]),v_min=0,v_max=PI,u_min=0,u_max=PI,checkerboard_colors=[BLUE, BLUE],
            resolution=(10, 16)).fade(0.5)
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
        sphere = ParametricSurface(
            lambda u, v: np.array([
                np.cos(u)*np.sin(v),
                np.sin(u)*np.sin(v),
                np.cos(v)
            ]),v_min=0,v_max=PI,u_min=0,u_max=PI,checkerboard_colors=[RED_D, RED_E],
            resolution=(15, 32)).set_fill(None,0.5)
        #sphere.shift(IN)
        #flat_earth=ImageMobject("flat_earth/flat_earth").set_height(7).move_to(ORIGIN)
        flat_earth_a=Circle(radius=1.5).set_fill(BLUE,0.5).set_stroke(BLUE,0.5)
        flat_earth_b=AnnularSector(inner_radius=1.5,outer_radius=3,angle=TAU).set_fill(GREEN,0.5).set_stroke(GREEN,0.5)
        flat_earth=VGroup(flat_earth_a,flat_earth_b)
        self.set_camera_orientation(phi=75 * DEGREES)
        #self.play(FadeIn(flat_earth))
        esfera1=esfera(0.1)
        pat=Patron(0.2,0.4,separacion=0.05,agregar_base=True,direccion="L",grosor=0.07).rotate(PI/2,axis=RIGHT).move_to(np.array([3,0,3]))
        pat.rotate(PI/4,axis=DOWN).set_color(WHITE)

        linea_base=Line(ORIGIN,pat[-1].get_center())
        vector_lb=linea_base.get_unit_vector()
        cuerda=Line(ORIGIN+vector_lb*3.3,pat[-1].get_center()).set_stroke(RED,2.3).set_shade_in_3d(True)

        esfera1.move_to(cuerda.get_start())


        linea_pre_giro=Line(DOWN,UP)
        vector_giro=linea_pre_giro.get_unit_vector()

        sist_ref1=sist_referencia(ORIGIN)
        sist_ref2=sist_referencia(np.array([3,0,3]),dir_z=-vector_lb,dir_x=rotate_vector(-vector_lb,PI/2,axis=UP),ang_z=PI/2,ang_x=PI/2)


        self.add(self.axes,cuerda,esfera1,semisphere,pat,sist_ref1,sist_ref2)
        def update(esfera):
            esfera.move_to(cuerda.get_start())





        self.begin_ambient_camera_rotation(rate=0.15)
        #semisphere[0:31].set_color(ORANGE)
        #'''
        self.play(cuerda.rotate,-15*DEGREES,{"about_point":cuerda.get_end(),"about_edge":cuerda.get_end(),"axis":DOWN},
            UpdateFromFunc(esfera1,update))
        self.play(girar_cuerda(cuerda),
            UpdateFromFunc(esfera1,update))
        self.play(girar_cuerda(cuerda),
            UpdateFromFunc(esfera1,update))

        pendulo=VGroup(pat,cuerda,esfera1)
        sistema_pendulo=VGroup(pat,cuerda,esfera1,sist_ref2)
        self.play(girar_sistema(sistema_pendulo))
        '''
        self.play(girar_cuerda(cuerda),
            UpdateFromFunc(esfera1,update))
        #self.wait()
        #'''

        #self.play(Transform(curva2,curva1))
        
        #'''

class Domo(Scene):
    def construct(self):
        linead=Line(UR,DR)
        lineai=Line(UL,DL)
        grupo=VMobject(linead,lineai).set_fill(RED,1)
        anillo=AnnularSector().set_stroke(RED,3).set_fill(ORANGE,0.5)
        domo_grupo=VGroup()
        num_divisiones=1
        for alpha in range(0,90,num_divisiones):
            partdomo=ParteDomo(desfase=alpha*DEGREES,angle=num_divisiones*DEGREES).set_stroke(None,1.5)
            domo_grupo.add(partdomo)

        domo_grupo.set_color_by_gradient(RED,YELLOW,GREEN)
        linea=Line(ORIGIN,UP*domo_grupo.get_height()).shift(RIGHT*domo_grupo.get_width()*1.5/2)
        mas_denso=Formula("\\rho_{\\text{inferior}}").move_to(linea.get_start()).set_color(domo_grupo[0].get_color())
        menos_denso=Formula("\\rho_{\\text{superior}}").move_to(linea.get_end()).set_color(domo_grupo[-1].get_color())

        comparacion1=Formula("\\rho_{\\text{inferior}}",">","\\rho_{\\text{superior}}").shift(DOWN*0.5+LEFT*4.5)
        comparacion1[0].set_color(mas_denso.get_color())
        comparacion1[-1].set_color(menos_denso.get_color())



        #partdomo1=ParteDomo(desfase=0)
        #partdomo2=ParteDomo(desfase=10)
        
        self.add(domo_grupo,mas_denso,menos_denso)
        self.play(ReplacementTransform(mas_denso[:].copy(),comparacion1[0],path_arc=-PI/2),
                  ReplacementTransform(menos_denso[:].copy(),comparacion1[-1],path_arc=PI/2),
                  Write(comparacion1[1]),run_time=2.5
                  )
        #self.play(ShowCreation(domo_grupo))
        self.wait()



class PruebaFlecha(Scene):
    def construct(self):
        dot1=Dot()
        dot2=Dot().shift(UP*2)
        flecha=Flecha(dot1,dot2,buff=0.1)
        self.add(dot1,dot2)

        self.play(GrowArrow(flecha))
        self.wait()

class FiguraPunteada(Scene):
    def construct(self):
        pre_cuadro=VMobject()
        pre_cuadro.set_points_as_corners([ORIGIN,LEFT,UP+LEFT,UP])
        pre_cuadro=Circle(radius=3)
        cuadro=DashedMobject(pre_cuadro)
        cuadro_c=Circle(radius=3)
        self.play(ShowCreation(cuadro))
        self.play(Transform(cuadro[0].copy(),cuadro_c))
        self.wait()
