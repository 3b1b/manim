from big_ol_pile_of_manim_imports import *

OUTPUT_DIRECTORY = "complex_numbers"

fix_stretch = lambda factor: (factor - 1) * 0.1 * LEFT

class StretchNumberLine(Scene):
	CONFIG = {
		"number_line_min": -6,
		"number_line_max":  6,
		"number_line_position": 2 * UP,

		"multiply_by": 2,
		"multiply_example": [
			(-2, 2 * LEFT),
		],

		"title": Title("Normal Multiplication"),

		"dot_color": YELLOW,

		"write_run_time": 1,

		"display_text": True,
	}
	def construct(self):
		# create the number line
		self.real_number_line = number_line = NumberLine(
			x_min=self.number_line_min,
			x_max=self.number_line_max
		)
		number_line.add_numbers()
		number_line.move_to(self.number_line_position)

		self.add(number_line)
		self.play(
			Write(number_line)
		)

		if self.display_text:
			self.write_and_fade( TextMobject("This is the number line") )
			self.write_and_fade( TextMobject("Let us copy the number line") )

		# create the second number line
		self.other_number_line = number_line_2 = self.real_number_line.copy()
		self.add(number_line_2)
		self.play(
			number_line_2.shift, (-2) * self.number_line_position
		)

		if self.display_text:
			self.wait(1)
			self.write_and_fade( TextMobject("Let us look at the act of multiplying by %s" % self.multiply_by) )
			self.write_and_fade( TextMobject("This will move 1 into the location of %s" % self.multiply_by) )

		# define 2 arrows.
		# since the animation of stretching the numberline occurs simultaniously to the stretching of the arrow,
		# 	I created both arrows according to the numberline before stretching it,
		# 	which means that both arrows are equal except for their initial position
		self.multiply_arrow = multiply_arrow_before_stretch = Arrow(
			self.other_number_line.number_to_point(1), # from
			self.real_number_line.number_to_point(self.multiply_by), # to
			color = RED, buff = MED_LARGE_BUFF
		)
		multiply_arrow_after_stretch = Arrow(
			self.other_number_line.number_to_point(self.multiply_by), # from
			self.real_number_line.number_to_point(self.multiply_by), # to
			color = RED, buff = MED_LARGE_BUFF
		)
		self.play( ShowCreation(multiply_arrow_before_stretch) )
	
		self.wait(1)

		self.write_and_fade(
			TextMobject("Now, we multiply by %s" % self.multiply_by),
			position=2 * LEFT
		)

		self.play(
			number_line_2.stretch, self.multiply_by, 0,
			# stretch moves the number line a bit to the right, so I fix it
			number_line_2.shift, fix_stretch(self.multiply_by),

			Transform(multiply_arrow_before_stretch, multiply_arrow_after_stretch),

			# for debugging purpose. to place both number lines on top of each other
			# number_line_2.shift, 2 * self.number_line_position
		)

		if self.display_text:
			self.wait(1.5)
			self.write_and_fade(
				TextMobject("Every number has been multiplied by %s" % self.multiply_by),
				position=2.4 * LEFT
			)
		for example_number, text_location in self.multiply_example:
			self.move_multiply_arrow(example_number, text_location)

		self.wait(3)

	def write_and_fade(self, obj, add=True, position=None):
		if position is not None:
			obj.move_to(position)
		if add:
			self.add(obj)
		self.play( Write(obj) , run_time=self.write_run_time)
		self.wait()
		self.play( FadeOut(obj) )

	def create_number_line(self):
		number_line = NumberLine(x_min=number_line_min, x_max=number_line_max)
		number_line.add_numbers()
		number_line.shift(self.number_line_position)

		self.add(number_line)
		self.play(
			Write(number_line)
		)

	def move_multiply_arrow(self, example_number, text_location):
		if self.display_text:
			self.write_and_fade(
				TexMobject(f"For \\enspace example, ({example_number})\\rightarrow({example_number * self.multiply_by})"),
				position=text_location
			)
		else:
			self.write_and_fade(
				TexMobject(f"({example_number})\\rightarrow({example_number * self.multiply_by})"),
				position=text_location
			)
		
		multiply_arrow_example = Arrow(
			self.other_number_line.number_to_point(example_number), # from
			self.real_number_line.number_to_point(example_number * self.multiply_by), # to
			color = BLUE, buff = MED_LARGE_BUFF
		)
		# self.play( ShowCreation(multiply_arrow_example) )
		self.play( Transform(self.multiply_arrow, multiply_arrow_example) )


