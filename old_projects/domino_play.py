#!/usr/bin/env python
# -*- coding: utf-8 -*-


from manimlib.imports import *


class SimpleVelocityGraph(GraphScene):
    CONFIG = {
        # "frame_rate" : 4000,
        # "domino_thickness" : 7.5438,
        # "domino_spacing" : 8.701314282,
        "data_files" : [
            "data07.txt",
            "data13.txt",
            # "data11.txt",
        ],
        "colors" : [WHITE, BLUE, YELLOW, GREEN, MAROON_B],
        "x_axis_label" : "$t$",
        "y_axis_label" : "$v$",
        "x_min" : 0,
        "x_max" : 1.8,
        "x_tick_frequency" : 0.1,
        "x_labeled_nums" : np.arange(0, 1.8, 0.2),
        "y_tick_frequency" : 100,
        "y_min" : 0,
        "y_max" : 1000,
        "y_labeled_nums" : list(range(0, 1000, 200)),
        "x_axis_width" : 12,
        "graph_origin" : 2.5*DOWN + 5*LEFT,
        "trailing_average_length" : 20,
        "include_domino_thickness" : False,
    }
    def construct(self):
        self.setup_axes()
        # self.save_all_images()
        for data_file, color in zip(self.data_files, self.colors):
            self.init_data(data_file)
            self.draw_dots(color)
            self.add_label_to_last_dot(
                "%s %s %.2f"%(
                    data_file[4:6], 
                    "hard" if self.friction == "low" else "felt",
                    self.domino_spacing,
                ),
                color
            )
            self.draw_lines(color)

    def save_all_images(self):
        indices = list(range(1, 20))
        for i1, i2 in it.combinations(indices, 2):
            to_remove = VGroup()
            for index in i1, i2:
                index_str = ("%.2f"%float(0.01*index))[-2:]
                data_file = "data%s.txt"%index_str
                self.init_data(data_file)
                color = WHITE if self.friction == "low" else BLUE
                self.draw_dots(color)
                self.add_label_to_last_dot(
                    "%s %s %.2f"%(
                        data_file[4:6], 
                        "hard" if self.friction == "low" else "felt",
                        self.domino_spacing,
                    ),
                    color
                )
                self.draw_lines(color)
                to_remove.add(self.dots, self.lines, self.label)
            self.save_image("dominos_%d_vs_%d"%(i1, i2))
            self.remove(to_remove)

    def init_data(self, data_file):
        file_name = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "dominos",
            data_file
        )

        file = open(file_name, "r")
        frames, notes = [], []
        for line in file:
            line = line.replace("  ", ",")
            line = line.replace("\n", "")
            entries = [s for s in line.split(",") if s is not ""]
            if len(entries) == 0:
                continue

            if entries[0] == "framerate":
                frame_rate = float(entries[1])
            elif entries[0] == "domino spacing":
                domino_spacing = float(entries[1])
            elif entries[0] == "domino thickness":
                domino_thickness = float(entries[1])
            elif entries[0] == "friction":
                self.friction = entries[1]
            else:
                try:
                    frames.append(int(entries[0]))
                except:
                    continue #How to treat?
                    # frames.append(frames[-1] + (frames[-1] - frames[-2]))
                if len(entries) > 1:
                    notes.append(entries[1])
                else:
                    notes.append("")
        frames = np.array(frames)

        self.times = (frames - frames[0])/float(frame_rate)
        delta_times = self.times[1:] - self.times[:-1]
        if self.include_domino_thickness:
            distance = domino_spacing+domino_thickness
        else:
            distance = domino_spacing
        self.velocities = distance/delta_times
        self.notes = notes

        n = self.trailing_average_length
        self.velocities = np.array([
            np.mean(self.velocities[max(0, i-n):i])
            for i in range(len(self.velocities))
        ])
        self.domino_spacing = domino_spacing
        self.domino_thickness = domino_thickness

    def draw_dots(self, color = WHITE):
        dots = VGroup()
        for time, v, note in zip(self.times, self.velocities, self.notes):
            dot = Dot(color = color)
            dot.scale(0.5)
            dot.move_to(self.coords_to_point(time, v))
            self.add(dot)
            dots.add(dot)
            if note == "twist":
                dot.set_color(RED)
        self.dots = dots

    def add_label_to_last_dot(self, label, color = WHITE):
        dot = self.dots[-1]
        label = TextMobject(label)
        label.scale(0.75)
        label.next_to(dot, UP, buff = MED_SMALL_BUFF)
        label.set_color(color)
        label.shift_onto_screen()
        self.label = label
        self.add(label)

    def draw_lines(self, color = WHITE, stroke_width = 2):
        lines = VGroup()
        for d1, d2 in zip(self.dots, self.dots[1:]):
            line = Line(d1.get_center(), d2.get_center())
            lines.add(line)
        lines.set_stroke(color, stroke_width)
        self.add(lines, self.dots)
        self.lines = lines

