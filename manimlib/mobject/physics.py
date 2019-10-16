import numpy as np
import random
from collections import defaultdict

from manimlib.constants import *
from manimlib.mobject.geometry import Arc, Arrow, Circle, DashedLine, Dot, Line
from manimlib.mobject.types.vectorized_mobject import VGroup, VectorizedPoint
from manimlib.mobject.svg.tex_mobject import TexMobject
from manimlib.utils.space_ops import get_norm
from manimlib.mobject.mobject_update_utils import always_redraw
from manimlib.animation.creation import Write


# physical constants.
# the TexMobjects are commented our so that it won't compile them when this file is being used

k_B = 1.38064852e-23
# k_B_tex = TexMobject("1.38064852\\times10^{-23} \\frac{m^2 kg}{s^2 K}")

SPEED_OF_LIGHT = 299_792_458 # m/s
# SPEED_OF_LIGHT_tex = TexMobject("3\\times10^8 \\frac{m}{s}")


#
# UTILS
#

def polar_to_cartesian(r, theta):
	return r*np.cos(theta), r*np.sin(theta)
def cartesian_to_polar(x, y):
	return np.sqrt(x**2 + y**2), np.arctan(y/x)

def almost_equal(x, y):
	return abs(x-y) < 0.01
def almost_same_point(a, b):
	return all(np.around(a, 3) == np.around(b, 3))

#
# Physical mobjects
#
class Particle(Dot):
	# by concention, full word (such as velocity, force) is for the vector, while single letter (v, F) is for the scalar
	CONFIG = {
		# velocity can be either a vector or a scalar
		"velocity": RIGHT, # m/s
		"mass": 1, # kg

		# the distance in which the particle can move, as measured from the initial_position
		"movement_radius": 1,
	}
	def __init__(self, point=ORIGIN, **kwargs):
		self.initial_position = point
		super().__init__(point, **kwargs)

	def __repr__(self):
		v = np.around(self.v, 3)
		return f"<Particle, v={v}, m={self.mass} at 0x{hex(id(self))}>"

	# shortcuts for ease of use
	@property
	def v(self):
		try: # assuming velocity is a vector
			return get_norm(self.velocity)
		except: # else, it is a scalar
			return self.velocity
	@v.setter
	def v(self, v):
		try:
			self.velocity *= v / get_norm(self.velocity)
		except:
			self.velocity = v

	@property
	def m(self):
		return self.mass
	@m.setter
	def m(self, m):
		self.mass = m

	#
	# special relativity
	#
	@property
	def beta(self):
		return self.v / SPEED_OF_LIGHT
	@beta.setter
	def beta(self, beta):
		if abs(beta) > 1:
			print("[!] warning - setting beta larger than 1 - faster than the speed of light")
		self.v = beta * SPEED_OF_LIGHT

	@property
	def gamma(self):
		return 1 / np.sqrt(1 - self.beta**2)
	@gamma.setter
	def gamma(self, gamma):
		self.beta = np.sqrt(1 - gamma**(-2))


	def get_kinetic_energy_classical(self):
		return 0.5 * self.m * self.v**2
	def get_kinetic_energy_relativistic(self):
		return (self.gamma - 1) * self.m * SPEED_OF_LIGHT**2


	def get_force(self):
		raise NotImplemented()

	@property
	def F(self):
		return get_norm(self.get_force())

	@property
	def Temperature(self):
		return self.m * self.v**2 / 3
	@Temperature.setter
	def Temperature(self, Temperature):
		self.v = np.sign(self.v) * np.sqrt(3*Temperature/self.m)
	# shortcut
	T = Temperature


	def colide_classical(self, other, edit=True):
		m1 = self.m
		m2 = other.m
		v1 = self.v
		v2 = other.v

		v1_new = v1 * (m1-m2)/(m1+m2) + v2 * (2*m2) / (m1+m2)
		v2_new = v1 * (2*m1)/(m1+m2) + v2 * (m2-m1) / (m1+m2)

		if edit:
			self.v = v1_new
			other.v = v2_new

		return v1_new, v2_new

	def colide_quantum(self, other, edit=True):
		raise NotImplemented()

	# updaters
	def random_walk(self, dt):
		raise NotImplemented()

	def walk_by_force(self, dt):
		"""
		increase velocity as if acceleration is constant
		increase position as if velocity     is constant

		non relative version! F=m*dv/dt
		"""
		dv = dt * self.get_force() / self.m
		self.velocity += dv

		dx = dt * self.velocity
		self.shift(dx)


