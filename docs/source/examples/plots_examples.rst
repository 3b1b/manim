Plotting with manim
=================================

Examples to illustrate the use of GrapheScenes in Manim


.. manim:: Plot1
    :quality: medium
    :save_last_frame:

    class Plot1(GraphScene):
        def construct(self):
            self.setup_axes()
            my_func = lambda x: np.sin(x)
            func_graph=self.get_graph(my_func)
            self.add(func_graph)

.. manim:: Plot2yLabel
    :quality: medium
    :save_last_frame:

    class Plot2yLabel(GraphScene):
        CONFIG = {
            "y_min": 0,
            "y_max": 100,
            "y_tick_frequency": 10,
            "y_labeled_nums": np.arange(0, 100, 10)
        }

        def construct(self):
            self.setup_axes(animate=True)
            dot = Dot()
            dot.move_to(self.coords_to_point(PI / 2, 20))
            my_func = lambda x: 20 * np.sin(x)
            func_graph = self.get_graph(my_func)
            self.add(func_graph)
            self.add(dot)

.. manim:: Plot3DataPoints
    :quality: medium
    :save_last_frame:

    class Plot3DataPoints(GraphScene):
        CONFIG = {
            "y_axis_label": r"Concentration[$\%$]",
            "x_axis_label": "Time [s]",
            }

        def construct(self):
            data = [1, 2, 2, 4, 4, 1, 3]
            self.setup_axes(animate=True)
            for time, dat in enumerate(data):
                dot = Dot().move_to(self.coords_to_point(time, dat))
                self.add(dot)
                self.wait(1)
                print(time)
            self.wait()

.. manim:: Plot3bGaussian
    :quality: medium
    :save_last_frame:

    class Plot3bGaussian(GraphScene):
        def construct(self):
            def gaussian(x):
                mu=3; sig= 1; amp=5
                return amp*np.exp( ( -1/2 * ( (x-mu)/sig)**2 ) )
            self.setup_axes()
            graph = self.get_graph(gaussian, x_min=-1, x_max=10, ).set_stroke(width=5)
            self.add(graph)

.. manim:: Plot4SinCos
    :quality: medium
    :save_last_frame:

    class Plot4SinCos(GraphScene):
        CONFIG = {
            "x_min": -10,
            "x_max": 10.3,
            "num_graph_anchor_points": 100,
            "y_min": -1.5,
            "y_max": 1.5,
            "graph_origin": ORIGIN,
            "function_color": RED,
            "axes_color": GREEN,
            "x_labeled_nums": range(-10, 12, 2),
        }

        def construct(self):
            self.setup_axes(animate=False)

            def func_cos(x):
                return np.cos(x)

            def func_sin(x):
                return np.sin(x)

            func_graph = self.get_graph(func_cos, self.function_color)
            func_graph2 = self.get_graph(func_sin)
            vert_line = self.get_vertical_line_to_graph(TAU, func_graph, color=YELLOW)
            graph_lab = self.get_graph_label(func_graph, label="\\cos(x)")
            graph_lab2 = self.get_graph_label(func_graph2, label="\\sin(x)", x_val=-10, direction=UP / 2)
            two_pi = TexMobject("x = 2 \\pi")
            label_coord = self.input_to_graph_point(TAU, func_graph)
            two_pi.next_to(label_coord, RIGHT + UP)
            self.add(func_graph, func_graph2, vert_line, graph_lab, graph_lab2, two_pi)

.. manim:: Plot5Area
    :quality: medium
    :save_last_frame:

    class Plot5Area(GraphScene):
        CONFIG = {
            "x_min" : 0,
            "x_max" : 5,
            "y_min" : 0,
            "y_max" : 6,
            "y_tick_frequency" : 1,
            "x_tick_frequency" : 1,
            "x_labeled_nums" : [0,2,3]
        }
        def construct(self):
            self.setup_axes(animate=False)
            curve1 = self.get_graph(lambda x : 4*x-x**2, x_min=0,x_max=4)
            curve2 = self.get_graph(lambda x : 0.8*x**2-3*x+4, x_min=0,x_max=4)
            line1 = self.get_vertical_line_to_graph(2,curve1,DashedLine,color=YELLOW)
            line2 = self.get_vertical_line_to_graph(3,curve1,DashedLine,color=YELLOW)
            area1 = self.get_area(curve1,0.3,0.6, dx_scaling=10, area_color=BLUE)
            area2 = self.get_area(curve2,2,3,bounded=curve1)
            self.add(curve1,curve2,line1,line2,area1,area2)

.. manim:: Plot6HeatDiagram
    :quality: medium
    :save_last_frame:

    class Plot6HeatDiagram(GraphScene):
        CONFIG = {
            "y_axis_label": r"T[$^\circ C$]",
            "x_axis_label": r"$\Delta Q$",
            "y_min": -8,
            "y_max": 30,
            "x_min": 0,
            "x_max": 40,
            "y_labeled_nums": np.arange(-5, 34, 5),
            "x_labeled_nums": np.arange(0, 40, 5),

        }

        def construct(self):
            data = [20, 0, 0, -5]
            x = [0, 8, 38, 39]
            print(x)
            self.setup_axes(animate=True)
            dot_collection = VGroup()
            for time, val in enumerate(data):
                dot = Dot().move_to(self.coords_to_point(x[time], val))
                self.add(dot)
                dot_collection.add(dot)
            l1 = Line(dot_collection[0].get_center(), dot_collection[1].get_center())
            l2 = Line(dot_collection[1].get_center(), dot_collection[2].get_center())
            l3 = Line(dot_collection[2].get_center(), dot_collection[3].get_center())
            self.add(l1, l2, l3)


This is an parametric function

.. manim:: ParamFunc1
    :quality: medium
    :save_last_frame:

    class ParamFunc1(Scene):
       def func(self,t):
           return np.array((np.sin(2*t), np.sin(3*t),0))
       def construct(self):
           func=ParametricFunction(self.func, t_max=TAU, fill_opacity=0).set_color(RED)
           self.add(func.scale(3))