from big_ol_pile_of_manim_imports import *

class EsquemaManim(Scene):
	def construct(self):
		valor=1.5
		python=self.recuadro("Python",RED).scale(valor)
		latex=self.recuadro("\\LaTeX",GREEN).scale(valor)
		cairo=self.recuadro("Cairo",BLUE).scale(valor)
		ffmpeg=self.recuadro("FFmpeg",ORANGE).scale(valor)
		sox=self.recuadro("SoX",PURPLE).scale(valor)

		latex.shift(self.pos_vect(3,180))
		cairo.shift(self.pos_vect(3,90))
		ffmpeg.shift(self.pos_vect(3,0))
		sox.shift(self.pos_vect(3,-90))
		grupo_lineas=VGroup()

		for obj in [python,latex,cairo,ffmpeg,sox]:
			self.play(Write(obj))
			self.add_foreground_mobjects(obj)
			if obj!=python:
				linea=Line(python.get_center(),obj.get_center())
				self.play(ShowCreation(linea))
				grupo_lineas.add(linea)
			self.wait(2)

		grupo_periferico=VGroup(latex,cairo,ffmpeg,sox)

		def update(grupo):
			for obj,lin in zip(grupo_periferico,grupo_lineas):
				obj.move_to(lin.get_end())

		self.play(Rotating(grupo_lineas,rate_func=smooth),
			UpdateFromFunc(grupo_periferico,update),run_time=7)
		self.wait()


	def recuadro(self,texto,color):
		text=Texto(texto,color=WHITE)
		text.add_background_rectangle(opacity=0.7,color=color,buff=SMALL_BUFF)
		return text

	def pos_vect(self,dist,ang):
		pos=np.array([dist*np.cos(ang*DEGREES),dist*np.sin(ang*DEGREES),0])
		return pos

class Ventajas(Scene):
	def construct(self):
		titulo=Texto("\\sc Ventajas").scale(2).to_edge(UP)
		ul=underline(titulo)
		lista=VGroup(
			Texto("1. Es software libre."),
			Texto("2. Funciona en computadoras de bajos recursos."),
			Texto("3. Disponible para Windows, MacOS y GNU/Linux."),
			Texto("4. En constante desarrollo."),
			Texto("5. Videos de alta calidad y bajo peso.")
			).arrange_submobjects(DOWN,aligned_edge=LEFT)

		self.play(Escribe(titulo),GrowFromCenter(ul))
		self.wait()

		for obj in lista:
			self.play(Escribe(obj))
			self.wait(2)

class Conocimientos(Scene):
	def construct(self):
		text1=Texto("No necesitas\\\\ conocimientos\\\\ previos!!",color=ORANGE).scale(4)
		self.play(LaggedStart(GrowFromCenter,text1))
		self.wait(2)

class Desventajas(Scene):
	def construct(self):
		titulo=Texto("\\sc Desventajas").scale(2).to_edge(UP)
		ul=underline(titulo)
		lista=VGroup(
			Texto("1. En total pesa unos 5GB (depende del S.O.)."),
			Texto("2. No hay una documentación clara (aún)."),
			).arrange_submobjects(DOWN*2,aligned_edge=LEFT)

		self.play(Escribe(titulo),GrowFromCenter(ul))
		self.wait()

		for obj in lista:
			self.play(Escribe(obj))
			self.wait(2)

class Pregunta(Scene):
	def construct(self):
		titulo=Texto("¿Qué es\\\\{\\sc Manim}?").scale(4)
		self.play(Write(titulo))
		self.wait()
		self.play(Write(titulo),rate_func=lambda t:smooth(1-1.05*t))
		self.wait()

class Temario(Scene):
	def construct(self):
		titulo=Texto("\\sc Temario").scale(2).to_edge(UP).shift(UP*0.25)
		ul=underline(titulo)
		lista=VGroup(
			Texto("0. Instalación (Windows, Mac, GNU/Linux)."),
			Texto("1. Formato de textos."),
			Texto("2. Fórmulas en \\TeX."),
			Texto("3. Arreglos."),
			Texto("4. Transformaciones."),
			Texto("5. Herramientas visuales."),
			Texto("6. Introducción a las gráficas 2D."),
			Texto("7. Introducción a las gráficas 3D."),
			Texto("8. Agregar audio."),
			Texto("9. Insertar imágenes y SVGs."),
			Texto("10. Primer proyecto.")
			).arrange_submobjects(DOWN,aligned_edge=LEFT).next_to(titulo,DOWN,buff=0.1).scale(0.87)

		self.play(Escribe(titulo),GrowFromCenter(ul))
		self.play(LaggedStart(Escribe,lista))
		self.wait()
