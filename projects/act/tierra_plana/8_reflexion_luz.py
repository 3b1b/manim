from big_ol_pile_of_manim_imports import *

class Curvatura(MovingCameraScene):
    CONFIG={
    "fixed_dimension": 0,
    "default_frame_stroke_width": 1,
    }
    def construct(self):
        self.definir_objetos()
        self.add(self.graficos)
        self.graficos[3:].set_fill(opacity=0)
        self.graficos[3:].set_stroke(opacity=0)
        self.wait()
        cuadro=Square().scale(0.9)
        cuadro.move_to(self.puntos[0])
        self.graficos.save_state()
        self.graficos.generate_target()
        self.graficos.target.set_stroke(None,8)
        self.graficos.target.shift(-cuadro.get_center())
        self.graficos.target.scale(
                FRAME_WIDTH / cuadro.get_width(),
                about_point=ORIGIN,
            )
        self.graficos.target.shift(-LEFT*1.5-UP*1.5)
        self.play(MoveToTarget(self.graficos, run_time=3))
        #self.play(self.graficos[:4].set_stroke,None,8)
        texto=Texto("a+b").scale(3)
        self.graficos.target.shift(-LEFT*1.5-UP*1.5)
        #self.play(MoveToTarget(self.graficos, run_time=3))
        self.play(Escribe(texto),rate_func=linear)
        self.play(texto.move_to,self.puntos[0])
        self.graficos.add(texto)
        self.graficos.target.add(texto)
        self.graficos[3:].set_stroke(opacity=1)
        self.play(ShowCreation(self.graficos[3:]))
        #self.graficos.add(texto)
        self.graficos.target.shift(-LEFT*1.5-UP*1.5)
        self.play(MoveToTarget(self.graficos, run_time=3))

        self.wait()
        #self.play(Restore(self.graficos, run_time=3))

    def definir_objetos(self):
        img = SVGMobject(
            file_name = "luz_curva",
            fill_opacity = 0,
            stroke_width = 2,
        )
        img.set_height(FRAME_HEIGHT*0.731)
        img.shift(DOWN+LEFT*0.07)
        tierra=img[8].set_color(BLACK) #tierra
        capas=VGroup()
        for i in range(len(img[9:16])):
            capas.add(img[9+i])
        capas.set_submobject_colors_by_gradient(BLUE,WHITE)

        lineas=img[0:7].set_color(RED)#lineas proyectadas
        puntos=img[16:24].set_color(ORANGE)#puntos
        tangentes=img[24:30].set_color(GREEN)#tangentes
        normales=img[24:30].copy()
        for i in range(len(normales)):
            normales[i].rotate(PI/2)

        linea=img[7].set_color(TEAL).rotate(PI)#linea que no podemos ver
        tray_luz=img[31].set_color(YELLOW)#trayectoria de la luz

        self.tierra=tierra
        self.capas=capas
        self.lineas=lineas
        self.puntos=puntos
        self.tangentes=tangentes
        self.normales=normales
        self.linea=linea
        self.tray_luz=tray_luz
        self.graficos=VGroup(tierra,capas,lineas,puntos,tangentes,normales,linea,tray_luz)

class DeformacionLuz1(MovingCameraScene):
	def construct(self):
		conjunto=VGroup()
		for i in range(15):
			ci=self.circ_punto(4+i*0.2,30*DEGREES+i*10*DEGREES)
			conjunto.add(ci)

		conjunto.set_submobject_colors_by_gradient(BLUE,WHITE).set_stroke(None,1)
		conjunto.shift(DOWN*5)
		self.add(conjunto)

	def coord_pol(self,radio,angulo,origen=np.array([0,0])):
		coord=np.array([
			radio*np.cos(angulo)+origen[0],
			radio*np.sin(angulo)+origen[1],
			0
			])
		return coord
	def malla(self,definicion=1):
		pass

	def circ_punto(self,radio,angulo,color=ORANGE):
		circulo=Circle(radius=radio,color=color)
		punto=Dot(self.coord_pol(radio,angulo),color=color)
		grupo=VGroup(circulo,punto)
		return grupo
		
