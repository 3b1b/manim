from big_ol_pile_of_manim_imports import *

class SecanteDerivadaV1(GraphScene):
    CONFIG = {
        "y_max": 8,
        "y_axis_height": 5,
    }

    def construct(self):
        self.add_title()
        self.show_function_graph()
        #self.otra_definicion()

    def add_title(self):
        title = self.title = TextMobject("\\underline{\\sc Visualizaci\\'on de la Derivada}")
        title.to_edge(UP)
        self.add_foreground_mobject(title)
        h_line = Line(LEFT, RIGHT)
        h_line.set_height(FRAME_WIDTH - 2 * LARGE_BUFF)
        h_line.next_to(title, DOWN)
        h_line.set_stroke(WHITE,3)
        title.to_edge(UP+LEFT)
        title.shift(RIGHT)

        self.add(title)
        self.lin_h = h_line

    def show_function_graph(self):
        self.setup_axes()

        def func(x):
            return 0.1 * (x + 3-5) * (x - 3-5) * (x-5) + 5

        def rect(x):
            return 2.775*(x-1.5)+3.862
        recta = self.get_graph(rect,x_min=-1,x_max=5)
        graph = self.get_graph(func,x_min=0.2,x_max=9)
        graph.set_color(TT_AZUL_T)
        input_tracker_p1 = ValueTracker(1.5)
        input_tracker_p2 = ValueTracker(3.5)

        def get_x_value_p1():
            return input_tracker_p1.get_value()

        def get_x_value_p2():
            return input_tracker_p2.get_value()

        def get_y_value_p1():
            return graph.underlying_function(get_x_value_p1())

        def get_y_value_p2():
            return graph.underlying_function(get_x_value_p2())

        def get_x_point_p1():
            return self.coords_to_point(get_x_value_p1(), 0)

        def get_x_point_p2():
            return self.coords_to_point(get_x_value_p2(), 0)

        def get_y_point_p1():
            return self.coords_to_point(0, get_y_value_p1())

        def get_y_point_p2():
            return self.coords_to_point(0, get_y_value_p2())

        def get_graph_point_p1():
            return self.coords_to_point(get_x_value_p1(), get_y_value_p1())

        def get_graph_point_p2():
            return self.coords_to_point(get_x_value_p2(), get_y_value_p2())

        def get_v_line_p1():
            return DashedLine(get_x_point_p1(), get_graph_point_p1(), stroke_width=2)

        def get_v_line_p2():
            return DashedLine(get_x_point_p2(), get_graph_point_p2(), stroke_width=2)

        def get_h_line_p1():
            return DashedLine(get_graph_point_p1(), get_y_point_p1(), stroke_width=2)

        def get_h_line_p2():
            return DashedLine(get_graph_point_p2(), get_y_point_p2(), stroke_width=2)
        # Triangulo a
        input_triangle_p1 = RegularPolygon(n=3, start_angle=TAU / 4)
        output_triangle_p1 = RegularPolygon(n=3, start_angle=0)
        for triangle in input_triangle_p1, output_triangle_p1:
            triangle.set_fill(WHITE, 1)
            triangle.set_stroke(width=0)
            triangle.scale(0.1)
        # Triangulo b
        input_triangle_p2 = RegularPolygon(n=3, start_angle=TAU / 4)
        output_triangle_p2 = RegularPolygon(n=3, start_angle=0)
        for triangle in input_triangle_p2, output_triangle_p2:
            triangle.set_fill(WHITE, 1)
            triangle.set_stroke(width=0)
            triangle.scale(0.1)
        # Entradas y salidas del triangulo a
        input_triangle_update_p1 = ContinualUpdate(
            input_triangle_p1, lambda m: m.move_to(get_x_point_p1(), DOWN)
        )
        output_triangle_update_p1 = ContinualUpdate(
            output_triangle_p1, lambda m: m.move_to(get_y_point_p1(), LEFT)
        )
        # Entradas y salidas del triangulo b
        input_triangle_update_p2 = ContinualUpdate(
            input_triangle_p2, lambda m: m.move_to(get_x_point_p2(), DOWN)
        )
        output_triangle_update_p2 = ContinualUpdate(
            output_triangle_p2, lambda m: m.move_to(get_y_point_p2(), LEFT)
        )
        # Etiqueas y salidas del punto a
        x_label_p1 = TexMobject("a")
        x_label_update_p1 = ContinualUpdate(
            x_label_p1, lambda ma: ma.next_to(input_triangle_p1, DOWN, SMALL_BUFF)
        )

        output_label_p1 = TexMobject("f(a)")
        output_label_update_p1 = ContinualUpdate(
            output_label_p1, lambda ma: ma.next_to(
                output_triangle_p1, LEFT, SMALL_BUFF)
        )
        # Etiqueas y salidas del punto b
        x_label_p2 = TexMobject("b")
        x_label_update_p2 = ContinualUpdate(
            x_label_p2, lambda mb: mb.next_to(input_triangle_p2, DOWN, SMALL_BUFF)
        )

        output_label_p2 = TexMobject("f(b)")
        output_label_update_p2 = ContinualUpdate(
            output_label_p2, lambda mb: mb.next_to(
                output_triangle_p2, LEFT, SMALL_BUFF)
        )
        # V_lines de a
        v_line_p1 = get_v_line_p1()
        v_line_update_p1 = ContinualUpdate(
            v_line_p1, lambda vla: Transform(vla, get_v_line_p1()).update(1)
        )
        # V_lines de b
        v_line_p2 = get_v_line_p2()
        v_line_update_p2 = ContinualUpdate(
            v_line_p2, lambda vlb: Transform(vlb, get_v_line_p2()).update(1)
        )
        # h_lines de a
        h_line_p1 = get_h_line_p1()
        h_line_update_p1 = ContinualUpdate(
            h_line_p1, lambda hla: Transform(hla, get_h_line_p1()).update(1)
        )
        # h_lines de b
        h_line_p2 = get_h_line_p2()
        h_line_update_p2 = ContinualUpdate(
            h_line_p2, lambda hlb: Transform(hlb, get_h_line_p2()).update(1)
        )
        # Animacion del punto a
        graph_dot_p1 = Dot(color=TT_SIMBOLO)
        graph_dot_update_p1 = ContinualUpdate(
            graph_dot_p1, lambda ma: ma.move_to(get_graph_point_p1())
        )
        # Animacion del punto b
        graph_dot_p2 = Dot(color=TT_SIMBOLO)
        graph_dot_update_p2 = ContinualUpdate(
            graph_dot_p2, lambda mb: mb.move_to(get_graph_point_p2())
        )
        #
        self.play(
            ShowCreation(graph),
        )
        # Animacion del punto a
        self.play(
            DrawBorderThenFill(input_triangle_p1, run_time=1),
            Write(x_label_p1),
            ShowCreation(v_line_p1),
            GrowFromCenter(graph_dot_p1),
        )
        self.add_foreground_mobject(graph_dot_p1)
        self.play(
            ShowCreation(h_line_p1),
            Write(output_label_p1),
            DrawBorderThenFill(output_triangle_p1, run_time=1)
        )
        self.add(
            input_triangle_update_p1,
            x_label_update_p1,
            graph_dot_update_p1,
            v_line_update_p1,
            h_line_update_p1,
            output_triangle_update_p1,
            output_label_update_p1,
        )
        self.play(
            input_tracker_p1.set_value, 5,
            run_time=6,
            rate_func=there_and_back
        )
        # Animacion del punto b
        self.play(
            DrawBorderThenFill(input_triangle_p2, run_time=1),
            Write(x_label_p2),
            ShowCreation(v_line_p2),
            GrowFromCenter(graph_dot_p2),
        )
        self.add_foreground_mobject(graph_dot_p2)
        self.play(
            ShowCreation(h_line_p2),
            Write(output_label_p2),
            DrawBorderThenFill(output_triangle_p2, run_time=1)
        )
        self.add(
            input_triangle_update_p2,
            x_label_update_p2,
            graph_dot_update_p2,
            v_line_update_p2,
            h_line_update_p2,
            output_triangle_update_p2,
            output_label_update_p2,
        )
        self.play(
            input_tracker_p2.set_value, 8,
            run_time=6,
            rate_func=there_and_back
        )
        self.play(
                FadeOut(x_label_p1),
                FadeOut(output_label_p1),
                FadeOut(x_label_p2),
                FadeOut(output_label_p2),
                )
        ###################
        self.graph = graph
        linea_x_b = DashedLine(self.coords_to_point(0,0),self.coords_to_point(get_x_value_p2(),0)).set_stroke(YELLOW,7)
        linea_x_a = DashedLine(self.coords_to_point(0,0),self.coords_to_point(get_x_value_p1(),0)).set_stroke(YELLOW,7)
        linea_f_b = DashedLine(self.coords_to_point(0,0),self.coords_to_point(0,get_y_value_p2())).set_stroke(YELLOW,7)
        linea_f_a = DashedLine(self.coords_to_point(0,0),self.coords_to_point(0,get_y_value_p1())).set_stroke(YELLOW,7)
        llave1 = Brace(Line(self.coords_to_point(1.5, 0),self.coords_to_point(3.5, 0)),DOWN)
        textollave1= llave1.get_tex("b-a")
        llave2 = Brace(Line(self.coords_to_point(0, get_y_value_p1()),self.coords_to_point(0,get_y_value_p2())),LEFT)
        textollave2= llave2.get_tex("f(b)-f(a)")
        self.play(ShowCreationThenDestruction(linea_x_b),submobject_mode="lagged_start",run_time=2)
        self.play(ShowCreationThenDestruction(linea_x_a),submobject_mode="lagged_start",run_time=1.5)
        self.play(GrowFromCenter(llave1),Write(textollave1))
        self.wait()
        self.play(ShowCreationThenDestruction(linea_f_b),submobject_mode="lagged_start",run_time=2)
        self.play(ShowCreationThenDestruction(linea_f_a),submobject_mode="lagged_start",run_time=1.5)
        self.play(GrowFromCenter(llave2),Write(textollave2))
        self.wait()
        pendiente_recta = self.get_secant_slope_group(
            1.9, recta, dx = 1.4,
            df_label = "\\Delta y",
            dx_label = "\\Delta x",
            dx_line_color = PURPLE,
            df_line_color= ORANGE,
            include_secant_line=False,
            )
        grupo_secante = self.get_secant_slope_group(
            1.5, graph, dx = 2,
            df_label = "f(b)-f(a)",
            dx_label = "b-a",
            dx_line_color = TT_FONDO_ROSA,
            df_line_color= TT_FONDO_VERDE,
            secant_line_color = RED,
            background_stroke_width=4
        )
        grupo_secantep = self.get_secant_slope_group(
            1.5, graph, dx = 2,
            df_label = None,
            dx_label = None,
            dx_line_color = PURPLE,
            df_line_color=ORANGE,
            secant_line_color = RED,
        )
        self.wait()
        self.play(ReplacementTransform(llave1,grupo_secante.dx_line),ReplacementTransform(llave2,grupo_secante.df_line),run_time=1.5)
        self.play(*[ReplacementTransform(textollave1[i],grupo_secante.dx_label[i],run_time=1.5) for i in range(len(textollave1))])
        self.play(*[ReplacementTransform(textollave2[i],grupo_secante.df_label[i],run_time=1.5) for i in range(len(textollave2))])
        self.wait()
        self.play(ShowCreation(grupo_secante.secant_line))
        self.remove(grupo_secantep)
        self.play(FadeOut(llave1),FadeOut(llave2))
        self.wait()
        punto_fijo = Dot(color=GRAY)
        punto_fijo.move_to(get_graph_point_p1())
        self.add_foreground_mobject(punto_fijo)
        self.play(GrowFromCenter(punto_fijo))
        self.wait()
        start_dx = grupo_secante.kwargs["dx"]
        start_x = grupo_secante.kwargs["x"]
        def update_func_0(group, alpha):
            dx = interpolate(start_dx, 4, alpha)
            x = interpolate(start_x, 1.5, alpha)
            kwargs = dict(grupo_secante.kwargs)
            kwargs["dx"] = dx
            kwargs["x"] = x
            new_group = self.get_secant_slope_group(**kwargs)
            Transform(group, new_group).update(1)
            return group
        def update_func_1(group, alpha):
            dx = interpolate(start_dx, 0.001, alpha)
            x = interpolate(start_x, 1.5, alpha)
            kwargs = dict(grupo_secante.kwargs)
            kwargs["dx"] = dx
            kwargs["x"] = x
            new_group = self.get_secant_slope_group(**kwargs)
            Transform(group, new_group).update(1)
            return group
        self.add(
            input_triangle_update_p2,
            graph_dot_update_p2,
            v_line_update_p2,
            h_line_update_p2,
            output_triangle_update_p2,
        )
        self.play(
            UpdateFromAlphaFunc(
                grupo_secante, update_func_0,
                run_time=3,rate_func = there_and_back
            ),
            input_tracker_p2.set_value, 5.5,
            run_time=3,rate_func = there_and_back
        )
        flecha_sub= Arrow(RIGHT,LEFT*0.7)
        flecha_sub.next_to(llave1,0*DOWN)
        flecha_sub.shift(2.5*DOWN)
        self.play(GrowArrow(flecha_sub))
        formula = TexMobject("\\lim_{b\\to a}","{f(b)-f(a) ","\\over","b-a}","=","{d\\over dx} f(a)")
        formula.next_to(self.lin_h,DOWN,buff=SMALL_BUFF)
        formula.shift(RIGHT*3)
        self.play(Write(formula[0]),Write(formula[2]))
        self.play(ReplacementTransform(grupo_secante.dx_label[0].copy(),formula[3][0]),
        	ReplacementTransform(grupo_secante.dx_label[1].copy(),formula[3][1]),
        	ReplacementTransform(grupo_secante.dx_label[2].copy(),formula[3][2]),
        	run_time=1)
        self.play(ReplacementTransform(grupo_secante.df_label[0].copy(),formula[1][0]),
        	ReplacementTransform(grupo_secante.df_label[1].copy(),formula[1][1]),
        	ReplacementTransform(grupo_secante.df_label[2].copy(),formula[1][2]),
        	ReplacementTransform(grupo_secante.df_label[3].copy(),formula[1][3]),
        	ReplacementTransform(grupo_secante.df_label[4].copy(),formula[1][4]),
        	ReplacementTransform(grupo_secante.df_label[5].copy(),formula[1][5]),
        	ReplacementTransform(grupo_secante.df_label[6].copy(),formula[1][6]),
        	ReplacementTransform(grupo_secante.df_label[7].copy(),formula[1][7]),
        	ReplacementTransform(grupo_secante.df_label[8].copy(),formula[1][8]),
        	run_time=1)
        bta = TexMobject("b\\to a")
        bta.next_to(flecha_sub,DOWN,buff=SMALL_BUFF)
        self.play(Write(bta))
        self.wait()
        self.play(
            UpdateFromAlphaFunc(
                grupo_secante, update_func_1,
                run_time=6
            ),
            input_tracker_p2.set_value, 1.5,
            run_time=6
        )
        self.wait()
        self.play(FadeOut(flecha_sub),FadeOut(bta))
        derivada = grupo_secante.secant_line.copy().set_color(YELLOW)
        self.play(ShowCreationThenDestruction(derivada))
        self.play(ShowCreationThenDestruction(derivada.rotate(PI)))
        self.wait()
        for_pend = TexMobject("{\\Delta y","\\over","\\Delta x}").next_to(formula[4],RIGHT,buff=SMALL_BUFF).shift(0.05*UP)
        self.play(Write(pendiente_recta))
        self.play(Write(formula[4]),
            ReplacementTransform(pendiente_recta.df_label[0].copy(),for_pend[0][0]),
            ReplacementTransform(pendiente_recta.df_label[1].copy(),for_pend[0][1]),
            ReplacementTransform(pendiente_recta.dx_label[0].copy(),for_pend[2][0]),
            ReplacementTransform(pendiente_recta.dx_label[1].copy(),for_pend[2][1]),
                Write(for_pend[1]))
        self.wait()
        self.animate_secant_slope_group_change(
            pendiente_recta, target_x=1,run_time=1.5
            )
        self.animate_secant_slope_group_change(
            pendiente_recta, target_x=2,run_time=1.5
            )
        self.animate_secant_slope_group_change(
            pendiente_recta, target_dx=2,target_x=None,rate_func=there_and_back,run_time=1.5
            )
        self.wait()
        self.play(ReplacementTransform(for_pend[0][0],formula[5][0]),
                  ReplacementTransform(for_pend[2][0],formula[5][2]),
                  ReplacementTransform(for_pend[1],formula[5][1]),
                  ReplacementTransform(for_pend[2][1],formula[5][3]),
                  ReplacementTransform(for_pend[0][1],formula[5][4:]),
            )
        self.wait()
        #self.remove(*[objecto for objecto in [grupo_secante,pendiente_recta]])

    def otra_definicion(self):
    	randy = Randolph()
    	randy[4].set_color(RED)
    	randy.to_corner(DOWN+LEFT)
    	randy.shift(2*RIGHT)
    	words = TexMobject("\\lim_{h\\to 0}\\frac{f(x+h)-f(x)}{h}","?")
    	words[1].set_color(RED_B)
    	words[1].scale(2.5).shift(RIGHT*0.5)
    	self.play(FadeIn(randy))
    	self.play(PiCreatureSays(
            randy, words, 
            bubble_kwargs = {"height" : 3, "width" : 4},
        ))
    	self.play(Blink(randy))
    	self.wait()