ALL_VELOCITIES = {
    10 : [
        0.350308642,
        0.3861880046,
        0.8665243271,
        0.9738947062,
        0.8087560386,
        1.067001275,
        0.9059117965,
        1.113855622,
        0.9088626493,
        1.504155436,
        1.347926731,
        1.274067732,
        1.242854491,
        1.118319973,
        1.177303094,
        1.202676006,
        0.9965029762,
        1.558775605,
        1.472405453,
        1.357765612,
        1.200089606,
        1.285810292,
        1.138860544,
        1.322373618,
        1.51230804,
        1.148233882,
        1.276983219,
        1.150601375,
        1.492090018,
        1.210502531,
        1.221097739,
        1.141189502,
        1.364405053,
        1.608189241,
        1.223775585,
        1.174824561,
        1.069045338,
        1.468530702,
        1.733048654,
        1.328670635,
        1.118319973,
        1.143528005,
        1.010945048,
        1.430876068,
        1.395104167,
        1.018324209,
        1.405646516,
        1.120565596,
        1.24562872,
        1.65590999,
        1.276983219,
        1.282854406,
        1.338229416,
        1.240092593,
        0.9982856291,
        1.811823593,
        1.328670635,
        1.167451185,
        1.27991208,
        1.221097739,
        1.022054335,
        1.160169785,
        1.805960086,
        0.9965029762,
        1.449458874,
        1.603568008,
        1.234605457,
        1.210502531,
        1.192396724,
        1.020185862,
        1.496090259,
        1.322373618,
        1.291763117,
        1.210502531,
        0.9807410662,
        1.341446314,
        1.391625104,
        1.480216622,
        1.148233882,
        1.125084005,
        1.670783433,
        1.118319973,
        1.174824561,
        1.395104167,
        1.167451185,
        1.182291667,
        1.696175279,
        1.306889149,
        1.430876068,
        1.048950501,
        1.823665577,
        1.24562872,
    ],
    13 : [
        0.2480920273,
        0.3532654568,
        0.549163523,
        0.5979017857,
        0.6643353175,
        0.8495940117,
        1.037573598,
        0.897413562,
        1.410977665,
        0.9180833562,
        1.303328143,
        0.9324004456,
        2.026785714,
        0.9721980256,
        1.339835934,
        1.002770291,
        2.3797086,
        1.235972684,
        1.508900406,
        1.239174685,
        1.374486864,
        1.181040564,
        1.144309638,
        1.195803571,
        1.265400605,
        1.223328462,
        1.678320802,
        1.198800573,
        0.7958759211,
        1.573425752,
        1.046655205,
        2.009753902,
        1.42782516,
        1.289276088,
        1.347384306,
        1.299786491,
        1.06530385,
        1.339835934,
        1.242393321,
        1.053571429,
        1.317689886,
        1.626943635,
        1.112375415,
        1.362739113,
        0.9110884354,
        1.578618576,
        1.853959025,
        1.504155436,
        1.158163265,
        1.262061817,
        1.060579664,
        1.122820255,
        1.594404762,
        1.27552381,
        1.382431874,
        1.109794498,
        1.303328143,
        1.160974341,
        1.296264034,
        1.092058056,
        1.077300515,
        1.462756662,
        1.317689886,
        1.390469269,
        1.099589491,
        1.649384236,
        1.467243646,
        1.402702137,
        1.092058056,
        1.201812635,
        1.258740602,
        1.321329913,
        1.272131459,
        1.175236925,
        1.181040564,
        1.296264034,
        1.24562872,
        1.358867695,
        1.332371667,
        1.296264034,
        1.217102872,
        1.169490045,
        1.114968365,
        1.528183478,
        1.374486864,
        1.223328462,
        1.324990107,
        1.268757105,
        1.169490045,
        1.578618576,
    ],
    14 : [
        0.4905860806,
        0.6236263736,
        0.71391258,
        0.8436004031,
        1.048950501,
        0.9585599771,
        1.138860544,
        1.210940325,
        1.27552381,
        1.282363079,
        1.166637631,
        1.242393321,
        1.163799096,
        1.166637631,
        1.42357568,
        1.382431874,
        1.278934301,
        1.390469269,
        1.181040564,
        1.107225529,
        1.08462909,
        1.160974341,
        1.374486864,
        1.382431874,
        1.355018211,
        1.25543682,
        1.192821518,
        0.9360497624,
        1.449458874,
        1.370548506,
        1.485470275,
        1.471758242,
        1.149811126,
        1.217102872,
        1.152581756,
        1.402702137,
        1.155365769,
        1.141578588,
        1.248881015,
        1.074879615,
        1.453864525,
        1.303328143,
        1.248881015,
        1.169490045,
        1.214013778,
        1.220207726,
        1.310469667,
        1.42357568,
        1.163799096,
        1.220207726,
        1.141578588,
        1.207882395,
        1.104668426,
        1.328670635,
        1.25543682,
        1.239174685,
        1.169490045,
        1.149811126,
        1.000672445,
        1.144309638,
        1.232787187,
        1.268757105,
        1.306889149,
        1.538011024,
        1.355018211,
        1.347384306,
        1.223328462,
        1.149811126,
        1.158163265,
        1.24562872,
        1.485470275,
        1.339835934,
        1.314069859,
        1.235972684,
        1.265400605,
        1.181040564,
        1.638087084,
        1.568266979,
        1.299786491,
        1.278934301,
        1.336093376,
        1.089570452,
        1.004876951,
        1.089570452,
        1.282363079,
        1.449458874,
        1.370548506,
        1.265400605,
        1.143215651,
    ],
    15 : [
        1.087094156,
        1.223328462,
        1.563141923,
        1.394523115,
        1.268757105,
        1.513675407,
        1.436400686,
        1.094557045,
        0.9761661808,
        1.072469571,
        1.178131597,
        1.366632653,
        1.258740602,
        1.25543682,
        1.285810292,
        1.235972684,
        1.347384306,
        1.239174685,
        1.195803571,
        1.186901808,
        1.141578588,
        1.152581756,
        1.136155412,
        1.102123107,
        1.242393321,
        1.347384306,
        1.278934301,
        1.366632653,
        1.351190476,
        0.9882674144,
        1.1898543,
        1.351190476,
        1.169490045,
        1.292760618,
        1.638087084,
        1.436400686,
        1.328670635,
        1.242393321,
        1.355018211,
        1.303328143,
        1.186901808,
        1.112375415,
        1.432100086,
        1.1898543,
        1.324990107,
        1.074879615,
        1.214013778,
        1.20483987,
        1.158163265,
        1.112375415,
        1.220207726,
        1.402702137,
        1.268757105,
        1.282363079,
        1.289276088,
        1.292760618,
        1.183963932,
        1.252150337,
        1.42782516,
        1.292760618,
        1.026440834,
        1.268757105,
        1.268757105,
        1.285810292,
        1.347384306,
        1.272131459,
        1.220207726,
        1.296264034,
        1.25543682,
        1.494754464,
        1.347384306,
        1.214013778,
        1.169490045,
        1.147053786,
        1.082175178,
        1.109794498,
        1.382431874,
        1.24562872,
        1.201812635,
        1.328670635,
        1.122820255,
        1.220207726,
        1.192821518,
        1.563141923,
        1.41935142,
        1.336093376,
        1.406827731,
        1.258740602,
        1.186901808,
        1.232787187,
        1.107225529,
    ],

}
# Felt: 8,9,10,11,12,13
# Hardwood 1-7, 14,15