class StretchNumberLine_example_0(StretchNumberLine):
	CONFIG = {
		"multiply_by": 0,
		"multiply_example": [
			(-2, 2 * LEFT),
			(1.5, 2 * RIGHT),
			(-1, 2 * LEFT),
			(0, 2 * LEFT),
		],
		"display_text": False,
	}
class StretchNumberLine_example_2(StretchNumberLine):
	CONFIG = {
		"multiply_by": 2,
		"multiply_example": [
			(-2, 2 * LEFT),
			(1.5, 2 * RIGHT),
			(-1, 2 * LEFT),
			(0, 2 * RIGHT),
		],
		"display_text": False,
	}
class StretchNumberLine_example_1_5(StretchNumberLine):
	CONFIG = {
		"multiply_by": 1.5,
		"multiply_example": [
			(-2, 2 * LEFT),
			(1.5, 2 * RIGHT),
			(-1, 2 * LEFT),
			(0, 2 * RIGHT),
		],
		"display_text": False,
	}
class StretchNumberLine_example_3(StretchNumberLine):
	CONFIG = {
		"multiply_by": 3,
		"multiply_example": [
			(-2, 2 * LEFT),
			(1.5, 2 * RIGHT),
			(-1, 2 * LEFT),
			(0, 2 * RIGHT),
		],
		"display_text": False,
	}


class RotateNumberLine(Scene):
	CONFIG = {
		"number_line_min": -6,
		"number_line_max":  6,

		"write_run_time": 1,
	}
	def construct(self):
		# create the number line
		self.number_line = number_line = NumberLine(
			x_min=self.number_line_min,
			x_max=self.number_line_max
		)
		number_line.add_numbers()

		self.add(number_line)
		self.play(
			Write(number_line)
		)

		self.write_and_fade( TextMobject("Let us look at the act of multiplying by (-1)"), position=2 * DOWN )
		self.write_and_fade( TextMobject("Which is equivalent to rotating by 180 degrees"), position=2 * DOWN )
		self.wait(1)

		self.play(
			Rotate( number_line, 180 * DEGREES ),
			run_time=1.5
		)

		self.wait(2)

	def write_and_fade(self, obj, add=True, position=None):
		if position is not None:
			obj.move_to(position)
		if add:
			self.add(obj)
		self.play( Write(obj) , run_time=self.write_run_time)
		self.wait()
		self.play( FadeOut(obj) )


class RotateNumberLine_Twice(Scene):
	CONFIG = {
		"number_line_min": -6,
		"number_line_max":  6,

		"write_run_time": 1,
	}
	def construct(self):
		# create the number line
		self.number_line = number_line = NumberLine(
			x_min=self.number_line_min,
			x_max=self.number_line_max
		)
		number_line.add_numbers()

		number_line_text = TextMobject("(number line)")
		number_line_text.move_to(2 * DOWN + 3 * LEFT)

		self.add(number_line, number_line_text)
		self.play(
			Write(number_line),
			Write(number_line_text)
		)

		self.wait(1)

		multiply_once = TexMobject("\\cdot(-1)")
		multiply_once.move_to(2 * DOWN + 0.9 * LEFT)
		self.add(multiply_once)
		self.play(
			Rotate( number_line, 180 * DEGREES ),
			Write(multiply_once),
			run_time=1.5
		)

		self.wait(1)

		multiply_twice = TexMobject("\\cdot(-1)")
		multiply_twice.move_to(2 * DOWN + 0.3 * RIGHT)
		self.add(multiply_twice)
		self.play(
			Rotate( number_line, 180 * DEGREES ),
			Write(multiply_twice),
			run_time=1.5
		)

		self.wait(2)

	def write_and_fade(self, obj, add=True, position=None):
		if position is not None:
			obj.move_to(position)
		if add:
			self.add(obj)
		self.play( Write(obj) , run_time=self.write_run_time)
		self.wait()
		self.play( FadeOut(obj) )

