from big_ol_pile_of_manim_imports import *

class PlotFunctions(GraphScene):
	CONFIG = {
			"x_min" : -20,
			"x_max" : 20,
			"y_min" : -1.5,
			"y_max" : 1.5,
			"graph_origin" : ORIGIN ,
			"function_color" : RED ,
			"function_2_color": YELLOW,
			"axes_color" : GREEN,
			"x_labeled_nums" :range(-20,12,4),
	}

	def func_to_graph(self,x):
		return np.cos(x)
	 
	def func_to_graph2(self,x):
		return np.sin(x)

	def construct(self):
		self.setup_axes(animate=True) # create axis

		func_graph  = self.get_graph(self.func_to_graph, self.function_color)
		func_graph2 = self.get_graph(self.func_to_graph2, self.function_2_color)

		vert_line = self.get_vertical_line_to_graph(5,func_graph,color=BLUE)

		graph_label = self.get_graph_label(func_graph, label = r"\cos(x)")
		graph_label2= self.get_graph_label(func_graph2,label = r"\sin(x)", x_val=-10, direction=UP/2)
		label_coord = self.input_to_graph_point(5,func_graph)

		two_pi = TexMobject("x = 5")#("x = 2 \\pi")
		two_pi.next_to(label_coord,RIGHT+UP)
		 
		self.play(ShowCreation(func_graph),ShowCreation(func_graph2))
		self.play(ShowCreation(vert_line), ShowCreation(graph_label), ShowCreation(graph_label2),ShowCreation(two_pi))
		self.wait(5)
		 
