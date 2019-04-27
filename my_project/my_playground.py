
class PlotParabola(GraphScene):
	CONFIG = {
		# graph parameters
		"x_min" : -5,
		"x_max" : 5,
		"y_min" : -5,
		"y_max" : 5,
		"graph_origin" : DOWN + 2*LEFT,
	}
	def construct(self):
		self.setup_axes()
		self._init_functions()
		self._play_all_times(True)

	def _init_functions(self):
		func_graphs = self.iter_functions()

		equations = self.iter_equations()

		self.first_func_graph = func_graphs.pop(0)
		self.first_equation   = equations.pop(0)
		self.func_graphs = func_graphs
		self.equations = equations

	def _play_first_time(self):
		self.play(
			ShowCreation(self.first_func_graph, run_time = 1),
			Animation(self.first_equation),
		)

	def _play_all_times(self, play_first=False):
		if play_first:
			self._play_first_time()

		for graph, equation in zip(self.func_graphs, self.equations):
			self.play(
				Transform(self.first_equation, equation),
				Transform(self.first_func_graph, graph, run_time = self.run_time),
			)
			self.wait()
		self.wait(2)

	def _setup_equation(self, *args, **kwargs):
		equation = TexMobject(parabola_tex(*args, **kwargs))
		equation.to_corner(UP + RIGHT)
		equation.set_color(self.function_color)
		equation.add_background_rectangle()
		return equation

class PlotParabolaUpDown(PlotParabola):
	CONFIG = {
		# function parameters
		"function_color" : BLUE,
		"center_point" : 0,
		"height_min" : -2,
		"height_max" : 2,
		"height_step" : 1,
		"run_time" : 0.5,
		# graph parameters
		"x_min" : -5,
		"x_max" : 5,
		"y_min" : -5,
		"y_max" : 5,
		"graph_origin" : DOWN + 2*LEFT,
	}

	def iter_functions(self):
		return [
			self.get_graph(
				parabola(
					height=height,
					center_point=self.center_point
				),
				self.function_color
			)
			for height in self._height_range
		]

	def iter_equations(self):
		return [
			self._setup_equation(
				height=height,
				center_point=self.center_point
			)
			for height in self._height_range
		]

	@property
	def _height_range(self):
		return np.arange(self.height_min, self.height_max + self.height_step, self.height_step)

class PlotParabolaLeftRight(PlotParabola):
	CONFIG = {
		# function parameters
		"function_color" : BLUE,
		"center_point_min" : -2,
		"center_point_max" : 2,
		"center_point_step" : 1,
		"run_time" : 0.5,
		"height" : 2,
		"sign" : -1,
		# graph parameters
		"x_min" : -5,
		"x_max" : 5,
		"y_min" : -5,
		"y_max" : 5,
		"graph_origin" : DOWN + 2*LEFT,
	}

	def iter_functions(self):
		return [
			self.get_graph(
				parabola(
					height=self.height,
					center_point=center_point,
					sign=self.sign
				),
				self.function_color
			)
			for center_point in self._center_point_range
		]

	def iter_equations(self):
		return [
			self._setup_equation(
				height=self.height,
				center_point=center_point,
				sign=self.sign
			)
			for center_point in self._center_point_range
		]

	@property
	def _center_point_range(self):
		return np.arange(
			self.center_point_min, 
			self.center_point_max + self.center_point_step, 
			self.center_point_step
		)


