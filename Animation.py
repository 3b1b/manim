"""Simple Manim example scene.

Place this file in your working directory and render with:

	manim -pql Animation.py SimpleTransform

Flags: -p opens the resulting video, -ql renders in low quality (fast).
"""

from manim import *
import numpy as np


class SimpleTransform(Scene):
	def construct(self):
		# Create a blue square
		square = Square(side_length=2, color=BLUE)
		# Create a green circle to transform into
		circle = Circle(radius=1.2, color=GREEN).shift(RIGHT * 2)

		# Animate the creation of the square
		self.play(Create(square))
		# Morph the square into the circle
		self.play(Transform(square, circle))
		# Move the transformed shape left and fade out
		self.play(square.animate.shift(LEFT))
		self.play(FadeOut(square))
		self.wait(1)


class TextWrite(Scene):
	def construct(self):
		text = Text("Hello, Manim!", font_size=72)
		self.play(Write(text))
		self.wait(1)


class JecklesLightning(Scene):
	"""Display 'JecklesTV' with lightning strike effects.

	Render with:
		manim -pql Animation.py JecklesLightning
	"""

	def make_bolt(self, start: np.ndarray, end: np.ndarray, segments=12,
				  variance=0.5) -> VMobject:
		"""Generate a jagged lightning bolt as a VMobject between two points.

		The bolt is a polyline with random perpendicular displacements.
		"""
		points = [np.array(start, dtype=float)]
		vec = end - start
		length = np.linalg.norm(vec)
		if length == 0:
			return VMobject()
		direction = vec / length
		# perpendicular vector for displacement
		perp = np.array([-direction[1], direction[0], 0.0])

		for i in range(1, segments):
			t = i / segments
			base = start + direction * (t * length)
			disp = (np.random.uniform(-1, 1) * variance) * (1 - abs(t - 0.5) * 2)
			jitter = base + perp * disp
			jitter += np.random.normal(scale=0.02, size=3)
			points.append(jitter)
		points.append(np.array(end, dtype=float))

		bolt = VMobject()
		bolt.set_points_as_corners(points)
		bolt.set_stroke(color=WHITE, width=3)
		bolt.set_fill(opacity=0)
		return bolt

	def construct(self):
		# Main title
		title = Text("JecklesTV", font_size=144, weight=BOLD)
		title.set_color_by_gradient(BLUE, TEAL)
		self.play(FadeIn(title, scale=0.6))
		self.wait(0.25)

		# Lightning strike parameters
		n_strikes = 4
		for i in range(n_strikes):
			# pick a random point above the title to strike down
			left = title.get_left()
			right = title.get_right()
			top = title.get_top()
			x = np.random.uniform(left[0] - 0.5, right[0] + 0.5)
			start = np.array([x, top[1] + np.random.uniform(1.0, 2.0), 0.0])
			# pick a random target point near the title baseline
			tx = np.random.uniform(left[0] + 0.2, right[0] - 0.2)
			ty = np.random.uniform(title.get_bottom()[1] + 0.1, title.get_top()[1] - 0.2)
			end = np.array([tx, ty, 0.0])

			bolt = self.make_bolt(start, end, segments=14, variance=0.6)
			# add a glow behind the bolt
			glow = bolt.copy()
			glow.set_stroke(color=YELLOW, width=18, opacity=0.15)

			# quick flash overlay to brighten the frame
			flash = FullScreenRectangle(fill_color=WHITE, fill_opacity=0.0)

			# show the glow then the bolt, flash, and make the title flicker
			self.add(glow)
			self.play(Create(bolt), run_time=0.08)
			self.play(flash.animate.set_opacity(0.6), run_time=0.03)
			self.play(flash.animate.set_opacity(0.0), run_time=0.06)

			# short title flicker: momentarily brighten the title
			orig_colors = title.get_color()
			self.play(title.animate.set_color(WHITE), run_time=0.04)
			self.play(title.animate.set_color_by_gradient(BLUE, TEAL), run_time=0.08)

			# fade bolt and glow quickly
			self.play(FadeOut(bolt, shift=DOWN), FadeOut(glow), run_time=0.12)
			self.wait(0.12)

		# final flourish
		self.play(title.animate.scale(1.03), run_time=0.4)
		self.play(title.animate.scale(1 / 1.03), run_time=0.35)
		self.wait(1)