class Particle1D(Particle):
	CONFIG = {
		# todo:
		# 	instead of choosing x/y, allow to choose an angle
		"axis": 0, # x
	}
	def __init__(self, point=ORIGIN, **kwargs):
		super().__init__(point=point, **kwargs)

	def _move_toward_new_location(self, allowed_movement):
		if get_norm(self.get_center() - self.initial_position) == self.movement_radius:
			direction = (-1) * (self.get_center()[self.axis] - self.initial_position[self.axis]) / self.movement_radius
		else:
			direction = random.choice((1, -1))

		current_position = self.get_center()[self.axis]
		new_location = current_position + direction*allowed_movement
		new_distance_from_center = abs(new_location - self.initial_position[self.axis])

		if new_distance_from_center <= self.movement_radius:
			shift_direction = np.array((0.,0.,0.))
			shift_direction[self.axis] += direction*allowed_movement
			self.shift(shift_direction)
			return 0
		else:
			move_direction = self.initial_position.copy()
			move_direction[self.axis] += direction*self.movement_radius
			move_distance = get_norm(self.get_center() - move_direction)
			self.move_to(move_direction)
			return allowed_movement - move_distance

	def random_walk(self, dt):
		allowed_movement = self.velocity * dt
		while allowed_movement:
			allowed_movement = self._move_toward_new_location(allowed_movement)

	def back_and_forth(self, dt):
		# import pdb; pdb.set_trace()
		allowed_movement = abs(self.velocity) * dt

		axis = np.array((0., 0., 0.))
		axis[self.axis] = 1

		initial_position = self.initial_position[self.axis]

		while allowed_movement:
			current_position = self.get_center()[self.axis]
			if almost_equal(abs(current_position - initial_position), self.movement_radius):
				self.velocity *= -1

			movement_radius_edge = initial_position + self.movement_radius * np.sign(self.velocity)
			length = abs(movement_radius_edge - current_position)

			if length > allowed_movement:
				fraction_of_movement = allowed_movement / length
				direction = axis.copy() * (movement_radius_edge - current_position)
				self.shift(direction * fraction_of_movement)
				allowed_movement = 0
			elif almost_equal(length, allowed_movement):
				direction = axis.copy() * (movement_radius_edge - current_position)
				self.shift(direction)
				allowed_movement = 0
			else:
				direction = axis.copy() * (movement_radius_edge - current_position)
				self.shift(direction)
				allowed_movement -= length

	# radius is a mobject used for visual display of the allowed movement, usually used with random_walk
	def create_radius(self):
		movement_radius_vector = np.array((0., 0., 0.))
		movement_radius_vector[self.axis] = self.movement_radius
		self.radius_mobject = Line(
			start = self.initial_position + movement_radius_vector,
			end   = self.initial_position - movement_radius_vector,
		)
		return self.radius_mobject

