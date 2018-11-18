from big_ol_pile_of_manim_imports import *

class PlotFunctions(GraphScene):
	CONFIG = {
	"x_min" : -10,
	"x_max" : 10,
	"y_min" : -1.5,
	"y_max" : 1.5,
	"z_min" : -5,
	"z_max" : 5,
	"graph_origin" : ORIGIN ,
	"function_color" : RED ,
	"axes_color" : GREEN,
	"x_labeled_nums" :range(-10,12,2),
	}

	def func_to_graph(self,x):
		return np.cos(x)
	 
	def func_to_graph2(self,x):
		return np.sin(x)

	def func_to_graph3(self,x,y):
		return x+y

	def construct(self):
		self.setup_axes(animate=True)
		
		func_graph  = self.get_graph(self.func_to_graph, self.function_color)
		func_graph2 = self.get_graph(self.func_to_graph2)
		func_graph3 = self.get_graph(self.func_to_graph3)

		vert_line = self.get_vertical_line_to_graph(TAU,func_graph,color=YELLOW)
		graph_lab = self.get_graph_label(func_graph, label = "\\cos(x)")
		graph_lab2=self.get_graph_label(func_graph2,label = "\\sin(x)", x_val=-10, direction=UP/2)
		graph_lab3 = self.get_graph_label(func_graph3, label = "\\x+y")
		#t
		wo_pi = TexMobject("x = 2 \\pi")
		label_coord = self.input_to_graph_point(TAU,func_graph)
		two_pi.next_to(label_coord,RIGHT+UP)
		 
		self.play(ShowCreation(func_graph), ShowCreation(func_graph2), ShowCreation(func_graph3))
		self.play(ShowCreation(vert_line), ShowCreation(graph_lab), ShowCreation(graph_lab2),ShowCreation(two_pi))
	 
