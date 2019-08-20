from big_ol_pile_of_manim_imports import *

OUTPUT_DIRECTORY = "magnetic_force"

def gamma_to_beta(gamma):
	return math.sqrt(1 - gamma**(-2))
def beta_to_gamma(beta):
	return 1 / math.sqrt(1 - beta**2)
def add_beta(b1, b2):
	return (b1+b2) / (1 + b1*b2)

class ReferenceFrame(Scene):
	CONFIG = {
		"protons_lambda_0"  : 0.25,
		"electrons_lambda_0": 0.5,
		"electrons_gamma_0": 2,
		# thus, lambda_electrons at the proton's rest frame is the same as protons_lambda_0

		"proton_color"  : RED,
		"electron_color": BLUE,

		"proton_height"  : 1.1 * UP,
		"electron_height": 0.9 * UP,

		"min_x_value": -15,
		"max_x_value": 15,

		"reference_frame_gamma": 1,
		"charge_gamma"         : 1.5,
		"charge_direction"     : RIGHT,
		"display_force" : False,

		"title" : TextMobject("Protons' Rest Frame"),

		"wait_time": 1,
		"end_wait_time": 5,
		"intro_run_time": DEFAULT_ANIMATION_RUN_TIME,
		"run_time": 5,
		"dt": 0.1,
	}

	def construct(self):
		self.init_values()
		self.show_particles()
		self.wait(self.wait_time)
		self.play(
			Write(self.velocity_proton_tex),
			Write(self.velocity_electron_tex),
			Write(self.velocity_charge_tex),
			Write(self.charge_per_metre),
			Write(self.title),
			run_time=self.intro_run_time
		)
		self.wait(self.wait_time)

		self.animate_particles()
		self.wait(self.end_wait_time)

	def init_values(self):
		if all(self.charge_direction == RIGHT):
			self.reference_frame_beta = beta = gamma_to_beta(self.reference_frame_gamma)
		else:
			self.reference_frame_beta = beta = -gamma_to_beta(self.reference_frame_gamma)

		self.protons_beta = add_beta(0, -beta)
		self.protons_gamma = beta_to_gamma(self.protons_beta)
		self.protons_lambda = self.protons_lambda_0 / self.protons_gamma

		self.electrons_beta = add_beta(gamma_to_beta(self.electrons_gamma_0), -beta)
		self.electrons_gamma = beta_to_gamma(self.electrons_beta)
		self.electrons_lambda = self.electrons_lambda_0 / self.electrons_gamma

		self.velocity_proton_tex   = TexMobject(f"\\beta_{{proton}}={self.protons_beta:.2f}")
		self.velocity_electron_tex = TexMobject(f"\\beta_{{electron}}={self.electrons_beta:.2f}")
		self.velocity_proton_tex.to_corner(DOWN+LEFT)
		self.velocity_electron_tex.to_corner(DOWN+RIGHT)

		self.charge_beta = gamma_to_beta(self.charge_gamma)
		self.velocity_charge_tex = TexMobject(f"\\beta_{{charge}}={self.charge_beta:.2f}")
		self.velocity_charge_tex.to_corner(DOWN * 0.5)

		self.total_charge = 1/self.protons_lambda - 1/self.electrons_lambda
		self.charge_per_metre = TexMobject(f"total \\enspace charge=({1/self.protons_lambda:.2f})^+"
			f" + ({1/self.electrons_lambda:.2f})^- = "
			f"{self.total_charge:.2f}"
		)
		self.charge_per_metre.move_to(2 * UP)

		self.title.to_corner(UP)

	def show_particles(self):
		self.show_protons()
		self.show_electrons()

		self.charge = Dot(1*DOWN)
		self.charge.set_color(self.electron_color)
		self.add(self.charge)

		if self.display_force:
			if "force_strength" in self.CONFIG:
				self.force_strength_initial = self.force_strength
			else:
				self.force_strength_initial = self.total_charge

			distance = get_norm(
  				1*UP - self.charge.get_y()
			)
			force_strength = self.force_strength_initial / distance**2

			self.force = Arrow(
				self.charge.get_center(),
				self.charge.get_center() + UP * 0.15 * force_strength,
				color=RED,
				buff=4,
			)
			self.play( GrowArrow(self.force) )

	def show_protons(self):
		protons_locations = np.arange(
			self.min_x_value,
			self.max_x_value + self.protons_lambda,
			self.protons_lambda
		)
		self.protons = protons = VGroup(*[
			Dot(location * RIGHT + self.proton_height)
			for location in protons_locations
		])
		protons.set_color(self.proton_color)
		# protons.set_sheen(0.2, UL)
		# protons.arrange(RIGHT, buff=SMALL_BUFF)
		# protons.set_width(FRAME_WIDTH - 1)
		self.add(protons)

	def show_electrons(self):
		electron_locations = np.arange(
			self.min_x_value,
			self.max_x_value + self.electrons_lambda,
			self.electrons_lambda
		)
		self.electrons = electrons = VGroup(*[
			Dot(location * RIGHT + self.electron_height)
			for location in electron_locations
		])
		electrons.set_color(self.electron_color)
		self.add(electrons)

	def animate_particles(self):
		for i in np.arange(0, self.run_time, self.dt):
			self.move_particles(self.dt)
			self.wait(self.dt)

	def move_particles(self, dt):
		for e in self.electrons:
			e.shift(self.electrons_beta * dt * RIGHT)
		for p in self.protons:
			p.shift(self.protons_beta * dt * RIGHT)

		self.charge.shift(self.charge_beta * dt * self.charge_direction)
		if self.display_force:
			distance = get_norm(
  				1*UP - self.charge.get_y()
			)
			force_strength = self.force_strength_initial / distance**2

			new_force = Arrow(
				self.charge.get_center(),
				self.charge.get_center() + UP * 0.5 * force_strength,
				color=RED,
				buff=4,
			)

			self.charge.shift(force_strength * 0.1 * dt * UP)
			self.force.shift(self.charge_beta * dt * self.charge_direction)
			self.play(
				Transform(self.force, new_force),
				run_time=0
			)