class Particle2D(Particle):
	CONFIG = {
		"location_list": [], # list of np.array((x,y,0)) to which the particle will move.
		# the list has to be unique, since the movement is stateless
		# thus, the next item is determined by getting the index of the current item
		# the list will be relative to self.initial_position

		# initialize for later use in move_1D
		"_limit_min" : None,
		"_limit_max" : None,
		"_axis"      : 0, # x
	}
	def __init__(self, point=ORIGIN, **kwargs):
		super().__init__(point=point, **kwargs)

		# initialize for later use in random_walk
		self._new_location = None


	# random walk helpers
	def _is_near(self, location, other_location=None):
		if other_location is not None:
			other = np.around(other_location, 3)
		else:
			other = np.around(self.get_center(), 3)
		loc = np.around(location, 3)
		return all(other == loc)

	def _get_next_location(self):
		if self.location_list:
			if self._new_location is None:
				new_index = 0
			elif all(self._new_location == self.initial_position):
				new_index = 0
			else:
				index = 0
				while not self._is_near(self.initial_position+self.location_list[index], self._new_location):
					index += 1
				new_index = (index + 1) % len(self.location_list)

			return self.initial_position + self.location_list[new_index]
		else:
			x, y = polar_to_cartesian(
				r     = np.random.random() * self.movement_radius,
				theta = np.random.random() * TAU,
			)
			return self.initial_position + x*RIGHT + y*UP

	def _get_direction(self):
		if self._new_location is None or self._is_near(self._new_location):
			self._new_location = self._get_next_location()

		return self._new_location - self.get_center()

	def _move_toward_new_location(self, allowed_movement):
		direction = self._get_direction()
		length = get_norm(direction)

		if length >= allowed_movement:
			fraction_of_movement = allowed_movement / length
			self.shift(direction * fraction_of_movement)
			return 0
		else:
			self.move_to(self._new_location)
			return allowed_movement - length
			return np.around(allowed_movement - length, 3)

	def random_walk(self, dt):
		# note: this is not exactly random walk
		# more like a version of random walk which is pretty to the eye
		allowed_movement = self.velocity * dt
		while allowed_movement:
			if allowed_movement < 0:
				raise Exception("allowed_movement was exceeded. aborting.")

			allowed_movement = self._move_toward_new_location(allowed_movement)

	# move_1D helpers
	def _move_toward_new_location_1D(self, allowed_movement):
		direction = np.array((0., 0., 0.))
		direction[self._axis] = 1
		if self.v >= 0:
			possible_movement = self._limit_max - self.get_center()[self._axis]
			limit = self._limit_max
		else:
			direction *= -1
			possible_movement = self.get_center()[self._axis] - self._limit_min
			limit = self._limit_min

		if possible_movement >= allowed_movement:
			self.shift(direction * allowed_movement)
			return 0
		else:
			end_location = self.get_center().copy()
			end_location[self._axis] = limit
			self.move_to(end_location)
			self.v *= -1
			return np.around(allowed_movement - possible_movement, 3)

	# move_1D is implimented in particle2D since Crystal uses 2D particles
	def move_1D(self, dt):
		# I expect self.velocity to have 2 zeros. i.e. motion along only one axis
		allowed_movement = abs(self.v * dt)
		while allowed_movement:
			if allowed_movement < 0:
				raise Exception("allowed_movement was exceeded. aborting.")

			allowed_movement = self._move_toward_new_location_1D(allowed_movement)


	# radius is a mobject used for visual display of the allowed movement, usually used with random_walk
	def create_radius(self):
		self.radius_mobject = Circle(
			arc_center=self.initial_position,
			radius=self.movement_radius
		)
		return self.radius_mobject