class VisualizeStates(Scene):
	CONFIG = {
		"coordinate_plane_config": {
			"y_line_frequency": PI / 2,
			# "x_line_frequency": PI / 2,
			"x_line_frequency": 1,
			"y_axis_config": {
				# "unit_size": 1.75,
				"unit_size": 1,
			},
			"y_max": 4,
			"faded_line_ratio": 4,
			"background_line_style": {
				"stroke_width": 1,
			},
		},
		"little_pendulum_config": {
			"length": 1,
			"gravity": 4.9,
			"weight_diameter": 0.3,
			"include_theta_label": False,
			"include_velocity_vector": True,
			"angle_arc_config": {
				"radius": 0.2,
			},
			"velocity_vector_config": {
				"max_tip_length_to_length_ratio": 0.35,
				"max_stroke_width_to_length_ratio": 6,
			},
			"velocity_vector_multiple": 0.25,
			"max_velocity_vector_length_to_length_ratio": 0.8,
		},
		"big_pendulum_config": {
			"length": 1.6,
			"gravity": 4.9,
			"damping": 0.2,
			"weight_diameter": 0.3,
			"include_velocity_vector": True,
			"angle_arc_config": {
				"radius": 0.5,
			},
			"initial_theta": 80 * DEGREES,
			"omega": -1,
			"set_theta_label_height_cap": True,
		},
		"n_thetas": 11,
		"n_omegas": 7,
		# "n_thetas": 5,
		# "n_omegas": 3,
		"initial_grid_wait_time": 15,
	}

	def construct(self):
		self.initialize_plane()

		simple = False
		if simple:
			self.add(self.plane)
		else:
			self.initialize_grid_of_states()
			self.show_all_states_evolving()
			self.show_grid_of_states_creation()
			self.collapse_grid_into_points()
		self.show_state_with_pair_of_numbers()
		self.show_acceleration_dependence()
		self.show_evolution_from_a_start_state()

	def initialize_grid_of_states(self):
		pendulums = VGroup()
		rects = VGroup()
		state_grid = VGroup()
		thetas = self.get_initial_thetas()
		omegas = self.get_initial_omegas()
		for omega in omegas:
			row = VGroup()
			for theta in thetas:
				rect = Rectangle(
					height=3,
					width=3,
					stroke_color=WHITE,
					stroke_width=2,
					fill_color=DARKER_GREY,
					fill_opacity=1,
				)
				pendulum = Pendulum(
					initial_theta=theta,
					omega=omega,
					top_point=rect.get_center(),
					**self.little_pendulum_config,
				)
				pendulum.add_velocity_vector()
				pendulums.add(pendulum)
				rects.add(rect)
				state = VGroup(rect, pendulum)
				state.rect = rect
				state.pendulum = pendulum
				row.add(state)
			row.arrange(RIGHT, buff=0)
			state_grid.add(row)
		state_grid.arrange(UP, buff=0)

		state_grid.set_height(FRAME_HEIGHT)
		state_grid.center()
		state_grid.save_state(use_deepcopy=True)

		self.state_grid = state_grid
		self.pendulums = pendulums

	def initialize_plane(self):
		plane = self.plane = NumberPlane(
			**self.coordinate_plane_config
		)
		plane.axis_labels = VGroup(
			plane.get_x_axis_label(
				"\\theta", RIGHT, UL, buff=SMALL_BUFF
			),
			plane.get_y_axis_label(
				"\\dot \\theta", UP, DR, buff=SMALL_BUFF
			).set_color(YELLOW),
		)
		for label in plane.axis_labels:
			label.add_background_rectangle()
		plane.add(plane.axis_labels)

		plane.y_axis.add_numbers(direction=DL)

		x_axis = plane.x_axis
		label_texs = ["\\pi \\over 2", "\\pi", "3\\pi \\over 2", "\\tau"]
		values = [PI / 2, PI, 3 * PI / 2, TAU]
		x_axis.coordinate_labels = VGroup()
		x_axis.add(x_axis.coordinate_labels)
		for value, label_tex in zip(values, label_texs):
			for u in [-1, 1]:
				tex = label_tex
				if u < 0:
					tex = "-" + tex
				label = TexMobject(tex)
				label.scale(0.5)
				if label.get_height() > 0.4:
					label.set_height(0.4)
				point = x_axis.number_to_point(u * value)
				label.next_to(point, DR, SMALL_BUFF)
				x_axis.coordinate_labels.add(label)
		return plane

	def show_all_states_evolving(self):
		state_grid = self.state_grid
		pendulums = self.pendulums

		for pendulum in pendulums:
			pendulum.start_swinging()

		self.add(state_grid)
		self.wait(self.initial_grid_wait_time)

	def show_grid_of_states_creation(self):
		self.remove(self.state_grid)
		self.initialize_grid_of_states()  # Again
		state_grid = self.state_grid

		title = TextMobject("All states")
		title.to_edge(UP, buff=MED_SMALL_BUFF)
		self.all_states_title = title

		state_grid.set_height(
			FRAME_HEIGHT - title.get_height() - 2 * MED_SMALL_BUFF
		)
		state_grid.to_edge(DOWN, buff=0)

		def place_at_top(state):
			state.set_height(3)
			state.center()
			state.next_to(title, DOWN)

		middle_row = state_grid[len(state_grid) // 2]
		middle_row_copy = middle_row.deepcopy()
		right_column_copy = VGroup(*[
			row[-1] for row in state_grid
		]).deepcopy()

		for state in it.chain(middle_row_copy, right_column_copy):
			place_at_top(state)

		self.add(title)
		self.play(
			ShowIncreasingSubsets(middle_row),
			ShowIncreasingSubsets(middle_row_copy),
			run_time=2,
			rate_func=linear,
		)
		self.wait()
		self.play(
			ShowIncreasingSubsets(state_grid),
			ShowIncreasingSubsets(right_column_copy),
			run_time=2,
			rate_func=linear,
		)
		self.remove(middle_row_copy)
		self.remove(middle_row)
		self.add(state_grid)
		self.remove(right_column_copy)
		self.play(
			ReplacementTransform(
				right_column_copy[-1],
				state_grid[-1][-1],
				remover=True
			)
		)
		self.wait()

	def collapse_grid_into_points(self):
		state_grid = self.state_grid
		plane = self.plane

		dots = VGroup()
		for row in state_grid:
			for state in row:
				dot = Dot(
					self.get_state_point(state.pendulum),
					radius=0.05,
					color=YELLOW,
					background_stroke_width=3,
					background_stroke_color=BLACK,
				)
				dot.state = state
				dots.add(dot)

		self.add(plane)
		self.remove(state_grid)
		flat_state_group = VGroup(*it.chain(*state_grid))
		flat_dot_group = VGroup(*it.chain(*dots))
		self.clear()  # The nuclear option
		self.play(
			ShowCreation(plane),
			FadeOut(self.all_states_title),
			LaggedStart(*[
				TransformFromCopy(m1, m2)
				for m1, m2 in zip(flat_state_group, flat_dot_group)
			], lag_ratio=0.1, run_time=4)
		)
		self.clear()  # Again, not sure why I need this
		self.add(plane, dots)
		self.wait()

		self.state_dots = dots

	def show_state_with_pair_of_numbers(self):
		axis_labels = self.plane.axis_labels

		state = self.get_flexible_state_picture()
		dot = self.get_state_controlling_dot(state)
		h_line = always_redraw(
			lambda: self.get_tracking_h_line(dot.get_center())
		)
		v_line = always_redraw(
			lambda: self.get_tracking_v_line(dot.get_center())
		)

		self.add(dot)
		anims = [GrowFromPoint(state, dot.get_center())]
		if hasattr(self, "state_dots"):
			anims.append(FadeOut(self.state_dots))
		self.play(*anims)

		for line, label in zip([h_line, v_line], axis_labels):
			# self.add(line, dot)
			self.play(
				ShowCreation(line),
				ShowCreationThenFadeAround(label),
				run_time=1
			)
		for vect in LEFT, 3 * UP:
			self.play(
				ApplyMethod(
					dot.shift, vect,
					rate_func=there_and_back,
					run_time=2,
				)
			)
		self.wait()
		for vect in 2 * LEFT, 3 * UP, 2 * RIGHT, 2 * DOWN:
			self.play(dot.shift, vect, run_time=1.5)
		self.wait()

		self.state = state
		self.state_dot = dot
		self.h_line = h_line
		self.v_line = v_line

	def show_acceleration_dependence(self):
		ode = get_ode()
		thetas = ode.get_parts_by_tex("\\theta")
		thetas[0].set_color(RED)
		thetas[1].set_color(YELLOW)
		ode.move_to(
			FRAME_WIDTH * RIGHT / 4 +
			FRAME_HEIGHT * UP / 4,
		)
		ode.add_background_rectangle_to_submobjects()

		self.play(Write(ode))
		self.wait()
		self.play(FadeOut(ode))

	def show_evolution_from_a_start_state(self):
		state = self.state
		dot = self.state_dot

		self.play(
			Rotating(
				dot,
				about_point=dot.get_center() + UR,
				rate_func=smooth,
			)
		)
		self.wait()

		# Show initial trajectory
		state.pendulum.clear_updaters(recursive=False)
		self.tie_dot_position_to_state(dot, state)
		state.pendulum.start_swinging()
		trajectory = self.get_evolving_trajectory(dot)
		self.add(trajectory)
		for x in range(20):
			self.wait()

		# Talk through start
		trajectory.suspend_updating()
		state.pendulum.end_swinging()
		dot.clear_updaters()
		self.tie_state_to_dot_position(state, dot)

		alphas = np.linspace(0, 0.1, 1000)
		index = np.argmin([
			trajectory.point_from_proportion(a)[1]
			for a in alphas
		])
		alpha = alphas[index]
		sub_traj = trajectory.copy()
		sub_traj.suspend_updating()
		sub_traj.pointwise_become_partial(trajectory, 0, alpha)
		sub_traj.match_style(trajectory)
		sub_traj.set_stroke(width=3)

		self.wait()
		self.play(dot.move_to, sub_traj.get_start())
		self.wait()
		self.play(
			ShowCreation(sub_traj),
			UpdateFromFunc(
				dot, lambda d: d.move_to(sub_traj.get_end())
			),
			run_time=6,
		)
		self.wait()

		# Comment on physical velocity vs. space position
		v_vect = state.pendulum.velocity_vector
		v_line_copy = self.v_line.copy()
		v_line_copy.clear_updaters()
		v_line_copy.set_stroke(PINK, 5)
		td_label = self.plane.axis_labels[1]
		y_axis_copy = self.plane.y_axis.copy()
		y_axis_copy.submobjects = []
		y_axis_copy.match_style(v_line_copy)

		self.play(ShowCreationThenFadeAround(v_vect))
		self.play(
			ShowCreationThenFadeAround(td_label),
			ShowCreationThenFadeOut(y_axis_copy)
		)
		self.play(ShowCreationThenFadeOut(v_line_copy))
		self.wait()

		# Abstract vs. physical
		abstract = TextMobject("Abstract")
		abstract.add_background_rectangle()
		abstract.scale(2)
		abstract.to_corner(UR)
		physical = TextMobject("Physical")
		physical.next_to(state.get_top(), DOWN)

		self.play(
			ApplyMethod(
				self.plane.set_stroke, YELLOW, 0.5,
				rate_func=there_and_back,
				lag_ratio=0.2,
			),
			FadeInFromDown(abstract),
			Animation(state),
		)
		self.wait()
		self.play(FadeInFromDown(physical))
		self.wait()

		# Continue on spiral
		sub_traj.resume_updating()
		state.pendulum.clear_updaters(recursive=False)
		state.pendulum.start_swinging()
		dot.clear_updaters()
		self.tie_dot_position_to_state(dot, state)
		self.wait(20)

	#
	def get_initial_thetas(self):
		angle = 3 * PI / 4
		return np.linspace(-angle, angle, self.n_thetas)

	def get_initial_omegas(self):
		return np.linspace(-1.5, 1.5, self.n_omegas)

	def get_state(self, pendulum):
		return (pendulum.get_theta(), pendulum.get_omega())

	def get_state_point(self, pendulum):
		return self.plane.coords_to_point(
			*self.get_state(pendulum)
		)

	def get_state_dot(self, state):
		dot = Dot(color=PINK)
		dot.move_to(self.get_state_point(state.pendulum))
		return dot

	def get_state_controlling_dot(self, state):
		dot = self.get_state_dot(state)
		self.tie_state_to_dot_position(state, dot)
		return dot

	def tie_state_to_dot_position(self, state, dot):
		def update_pendulum(pend):
			theta, omega = self.plane.point_to_coords(
				dot.get_center()
			)
			pend.set_theta(theta)
			pend.set_omega(omega)
			return pend
		state.pendulum.add_updater(update_pendulum)
		state.pendulum.get_arc_angle_theta = \
			lambda: self.plane.x_axis.point_to_number(dot.get_center())
		return self

	def tie_dot_position_to_state(self, dot, state):
		dot.add_updater(lambda d: d.move_to(
			self.get_state_point(state.pendulum)
		))
		return dot

	def get_tracking_line(self, point, axis, color=WHITE):
		number = axis.point_to_number(point)
		axis_point = axis.number_to_point(number)
		return DashedLine(
			axis_point, point,
			dash_length=0.025,
			color=color,
		)

	def get_tracking_h_line(self, point):
		return self.get_tracking_line(
			point, self.plane.y_axis, WHITE,
		)

	def get_tracking_v_line(self, point):
		return self.get_tracking_line(
			point, self.plane.x_axis, YELLOW,
		)

	def get_evolving_trajectory(self, mobject):
		trajectory = VMobject()
		trajectory.start_new_path(mobject.get_center())
		trajectory.set_stroke(RED, 1)

		def update_trajectory(traj):
			point = mobject.get_center()
			if get_norm(trajectory.points[-1] == point) > 0.05:
				traj.add_smooth_curve_to(point)
		trajectory.add_updater(update_trajectory)
		return trajectory


class IntroduceVectorField(VisualizeStates):
	CONFIG = {
		"vector_field_config": {
			"max_magnitude": 3,
			# "delta_x": 2,
			# "delta_y": 2,
		},
	}

	def construct(self):
		self.initialize_plane()
		self.initialize_vector_field()
		# self.preview_vector_field()
		self.show_full_vector_field()
		# self.show_trajectory()

	def initialize_plane(self):
		super().initialize_plane()
		self.add(self.plane)

	def initialize_vector_field(self):
		self.vector_field = VectorField(
			self.vector_field_func,
			**self.vector_field_config,
		)
		self.vector_field.sort(get_norm)

	def preview_vector_field(self):
		vector_field = self.vector_field

		growth = LaggedStartMap(
			GrowArrow, vector_field,
			run_time=3,
			lag_ratio=0.01,
		)
		self.add(
			growth.mobject,
			vector_field,
		)

		self.play(growth)
		self.wait()
		self.play(FadeOut(vector_field))
		self.remove(growth.mobject)

	def show_full_vector_field(self):
		vector_field = self.vector_field

		growth = LaggedStartMap(
			GrowArrow, vector_field,
			run_time=3,
			lag_ratio=0.01,
		)
		self.add(
			growth.mobject,
		)
		self.play(
			growth,
		)

	def vector_field_func(self, point):
		x, y = self.plane.point_to_coords(point)
		# return np.array([
		# 	2., # x
		# 	1., # y
		# 	0, # z
		# ])
		return np.array([
			y, # x
			-x, # y
			0, # z
		])


class PlotFunctions(GraphScene):
	CONFIG = {
		"x_min" : -10,
		"x_max" : 10,
		"y_min" : -10,
		"y_max" : 10,
		"graph_origin" : ORIGIN ,
		"function_color" : RED ,
		"axes_color" : GREEN,
		"x_labeled_nums" :range(-10,12,2),

		"func_name": "x^2 - r",
	}
	FUNC_PARAMETER = 2

	def construct(self):
		# graph
		self.setup_axes(animate=False)
		func_graph = self.get_graph(
			self.func_to_graph,
			self.function_color
		)

		graph_lab = self.get_graph_label(func_graph, label = self.func_name)
		self.play(ShowCreation(func_graph))
		for x in range(-4,4):
			self.FUNC_PARAMETER = x
			graph_lab_transformed = self.get_graph_label(func_graph, label = self.func_name)
			Transform(graph_lab_transformed, graph_lab, run_time = 2),
			func_text = TextMobject( "func y $= %s$" % self.func_name )
			func_text.to_corner(UP + RIGHT)
			Animation(func_text)
			self.wait()


		# ???
		# vert_line = self.get_vertical_line_to_graph(0 ,func_graph,color=YELLOW)
		label_coord = self.input_to_graph_point(TAU,func_graph)
		# ???

		func_name_display = TexMobject("y = " + self.func_name)
		func_name_display.next_to(label_coord,RIGHT+UP)

		self.play(
			# ShowCreation(vert_line),
			ShowCreation(graph_lab),
			ShowCreation(func_name_display)
		)

	def func_to_graph(self,x):
		return x**2 + self.FUNC_PARAMETER
