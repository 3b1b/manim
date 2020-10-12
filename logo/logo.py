from manim import *

NEW_BLUE = "#68a8e1"


class Thumbnail(GraphScene):
    CONFIG = {
        "y_max": 8,
        "y_axis_height": 5,
    }

    def construct(self):
        self.show_function_graph()

    def show_function_graph(self):
        self.setup_axes(animate=False)

        def func(x):
            return 0.1 * (x + 3 - 5) * (x - 3 - 5) * (x - 5) + 5

        def rect(x):
            return 2.775 * (x - 1.5) + 3.862

        recta = self.get_graph(rect, x_min=-1, x_max=5)
        graph = self.get_graph(func, x_min=0.2, x_max=9)
        graph.set_color(NEW_BLUE)
        input_tracker_p1 = ValueTracker(1.5)
        input_tracker_p2 = ValueTracker(3.5)

        def get_x_value(input_tracker):
            return input_tracker.get_value()

        def get_y_value(input_tracker):
            return graph.underlying_function(get_x_value(input_tracker))

        def get_x_point(input_tracker):
            return self.coords_to_point(get_x_value(input_tracker), 0)

        def get_y_point(input_tracker):
            return self.coords_to_point(0, get_y_value(input_tracker))

        def get_graph_point(input_tracker):
            return self.coords_to_point(
                get_x_value(input_tracker), get_y_value(input_tracker)
            )

        def get_v_line(input_tracker):
            return DashedLine(
                get_x_point(input_tracker),
                get_graph_point(input_tracker),
                stroke_width=2,
            )

        def get_h_line(input_tracker):
            return DashedLine(
                get_graph_point(input_tracker),
                get_y_point(input_tracker),
                stroke_width=2,
            )

        #
        input_triangle_p1 = RegularPolygon(n=3, start_angle=TAU / 4)
        output_triangle_p1 = RegularPolygon(n=3, start_angle=0)
        for triangle in input_triangle_p1, output_triangle_p1:
            triangle.set_fill(WHITE, 1)
            triangle.set_stroke(width=0)
            triangle.scale(0.1)
        #
        input_triangle_p2 = RegularPolygon(n=3, start_angle=TAU / 4)
        output_triangle_p2 = RegularPolygon(n=3, start_angle=0)
        for triangle in input_triangle_p2, output_triangle_p2:
            triangle.set_fill(WHITE, 1)
            triangle.set_stroke(width=0)
            triangle.scale(0.1)

        #
        x_label_p1 = MathTex("a")
        output_label_p1 = MathTex("f(a)")
        x_label_p2 = MathTex("b")
        output_label_p2 = MathTex("f(b)")
        v_line_p1 = get_v_line(input_tracker_p1)
        v_line_p2 = get_v_line(input_tracker_p2)
        h_line_p1 = get_h_line(input_tracker_p1)
        h_line_p2 = get_h_line(input_tracker_p2)
        graph_dot_p1 = Dot(color=WHITE)
        graph_dot_p2 = Dot(color=WHITE)

        # reposition mobjects
        x_label_p1.next_to(v_line_p1, DOWN)
        x_label_p2.next_to(v_line_p2, DOWN)
        output_label_p1.next_to(h_line_p1, LEFT)
        output_label_p2.next_to(h_line_p2, LEFT)
        input_triangle_p1.next_to(v_line_p1, DOWN, buff=0)
        input_triangle_p2.next_to(v_line_p2, DOWN, buff=0)
        output_triangle_p1.next_to(h_line_p1, LEFT, buff=0)
        output_triangle_p2.next_to(h_line_p2, LEFT, buff=0)
        graph_dot_p1.move_to(get_graph_point(input_tracker_p1))
        graph_dot_p2.move_to(get_graph_point(input_tracker_p2))

        #
        self.play(ShowCreation(graph))
        # Animacion del punto a
        self.add_foreground_mobject(graph_dot_p1)
        self.add_foreground_mobject(graph_dot_p2)
        self.play(
            DrawBorderThenFill(input_triangle_p1),
            Write(x_label_p1),
            ShowCreation(v_line_p1),
            GrowFromCenter(graph_dot_p1),
            ShowCreation(h_line_p1),
            Write(output_label_p1),
            DrawBorderThenFill(output_triangle_p1),
            DrawBorderThenFill(input_triangle_p2),
            Write(x_label_p2),
            ShowCreation(v_line_p2),
            GrowFromCenter(graph_dot_p2),
            ShowCreation(h_line_p2),
            Write(output_label_p2),
            DrawBorderThenFill(output_triangle_p2),
            run_time=0.5,
        )
        self.add(
            input_triangle_p2,
            x_label_p2,
            graph_dot_p2,
            v_line_p2,
            h_line_p2,
            output_triangle_p2,
            output_label_p2,
        )
        ###################
        pendiente_recta = self.get_secant_slope_group(
            1.9,
            recta,
            dx=1.4,
            df_label=None,
            dx_label=None,
            dx_line_color=PURPLE,
            df_line_color=ORANGE,
        )
        grupo_secante = self.get_secant_slope_group(
            1.5,
            graph,
            dx=2,
            df_label=None,
            dx_label=None,
            dx_line_color="#942357",
            df_line_color="#3f7d5c",
            secant_line_color=RED,
        )

        self.add(
            input_triangle_p2,
            graph_dot_p2,
            v_line_p2,
            h_line_p2,
            output_triangle_p2,
        )
        self.play(FadeIn(grupo_secante))

        kwargs = {
            "x_min": 4,
            "x_max": 9,
            "fill_opacity": 0.75,
            "stroke_width": 0.25,
        }
        self.graph = graph
        iteraciones = 6

        self.rect_list = self.get_riemann_rectangles_list(
            graph, iteraciones, start_color=PURPLE, end_color=ORANGE, **kwargs
        )
        flat_rects = self.get_riemann_rectangles(
            self.get_graph(lambda x: 0),
            dx=0.5,
            start_color=invert_color(PURPLE),
            end_color=invert_color(ORANGE),
            **kwargs
        )
        rects = self.rect_list[0]
        self.transform_between_riemann_rects(
            flat_rects, rects, replace_mobject_with_target_in_scene=True, run_time=0.9
        )

        # adding manim
        picture = Group(*self.mobjects)
        picture.scale(0.6).to_edge(LEFT, buff=SMALL_BUFF)
        manim = Tex("Manim").set_height(1.5).next_to(picture, RIGHT).shift(DOWN * 0.7)
        self.add(manim)
