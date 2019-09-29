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


class Algebra(Scene):
	def construct(self):
		"""
		We will assume that the material is an ideal gas
			atoms are far apart, they dont know about each other
			thus, energy only depends on temperature
			energy doesnt depend on volume or pressure
				cause they dont collide
		We will further assume that the gas is monoatomic
			This tells us that all of the particle energy is kinetic energy
			no potential energy
		thus, we know that the total energy of a system, which is given by the 
			equation of state of an ideal gas
			U = 3/2 N k_B T
		We know that the energy is only kinetic energy, and that kinetic energy is
			E_k = 1/2 m v^2
			kinetic energy is additive
		U = N * E_k
		"""

		E_k = TexMobject("E_k=\\frac{1}{2} m v^2")
		E_k.to_corner(UL)
		U_E_k = TexMobject("U=N E_k")
		U_E_k.to_corner(UR)
		self.add(E_k, U_E_k)

		U_equation = TexMobject(
			"U", "=", "\\frac{3}{2}", "N", "k_B", "T"
		)
		U_equation.set_color_by_tex("T", GREEN)

		self.play(
			Write(U_equation),
		)

		N__E_k = TexMobject("N", "E_k")
		N__E_k.move_to(U_equation[0].get_center())
		N__E_k.shift(0.3 * LEFT)
		self.play(
			ReplacementTransform( U_equation[0], N__E_k ),
		)

		self.play(
			U_equation[2].move_to, U_equation[3].get_center(),
			U_equation[3].move_to, U_equation[2].get_center(),
		)

		N = U_equation[3]
		self.play(
			FadeOut(N__E_k[0]),
			FadeOut(N),
		)

		self.play(
			U_equation[1].move_to, N.get_center()
		)

		E_k = N__E_k[1]
		E_k_equation = TexMobject("\\frac{1}{2}", "m", "v^2")
		E_k_equation.move_to(E_k.get_center())
		self.play(
			ReplacementTransform( E_k, E_k_equation ),
		)

		one = TexMobject("1")
		one.move_to(E_k_equation[0].get_center())
		three = TexMobject("3")
		three.move_to(U_equation[2].get_center())

		self.play(
			ReplacementTransform( E_k_equation[0], one ),
			ReplacementTransform( U_equation[2], three ),
		)
		self.play(
			FadeOut(one)
		)

		temp = TexMobject("\\frac{3 k_B}{m}")
		temp.move_to(
			(three.get_center() + U_equation[4].get_center()) / 2
		)
		group = VGroup(E_k_equation[1], three, U_equation[4])
		self.play(
			ReplacementTransform( group, temp ),
		)

		self.wait(5)


class Algebra_test(Scene):
	def construct(self):
		equation = TexMobject(
			"A", "\\vec{\\textbf{x}}", "=", "\\vec{\\textbf{v}}"
		)
		equation.scale(1.25)
		equation.set_color_by_tex("{x}", GREEN)
		equation.set_color_by_tex("{v}", RED)
		equation.to_corner(UL)
		self.add(equation)
		self.add_foreground_mobject(equation)

		det_equation = TexMobject(
			"\\det{", "A", "}", "=", "0"
		)
		det_equation.scale(1.25)
		det_equation.next_to(
			equation, DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
		self.play(
			Write(det_equation[0]),
		)
		self.wait(2)
		self.play(
			ReplacementTransform(
				equation.get_part_by_tex("A").copy(),
				det_equation.get_part_by_tex("A").copy(),
			),
			Write(det_equation[2:]),
		)
		self.add_foreground_mobject(det_equation)

		self.wait(3)
		return



class LorentzForce(Scene):
	def construct(self):
		equation = TexMobject(
			*("F = q ( E + v \\times B )".split())
		)
		equation.set_height(1.6)

		equation.set_color_by_tex("E", BLUE)
		equation.set_color_by_tex("B", RED)
		equation.set_color_by_tex("v", GREEN)

		self.play(
			Write(equation),
		)

		self.wait(3)
		return