# can inherit from Particle2D, but there's no need
class ChargedParticle(Particle):
	CONFIG = {
		"q": 1,
		"E": UP,
		"B": OUT,
	}
	def get_force(self):
		force = self.q * (self.E + np.cross(self.velocity, self.B))
		# there's a bug whenever the force exactly equals 0.5
		# the force arrow will become of size 0, and will raise an exception
		if get_norm(force) == 0.5:
			force *= 1.002
		return force

	def init_force_arrow(self):
		# import pdb; pdb.set_trace()
		c = self.get_center()
		f = self.get_force()
		self.force_arrow = Arrow(
			start=c,
			end=c + f,
		)
		if all(f == 0):
			return
		self.force_arrow.put_start_and_end_on(
			# start=c,
			start=self.force_arrow.start,
			# end=c + f,
			end=self.force_arrow.end,
		)

	def update_force_arrow(self):
		c = self.get_center()
		f = self.get_force()
		if all(f == 0):
			return
		try:
			self.force_arrow.put_start_and_end_on(
				start=c,
				end=c + f,
			)
		except:
			self.force_arrow = Arrow(
				start=c,
				end=c + f,
			)


class Crystal(VGroup):
	CONFIG = {
		"theta": 45*DEGREES,
		"x_min": -10,
		"x_max":  10,
		"y_min": -10,
		"y_max":  10,

		"distance_between_particles": None, # defaults to particle_config.movement_radius


		"particle_config": {
			"movement_radius": 0.5,
		},

		"updater": "random_walk",
		"max_amount_of_particles": None,
	}
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		particles = []
		for point in self._generate_positions():
			p = Particle2D(
				point=point,
				**self.particle_config,
			)
			if self.updater:
				p.add_updater( getattr(p.__class__, self.updater) )
				p.suspend_updating()
			particles.append(p)

			if self.max_amount_of_particles and len(particles) == self.max_amount_of_particles:
				break

		self.particles = VGroup(*particles)
		self.add(self.particles)


	def _generate_positions(self):
		radius = self.distance_between_particles or self.particle_config["movement_radius"]
		# e for effective
		grid_1_x_min = self.x_min + radius
		grid_1_x_max = self.x_max - radius
		grid_1_y_min = self.y_min + radius
		grid_1_y_max = self.y_max - radius

		step_x = 4 * radius * np.cos(self.theta)
		step_y = 4 * radius * np.sin(self.theta)

		for x in np.arange(grid_1_x_min, grid_1_x_max+step_x, step_x):
			for y in np.arange(grid_1_y_min, grid_1_y_max+step_y, step_y):
				if y > grid_1_y_max or x > grid_1_x_max:
					continue
				yield np.array((x, y, 0.))


		grid_2_x_min = grid_1_x_min + 0.5 * step_x
		grid_2_x_max = grid_1_x_max
		grid_2_y_min = grid_1_y_min + 0.5 * step_y
		grid_2_y_max = grid_1_y_max

		for x in np.arange(grid_2_x_min, grid_2_x_max+step_x, step_x):
			for y in np.arange(grid_2_y_min, grid_2_y_max+step_y, step_y):
				if y > grid_2_y_max or x > grid_2_x_max:
					continue
				yield np.array((x, y, 0.))

	def get_particles_by_height(self):
		particles = defaultdict(list)
		for p in self.particles:
			height = np.around(p.initial_position[1], 2)
			particles[height].append(p)
		return particles

	def get_random_portion(self, n=0.5):
		indexes = list(range(len(self.particles)))
		res = []

		for _ in range(int(len(self.particles) * n)):
			index = random.randrange(len(indexes))
			res.append(self.particles[indexes[index]])
			del indexes[index]

		return res

	def write_simultaneously(self):
		"""
		usage:
		self.play(*crystal.write_simultaneously())
		"""
		return [Write(p) for p in self.particles]

	def write_radius_simultaneously(self):
		"""
		usage:
		self.play(*crystal.write_radius_simultaneously())
		"""
		return [Write(p.create_radius()) for p in self.particles]



