import numpy as np
import random
from collections import defaultdict

from manimlib.constants import *
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.geometry import Dot, Line, Circle, Arrow
from manimlib.utils.space_ops import get_norm
from manimlib.mobject.svg.tex_mobject import TexMobject
from manimlib.animation.creation import Write


k_B = 1.38064852e-23
k_B_tex = TexMobject("1.38064852\\times10^{-23} \\frac{m^2 kg}{s^2 K}")

SPEED_OF_LIGHT = 299_792_458 # m/s
SPEED_OF_LIGHT_tex = TexMobject("3\\times10^8 \\frac{m}{s}")

def polar_to_cartesian(r, theta):
	return r*np.cos(theta), r*np.sin(theta)
def cartesian_to_polar(x, y):
	return np.sqrt(x**2 + y**2), np.arctan(y/x)

def almost_equal(x, y):
	return abs(x-y) < 0.01
def almost_same_point(a, b):
	return all(np.around(a, 3) == np.around(b, 3))

class Particle(Dot):
	CONFIG = {
		"velocity": RIGHT, # m/s
		"mass": 1, # kg
		
		"movement_radius": 1,
	}
	def __init__(self, point=ORIGIN, **kwargs):
		self.initial_position = point
		super().__init__(point, **kwargs)

	def __repr__(self):
		return f"Particle, v={self.v}, m={self.mass}"

	# shortcuts for ease of use
	@property
	def v(self):
		try:
			return get_norm(self.velocity)
		except:
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


	def energy_classical(self):
		return 0.5 * self.m * self.v**2
	def energy_relativistic(self):
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

	def colide_quantom(self, other, edit=True):
		pass

	# updaters
	def random_walk(self, dt):
		raise NotImplemented()

	# non relative vertion! F=m*dv/dt
	def walk_by_force(self, dt):
		"""
		increase velocity as if acceleration is constant
		increase position as if velocity     is constant
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

	def move_1D(self, dt):
		# I expect self.velocity to have 2 zeros. i.e. motion along only one axis
		allowed_movement = abs(self.v * dt)
		while allowed_movement:
			if allowed_movement < 0:
				raise Exception("allowed_movement was exceeded. aborting.")

			allowed_movement = self._move_toward_new_location_1D(allowed_movement)


	def create_radius(self):
		self.radius_mobject = Circle(
			arc_center=self.initial_position,
			radius=self.movement_radius
		)
		return self.radius_mobject



# can ingerit from Particle2D, but there's no need
class ChargedParticle(Particle):
	CONFIG = {
		"q": 1,
		"E": UP,
		"B": np.array((0., 0., 1)),
	}
	def get_force(self):
		# import pdb; pdb.set_trace()
		force = self.q * (self.E + np.cross(self.velocity, self.B))
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
			# import pdb; pdb.set_trace()
			self.force_arrow = Arrow(
				start=c,
				end=c + f,
			)
		# print(f"force={self.get_force()} ; F={self.F} ; v={self.v}")
		# print(f"vB={np.cross(self.velocity, self.B)} ; start={self.force_arrow.get_start()} ; end={self.force_arrow.get_end()}")


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
	}
	def __init__(self, updater="random_walk", **kwargs):
		super().__init__(**kwargs)
		
		particles = []
		for point in self._generate_positions():
			p = Particle2D(
				point=point,
				**self.particle_config,
			)
			if updater:
				p.add_updater( getattr(p.__class__, updater) )
				p.suspend_updating()
			particles.append(p)

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
	