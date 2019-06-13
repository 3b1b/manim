from big_ol_pile_of_manim_imports import *

class Llaves(Scene):
    def construct(self):
        cuadro=Square()
        brazo=Medicion(Line(cuadro.get_corner(DL),cuadro.get_corner(UL)),dashed=True).add_tips()
        self.play(Write(cuadro),Write(brazo))
        texto=brazo.get_text("hola",buff=0.7)
        self.play(Write(texto))

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

class Triangulo(Scene):
	def construct(self):
		tr1=Polygon(LEFT*2,ORIGIN,UP*2)
		tr1.move_to(Dot())
		med=Medicion(Line(tr1.points[0],tr1.points[3]),invertir=True,dashed=True).add_tips().add_letter("x",buff=-3.2)
		med2=Medicion(Line(tr1.points[3],tr1.points[6]),invertir=True,dashed=True).add_tips().add_letter("y",buff=-2.6)
		med3=Medicion(Line(tr1.points[0],tr1.points[6]),dashed=True).add_tips().add_letter("z",buff=1.2)
		self.add(tr1,med,med2,med3)
		def updatef(self):
			sub_med=Medicion(Line(tr1.points[0],tr1.points[3]),invertir=True,dashed=True).add_tips().add_letter("x",buff=-3.2)
			sub_med2=Medicion(Line(tr1.points[3],tr1.points[6]),invertir=True,dashed=True).add_tips().add_letter("y",buff=-2.6)
			sub_med3=Medicion(Line(tr1.points[0],tr1.points[6]),dashed=True).add_tips().add_letter("z",buff=1.2)
			Transform(med,sub_med).update(1)
			Transform(med2,sub_med2).update(1)
			Transform(med3,sub_med3).update(1)
		self.wait()
		self.play(tr1.stretch_to_fit_width,4,tr1.shift,LEFT*4,tr1.rotate,PI/4,
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

class P2(Scene):
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

class P1(Scene):
    def construct(self):
        flecha=Arc(PI/2).add_tip().scale(2)
        self.add(flecha)
        def update(grupo,alpha):
            dx = interpolate(0, 360*DEGREES, alpha)
            nuevo_grupo=Arc(PI/2).add_tip().rotate(dx,about_point=ORIGIN,
            about_edge=ORIGIN)
            grupo.become(nuevo_grupo)
            return grupo
        self.wait(0.5)
        self.play(UpdateFromAlphaFunc(flecha,update),run_time=5)
        self.wait(0.5)

class Triangulo3(Scene):
    def construct(self):
        tr1=VMobject().set_points_as_corners([LEFT*2,ORIGIN,UP*2,LEFT*2])
        #tr1.points[3:6]=RIGHT*2
        tr1.points[3:6]=RIGHT*2
        tr1.points[6:9]=RIGHT*2+UP*2


        p1=Dot()
        p2=Dot(color=RED)
        p3=Dot(color=BLUE)
        p1.move_to(tr1.points[0])
        p2.move_to(tr1.points[3])
        p3.move_to(tr1.points[6])
        self.add(tr1,p1,p2,p3)
        self.wait()

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
        for i in rango(self.x_min,self.x_max,self.x_tick_frequency):
            if i!=0:
                lin1=DashedLine(self.coords_to_point(i,self.y_min),self.coords_to_point(i,self.y_max))
                lineas1.add(lin1)
        for i in rango(self.y_min,self.y_max,self.y_tick_frequency):
            if i!=0:
                lin2=DashedLine(self.coords_to_point(self.x_min,i),self.coords_to_point(self.x_max,i))
                lineas2.add(lin2)
        self.lineas_punteadas=VMobject(lineas1,lineas2).set_color(GRAY).fade(0.5).set_stroke(None,1.5)

        self.play(Write(self.axes),
            *[GrowFromCenter(self.lineas_punteadas[i][j])for i in [0,1] 
                for j in range(len(self.lineas_punteadas[i]))],)

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
        self.play(ShowCreation(conjunto))
        self.wait()

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

class TestDedo1(Scene):
    def construct(self):
        dedo=Dedo1().flip()#.set_fill(opacity=0).set_stroke(width=2)
        ec=Formula("ax+b=c")
        dedo.next_to(ec,RIGHT,buff=0.8)
        self.play(Escribe(ec))
        self.play(FadeInFrom(dedo,RIGHT))
        self.wait()

class TestDedo2(Scene):
    def construct(self):
        dedo=Dedo_i2()#.set_fill(opacity=0).set_stroke(width=2)
        ec=Formula("ax+b=c")
        dedo.next_to(ec,RIGHT,buff=0.8)
        self.play(Escribe(ec))
        self.play(FadeInFrom(dedo,RIGHT))
        self.wait()

class ZoomT(ZoomedScene):
    CONFIG = {
        "show_basis_vectors": False,
        "show_coordinates": True,
        "zoom_factor": 0.3,
        "zoomed_display_height": 1,
        "zoomed_display_width": 6,
    }

    def setup(self):
        ZoomedScene.setup(self)

    def construct(self):
        grilla=Grilla()
        #self.add_foreground_mobject(grilla)
        texto1=Texto("Undolatory theory",color=RED)
        texto2=Texto("Experimento de Airy",color=PURPLE)

        conj_texto1=VGroup(texto1,texto2)
        conj_texto1.arrange_submobjects(DOWN,aligned_edge=LEFT)



        imagen=ImageMobject("flat_earth/airy3")
        imagen.set_height(7)
        imagen.shift(LEFT*3)
        self.add(imagen)

        zoomed_camera = self.zoomed_camera
        zoomed_display = self.zoomed_display
        frame = zoomed_camera.frame

        frame.move_to(3.05 * LEFT + 1.4 * UP)
        frame.set_color(WHITE)

        zoomed_display.display_frame.set_color(WHITE)

        zd_rect = BackgroundRectangle(
            zoomed_display,
            fill_opacity=0,
            buff=MED_SMALL_BUFF,
        )

        self.add_foreground_mobject(zd_rect)

        zd_rect.anim = UpdateFromFunc(
            zd_rect,
            lambda rect: rect.replace(zoomed_display).scale(1.1)
        )
        #zd_rect.next_to(FRAME_HEIGHT * RIGHT, UP)

        zoomed_display.move_to(ORIGIN+RIGHT*3+UP*3)

        conj_texto1.next_to(zoomed_display,DOWN)

        self.play(ShowCreation(frame))
        self.activate_zooming()
        #'''
        self.play(
            self.get_zoomed_display_pop_out_animation(),
            zd_rect.anim
        )
        self.play(Escribe(texto1))
        #'''
        self.wait()
        '''
        self.play(
            #self.get_zoomed_display_pop_out_animation(),
            zd_rect.anim,
            rate_func=lambda t: smooth(1-t)
        )
        #'''
        self.play(
            frame.shift,UP,
            )
        self.play(Escribe(texto2))
        self.wait()
        self.play(
            self.get_zoomed_display_pop_out_animation(),
            zd_rect.anim,
            rate_func=lambda t: smooth(1-t)
        )
        self.play(
            zoomed_display.display_frame.fade,1,
            frame.fade,1
            )
        self.wait()

class Pantalla(Scene):
    def construct(self):
        height = self.camera.get_pixel_height()
        width = self.camera.get_pixel_width()
        print("%s x %s"%(height,width))
        self.add(Square())

class ComputationalNetwork(MovingCameraScene):
    CONFIG = {
        "x_color": YELLOW,
        "f_color": BLUE,
        "g_color": GREEN,
        "h_color": RED,
    }

    def construct(self):
        self.draw_network()
        self.walk_through_parts()
        self.write_dh_dx_goal()
        self.feed_forward_input()
        self.compare_x_and_h_wiggling()
        self.expand_out_h_as_function_of_x()
        self.show_four_derivatives()
        self.show_chain_rule()
        self.talk_through_mvcr_parts()
        self.plug_in_expressions()
        self.plug_in_values()
        self.discuss_meaning_of_result()

    def draw_network(self):
        x = TexMobject("x")
        f_formula = TexMobject("f", "=", "x", "^2")
        g_formula = TexMobject("g", "=", "\\cos(\\pi", "x", ")")
        h_formula = TexMobject("h", "=", "f", "^2", "g")

        self.tex_to_color_map = {
            "x": self.x_color,
            "f": self.f_color,
            "g": self.g_color,
            "h": self.h_color,
        }

        formulas = VGroup(x, f_formula, g_formula, h_formula)
        formula_groups = VGroup()
        for formula in formulas:
            formula.box = SurroundingRectangle(formula)
            formula.box.set_color(WHITE)
            formula.group = VGroup(formula, formula.box)
            formula.set_color_by_tex_to_color_map(
                self.tex_to_color_map
            )
            formula_groups.add(formula.group)
        f_formula.box.match_width(
            g_formula.box, stretch=True, about_edge=LEFT
        )

        fg_group = VGroup(f_formula.group, g_formula.group)
        fg_group.arrange_submobjects(DOWN, buff=LARGE_BUFF)
        fg_group.to_edge(UP)
        x.group.next_to(fg_group, LEFT, buff=2)
        h_formula.group.next_to(fg_group, RIGHT, buff=2)

        xf_line = Line(x.box.get_right(), f_formula.box.get_left())
        xg_line = Line(x.box.get_right(), g_formula.box.get_left())
        fh_line = Line(f_formula.box.get_right(), h_formula.box.get_left())
        gh_line = Line(g_formula.box.get_right(), h_formula.box.get_left())

        graph_edges = VGroup(
            xf_line, xg_line, fh_line, gh_line
        )

        self.play(
            Write(x),
            FadeIn(x.box),
        )
        self.play(
            ShowCreation(xf_line),
            ShowCreation(xg_line),
            ReplacementTransform(x.box.copy(), f_formula.box),
            ReplacementTransform(x.box.copy(), g_formula.box),
        )
        self.play(
            Write(f_formula),
            Write(g_formula),
        )
        self.play(
            ShowCreation(fh_line),
            ShowCreation(gh_line),
            ReplacementTransform(f_formula.box.copy(), h_formula.box),
            ReplacementTransform(g_formula.box.copy(), h_formula.box),
        )
        self.play(Write(h_formula))
        self.wait()

        network = VGroup(formula_groups, graph_edges)

        self.set_variables_as_attrs(
            x, f_formula, g_formula, h_formula,
            xf_line, xg_line, fh_line, gh_line,
            formulas, formula_groups,
            graph_edges, network
        )

    def walk_through_parts(self):
        x = self.x
        f_formula = self.f_formula
        g_formula = self.g_formula
        h_formula = self.h_formula

        def indicate(mob):
            return ShowCreationThenDestructionAround(
                mob,
                surrounding_rectangle_config={
                    "buff": 0.5 * SMALL_BUFF,
                    "color": mob.get_color()
                }
            )

        for formula in f_formula, g_formula:
            self.play(indicate(formula[0]))
            self.play(ReplacementTransform(
                x.copy(),
                formula.get_parts_by_tex("x"),
                path_arc=PI / 3
            ))
            self.wait()

        self.play(indicate(h_formula[0]))
        self.play(ReplacementTransform(
            f_formula[0].copy(),
            h_formula.get_part_by_tex("f"),
            path_arc=PI / 3
        ))
        self.play(ReplacementTransform(
            g_formula[0].copy(),
            h_formula.get_part_by_tex("g"),
            path_arc=PI / 3
        ))
        self.wait()

    def write_dh_dx_goal(self):
        deriv = TexMobject(
            "{dh", "\\over", "dx}", "(", "2", ")"
        )
        deriv.set_color_by_tex_to_color_map(
            self.tex_to_color_map
        )
        deriv.scale(1.5)
        deriv.move_to(DOWN)

        self.play(FadeInFromDown(deriv[:3]))
        self.play(ShowCreationThenDestructionAround(deriv[:3]))
        self.wait(2)
        self.play(Write(deriv[3:]))
        self.wait()

        self.dh_dx_at_two = deriv

    def feed_forward_input(self):
        formula_groups = self.formula_groups
        x, f_formula, g_formula, h_formula = self.formulas
        dh_dx_at_two = self.dh_dx_at_two

        values = [2, 4, 1, 16]
        value_labels = VGroup()
        for formula_group, value in zip(formula_groups, values):
            label = TexMobject("=", str(value))
            eq, value_mob = label
            eq.rotate(90 * DEGREES)
            eq.next_to(value_mob, UP, SMALL_BUFF)
            var = formula_group[0][0]
            label[1].match_color(var)
            # label.next_to(formula_group, DOWN, SMALL_BUFF)
            label.next_to(var, DOWN, SMALL_BUFF)
            eq.add_background_rectangle(buff=SMALL_BUFF, opacity=1)
            value_labels.add(label)
        x_val_label, f_val_label, g_val_label, h_val_label = value_labels
        two, four, one, sixteen = [vl[1] for vl in value_labels]

        self.play(
            ReplacementTransform(
                dh_dx_at_two.get_part_by_tex("2").copy(),
                two,
            ),
            Write(x_val_label[0])
        )
        self.wait()

        two_copy1 = two.copy()
        two_copy2 = two.copy()
        four_copy = four.copy()
        one_copy = one.copy()
        x_in_f = f_formula.get_part_by_tex("x")
        x_in_g = g_formula.get_part_by_tex("x")
        f_in_h = h_formula.get_part_by_tex("f")
        g_in_h = h_formula.get_part_by_tex("g")

        self.play(
            two_copy1.move_to, x_in_f, DOWN,
            x_in_f.set_fill, {"opacity": 0},
        )
        self.wait()
        self.play(Write(f_val_label))
        self.wait()
        self.play(
            two_copy2.move_to, x_in_g, DOWN,
            x_in_g.set_fill, {"opacity": 0},
        )
        self.wait()
        self.play(Write(g_val_label))
        self.wait()

        self.play(
            four_copy.move_to, f_in_h, DOWN,
            f_in_h.set_fill, {"opacity": 0},
        )
        self.play(
            one_copy.move_to, g_in_h, DOWN,
            g_in_h.set_fill, {"opacity": 0},
        )
        self.wait()
        self.play(Write(h_val_label))
        self.wait()

        self.value_labels = value_labels
        self.revert_to_formula_animations = [
            ApplyMethod(term.set_fill, {"opacity": 1})
            for term in (x_in_f, x_in_g, f_in_h, g_in_h)
        ] + [
            FadeOut(term)
            for term in (two_copy1, two_copy2, four_copy, one_copy)
        ]

    def compare_x_and_h_wiggling(self):
        x_val = self.value_labels[0][1]
        h_val = self.value_labels[3][1]

        x_line = NumberLine(
            x_min=0,
            x_max=4,
            include_numbers=True,
            numbers_to_show=[0, 2, 4],
            unit_size=0.75,
        )
        x_line.next_to(
            x_val, DOWN, LARGE_BUFF,
            aligned_edge=RIGHT
        )
        h_line = NumberLine(
            x_min=0,
            x_max=32,
            include_numbers=True,
            numbers_with_elongated_ticks=[0, 16, 32],
            numbers_to_show=[0, 16, 32],
            tick_frequency=1,
            tick_size=0.05,
            unit_size=1.0 / 12,
        )
        h_line.next_to(
            h_val, DOWN, LARGE_BUFF,
            aligned_edge=LEFT
        )

        x_dot = Dot(color=self.x_color)
        x_dot.move_to(x_line.number_to_point(2))
        x_arrow = Arrow(self.x.get_bottom(), x_dot.get_top())
        x_arrow.match_color(x_dot)

        h_dot = Dot(color=self.h_color)
        h_dot.move_to(h_line.number_to_point(16))
        h_arrow = Arrow(self.h_formula[0].get_bottom(), h_dot.get_top())
        h_arrow.match_color(h_dot)

        self.play(
            ShowCreation(x_line),
            ShowCreation(h_line),
        )
        self.play(
            GrowArrow(x_arrow),
            GrowArrow(h_arrow),
            ReplacementTransform(x_val.copy(), x_dot),
            ReplacementTransform(h_val.copy(), h_dot),
        )
        self.wait()
        for x in range(2):
            self.play(
                x_dot.shift, 0.25 * RIGHT,
                h_dot.shift, 0.35 * RIGHT,
                rate_func=wiggle,
                run_time=1,
            )

        self.set_variables_as_attrs(
            x_line, h_line,
            x_dot, h_dot,
            x_arrow, h_arrow,
        )

    def expand_out_h_as_function_of_x(self):
        self.play(*self.revert_to_formula_animations)

        deriv = self.dh_dx_at_two

        expanded_formula = TexMobject(
            "h = x^4 \\cos(\\pi x)",
            tex_to_color_map=self.tex_to_color_map
        )
        expanded_formula.move_to(deriv)
        cross = Cross(expanded_formula)

        self.play(
            FadeInFromDown(expanded_formula),
            deriv.scale, 1.0 / 1.5,
            deriv.shift, DOWN,
        )
        self.wait()
        self.play(ShowCreation(cross))
        self.wait()
        self.play(
            FadeOut(VGroup(expanded_formula, cross)),
            deriv.shift, UP,
        )
        for edge in self.graph_edges:
            self.play(ShowCreationThenDestruction(
                edge.copy().set_stroke(YELLOW, 6)
            ))

    def show_four_derivatives(self):
        lines = self.graph_edges
        xf_line, xg_line, fh_line, gh_line = lines

        df_dx = TexMobject("df", "\\over", "dx")
        dg_dx = TexMobject("dg", "\\over", "dx")
        dh_df = TexMobject("\\partial h", "\\over", "\\partial f")
        dh_dg = TexMobject("\\partial h", "\\over", "\\partial g")
        derivatives = VGroup(df_dx, dg_dx, dh_df, dh_dg)

        df_dx.next_to(xf_line.get_center(), UP, SMALL_BUFF)
        dg_dx.next_to(xg_line.get_center(), DOWN, SMALL_BUFF)
        dh_df.next_to(fh_line.get_center(), UP, SMALL_BUFF)
        dh_dg.next_to(gh_line.get_center(), DOWN, SMALL_BUFF)

        partial_terms = VGroup(
            dh_df[0][0],
            dh_df[2][0],
            dh_dg[0][0],
            dh_dg[2][0],
        )
        partial_term_rects = VGroup(*[
            SurroundingRectangle(pt, buff=0.05)
            for pt in partial_terms
        ])
        partial_term_rects.set_stroke(width=0)
        partial_term_rects.set_fill(TEAL, 0.5)

        self.play(FadeOut(self.value_labels))
        for derivative in derivatives:
            derivative.set_color_by_tex_to_color_map(self.tex_to_color_map)
            derivative.add_to_back(derivative.copy().set_stroke(BLACK, 5))
            self.play(FadeInFromDown(derivative))
            self.wait()

        self.play(
            LaggedStart(FadeIn, partial_term_rects),
            Animation(derivatives)
        )
        self.wait()
        self.play(
            LaggedStart(FadeOut, partial_term_rects),
            Animation(derivatives)
        )

        self.derivatives = derivatives

    def show_chain_rule(self):
        dh_dx_at_two = self.dh_dx_at_two
        dh_dx = dh_dx_at_two[:3]
        at_two = dh_dx_at_two[3:]
        derivatives = self.derivatives.copy()
        df_dx, dg_dx, dh_df, dh_dg = derivatives

        frame = self.camera_frame

        self.play(
            frame.shift, 3 * UP,
            dh_dx.to_edge, UP,
            dh_dx.shift, 3 * LEFT + 3 * UP,
            at_two.set_fill, {"opacity": 0},
        )

        for deriv in derivatives:
            deriv.generate_target()
        rhs = VGroup(
            TexMobject("="),
            df_dx.target, dh_df.target,
            TexMobject("+"),
            dg_dx.target, dh_dg.target
        )
        rhs.arrange_submobjects(
            RIGHT,
            buff=2 * SMALL_BUFF,
        )
        rhs.next_to(dh_dx, RIGHT)
        for deriv in derivatives:
            y = rhs[0].get_center()[1]
            alt_y = deriv.target[2].get_center()[1]
            deriv.target.shift((y - alt_y) * UP)

        self.play(
            Write(rhs[::3]),
            LaggedStart(MoveToTarget, derivatives)
        )
        self.wait()

        self.chain_rule_derivatives = derivatives
        self.chain_rule_rhs = rhs

    def talk_through_mvcr_parts(self):
        derivatives = self.derivatives
        cr_derivatives = self.chain_rule_derivatives

        df_dx, dg_dx, dh_df, dh_dg = cr_derivatives

        df, dx1 = df_dx[1::2]
        dg, dx2 = dg_dx[1::2]
        del_h1, del_f = dh_df[1::2]
        del_h2, del_g = dh_dg[1::2]
        terms = VGroup(df, dx1, dg, dx2, del_h1, del_f, del_h2, del_g)
        for term in terms:
            term.rect = SurroundingRectangle(
                term,
                buff=0.5 * SMALL_BUFF,
                stroke_width=0,
                fill_color=TEAL,
                fill_opacity=0.5
            )
        for derivative in derivatives:
            derivative.rect = SurroundingRectangle(
                derivative,
                color=TEAL
            )

        del_h_sub_f = TexMobject("f")
        del_h_sub_f.scale(0.5)
        del_h_sub_f.next_to(del_h1.get_corner(DR), RIGHT, buff=0)
        del_h_sub_f.set_color(self.f_color)

        lines = self.graph_edges
        top_lines = lines[::2].copy()
        bottom_lines = lines[1::2].copy()
        for group in top_lines, bottom_lines:
            group.set_stroke(YELLOW, 6)

        self.add_foreground_mobjects(cr_derivatives)
        rect = dx1.rect.copy()
        rect.save_state()
        rect.scale(3)
        rect.set_fill(opacity=0)

        self.play(
            rect.restore,
            FadeIn(derivatives[0].rect)
        )
        self.wait()
        self.play(Transform(rect, df.rect))
        self.wait()
        self.play(
            rect.replace, df_dx, {"stretch": True},
            rect.scale, 1.1,
        )
        self.wait()
        self.play(
            Transform(rect, del_f.rect),
            FadeOut(derivatives[0].rect),
            FadeIn(derivatives[2].rect),
        )
        self.wait()
        self.play(Transform(rect, del_h1.rect))
        self.wait()
        self.play(ReplacementTransform(
            del_f[1].copy(), del_h_sub_f,
            path_arc=PI,
        ))
        self.wait()
        self.play(
            del_h_sub_f.shift, UR,
            del_h_sub_f.fade, 1,
            rate_func=running_start,
            remover=True
        )
        self.wait()
        self.play(
            Transform(rect, del_f.rect),
            ReplacementTransform(rect.copy(), df.rect),
        )
        self.wait()
        for x in range(3):
            self.play(ShowCreationThenDestruction(
                top_lines,
                submobject_mode="one_at_a_time"
            ))
        self.wait()
        self.play(
            rect.replace, cr_derivatives[1::2], {"stretch": True},
            rect.scale, 1.1,
            FadeOut(df.rect),
            FadeOut(derivatives[2].rect),
            FadeIn(derivatives[1].rect),
            FadeIn(derivatives[3].rect),
        )
        self.wait()
        self.play(
            Transform(rect, dg.rect),
            FadeOut(derivatives[3].rect)
        )
        self.wait()
        self.play(Transform(rect, dx2.rect))
        self.wait()
        self.play(
            Transform(rect, del_h2.rect),
            FadeOut(derivatives[1].rect),
            FadeIn(derivatives[3].rect),
        )
        self.wait()
        self.play(Transform(rect, del_g.rect))
        self.wait()
        self.play(
            rect.replace, cr_derivatives, {"stretch": True},
            rect.scale, 1.1,
            FadeOut(derivatives[3].rect)
        )
        for x in range(3):
            self.play(*[
                ShowCreationThenDestruction(
                    group,
                    submobject_mode="one_at_a_time"
                )
                for group in (top_lines, bottom_lines)
            ])
        self.wait()
        self.play(FadeOut(rect))
        self.remove_foreground_mobject(cr_derivatives)

    def plug_in_expressions(self):
        lhs = VGroup(
            self.dh_dx_at_two[:3],
            self.chain_rule_rhs[::3],
            self.chain_rule_derivatives,
        )
        lhs.generate_target()
        lhs.target.to_edge(LEFT)
        df_dx, dg_dx, dh_df, dh_dg = self.chain_rule_derivatives

        formulas = self.formulas
        x, f_formula, g_formula, h_formula = formulas

        full_derivative = TexMobject(
            "=",
            "(", "2", "x", ")",
            "(", "2", "f", "g", ")",
            "+",
            "(", "-\\sin(", "\\pi", "x", ")", "\\pi", ")",
            "(", "f", "^2", ")"
        )
        full_derivative.next_to(lhs.target, RIGHT)
        full_derivative.set_color_by_tex_to_color_map(
            self.tex_to_color_map
        )

        self.play(MoveToTarget(lhs))
        self.play(Write(full_derivative[0]))

        # df/dx
        self.play(
            f_formula.shift, UP,
            df_dx.shift, 0.5 * DOWN
        )
        self.play(
            ReplacementTransform(
                f_formula[2:].copy(),
                full_derivative[2:4],
            ),
            FadeIn(full_derivative[1:5:3])
        )
        self.wait()
        self.play(
            f_formula.shift, DOWN,
            df_dx.shift, 0.5 * UP
        )
        self.wait()

        # dg/dx
        self.play(
            g_formula.shift, 0.75 * UP,
            dg_dx.shift, 0.5 * DOWN
        )
        self.play(
            ReplacementTransform(
                g_formula[2:].copy(),
                full_derivative[12:17],
            ),
            FadeIn(full_derivative[11:18:6]),
            Write(full_derivative[10]),
        )
        self.wait()
        self.play(
            g_formula.shift, 0.75 * DOWN,
            dg_dx.shift, 0.5 * UP
        )
        self.wait()

        # dh/df
        self.play(
            h_formula.shift, UP,
            dh_df.shift, 0.5 * DOWN
        )
        self.wait()
        self.play(
            ReplacementTransform(
                h_formula[2:].copy(),
                full_derivative[6:9],
            ),
            FadeIn(full_derivative[5:10:4])
        )
        self.wait()
        self.play(
            dh_df.shift, 0.5 * UP
        )

        # dh/dg
        self.play(
            dh_dg.shift, 0.5 * DOWN,
        )
        self.wait()
        self.play(
            ReplacementTransform(
                h_formula[2:].copy(),
                full_derivative[19:21],
            ),
            FadeIn(full_derivative[18:22:3])
        )
        self.wait()
        self.play(
            h_formula.shift, DOWN,
            dh_dg.shift, 0.5 * UP
        )
        self.wait()

        self.full_derivative = full_derivative

    def plug_in_values(self):
        full_derivative = self.full_derivative
        value_labels = self.value_labels

        rhs = TexMobject(
            """
            =
            (2 \\cdot 2)
            (2 \\cdot 4 \\cdot 1) +
            (-\\sin(\\pi 2)\\pi)(4^2)
            """,
            tex_to_color_map={
                "2": self.x_color,
                "4": self.f_color,
                "1": self.g_color,
                "^2": WHITE,
            }
        )
        rhs.next_to(full_derivative, DOWN, aligned_edge=LEFT)

        result = TexMobject("=", "32", "+", "0")
        result.next_to(rhs, DOWN, aligned_edge=LEFT)

        self.play(LaggedStart(Write, value_labels))
        self.wait()
        self.play(ReplacementTransform(
            full_derivative.copy(), rhs,
            submobject_mode="lagged_start",
            run_time=2
        ))
        self.wait()
        self.play(Write(result))
        self.wait()

    def discuss_meaning_of_result(self):
        x_dot = self.x_dot
        h_dot = self.h_dot

        for x in range(3):
            self.play(
                x_dot.shift, 0.25 * RIGHT,
                h_dot.shift, RIGHT,
                run_time=2,
                rate_func=lambda t: wiggle(t, 4)
            )
            self.wait()

class FondoTexto(Scene):
    def construct(self):
        texto=TexMobject("Hola","mundo")
        fondo=Square().set_fill(GREEN,1)

        self.tex_to_color_map = {
            "Hola": RED,
        }

        texto.set_color_by_tex_to_color_map(
                self.tex_to_color_map
            )
        self.add(fondo,texto)

class CompartirVariables(Scene):
    def construct(self):
        self.paso1()
        self.paso2()
        self.paso3()
        x,y=self.get_attrs("x","y")
        x+=1
        y+=1
        print("En construct: x= %s, y= %s,z= %s"%(x,y,self.z))

    def paso1(self):
        x=9.5
        y=8.7
        self.set_variables_as_attrs(x,y)
        print("En paso 1: x= %s, y= %s"%(x,y))

    def paso2(self):
        x,y=self.get_attrs("x","y")
        x+=1
        y+=1
        self.z=3
        print("En paso 2: x= %s, y= %s"%(x,y))
        self.set_variables_as_attrs(x,y)

    def paso3(self):
        x,y=self.get_attrs("x","y")
        x+=1
        self.x=self.x*(-1)
        y+=1
        self.set_variables_as_attrs(x,y)                                # Jugar
        print("En paso 3: x= %s, y= %s, self.x= %s"%(x,y,self.x))       # con las posiciones de estas dos lineas

class WriteStuff3(Scene):
    def construct(self):
        example_tex = TexMobject(
            "{\\sf","print","(","`Hello, world!'",")}",
            tex_to_color_map={"print": YELLOW, "`Hello, world!'": ORANGE}
        )

        self.play(Write(example_tex))
        self.wait()



class NumerosPuntosSVG(Scene):
    def construct(self):
        burbuja=SVGMobject(file_name = "Speach.svg", initial_scale_factor = 0.02)[0]
        burbuja.set_fill(None,0).set_stroke(ORANGE,1).scale(2.4)
        tam=31
        puntos=VGroup(*[Dot()for i in range(tam)]).set_color_by_gradient(GREEN,RED,YELLOW)
        textos=VGroup()
        for i in range(tam):
            puntos[i].move_to(burbuja.points[i])
            texto=Formula("%s"%i,color=WHITE).scale(0.8).move_to(puntos[i])
            textos.add(texto)
        self.add(burbuja,puntos,textos)

class PuntosSVG(Scene):
    def construct(self):
        burbuja=SVGMobject(file_name = "Speach.svg", initial_scale_factor = 0.02)[0]
        burbuja.set_fill(None,0).set_stroke(ORANGE,1).scale(2.4)
        tam=31
        puntos=VGroup(*[Dot()for i in range(tam)]).set_color_by_gradient(GREEN,RED,YELLOW)
        textos=VGroup()
        burbuja.scale([0.5,1.5,1])
        for i in range(tam):
            puntos[i].move_to(burbuja.points[i])
            texto=Formula("%s"%i,color=WHITE).scale(0.8).move_to(puntos[i])
            textos.add(texto)

        self.add(burbuja,puntos,textos)

        np=Dot(color=WHITE)

        np2=np.copy().set_color(PURPLE).scale(2)
        np3=np.copy().set_color(PINK).scale(2.5)
        np.move_to(burbuja.points[12])
        np2.move_to(burbuja.points[13,1])
        np3.move_to(burbuja.points[16,1])

        npx=np.get_center()[0]
        npy=np.get_center()[1]
        npz=np.get_center()[2]
        print("np: x=%f,y=%f,z=%f\n"%(npx,npy,npz))
        print("po: x=%f,y=%f,z=%f\n"%(burbuja.points[12,0],burbuja.points[12,1],burbuja.points[12,2]))
        self.add(np3,np2,np)

class ZoomT2(ZoomedScene):
    CONFIG = {
        "show_basis_vectors": False,
        "show_coordinates": True,
        "zoom_factor": 0.3,
        "zoomed_display_height": 1,
        "zoomed_display_width": 6,
    }

    def setup(self):
        ZoomedScene.setup(self)

    def construct(self):
        grilla=Grilla()
        #self.add_foreground_mobject(grilla)
        texto1=Texto("Undolatory theory",color=RED)
        texto2=Texto("Experimento de Airy",color=PURPLE)

        conj_texto1=VGroup(texto1,texto2)
        conj_texto1.arrange_submobjects(DOWN,aligned_edge=LEFT)



        imagen=ImageMobject("flat_earth/airy3")
        imagen.set_height(7)
        imagen.shift(LEFT*3)
        self.add(imagen)

        zoomed_camera = self.zoomed_camera
        zoomed_display = self.zoomed_display
        frame = zoomed_camera.frame

        frame.move_to(3.05 * LEFT + 1.4 * UP)
        frame.set_color(WHITE)

        zoomed_display.display_frame.set_color(WHITE)

        zd_rect = BackgroundRectangle(
            zoomed_display,
            fill_opacity=0,
            buff=MED_SMALL_BUFF,
        )

        self.add_foreground_mobject(zd_rect)

        zd_rect.anim = UpdateFromFunc(
            zd_rect,
            lambda rect: rect.replace(zoomed_display).scale(1.1)
        )
        #zd_rect.next_to(FRAME_HEIGHT * RIGHT, UP)

        zoomed_display.move_to(ORIGIN+RIGHT*3+UP*3)

        conj_texto1.next_to(zoomed_display,DOWN)

        self.play(ShowCreation(frame))
        self.activate_zooming()
        #'''
        self.play(
            self.get_zoomed_display_pop_out_animation(),
            zd_rect.anim
        )
        self.play(Escribe(texto1))
        #'''
        self.wait()
        '''
        self.play(
            #self.get_zoomed_display_pop_out_animation(),
            zd_rect.anim,
            rate_func=lambda t: smooth(1-t)
        )
        #'''
        print("aqui")
        self.play(
            frame.scale,[0.5,1.5,1],
            zoomed_display.scale,[0.5,1.5,1],
            zoomed_display.display_frame.scale,[0.5,1.5,1],
            )
        self.play(
            frame.scale,1.5,
            frame.shift,2.5*DOWN
            )

        self.wait()
        self.play(
            self.get_zoomed_display_pop_out_animation(),
            zd_rect.anim,
            rate_func=lambda t: smooth(1-t)
        )
        self.play(
            zoomed_display.display_frame.fade,1,
            frame.fade,1
            )
        self.wait()

class Justificado(Scene):
    def construct(self):
        texto=Texto("""
        \\justify
This  is  the  second  paragraph. Hello, here is some text without
a meaning.  This text should show what 
a printed text will look like at this place.  If you read this text, 
you will get no information.  Really?  Is there no information?  Is there 
a difference between this text and some nonsense like not at all!  A 
blind text like this gives you information about the selected font, how 
the letters are written and an impression of the look.  This text should
contain all letters of the alphabet and it should be written in of the
original language.There is no need for special content, but the length of
words should match the language.
        """).scale(0.7)
        self.play(LaggedStart(FadeIn,texto))
        self.wait()

class BielaManivelaCorredera(Scene):
	CONFIG={
		"a":2,
		"b":-6.5,
		"c":1.7,
		"theta_in":70,
		"theta_fin":70-3*360,
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
		semi_circulo_ancla=Dot(O2.get_center(),radius=0.3,color=self.ancla_color)
		rect_ancla=Square(side_length=0.6).set_stroke(None,0).set_fill(self.ancla_color,1).move_to(O2.get_center()+DOWN*semi_circulo_ancla.get_width()/2)
		patron_ancla=Patron(0.9,0.2,color=self.ancla_color,separacion=0.1,direccion="U",agregar_base=True,grosor=0.1).next_to(rect_ancla,DOWN,buff=0)
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
		self.play(Escribe(titulo),ShowCreation(underline))
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

		self.play(UpdateFromAlphaFunc(grupo,update),run_time=6,rate_func=double_smooth)

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

formula_txt=["\\lim_{","x","\\to","\\infty}","{1","\\over","x}","=","0"]

class EnlistarFormulas(Scene):
    def construct(self):
        formula=Formula(*formula_txt)
        for w in formula:
            print(w.get_tex_string())
        self.add(formula)

class EnlistarFormulasTXT(CheckFormulaByTXT):
    CONFIG={
    "text":Formula(*formula_txt),
    "remove":[]
    }

class Show1(ShowNumberElements):
    CONFIG={
    "text":Formula(*formula_txt),
    "remove":[]
    }

import csv

class Export1(ExportCSV):
    CONFIG={
    "text":Formula(*formula_txt),
    "csv_name":"csv1",
    }

class MatrixBracket(TexMobject):
    pass

mat=MatrixBracket(r"""
            \begin{bmatrix}
            %s & b & c \\
            d & e & f \\
            \end{bmatrix}
        """%r"\frac{y}{x}")

class MatrixCheck(CheckFormulaByTXT):
    CONFIG={
    #"set_size":"height",
    "text":Formula("\\sqrt{{a\\over\\sqrt[2]{xb}}}"),
    }

class MatrixGroup(VGroup):
    def __init__(self,matrix_complete,show_desg=False,start=3):
        matrix_complete_full=""
        coords=[]
        for w in range(len(matrix_complete)):
            coords_r=[]
            for i in range(len(matrix_complete[w])):
                tex_i=""
                for j in matrix_complete[w][i]:
                    matrix_complete_full+=j
                    tex_i+=j
                    matrix_complete_full+=" "
                    tex_i+=" "
                l_tex=len(Formula(tex_i))
                coords_r.append(l_tex)
                print(l_tex)
                if i<len(matrix_complete[w])-1:
                    matrix_complete_full+=" & "
                else:
                    matrix_complete_full+=r" \\ "
            coords.append(coords_r)

        VGroup.__init__(self)
        matrix_frag=VGroup()

        matrix_desg=TexMobject(r"""
            \begin{bmatrix}
            %s
            \end{bmatrix}
        """%(matrix_complete_full))
        end=start
        
        for w in range(len(matrix_complete)):
            matrix_rows=VGroup()
            for i in range(len(matrix_complete[w])):
                element=VGroup(Formula(*matrix_complete[w][i]))
                element.set_height(matrix_desg[start:start+coords[w][i]].get_height())
                element.move_to(matrix_desg[start:start+coords[w][i]])
                start+=coords[w][i]
                matrix_rows.add(element)
            matrix_frag.add(matrix_rows)
        matrix_frag.add(matrix_desg[:end],matrix_desg[-end:])

        if show_desg==True:
            self.add(*matrix_desg)
        else:
            self.add(*matrix_frag)


class CheckNewMatrix(CheckFormula):
    CONFIG={
    #"set_size":"height"
    }
    def import_text(self):
        matrix_complete=MatrixGroup(np.transpose([
            [["a"],["\\sqrt{","{a","\\over","\\sqrt[2]{xb}}","}"]],
            [["\\displaystyle\\int^x_yf(x)"],       ["e"]],
        ]),start=3)
        matrix_complete[0][1].set_color(PINK)
        return matrix_complete



class Matrix1(Scene):
    def construct(self):
        matrix_1=[
            ["a","{a\\over b}"],
            ["d","e",],

        ]
        matrix_tex=""
        for w in range(len(matrix_1)):  
            for i in range(len(matrix_1[w])):
                if i<len(matrix_1[w])-1:
                    matrix_tex+=matrix_1[w][i]
                    matrix_tex+=" & "
                else:
                    matrix_tex+=matrix_1[w][i]
                    matrix_tex+=r" \\ "

        matrix_complete=[
            [["a"],["\\sqrt{","{a","\\over","\\sqrt[2]{xb}}","}"]],
            [["\\displaystyle\\int^x_yf(x)"],       ["e"]],
        ]
        matrix_complete_full=""
        coords=[]
        for w in range(len(matrix_complete)):
            coords_r=[]
            for i in range(len(matrix_complete[w])):
                tex_i=""
                for j in matrix_complete[w][i]:
                    matrix_complete_full+=j
                    tex_i+=j
                    matrix_complete_full+=" "
                    tex_i+=" "
                l_tex=len(Formula(tex_i))
                coords_r.append(l_tex)
                print(l_tex)
                if i<len(matrix_complete[w])-1:
                    matrix_complete_full+=" & "
                else:
                    matrix_complete_full+=r" \\ "
            coords.append(coords_r)

        matrix_frag=VGroup()
        start=1

        matrix_desg=MatrixBracket(r"""
            \begin{bmatrix}
            %s
            \end{bmatrix}
        """%(matrix_complete_full))
        
        for w in range(len(matrix_complete)):
            matrix_rows=VGroup()
            for i in range(len(matrix_complete[w])):
                element=VGroup(Formula(*matrix_complete[w][i]))
                element.set_height(matrix_desg[start:start+coords[w][i]].get_height())
                element.move_to(matrix_desg[start:start+coords[w][i]])
                start+=coords[w][i]
                print("[",start,"][",start+coords[w][i],"]")
                matrix_rows.add(element)
            matrix_frag.add(matrix_rows)
        matrix_frag.set_color(RED)

        self.add(matrix_desg)
        self.add(matrix_frag)