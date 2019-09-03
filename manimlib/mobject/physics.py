import numpy as np
import random

from manimlib.constants import *
from manimlib.mobject.geometry import Dot, Line, Circle
from manimlib.utils.space_ops import get_norm
from manimlib.mobject.svg.tex_mobject import TexMobject


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
		"velocity": 1, # m/s
		"mass": 1, # kg
		
		"movement_radius": 1,
	}
	def __init__(self, point=ORIGIN, **kwargs):
		self.initial_position = point
		super().__init__(point, **kwargs)

	def __repr__(self):
		return f"Particle, v={self.velocity}, m={self.mass}"

	# shortcuts for ease of use
	@property
	def v(self):
		return self.velocity
	@v.setter
	def v(self, v):
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
	

	def colide_classical(self, other, edit=True):
		m1 = self.m
		m2 = other.m
		v1 = self.v
		v2 = other.v

		v1_new = v1 * (m1-m2)/(m1+m2) + v2 * (2*m2) / (m1+m2)
		v2_new = v1 * (2*m1)/(m1+m2) + v2 * (m2-m1) / (m1+m2)

		if edit:
			self.velocity = v1_new
			other.velocity = v2_new

		return v1_new, v2_new

	def colide_quantom(self, other, edit=True):
		pass

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
		return Line(
			start = self.initial_position + movement_radius_vector,
			end   = self.initial_position - movement_radius_vector,
		)

class Particle2D(Particle):
	CONFIG = {
		"location_list": [], # list of np.array((x,y,0)) to which the particle will move.
		# the list has to be unique, since the movement is stateless
		# thus, the next item is determined by getting the index of the current item
		# the list will be relative to self.initial_position
	}
	def __init__(self, point=ORIGIN, **kwargs):
		super().__init__(point=point, **kwargs)

		# initialize for later use
		self.new_location = None
	
	def _is_near(self, location, other_location=None):
		if other_location is not None:
			other = np.around(other_location, 3)
		else:
			other = np.around(self.get_center(), 3)
		loc = np.around(location, 3)
		return all(other == loc)

	def _get_next_location(self):
		if self.location_list:
			if self.new_location is None:
				new_index = 0
			elif all(self.new_location == self.initial_position):
				new_index = 0
			else:
				index = 0
				while not self._is_near(self.initial_position+self.location_list[index], self.new_location):
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
		if self.new_location is None or self._is_near(self.new_location):
			self.new_location = self._get_next_location()

		return self.new_location - self.get_center()

	def _move_toward_new_location(self, allowed_movement):
		direction = self._get_direction()
		length = get_norm(direction)

		if length >= allowed_movement:
			fraction_of_movement = allowed_movement / length
			self.shift(direction * fraction_of_movement)
			return 0
		else:
			self.move_to(self.new_location)
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

	def create_radius(self):
		return Circle(
			arc_center=self.initial_position,
			radius=self.movement_radius
		)
