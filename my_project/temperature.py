from big_ol_pile_of_manim_imports import *

OUTPUT_DIRECTORY = "temperature"

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

class TestParticles(Scene):
	def construct(self):
		self.wait(0.2)
		p1D = self.add_particle(Particle1D(
			point=ORIGIN,
			velocity=1,
			movement_radius=0.5,
			axis=1,
		).set_color(YELLOW))
		self.wait(8)
		return

		p2D = self.add_particle(Particle2D(
			point=2.5*UP,
			velocity=3,
			movement_radius=0.3,
		).set_color(RED))
		self.wait(8)

	def add_particle(self, p, write=False):
		radius = p.create_radius()
		self.add(radius, p)
		if write:
			self.play(Write(p))
		p.add_updater(p.__class__.back_and_forth)
		return p

class IntroduceTemperature(Scene):
	CONFIG = {
		"material_A": {
			# initial parameters
			"dots_location": (2*LEFT + i*UP for i in range(-2,3)),
			"color": color(MAX_HOT),
			"velocity": 1,
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
		"travel_radius": 0.2,
		
	}

	def construct(self):
		self.add_plane(1)

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


	def add_plane(self, animate=False, **kwargs):
		plane = NumberPlane(**kwargs)
		if animate:
			self.play(ShowCreation(plane, lag_ratio=0.5))
		self.add(plane)
		return plane

	def update_position(self, dt):
		pass

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
