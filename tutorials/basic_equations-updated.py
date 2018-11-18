from big_ol_pile_of_manim_imports import *

class BasicEquations(Scene):
#A short script showing how to use Latex commands
	def construct(self):
		eq1=TextMobject("$\\vec{X}_0 \\cdot \\vec{Y}_1 = 3$")
		eq1.shift(2*UP)
		eq2=TexMobject("\\vec{F}_{net} = \\sum_i \\vec{F}_i")
		eq2.shift(2*DOWN)
		 
		self.play(Write(eq1))
		self.play(Write(eq2))