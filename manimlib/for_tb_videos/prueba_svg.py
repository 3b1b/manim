from big_ol_pile_of_manim_imports import *

class PruebaSVG(Scene):
	CONFIG={
	"file":"",
	"height":4,
	"angle":0,
	"vflip":False
	}
	def construct(self):
		self.imagen=SVGMobject(
	        "pruebas/%s"%self.file,
	        fill_opacity = 1,
	        stroke_width = 2,
	        height = self.height,
	        stroke_color = WHITE,
	    ).set_color(WHITE).rotate(self.angle)
		if self.vflip==True:
			self.imagen.flip()
		self.cambiar_colores(self.imagen)
		self.play(DrawBorderThenFill(self.imagen))
		self.wait()

	def cambiar_colores(self,imagen):
		pass