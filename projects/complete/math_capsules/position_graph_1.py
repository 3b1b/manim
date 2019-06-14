from manimlib.imports import *

class OperationsGraph(GraphScene):
    CONFIG = {
        "x_min": -9,
        "x_max": 9,
        "x_axis_width": 13,
        "x_tick_frequency": 1,
        "x_axis_label": False,
        "y_min": -9,
        "y_max": 9,
        "y_axis_height": 7.5,
        "y_tick_frequency": 1.5,
        "y_axis_label": False,
        "axes_color": GREY,
        "graph_origin": ORIGIN,
        "area_opacity": 0.8,
        "num_rects": 50,
        "axes_stroke":3,
        "tick_size":0.07,
        "tiempo_wait":1.5,
    }
    def espera(self):
        self.wait(self.tiempo_wait)

    def construct(self):
        self.include_title()
        self.setup_axes()
        self.move_graph()
        self.reflect_graph()

    def include_title(self):
        tikz="""
        \\begin{tikzpicture}[pencildraw/.style={decorate,
        decoration={random steps,segment length=0.8pt,amplitude=0.3pt}}]
            \\node[pencildraw,draw] {\\sc Shifting Graphs};
        \\end{tikzpicture} 
            """
        tit=Tikz(tikz,stroke_width=2,fill_opacity=.1,color=WHITE).scale(3)
        tit[0][0].set_fill(BLACK,1)
        tit[0][1:].set_stroke(None,0).set_fill(WHITE,1)
        self.Oldplay(Escribe(tit[0][1:]))
        self.add_foreground_mobject(tit[0])
        self.add_foreground_mobject(tit[1:])
        self.Oldplay(OldWrite(tit[0][0]))
        esq_left=tit[0][1:].get_left()
        esq_right=tit[0][1:].get_right()
        cuerda_left=Line(esq_left+UP*5,esq_left,color=WHITE)
        cuerda_right=Line(esq_right+UP*5,esq_right,color=WHITE)
        self.play(ShowCreation(cuerda_left),ShowCreation(cuerda_right))
        self.espera()
        self.add_foreground_mobjects(tit[0],tit[1:])
        self.play(
        VGroup(tit[0],cuerda_left,cuerda_right,tit[1:]).shift,UP*8
        )

    def move_graph(self):
        graph = self.get_graph(
            lambda x: 0.1 * (x + 3-5+2) * (x - 3-5+2) * (x-5+2) + 5,
            x_min=0.1-2,
            x_max=8.5-2,
        )
        graph.shift(LEFT*2.2+DOWN*1.1)
        #                    0   1    2   3
        graph_label=Formula("-","f(","x",")")\
                    .match_color(graph)\
                    .next_to(graph.points[-1],UP)
        graph_label[0].fade(1)
        x_label=Formula("x").fade(0.6)
        y_label=Formula("y").fade(0.6)

        y_label.next_to(self.y_axis_line[0].get_end(),LEFT)
        x_label.next_to(self.x_axis_line[0].get_end(),RIGHT)

        graph_group=VGroup(graph,graph_label)

        #graph_dx
        graph_dx = graph.copy()
        graph_dx.set_color(RED)\
                .shift(LEFT*3)
        #                         0   1    2    3
        graph_label_dx = Formula("f(","x","+k",")")
        graph_label_dx.next_to(graph_dx,UP)\
                      .match_color(graph_dx)

        line_distance_dx=Line(
            graph_dx.points[0],graph.points[0]
        )
        med_dx=MeasureDistance(line_distance_dx).add_tips()
        remark_k=Formula("k \\geq 0")
        remark_k.next_to(med_dx,DOWN)

        group_dx=VGroup(
            graph_dx,
            graph_label_dx,
            med_dx,
            remark_k
            )

        #graph_dx_2
        graph_dx_2 = graph.copy()
        graph_dx_2.set_color(PURPLE)\
                .shift(RIGHT*4)
        #                         0   1    2    3
        graph_label_dx_2 = Formula("f(","x","-k",")")
        graph_label_dx_2.next_to(graph_dx_2.points[-1],UP)\
                      .match_color(graph_dx_2)\
                      .shift(LEFT*0.8)

        line_distance_dx_2=Line(
            graph_dx_2.points[0],graph.points[0]
        )
        med_dx_2=MeasureDistance(line_distance_dx_2,invertir=False).add_tips()
        remark_k_2=Formula("k \\geq 0")
        remark_k_2.next_to(med_dx_2,DOWN)

        group_dx_2=VGroup(
            graph_dx_2,
            graph_label_dx_2,
            med_dx_2,
            remark_k_2
            )

        #graph_dy
        graph_dy = graph.copy()
        graph_dy.set_color(RED)\
                .shift(UP*1.2)
        #                         0   1    2    3
        graph_label_dy = Formula("f(","x",")","+h")
        graph_label_dy.next_to(graph_dy.points[-1],UP)\
                      .match_color(graph_dy)

        line_distance_dy=Line(
            graph_dy.points[0],graph.points[0]
        )
        med_dy=MeasureDistance(line_distance_dy).add_tips()
        remark_h=Formula("h \\geq 0")
        remark_h.next_to(med_dy,LEFT)

        group_dy=VGroup(
            graph_dy,
            graph_label_dy,
            med_dy,
            remark_h
            )

        #graph_dy_2
        graph_dy_2 = graph.copy()
        graph_dy_2.set_color(PURPLE)\
                .shift(DOWN*1.2)
        #                         0   1    2    3
        graph_label_dy_2 = Formula("f(","x",")","-h")
        graph_label_dy_2.next_to(graph_dy_2.points[-1],UP)\
                      .match_color(graph_dy_2)

        line_distance_dy_2=Line(
            graph_dy_2.points[0],graph.points[0]
        )
        med_dy_2=MeasureDistance(line_distance_dy_2,invertir=False).add_tips()
        remark_h_2=Formula("h \\geq 0")
        remark_h_2.next_to(med_dy_2,LEFT)

        group_dy_2=VGroup(
            graph_dy_2,
            graph_label_dy_2,
            med_dy_2,
            remark_h_2
            )


        self.Oldplay(
            OldWrite(self.x_axis_line),
            OldWrite(self.y_axis_line),
            Escribe(x_label),
            Escribe(y_label),
            )
        self.espera()

        self.Oldplay(
            OldShowCreation(graph),
            Escribe(graph_label)
            )
        self.espera()

        graph.save_state()
        graph_label.save_state()

        #self.add(graph_label_dx[3].set_color(ORANGE))


        # Transform -> dx
        self.play(*[
            ReplacementTransform(
                graph_label[i].copy(),graph_label_dx[j]
            )
            for i,j in zip(
                [1,2,3],
                [0,1,3]
            )],
            ReplacementTransform(graph.copy(),graph_dx),
            GrowFromEdge(med_dx,RIGHT),
            FadeInFromDown(remark_k),
            ApplyMethod(graph.fade,0.5),
            ApplyMethod(graph_label.fade,0.5),
            run_time=2
        )
        self.play(Write(graph_label_dx[2]))

        self.espera()

        self.play(
            ApplyMethod(group_dx.fade,1),
            Restore(graph),
            Restore(graph_label)
            )
        self.espera()

        # Transform -> dx_2
        self.play(*[
            ReplacementTransform(
                graph_label[i].copy(),graph_label_dx_2[j]
            )
            for i,j in zip(
                [1,2,3],
                [0,1,3]
            )],
            ReplacementTransform(graph.copy(),graph_dx_2),
            GrowFromEdge(med_dx_2,LEFT),
            FadeInFromDown(remark_k_2),
            ApplyMethod(graph.fade,0.5),
            ApplyMethod(graph_label.fade,0.5),
            run_time=2
        )
        self.play(Write(graph_label_dx_2[2]))

        self.espera()

        self.play(
            ApplyMethod(group_dx_2.fade,1),
            Restore(graph),
            Restore(graph_label)
            )
        self.espera()

        # Transform -> dy
        self.play(*[
            ReplacementTransform(
                graph_label[i].copy(),graph_label_dy[j]
            )
            for i,j in zip(
                [1,2,3],
                [0,1,2]
            )],
            ReplacementTransform(graph.copy(),graph_dy),
            GrowFromEdge(med_dy,DOWN),
            FadeInFromDown(remark_h),
            ApplyMethod(graph.fade,0.5),
            ApplyMethod(graph_label.fade,0.5),
            run_time=2
        )
        self.play(Write(graph_label_dy[3]))

        self.espera()

        self.play(
            ApplyMethod(group_dy.fade,1),
            Restore(graph),
            Restore(graph_label)
            )
        self.espera()

        # Transform -> dy_2
        self.play(*[
            ReplacementTransform(
                graph_label[i].copy(),graph_label_dy_2[j]
            )
            for i,j in zip(
                [1,2,3],
                [0,1,2]
            )],
            ReplacementTransform(graph.copy(),graph_dy_2),
            GrowFromEdge(med_dy_2,UP),
            FadeInFromDown(remark_h_2),
            ApplyMethod(graph.fade,0.5),
            ApplyMethod(graph_label.fade,0.5),
            run_time=2
        )
        self.play(Write(graph_label_dy_2[3]))

        self.espera()

        self.play(
            ApplyMethod(group_dy_2.fade,1),
            Restore(graph),
            Restore(graph_label)
            )
        self.espera()

        self.graph=graph
        self.graph_label=graph_label

    def reflect_graph(self):
        graph=self.graph
        graph_label=self.graph_label
        desp_x=0
        desp_y=0

        new_graph=self.get_graph(
            lambda x: 0.1 * (x + 3-5+desp_x) * (x - 3-5+desp_x) * (x-5+desp_x) + 5+desp_y,
            x_min=0.1-desp_x,
            x_max=8.5-desp_x,
            color=BLUE
        )
        new_graph_label=graph_label.copy()

        new_graph_label.next_to(new_graph,UP)

        self.play(
            Transform(graph,new_graph),
            Transform(graph_label,new_graph_label),
            )

        ref_graph=self.get_graph(
            lambda x: 0.1 * (-x + 3-5+desp_x) * (-x - 3-5+desp_x) * (-x-5+desp_x) + 5+desp_y,
            x_min=-0.1,
            x_max=-8.5,
            color=RED
        )
        #                        0    1   2   3
        ref_graph_label=Formula("f(","-","x",")").next_to(ref_graph,UP)
        ref_graph_label.match_color(ref_graph)

        mirrow_graph=self.get_graph(
            lambda x: (0.1 * (x + 3-5+desp_x) * (x - 3-5+desp_x) * (x-5+desp_x) + 5+desp_y)*(-1),
            x_min=0.1,
            x_max=8.5,
            color=PURPLE
        )
        #                           0    1   2   3
        mirrow_graph_label=Formula("-","f(","x",")").next_to(mirrow_graph,DOWN)
        mirrow_graph_label.match_color(mirrow_graph)

        ref_mirrow_graph=self.get_graph(
            lambda x: (0.1 * (-x + 3-5+desp_x) * (-x - 3-5+desp_x) * (-x-5+desp_x) + 5+desp_y)*(-1),
            x_min=-0.1,
            x_max=-8.5,
            color=GREEN
        )
        #                               0    1   2   3   4
        ref_mirrow_graph_label=Formula("-","f(","-","x",")").next_to(ref_mirrow_graph,DOWN)
        ref_mirrow_graph_label.match_color(ref_mirrow_graph)

        #graph_group=VGroup(graph,graph_label)

        reflect_x_line=DashedLine(
            self.x_axis_line[0].get_start(),
            self.x_axis_line[0].get_end()
            )

        reflect_y_line=DashedLine(
            self.y_axis_line[0].get_start(),
            self.y_axis_line[0].get_end()
            )

        graph.save_state()
        graph_label.save_state()

        # f(-x)

        self.play(ShowCreation(reflect_y_line))
        self.play(*[
            ReplacementTransform(
                graph_label[i].copy(),ref_graph_label[j]
            )
            for i,j in zip(
                [1,2,3],
                [0,2,3]
            )],
            ReplacementTransform(graph.copy(),ref_graph),
            ApplyMethod(graph.fade,0.5),
            ApplyMethod(graph_label.fade,0.5),
            run_time=2
        )
        self.play(Write(ref_graph_label[1]))
        self.espera()
        
        self.play(
            ApplyMethod(ref_graph_label.fade,1),
            ApplyMethod(ref_graph.fade,1),
            ApplyMethod(reflect_y_line.fade,1),
            Restore(graph),
            Restore(graph_label)
            )
        
        self.espera()

        # -f(x)

        self.play(ShowCreation(reflect_x_line))
        self.play(*[
            ReplacementTransform(
                graph_label[i].copy(),mirrow_graph_label[j]
            )
            for i,j in zip(
                [1,2,3],
                [1,2,3]
            )],
            ReplacementTransform(graph.copy(),mirrow_graph),
            ApplyMethod(graph.fade,0.5),
            ApplyMethod(graph_label.fade,0.5),
            run_time=2
        )
        self.play(Write(mirrow_graph_label[0]))
        self.espera()
        
        self.play(
            ApplyMethod(mirrow_graph_label.fade,1),
            ApplyMethod(mirrow_graph.fade,1),
            ApplyMethod(reflect_x_line.fade,1),
            Restore(graph),
            Restore(graph_label)
            )
        
        self.espera()

        # -f(-x)

        self.play(*[
            ReplacementTransform(
                graph_label[i].copy(),ref_mirrow_graph_label[j]
            )
            for i,j in zip(
                [1,2,3],
                [1,3,4]
            )],
            ReplacementTransform(graph.copy(),ref_mirrow_graph),
            ApplyMethod(graph.fade,0.5),
            ApplyMethod(graph_label.fade,0.5),
            run_time=2
        )
        self.play(Write(ref_mirrow_graph_label[0]),Write(ref_mirrow_graph_label[2]))
        self.espera()
        
        self.play(
            ApplyMethod(ref_mirrow_graph_label.fade,1),
            ApplyMethod(ref_mirrow_graph.fade,1),
            Restore(graph),
            Restore(graph_label)
            )
        
        self.espera()