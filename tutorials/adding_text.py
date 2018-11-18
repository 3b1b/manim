from big_ol_pile_of_manim_imports import *

class AddingText(Scene):
#Adding text on the screen
	def construct(self):
		my_first_text=TextMobject("My name is Purusharth!")
		second_line=TextMobject("(The annihilator)")
		second_line.next_to(my_first_text,DOWN)
		third_line=TextMobject("and this is so fucking awesome.")
		third_line.next_to(my_first_text,DOWN)

		self.add(my_first_text)
		self.wait(2)
		self.add(second_line)
		self.wait(2)
		self.play(Transform(second_line,third_line))
		self.wait(2)
		second_line.shift(3*DOWN)
		self.play(ApplyMethod(my_first_text.shift,3*UP))
		self.play(ApplyMethod(my_first_text.shift,5*DOWN))
		self.play(ApplyMethod(my_first_text.shift,2*UP))
		self.wait(3)