class StretchNumberLine_summary(Scene):
	CONFIG = {
		"number_line_min": -6,
		"number_line_max":  6,
		"number_line_position": 2 * UP,

		"multiply_by": 2,

		"write_run_time": 1,
	}
	def construct(self):
		# create the number line
		self.real_number_line = number_line = NumberLine(
			x_min=self.number_line_min,
			x_max=self.number_line_max
		)
		number_line.add_numbers()
		number_line.move_to(self.number_line_position)

		self.add(number_line)
		self.play(
			Write(number_line)
		)

		# create the second number line
		self.other_number_line = number_line_2 = self.real_number_line.copy()
		self.add(number_line_2)
		self.play(
			number_line_2.shift, (-2) * self.number_line_position
		)

		self.write_and_fade(
			TextMobject("First, we multiply by %s" % self.multiply_by),
			position=2 * LEFT
		)

		# define 2 arrows.
		# since the animation of stretching the numberline occurs simultaniously to the stretching of the arrow,
		# 	I created both arrows according to the numberline before stretching it,
		# 	which means that both arrows are equal except for their initial position
		self.multiply_arrow = multiply_arrow_before_stretch = Arrow(
			self.other_number_line.number_to_point(1), # from
			self.real_number_line.number_to_point(self.multiply_by), # to
			color = RED, buff = MED_LARGE_BUFF
		)
		multiply_arrow_after_stretch = Arrow(
			self.other_number_line.number_to_point(self.multiply_by), # from
			self.real_number_line.number_to_point(self.multiply_by), # to
			color = RED, buff = MED_LARGE_BUFF
		)
		self.play( ShowCreation(multiply_arrow_before_stretch) )
	
		self.wait(1)

		self.play(
			number_line_2.stretch, self.multiply_by, 0,
			# stretch moves the number line a bit to the right, so I fix it
			number_line_2.shift, fix_stretch(self.multiply_by),

			Transform(multiply_arrow_before_stretch, multiply_arrow_after_stretch),

			# for debugging purpose. to place both number lines on top of each other
			# number_line_2.shift, 2 * self.number_line_position
		)
		self.wait(2)



		self.multiply_by = 1.5
		self.write_and_fade(
			TextMobject("Then, by %s" % self.multiply_by),
			position=2 * LEFT
		)
		multiply_arrow_before_stretch_new = Arrow(
			self.other_number_line.number_to_point(1), # from
			self.real_number_line.number_to_point(3), # to
			color = RED, buff = MED_LARGE_BUFF
		)
		self.play(Transform(multiply_arrow_before_stretch, multiply_arrow_before_stretch_new))

		multiply_arrow_after_stretch_new = Arrow(
			self.other_number_line.number_to_point(self.multiply_by), # from
			self.real_number_line.number_to_point(3), # to
			color = RED, buff = MED_LARGE_BUFF
		)
		self.play(
			number_line_2.stretch, self.multiply_by, 0,
			# stretch moves the number line a bit to the right, so I fix it
			number_line_2.shift, fix_stretch(self.multiply_by),

			Transform(multiply_arrow_before_stretch, multiply_arrow_after_stretch_new),

			# for debugging purpose. to place both number lines on top of each other
			# number_line_2.shift, 2 * self.number_line_position
		)
		self.wait(2)




		self.multiply_by = 0.5
		self.write_and_fade(
			TextMobject("Finally, by %s" % self.multiply_by),
			position=2 * LEFT
		)
		multiply_arrow_before_stretch_new = Arrow(
			self.other_number_line.number_to_point(1), # from
			self.real_number_line.number_to_point(1.5), # to
			color = RED, buff = MED_LARGE_BUFF
		)
		self.play(Transform(multiply_arrow_before_stretch, multiply_arrow_before_stretch_new))
		multiply_arrow_after_stretch_new = Arrow(
			self.other_number_line.number_to_point(self.multiply_by), # from
			self.real_number_line.number_to_point(1.5), # to
			color = RED, buff = MED_LARGE_BUFF
		)
		self.play(
			number_line_2.stretch, self.multiply_by, 0,
			# stretch moves the number line a bit to the right, so I fix it
			number_line_2.shift, 0.2 * RIGHT,

			Transform(multiply_arrow_before_stretch, multiply_arrow_after_stretch_new),

			# for debugging purpose. to place both number lines on top of each other
			# number_line_2.shift, 2 * self.number_line_position
		)


		self.wait(3)

	def write_and_fade(self, obj, add=True, position=None):
		if position is not None:
			obj.move_to(position)
		if add:
			self.add(obj)
		self.play( Write(obj) , run_time=self.write_run_time)
		self.wait()
		self.play( FadeOut(obj) )

