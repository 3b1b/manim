from helpers import *
from mobject import Mobject
from mobject.vectorized_mobject import *
from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from topics.geometry import *
from scene import Scene
from camera import *
from topics.number_line import *
from topics.three_dimensions import *
from topics.light import *
from topics.characters import *
from topics.numerals import *



class Histogram(VMobject):

	CONFIG = {
		"start_color" : YELLOW,
		"end_color" : BLUE,
		"x_scale" : 1.0,
		"y_scale" : 1.0,
	}

	def __init__(self, x_values, y_values, **kwargs):

		digest_config(self, kwargs)

		# preliminaries
		self.x_values = x_values
		self.y_values = y_values

		self.x_steps = x_values[1:] - x_values[:-1]
		self.x_min = x_values[0] - self.x_steps[0] * 0.5
		self.x_posts = (x_values[1:] + x_values[:-1]) * 0.5
		self.x_max = x_values[-1] + self.x_steps[-1] * 0.5
		self.x_posts = np.insert(self.x_posts,0,self.x_min)
		self.x_posts = np.append(self.x_posts,self.x_max)

		self.x_widths = self.x_posts[1:] - self.x_posts[:-1]

		self.x_values_scaled = self.x_scale * x_values
		self.x_steps_scaled = self.x_scale * self.x_steps
		self.x_posts_scaled = self.x_scale * self.x_posts
		self.x_min_scaled = self.x_scale * self.x_min
		self.x_max_scaled = self.x_scale * self.x_max
		self.x_widths_scaled = self.x_scale * self.x_widths

		self.y_values_scaled = self.y_scale * self.y_values

		VMobject.__init__(self, **kwargs)
		
	def generate_points(self):

		previous_bar = ORIGIN

		outline_points = []

		for (i,x) in enumerate(self.x_values):

			bar = Rectangle(
				width = self.x_widths_scaled[i],
				height = self.y_values_scaled[i],
			)
			t = float(x - self.x_values[0])/(self.x_values[-1] - self.x_values[0])
			bar_color = interpolate_color(
				self.start_color,
				self.end_color,
				t
			)
			bar.set_fill(color = bar_color, opacity = 1)
			bar.set_stroke(width = 0)
			bar.next_to(previous_bar,RIGHT,buff = 0)
			if i != 0:
				height_diff = previous_bar.get_height() - bar.get_height()
				bar.shift(height_diff * 0.5 * DOWN)
			
			self.add(bar)

			if i == 0:
				# start with the lower left
				outline_points.append(bar.get_anchors()[-2])

			# upper two points of each bar
			outline_points.append(bar.get_anchors()[0])
			outline_points.append(bar.get_anchors()[1])

			previous_bar = bar

		# close the outline
			# lower right
		outline_points.append(bar.get_anchors()[2])
			# lower left
		outline_points.append(outline_points[0])

		self.outline = Polygon(*outline_points)
		self.outline.set_stroke(color = WHITE)
		self.add(self.outline)



class SampleScene(Scene):

	def construct(self):

		x_values = np.array([1,3,6,10,15])
		y_values = np.array([15,10,6,3,1])

		hist = Histogram(
			x_values = x_values,
			y_values = y_values,
			x_scale = 0.2,
			y_scale = 0.2,
		)
		self.add(hist)
		self.wait()













