import random
from manimlib.imports import *
from manimlib.mobject.three_dimensions import Cube, Prism
from manimlib.mobject.types.vectorized_mobject import VMobject
from math import sqrt
import math

class Scale(VGroup):
    CONFIG = {
        "fill_opacity": 0.5,
        # "fill_color": BLUE_D,
        "stroke_width": 0.7,
        "side_length": 2,
    }
    color = WHITE
    def generate_points(self):
        for ln in np.arange(0, 0.5, 0.1):
            face = Rectangle(
            	height=self.height,
            	width=self.width,
                shade_in_3d=True,
                color = self.color,
            )
            face.flip()
            face.shift( ln*OUT / 2.0)
            face.apply_matrix(z_to_vector(OUT))
            self.add(face)
class Grid(VGroup):
	
	CONFIG = {
        "fill_opacity": 0.5,
        # "fill_color": BLUE_D,
        "stroke_width": 0.7,
        "side_length": 2,
    }
	height,width = 0,1
	def generate_points(self,height=10,width=1):
		box=Scale(height=self.height,width=self.width)
		division = math.ceil(width/2)
		
		for i in range(int(division/2)):
			lineR = Line(height=self.height,width=1)
			position+=RIGHT
			lineR.shift(position)
			box.add(lineR)
		position = LEFT*0	
		for i in range(int(division/2)):
			position+=LEFT
			lineL = Line(height=self.height,width=1)
			lineL.shift(position)
			box.add(lineL)
		return VGroup(box,lineL,lineR)


class Addition(ThreeDScene):
	def construct(self):

		box = Scale(height=1,width=1,fill_color='#838447')
		box.shift(LEFT*3)
		self.add(box)
		self.wait(1)
		ad = TextMobject("+",color=BLACK)
		ad.shift(LEFT*2)
		self.add(ad)
		box1 = copy.deepcopy(box)
		self.play(box1.move_to,LEFT)

		sum1 = Scale(height=1,width=2,fill_color='#838447')
		equal = TextMobject("=",color=BLACK)
		equal.scale(1)
		self.add(equal)
		sum1.shift(RIGHT*1.8)
		self.play(FadeIn(sum1))
		self.wait(1)

class Addition10(ThreeDScene):	

	def construct(self):
		box = Scale(height=10,width=2)
		grid = Grid(height=10,width=2)
		self.play(ShowCreation(grid))
		self.wait(1)

