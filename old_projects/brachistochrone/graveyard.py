import numpy as np
import itertools as it

from manimlib.imports import *

from old_projects.brachistochrone.curves import Cycloid

class MultilayeredGlass(PhotonScene, ZoomedScene):
    CONFIG = {
        "num_discrete_layers" : 5,
        "num_variables" : 3,
        "top_color" : BLUE_E,
        "bottom_color" : BLUE_A,
        "zoomed_canvas_frame_shape" : (5, 5),
        "square_color" : GREEN_B,
    }
    def construct(self):
        self.cycloid = Cycloid(end_theta = np.pi)
        self.cycloid.set_color(YELLOW)
        self.top = self.cycloid.get_top()[1]
        self.bottom = self.cycloid.get_bottom()[1]-1
        self.generate_layers()
        self.generate_discrete_path()
        photon_run = self.photon_run_along_path(
            self.discrete_path,
            run_time = 1,
            rate_func = rush_into
        )



        self.continuous_to_smooth()
        self.add(*self.layers)
        self.show_layer_variables()
        self.play(photon_run)
        self.play(ShowCreation(self.discrete_path))
        self.isolate_bend_points()
        self.clear()
        self.add(*self.layers)
        self.show_main_equation()
        self.ask_continuous_question()

    def continuous_to_smooth(self):
        self.add(*self.layers)
        continuous = self.get_continuous_background()
        self.add(continuous)
        self.wait()
        self.play(ShowCreation(
            continuous,
            rate_func = lambda t : smooth(1-t)
        ))
        self.remove(continuous)
        self.wait()
        
    def get_continuous_background(self):
        glass = FilledRectangle(
            height = self.top-self.bottom,
            width = FRAME_WIDTH,
        )
        glass.sort_points(lambda p : -p[1])
        glass.shift((self.top-glass.get_top()[1])*UP)
        glass.set_color_by_gradient(self.top_color, self.bottom_color)
        return glass

    def generate_layer_info(self):
        self.layer_thickness = float(self.top-self.bottom)/self.num_discrete_layers
        self.layer_tops = np.arange(
            self.top, self.bottom, -self.layer_thickness
        )
        top_rgb, bottom_rgb = [
            np.array(Color(color).get_rgb())
            for color in (self.top_color, self.bottom_color)
        ]
        epsilon = 1./(self.num_discrete_layers-1)
        self.layer_colors = [
            Color(rgb = interpolate(top_rgb, bottom_rgb, alpha))
            for alpha in np.arange(0, 1+epsilon, epsilon)
        ]

    def generate_layers(self):
        self.generate_layer_info()
        def create_region(top, color):
            return Region(
                lambda x, y : (y < top) & (y > top-self.layer_thickness),
                color = color
            )
        self.layers = [
            create_region(top, color)
            for top, color in zip(self.layer_tops, self.layer_colors)
        ]


    def generate_discrete_path(self):
        points = self.cycloid.points
        tops = list(self.layer_tops)
        tops.append(tops[-1]-self.layer_thickness)
        indices = [
            np.argmin(np.abs(points[:, 1]-top))
            for top in tops
        ]
        self.bend_points = points[indices[1:-1]]
        self.path_angles = []
        self.discrete_path = Mobject1D(
            color = YELLOW,
            density = 3*DEFAULT_POINT_DENSITY_1D
        )
        for start, end in zip(indices, indices[1:]):
            start_point, end_point = points[start], points[end]
            self.discrete_path.add_line(
                start_point, end_point
            )
            self.path_angles.append(
                angle_of_vector(start_point-end_point)-np.pi/2
            )
        self.discrete_path.add_line(
            points[end], FRAME_X_RADIUS*RIGHT+(self.layer_tops[-1]-1)*UP
        )

    def show_layer_variables(self):
        layer_top_pairs = list(zip(
            self.layer_tops[:self.num_variables], 
            self.layer_tops[1:]
        ))
        v_equations = []
        start_ys = []
        end_ys = []
        center_paths = []
        braces = []
        for (top1, top2), x in zip(layer_top_pairs, it.count(1)):
            eq_mob = TexMobject(
                ["v_%d"%x, "=", "\sqrt{\phantom{y_1}}"],
                size = "\\Large"
            )
            midpoint = UP*(top1+top2)/2
            eq_mob.shift(midpoint)
            v_eq = eq_mob.split()
            center_paths.append(Line(
                midpoint+FRAME_X_RADIUS*LEFT, 
                midpoint+FRAME_X_RADIUS*RIGHT
            ))            
            brace_endpoints = Mobject(
                Point(self.top*UP+x*RIGHT),
                Point(top2*UP+x*RIGHT)
            )
            brace = Brace(brace_endpoints, RIGHT)

            start_y = TexMobject("y_%d"%x, size = "\\Large")
            end_y = start_y.copy()            
            start_y.next_to(brace, RIGHT)
            end_y.shift(v_eq[-1].get_center())
            end_y.shift(0.2*RIGHT)

            v_equations.append(v_eq)
            start_ys.append(start_y)
            end_ys.append(end_y)
            braces.append(brace)

        for v_eq, path, time in zip(v_equations, center_paths, [2, 1, 0.5]):
            photon_run = self.photon_run_along_path(
                path,
                rate_func=linear
            )
            self.play(
                ShimmerIn(v_eq[0]),
                photon_run,
                run_time = time
            )
        self.wait()
        for start_y, brace in zip(start_ys, braces):
            self.add(start_y)            
            self.play(GrowFromCenter(brace))
        self.wait()
        quads = list(zip(v_equations, start_ys, end_ys, braces))
        self.equations = []
        for v_eq, start_y, end_y, brace in quads:
            self.remove(brace)
            self.play(
                ShowCreation(v_eq[1]),
                ShowCreation(v_eq[2]),
                Transform(start_y, end_y)
            )

            v_eq.append(start_y)
            self.equations.append(Mobject(*v_eq))

    def isolate_bend_points(self):
        arc_radius = 0.1
        self.activate_zooming()
        little_square = self.get_zoomed_camera_mobject()

        for index in range(3):
            bend_point = self.bend_points[index]
            line = Line(
                bend_point+DOWN, 
                bend_point+UP,
                color = WHITE,
                density = self.zoom_factor*DEFAULT_POINT_DENSITY_1D
            )
            angle_arcs = []
            for i, rotation in [(index, np.pi/2), (index+1, -np.pi/2)]:
                arc = Arc(angle = self.path_angles[i])
                arc.scale(arc_radius)
                arc.rotate(rotation)
                arc.shift(bend_point)
                angle_arcs.append(arc)
            thetas = []
            for i in [index+1, index+2]:
                theta = TexMobject("\\theta_%d"%i)
                theta.scale(0.5/self.zoom_factor)
                vert = UP if i == index+1 else DOWN
                horiz = rotate_vector(vert, np.pi/2)
                theta.next_to(
                    Point(bend_point), 
                    horiz, 
                    buff = 0.01
                )
                theta.shift(1.5*arc_radius*vert)
                thetas.append(theta)
            figure_marks = [line] + angle_arcs + thetas                

            self.play(ApplyMethod(
                little_square.shift,
                bend_point - little_square.get_center(),
                run_time = 2
            ))
            self.play(*list(map(ShowCreation, figure_marks)))
            self.wait()
            equation_frame = little_square.copy()
            equation_frame.scale(0.5)
            equation_frame.shift(
                little_square.get_corner(UP+RIGHT) - \
                equation_frame.get_corner(UP+RIGHT)
            )
            equation_frame.scale_in_place(0.9)
            self.show_snells(index+1, equation_frame)
            self.remove(*figure_marks)
        self.disactivate_zooming()

    def show_snells(self, index, frame):
        left_text, right_text = [
            "\\dfrac{\\sin(\\theta_%d)}{\\phantom{\\sqrt{y_1}}}"%x
            for x in (index, index+1)
        ]
        left, equals, right = TexMobject(
            [left_text, "=", right_text]
        ).split()
        vs = []
        sqrt_ys = []
        for x, numerator in [(index, left), (index+1, right)]:
            v, sqrt_y = [
                TexMobject(
                    text, size = "\\Large"
                ).next_to(numerator, DOWN)
                for text in ("v_%d"%x, "\\sqrt{y_%d}"%x)
            ]
            vs.append(v)
            sqrt_ys.append(sqrt_y)
        start, end = [
            Mobject(
                left.copy(), mobs[0], equals.copy(), right.copy(), mobs[1]
            ).replace(frame)
            for mobs in (vs, sqrt_ys)
        ]

        self.add(start)
        self.wait(2)
        self.play(Transform(
            start, end, 
            path_func = counterclockwise_path()
        ))
        self.wait(2)
        self.remove(start, end)

    def show_main_equation(self):
        self.equation = TexMobject("""
            \\dfrac{\\sin(\\theta)}{\\sqrt{y}} = 
            \\text{constant}
        """)
        self.equation.shift(LEFT)
        self.equation.shift(
            (self.layer_tops[0]-self.equation.get_top())*UP
        )
        self.add(self.equation)
        self.wait()

    def ask_continuous_question(self):
        continuous = self.get_continuous_background()
        line = Line(
            UP, DOWN,
            density = self.zoom_factor*DEFAULT_POINT_DENSITY_1D
        )
        theta = TexMobject("\\theta")
        theta.scale(0.5/self.zoom_factor)

        self.play(
            ShowCreation(continuous),
            Animation(self.equation)
        )
        self.remove(*self.layers)
        self.play(ShowCreation(self.cycloid))
        self.activate_zooming()
        little_square = self.get_zoomed_camera_mobject()

        self.add(line)
        indices = np.arange(
            0, self.cycloid.get_num_points()-1, 10
        )
        for index in indices:
            point = self.cycloid.points[index]
            next_point = self.cycloid.points[index+1]
            angle = angle_of_vector(point - next_point)
            for mob in little_square, line:
                mob.shift(point - mob.get_center())
            arc = Arc(angle-np.pi/2, start_angle = np.pi/2)
            arc.scale(0.1)
            arc.shift(point)
            self.add(arc)
            if angle > np.pi/2 + np.pi/6:
                vect_angle = interpolate(np.pi/2, angle, 0.5)
                vect = rotate_vector(RIGHT, vect_angle)
                theta.center()
                theta.shift(point)
                theta.shift(0.15*vect)
                self.add(theta)
            self.wait(self.frame_duration)
            self.remove(arc)