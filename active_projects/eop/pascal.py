from big_ol_pile_of_manim_imports import *

nb_levels = 50

dev_x_step = 2
dev_y_step = 5

def rainbow_color(alpha):
	nb_colors = 100
	rainbow = color_gradient([RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE], nb_colors)
	rainbow = np.append(rainbow,PURPLE)
	index = int(alpha * nb_colors)
	return rainbow[index]






class PascalScene(Scene):

	def construct(self):

		unit_width = 0.25
		top_height = 4.0
		level_height = 2.0 * top_height / nb_levels

		start_points = np.array([top_height * UP])

		dev_start = start_points[0]

		j = 0

		for n in range(nb_levels):

			half_width = 0.5 * (n + 0.5) * unit_width

			stop_points_left = start_points.copy()
			stop_points_left[:,0] -= 0.5 * unit_width
			stop_points_left[:,1] -= level_height

			stop_points_right = start_points.copy()
			stop_points_right[:,0] += 0.5 * unit_width
			stop_points_right[:,1] -= level_height
			
			for (p,q) in zip(start_points,stop_points_left):
				alpha = np.abs((p[0]+q[0])/2) / half_width
				color = rainbow_color(alpha)
				line = Line(p,q, stroke_color = color)
				self.add(line)

			for (i,(p,q)) in enumerate(zip(start_points,stop_points_right)):
				alpha = np.abs((p[0]+q[0])/2) / half_width
				color = rainbow_color(alpha)
				line = Line(p,q, stroke_color = color)
				self.add(line)

			if (n + 1) % dev_y_step == 0 and n != 1:
				j += dev_x_step
				dev_stop = stop_points_left[j]
				line = Line(dev_start,dev_stop,stroke_color = WHITE)
				self.add(line)
				dot = Dot(dev_stop, fill_color = WHITE)
				self.add_foreground_mobject(dot)
				dev_start = dev_stop

			start_points = np.append(stop_points_left,[stop_points_right[-1]], axis = 0)


		self.wait()



class RescaledPascalScene(Scene):

	def construct(self):

		half_width = 3.0
		top_height = 4.0
		level_height = 2.0 * top_height / nb_levels

		start_points = np.array([top_height * UP])
		left_edge = top_height * UP + half_width * LEFT
		right_edge = top_height * UP + half_width * RIGHT

		dev_start = start_points[0]

		j = 0

		for n in range(nb_levels):

			if n == 0:
				start_points_left_shift = np.array([left_edge])
			else:
				start_points_left_shift = start_points[:-1]
				start_points_left_shift = np.insert(start_points_left_shift,0,left_edge, axis = 0)
			stop_points_left = 0.5 * (start_points + start_points_left_shift)
			stop_points_left += level_height * DOWN

			
			if n == 0:
				start_points_right_shift = np.array([right_edge])
			else:
				start_points_right_shift = start_points[1:]
				start_points_right_shift = np.append(start_points_right_shift,np.array([right_edge]), axis = 0)
			stop_points_right = 0.5 * (start_points + start_points_right_shift)
			stop_points_right += level_height * DOWN

			
			for (i,(p,q)) in enumerate(zip(start_points,stop_points_left)):
				
				color = LIGHT_GRAY 

				if n % 2 == 0 and i <= n/2:
					m = n/2 + 0.25
					jj = i
					alpha = 1 - float(jj)/m
					color = rainbow_color(alpha)

				elif n % 2 == 0 and i > n/2:
					m = n/2 + 0.25
					jj = n - i + 0.5
					alpha = 1 - float(jj)/m
					color = rainbow_color(alpha)

				elif n % 2 == 1 and i <= n/2:
					m = n/2 + 0.75
					jj = i
					alpha = 1 - float(jj)/m
					color = rainbow_color(alpha)

				elif n % 2 == 1 and i > n/2:
					m = n/2 + 0.75
					jj = n - i + 0.5
					alpha = 1 - float(jj)/m
					color = rainbow_color(alpha)

				line = Line(p,q, stroke_color = color)
				self.add(line)

			for (i,(p,q)) in enumerate(zip(start_points,stop_points_right)):
				
				color = LIGHT_GRAY

				if n % 2 == 0 and i < n/2:
					m = n/2 + 0.25
					jj = i + 0.5
					alpha = 1 - float(jj)/m
					color = rainbow_color(alpha)

				elif n % 2 == 0 and i >= n/2:
					m = n/2 + 0.25
					jj = n - i
					alpha = 1 - float(jj)/m
					color = rainbow_color(alpha)

				elif n % 2 == 1 and i <= n/2:
					m = n/2 + 0.75
					jj = i + 0.5
					alpha = 1 - float(jj)/m
					color = rainbow_color(alpha)

				elif n % 2 == 1 and i > n/2:
					m = n/2 + 0.75
					jj = n - i
					alpha = 1 - float(jj)/m
					color = rainbow_color(alpha)


				line = Line(p,q, stroke_color = color)
				self.add(line)

			if (n + 1) % dev_y_step == 0 and n != 1:
				j += dev_x_step
				dev_stop = stop_points_left[j]
				line = Line(dev_start,dev_stop,stroke_color = WHITE)
				self.add(line)
				dot = Dot(dev_stop, fill_color = WHITE)
				self.add_foreground_mobject(dot)
				dev_start = dev_stop



			start_points = np.append(stop_points_left,[stop_points_right[-1]], axis = 0)
			
			left_edge += level_height * DOWN
			right_edge += level_height * DOWN


		self.wait()









