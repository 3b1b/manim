from big_ol_pile_of_manim_imports import *

OUTPUT_DIRECTORY = "magnetic_force"

class StretchNumberLine(Scene):
	CONFIG = {
		"dot_color": YELLOW,
		"write_run_time": 1,
	}
	def construct(self):
		# Too much dumb manually positioning in here...
		title = Title("Normal Multiplication")

		number_line = NumberLine(x_min=-6, x_max=6)
		number_line.add_numbers()
		number_line.shift(2 * UP)

		self.add(number_line)
		self.play(
			Write(number_line)
		)

		number_line_text = TextMobject("This is the number line")
		self.add(number_line_text)
		self.write_and_fade(number_line_text)

		R_example_dot = Dot(number_line.number_to_point(1))
		R_example_dot.set_color(self.dot_color)

		R_example_dot_text = TextMobject("Let us mark the number 1")
		self.add(R_example_dot_text)
		self.write_and_fade(R_example_dot_text)
		self.play( GrowFromCenter(R_example_dot) )

		# number_line.add(R_example_dot)
		self.wait(2)
		self.wait()

	def write_and_fade(self, obj):
		self.play( Write(obj) , run_time=self.write_run_time)
		self.wait()
		self.play( FadeOut(obj) )