class DeformacionLuz2(MovingCameraScene):
	def construct(self):
		conjunto=VGroup()
		gamma=100*DEGREES
		r1=4;r2=4.2;r3=4.4
		th1=20*DEGREES;th2=70*DEGREES
		c1=self.circ_punto(r1,th1,RED)
		c2=self.circ_punto(r2,th2,BLUE)
		c3=Circle(radius=4.4,color=ORANGE)
		linea_r1=Line(c1[0].get_center(),c1[1].get_center())
		linea_pre=Line(LEFT*FRAME_WIDTH,RIGHT*FRAME_WIDTH).rotate(gamma)
		linea_pos=linea_pre.copy().move_to(c1[1].get_center())
		linea_fin=DashedLine(
			c1[1].get_center(),
			c1[1].get_center()+self.proyeccion(r1,r2,th1,gamma)*linea_pre.get_unit_vector()
			).set_color(PURPLE)
		punto_fin=Dot(linea_fin.get_end())

		linea_pre2=Line(LEFT*FRAME_WIDTH,RIGHT*FRAME_WIDTH).rotate(gamma+10*DEGREES)
		linea_r2=Line(c3.get_center(),punto_fin.get_center()).set_color(TEAL)
		linea_fin2=DashedLine(
			punto_fin.get_center(),
			punto_fin.get_center()+self.proyeccion(r2,r3,linea_r2.get_angle(),gamma+10*DEGREES)*linea_pre2.get_unit_vector()
			).set_color(ORANGE)
		punto_fin2=Dot(linea_fin2.get_end())

		conjunto.add(c1,c2,linea_r1,linea_fin,punto_fin,c3,linea_fin2,punto_fin2,linea_r2).shift(DOWN*4).set_stroke(None,1)
		self.add(conjunto)

	def coord_pol(self,radio,angulo,origen=np.array([0,0])):
		coord=np.array([
			radio*np.cos(angulo)+origen[0],
			radio*np.sin(angulo)+origen[1],
			0
			])
		return coord
	def malla(self,definicion=1):
		pass

	def circ_punto(self,radio,angulo,color=ORANGE):
		circulo=Circle(radius=radio,color=color)
		punto=Dot(self.coord_pol(radio,angulo),color=color)
		grupo=VGroup(circulo,punto)
		return grupo

	def proyeccion(self,r1,r2,th,gm):
		if gm-PI/2>=th:
			return np.sqrt(r2**2-(r1**2)*(np.cos(gm-th-PI/2))**2)+np.sqrt(r1**2-(r1**2)*(np.cos(gm-th-PI/2))**2)
		else:
			return np.sqrt(r2**2-(r1**2)*(np.cos(gm-th-PI/2))**2)-np.sqrt(r1**2-(r1**2)*(np.cos(gm-th-PI/2))**2)


class DeformacionLuz3(MovingCameraScene):
	def construct(self):
		total_niveles=9
		r_i=4
		Dr=0.3
		th_i=20*DEGREES
		Dth=10*DEGREES
		gamma=100*DEGREES
		c_i=Circle(radius=r_i)
		p_i=Dot(self.coord_pol(r_i,th_i))
		#--------------------------------------
		conjunto_c_p=VGroup()
		circulos=VGroup()
		puntos=VGroup()
		lineas_punto_punto=VGroup()
		lineas_pasadas=VGroup()
		lineas_tangentes=VGroup()
		lineas_perpendiculares=VGroup()
		#--------------------------------------
		circulos.add(c_i)
		puntos.add(p_i)
		conjunto_c_p.add(VGroup(c_i,p_i))
		#--------------------------------------
		for cont in range(total_niveles):
			linea_centro_punto=Line(circulos[cont].get_center(),puntos[cont].get_center())
			linea_gamma=Line(LEFT,RIGHT).rotate(gamma+Dth*cont)
			linea_punto_punto=DashedLine(
											puntos[cont].get_center(),
											puntos[cont].get_center()+self.proyeccion(r_i+Dr*cont,
												 									  r_i+Dr*(cont+1),
																					  linea_centro_punto.get_angle(),
																					  gamma+Dth*(cont))*linea_gamma.get_unit_vector()
											)
			punto_final=Dot(linea_punto_punto.get_end())
			circulo_final=Circle(radius=r_i+Dr*(cont+1))
			circulos.add(circulo_final)
			puntos.add(punto_final)
			
			linea_pasada=linea_punto_punto.copy().rotate(PI,about_point=linea_punto_punto.get_end(),about_edge=linea_punto_punto.get_end())
			linea_tangente=Line(LEFT,RIGHT).rotate(Line(circulos[cont+1].get_center(),puntos[cont+1].get_center()).get_angle()+PI/2).move_to(puntos[cont+1]).set_stroke(BLUE,2)
			linea_perpendicular=linea_tangente.copy().rotate(PI/2).set_color(ORANGE)


			lineas_punto_punto.add(linea_punto_punto)
			lineas_tangentes.add(linea_tangente)
			lineas_pasadas.add(linea_pasada)
			lineas_perpendiculares.add(linea_perpendicular)
			conjunto_c_p.add(VGroup(circulo_final,punto_final))

		conjunto_total=VGroup(conjunto_c_p,lineas_punto_punto,lineas_tangentes,lineas_perpendiculares,lineas_pasadas)
		conjunto_total.shift(DOWN*4).set_stroke(None,2)

		self.add(conjunto_total)



	def coord_pol(self,radio,angulo,origen=np.array([0,0])):
		coord=np.array([
			radio*np.cos(angulo)+origen[0],
			radio*np.sin(angulo)+origen[1],
			0
			])
		return coord

	def proyeccion(self,r1,r2,th,gm):
		if gm-PI/2>=th:
			return np.sqrt(r2**2-(r1**2)*(np.cos(gm-th-PI/2))**2)+np.sqrt(r1**2-(r1**2)*(np.cos(gm-th-PI/2))**2)
		else:
			return np.sqrt(r2**2-(r1**2)*(np.cos(gm-th-PI/2))**2)-np.sqrt(r1**2-(r1**2)*(np.cos(gm-th-PI/2))**2)