class ReferenceFrame_ProtonsRestFrame(ReferenceFrame):
	CONFIG = {
		"reference_frame_gamma": 1,
		"charge_gamma"         : 1.1,
		"title" : TextMobject("Protons' Rest Frame"),
		"run_time": 7,
		"force_strength": 3.87,
	}
class ReferenceFrame_ProtonsRestFrame_WithForce(ReferenceFrame):
	CONFIG = {
		"reference_frame_gamma": 1,
		"charge_gamma"         : 1.1,
		"title" : TextMobject("Protons' Rest Frame"),
		"run_time": 7,
		"force_strength": 3.87,
		"display_force": True,
	}
class ReferenceFrame_ChargeRestFrame(ReferenceFrame):
	CONFIG = {
		"reference_frame_gamma": 1.5,
		"charge_gamma"         : 1,
		"title" : TextMobject("Charge's Rest Frame"),
		"run_time": 7,
	}
class ReferenceFrame_ChargeRestFrame_WithForce(ReferenceFrame_ChargeRestFrame):
	CONFIG = {
		"display_force": True,
	}

class ReferenceFrame_ChargeRestFrame_Appendix_1(ReferenceFrame_ChargeRestFrame_WithForce):
	# faster, nothing special
	CONFIG = {
		"reference_frame_gamma": 1.8,
		"intro_run_time": 0.1,
		"wait_time": 0.2,
	}
class ReferenceFrame_ChargeRestFrame_Appendix_2(ReferenceFrame_ChargeRestFrame_WithForce):
	# same speed as the elctrons
	CONFIG = {
		"reference_frame_gamma": 2,
		"intro_run_time": 0.1,
		"wait_time": 0.2,
	}
class ReferenceFrame_ChargeRestFrame_Appendix_3(ReferenceFrame_ChargeRestFrame_WithForce):
	# faster than the electrons
	CONFIG = {
		"reference_frame_gamma": 2.5,
		"intro_run_time": 0.1,
		"wait_time": 0.2,
	}
class ReferenceFrame_ChargeRestFrame_Appendix_4(ReferenceFrame_ChargeRestFrame_WithForce):
	# oposite direction
	CONFIG = {
		"charge_direction": LEFT,
		"intro_run_time": 0.1,
		"wait_time": 0.2,
	}

