#!/usr/bin/env python

from manimlib.imports import *

class WriteHelloWorld(Scene):
	def construct(self):
		hello_world = TextMobject("Hello World!").scale(2)
		self.play(Write(hello_world))
		self.wait()

# DrawBorderThenFill
class DrawBorderThenFillAnimation(Scene):
	def construct(self):
		square = Square(
			fill_color=ORANGE,
			fill_opacity=1
			)
		self.play(DrawBorderThenFill(square))
		self.wait()


# ShowCreation
class ShowCreationAnimation(Scene):
	def construct(self):
		line = Line(LEFT*3,RIGHT*3)
		self.play(ShowCreation(line))
		self.wait()

# GrowArrow
class GrowArrowAnimation(Scene):
	def construct(self):
		arrow = Arrow(LEFT*3,RIGHT*3)
		self.play(GrowArrow(arrow))
		self.wait()

# Uncreate
class UncreateAnimation(Scene):
	def construct(self):
		circle = Circle(radius=3)
		self.add(circle)

		self.play(Uncreate(circle))
		self.wait()

# ShowCreationThenDestruction
class ShowCreationThenDestructionAnimation(Scene):
	def construct(self):
		circle = Circle(radius=3)
		self.add(circle)

		self.play(ShowCreationThenDestruction(circle))
		self.wait()

#-----------------------------
# FocusOn

class FocusOnAnimation(Scene):
	def construct(self):
		points_group = VGroup(*[Dot()for x in range(3)])
		points_group.arrange(RIGHT,buff=2)

		colors = [RED,ORANGE,BLUE]
		self.add(points_group)
		
		for dot,color in zip(points_group,colors):
			self.play(FocusOn(dot,color=color))
		self.wait()

'''
Parameters:
Required : 1
			 VMobject
Optional :
			opacity = 0.2
			color	= GRAY
			remover = True
'''

# Indicate
class IndicateAnimation(Scene):
	def construct(self):
		formula = TexMobject("\\nabla","{\\bf u}")
		formula.scale(3)
		colors = [RED,BLUE]

		self.add(formula)

		for text,color in zip(formula,colors):
			self.play(Indicate(text,color=color))
		self.wait()

# Flash

class IndicateAnimation(Scene):
	def construct(self):
		points_group = VGroup(*[Dot()for x in range(3)])
		points_group.arrange(RIGHT,buff=2)

		colors = [RED,ORANGE,BLUE]

		self.add(points_group)

		for text,color in zip(formula,colors):
			self.play(Indicate(text,color=color))
		self.wait()
