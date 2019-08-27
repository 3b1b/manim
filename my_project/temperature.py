from big_ol_pile_of_manim_imports import *
import numbers

OUTPUT_DIRECTORY = "temperature"

k_B = 1.38064852e-23
k_B_tex = TexMobject("1.38064852\\times10^{-23} \\frac{m^2 kg}{s^2 K}")

internal_energy_of_all_particles = TexMobject("U=\\frac{3}{2}N k_B T")
energy_of_a_single_particle = TexMobject("E=\\frac{U}{N}")
energy_of_a_single_particle_2 = TexMobject("E=\\frac{3}{2} k_B T")
kinetic_energy = TexMobject("E_k=\\frac{1}{2} m v^2")
velocity_of_particle = TexMobject("\\frac{1}{2} m v^2 = \\frac{3}{2} k_B T")
velocity_of_particle_extracted = TexMobject("v = \\sqrt{\\frac{3 k_B T}{m}}")
velocity_of_particle_extracted_as_func_of_T = TexMobject("v = \\sqrt{\\frac{3 k_B}{m}}\\cdot\\sqrt{T}")


def color(hot=0):
	cold_color = [0x58, 0xC4, 0xDD]
	hot_color = [0xff, 0x00, 0x00]
	if not (MIN_HOT <= hot <= MAX_HOT):
		print("please enter a value between 0 and 100")
		return False
	
	color = []
	for i in range(len(cold_color)):
		color.append(
			cold_color[i]
			+
			(hot_color[i] - cold_color[i]) * hot / 100
		)
	return '#' + ''.join("%02X"%int(i) for i in color)
MAX_HOT = MIN_COLD = 100
MIN_HOT = MAX_COLD = 0

class Dot(Circle):
    CONFIG = {
        "radius": DEFAULT_DOT_RADIUS,
        "stroke_width": 0,
        "fill_opacity": 1.0,
        "color": WHITE
    }

    def __init__(self, point=ORIGIN, **kwargs):
        Circle.__init__(self, arc_center=point, **kwargs)

class Particle(Dot):
	def __init__(self, point=ORIGIN, velocity=1, mass=1, allowed_movement=1, **kwargs):
		self.velocity = velocity
		self.mass = mass
		self.allowed_movement = allowed_movement
		self.initial_position = point
		super().__init__(point, **kwargs)

	def __repr__(self):
		return f"Particle, v={self.velocity}, m={self.mass}"

	def colide(self, other):
		m1 = self.mass
		m2 = other.mass
		v1 = self.velocity
		v2 = other.velocity

		v1_new = v1 * (m1-m2)/(m1+m2) + v2 * (2*m2) / (m1+m2)
		v2_new = v1 * (2*m1)/(m1+m2) + v2 * (m2-m1) / (m1+m2)
		return v1_new, v2_new

	def update_position(self, dt):
		if abs(self.get_center()[0] - self.initial_position[0]) >= self.allowed_movement:
			self.velocity *= -1
		self.shift(self.velocity * dt * RIGHT)

class IntroduceTemperature(Scene):
	CONFIG = {
		"material_A": {
			# initial parameters
			"dots_location": (2*LEFT + i*UP for i in range(-2,3)),
			"color": color(MAX_HOT),
			"velocity": 10,
			"mass": 3,

		},
		"material_B": {
			# initial parameters
			"dots_location": (2*RIGHT + i*UP for i in range(-2,3)),
			"color": color(MAX_COLD),
			"velocity": 1,
			"mass": 3,

		},
		# how far from the original position does the particle move
		"travel_radius": 1
		
	}

	def construct(self):
		hot_matter  = []
		for location in self.material_A["dots_location"]:
			p = Particle(location, self.material_A["velocity"], self.material_A["mass"])
			p.set_color(self.material_A["color"])
			p.add_updater(p.__class__.update_position)
			hot_matter.append(p)

		cold_matter  = []
		for location in self.material_B["dots_location"]:
			p = Particle(location, self.material_B["velocity"], self.material_B["mass"])
			p.set_color(self.material_B["color"])
			p.add_updater(p.__class__.update_position)
			cold_matter.append(p)

		self.min_velocity = min(self.material_A["velocity"], self.material_B["velocity"])
		self.max_velocity = max(self.material_A["velocity"], self.material_B["velocity"])

		self.add(*hot_matter, *cold_matter)
		self.wait(8)



class Playground(Scene):
	CONFIG = {
		"color_hot": RED_A,
		"color_cold": BLUE_A,
	}
	def construct(self):
		hot_matter  = [Dot(i)  for i in range(-2,3)]
		# list(map(lambda d:d.set_color(self.color_hot), hot_matter))
		hot_matter[0].set_color(color(100))
		hot_matter[1].set_color(color(100 - 10))
		hot_matter[2].set_color(color(100 - 20))
		hot_matter[3].set_color(color(100 - 30))
		hot_matter[4].set_color(color(100 - 40))

		cold_matter = [Dot(i*UP + 2*RIGHT) for i in range(-2,3)]
		# list(map(lambda d:d.set_color(self.color_cold), cold_matter))
		cold_matter[0].set_color(color(0))
		cold_matter[1].set_color(color(0 + 10))
		cold_matter[2].set_color(color(0 + 20))
		cold_matter[3].set_color(color(0 + 30))
		cold_matter[4].set_color(color(0 + 40))
		self.add(*hot_matter, *cold_matter)
		self.wait(3)
