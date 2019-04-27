from big_ol_pile_of_manim_imports import *

OUTPUT_DIRECTORY = "my_project_test"

def parabola(height = 0, center_point = 0, sign=1):
	return lambda x: sign*(x - center_point)**2 + height

def parabola_tex(height = 0, center_point = 0, sign=1):
	s = ""
	if sign == -1:
		s += "-"

	if center_point:
		s += "(x-%s)^2" % center_point
	else:
		s += "(x)^2"

	if height:
		s += " %s %s" % ('-' if height < 0 else '+', abs(height))

	return s

class VectorFieldParabola(GraphScene):
	CONFIG = {
		# graph parameters
		"x_min" : -5,
		"x_max" : 5,
		"y_min" : -5,
		"y_max" : 5,
		"graph_origin" : ORIGIN,

		"coordinate_plane_config": {
			# "y_line_frequency": PI / 2,
			"y_line_frequency": 1,
			"x_line_frequency": 1,
			"y_axis_config": {
				"unit_size": 1,
			},
			"y_max": 5,
			"faded_line_ratio": 4,
			"background_line_style": {
				"stroke_width": 1,
			},
		},
		"vector_field_config": {
			"max_magnitude": 3,
			# "delta_x": 2,
			# "delta_y": 2,
		},

		"run_time_first": 1,
		"run_time": 0.5,

		# function parameters
		"function_color" : BLUE,
		"height": 2,
		"center_point": 0,
		"sign": -1,

		"walk_vector_right": 1.1,
		"walk_vector_left": -1.1,
	}
	def construct(self):
		self.initialize_plane()

		self.initialize_functions()

		self._play_first_time()
		for i in range(1, self._range):
			self._play_next_time()

		self.wait(2)

	def initialize_plane(self):
		self.setup_axes()
		plane = self.plane = NumberPlane(
			**self.coordinate_plane_config
		)
		return plane

	def initialize_functions(self):
		self.functions = self.iter_functions()
		self.first_func_graph = next(self.functions)

		self.equations = self.iter_equations()
		self.first_equation = next(self.equations)

		self.vector_fields = self.iter_vector_field()
		self.initialize_vector_field()

	def initialize_vector_field(self):
		self.vector_field = next(self.vector_fields)
		self.vector_field.sort(get_norm)

	def show_full_vector_field(self):
		self.vector_field

		growth = LaggedStartMap(
			GrowArrow, self.vector_field,
			run_time=1,
			lag_ratio=0.01,
		)
		self.add(
			growth.mobject,
		)
		self.play(
			growth,
		)

	def _play_first_time(self):
		self.play(
			ShowCreation(self.first_func_graph, run_time=self.run_time_first),
			Animation(self.first_equation),
		)
		self.show_full_vector_field()

	def _play_next_time(self):
		self.play(
			Transform(self.first_equation, next(self.equations)),
			Transform(self.first_func_graph, next(self.functions), run_time = self.run_time),
			Transform(self.vector_field, next(self.vector_fields)),
		)
		self.wait()

	def _setup_equation(self, *args, **kwargs):
		equation = TexMobject(self.function_tex(*args, **kwargs))
		equation.to_corner(UP + RIGHT)
		equation.set_color(self.function_color)
		equation.add_background_rectangle()
		return equation

	def iter_functions(self):
		self.function = parabola(
			height=self.height,
			center_point=self.center_point,
			sign=self.sign,
		)
		yield self.get_graph(
			self.function,
			self.function_color
		)

	def iter_equations(self):
		yield self._setup_equation(
			height=self.height,
			center_point=self.center_point,
			sign=self.sign,
		)

	def iter_vector_field(self):
		while 1:
			yield VectorField(
				self.vector_field_func,
				**self.vector_field_config,
			)

	@property
	def _range(self):
		return 1

	def function_tex(self, *args, **kwargs):
		return parabola_tex(*args, **kwargs)

	def function(self, *args, **kwargs):
		return parabola(*args, **kwargs)

	def vector_field_func(self, point):
		x, y = self.plane.point_to_coords(point)

		parabola_value = self.function(x)

		if parabola_value == 0:
			if y > 0: return DOWN
			elif y < 0: return UP
			else: return ORIGIN
		elif parabola_value > 0:
			if 0 <= y < parabola_value: return RIGHT*.5
			else: return ORIGIN
		else: # parabola_value < 0
			if 0 >= y > parabola_value: return LEFT*10
			else: return ORIGIN

	def walk_along(self):
		point_right = VectorizedPoint(
			self.walk_vector_right * RIGHT +
			self.function(self.walk_vector_right) * UP
		)
		point_left = VectorizedPoint(
			self.walk_vector_left * RIGHT +
			self.function(self.walk_vector_left) * UP
		)
		self.add(move_along_vector_field(
			point_right,
			self.function,
		))
		self.add(move_along_vector_field(
			point_left,
			self.function,
		))