class StretchNumberLine_summary_negative(Scene):
	CONFIG = {
		"number_line_min": -6,
		"number_line_max":  6,
		"number_line_position": 2 * UP,

		"multiply_by": 3,

		"write_run_time": 1,
	}
	def construct(self):
		# create the number line
		self.real_number_line = number_line = NumberLine(
			x_min=self.number_line_min,
			x_max=self.number_line_max
		)
		number_line.add_numbers()
		number_line.move_to(self.number_line_position)

		self.add(number_line)
		self.play(
			Write(number_line)
		)

		# create the second number line
		self.other_number_line = number_line_2 = self.real_number_line.copy()
		self.add(number_line_2)
		self.play(
			number_line_2.shift, (-2) * self.number_line_position
		)

		self.write_and_fade(
			TextMobject("First, we will multiply by (-1)"),
			position=2 * LEFT
		)
		self.write_and_fade(
			TextMobject("Then, we will multiply by (3)"),
			position=2 * LEFT
		)

		# define 2 arrows.
		# since the animation of stretching the numberline occurs simultaniously to the stretching of the arrow,
		# 	I created both arrows according to the numberline before stretching it,
		# 	which means that both arrows are equal except for their initial position
		multiply_arrow = Arrow(
			self.other_number_line.number_to_point(1), # from
			self.real_number_line.number_to_point(self.multiply_by), # to
			color = RED, buff = MED_LARGE_BUFF
		)
		multiply_arrow_negative = Arrow(
			self.other_number_line.number_to_point(-1), # from
			self.real_number_line.number_to_point(-self.multiply_by), # to
			color = RED, buff = MED_LARGE_BUFF
		)
		multiply_arrow_negative_stretched = Arrow(
			self.other_number_line.number_to_point(-self.multiply_by), # from
			self.real_number_line.number_to_point(-self.multiply_by), # to
			color = RED, buff = MED_LARGE_BUFF
		)
		self.play( ShowCreation(multiply_arrow) )
	
		self.wait(1)

		self.play(
			Rotate( number_line_2, 180 * DEGREES ),
			Transform(multiply_arrow, multiply_arrow_negative),
		)
		self.wait()
		self.play(
			number_line_2.stretch, self.multiply_by, 0,
			# stretch moves the number line a bit to the right, so I fix it
			number_line_2.shift, fix_stretch(self.multiply_by) * (-2),

			Transform(multiply_arrow, multiply_arrow_negative_stretched),

			# for debugging purpose. to place both number lines on top of each other
			# number_line_2.shift, 2 * self.number_line_position
		)
		
		self.wait(3)

	def write_and_fade(self, obj, add=True, position=None):
		if position is not None:
			obj.move_to(position)
		if add:
			self.add(obj)
		self.play( Write(obj) , run_time=self.write_run_time)
		self.wait()
		self.play( FadeOut(obj) )

