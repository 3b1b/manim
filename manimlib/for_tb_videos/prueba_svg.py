from big_ol_pile_of_manim_imports import *

class PruebaSVG(Scene):
	CONFIG={
	"camera_config":{"background_color": WHITE},
	"tipo_svg":"svg",
	"file":"",
	"escala":1.4,
	"angle":0,
	"vflip":False,
	"opacidad_fondo": 1,
	"remover": [],
	"color": BLACK,
	"fondo": BLACK,
	"grosor": 3,
	"escala_numeros":0.5,
	"mostrar_todos_numeros": False,
	"animacion": False,
	"direccion_numeros": UP,
	"color_numeros": RED,
	"separacion_numeros":0,
	"muestra_elementos":[],
	"color_resaltado":BLUE,
	}
	def construct(self):
		if self.tipo_svg=="svg":
			self.imagen=SVGMobject(
		        "%s"%self.file,
		        fill_opacity = 1,
		        stroke_width = self.grosor,
		        stroke_color = self.color,
		    ).rotate(self.angle).set_fill(self.fondo,self.opacidad_fondo).scale(self.escala)
		else:
			self.imagen=self.importa_texto().set_fill(self.fondo,self.opacidad_fondo).rotate(self.angle).set_stroke(self.color,self.grosor).scale(self.escala)
		if self.vflip==True:
			self.imagen.flip()
		self.cambiar_colores(self.imagen)
		if self.animacion==True:
			self.play(DrawBorderThenFill(self.imagen))
		else:
			self.add(self.imagen)
		if self.mostrar_todos_numeros==True:
			self.imprimir_formula(self.imagen,
				self.escala_numeros,
				self.direccion_numeros,
				self.remover,
				self.separacion_numeros,
				self.color_numeros)

		self.devolver(self.imagen,self.muestra_elementos)
		
		self.wait()
	def importa_texto(self):
		return TexMobject("")

	def cambiar_colores(self,imagen):
		pass

	def imprimir_formula(self,texto,escala_inversa,direccion,excepcion,separacion,color):
		texto.set_color(RED)
		self.add(texto)
		contador = 0
		for j in range(len(texto)):
			permiso_imprimir=True
			for w in excepcion:
				if j==w:
					permiso_imprimir=False
			if permiso_imprimir:
				self.add(texto[j].set_color(self.color))
		contador = contador + 1

		contador=0
		for j in range(len(texto)):
			permiso_imprimir=True
			elemento = TexMobject("%d" %contador,color=color)
			elemento.scale(escala_inversa)
			elemento.next_to(texto[j],direccion,buff=separacion)
			for w in excepcion:
				if j==w:
					permiso_imprimir=False
			if permiso_imprimir:
				self.add(elemento)
			contador = contador + 1 

	def devolver(self,formula,adicion):
		for i in adicion:
			self.add_foreground_mobjects(formula[i].set_color(self.color_resaltado),
				TexMobject("%d"%i,color=self.color_resaltado).next_to(formula[i],self.direccion_numeros,buff=self.separacion_numeros).scale(self.escala_numeros))