# copy pasted from active_projects/diffyq/part1/pendulum.py
class Pendulum(VGroup):
	CONFIG = {
		"length": 3,
		"gravity": 9.8,
		"weight_diameter": 0.5,
		"initial_theta": 0.3,
		"omega": 0,
		"damping": 0.1,
		"top_point": 2 * UP,
		"rod_style": {
			"stroke_width": 3,
			"stroke_color": LIGHT_GREY,
			"sheen_direction": UP,
			"sheen_factor": 1,
		},
		"weight_style": {
			"stroke_width": 0,
			"fill_opacity": 1,
			"fill_color": GREY_BROWN,
			"sheen_direction": UL,
			"sheen_factor": 0.5,
			"background_stroke_color": BLACK,
			"background_stroke_width": 3,
			"background_stroke_opacity": 0.5,
		},
		"dashed_line_config": {
			"num_dashes": 25,
			"stroke_color": WHITE,
			"stroke_width": 2,
		},
		"angle_arc_config": {
			"radius": 1,
			"stroke_color": WHITE,
			"stroke_width": 2,
		},
		"velocity_vector_config": {
			"color": RED,
		},
		"theta_label_height": 0.25,
		"set_theta_label_height_cap": False,
		"n_steps_per_frame": 100,
		"include_theta_label": True,
		"include_velocity_vector": False,
		"velocity_vector_multiple": 0.5,
		"max_velocity_vector_length_to_length_ratio": 0.5,
	}

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.create_fixed_point()
		self.create_rod()
		self.create_weight()
		self.rotating_group = VGroup(self.rod, self.weight)
		self.create_dashed_line()
		self.create_angle_arc()
		if self.include_theta_label:
			self.add_theta_label()
		if self.include_velocity_vector:
			self.add_velocity_vector()

		self.set_theta(self.initial_theta)
		self.update()

	def create_fixed_point(self):
		self.fixed_point_tracker = VectorizedPoint(self.top_point)
		self.add(self.fixed_point_tracker)
		return self

	def create_rod(self):
		rod = self.rod = Line(UP, DOWN)
		rod.set_height(self.length)
		rod.set_style(**self.rod_style)
		rod.move_to(self.get_fixed_point(), UP)
		self.add(rod)

	def create_weight(self):
		weight = self.weight = Circle()
		weight.set_width(self.weight_diameter)
		weight.set_style(**self.weight_style)
		weight.move_to(self.rod.get_end())
		self.add(weight)

	def create_dashed_line(self):
		line = self.dashed_line = DashedLine(
			self.get_fixed_point(),
			self.get_fixed_point() + self.length * DOWN,
			**self.dashed_line_config
		)
		line.add_updater(
			lambda l: l.move_to(self.get_fixed_point(), UP)
		)
		self.add_to_back(line)

	def create_angle_arc(self):
		self.angle_arc = always_redraw(lambda: Arc(
			arc_center=self.get_fixed_point(),
			start_angle=-90 * DEGREES,
			angle=self.get_arc_angle_theta(),
			**self.angle_arc_config,
		))
		self.add(self.angle_arc)

	def get_arc_angle_theta(self):
		# Might be changed in certain scenes
		return self.get_theta()

	def add_velocity_vector(self):
		def make_vector():
			omega = self.get_omega()
			theta = self.get_theta()
			mvlr = self.max_velocity_vector_length_to_length_ratio
			max_len = mvlr * self.rod.get_length()
			vvm = self.velocity_vector_multiple
			multiple = np.clip(
				vvm * omega, -max_len, max_len
			)
			vector = Vector(
				multiple * RIGHT,
				**self.velocity_vector_config,
			)
			vector.rotate(theta, about_point=ORIGIN)
			vector.shift(self.rod.get_end())
			return vector

		self.velocity_vector = always_redraw(make_vector)
		self.add(self.velocity_vector)
		return self

	def add_theta_label(self):
		self.theta_label = always_redraw(self.get_label)
		self.add(self.theta_label)

	def get_label(self):
		label = TexMobject("\\theta")
		label.set_height(self.theta_label_height)
		if self.set_theta_label_height_cap:
			max_height = self.angle_arc.get_width()
			if label.get_height() > max_height:
				label.set_height(max_height)
		top = self.get_fixed_point()
		arc_center = self.angle_arc.point_from_proportion(0.5)
		vect = arc_center - top
		norm = get_norm(vect)
		vect = normalize(vect) * (norm + self.theta_label_height)
		label.move_to(top + vect)
		return label

	#
	def get_theta(self):
		theta = self.rod.get_angle() - self.dashed_line.get_angle()
		theta = (theta + PI) % TAU - PI
		return theta

	def set_theta(self, theta):
		self.rotating_group.rotate(
			theta - self.get_theta()
		)
		self.rotating_group.shift(
			self.get_fixed_point() - self.rod.get_start(),
		)
		return self

	def get_omega(self):
		return self.omega

	def set_omega(self, omega):
		self.omega = omega
		return self

	def get_fixed_point(self):
		return self.fixed_point_tracker.get_location()

	#
	def start_swinging(self):
		self.add_updater(Pendulum.update_by_gravity)

	def end_swinging(self):
		self.remove_updater(Pendulum.update_by_gravity)

	def update_by_gravity(self, dt):
		theta = self.get_theta()
		omega = self.get_omega()
		nspf = self.n_steps_per_frame
		for x in range(nspf):
			d_theta = omega * dt / nspf
			d_omega = op.add(
				-self.damping * omega,
				-(self.gravity / self.length) * np.sin(theta),
			) * dt / nspf
			theta += d_theta
			omega += d_omega
		self.set_theta(theta)
		self.set_omega(omega)
		return self