class StretchNumberLine_3_times(Scene):
	CONFIG = {
		"number_line_min": -10,
		"number_line_max":  10,
		"number_line_position": 2 * UP,

		"multiply_by": 2,

		"title": Title("Normal Multiplication"),

		"dot_color": YELLOW,

		"write_run_time": 1,

		"display_text": True,
	}
	def construct(self):
		# create the number line
		self.real_number_line = number_line = NumberLine(
			x_min=self.number_line_min,
			x_max=self.number_line_max
		)
		number_line.add_numbers()
		number_line.move_to(self.number_line_position)
		number_line.stretch(1 / 1.5, 0)

		self.add(number_line)
		self.play(
			Write(number_line)
		)

		# create the second number line
		self.other_number_line = number_line_2 = self.real_number_line.copy()
		self.add(number_line_2)
		self.play(
			number_line_2.shift, (-2) * self.number_line_position
		)

		# define 2 arrows.
		# since the animation of stretching the numberline occurs simultaniously to the stretching of the arrow,
		# 	I created both arrows according to the numberline before stretching it,
		# 	which means that both arrows are equal except for their initial position
		arrows = []
		for i in range(3):
			# arrow before multiplication
			arrows.append(
				Arrow(
					self.other_number_line.number_to_point( self.multiply_by**i ), # from
					self.real_number_line.number_to_point(  self.multiply_by**(i+1) ), # to
					color = RED, buff = MED_LARGE_BUFF
				)
			)
			# arrow after multiplication
			arrows.append(
				Arrow(
					self.other_number_line.number_to_point( self.multiply_by**(i+1) ), # from
					self.real_number_line.number_to_point(  self.multiply_by**(i+1) ), # to
					color = RED, buff = MED_LARGE_BUFF
				)
			)
			
		self.multiply_arrow = arrows[0]
		self.play( ShowCreation(self.multiply_arrow) )
		self.wait(1)

		for i in range(3):
			self.play(
				number_line_2.stretch, self.multiply_by, 0,
				# stretch moves the number line a bit to the right, so I fix it
				number_line_2.shift, fix_stretch(self.multiply_by**(i+1) / 1.5),

				Transform(self.multiply_arrow, arrows[2*i + 1]),

				# for debugging purpose. to place both number lines on top of each other
				# number_line_2.shift, 2 * self.number_line_position
			)
			if i ==2: break
			self.play(
				Transform(self.multiply_arrow, arrows[2*(i+1)]),
			)

		self.wait(3)

	def write_and_fade(self, obj, add=True, position=None):
		if position is not None:
			obj.move_to(position)
		if add:
			self.add(obj)
		self.play( Write(obj) , run_time=self.write_run_time)
		self.wait()
		self.play( FadeOut(obj) )


