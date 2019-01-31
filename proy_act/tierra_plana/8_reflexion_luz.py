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