class DeformacionLuz4(MovingCameraScene):
	def construct(self):
		conj1=self.escenario_capas(
								total_niveles=9,
								r_i=4,
								Dr=0.2,
								th_i=20*DEGREES,
								Dth=10*DEGREES,
								gamma=100*DEGREES
								)
		conj2=self.escenario_capas(
								total_niveles=9,
								r_i=4,
								Dr=0.3,
								th_i=20*DEGREES,
								Dth=15*DEGREES,
								gamma=100*DEGREES
								)
		conj1.shift(DOWN*4).set_stroke(width=2)
		conj2.shift(DOWN*4).set_stroke(width=2)
		self.play(ShowCreation(conj1))
		self.wait()
		self.play(Transform(conj1,conj2),run_time=3)
		self.wait()

	def escenario_capas(self,total_niveles,r_i,Dr,th_i,Dth,gamma):
		c_i=Circle(radius=r_i)
		p_i=Dot(self.coord_pol(r_i,th_i))
		#--------------------------------------
		conjunto_c_p=VGroup()
		circulos=VGroup()
		puntos=VGroup()
		lineas_punto_punto=VGroup()
		lineas_pasadas=VGroup()
		lineas_tangentes=VGroup()
		lineas_perpendiculares=VGroup()
		#--------------------------------------
		circulos.add(c_i)
		puntos.add(p_i)
		conjunto_c_p.add(VGroup(c_i,p_i))
		#--------------------------------------
		for cont in range(total_niveles):
			linea_centro_punto=Line(circulos[cont].get_center(),puntos[cont].get_center())
			linea_gamma=Line(LEFT,RIGHT).rotate(gamma+Dth*cont)
			linea_punto_punto=DashedLine(
											puntos[cont].get_center(),
											puntos[cont].get_center()+self.proyeccion(r_i+Dr*cont,
												 									  r_i+Dr*(cont+1),
																					  linea_centro_punto.get_angle(),
																					  gamma+Dth*(cont))*linea_gamma.get_unit_vector()
											)
			punto_final=Dot(linea_punto_punto.get_end())
			circulo_final=Circle(radius=r_i+Dr*(cont+1))
			circulos.add(circulo_final)
			puntos.add(punto_final)
			
			linea_pasada=linea_punto_punto.copy().rotate(PI,about_point=linea_punto_punto.get_end(),about_edge=linea_punto_punto.get_end())
			linea_tangente=Line(LEFT,RIGHT).rotate(Line(circulos[cont+1].get_center(),puntos[cont+1].get_center()).get_angle()+PI/2).move_to(puntos[cont+1]).set_stroke(BLUE,2)
			linea_perpendicular=linea_tangente.copy().rotate(PI/2).set_color(ORANGE)


			lineas_punto_punto.add(linea_punto_punto)
			lineas_tangentes.add(linea_tangente)
			lineas_pasadas.add(linea_pasada)
			lineas_perpendiculares.add(linea_perpendicular)
			conjunto_c_p.add(VGroup(circulo_final,punto_final))

		conjunto_total=VGroup(conjunto_c_p,lineas_punto_punto,lineas_tangentes,lineas_perpendiculares,lineas_pasadas)
		#conjunto_total.shift(DOWN*4).set_stroke(None,2)

		return conjunto_total



	def coord_pol(self,radio,angulo,origen=np.array([0,0])):
		coord=np.array([
			radio*np.cos(angulo)+origen[0],
			radio*np.sin(angulo)+origen[1],
			0
			])
		return coord

	def proyeccion(self,r1,r2,th,gm):
		if gm-PI/2>=th:
			return np.sqrt(r2**2-(r1**2)*(np.cos(gm-th-PI/2))**2)+np.sqrt(r1**2-(r1**2)*(np.cos(gm-th-PI/2))**2)
		else:
			return np.sqrt(r2**2-(r1**2)*(np.cos(gm-th-PI/2))**2)-np.sqrt(r1**2-(r1**2)*(np.cos(gm-th-PI/2))**2)