class ContrastTwoGraphs(SimpleVelocityGraph):
    CONFIG = {
        "velocities1_index" : 13,
        "velocities2_index" : 14,
        "x_min" : -1,
        "x_max" : 10,
        "y_min" : -0.25,
        "y_max" : 2,
        "x_axis_label" : "",
        "y_axis_label" : "",
        "x_labeled_nums" : [],
        "y_labeled_nums" : [],
        "y_tick_frequency" : 0.25,
        "x_tick_frequency" : 12,
        "moving_average_n" : 20,
    }
    def construct(self):
        self.setup_axes()
        velocities1 = ALL_VELOCITIES[self.velocities1_index]
        velocities2 = ALL_VELOCITIES[self.velocities2_index]

        self.n_data_points = len(velocities1)
        graph1 = self.get_velocity_graph(velocities1)
        graph2 = self.get_velocity_graph(velocities2)
        smoothed_graph1 = self.get_smoothed_velocity_graph(velocities1)
        smoothed_graph2 = self.get_smoothed_velocity_graph(velocities2)
        for graph in graph1, smoothed_graph1:
            self.color_graph(graph)
        for graph in graph2, smoothed_graph2:
            self.color_graph(graph, BLUE, RED)
        for graph in graph1, graph2, smoothed_graph1, smoothed_graph2:
            graph.axes = self.axes.deepcopy()
            graph.add_to_back(graph.axes)

        lower_left = self.axes.get_corner(DOWN+LEFT)
        self.remove(self.axes)

        felt = TextMobject("Felt")
        hardwood = TextMobject("Hardwood")
        hardwood.set_color(RED)
        words = VGroup(felt, hardwood)

        self.force_skipping()

        #Show jaggediness
        graph1.scale(0.5).to_edge(UP)
        graph2.scale(0.5).to_edge(DOWN)
        felt.next_to(graph1, LEFT, buff = 0.75)
        hardwood.next_to(graph2, LEFT, buff = 0.75)

        self.play(
            ShowCreation(graph1, run_time = 3, rate_func=linear),
            Write(felt)
        )
        self.play(
            ShowCreation(graph2, run_time = 4, rate_func=linear),
            Write(hardwood)
        )
        self.wait()

        for g, sg in (graph1, smoothed_graph1), (graph2, smoothed_graph2):
            sg_copy = sg.deepcopy()
            sg_copy.scale(0.5)
            sg_copy.shift(g.get_center())
            mover = VGroup(*it.chain(*list(zip(g.dots, g.lines))))
            target = VGroup(*it.chain(*list(zip(sg_copy.dots, sg_copy.lines))))
            for m, t in zip(mover, target):
                m.target = t
            self.play(LaggedStartMap(
                MoveToTarget, mover,
                rate_func = lambda t : 0.3*wiggle(t),
                run_time = 3,
                lag_ratio = 0.2,
            ))
        twists = TextMobject("Twists?")
        variable_distances = TextMobject("Variable distances")
        for word in twists, variable_distances:
            word.to_corner(UP+RIGHT)
        self.play(Write(twists))
        self.wait()
        self.play(ReplacementTransform(twists, variable_distances))
        self.wait(3)
        self.play(FadeOut(variable_distances))

        self.revert_to_original_skipping_status()
        self.play(
            graph1.scale, 2,
            graph1.move_to, lower_left, DOWN+LEFT,
            graph2.scale, 2,
            graph2.move_to, lower_left, DOWN+LEFT,
            FadeOut(words)
        )
        self.wait()
        return

        #Show moving averages
        self.play(FadeOut(graph2))

        dots = graph1.dots
        dot1, dot2 = dots[21], dots[41]
        rect = Rectangle(
            width = dot2.get_center()[0] - dot1.get_center()[0],
            height = FRAME_Y_RADIUS - self.x_axis.get_center()[1],
            stroke_width = 0,
            fill_color = YELLOW,
            fill_opacity = 0.5
        )
        rect.move_to(dot2.get_center(), RIGHT)
        rect.to_edge(UP, buff = 0)
        pre_rect = rect.copy()
        pre_rect.stretch_to_fit_width(0)
        pre_rect.move_to(rect, RIGHT)

        arrow = Vector(DOWN)
        arrow.next_to(dot2, UP, SMALL_BUFF)

        self.play(GrowArrow(arrow))
        self.play(
            dot2.shift, MED_SMALL_BUFF*UP,
            dot2.set_color, PINK,
            rate_func = wiggle
        )
        self.wait()
        self.play(
            FadeOut(arrow),
            ReplacementTransform(pre_rect, rect),
        )
        self.wait()
        self.play(
            Transform(graph1, smoothed_graph1, run_time = 2),
            Animation(rect)
        )
        self.play(FadeOut(rect))
        self.wait()
        self.play(FadeIn(graph2))
        self.play(Transform(graph2, smoothed_graph2))

        felt.next_to(dot2, UP, MED_LARGE_BUFF)
        hardwood.next_to(felt, DOWN, LARGE_BUFF)

        self.play(
            LaggedStartMap(FadeIn, felt),
            LaggedStartMap(FadeIn, hardwood),
            run_time = 1
        )
        self.wait()

        #Compare regions
        dot_group1 = VGroup(
            *graph1.dots[35:75] + graph2.dots[35:75]
        )
        dot_group2 = VGroup(
            *graph1.dots[75:] + graph2.dots[75:]
        )
        dot_group3 = VGroup(
            *graph1.dots[35:] + graph2.dots[35:]
        )
        rect1 = SurroundingRectangle(dot_group1)
        rect2 = SurroundingRectangle(dot_group2)
        rect3 = SurroundingRectangle(dot_group3)

        self.play(ShowCreation(rect1))
        for x in range(2):
            self.play(LaggedStartMap(
                ApplyMethod, dot_group1,
                lambda m : (m.scale_in_place, 0.5),
                rate_func = wiggle,
                lag_ratio = 0.05,
                run_time = 3,
            ))
        self.wait()
        self.play(ReplacementTransform(rect1, rect2))
        for x in range(2):
            self.play(LaggedStartMap(
                ApplyMethod, dot_group2,
                lambda m : (m.scale_in_place, 0.5),
                rate_func = wiggle,
                lag_ratio = 0.05,
                run_time = 3,
            ))
        self.wait()
        self.play(ReplacementTransform(rect1, rect3))
        for x in range(2):
            self.play(LaggedStartMap(
                ApplyMethod, dot_group3,
                lambda m : (m.scale_in_place, 0.5),
                rate_func = wiggle,
                lag_ratio = 0.05,
                run_time = 3,
            ))
        self.wait()


    ###

    def color_graph(self, graph, color1 = BLUE, color2 = WHITE, n_starts = 20):
        graph.set_color(color2)
        VGroup(*graph.dots[:11] + graph.lines[:10]).set_color(color1)

    def get_smoothed_velocity_graph(self, velocities):
        n = self.moving_average_n
        smoothed_vs = np.array([
            np.mean(velocities[max(0, i-n):i])
            for i in range(len(velocities))
        ])
        return self.get_velocity_graph(smoothed_vs)

    def get_velocity_graph(self, velocities):
        n = len(velocities)
        dots = VGroup(self.get_dot(1, velocities[0]))
        lines = VGroup()
        for x in range(1, n):
            dots.add(self.get_dot(x+1, velocities[x]))
            lines.add(Line(
                dots[-2].get_center(),
                dots[-1].get_center(),
            ))
        graph = VGroup(dots, lines)
        graph.dots = dots
        graph.lines = lines

        return graph

    def get_dot(self, x, y):
        dot = Dot(radius = 0.05)
        dot.move_to(self.coords_to_point(
            x * float(self.x_max) / self.n_data_points, y
        ))
        return dot




