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
		titulo=Texto("\\sc Advantages").scale(2).to_edge(UP)
		ul=underline(titulo)
		lista=VGroup(
			Texto("1. It is free software."),
			Texto("2. It can work on low resource or old computers."),
			Texto("3. It works on Windows, GNU/Linux\\\\\\ \\ \\ \\ \\ (any distribution) and Mac perfectly."),
			Texto("4. It is constantly improving."),
			Texto("5. The video files are very high quality and low weight.")
			).arrange_submobjects(DOWN,aligned_edge=LEFT)
		lista.next_to(titulo,DOWN,buff=1)

		self.play(Escribe(titulo),GrowFromCenter(ul))
		self.wait()

		for obj in lista:
			self.play(Escribe(obj))
			self.wait(2)

class Conocimientos(Scene):
	def construct(self):
		text1=Texto("You don't\\\\need previous\\\\knowledge!!",color=ORANGE).scale(4)
		self.play(LaggedStart(GrowFromCenter,text1))
		self.wait(2)

class Desventajas(Scene):
	def construct(self):
		titulo=Texto("\\sc Disadvantages").scale(2).to_edge(UP)
		ul=underline(titulo)
		lista=VGroup(
			Texto("1. The space required are approximately 5GB."),
			Texto("2. There is not a very clearly documentation (yet)."),
			).arrange_submobjects(DOWN*2,aligned_edge=LEFT)

		self.play(Escribe(titulo),GrowFromCenter(ul))
		self.wait()

		for obj in lista:
			self.play(Escribe(obj))
			self.wait(2)

class Pregunta(Scene):
	def construct(self):
		titulo=Texto("What is\\\\{\\sc Manim}?").scale(4)
		self.play(Write(titulo))
		self.wait()
		self.play(Write(titulo),rate_func=lambda t:smooth(1-1.05*t))
		self.wait()

class Temario(Scene):
	def construct(self):
		titulo=Texto("\\sc Silabus").scale(2).to_edge(UP)
		ul=underline(titulo)
		lista=VGroup(
			Texto("0. Installation (Windows,Mac,GNU/Linux)"),
			Texto("1. Text format."),
			Texto("2. \\TeX\\ formulas."),
			Texto("3. Arrays."),
			Texto("4. Transformations."),
			Texto("5. Visual tools."),
			Texto("6. Introduction to 2D graphs."),
			Texto("7. Introduction to 3D animations."),
			Texto("8. Add audio."),
			Texto("9. Insert pictures and SVGs."),
			Texto("10. First project.")
			).arrange_submobjects(DOWN,aligned_edge=LEFT).next_to(titulo,DOWN,buff=0.1).scale(0.87)

		self.play(Escribe(titulo),GrowFromCenter(ul))
		self.play(LaggedStart(Escribe,lista))
		self.wait()