class RotateComplexPlane(ComplexTransformationScene):
	CONFIG = {
		"plane_config": {},

		"roots": 3,

		"circle_radius": 1,

		"dot_color": YELLOW,
		"write_run_time": 1,

		"display_text": True,

		"dot_positions": [
			2 * UR,
			2 * UL,
			2 * DL,
		],
	}
	def construct(self):
		self.add_plane()
		if self.display_text:
			self.write_and_fade(TextMobject("This is the complex plane"), position=2.3*UP + 3.5*LEFT)
			self.wait()


		if self.display_text:
			self.write_and_fade(TextMobject("Let us draw the unit circle"), position=2.3*UP + 3.5*LEFT)

		unit_circle = Circle(radius=self.circle_radius)
		self.add(unit_circle)

		self.play( Write(unit_circle) )
		self.wait()


		if self.display_text:
			self.write_and_fade(TextMobject("Now we can visualise our solutions"), position=2.3 * UP + 1.8 * LEFT)

		dots = [Dot(self.z_to_point(i)) for i in self.get_all_roots_of_1()]
		angles = self.get_all_angles()
		

		arrows = []
		
		for dot, angle, position in zip(dots, angles, self.dot_positions):
			angle_tex = TexMobject(f"{angle:.0f}^\\circ")
			angle_tex.move_to(position)

			arrow = Arrow(
				position, # from
				dot.get_center(), # to
				color = YELLOW,
				buff = MED_LARGE_BUFF
			)
			arrows.append(arrow)

			self.add(dot, angle_tex, arrow)
			self.play(
				Write(dot),
				Write(angle_tex),
				Write(arrow),
			)

		self.wait(3)

	def add_plane(self):
		self.plane = ComplexPlane(**self.plane_config)
		self.plane.add_coordinates()
		self.add(self.plane)

	def get_all_angles(self):
		return [360*i/self.roots for i in range(self.roots)]

	def get_all_roots_of_1(self):
		return [
			self.circle_radius * complex(np.cos(angle*DEGREES), np.sin(angle*DEGREES))
			for angle in self.get_all_angles()
		]

	def write_and_fade(self, obj, add=True, position=None, fade=True):
		if position is not None:
			obj.move_to(position)
		if add:
			self.add(obj)
		self.play( Write(obj) , run_time=self.write_run_time)
		self.wait()
		if fade:
			self.play( FadeOut(obj) )

class RotateComplexPlane_example_1(RotateComplexPlane):
	CONFIG = {
		"roots": 4,
		"dot_positions": [
			2 * UR,
			2 * UL,
			2 * DL,
			2 * DR,
		],
		"display_text": False,
	}
class RotateComplexPlane_example_2(RotateComplexPlane):
	CONFIG = {
		"roots": 3,
		"circle_radius": np.power(2, 1/3),
		"dot_positions": [
			2 * UR,
			2 * UL + 1.5 * LEFT,
			2 * DL + 1.5 * LEFT,
		],
		"display_text": False,
	}
class RotateComplexPlane_example_3(RotateComplexPlane):
	CONFIG = {
		"roots": 6,
		"dot_positions": [
			(+1) * (3 * RIGHT + 1 * UP),
			(+1) * (1 * RIGHT + 3 * UP),
			(+1) * (2 * UL),
			(-1) * (3 * RIGHT + 1 * UP),
			(-1) * (1 * RIGHT + 3 * UP),
			(-1) * (2 * UL),
		],
		"display_text": False,
	}
class RotateComplexPlane_example_4(RotateComplexPlane):
	CONFIG = {
		"roots": 4,
		"circle_radius": np.power(2, 1/4),
		"dot_positions": [
			2 * UR,
			2 * UL,
			2 * DL,
			2 * DR,
		],
		"display_text": False,
	}