class ShowAllSteadyStateVelocities(SimpleVelocityGraph):
    CONFIG = {
        "x_axis_label" : "\\text{Domino spacing}",
        "x_min" : 0,
        "x_max" : 40,
        "x_axis_width" : 9,
        "x_tick_frequency" : 5,
        "x_labeled_nums" : list(range(0, 50, 10)),
        "y_min" : 0,
        "y_max" : 400,
        "y_labeled_nums" : [],
        # "y_labeled_nums" : range(200, 1400, 200),
    }
    def construct(self):
        self.setup_axes()
        for index in range(1, 20):
            index_str = ("%.2f"%float(0.01*index))[-2:]
            data_file = "data%s.txt"%index_str
            self.init_data(data_file)
            color = WHITE if self.friction == "low" else BLUE
            label = TextMobject(
                index_str,
                color = color
            )
            label.scale(0.5)
            label.set_color(color)

            dot = Dot(color = color)
            dot.scale(0.5)
            dot.move_to(self.coords_to_point(
                self.domino_spacing, self.velocities[-1] - 400
            ))
            label.next_to(
                dot, 
                random.choice([LEFT, RIGHT]), 
                SMALL_BUFF
            )
            self.add(dot)
            self.add(label)
            print(index_str, self.velocities[-1], self.friction)

