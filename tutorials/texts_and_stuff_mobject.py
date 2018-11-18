from big_ol_pile_of_manim_imports import *

class BasicText(Scene):
	def construct(self):
		quote = TextMobject("I ain't want no tree fiddy") # created an mobject - text feild
		quote2 = TextMobject("Blah blah blah blah blah Blah blah blah blah blahBlah blah blah blah blahBlah blah blah blah blahBlah blah blah blah blahBlah blah blah blah blahBlah blah blah blah blahBlah blah blah blah blahBlah blah blah blah blah")
		author=TextMobject("-Albert Einstein")

		quote.set_color(RED)
		quote2.set_color(YELLOW)
		quote.to_edge(UP) # or move_to(3*UP)
		quote2.to_edge(UP) # to make sure the transformation happesn in the same location
		author.scale(0.75)
		author.next_to(quote.get_corner(DOWN+RIGHT),DOWN)
		print(quote.get_corner(DOWN+RIGHT))

		self.add(quote)
		self.add(author)
		self.wait(2)
		# transform, move
		self.play(Transform(quote,quote2))
		self.play(ApplyMethod(author.move_to, quote2.get_corner(DOWN+RIGHT)+DOWN+2*LEFT))
		print(quote2.get_corner(DOWN), quote2.get_corner(RIGHT), quote2.get_corner(LEFT), quote2.get_corner(UP))
		print(quote2.get_corner(DOWN+RIGHT)+DOWN+2*LEFT)
		#self.play(Transform(quote,quote2),ApplyMethod(author.move_to,quote2.get_corner(DOWN+RIGHT)+DOWN+2*LEFT))
		#self.play(ApplyMethod(author.match_color,quote2),Transform(author,author.scale(1)))
		#self.play(FadeOut(quote))
		self.wait(3)

class BasicEquations(Scene):
	def construct(self):
		

		