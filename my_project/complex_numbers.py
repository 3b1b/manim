from big_ol_pile_of_manim_imports import *

OUTPUT_DIRECTORY = "complex_numbers"

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

class IntroduceNumberLine(Scene):
	CONFIG = {
		"dot_color_focused": YELLOW,
		"dot_color_default": WHITE,
		"text_color": WHITE,
		"write_run_time": 1,
	}
	def construct(self):
		# number line
		number_line = NumberLine(x_min=-6, x_max=6)
		# number_line.shift(2 * UP)

		self.add(number_line)
		self.play( Write(number_line) )
		self.wait(1.5)

		dot_0 = Dot(number_line.number_to_point(0))
		dot_0.set_color(self.dot_color_focused)
		text_0 = TextMobject('0')
		text_0.set_color(self.text_color)
		self.add(dot_0, text_0)
		self.play(
			Write(dot_0),
			text_0.next_to, dot_0, UP,
		)
		self.wait(1)

		dot_0_old = dot_0.copy()
		dot_0_old.set_color(self.dot_color_default)
		dot_1 = Dot(number_line.number_to_point(1))
		dot_1.set_color(self.dot_color_focused)
		text_1 = TextMobject('1')
		text_1.set_color(self.text_color)
		self.add(dot_1, text_1, dot_0_old)
		self.play(
			Write(dot_1),
			text_1.next_to, dot_1, UP,
			Transform(dot_0, dot_0_old),
		)
		self.wait(1)

		dot_1_old = dot_1.copy()
		dot_1_old.set_color(self.dot_color_default)
		self.play(
			Transform(dot_1, dot_1_old),
			number_line.add_numbers,
			FadeOut(text_0),
			FadeOut(text_1),
		)
		self.wait(2)

		# number_line_0 = number_line.copy()
		# number_line_0.add_numbers(0)

		# self.play(
		# 	Transform(number_line, number_line_0)
		# )
		# self.wait(2)

		# number_line_1 = number_line.copy()
		# number_line_1.add_numbers(0, 1)

		# self.play(
		# 	Transform(number_line, number_line_1)
		# )
		# self.wait(2)

	def write(self, *objs, add=True, fade=True, run_time=None):
		if add:
			self.add(*objs)
		self.play(
			*[Write(obj) for obj in objs],
			run_time=run_time or self.write_run_time
		)
		if fade:
			self.wait()
			self.play(
				*[FadeOut(obj) for obj in objs]
			)