class RotateComplexPlane_by_root_of_2(ComplexTransformationScene):
	CONFIG = {
		"plane_config": {},

		"root": 3,
		"root_text": "3rd",
		"root_of": 2,

		"solution_index": 1,

		"magnitude_tex_location": 2.3 * DOWN + 4 * RIGHT,
		"angle_tex_location"    : 3.3 * DOWN + 4.5 * RIGHT,
		"solution_tex_location" : 2.3 * DOWN + 4 * LEFT,

		"write_run_time" : 1,
		# "write_run_time" : 0.25,
		"write_wait_time": DEFAULT_WAIT_TIME, # 1
		# "write_wait_time": 0.25, # 1

		"display_text": True,
	}
	def construct(self):
		self.add_plane()

		self.magnitude      = np.power(self.root_of, 1/self.root)
		self.solution_angle = self.get_all_angles()[self.solution_index]
		self.angle_rad      = self.solution_angle * DEGREES

		if self.display_text:
			self.write_and_fade(TextMobject(f"We are looking for the {self.root_text} root of {self.root_of}"), position=2.3 * UP + 2 * LEFT)

			self.write_and_fade(TextMobject(f"Let us look at the solution with {self.solution_angle:.0f} degrees"), position=2.3 * UP + 1.1 * LEFT)

			temp_1 = self.write_and_fade(
				TextMobject(f"since it is the {self.root_text} root, it will have a magnitude of"),
				position=2.3 * UP + 1 * LEFT,
				fade=False,
				wait=False,
			)
			temp_2 = self.write_and_fade(
				TexMobject(f"\\sqrt[{self.root}]{self.root_of}\\approx{self.magnitude:.3f}"),
				position=1.3 * UP + 2.8 * RIGHT,
				fade=False
			)
			self.play(
				FadeOut(temp_1),
				FadeOut(temp_2),
			)

		#
		# calculate the initial point
		#
		# the _1 suffix stands for power of 1
		self.solution        = solution_1        = self.get_solution()
		self.solution_vector = solution_vector_1 = self.complex_to_vector(solution_1)
		self.solution_dot    = solution_dot_1    = Dot(self.z_to_point(solution_1))

		self.add(solution_vector_1, solution_dot_1)
		self.play(
			Write(solution_vector_1),
			Write(solution_dot_1),
		)

		self.initiate_tex()

		# 
		# display details on screen
		# 
		# self.magnitude_tex = TexMobject(f"Magnitude\\approx{self.magnitude:.3f}")
		# self.magnitude_tex.move_to(2.3 * DOWN + 2 * RIGHT)
		# self.angle_tex = TexMobject(f"angle={self.solution_angle:.0f}^\\circ")
		# self.angle_tex.move_to(3.3 * DOWN + 2 * RIGHT)
		# self.solution_tex = TexMobject(f"z={np.around(self.solution, 3)}")
		# self.solution_tex.move_to(2.3 * DOWN + 2 * LEFT)

		latest_solution = self.solution
		# skip the first time, since it was calculated manually just above this line
		for i in range(1, self.root):
			newest_solution_step_1 = self.step_1(latest_solution)
			newest_solution_step_2 = self.step_2(latest_solution)
			latest_solution = newest_solution_step_2

		self.wait(3)

	def add_plane(self):
		self.plane = ComplexPlane(**self.plane_config)
		self.plane.add_coordinates()
		self.add(self.plane)

	def get_all_angles(self):
		return [360*i/self.root for i in range(self.root)]

	def get_solution(self):
		return self.magnitude * complex(
			np.cos(self.angle_rad),
			np.sin(self.angle_rad)
		)

	def complex_to_vector(self, c):
		return Vector(c.real * RIGHT + c.imag * UP)

	def step_1(self, last_solution):
		self.write_and_fade(TextMobject(f"Step 1: multiply by magnitude"), position=2.3 * UP + 3.5 * LEFT)

		new_solution        = last_solution * self.magnitude
		new_solution_vector = self.complex_to_vector(new_solution)
		new_solution_dot    = Dot(self.z_to_point(new_solution))

		magnitude_tex, angle_tex, solution_tex = self.get_new_tex(new_solution)

		self.play(
			Transform(self.solution_vector, new_solution_vector),
			Transform(self.solution_dot,    new_solution_dot),

			Transform(self.magnitude_tex, magnitude_tex),
			Transform(self.angle_tex    , angle_tex),
			Transform(self.solution_tex , solution_tex),
		)

		return new_solution

	def step_2(self, last_solution):
		self.write_and_fade(TextMobject(f"Step 2: rotate by angle"), position=2.3 * UP + 3 * LEFT)

		new_solution = last_solution * self.solution

		arc = Arc(
			start_angle = np.angle(last_solution),
			angle = self.angle_rad,
			radius = 0.5,
		)
		self.add(arc)
		self.play( Write(arc) )

		magnitude_tex, angle_tex, solution_tex = self.get_new_tex(new_solution)

		self.play(
			Rotate( self.solution_vector, self.angle_rad, about_point=ORIGIN ),
			Rotate( self.solution_dot,    self.angle_rad, about_point=ORIGIN ),

			Transform(self.magnitude_tex, magnitude_tex),
			Transform(self.angle_tex    , angle_tex),
			Transform(self.solution_tex , solution_tex),
		)

		self.play( FadeOut(arc) )
		return new_solution

	def initiate_tex(self):
		self.magnitude_tex = magnitude_tex = TexMobject(f"Magnitude\\approx{self.magnitude:.3f}")
		magnitude_tex.move_to(self.magnitude_tex_location)

		self.angle_tex = angle_tex = TexMobject(f"angle={self.solution_angle:.1f}^\\circ")
		angle_tex.move_to(self.angle_tex_location)

		self.solution_tex = solution_tex = TexMobject(f"z={np.around(self.solution, 3)}")
		solution_tex.move_to(self.solution_tex_location)

		self.add(magnitude_tex, angle_tex, solution_tex)
		self.play(
			Write(magnitude_tex),
			Write(angle_tex),
			Write(solution_tex),
		)

	def get_new_tex(self, current_solution):
		magnitude_tex = TexMobject(f"Magnitude\\approx{abs(current_solution):.3f}")
		magnitude_tex.move_to(self.magnitude_tex_location)

		# fun with rounding floats
		angle = np.angle(current_solution, deg=True)
		if np.around(angle) < 0:
			angle += 360
		if np.around(angle) >= 360:
			angle -= 360
		if np.around(angle) == 0:
			angle = 0.0

		angle_tex = TexMobject(f"angle={angle:.1f}^\\circ")
		angle_tex.move_to(self.angle_tex_location)

		solution_tex = TexMobject(f"z={np.around(current_solution, 3)}")
		solution_tex.move_to(self.solution_tex_location)

		return magnitude_tex, angle_tex, solution_tex

	def write_and_fade(self, obj, add=True, position=None, fade=True, wait=True):
		if position is not None:
			obj.move_to(position)
		if add:
			self.add(obj)
		self.play( Write(obj) , run_time=self.write_run_time)
		if wait:
			self.wait()
		if fade:
			self.play( FadeOut(obj) )
		return obj


class RotateComplexPlane_by_root_of_2_example(RotateComplexPlane_by_root_of_2):
	CONFIG = {
		"write_run_time" : 0.25,
		"write_wait_time": 0.25,
		"display_text": False,
	}
# 2_3_1 : 
# root 3 of 2, 1st solution
class RotateComplexPlane_by_root_of_2_example_2_3_2(RotateComplexPlane_by_root_of_2_example):
	CONFIG = {
		"root": 3,
		"root_of": 2,
		"solution_index": 2,
	}
class RotateComplexPlane_by_root_of_2_example_2_4_1(RotateComplexPlane_by_root_of_2_example):
	CONFIG = {
		"root": 4,
		"root_of": 2,
		"solution_index": 1,
	}
class RotateComplexPlane_by_root_of_2_example_1_4_1(RotateComplexPlane_by_root_of_2_example):
	CONFIG = {
		"root": 4,
		"root_of": 1,
		"solution_index": 1,
	}
class RotateComplexPlane_by_root_of_2_example_3_6_1(RotateComplexPlane_by_root_of_2_example):
	CONFIG = {
		"root": 6,
		"root_of": 3,
		"solution_index": 1,
	}
