from big_ol_pile_of_manim_imports import *

class EscenaIntegral(GraphScene):
    CONFIG = {
        "lower_bound" : 1,
        "upper_bound" : 9,
        "lower_bound_color" : RED_B,
        "upper_bound_color" : GREEN,
        "n_riemann_iterations" : 3,
        "default_riemann_start_color": PURPLE_B,
        "default_riemann_end_color": RED_B,
        "y_axis_label": "$y$",
        "graph_origin": 3 * DOWN + 4.7 * LEFT,
    }

    def construct(self):
        self.setup_axes()
        self.mostrar_grafica()
        #self.mostrar_randolf()
        #self.desglose_integral()
        #self.mostrar_randolf2()

    def setup_axes(self):
        # Linea por defecto
        GraphScene.setup_axes(self) 
        # Parámetros de las etiquetas de los ejes
        #   Para x
        et_x_inicial = 1
        et_x_final = 10
        pasos_x = 1
        #   Para y
        et_y_inicial = 1
        et_y_final = 10
        pasos_y = 1
        # Posición de las etiquetas (siempre se definen antes de add_numbers)
        #   Para x
        self.x_axis.label_direction = DOWN #DOWN está por defecto así que se puede obviar
        #   Para y
        self.y_axis.label_direction = LEFT
        # Adición de las etiquetas
        #   Para x
        self.x_axis.add_numbers(*range(
                                        et_x_inicial,
                                        et_x_final+pasos_x,
                                        pasos_x
                                    ))
        #   Para y
        self.y_axis.add_numbers(*range(
                                        et_y_inicial,
                                        et_y_final+pasos_y,
                                        pasos_y
                                    ))
        #---------
        #   Animación Write (se puede modificar a Show...)
        self.play(
            Write(self.x_axis),
            Write(self.y_axis)
        )
        

    def mostrar_grafica(self):
        integral = TexMobject("\\lim_{n\\to\\infty}\\sum_{i=1}^{n}f\\left(a+{b-a\\over n}i\\right){b-a\\over n}")
        for color in [13,17,24]:
            integral[color].set_color(RED_B)
        for color in [15,22]:
            integral[color].set_color(PURPLE_B)
        for color in [3,6,19,26]:
            integral[color].set_color(TEAL_B)
        for color in [8,20]:
            integral[color].set_color(YELLOW_B)
        simint = TexMobject("=\\int_a^b f(x)dx")
        simint[2].set_color(PURPLE_B)
        simint[3].set_color(RED_B)
        integral.to_edge(UP)
        simint.next_to(integral,RIGHT,buff=SMALL_BUFF).shift(0.1*UP)
        self.simint=simint
        graph = self.get_graph(
            lambda x : x,
        )
        self.integral = integral
        self.play(Write(integral),Write(simint))
        self.wait()
        self.play(FadeOut(simint))
        self.play(
                    self.integral.scale, 1/1.2,
                    self.integral.shift, LEFT*1.7+UP*0.5,
            )
        self.play(FadeOut(self.integral[0:6]))
        fx=TexMobject("f(x)=x").next_to(self.integral,RIGHT,buff=1.5).match_color(graph)
        self.play(Write(fx))
        self.graph = graph
        self.play(ShowCreation(graph))
        self.wait()
        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        p1=ValueTracker(2)
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
        x_label_p1 = TexMobject("x")
        x_label_update_p1 = ContinualUpdate(
            x_label_p1, lambda ma: ma.next_to(input_triangle_p1, DOWN, SMALL_BUFF*7)
        )

        output_label_p1 = TexMobject("f(x)=")
        output_label_update_p1 = ContinualUpdate(
            output_label_p1, lambda ma: ma.next_to(
                output_triangle_p1, LEFT, SMALL_BUFF*7.5)
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
            p1.set_value, 2,
            run_time=2,
        )
        self.wait()
        self.play(
            p1.set_value, 3,
            run_time=2,
        )
        self.wait()
        self.play(
            p1.set_value, 4,
            run_time=2,
        )
        self.wait()
        self.play(
            p1.set_value, 7,
            run_time=2,
        )
        self.wait()
        self.play(
            p1.set_value, 2,
            run_time=2,
        )
        self.remove(
            h_line_p1,
            v_line_p1
            )
        self.add(
            h_line_p1,
            v_line_p1
            )
        self.play(
            *[FadeOut(
                objeto
                )
            for objeto in [
            input_triangle_p1,
            x_label_p1,
            graph_dot_p1,
            output_label_p1,
            output_triangle_p1,
            h_line_p1,
            v_line_p1
                ]
            ]
            )
        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        #Lineas---------------------------
        def lineaDash(xi,yi,xf,yf):
            linea = DashedLine(self.coords_to_point(xi,yi),self.coords_to_point(xf,yf))
            return linea
        
        self.play(
                *[ShowCreationThenDestruction(lineaDash(0,i,i,i),
                submobject_mode = "lagged_start")for i in range(1,10)],
                *[ShowCreationThenDestruction(lineaDash(i,0,i,i),
                submobject_mode = "lagged_start")for i in range(1,10)],
                run_time=3
                )
        self.play(FadeOut(fx))
        #---------------------------------
        pt1 = self.coords_to_point(1,0)
        pt2 = self.coords_to_point(1,1)
        pt3 = self.coords_to_point(9,9)
        pt4 = self.coords_to_point(9,0)
        pt5 = self.coords_to_point(9,1)
        pt6 = self.coords_to_point(1,9)
        pt7 = self.coords_to_point(1,5)
        pt8 = self.coords_to_point(5,9)
        pt9 = self.coords_to_point(5,5)
        pt10 = self.coords_to_point(1,3.666)
        pt11 = self.coords_to_point(3.666,3.666)
        pt12 = self.coords_to_point(3.666,6.333)
        pt13 = self.coords_to_point(6.333,6.333)
        pt14 = self.coords_to_point(6.333,9)
        #pt = self.coords_to_point(,)
        #pt = self.coords_to_point(,)
        triangulo1=Polygon(pt2,pt3,pt5).set_stroke(RED,11)
        triangulo2=Polygon(pt2,pt6,pt3).set_stroke(YELLOW,9)
        triangulo3_1=Polygon(pt2,pt7,pt9).set_stroke(YELLOW,7)
        triangulo3_2=Polygon(pt9,pt8,pt3).set_stroke(YELLOW,7)
        triangulo4_1=Polygon(pt2,pt10,pt11).set_stroke(YELLOW,9)
        triangulo4_2=Polygon(pt11,pt12,pt13).set_stroke(YELLOW,9)
        triangulo4_3=Polygon(pt13,pt14,pt3).set_stroke(YELLOW,9)
        #triangulo_=Polygon(pt,pt,pt).set_stroke(YELLOW,9)
        self.triangulo2=triangulo2
        self.triangulo3_1=triangulo3_1
        self.triangulo3_2=triangulo3_2
        self.triangulo4_1=triangulo4_1
        self.triangulo4_2=triangulo4_2
        self.triangulo4_3=triangulo4_3
        rectangulo1=Polygon(pt1,pt2,pt5,pt4).set_stroke(BLUE,11)
        cuadro1=Polygon(pt1,pt2,pt3,pt4)
        linea_a=Line(self.coords_to_point(1,0),self.coords_to_point(1,1)).set_stroke(RED_B,8)
        linea_b=Line(self.coords_to_point(9,0),self.coords_to_point(9,9)).set_stroke(PURPLE_B,8)
        self.linea_a=linea_a
        self.linea_b=linea_b
        self.cuadro1=cuadro1
        #cuadro1.set_fill(GREEN,opacity=1)
        cuadro1.set_stroke(GREEN,0)
        self.wait()
        self.play(ShowCreation(linea_a))
        self.wait()
        self.play(ShowCreation(linea_b))
        #self.play(ShowCreation(cuadro1[0]),run_time=3, rate_func= lambda w: w)
        self.wait()
        self.play(linea_a.set_stroke,None,3,
                  linea_b.set_stroke,None,3,)
        self.play(cuadro1.set_fill, TEAL_E, 0.2, run_time=1)
        self.wait()
        self.play(ShowCreationThenDestruction(rectangulo1,rate_func=lambda w: w),run_time=2.5)
        self.wait()
        self.play(ShowCreationThenDestruction(triangulo1,rate_func= lambda w: w),run_time=2.5)
        self.wait()

        AreaAprox = TexMobject("=","A_{aprox}").scale(1/1.5).next_to(self.integral,RIGHT,buff=SMALL_BUFF)
        self.wait()
        self.play(Write(AreaAprox))
        self.wait()
        self.AreaReal=TexMobject("A_{real}=40[u^2]")
        self.AreaReal.scale(0.8)
        self.AreaReal.to_edge(UP+RIGHT)
        Flecha = Arrow(self.AreaReal.get_bottom(),self.coords_to_point(7,4))
        self.play(Write(self.AreaReal),GrowArrow(Flecha))
        self.wait()
        self.play(FadeOut(Flecha))
        self.AreaAprox=AreaAprox
        #Sacar ejes
        self.play(FadeOut(self.x_axis[3]),FadeOut(self.y_axis[3]))
        self.wait()
    #def mostrar_xy(self):
        

    def mostrar_randolf(self):
        randy = Alex()
        randy.to_corner(DOWN+LEFT)
        randy.shift(2*RIGHT)
        words = TextMobject("Yo s\\'olo s\\'e calcular\\\\ \\'areas de rect\\'angulos")
        words.scale(0.7)

        self.play(FadeIn(randy))
        self.play(OmegaCreatureDice(
            randy, words, 
            bubble_kwargs = {"height" : 3, "width" : 4},
            target_mode="speaking"
        ))
        self.play(Blink(randy))
        self.wait(2)
        self.play(Blink(randy))
        self.wait(0.5)
        self.play(RemueveDialogo(randy))
        self.play(FadeOut(randy))

    def desglose_integral(self):
        kwargs = {
            "x_min" : self.lower_bound,
            "x_max" : self.upper_bound,
            "fill_opacity" : 0.75,
            "stroke_width" : 0.5,
        }
        ##################################
        AreaAprox=self.AreaAprox
        ################################
        # Animacion de recuadro destruction
        def recuadroObjeto(objeto,tiempo):
            return self.play(ShowCreationThenDestruction(SurroundingRectangle(objeto,buff=0).match_color(objeto)),run_time=tiempo)
        #################################
        #low_opacity = 0.25
        start_rect_index = 1
        num_shown_sum_steps = 3
        last_rect_index = start_rect_index + num_shown_sum_steps + 1

        self.rect_list = self.get_riemann_rectangles_list(
            self.graph, 10, input_sample_type="right",  max_dx=8,
            start_color= RED_B, power_base=2,
            end_color= PURPLE_B,**kwargs
        )
        self.rect_listb = self.get_riemann_rectangles_list(
            self.graph, 2, input_sample_type="right",  max_dx=8,
            start_color= RED_B, power_base=3,
            end_color= PURPLE_B,**kwargs
        )
        rects = self.rects = self.rect_list[0]
        rects.save_state()

        #start_rect = rects[start_rect_index]
        #f_brace = Brace(start_rect, LEFT, buff = 0)
        #dx_brace = Brace(start_rect, DOWN, buff = 0)
        #f_brace.label = TexMobject("f","(*)").next_to(f_brace,LEFT,buff=0.1)
        #dx_brace.label = TextMobject("${b-a\\over n}$").next_to(dx_brace,DOWN,buff=0.1)

        flat_rects = self.get_riemann_rectangles(
            self.get_graph(lambda x : 0), dx = 8, **kwargs
        )
        self.formulas_sum= TexMobject(
            "\\sum_{i=1}^{1}f\\left(1+{9-1\\over 1}i\\right){9-1\\over 1}",
            "\\sum_{i=1}^{2}f\\left(1+\\frac{9-1}{2}i\\right){9-1\\over 2}",
            "\\sum_{i=1}^{3}f\\left(1+\\frac{9-1}{3}i\\right){9-1\\over 3}",
            ).scale(1/1.2)
        #-------------------------------
        for f in range(0,len(self.formulas_sum)):
            for color in [7,11,18]:
                self.formulas_sum[f][color].set_color(RED_B)
            for color in [9,16]:
                self.formulas_sum[f][color].set_color(PURPLE_B)
            for color in [0,13,20]:
                self.formulas_sum[f][color].set_color(TEAL_B)
            for color in [2,14]:
                self.formulas_sum[f][color].set_color(YELLOW_B)
        #-------------------------------
        formula_1= TexMobject(
            "(1+8\\cdot 1)\\cdot 8","=","72[u^2]"
            )
        formula_2= TexMobject(
            "(1+4\\cdot 1)\\cdot 4+(1+4\\cdot 2)\\cdot 4",
            "=","56[u^2]"
            )
        formula_3= TexMobject(
            "(1+2.\\overline{6}\\cdot 1)\\cdot 2.\\overline{6}+(1+2.\\overline{6}\\cdot 2)\\cdot 2.\\overline{6}+(1+2.\\overline{6}\\cdot 3)\\cdot 2.\\overline{6}",
            "=","50.\\overline{6}[u^2]")
        part_n = [1,2,3]
        nums = TexMobject("n=1","n=2","n=3")
        for col in range(0,len(nums)):
            nums[col][0].set_color(TEAL_B)
        # n=1
        # Cambia n por n=1
        nums[0].scale(0.8).next_to(self.AreaReal,DOWN,buff=SMALL_BUFF*3)
        self.play(ReplacementTransform(self.integral[6].copy(),nums[0][0]),
                  ReplacementTransform(self.integral[19].copy(),nums[0][0]),
                  ReplacementTransform(self.integral[26].copy(),nums[0][0]),
                  run_time=3)
        self.wait(1.5)
        self.wait(0.3)
        self.play(Write(nums[0][1:]))
        self.wait(1.5)
        # Posiciona formula suma n=1
        self.formulas_sum[0].next_to(self.integral,DOWN,buff=SMALL_BUFF*2).shift(RIGHT*0.4)
        # Animacion de bajar formula de suma
        self.play(*[ReplacementTransform(self.integral[i+6].copy(),self.formulas_sum[0][i])
                    for i in range(len(self.formulas_sum[0]))],run_time=2)
        # Linea base n=1
        lineai = Line(self.coords_to_point(1,0),self.coords_to_point(1+(9-1)/1,0))
        lineai.set_fill(opacity=0)
        # Brazo n=1
        brace_n = Brace(lineai,DOWN,buff=0.1)
        # Base abajo del brazo n=1
        bman = TexMobject("8[u]").set_fill(opacity=0)
        self.add(bman)
        bman.move_to(self.formulas_sum[0][-5:])
        # Definicion de triangulos delimitadores
        tri1 = RegularPolygon(n=3, start_angle=TAU / 4)
        tri8 = RegularPolygon(n=3, start_angle=TAU / 4)
        for triangulo in [tri1,tri8]:
            triangulo.set_fill(WHITE, 1)
            triangulo.set_stroke(width=0)
            triangulo.scale(0.1)
        tri1.move_to(self.coords_to_point(1,0),UP)
        tri8.move_to(self.coords_to_point(9,0),UP)
        self.wait(1.5)
        # Agrega el brazo n=1
        self.play(GrowFromCenter(brace_n))
        self.wait(1.5)
        # Animacion de bajar la base abajo del brazo n=1
        cuadror=SurroundingRectangle(self.formulas_sum[0][-5:])
        self.play(ShowCreationThenDestruction(cuadror))
        self.wait(1.5)
        self.play(bman.set_fill,WHITE,1,bman.next_to,brace_n,DOWN,bman.shift,0.007*LEFT+0.2*UP,run_time=3)
        self.wait()
        # Animacion de agregar triangulos
        self.play(
            DrawBorderThenFill(tri1),
            DrawBorderThenFill(tri8),
            run_time=1
            )
        # Sale el brazo y su texto
        self.play(FadeOut(bman),FadeOut(brace_n))
        self.wait(1.5)
        #Resaltado de i=1 y n=1
        self.play(
            self.formulas_sum[0][4].scale,1.2,
            self.formulas_sum[0][4].set_color,YELLOW,
            self.formulas_sum[0][0].scale,1.2,
            self.formulas_sum[0][0].set_color,YELLOW,
            run_time=0.5
            )
        self.wait(1.5)
        # Posicion de la suma desglozada abajo de la base
        formula_1.scale(0.8).next_to(self.coords_to_point(3.5,0),DOWN,buff= SMALL_BUFF*3).shift(RIGHT*1.5)
        formula_1[0][1].set_color(RED_B)
        formula_1[0][5].set_color(TEAL_B)
        suma1=TexMobject("88").set_fill(opacity=0)
        suma1[0].move_to(self.formulas_sum[0][9:14])
        suma1[1].move_to(self.formulas_sum[0][-5:])
        self.add(suma1)
        # Animacion de bajar numeros parentesis, i y agregar simbolos de multiplicacion
        self.play(ReplacementTransform(self.formulas_sum[0][6:9].copy(),formula_1[0][0:3]),
            ReplacementTransform(self.formulas_sum[0][14].copy(),formula_1[0][5]),
            ReplacementTransform(self.formulas_sum[0][15].copy(),formula_1[0][6]),
            Write(formula_1[0][4]),Write(formula_1[0][7]),run_time=3.5
                )
        self.wait(1.5)
        #Regresar de i=1 y n=1
        self.play(
            self.formulas_sum[0][4].scale,1/1.2,
            self.formulas_sum[0][4].set_color,WHITE,
            self.formulas_sum[0][0].scale,1/1.2,
            self.formulas_sum[0][0].set_color,TEAL_B,
            run_time=0.5
            )
        self.wait(1.5)
        # Bajar las bases b-a/n
        cuadror=SurroundingRectangle(self.formulas_sum[0][9:14])
        self.play(ShowCreationThenDestruction(cuadror))
        self.wait(1.5)
        self.play(ReplacementTransform(suma1[0],formula_1[0][3]),run_time=2)
        self.wait(1.5)
        cuadror=SurroundingRectangle(self.formulas_sum[0][-5:])
        self.play(ShowCreationThenDestruction(cuadror))
        self.wait(1.5)
        self.play(ReplacementTransform(suma1[1],formula_1[0][8]),run_time=2)
        self.wait(1.5)
        # Bajar el area aproximada
        self.play(ReplacementTransform(AreaAprox[0].copy(),formula_1[1]),
            ReplacementTransform(AreaAprox[1].copy(),formula_1[2]),run_time=2)
        self.wait(1.5)
        # Quitar fondo negro y quitar formula suma
        self.play(FadeOut(self.formulas_sum[0]))
        self.wait(1.5)
        # Sombra en suma desglozada
        self.play(formula_1.set_fill,None,0.5)
        self.wait(1.5)
        # Resalta numero 1 de 0->1
        self.play(
            formula_1[0][1].set_color, YELLOW,
            formula_1[0][1].set_fill, None,1,
            run_time=0.3
            )
        self.wait(1.5)
        # Añade/Destruye 0->1
        lineaSD = DashedLine(self.coords_to_point(0,0),self.coords_to_point(1,0))
        lineaSD.set_color(YELLOW).set_stroke(width=11)
        self.play(ShowCreationThenDestruction(
            lineaSD, 
            submobject_mode = "lagged_start"),
            run_time=2)
        # Normal numero 1
        self.play(
            formula_1[0][1].set_color, WHITE,
            formula_1[0][1].set_fill, None,0.5,
            run_time=0.3
            )
        self.wait(1.5)
        # Resalta numero 8*1 de 1->9
        self.play(
            formula_1[0][3:6].set_fill, YELLOW,1,
            run_time=0.3
            )
        self.wait(1.5)
        # Añade/Destruye 1->9
        lineaSD = DashedLine(self.coords_to_point(1,0),self.coords_to_point(9,0))
        lineaSD.set_color(YELLOW).set_stroke(width=11)
        self.play(ShowCreationThenDestruction(
            lineaSD, 
            submobject_mode = "lagged_start"),
            run_time=2)
        self.wait(1.5)
        # Regresa numero 8*1 de 1->9
        self.play(
            formula_1[0][3:6].set_fill, WHITE,0.5,
            run_time=0.3
            )
        self.wait(1.5)
        # Resalta funcion de 9->f(9)
        self.play(
            formula_1[0][0:7].set_fill, YELLOW,1,
            run_time=0.3
            )
        self.wait(1.5)
        # Añade/Destruye 9->f(9)
        lineaSD = DashedLine(self.coords_to_point(9,0),self.coords_to_point(9,9))
        lineaSD.set_color(YELLOW).set_stroke(width=11)
        self.play(ShowCreationThenDestruction(
            lineaSD, 
            submobject_mode = "lagged_start"),
            run_time=2)
        self.wait(1.5)
        #Regresa 
        self.play(
            formula_1[0][0:7].set_fill, WHITE,0.5,
            run_time=0.3
            )
        self.wait(1.5)
        #Resalta todo
        self.play(
            formula_1[0][0:9].set_fill, PURPLE_B,1,
            formula_1[1].set_fill, WHITE,1,
            formula_1[2].set_fill, WHITE,1,
            run_time=0.3
            )
        self.wait(1.5)
        # Cuadro Añade/Destruye
        self.play(ShowCreationThenDestruction(SurroundingRectangle(self.rect_list[0],buff=0).set_color(PURPLE_B)),run_time=1)
        self.wait(1.5)
        # Añadir rectangulo de n=1
        self.transform_between_riemann_rects(
            flat_rects, self.rect_list[0], dx=1,
            replace_mobject_with_target_in_scene = True,
            )
        # Resalta numero 8 de base
        self.wait(1.5)
        self.play(ShowCreationThenDestruction(self.triangulo2,rate_func= lambda w: w),run_time=2.5)
        self.wait(1.5)
        self.play(FadeOut(formula_1),FadeOut(self.rect_list[0]))
        self.wait(1.5)
        # Elimina triangulos
        self.play(
            FadeOut(tri1),FadeOut(tri8)
            )
        self.wait(1.5)
        ###########################################################################################
        ###########################################################################################
        #
        #                                   n=2
        #
        ###########################################################################################
        ###########################################################################################
        # Posicionar y remplazar n=1 por n=2
        nums[1].scale(0.8).next_to(self.AreaReal,DOWN,buff=SMALL_BUFF*3)
        self.play(ReplacementTransform(nums[0],nums[1]))
        self.wait(1.5)
        # Bajar formula de la suma general a la suma de n=2
        self.formulas_sum[1].next_to(self.integral,DOWN,buff=SMALL_BUFF*2).shift(RIGHT*0.4)
        self.play(*[ReplacementTransform(self.integral[i+6].copy(),self.formulas_sum[1][i])
                    for i in range(len(self.formulas_sum[1]))],run_time=2)
        self.wait(1.5)
        # Linea fantasma de base n=2
        lineai = Line(self.coords_to_point(1,0),self.coords_to_point(1+(9-1)/2,0))
        lineai.set_fill(opacity=0)
        lineai2 = Line(self.coords_to_point(5,0),self.coords_to_point(9,0))
        lineai2.set_fill(opacity=0)
        # Brazo de n=2
        brace_n = Brace(lineai,DOWN)
        brace_n2 = Brace(lineai2,DOWN)
        # Texto de n=2
        bman = TexMobject("4[u]").set_fill(opacity=0)
        bman2 = TexMobject("4[u]").set_fill(opacity=0)
        self.add(bman,bman2)
        bman.move_to(self.formulas_sum[1][-5:])
        bman2.move_to(self.formulas_sum[1][-5:])
        self.play(GrowFromCenter(brace_n),GrowFromCenter(brace_n2))
        self.wait(1.5)
        # Definicion de triangulos delimitadores
        tri1 = RegularPolygon(n=3, start_angle=TAU / 4)
        tri5 = RegularPolygon(n=3, start_angle=TAU / 4)
        tri9 = RegularPolygon(n=3, start_angle=TAU / 4)
        for triangulo in [tri1,tri5,tri9]:
            triangulo.set_fill(WHITE, 1)
            triangulo.set_stroke(width=0)
            triangulo.scale(0.1)
        tri1.move_to(self.coords_to_point(1,0),UP)
        tri5.move_to(self.coords_to_point(5,0),UP)
        tri9.move_to(self.coords_to_point(9,0),UP)
        # Animacion de añadir triangulos
        self.play(
            *[DrawBorderThenFill(triangulo)for triangulo in (tri1,tri5,tri9)]
            )
        self.wait(1.5)
        # Animar cuadro al rededor de base
        self.play(ShowCreationThenDestruction(SurroundingRectangle(self.formulas_sum[1][-5:])))
        self.wait(1.5)
        # Animacion de bajar la base n=2
        self.play(bman.set_fill,WHITE,1,bman.next_to,brace_n,DOWN,bman.shift,0.007*LEFT,run_time=3)
        self.wait(1.5)
        self.play(bman2.set_fill,WHITE,1,bman2.next_to,brace_n2,DOWN,bman2.shift,0.007*LEFT,run_time=3)
        self.wait(1.5)
        # Salida de la base y el brazo n=2
        self.play(FadeOut(bman),FadeOut(brace_n),FadeOut(bman2),FadeOut(brace_n2))
        self.wait(1.5)
        #Resaltado de i=1 y n=1
        self.play(
            self.formulas_sum[1][4].scale,1.2,
            self.formulas_sum[1][4].set_color,YELLOW,
            self.formulas_sum[1][0].scale,1.2,
            self.formulas_sum[1][0].set_color,YELLOW,
            run_time=0.5
            )
        self.wait(1.5)
        # Posicionar la suma desglozada
        formula_2.scale(0.8).next_to(self.coords_to_point(4.5,0),DOWN,buff= SMALL_BUFF*3).shift(RIGHT*1.2)
        formula_2[0][1].set_color(RED_B)
        formula_2[0][5].set_color(YELLOW_B)
        formula_2[0][11].set_color(RED_B)
        formula_2[0][15].set_color(TEAL_B)
        suma2=TexMobject("4444").set_fill(opacity=0)
        suma2[0].move_to(self.formulas_sum[0][9:14])
        suma2[1].move_to(self.formulas_sum[0][-5:])
        suma2[2].move_to(self.formulas_sum[0][9:14])
        suma2[3].move_to(self.formulas_sum[0][-5:])
        self.add(suma2)
        # Bajar los parentesis e i con i=1
        # i=1
        self.play(ReplacementTransform(self.formulas_sum[1][6:9].copy(),formula_2[0][0:3]), # (1+
            ReplacementTransform(self.formulas_sum[1][14].copy(),formula_2[0][5]), # i
            ReplacementTransform(self.formulas_sum[1][15].copy(),formula_2[0][6]), # )
            Write(formula_2[0][4]),Write(formula_2[0][7]),run_time=3.5
                )
        self.wait(1.5)
        # Bajar los parentesis e i con i=2
        # i=2
        self.play(ReplacementTransform(self.formulas_sum[1][6:9].copy(),formula_2[0][10:13]), # (1+
            ReplacementTransform(self.formulas_sum[1][14].copy(),formula_2[0][15]), # i
            ReplacementTransform(self.formulas_sum[1][15].copy(),formula_2[0][16]), # )
            *[Write(formula_2[0][j])for j in [9,14,17]],run_time=3.5
            #Write(formula_2[0][4]),Write(formula_2[0][7]),Write(formula_2[0][9]),Write(formula_2[0][15]),Write(formula_2[0][17])
                )
        self.wait(1.5)
        #Regresar de i=1 y n=1
        self.play(
            self.formulas_sum[1][4].scale,1/1.2,
            self.formulas_sum[1][4].set_color,WHITE,
            self.formulas_sum[1][0].scale,1/1.2,
            self.formulas_sum[1][0].set_color,TEAL_B,
            run_time=0.5
            )
        self.wait(1.5)
        # Bajar bases
        # Resaltar cuadro
        cuadrob1=SurroundingRectangle(self.formulas_sum[0][9:14])
        cuadrob2=SurroundingRectangle(self.formulas_sum[0][-5:])
        self.play(ShowCreationThenDestruction(cuadrob1))
        self.wait()
        self.play(ReplacementTransform(suma2[0],formula_2[0][3]),run_time=2)
        self.wait()
        self.play(ShowCreationThenDestruction(cuadrob2))
        self.wait()
        self.play(ReplacementTransform(suma2[1],formula_2[0][8]),run_time=2)
        self.wait()
        self.play(ShowCreationThenDestruction(cuadrob1))
        self.wait()
        self.play(ReplacementTransform(suma2[2],formula_2[0][13]),run_time=2)
        self.wait()
        self.play(ShowCreationThenDestruction(cuadrob2))
        self.wait()
        self.play(ReplacementTransform(suma2[3],formula_2[0][18]),run_time=2)
        self.wait()
        # Transformar area aproximada a valor numerico
        self.play(ReplacementTransform(AreaAprox[0].copy(),formula_2[1]),
            ReplacementTransform(AreaAprox[1].copy(),formula_2[2]),run_time=1.5)
        self.wait()
        
        # Sacar suma con n=2
        self.play(FadeOut(self.formulas_sum[1]))
        self.wait()
        # Oscurecer formula desglozada
        self.play(formula_2.set_fill,None,0.5)
        self.wait()
        # Resalta numero 1 de 0->1
        self.play(
            formula_2[0][1].set_fill, YELLOW,1,
            run_time=0.3
            )
        self.wait()
        # Añade/Destruye 0->1
        lineaSD = DashedLine(self.coords_to_point(0,0),self.coords_to_point(1,0))
        lineaSD.set_color(YELLOW).set_stroke(width=11)
        self.play(ShowCreationThenDestruction(
            lineaSD, 
            submobject_mode = "lagged_start"),
            run_time=2)
        self.wait()
        # Normal numero 1
        self.play(
            formula_2[0][1].set_fill, WHITE,0.5,
            run_time=0.3
            )
        self.wait()
        # Resalta numero 4*1 de 1->5
        self.play(
            formula_2[0][3:6].set_fill, YELLOW,1,
            run_time=0.3
            )
        self.wait()
        # Añade/Destruye 1->5
        lineaSD = DashedLine(self.coords_to_point(1,0),self.coords_to_point(5,0))
        lineaSD.set_color(YELLOW).set_stroke(width=11)
        self.play(ShowCreationThenDestruction(
            lineaSD, 
            submobject_mode = "lagged_start"),
            run_time=2)
        self.wait()
        # Regresa 4*1
        self.play(
            formula_2[0][3:6].set_fill, WHITE,0.5,
            run_time=0.3
            )
        self.wait()
        # Resalta funcion 5->5
        self.play(
            formula_2[0][0:7].set_fill, YELLOW,1,
            run_time=0.3
            )
        self.wait()
        # Añade/Destruye 5->5
        lineaSD = DashedLine(self.coords_to_point(5,0),self.coords_to_point(5,5))
        lineaSD.set_color(YELLOW).set_stroke(width=11)
        self.play(ShowCreationThenDestruction(
            lineaSD, 
            submobject_mode = "lagged_start"),
            run_time=2)
        self.wait()
        # Regresa 4*1
        self.play(
            formula_2[0][0:7].set_fill, WHITE,0.5,
            run_time=0.3
            )
        self.wait()
        # Resaltar area de primer cuadro
        self.play(
            formula_2[0][0:9].set_fill,RED_B,1,
            run_time=0.3
            )
        self.wait()
        # Convertir rectagulo 8*9 por 4*2[0]
        recuadroObjeto(self.rect_list[1][0],1)
        self.play(FadeIn(self.rect_list[1][0]))
        self.wait()
        ############################## Cuadro 2
        # Resalta numero 1 de 0->1
        self.play(
            formula_2[0][11].set_fill, YELLOW,1,
            run_time=0.3
            )
        self.wait()
        # Añade/Destruye 0->1
        lineaSD = DashedLine(self.coords_to_point(0,0),self.coords_to_point(1,0))
        lineaSD.set_color(YELLOW).set_stroke(width=11)
        self.play(ShowCreationThenDestruction(
            lineaSD, 
            submobject_mode = "lagged_start"),
            run_time=2)
        self.wait()
        # Normal numero 1
        self.play(
            formula_2[0][11].set_fill, WHITE,0.5,
            run_time=0.3
            )
        self.wait()
        # Resalta numero 4*1 de 1->5
        self.play(
            formula_2[0][13:16].set_fill, YELLOW,1,
            run_time=0.3
            )
        self.wait()
        # Añade/Destruye 1->9
        lineaSD = DashedLine(self.coords_to_point(1,0),self.coords_to_point(9,0))
        lineaSD.set_color(YELLOW).set_stroke(width=11)
        self.play(ShowCreationThenDestruction(
            lineaSD, 
            submobject_mode = "lagged_start"),
            run_time=2)
        self.wait()
        # Regresa 4*2
        self.play(
            formula_2[0][13:16].set_fill, WHITE,0.5,
            run_time=0.3
            )
        self.wait()
        # Resalta funcion 9->f(9)
        self.play(
            formula_2[0][10:17].set_fill, YELLOW,1,
            run_time=0.3
            )
        self.wait()
        # Añade/Destruye 9->f(9)
        lineaSD = DashedLine(self.coords_to_point(9,0),self.coords_to_point(9,9))
        lineaSD.set_color(YELLOW).set_stroke(width=11)
        self.play(ShowCreationThenDestruction(
            lineaSD, 
            submobject_mode = "lagged_start"),
            run_time=2)
        self.wait()
        # Regresa funcion 9->f(9)
        self.play(
            formula_2[0][10:17].set_fill, WHITE,0.5,
            run_time=0.3
            )
        self.wait()
        # Resaltar formula desglozada gradiente
        self.play(
            formula_2[0].set_fill,None,1,
            formula_2[0][10:19].set_fill,PURPLE_B,1,
            formula_2[1:].set_fill,WHITE,1,
            run_time=0.3
            )
        self.wait()
        # Convertir rectagulo 8*9 por 4*2[1]
        recuadroObjeto(self.rect_list[1][1],1)
        self.play(FadeIn(self.rect_list[1][1]))
        self.wait()
        self.play(ShowCreationThenDestruction(self.triangulo3_1,rate_func= lambda w: w),
            ShowCreationThenDestruction(self.triangulo3_2,rate_func= lambda w: w),
            run_time=2.5)
        self.wait()
        self.play(FadeOut(formula_2),FadeOut(self.rect_list[1]))
        #quitar triangulos
        self.play(
            *[FadeOut(triangulo)for triangulo in (tri1,tri5,tri9)]
            )
        self.wait()
        ############################################################
        #
        #                       n=3
        ############################################################
        # Parametros: --------------------------------------------------------------
        #---------------------------------------------------------------------------
        nums[2].scale(0.8).next_to(self.AreaReal,DOWN,buff=SMALL_BUFF*3)
        self.formulas_sum[2].next_to(self.integral,DOWN,buff=SMALL_BUFF*2).shift(RIGHT*0.4)
        formula_3.scale(0.6).next_to(self.coords_to_point(4.5,0),DOWN,buff= SMALL_BUFF*3).shift(RIGHT*1)
        formula_3[0][1].set_color(RED_B)
        formula_3[0][17].set_color(RED_B)
        formula_3[0][33].set_color(RED_B)
        formula_3[0][8].set_color(YELLOW_B)
        formula_3[0][40].set_color(TEAL_B)
        lineai = Line(self.coords_to_point(1,0),self.coords_to_point(1+(9-1)/3,0)).set_fill(opacity=0)
        lineai2 = Line(self.coords_to_point(3.666,0),self.coords_to_point(6.333,0)).set_fill(opacity=0)
        lineai3 = Line(self.coords_to_point(6.333,0),self.coords_to_point(9,0)).set_fill(opacity=0)
        brace_n = Brace(lineai,DOWN)
        brace_n2 = Brace(lineai2,DOWN)
        brace_n3 = Brace(lineai3,DOWN)
        bman = TexMobject("2.\\overline{6}[u]").set_fill(opacity=0).move_to(self.formulas_sum[2][-5:])
        bman2=bman.copy()
        bman3=bman.copy()
        self.add(bman,bman2,bman3)
        #   Recuadro de base
        cuadroB=SurroundingRectangle(self.formulas_sum[2][-5:])
        #   Triangulos
        tri1 = RegularPolygon(n=3, start_angle=TAU / 4)
        tri3_6 = RegularPolygon(n=3, start_angle=TAU / 4)
        tri6_3 = RegularPolygon(n=3, start_angle=TAU / 4)
        tri9 = RegularPolygon(n=3, start_angle=TAU / 4)
        for triangulo in [tri1,tri3_6,tri6_3,tri9]:
            triangulo.set_fill(WHITE, 1)
            triangulo.set_stroke(width=0)
            triangulo.scale(0.1)
        tri1.move_to(self.coords_to_point(1,0),UP)
        tri3_6.move_to(self.coords_to_point(3.666,0),UP)
        tri6_3.move_to(self.coords_to_point(6.333,0),UP)
        tri9.move_to(self.coords_to_point(9,0),UP)
        #   DashedLines horizontales
        #       1->3.66
        linea1_a_3_6 = DashedLine(self.coords_to_point(0,0),self.coords_to_point(3.666,0))
        #       1->5.33
        linea1_a_6_3 = DashedLine(self.coords_to_point(0,0),self.coords_to_point(6.333,0))
        #       1->9
        linea1_a_9 = DashedLine(self.coords_to_point(0,0),self.coords_to_point(9,0))
        #   DashedLines verticales
        #       3.66->3.66
        linea3_6_a_3_6 = DashedLine(self.coords_to_point(3.666,0),self.coords_to_point(3.666,3.666))
        #       5.33->5.33
        linea6_3_a_6_3 = DashedLine(self.coords_to_point(6.333,0),self.coords_to_point(6.333,6.333))
        #       9->9
        linea9_a_9 = DashedLine(self.coords_to_point(9,0),self.coords_to_point(9,9))
        #           Propiedades
        for linea in [linea1_a_3_6,linea1_a_6_3,linea1_a_9,linea3_6_a_3_6,linea6_3_a_6_3,linea9_a_9]:
            linea.set_color(YELLOW).set_stroke(width=11)
        # Animaciones de resaltado: %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        def resaltado(formulaR):
            return self.play(formulaR.set_fill,YELLOW,1,run_time=0.3)
        def desresaltado(formulaR,objeto):
            return self.play(
                formulaR.match_color,objeto,
                formulaR.set_fill,None,0.5,
                run_time=0.3
                )
        #-----------------------------------------------------------------------------
        # Fin de parámetros: ---------------------------------------------------------
        # n=3
        self.play(
            ReplacementTransform(nums[1],nums[2]))
        self.wait()
        self.play(*[ReplacementTransform(self.integral[i+6].copy(),self.formulas_sum[2][i])
                    for i in range(len(self.formulas_sum[2]))],run_time=2)
        self.wait()
        # Añadir brazo
        self.play(GrowFromCenter(brace_n),GrowFromCenter(brace_n2),GrowFromCenter(brace_n3))
        self.wait()
        # Añadir triangulos
        self.play(
            *[DrawBorderThenFill(triangulo)for triangulo in (tri1,tri3_6,tri6_3,tri9)]
            )
        self.wait()
        # Show/Destruction recuadro base suma condensada
        self.play(ShowCreationThenDestruction(cuadroB))
        self.wait()
        # Bajar base abajo del brazo
        self.play(bman.set_fill,WHITE,1,bman.next_to,brace_n,DOWN,bman.shift,0.007*LEFT)
        self.wait()
        self.play(bman2.set_fill,WHITE,1,bman2.next_to,brace_n2,DOWN,bman2.shift,0.007*LEFT)
        self.wait()
        self.play(bman3.set_fill,WHITE,1,bman3.next_to,brace_n3,DOWN,bman3.shift,0.007*LEFT)
        self.wait()
        # Salida de brazo y su texto
        self.play(FadeOut(bman),FadeOut(brace_n),
                  FadeOut(bman2),FadeOut(brace_n2),
                  FadeOut(bman3),FadeOut(brace_n3))
        self.wait()
        # Desglozar suma
        # Animacion de bajar numeros parentesis, i y agregar simbolos de multiplicacion
        # I=1
        self.play(ReplacementTransform(self.formulas_sum[2][6:9].copy(),formula_3[0][0:3]),
            ReplacementTransform(self.formulas_sum[2][14].copy(),formula_3[0][8]),
            ReplacementTransform(self.formulas_sum[2][15].copy(),formula_3[0][9]),
            Write(formula_3[0][10]),Write(formula_3[0][7]),run_time=2
                )
        self.wait()
        # I=2
        self.play(ReplacementTransform(self.formulas_sum[2][6:9].copy(),formula_3[0][16:19]),
            ReplacementTransform(self.formulas_sum[2][14].copy(),formula_3[0][24]),
            ReplacementTransform(self.formulas_sum[2][15].copy(),formula_3[0][25]),
            Write(formula_3[0][23]),Write(formula_3[0][26]),Write(formula_3[0][15]),run_time=2
                )
        self.wait()
        # I=3
        self.play(ReplacementTransform(self.formulas_sum[2][6:9].copy(),formula_3[0][32:35]),
            ReplacementTransform(self.formulas_sum[2][14].copy(),formula_3[0][40]),
            ReplacementTransform(self.formulas_sum[2][15].copy(),formula_3[0][41]),
            Write(formula_3[0][39]),Write(formula_3[0][42]),Write(formula_3[0][31]),run_time=2
                )
        self.wait()
        # Poiscionar 2.6periodico
        dp61=TexMobject("2.\\overline{6}","\\,").set_fill(opacity=0)
        dp62=dp61.copy()
        dp61[0].move_to(self.formulas_sum[2][9:14])
        dp62[0].move_to(self.formulas_sum[2][-5:])
        # Bajar bases
        self.play(ReplacementTransform(dp61[0].copy(),formula_3[0][3:7]),
                  ReplacementTransform(dp62[0].copy(),formula_3[0][11:15]),
                  run_time=2
            )
        self.wait()
        self.play(ReplacementTransform(dp61[0].copy(),formula_3[0][19:23]),
                  ReplacementTransform(dp62[0].copy(),formula_3[0][27:31]),
                  run_time=2
            )
        self.wait()
        self.play(ReplacementTransform(dp61[0].copy(),formula_3[0][35:39]),
                  ReplacementTransform(dp62[0].copy(),formula_3[0][43:47]),
                  run_time=2
            )
        self.wait()
        # Transformar area aproximada a valor numerico
        self.play(ReplacementTransform(AreaAprox[0].copy(),formula_3[1]),
            ReplacementTransform(AreaAprox[1].copy(),formula_3[2]),run_time=1.5)
        self.wait()
        # Sale suma condensada
        self.play(FadeOut(self.formulas_sum[2]))
        self.wait()
        # Sombra formula_3
        self.play(formula_3.set_fill,WHITE,0.5)
        self.wait()
        # Animaciones de cuadro 0------------------------------------
        resaltado(formula_3[0][:15])
        self.wait()
        # Añadir linea horizontal y vertical
        self.play(ShowCreationThenDestruction(
            linea1_a_3_6, 
            submobject_mode = "lagged_start"),
            run_time=2)
        self.play(ShowCreationThenDestruction(
            linea3_6_a_3_6, 
            submobject_mode = "lagged_start"),
            run_time=2)
        # Añadir rectangulo 0
        recuadroObjeto(self.rect_listb[1][0],1)
        self.wait()
        self.play(FadeIn(self.rect_listb[1][0]))
        self.wait()
        # Quitar resaltado
        desresaltado(formula_3[0][:15],self.rect_listb[1][0])
        # Animaciones de cuadro 1------------------------------------
        resaltado(formula_3[0][16:31])
        self.wait()
        # Añadir linea horizontal y vertical
        self.play(ShowCreationThenDestruction(
            linea1_a_6_3, 
            submobject_mode = "lagged_start"),
            run_time=2)
        self.wait()
        self.play(ShowCreationThenDestruction(
            linea6_3_a_6_3, 
            submobject_mode = "lagged_start"),
            run_time=2)
        self.wait()
        # Añadir rectangulo 1
        recuadroObjeto(self.rect_listb[1][1],1)
        self.wait()
        self.play(FadeIn(self.rect_listb[1][1]))
        self.wait()
        desresaltado(formula_3[0][16:31],self.rect_listb[1][1])
        self.wait()
        # Animaciones de cuadro 2------------------------------------
        resaltado(formula_3[0][32:])
        # Añadir linea horizontal y vertical
        self.play(ShowCreationThenDestruction(
            linea1_a_9, 
            submobject_mode = "lagged_start"),
            run_time=2)
        self.play(ShowCreationThenDestruction(
            linea9_a_9, 
            submobject_mode = "lagged_start"),
            run_time=2)
        # Añadir rectangulo 2
        recuadroObjeto(self.rect_listb[1][2],1)
        self.play(FadeIn(self.rect_listb[1][2]))
        desresaltado(formula_3[0][32:],self.rect_listb[1][2])
        # Color de formula_3
        self.play(
            formula_3[1:].set_fill,WHITE,1,
            formula_3[0][32:].set_fill,PURPLE_B,1,
            formula_3[0][:32].set_fill,None,1
            )
        self.wait()
        # Triangulos amarillos
        self.play(
            ShowCreationThenDestruction(self.triangulo4_1,rate_func= lambda w: w),
            ShowCreationThenDestruction(self.triangulo4_2,rate_func= lambda w: w),
            ShowCreationThenDestruction(self.triangulo4_3,rate_func= lambda w: w),
            )
        self.wait()
        # Salir suma desglozada
        self.play(FadeOut(formula_3))
        self.wait()
        # Salidas
        self.play(*[FadeOut(triangulo)for triangulo in [tri1,tri3_6,tri6_3,tri9]])
        self.wait()
        nti=TexMobject("n\\to\\infty").move_to(nums[2]).scale(0.8).next_to(self.AreaReal,DOWN,buff=SMALL_BUFF*3)
        nti[0].set_color(TEAL_B)
        #-----------------------
        self.play(*[ReplacementTransform(nums[2][w],nti[w])for w in range(len(nti))])
        self.wait()
        #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        self.transform_between_riemann_rects(
            self.rect_listb[1], self.rect_list[2], dx=1,
            replace_mobject_with_target_in_scene = True,
            )
        for j in range(3,10):
            self.transform_between_riemann_rects(
            self.rect_list[j-1], self.rect_list[j], dx=1,
            replace_mobject_with_target_in_scene = True,
            )
        # Salir triangulos
        ArtAp=TexMobject("A_{aprox}\\to A_{real}").to_edge(DOWN).scale(1.2)
        self.play(Write(ArtAp))
        self.wait(2)
        #Remplazar n->infty
        self.play(
            *[ReplacementTransform(nti[j],self.integral[j+3])for j in range(0,len(nti))],
            run_time=2.5
            )
        self.wait()
        self.play(Write(self.integral[:3]))
        self.wait()
        #Quitar todo
        self.play(*[
            FadeOut(objeto)
            for objeto in [self.x_axis[:3],self.y_axis[:3],self.graph,self.rect_list[9],self.AreaReal,self.linea_a,self.linea_b,self.cuadro1,AreaAprox,ArtAp]
            ])
        self.wait()
        # Salir AreaAprox
        self.play(self.integral.set_fill,None,1,
                  self.integral.shift,DOWN*3,
                  self.integral.scale,1.3)
        self.wait()
        self.simint.next_to(self.integral,RIGHT,buff=SMALL_BUFF).shift(0.07*UP)
        self.simint[4:].shift(LEFT*0.2)
        self.play(Write(self.simint))
        self.wait()
        #'''

    def mostrar_randolf2(self):
        randy = Alex()
        randy.to_corner(DOWN+LEFT)
        randy.shift(2*RIGHT)
        words = TextMobject("Qué fácil!")
        words.scale(0.7)

        self.play(FadeIn(randy))
        self.play(OmegaCreatureDice(
            randy, words, 
            bubble_kwargs = {"height" : 3, "width" : 4},
            target_mode="speaking"
        ))
        self.play(Blink(randy))
        self.wait()
        self.play(Blink(randy))
        self.wait(0.5)
        self.play(RemueveDialogo(randy))
        self.play(FadeOut(randy))
        #'''