class Test(Scene):
    def construct(self):
        shift_val = 1.5

        domino1 = Rectangle(
            width = 0.5, height = 3,
            stroke_width = 0,
            fill_color = GREEN,
            fill_opacity = 1
        )
        domino1.shift(LEFT)
        domino2 = domino1.copy()
        domino2.set_fill(BLUE_E)
        domino2.shift(shift_val*RIGHT)
        spacing = shift_val - domino2.get_width()
        dominos = VGroup(domino1, domino2)
        for domino in dominos:
            line = DashedLine(domino.get_left(), domino.get_right())
            dot = Dot(domino.get_center())
            domino.add(line, dot)

        arc1 = Arc(
            radius = domino1.get_height(),
            start_angle = np.pi/2,
            angle = -np.arcsin(spacing / domino1.get_height())
        )
        arc1.shift(domino1.get_corner(DOWN+RIGHT))
        arc2 = Arc(
            radius = domino1.get_height()/2,
            start_angle = np.pi/2,
            angle = -np.arcsin(2*spacing/domino1.get_height())
        )
        arc2.shift(domino1.get_right())
        arc2.set_color(BLUE)
        arcs = VGroup(arc1, arc2)
        for arc, vect in zip(arcs, [DOWN+RIGHT, RIGHT]):
            arc_copy = arc.copy()
            point = domino1.get_critical_point(vect)
            arc_copy.add_line_to([point])
            arc_copy.set_stroke(width = 0)
            arc_copy.set_fill(
                arc.get_stroke_color(),
                0.2,
            )
            self.add(arc_copy)

        domino1_ghost = domino1.copy()
        domino1_ghost.fade(0.8)
        self.add(domino1_ghost, dominos, arcs)

        self.play(Rotate(
            domino1,
            angle = arc1.angle,
            about_point = domino1.get_corner(DOWN+RIGHT),
            rate_func = there_and_back,
            run_time = 3,
        ))
        self.play(Rotate(
            domino1,
            angle = arc2.angle,
            about_point = domino1.get_right(),
            rate_func = there_and_back,
            run_time = 3,
        ))

        print(arc1.angle, arc2.angle)



