class DoublePendulum(VGroup):
	CONFIG = {
		"top_point": 2*UP,
		"L1": 2,
		"L2": 2,
		"m1": 1,
		"m2": 1,
		"initial_theta1": np.float128(45*DEGREES),
		"initial_theta2": np.float128(90*DEGREES),
		"initial_omega1": np.float128(0),
		"initial_omega2": np.float128(0),
		"gravity": 9.8,
		"weight_diameter": 0.5,

		"rod_style": {
			"stroke_width": 3,
			"stroke_color": LIGHT_GREY,
			"sheen_direction": UP,
			"sheen_factor": 1,
		},
		"weight_style": {
			"stroke_width": 0,
			"fill_opacity": 1,
			"fill_color": GREY_BROWN,
			"sheen_direction": UL,
			"sheen_factor": 0.5,
			"background_stroke_color": BLACK,
			"background_stroke_width": 3,
			"background_stroke_opacity": 0.5,
		},
		"weight1_color": RED,
		"weight2_color": BLUE,
		"dashed_line_config": {
			"num_dashes": 25,
			"stroke_color": WHITE,
			"stroke_width": 2,
		},
		"angle_arc_config": {
			"radius": 1,
			"stroke_color": WHITE,
			"stroke_width": 2,
		},
		"include_theta_label": False,
		"include_velocity_vector": False,
		"n_steps_per_frame": 100,
		"add_1st_trajectory": False,
		"add_2nd_trajectory": False,
	}
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.initialize()

		if self.include_theta_label:
			# self.add_theta_label()
			pass
		if self.include_velocity_vector:
			# self.add_velocity_vector()
			pass

		self.set_initial_values()

	def initialize(self):
		self.create_fixed_point()
		self.create_rod1()
		self.create_weight1()
		self.create_rod2()
		self.create_weight2()
		self.rotating_group1 = VGroup(self.rod1, self.weight1)
		self.rotating_group2 = VGroup(self.rod2, self.weight2)
		self.create_dashed_line1()
		self.create_dashed_line2()
		self.create_angle_arc1()
		self.create_angle_arc2()

	def set_initial_values(self):
		self.set_theta1(self.initial_theta1)
		self.set_theta2(self.initial_theta2)
		self.set_omega1(self.initial_omega1)
		self.set_omega2(self.initial_omega2)

	def create_fixed_point(self):
		self.fixed_point_tracker = VectorizedPoint(self.top_point)
		self.add(self.fixed_point_tracker)
		return self
	def get_fixed_point(self):
		return self.fixed_point_tracker.get_location()
	def get_pivot_point(self):
		# all these 3 are equivalent
		return self.rod1.get_end()
		return self.weight1.get_center()
		return self.rod2.get_start()

	def _create_rod(self, length, top_point):
		rod = Line(UP, DOWN)
		rod.set_height(length)
		rod.set_style(**self.rod_style)
		rod.move_to(top_point, aligned_edge=UP)
		self.add(rod)
		return rod
	def create_rod1(self):
		self.rod1 = self._create_rod(self.L1, self.get_fixed_point())
	def create_rod2(self):
		self.rod2 = self._create_rod(self.L2, self.get_pivot_point())

	def _create_weight(self, center):
		weight = Circle()
		weight.set_width(self.weight_diameter)
		weight.set_style(**self.weight_style)
		weight.move_to(center)
		self.add(weight)
		return weight
	def create_weight1(self):
		self.weight1 = self._create_weight(self.rod1.get_end())
		self.weight1.set_color(self.weight1_color)
	def create_weight2(self):
		self.weight2 = self._create_weight(self.rod2.get_end())
		self.weight2.set_color(self.weight2_color)

	def create_dashed_line1(self):
		self.dashed_line1 = line = DashedLine(
			self.get_fixed_point(),
			self.get_fixed_point() + self.L1 * DOWN,
			**self.dashed_line_config
		)
		line.add_updater(
			lambda l: l.move_to(self.get_fixed_point(), aligned_edge=UP)
		)
		self.add_to_back(line)
	def create_dashed_line2(self):
		self.dashed_line2 = line = DashedLine(
			self.get_pivot_point(),
			self.get_pivot_point() + self.L2 * DOWN,
			**self.dashed_line_config
		)
		line.add_updater(
			lambda l: l.move_to(self.get_pivot_point(), aligned_edge=UP)
		)
		self.add_to_back(line)

	def create_angle_arc1(self):
		self.angle_arc1 = always_redraw(lambda: Arc(
			arc_center=self.get_fixed_point(),
			start_angle=-90 * DEGREES,
			angle=self.get_theta1(),
			**self.angle_arc_config,
		))
		self.add(self.angle_arc1)
	def create_angle_arc2(self):
		self.angle_arc2 = always_redraw(lambda: Arc(
			arc_center=self.get_pivot_point(),
			start_angle=-90 * DEGREES,
			angle=self.get_theta2(),
			**self.angle_arc_config,
		))
		self.add(self.angle_arc2)

	#
	def _get_theta(self, rod, dashed_line):
		theta = rod.get_angle() - dashed_line.get_angle()
		theta = (theta + PI) % TAU - PI
		return theta
	def get_theta1(self):
		return self._get_theta(self.rod1, self.dashed_line1)
	def get_theta2(self):
		return self._get_theta(self.rod2, self.dashed_line2)

	def set_theta1(self, theta):
		self.rotating_group1.rotate(
			theta - self.get_theta1()
		)
		self.rotating_group1.shift(
			self.get_fixed_point() - self.rod1.get_start(),
		)
		return self
	def set_theta2(self, theta):
		self.rotating_group2.rotate(
			theta - self.get_theta2()
		)
		self.rotating_group2.shift(
			self.get_pivot_point() - self.rod2.get_start(),
		)
		return self

	def get_omega1(self):
		return self.omega1
	def get_omega2(self):
		return self.omega2
	def set_omega1(self, omega):
		self.omega1 = omega
		return self
	def set_omega2(self, omega):
		self.omega2 = omega
		return self

	#
	def get_energy_detailed(self):
		h1 = (1 - np.cos(self.get_theta1())) * self.L1
		h2 = (1 - np.cos(self.get_theta2())) * self.L2
		U_1 = self.m1 * self.gravity * h1
		U_2 = self.m2 * self.gravity * h2

		I_1 = self.m1 * self.L1**2
		I_2 = self.m2 * self.L2**2
		E_k_1 = 0.5 * I_1 * self.get_omega1()**2
		E_k_2 = 0.5 * I_2 * self.get_omega2()**2

		return {"U1": U_1, "U2": U_2, "EK1": E_k_1, "EK2": E_k_2}
	def get_energy(self):
		return sum(self.get_energy_detailed().values())
	def display_energy(self):
		e = self.get_energy_detailed()
		E = self.get_energy()
		h1 = (1 - np.cos(self.get_theta1())) * self.L1
		h2 = (1 - np.cos(self.get_theta2())) * self.L2
		print(f"E={E:6.3f} U1={e['U1']:6.3f} U2={e['U2']:6.3f} EK1={e['EK1']:6.3f} EK2={e['EK2']:6.3f} h1={h1:6.3f} h2={h2:6.3f}")

	#
	def add_trajectory(self, weight, color=None):
		def update_trajectory(traj, dt):
			new_point = traj.weight.get_center()
			if get_norm(new_point - traj.points[-1]) > 0.01:
				traj.add_smooth_curve_to(new_point)

		traj = VMobject()
		traj.set_color(color or weight.get_color())
		traj.weight = weight
		# traj.start_new_path(p.point)
		traj.start_new_path(weight.get_center())
		traj.set_stroke(weight.get_color(), 1, opacity=0.75)
		traj.add_updater(update_trajectory)
		self.add(traj, weight)
		return traj

	#
	def start_swinging(self):
		self.add_updater(DoublePendulum.update_by_gravity)

		if self.add_1st_trajectory:
			self.traj1 = self.add_trajectory(self.weight1)
		if self.add_2nd_trajectory:
			self.traj2 = self.add_trajectory(self.weight2)

	def end_swinging(self):
		self.remove_updater(DoublePendulum.update_by_gravity)

		if self.add_1st_trajectory:
			for u in self.traj1.get_updaters():
				self.traj1.remove_updater(u)
		if self.add_2nd_trajectory:
			for u in self.traj2.get_updaters():
				self.traj2.remove_updater(u)


	def update_by_gravity(self, dt):
		m1    , m2     = self.m1          , self.m2
		L1    , L2     = self.L1          , self.L2
		theta1, theta2 = self.get_theta1(), self.get_theta2()
		omega1, omega2 = self.get_omega1(), self.get_omega2()
		sin   , cos    = np.sin           , np.cos
		g              = self.gravity

		M = m1+m2
		delta_theta = theta1 - theta2

		n = self.n_steps_per_frame
		d_dt = dt / n

		# http://scienceworld.wolfram.com/physics/DoublePendulum.html
		for _ in range(n):
			omega_2_dot = (
				(
					(m2**2 / M) * L2 * omega2**2 * sin(delta_theta) * cos(delta_theta)
					 +
					m2 * g * sin(theta1) * cos(delta_theta)
					 +
					m2 * L1 * omega1**2 * sin(delta_theta)
					 -
					m2 * g * sin(theta2)
				)
				 /
				(
					m2*L2
					 -
					(m2**2 / M) * L2 * cos(delta_theta)**2
				)
			)

			omega_1_dot = -(
				(
					m2 * L2 * omega_2_dot * cos(delta_theta)
					 +
					m2 * L2 * omega2**2 * sin(delta_theta)
					 +
					g * M * sin(theta1)
				)
				 /
				(M * L1)
			)

			theta1 += omega1 * d_dt
			theta2 += omega2 * d_dt
			omega1 += omega_1_dot * d_dt
			omega2 += omega_2_dot * d_dt
		self.set_theta1(theta1)
		self.set_theta2(theta2)
		self.set_omega1(omega1)
		self.set_omega2(omega2)