class VectorFieldParabolaUpDown(VectorFieldParabola):
	CONFIG = {
		# function parameters
		"height_min" : -2,
		"height_max" : 2,
		"height_step" : 1,
	}

	def iter_functions(self):
		for height in self._height_range:
			self.function = parabola(
				height=height,
				center_point=self.center_point
			)
			yield self.get_graph(
				self.function,
				self.function_color
			)

	def iter_equations(self):
		for height in self._height_range:
			yield self._setup_equation(
				height=height,
				center_point=self.center_point
			)

	@property
	def _height_range(self):
		return np.arange(self.height_min, self.height_max + self.height_step, self.height_step)

	@property
	def _range(self):
		return len(self._height_range)

class VectorFieldParabolaLeftRight(VectorFieldParabola):
	CONFIG = {
		# function parameters
		"center_point_min" : -2,
		"center_point_max" : 2,
		"center_point_step" : 1,
		"height" : 2,
		"sign" : -1,
	}

	def iter_functions(self):
		for center_point in self._center_point_range:
			self.function = parabola(
				height=self.height,
				center_point=center_point,
				sign=self.sign
			)
			yield self.get_graph(
				parabola(
					height=self.height,
					center_point=center_point,
					sign=self.sign
				),
				self.function_color
			)

	def iter_equations(self):
		for center_point in self._center_point_range:
			yield self._setup_equation(
				height=self.height,
				center_point=center_point,
				sign=self.sign
			)

	@property
	def _center_point_range(self):
		return np.arange(
			self.center_point_min, 
			self.center_point_max + self.center_point_step, 
			self.center_point_step
		)

	@property
	def _range(self):
		return len(self._center_point_range)


class MyParameterizedCurve(GraphScene):
	CONFIG = {
		"curve_config": {
	        "t_min": -.99,
	        "t_max": 100,
	        "dt": 1e-8,
	        # TODO, be smarter about figuring these out?
	        "discontinuities": [],
        },

		"function_color" : BLUE,
		# graph parameters
		"x_min" : -5,
		"x_max" : 5,
		"y_min" : -5,
		"y_max" : 5,
		"graph_origin" : ORIGIN,
	}

	def function(self, t):
		return np.array([
			(3*t) / (1+t**3),
			(3*t**2) / (1+t**3),
			0
		])
	def construct(self):
		self.setup_axes()

		my_curve = ParametricInfiniteFunction(self.function, **self.curve_config)
		self.play(
			ShowCreation(my_curve, run_time = 2),
			Animation(self._setup_equation()),
		)
		self.wait(2)

	def _setup_equation(self, *args, **kwargs):
		equation_tex = "(3t/{1+t^3}, 3t^2/{1+t^3})"
		equation = TexMobject(equation_tex)
		equation.to_corner(UP + RIGHT)
		equation.set_color(self.function_color)
		equation.add_background_rectangle()
		return equation
