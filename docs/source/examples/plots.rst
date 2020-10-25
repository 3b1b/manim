Plotting with manim
=================================

Examples to illustrate the use of :class:`.GraphScene` in manim.


.. manim:: FunctionPlot
    :save_last_frame:

    class FunctionPlot(GraphScene):
        def construct(self):
            self.setup_axes()
            func_graph=self.get_graph(lambda x: np.sin(x))
            self.add(func_graph)

.. manim:: FunctionPlotWithLabbeledYAxe
    :save_last_frame:

    class FunctionPlotWithLabbeledYAxe(GraphScene):
        CONFIG = {
            "y_min": 0,
            "y_max": 100,
            "y_axis_config": {"tick_frequency": 10},
            "y_labeled_nums": np.arange(0, 100, 10)
        }

        def construct(self):
            self.setup_axes()
            dot = Dot().move_to(self.coords_to_point(PI / 2, 20))
            func_graph = self.get_graph(lambda x: 20 * np.sin(x))
            self.add(dot,func_graph)

.. manim:: SequencePlot
    :save_last_frame:

    class SequencePlot(GraphScene):
        CONFIG = {
            "y_axis_label": r"Concentration [\%]",
            "x_axis_label": "Time [s]",
            }

        def construct(self):
            data = [1, 2, 2, 4, 4, 1, 3]
            self.setup_axes()
            for time, dat in enumerate(data):
                dot = Dot().move_to(self.coords_to_point(time, dat))
                self.add(dot)

.. manim:: GaussianFunctionPlot1
    :save_last_frame:

    amp = 5
    mu = 3
    sig = 1

    def gaussian(x):
        return amp * np.exp((-1 / 2 * ((x - mu) / sig) ** 2))

    class GaussianFunctionPlot1(GraphScene):
        def construct(self):
            self.setup_axes()
            graph = self.get_graph(gaussian, x_min=-1, x_max=10)
            graph.set_stroke(width=5)
            self.add(graph)

.. manim:: GaussianFunctionPlot2
    :save_last_frame:

    class GaussianFunctionPlot2(GraphScene):
        def construct(self):
            def gaussian(x):
                amp = 5
                mu = 3
                sig = 1
                return amp * np.exp((-1 / 2 * ((x - mu) / sig) ** 2))
            self.setup_axes()
            graph = self.get_graph(gaussian, x_min=-1, x_max=10)
            graph.set_style(stroke_width=5, stroke_color=GREEN)
            self.add(graph)


.. manim:: SinAndCosFunctionPlot
    :save_last_frame:

    class SinAndCosFunctionPlot(GraphScene):
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
            func_graph = self.get_graph(np.cos, self.function_color)
            func_graph2 = self.get_graph(np.sin)
            vert_line = self.get_vertical_line_to_graph(TAU, func_graph, color=YELLOW)
            graph_lab = self.get_graph_label(func_graph, label="\\cos(x)")
            graph_lab2 = self.get_graph_label(func_graph2, label="\\sin(x)",
                                x_val=-10, direction=UP / 2)
            two_pi = MathTex(r"x = 2 \pi")
            label_coord = self.input_to_graph_point(TAU, func_graph)
            two_pi.next_to(label_coord, RIGHT + UP)
            self.add(func_graph, func_graph2, vert_line, graph_lab, graph_lab2, two_pi)

.. manim:: GraphAreaPlot
    :save_last_frame:

    class GraphAreaPlot(GraphScene):
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
            self.setup_axes()
            curve1 = self.get_graph(lambda x: 4 * x - x ** 2, x_min=0, x_max=4)
            curve2 = self.get_graph(lambda x: 0.8 * x ** 2 - 3 * x + 4, x_min=0, x_max=4)
            line1 = self.get_vertical_line_to_graph(2, curve1, DashedLine, color=YELLOW)
            line2 = self.get_vertical_line_to_graph(3, curve1, DashedLine, color=YELLOW)
            area1 = self.get_area(curve1, 0.3, 0.6, dx_scaling=10, area_color=BLUE)
            area2 = self.get_area(curve2, 2, 3, bounded=curve1)
            self.add(curve1, curve2, line1, line2, area1, area2)

.. manim:: HeatDiagramPlot
    :save_last_frame:

    class HeatDiagramPlot(GraphScene):
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
            self.setup_axes()
            dot_collection = VGroup()
            for time, val in enumerate(data):
                dot = Dot().move_to(self.coords_to_point(x[time], val))
                self.add(dot)
                dot_collection.add(dot)
            l1 = Line(dot_collection[0].get_center(), dot_collection[1].get_center())
            l2 = Line(dot_collection[1].get_center(), dot_collection[2].get_center())
            l3 = Line(dot_collection[2].get_center(), dot_collection[3].get_center())
            self.add(l1, l2, l3)


.. manim:: ParametricFunctionWithoutGraphScene
    :save_last_frame:

    class ParametricFunctionWithoutGraphScene(Scene):
        def func(self, t):
            return np.array((np.sin(2 * t), np.sin(3 * t), 0))

        def construct(self):
            func = ParametricFunction(self.func, t_max = TAU, fill_opacity=0).set_color(RED)
            self.add(func.scale(3))