class SecanteDerivadaV2(GraphScene):
    CONFIG = {
        "y_max": 8,
        "y_axis_height": 5,
    }

    def construct(self):
        self.add_title()
        self.show_function_graph()
        #self.otra_definicion()

    def add_title(self):
        title = self.title = TextMobject("\\underline{\\sc Visualizaci\\'on de la Derivada}")
        title.to_edge(UP)
        self.add_foreground_mobject(title)
        h_line = Line(LEFT, RIGHT)
        h_line.set_height(FRAME_WIDTH - 2 * LARGE_BUFF)
        h_line.next_to(title, DOWN)
        h_line.set_stroke(WHITE,3)
        title.to_edge(UP+LEFT)
        title.shift(RIGHT)

        self.add(title)
        self.lin_h = h_line

    def show_function_graph(self):
        self.setup_axes()

        def func(x):
            return 0.1 * (x + 3-5) * (x - 3-5) * (x-5) + 5

        def rect(x):
            return 2.775*(x-1.5)+3.862
        recta = self.get_graph(rect,x_min=-1,x_max=5)
        graph = self.get_graph(func,x_min=0.2,x_max=9)
        graph.set_color(TT_AZUL_T)
        p1 = ValueTracker(1.5)

        def get_x_value(input_tracker):
            return input_tracker.get_value()

        def get_y_value(input_tracker):
            return graph.underlying_function(get_x_value(input_tracker))

        def get_x_point(input_tracker):
            return self.coords_to_point(get_x_value(input_tracker), 0)

        def get_y_point(input_tracker):
            return self.coords_to_point(0, get_y_value(input_tracker))

        def get_graph_point(input_tracker):
            return self.coords_to_point(get_x_value(input_tracker), get_y_value(input_tracker))

        def get_v_line(input_tracker):
            return DashedLine(get_x_point(input_tracker), get_graph_point(input_tracker), stroke_width=2)

        def get_h_line(input_tracker):
            return DashedLine(get_graph_point(input_tracker), get_y_point(input_tracker), stroke_width=2)

        # Triangulo a
        input_triangle_p1 = RegularPolygon(n=3, start_angle=TAU / 4)
        output_triangle_p1 = RegularPolygon(n=3, start_angle=0)
        for triangle in input_triangle_p1, output_triangle_p1:
            triangle.set_fill(WHITE, 1)
            triangle.set_stroke(width=0)
            triangle.scale(0.1)
        # Entradas y salidas del triangulo a
        input_triangle_update_p1 = ContinualUpdate(
            input_triangle_p1, lambda m: m.move_to(get_x_point(p1), DOWN)
        )
        output_triangle_update_p1 = ContinualUpdate(
            output_triangle_p1, lambda m: m.move_to(get_y_point(p1), LEFT)
        )
        # Etiqueas y salidas del punto a
        x_label_p1 = TexMobject("a")
        x_label_update_p1 = ContinualUpdate(
            x_label_p1, lambda ma: ma.next_to(input_triangle_p1, DOWN, SMALL_BUFF)
        )

        output_label_p1 = TexMobject("f(a)")
        output_label_update_p1 = ContinualUpdate(
            output_label_p1, lambda ma: ma.next_to(
                output_triangle_p1, LEFT, SMALL_BUFF)
        )
        # V_lines de a
        v_line_p1 = get_v_line(p1)
        v_line_update_p1 = ContinualUpdate(
            v_line_p1, lambda vla: Transform(vla, get_v_line(p1)).update(1)
        )
        # h_lines de a
        h_line_p1 = get_h_line(p1)
        h_line_update_p1 = ContinualUpdate(
            h_line_p1, lambda hla: Transform(hla, get_h_line(p1)).update(1)
        )
        # Animacion del punto a
        graph_dot_p1 = Dot(color=TT_SIMBOLO)
        graph_dot_update_p1 = ContinualUpdate(
            graph_dot_p1, lambda ma: ma.move_to(get_graph_point(p1))
        )
        self.play(
            ShowCreation(graph),
        )
        # Animacion del punto a
        self.play(
            DrawBorderThenFill(input_triangle_p1, run_time=1),
            Write(x_label_p1),
            ShowCreation(v_line_p1),
            GrowFromCenter(graph_dot_p1),
        )
        self.add_foreground_mobject(graph_dot_p1)
        self.play(
            ShowCreation(h_line_p1),
            Write(output_label_p1),
            DrawBorderThenFill(output_triangle_p1, run_time=1)
        )
        self.add(
            input_triangle_update_p1,
            x_label_update_p1,
            graph_dot_update_p1,
            v_line_update_p1,
            h_line_update_p1,
            output_triangle_update_p1,
            output_label_update_p1,
        )
        self.play(
            p1.set_value, 5,
            run_time=6,
            rate_func=there_and_back
        )
