from big_ol_pile_of_manim_imports import *

class Shapes(Scene):
	def construct(self):
		circle = Circle()
		square = Square()
		line=Line(np.array([3,0,0]),np.array([5,0,0]))
		triangle=Polygon(np.array([0,0,0]),np.array([1,1,0]),np.array([1,-1,0]))
		dot = Dot()

		self.add(line) # add line
		self.play(ShowCreation(circle))
		self.play(FadeOut(circle))
		self.play(GrowFromCenter(square))
		self.play(Transform(square,triangle))
		self.play(FadeOut(line))
		self.play(ShowCreation(line))
		self.play(Transform(line,circle))
		self.play(FadeOut(triangle))
		self.play(Transform(circle,dot))

class MoreShapes(Scene):
	#A few more simple shapes
	def construct(self):
		circle = Circle(color=PURPLE_A, radius=1, center=np.array([3,1,0]))
		square = Square(fill_color=GOLD_B, fill_opacity=1, color=GOLD_A)
		rectangle = Rectangle(height=2, width=3)
		ellipse = Ellipse(width=3, height=1, color=RED)
		pointer = CurvedArrow(2*RIGHT,5*RIGHT,color=MAROON_C)
		arrow = Arrow(LEFT,UP)
		ring = Annulus(inner_radius=.5, outer_radius=1, color=BLUE)
		
		square.move_to(UP+OUT)
		#circle.surround(square)
		circle.shift(3*RIGHT+1*UP) # changing the center of the circle
		ellipse.shift(2*DOWN+2*RIGHT)
		arrow.next_to(circle,DOWN+LEFT)
		rectangle.next_to(arrow,DOWN+LEFT)
		ring.next_to(ellipse, RIGHT)
		 
		self.add(pointer)
		self.play(FadeIn(square))
		self.play(Rotating(square),FadeIn(circle))
		self.play(GrowArrow(arrow))
		self.play(GrowFromCenter(rectangle), GrowFromCenter(ellipse), GrowFromCenter(ring))