class ReferenceFrameTransform(Scene):
	CONFIG = {
		"protons_lambda_0"  : 0.25,
		"electrons_lambda_0": 0.5,
		"electrons_gamma_0": 2,
		# thus, lambda_electrons at the proton's rest frame is the same as protons_lambda_0

		"proton_color"  : RED,
		"electron_color": BLUE,

		"proton_height"  : 1.1 * UP,
		"electron_height": 0.9 * UP,

		"min_x_value": -15,
		"max_x_value": 15,

		"reference_frame_gamma": 1.5,
		"charge_gamma"         : 1,
		"charge_direction"     : RIGHT,
		"display_force" : False,

		"title" : TextMobject("Protons' Rest Frame"),

		"wait_time": 1,
		"end_wait_time": 5,
		"intro_run_time": DEFAULT_ANIMATION_RUN_TIME,
		"run_time": 5,
		"dt": 0.1,
	}

	def construct(self):
		self.init_values()

		self.show_charge()
		self.show_protons()
		# self.show_electrons()

		self.wait(self.wait_time)

		self.transform_protons()
		# self.transform_electrons()

		self.wait(self.end_wait_time)

	def init_values(self):
		beta = 0

		self.protons_rest_beta = add_beta(0, -beta)
		self.protons_rest_gamma = beta_to_gamma(self.protons_rest_beta)
		self.protons_rest_lambda = self.protons_lambda_0 / self.protons_rest_gamma

		self.electrons_rest_beta = add_beta(gamma_to_beta(self.electrons_gamma_0), -beta)
		self.electrons_rest_gamma = beta_to_gamma(self.electrons_rest_beta)
		self.electrons_rest_lambda = self.electrons_lambda_0 / self.electrons_rest_gamma

		beta = gamma_to_beta(self.reference_frame_gamma)

		self.protons_move_beta = add_beta(0, -beta)
		self.protons_move_gamma = beta_to_gamma(self.protons_move_beta)
		self.protons_move_lambda = self.protons_lambda_0 / self.protons_move_gamma

		self.electrons_move_beta = add_beta(gamma_to_beta(self.electrons_gamma_0), -beta)
		self.electrons_move_gamma = beta_to_gamma(self.electrons_move_beta)
		self.electrons_move_lambda = self.electrons_lambda_0 / self.electrons_move_gamma

	def show_charge(self):
		
		self.charge = Dot(1*DOWN)
		self.charge.set_color(self.electron_color)
		self.add(self.charge)

	def show_protons(self):
		protons_locations = np.arange(
			self.min_x_value,
			self.max_x_value + self.protons_rest_lambda,
			self.protons_rest_lambda
		)
		self.protons = protons = VGroup(*[
			Dot(location * RIGHT + self.proton_height)
			for location in protons_locations
		])
		protons.set_color(self.proton_color)
		self.add(protons)

	def transform_protons(self):
		protons_locations = np.arange(
			self.min_x_value,
			self.max_x_value + self.protons_move_lambda,
			self.protons_move_lambda
		)
		self.new_protons = protons = VGroup(*[
			Dot(location * RIGHT + self.proton_height)
			for location in protons_locations
		])
		protons.set_color(self.proton_color)
		self.play(Transform(self.protons, protons))

	def show_electrons(self):
		electron_locations = np.arange(
			self.min_x_value,
			self.max_x_value + self.electrons_rest_lambda,
			self.electrons_rest_lambda
		)
		self.electrons = electrons = VGroup(*[
			Dot(location * RIGHT + self.electron_height)
			for location in electron_locations
		])
		electrons.set_color(self.electron_color)
		self.add(electrons)

	def transform_electrons(self):
		electrons_locations = np.arange(
			self.min_x_value,
			self.max_x_value + self.electrons_move_lambda,
			self.electrons_move_lambda
		)
		self.new_electrons = electrons = VGroup(*[
			Dot(location * RIGHT + self.electron_height)
			for location in electrons_locations
		])
		electrons.set_color(self.electron_color)
		self.play(Transform(self.electrons, electrons))


class ReferenceFrameIntroduction(Scene):
	CONFIG = {
		"A_color": RED,
		"B_color": BLUE,

		"A_height": 1 * UP,
		"B_height": 0 * UP,

		"reference_frame_velocity": 0,
		"B_absolute_velocity": 2,

        "title" : TextMobject("A's Reference Frame"),

		"run_time": 5,
		"dt": 0.1,
	}

	def construct(self):
		self.init_values()

		self.A = Dot(self.A_height)
		self.A.set_color(self.A_color)
		self.add(self.A)

		self.B = Dot(self.B_height)
		self.B.set_color(self.B_color)
		self.add(self.B)

		self.add(self.velocity_A_tex, self.velocity_B_tex)

		self.title.to_corner(UP)
		self.add(self.title)
		# self.play( Write(self.title) )

		self.wait(1)
		self.animate_people()
		self.wait(1)

	def init_values(self):
		self.A_velocity = 0 - self.reference_frame_velocity
		self.B_velocity = self.B_absolute_velocity - self.reference_frame_velocity

		self.velocity_A_tex = TexMobject(f"Velocity_A={self.A_velocity:.2f} \\frac{{m}}{{s}}")
		self.velocity_A_tex.to_corner(DOWN+LEFT)
		self.velocity_B_tex = TexMobject(f"Velocity_B={self.B_velocity:.2f} \\frac{{m}}{{s}}")
		self.velocity_B_tex.to_corner(DOWN+RIGHT)
										

	def animate_people(self):
		for i in np.arange(0, self.run_time, self.dt):
			self.move_people(self.dt)
			self.wait(self.dt)

	def move_people(self, dt):
		self.A.shift(self.A_velocity * dt * RIGHT)
		self.B.shift(self.B_velocity * dt * RIGHT)


class ReferenceFrameIntroduction_A(ReferenceFrameIntroduction):
	CONFIG = {
		"reference_frame_velocity": 0,
        "title" : TextMobject("A's Reference Frame"),
	}
class ReferenceFrameIntroduction_B(ReferenceFrameIntroduction):
	CONFIG = {
		"reference_frame_velocity": 2,
        "title" : TextMobject("B's Reference Frame"),
	}
class ReferenceFrameIntroduction_COM(ReferenceFrameIntroduction):
	CONFIG = {
		"reference_frame_velocity": 1,
        "title" : TextMobject("Center of Mass Reference Frame"),
		"run_time": 7.2,
	}
