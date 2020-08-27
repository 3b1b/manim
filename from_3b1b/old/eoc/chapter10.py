from manimlib.imports import *

def derivative(func, x, n = 1, dx = 0.01):
    samples = [func(x + (k - n/2)*dx) for k in range(n+1)]
    while len(samples) > 1:
        samples = [
            (s_plus_dx - s)/dx
            for s, s_plus_dx in zip(samples, samples[1:])
        ]
    return samples[0]

def taylor_approximation(func, highest_term, center_point = 0):
    derivatives = [
        derivative(func, center_point, n = n)
        for n in range(highest_term + 1)
    ]
    coefficients = [
        d/math.factorial(n) 
        for n, d in enumerate(derivatives)
    ]
    return lambda x : sum([
        c*((x-center_point)**n) 
        for n, c in enumerate(coefficients)
    ])

class Chapter10OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            "For me, mathematics is a collection of ", 
            "examples", "; a ",
            "theorem", " is a statement about a collection of ",
            "examples", " and the purpose of proving ",
            "theorems", " is to classify and explain the ",
            "examples", "."
        ],
        "quote_arg_separator" : "",
        "highlighted_quote_terms" : {
            "examples" : BLUE,
        },
        "author" : "John B. Conway",
        "fade_in_kwargs" : {
            "run_time" : 7,
        }
    }

class ExampleApproximation(GraphScene):
    CONFIG = {
        "function" : lambda x : np.exp(-x**2),
        "function_tex" : "e^{-x^2}", 
        "function_color" : BLUE,
        "order_sequence" : [0, 2, 4],
        "center_point" : 0,
        "approximation_terms" : ["1 ", "-x^2", "+\\frac{1}{2}x^4"],
        "approximation_color" : GREEN,
        "x_min" : -3,
        "x_max" : 3,
        "y_min" : -1,
        "y_max" : 2,
        "graph_origin" : DOWN + 2*LEFT,
    }
    def construct(self):
        self.setup_axes()
        func_graph = self.get_graph(
            self.function,
            self.function_color,
        )
        approx_graphs = [
            self.get_graph(
                taylor_approximation(self.function, n),
                self.approximation_color
            )
            for n in self.order_sequence
        ]

        near_text = TextMobject(
            "Near %s $= %d$"%(
                self.x_axis_label, self.center_point
            )
        )
        near_text.to_corner(UP + RIGHT)
        near_text.add_background_rectangle()
        equation = TexMobject(
            self.function_tex, 
            "\\approx",
            *self.approximation_terms
        )
        equation.next_to(near_text, DOWN, MED_LARGE_BUFF)
        equation.to_edge(RIGHT)
        near_text.next_to(equation, UP, MED_LARGE_BUFF)
        equation.set_color_by_tex(
            self.function_tex, self.function_color,
            substring = False
        )
        approx_terms = VGroup(*[
            equation.get_part_by_tex(tex, substring = False)
            for tex in self.approximation_terms
        ])
        approx_terms.set_fill(
            self.approximation_color,
            opacity = 0,
        )
        equation.add_background_rectangle()

        approx_graph = VectorizedPoint(
            self.input_to_graph_point(self.center_point, func_graph)
        )

        self.play(
            ShowCreation(func_graph, run_time = 2),
            Animation(equation),
            Animation(near_text),
        )
        for graph, term in zip(approx_graphs, approx_terms):
            self.play(
                Transform(approx_graph, graph, run_time = 2),
                Animation(equation),
                Animation(near_text),
                term.set_fill, None, 1,
            )
            self.wait()
        self.wait(2)

class ExampleApproximationWithSine(ExampleApproximation):
    CONFIG = {
        "function" : np.sin,
        "function_tex" : "\\sin(x)", 
        "order_sequence" : [1, 3, 5],
        "center_point" : 0,
        "approximation_terms" : [
            "x", 
            "-\\frac{1}{6}x^3", 
            "+\\frac{1}{120}x^5",
        ],
        "approximation_color" : GREEN,
        "x_min" : -2*np.pi,
        "x_max" : 2*np.pi,
        "x_tick_frequency" : np.pi/2,
        "y_min" : -2,
        "y_max" : 2,
        "graph_origin" : DOWN + 2*LEFT,
    }

class ExampleApproximationWithExp(ExampleApproximation):
    CONFIG = {
        "function" : np.exp,
        "function_tex" : "e^x", 
        "order_sequence" : [1, 2, 3, 4],
        "center_point" : 0,
        "approximation_terms" : [
            "1 + x", 
            "+\\frac{1}{2}x^2", 
            "+\\frac{1}{6}x^3",
            "+\\frac{1}{24}x^4",
        ],
        "approximation_color" : GREEN,
        "x_min" : -3,
        "x_max" : 4,
        "y_min" : -1,
        "y_max" : 10,
        "graph_origin" : 2*DOWN + 3*LEFT,
    }

class Pendulum(ReconfigurableScene):
    CONFIG = {
        "anchor_point" : 3*UP + 4*LEFT,
        "radius" : 4,
        "weight_radius" : 0.2,
        "angle" : np.pi/6,
        "approx_tex" : [
            "\\approx 1 - ", "{\\theta", "^2", "\\over", "2}"
        ],
        "leave_original_cosine" : False,
        "perform_substitution" : True,
    }
    def construct(self):
        self.draw_pendulum()
        self.show_oscillation()
        self.show_height()
        self.get_angry_at_cosine()
        self.substitute_approximation()
        self.show_confusion()

    def draw_pendulum(self):
        pendulum = self.get_pendulum()
        ceiling = self.get_ceiling()

        self.add(ceiling)
        self.play(ShowCreation(pendulum.line))
        self.play(DrawBorderThenFill(pendulum.weight, run_time = 1))

        self.pendulum = pendulum

    def show_oscillation(self):
        trajectory_dots = self.get_trajectory_dots()
        kwargs = self.get_swing_kwargs()

        self.play(
            ShowCreation(
                trajectory_dots,
                rate_func=linear,
                run_time = kwargs["run_time"]
            ),
            Rotate(self.pendulum, -2*self.angle, **kwargs),
        )
        for m in 2, -2, 2:
            self.play(Rotate(self.pendulum, m*self.angle, **kwargs))
        self.wait()

    def show_height(self):
        v_line = self.get_v_line()
        h_line = self.get_h_line()
        radius_brace = self.get_radius_brace()
        height_brace = self.get_height_brace()
        height_tex = self.get_height_brace_tex(height_brace)
        arc, theta = self.get_arc_and_theta()

        height_tex_R = height_tex.get_part_by_tex("R")
        height_tex_theta = height_tex.get_part_by_tex("\\theta")
        to_write = VGroup(*[
            part
            for part in height_tex
            if part not in [height_tex_R, height_tex_theta]
        ])

        self.play(
            ShowCreation(h_line),
            GrowFromCenter(height_brace)
        )
        self.play(
            ShowCreation(v_line),
            ShowCreation(arc),
            Write(theta),
        )
        self.play(
            GrowFromCenter(radius_brace)
        )
        self.wait(2)
        self.play(
            Write(to_write),
            ReplacementTransform(
                radius_brace[-1].copy(),
                height_tex_R
            ),
            ReplacementTransform(
                theta.copy(),
                height_tex_theta
            ),
            run_time = 2
        )
        self.wait(2)

        self.arc = arc
        self.theta = theta
        self.height_tex_R = height_tex_R
        self.cosine = VGroup(*[
            height_tex.get_part_by_tex(tex)
            for tex in ("cos", "theta", ")")
        ])
        self.one_minus = VGroup(*[
            height_tex.get_part_by_tex(tex)
            for tex in ("\\big(1-", "\\big)")
        ])

    def get_angry_at_cosine(self):
        cosine = self.cosine
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        cosine.generate_target()
        cosine.save_state()
        cosine.target.next_to(morty, UP)
        if self.leave_original_cosine:
            cosine_copy = cosine.copy()
            self.add(cosine_copy)
            self.one_minus.add(cosine_copy)

        self.play(FadeIn(morty))
        self.play(
            MoveToTarget(cosine),
            morty.change, "angry", cosine.target,
        )
        self.wait()
        self.play(Blink(morty))
        self.wait()

        self.morty = morty

    def substitute_approximation(self):
        morty = self.morty
        cosine = self.cosine
        cosine.generate_target()
        cosine_approx = self.get_cosine_approx()
        cosine_approx.next_to(cosine, UP+RIGHT)
        cosine_approx.to_edge(RIGHT)
        cosine.target.next_to(
            cosine_approx, LEFT,
            align_using_submobjects = True
        )
        kwargs = self.get_swing_kwargs()

        self.play(
            FadeIn(
                cosine_approx,
                run_time = 2,
                lag_ratio = 0.5
            ),
            MoveToTarget(cosine),
            morty.change, "pondering", cosine_approx
        )
        self.wait()
        if not self.perform_substitution:
            return
        self.play(
            ApplyMethod(
                cosine_approx.theta_squared_over_two.copy().next_to,
                self.height_tex_R,
                run_time = 2,
            ),
            FadeOut(self.one_minus),
            morty.look_at, self.height_tex_R,
        )
        self.play(morty.change, "thinking", self.height_tex_R)
        self.transition_to_alt_config(
            angle = np.pi/12,
            transformation_kwargs = {"run_time" : 2},
        )

    def show_confusion(self):
        randy = Randolph(color = BLUE_C)
        randy.scale(0.8)
        randy.next_to(self.cosine, DOWN+LEFT)
        randy.to_edge(DOWN)

        self.play(FadeIn(randy))
        self.play(
            randy.change, "confused", self.cosine
        )
        self.play(randy.look_at, self.height_tex_R)
        self.wait()
        self.play(randy.look_at, self.cosine)
        self.play(Blink(randy))
        self.wait()

    #######

    def get_pendulum(self):
        line = Line(
            self.anchor_point,
            self.anchor_point + self.radius*DOWN,
            color = WHITE
        )
        weight = Circle(
            radius = self.weight_radius,
            fill_color = GREY,
            fill_opacity = 1,
            stroke_width = 0,
        )
        weight.move_to(line.get_end())
        result = VGroup(line, weight)
        result.rotate(
            self.angle, 
            about_point = self.anchor_point
        )
        result.line = line
        result.weight = weight

        return result

    def get_ceiling(self):
        line = Line(LEFT, RIGHT, color = GREY)
        line.scale(FRAME_X_RADIUS)
        line.move_to(self.anchor_point[1]*UP)
        return line

    def get_trajectory_dots(self, n_dots = 40, color = YELLOW):
        arc_angle = np.pi/6
        proportions = self.swing_rate_func(
            np.linspace(0, 1, n_dots)
        )
        angles = -2*arc_angle*proportions
        angle_to_point = lambda a : np.cos(a)*RIGHT + np.sin(a)*UP
        dots = VGroup(*[
            # Line(*map(angle_to_point, pair))
            Dot(angle_to_point(angle), radius = 0.005)
            for angle in angles
        ])
            
        dots.set_color(color)
        dots.scale(self.radius)
        dots.rotate(-np.pi/2 + arc_angle)
        dots.shift(self.anchor_point)
        return dots

    def get_v_line(self):
        return DashedLine(
            self.anchor_point, 
            self.anchor_point + self.radius*DOWN,
            color = WHITE
        )

    def get_h_line(self, color = BLUE):
        start = self.anchor_point + self.radius*DOWN
        end = start + self.radius*np.sin(self.angle)*RIGHT

        return Line(start, end, color = color)

    def get_radius_brace(self):
        v_line = self.get_v_line()
        brace = Brace(v_line, RIGHT)
        brace.rotate(self.angle, about_point = self.anchor_point)
        brace.add(brace.get_text("$R$", buff = SMALL_BUFF))
        return brace

    def get_height_brace(self):
        h_line = self.get_h_line()
        height = (1 - np.cos(self.angle))*self.radius
        line = Line(
            h_line.get_end(),
            h_line.get_end() + height*UP,
        )
        brace = Brace(line, RIGHT)
        return brace

    def get_height_brace_tex(self, brace):
        tex_mob = TexMobject(
            "R", "\\big(1-", "\\cos(", "\\theta", ")", "\\big)"
        )
        tex_mob.set_color_by_tex("theta", YELLOW)
        tex_mob.next_to(brace, RIGHT)
        return tex_mob

    def get_arc_and_theta(self):
        arc = Arc(
            start_angle = -np.pi/2,
            angle = self.angle,
            color = YELLOW
        )
        theta = TexMobject("\\theta")
        theta.set_color(YELLOW)
        theta.next_to(
            arc.point_from_proportion(0.5), 
            DOWN, SMALL_BUFF
        )
        for mob in arc, theta:
            mob.shift(self.anchor_point)
        return arc, theta

    def get_cosine_approx(self):
        approx = TexMobject(*self.approx_tex)
        approx.set_color_by_tex("theta", YELLOW)
        approx.theta_squared_over_two = VGroup(*approx[1:5])

        return approx

    def get_swing_kwargs(self):
        return {
            "about_point" : self.anchor_point,
            "run_time" : 1.7,
            "rate_func" : self.swing_rate_func,
        }

    def swing_rate_func(self, t):
        return (1-np.cos(np.pi*t))/2.0

class PendulumWithBetterApprox(Pendulum):
    CONFIG = {
        "approx_tex" : [
            "\\approx 1 - ", "{\\theta", "^2", "\\over", "2}",
            "+", "{\\theta", "^4", "\\over", "24}"
        ],
        "leave_original_cosine" : True,
        "perform_substitution" : False,
    }
    def show_confusion(self):
        pass

class ExampleApproximationWithCos(ExampleApproximationWithSine):
    CONFIG = {
        "function" : np.cos,
        "function_tex" : "\\cos(\\theta)", 
        "order_sequence" : [0, 2],
        "approximation_terms" : [
            "1", 
            "-\\frac{1}{2} \\theta ^2", 
        ],
        "x_axis_label" : "$\\theta$",
        "y_axis_label" : "",
        "x_axis_width" : 13,
        "graph_origin" : DOWN,
    }

    def construct(self):
        ExampleApproximationWithSine.construct(self)
        randy = Randolph(color = BLUE_C)
        randy.to_corner(DOWN+LEFT)
        high_graph = self.get_graph(lambda x : 4)
        v_lines, alt_v_lines = [
            VGroup(*[
                self.get_vertical_line_to_graph(
                    u*dx, high_graph,
                    line_class = DashedLine,
                    color = YELLOW
                )
                for u in (-1, 1)
            ])
            for dx in (0.01, 0.7)
        ]

        self.play(*list(map(ShowCreation, v_lines)), run_time = 2)
        self.play(Transform(
            v_lines, alt_v_lines,
            run_time = 2,
        ))
        self.play(FadeIn(randy))
        self.play(PiCreatureBubbleIntroduction(
            randy, "How...?",
            bubble_class = ThoughtBubble,
            look_at_arg = self.graph_origin,
            target_mode = "confused"
        ))
        self.wait(2)
        self.play(Blink(randy))
        self.wait()

    def setup_axes(self):
        GraphScene.setup_axes(self)
        x_val_label_pairs = [
            (-np.pi, "-\\pi"),
            (np.pi, "\\pi"),
            (2*np.pi, "2\\pi"),
        ]
        self.x_axis_labels = VGroup()
        for x_val, label in x_val_label_pairs:
            tex = TexMobject(label)
            tex.next_to(self.coords_to_point(x_val, 0), DOWN)
            self.add(tex)
            self.x_axis_labels.add(tex)

class ConstructQuadraticApproximation(ExampleApproximationWithCos):
    CONFIG = {
        "x_axis_label" : "$x$",
        "colors" : [BLUE, YELLOW, GREEN],
    }
    def construct(self):
        self.setup_axes()
        self.add_cosine_graph()
        self.add_quadratic_graph()
        self.introduce_quadratic_constants()
        self.show_value_at_zero()
        self.set_c0_to_one()
        self.let_c1_and_c2_vary()
        self.show_tangent_slope()
        self.compute_cosine_derivative()
        self.compute_polynomial_derivative()
        self.let_c2_vary()
        self.point_out_negative_concavity()
        self.compute_cosine_second_derivative()
        self.show_matching_curvature()
        self.show_matching_tangent_lines()
        self.compute_polynomial_second_derivative()
        self.box_final_answer()

    def add_cosine_graph(self):
        cosine_label = TexMobject("\\cos(x)")
        cosine_label.to_corner(UP+LEFT)
        cosine_graph = self.get_graph(np.cos)
        dot = Dot(color = WHITE)
        dot.move_to(cosine_label)
        for mob in cosine_label, cosine_graph:
            mob.set_color(self.colors[0])

        def update_dot(dot):
            dot.move_to(cosine_graph.points[-1])
            return dot

        self.play(Write(cosine_label, run_time = 1))
        self.play(dot.move_to, cosine_graph.points[0])
        self.play(
            ShowCreation(cosine_graph),
            UpdateFromFunc(dot, update_dot),
            run_time = 4
        )
        self.play(FadeOut(dot))

        self.cosine_label = cosine_label
        self.cosine_graph = cosine_graph

    def add_quadratic_graph(self):
        quadratic_graph = self.get_quadratic_graph()

        self.play(ReplacementTransform(
            self.cosine_graph.copy(),
            quadratic_graph,
            run_time = 3
        ))

        self.quadratic_graph = quadratic_graph

    def introduce_quadratic_constants(self):
        quadratic_tex = self.get_quadratic_tex("c_0", "c_1", "c_2")
        const_terms = quadratic_tex.get_parts_by_tex("c")
        free_to_change = TextMobject("Free to change")
        free_to_change.next_to(const_terms, DOWN, LARGE_BUFF)
        arrows = VGroup(*[
            Arrow(
                free_to_change.get_top(),
                const.get_bottom(),
                tip_length = 0.75*Arrow.CONFIG["tip_length"],
                color = const.get_color()
            )
            for const in const_terms
        ])
        alt_consts_list = [
            (0, -1, -0.25),
            (1, -1, -0.25),
            (1, 0, -0.25),
            (),
        ]

        self.play(FadeIn(
            quadratic_tex, 
            run_time = 3,
            lag_ratio = 0.5
        ))
        self.play(
            FadeIn(free_to_change),
            *list(map(ShowCreation, arrows))
        )
        self.play(*[
            ApplyMethod(
                const.scale_in_place, 0.8,
                run_time = 2,
                rate_func = squish_rate_func(there_and_back, a, a + 0.75)
            )
            for const, a in zip(const_terms, np.linspace(0, 0.25, len(const_terms)))
        ])
        for alt_consts in alt_consts_list:
            self.change_quadratic_graph(
                self.quadratic_graph, *alt_consts
            )
            self.wait()

        self.quadratic_tex = quadratic_tex
        self.free_to_change_group = VGroup(free_to_change, *arrows)
        self.free_to_change_group.arrows = arrows

    def show_value_at_zero(self):
        arrow, x_equals_0 = ax0_group = self.get_arrow_x_equals_0_group()
        ax0_group.next_to(
            self.cosine_label, RIGHT,
            align_using_submobjects = True
        )
        one = TexMobject("1")
        one.next_to(arrow, RIGHT)
        one.save_state()
        one.move_to(self.cosine_label)
        one.set_fill(opacity = 0)

        v_line = self.get_vertical_line_to_graph(
            0, self.cosine_graph,
            line_class = DashedLine, 
            color = YELLOW
        )

        self.play(ShowCreation(v_line))
        self.play(
            ShowCreation(arrow),
            Write(x_equals_0, run_time = 2)
        )
        self.play(one.restore)
        self.wait()

        self.v_line = v_line
        self.equals_one_group = VGroup(arrow, x_equals_0, one)

    def set_c0_to_one(self):
        poly_at_zero = self.get_quadratic_tex(
            "c_0", "c_1", "c_2", arg = "0"
        )
        poly_at_zero.next_to(self.quadratic_tex, DOWN)
        equals_c0 = TexMobject("=", "c_0", "+0")
        equals_c0.set_color_by_tex("c_0", self.colors[0])
        equals_c0.next_to(
            poly_at_zero.get_part_by_tex("="), DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        poly_group = VGroup(
            equals_c0,
            poly_at_zero,
            self.quadratic_tex,
        )
        poly_group_target = VGroup(
            TexMobject("=", "1", "+0").set_color_by_tex("1", self.colors[0]),
            self.get_quadratic_tex("1", "c_1", "c_2", arg = "0"),
            self.get_quadratic_tex("1", "c_1", "c_2"),
        )
        for start, target in zip(poly_group, poly_group_target):
            target.move_to(start)

        self.play(FadeOut(self.free_to_change_group))
        self.play(ReplacementTransform(
            self.quadratic_tex.copy(),
            poly_at_zero
        ))
        self.wait(2)
        self.play(FadeIn(equals_c0))
        self.wait(2)
        self.play(Transform(
            poly_group, poly_group_target,
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.wait(2)
        self.play(*list(map(FadeOut, [poly_at_zero, equals_c0])))

        self.free_to_change_group.remove(
            self.free_to_change_group.arrows[0]
        )
        self.play(FadeIn(self.free_to_change_group))

    def let_c1_and_c2_vary(self):
        alt_consts_list = [
            (1, 1, -0.25),
            (1, -1, -0.25),
            (1, -1, 0.25),
            (1, 1, -0.1),
        ]

        for alt_consts in alt_consts_list:
            self.change_quadratic_graph(
                self.quadratic_graph,
                *alt_consts
            )
            self.wait()

    def show_tangent_slope(self):
        graph_point_at_zero = self.input_to_graph_point(
            0, self.cosine_graph
        ) 
        tangent_line = self.get_tangent_line(0, self.cosine_graph)

        self.play(ShowCreation(tangent_line))
        self.change_quadratic_graph(
            self.quadratic_graph, 1, 0, -0.1
        )
        self.wait()
        self.change_quadratic_graph(
            self.quadratic_graph, 1, 1, -0.1
        )
        self.wait(2)
        self.change_quadratic_graph(
            self.quadratic_graph, 1, 0, -0.1
        )
        self.wait(2)

        self.tangent_line = tangent_line

    def compute_cosine_derivative(self):
        derivative, rhs = self.get_cosine_derivative()


        self.play(FadeIn(
            VGroup(derivative, *rhs[:2]),
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.wait(2)
        self.play(Write(VGroup(*rhs[2:])), run_time = 2)
        self.wait()
        self.play(Rotate(
            self.tangent_line, np.pi/12,
            in_place = True,
            run_time = 3,
            rate_func = wiggle
        ))
        self.wait()

    def compute_polynomial_derivative(self):
        derivative = self.get_quadratic_derivative("c_1", "c_2")
        derivative_at_zero = self.get_quadratic_derivative(
            "c_1", "c_2", arg = "0"
        )
        equals_c1 = TexMobject("=", "c_1", "+0")
        equals_c1.next_to(
            derivative_at_zero.get_part_by_tex("="), DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT,
        )
        equals_c1.set_color_by_tex("c_1", self.colors[1])
        poly_group = VGroup(
            equals_c1,
            derivative,
            self.quadratic_tex
        )
        poly_group_target = VGroup(
            TexMobject("=", "0", "+0").set_color_by_tex(
                "0", self.colors[1], substring = False
            ),
            self.get_quadratic_derivative("0", "c_2", arg = "0"),
            self.get_quadratic_tex("1", "0", "c_2")
        )
        for start, target in zip(poly_group, poly_group_target):
            target.move_to(start)

        self.play(FadeOut(self.free_to_change_group))
        self.play(FadeIn(
            derivative, 
            run_time = 3,
            lag_ratio = 0.5
        ))
        self.wait()
        self.play(Transform(
            derivative, derivative_at_zero,
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.wait(2)
        self.play(Write(equals_c1))
        self.wait(2)
        self.play(Transform(
            poly_group, poly_group_target,
            run_time = 3,
            lag_ratio = 0.5
        ))
        self.wait(2)

        self.play(*list(map(FadeOut, poly_group[:-1])))
        self.free_to_change_group.remove(
            self.free_to_change_group.arrows[1]
        )
        self.play(FadeIn(self.free_to_change_group))

    def let_c2_vary(self):
        alt_c2_values = [-1, -0.05, 1, -0.2]
        for alt_c2 in alt_c2_values:
            self.change_quadratic_graph(
                self.quadratic_graph,
                1, 0, alt_c2
            )
            self.wait()

    def point_out_negative_concavity(self):
        partial_cosine_graph = self.get_graph(
            np.cos,
            x_min = -1, 
            x_max = 1,
            color = PINK
        )

        self.play(ShowCreation(partial_cosine_graph, run_time = 2))
        self.wait()
        for x, run_time in (-1, 2), (1, 4):
            self.play(self.get_tangent_line_change_anim(
                self.tangent_line, x, self.cosine_graph,
                run_time = run_time
            ))
            self.wait()
        self.play(*list(map(FadeOut, [
            partial_cosine_graph, self.tangent_line
        ])))

    def compute_cosine_second_derivative(self):
        second_deriv, rhs = self.get_cosine_second_derivative()

        self.play(FadeIn(
            VGroup(second_deriv, *rhs[1][:2]),
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.wait(3)
        self.play(Write(VGroup(*rhs[1][2:]), run_time = 2))
        self.wait()

    def show_matching_curvature(self):
        alt_consts_list = [
            (1, 1, -0.2),
            (1, 0, -0.2),
            (1, 0, -0.5),
        ]
        for alt_consts in alt_consts_list:
            self.change_quadratic_graph(
                self.quadratic_graph,
                *alt_consts
            )
            self.wait()

    def show_matching_tangent_lines(self):
        graphs = [self.quadratic_graph, self.cosine_graph]
        tangent_lines = [
            self.get_tangent_line(0, graph, color = color)
            for graph, color in zip(graphs, [WHITE, YELLOW])
        ]
        tangent_change_anims = [
            self.get_tangent_line_change_anim(
                line, np.pi/2, graph, 
                run_time = 6,
                rate_func = there_and_back,
            )
            for line, graph in zip(tangent_lines, graphs)
        ]

        self.play(*list(map(ShowCreation, tangent_lines)))
        self.play(*tangent_change_anims)
        self.play(*list(map(FadeOut, tangent_lines)))

    def compute_polynomial_second_derivative(self):
        c2s = ["c_2", "\\text{\\tiny $\\left(-\\frac{1}{2}\\right)$}"]
        derivs = [
            self.get_quadratic_derivative("0", c2)
            for c2 in c2s
        ]
        second_derivs = [
            TexMobject(
                "{d^2 P \\over dx^2}", "(x)", "=", "2", c2
            )
            for c2 in c2s
        ]
        for deriv, second_deriv in zip(derivs, second_derivs):
            second_deriv[0].scale(
                0.7, about_point = second_deriv[0].get_right()
            )
            second_deriv[-1].set_color(self.colors[-1])
            second_deriv.next_to(
                deriv, DOWN, 
                buff = MED_LARGE_BUFF,
                aligned_edge = LEFT
            )

        poly_group = VGroup(
            second_derivs[0], 
            derivs[0],
            self.quadratic_tex
        )
        poly_group_target = VGroup(
            second_derivs[1],
            derivs[1],
            self.get_quadratic_tex("1", "0", c2s[1])
        )
        for tex_mob in poly_group_target:
            tex_mob.get_part_by_tex(c2s[1]).shift(SMALL_BUFF*UP)

        self.play(FadeOut(self.free_to_change_group))
        self.play(FadeIn(derivs[0]))
        self.wait(2)
        self.play(Write(second_derivs[0]))
        self.wait(2)
        self.play(Transform(
            poly_group, poly_group_target,
            run_time = 3,
            lag_ratio = 0.5
        ))
        self.wait(3)

    def box_final_answer(self):
        box = Rectangle(stroke_color = PINK)
        box.stretch_to_fit_width(
            self.quadratic_tex.get_width() + MED_LARGE_BUFF
        )
        box.stretch_to_fit_height(
            self.quadratic_tex.get_height() + MED_LARGE_BUFF
        )
        box.move_to(self.quadratic_tex)

        self.play(ShowCreation(box, run_time = 2))
        self.wait(2)

    ######

    def change_quadratic_graph(self, graph, *args, **kwargs):
        transformation_kwargs = {}
        transformation_kwargs["run_time"] = kwargs.pop("run_time", 2)
        transformation_kwargs["rate_func"] = kwargs.pop("rate_func", smooth)
        new_graph = self.get_quadratic_graph(*args, **kwargs)
        self.play(Transform(graph, new_graph, **transformation_kwargs))
        graph.underlying_function = new_graph.underlying_function

    def get_quadratic_graph(self, c0 = 1, c1 = 0, c2 = -0.5):
        return self.get_graph(
            lambda x : c0 + c1*x + c2*x**2,
            color = self.colors[2]
        )

    def get_quadratic_tex(self, c0, c1, c2, arg = "x"):
        tex_mob = TexMobject(
            "P(", arg, ")", "=", 
            c0, "+", c1, arg, "+", c2, arg, "^2"
        )
        for tex, color in zip([c0, c1, c2], self.colors):
            tex_mob.set_color_by_tex(tex, color)
        tex_mob.to_corner(UP+RIGHT)
        return tex_mob

    def get_quadratic_derivative(self, c1, c2, arg = "x"):
        result = TexMobject(
            "{dP \\over dx}", "(", arg, ")", "=",
            c1, "+", "2", c2, arg
        )
        result[0].scale(0.7, about_point = result[0].get_right())
        for index, color in zip([5, 8], self.colors[1:]):
            result[index].set_color(color)
        if hasattr(self, "quadratic_tex"):
            result.next_to(
                self.quadratic_tex, DOWN,
                buff = MED_LARGE_BUFF,
                aligned_edge = LEFT
            )
        return result

    def get_arrow_x_equals_0_group(self):
        arrow = Arrow(LEFT, RIGHT)
        x_equals_0 = TexMobject("x = 0")
        x_equals_0.scale(0.75)
        x_equals_0.next_to(arrow.get_center(), UP, 2*SMALL_BUFF)
        x_equals_0.shift(SMALL_BUFF*LEFT)
        return VGroup(arrow, x_equals_0)

    def get_tangent_line(self, x, graph, color = YELLOW):
        tangent_line = Line(LEFT, RIGHT, color = color)
        tangent_line.rotate(self.angle_of_tangent(x, graph))
        tangent_line.scale(2)
        tangent_line.move_to(self.input_to_graph_point(x, graph))
        return tangent_line

    def get_tangent_line_change_anim(self, tangent_line, new_x, graph, **kwargs):
        start_x = self.x_axis.point_to_number(
            tangent_line.get_center()
        )
        def update(tangent_line, alpha):
            x = interpolate(start_x, new_x, alpha)
            new_line = self.get_tangent_line(
                x, graph, color = tangent_line.get_color()
            )
            Transform(tangent_line, new_line).update(1)
            return tangent_line
        return UpdateFromAlphaFunc(tangent_line, update, **kwargs)

    def get_cosine_derivative(self):
        if not hasattr(self, "cosine_label"):
            self.cosine_label = TexMobject("\\cos(x)")
            self.cosine_label.to_corner(UP+LEFT)
        derivative = TexMobject(
            "{d(", "\\cos", ")", "\\over", "dx}", "(0)",
        )
        derivative.set_color_by_tex("\\cos", self.colors[0])
        derivative.scale(0.7)
        derivative.next_to(
            self.cosine_label, DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        rhs = TexMobject("=", "-\\sin(0)", "=", "0")
        rhs.set_color_by_tex("\\sin", self.colors[1])
        rhs.scale(0.75)
        rhs.next_to(
            derivative, RIGHT,
            align_using_submobjects = True
        )

        self.cosine_derivative = VGroup(derivative, rhs)
        return self.cosine_derivative

    def get_cosine_second_derivative(self):
        if not hasattr(self, "cosine_derivative"):
            self.get_cosine_derivative()
        second_deriv = TexMobject(
            "{d^2(", "\\cos", ")", "\\over", "dx^2}", 
            "(", "0", ")",
        )
        second_deriv.set_color_by_tex("cos", self.colors[0])
        second_deriv.set_color_by_tex("-\\cos", self.colors[2])
        second_deriv.scale(0.75)
        second_deriv.add_background_rectangle()
        second_deriv.next_to(
            self.cosine_derivative, DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        rhs = TexMobject("=", "-\\cos(0)", "=", "-1")
        rhs.set_color_by_tex("cos", self.colors[2])
        rhs.scale(0.8)
        rhs.next_to(
            second_deriv, RIGHT, 
            align_using_submobjects = True
        )
        rhs.add_background_rectangle()

        self.cosine_second_derivative = VGroup(second_deriv, rhs)
        return self.cosine_second_derivative

class ReflectOnQuadraticApproximation(TeacherStudentsScene):
    def construct(self):
        self.show_example_approximation()
        # self.add_polynomial()
        # self.show_c0()
        # self.show_c1()
        # self.show_c2()

    def show_example_approximation(self):
        approx_at_x, approx_at_point = [
            TexMobject(
                "\\cos(", s, ")", "\\approx",
                "1 - \\frac{1}{2}", "(", s, ")", "^2"
            ).next_to(self.get_students(), UP, 2)
            for s in ("x", "0.1",)
        ]
        approx_rhs = TexMobject("=", "0.995")
        approx_rhs.next_to(approx_at_point, RIGHT)
        real_result = TexMobject(
            "\\cos(", "0.1", ")", "=", 
            "%.7f\\dots"%np.cos(0.1)
        )
        real_result.shift(
            approx_rhs.get_part_by_tex("=").get_center() -\
            real_result.get_part_by_tex("=").get_center()
        )
        for mob in approx_at_point, real_result:
            mob.set_color_by_tex("0.1", YELLOW)
        real_result.set_fill(opacity = 0)

        self.play(
            Write(approx_at_x, run_time = 2),
            self.teacher.change_mode, "raise_right_hand"
        )
        self.wait(2)
        self.play(ReplacementTransform(
            approx_at_x, approx_at_point,
        ))
        self.wait()
        self.play(Write(approx_rhs))
        self.wait(2)
        self.play(
            real_result.shift, 1.5*DOWN,
            real_result.set_fill, None, 1,
        )
        self.change_student_modes(*["hooray"]*3)
        self.wait(2)
        self.change_student_modes(
            *["plain"]*3,
            added_anims = list(map(FadeOut, [
                approx_at_point, approx_rhs, real_result
            ])),
            look_at_arg = approx_at_x
        )

    def add_polynomial(self):
        polynomial = self.get_polynomial()
        const_terms = polynomial.get_parts_by_tex("c")

        self.play(
            Write(polynomial),
            self.teacher.change, "pondering"
        )
        self.wait(2)
        self.play(*[
            ApplyMethod(
                const.shift, MED_LARGE_BUFF*UP,
                run_time = 2,
                rate_func = squish_rate_func(there_and_back, a, a+0.7)
            )
            for const, a in zip(const_terms, np.linspace(0, 0.3, len(const_terms)))
        ])
        self.wait()

        self.const_terms = const_terms
        self.polynomial = polynomial

    def show_c0(self):
        c0 = self.polynomial.get_part_by_tex("c_0")
        c0.save_state()
        equation = TexMobject("P(0) = \\cos(0)")
        equation.to_corner(UP+RIGHT)
        new_polynomial = self.get_polynomial(c0 = "1")

        self.play(c0.shift, UP)
        self.play(Write(equation))
        self.wait()
        self.play(Transform(self.polynomial, new_polynomial))
        self.play(FadeOut(equation))

    def show_c1(self):
        c1 = self.polynomial.get_part_by_tex("c_1")
        c1.save_state()
        equation = TexMobject(
            "\\frac{dP}{dx}(0) = \\frac{d(\\cos)}{dx}(0)"
        )
        equation.to_corner(UP+RIGHT)
        new_polynomial = self.get_polynomial(c0 = "1", c1 = "0")

        self.play(c1.shift, UP)
        self.play(Write(equation))
        self.wait()
        self.play(Transform(self.polynomial, new_polynomial))
        self.wait()
        self.play(FadeOut(equation))

    def show_c2(self):
        c2 = self.polynomial.get_part_by_tex("c_2")
        c2.save_state()
        equation = TexMobject(
            "\\frac{d^2 P}{dx^2}(0) = \\frac{d^2(\\cos)}{dx^2}(0)"
        )
        equation.to_corner(UP+RIGHT)
        alt_c2_tex = "\\text{\\tiny $\\left(-\\frac{1}{2}\\right)$}"
        new_polynomial = self.get_polynomial(
            c0 = "1", c1 = "0", c2 = alt_c2_tex
        )
        new_polynomial.get_part_by_tex(alt_c2_tex).shift(SMALL_BUFF*UP)

        self.play(c2.shift, UP)
        self.play(FadeIn(equation))
        self.wait(2)
        self.play(Transform(self.polynomial, new_polynomial))
        self.wait(2)
        self.play(FadeOut(equation))

    #####

    def get_polynomial(self, c0 = "c_0", c1 = "c_1", c2 = "c_2"):
        polynomial = TexMobject(
            "P(x) = ", c0, "+", c1, "x", "+", c2, "x^2"
        )
        colors = ConstructQuadraticApproximation.CONFIG["colors"]
        for tex, color in zip([c0, c1, c2], colors):
            polynomial.set_color_by_tex(tex, color, substring = False)

        polynomial.next_to(self.teacher, UP, LARGE_BUFF)
        polynomial.to_edge(RIGHT)
        return polynomial

class ReflectionOnQuadraticSupplement(ConstructQuadraticApproximation):
    def construct(self):
        self.setup_axes()
        self.add(self.get_graph(np.cos, color = self.colors[0]))
        quadratic_graph = self.get_quadratic_graph()
        self.add(quadratic_graph)

        self.wait()
        for c0 in 0, 2, 1:
            self.change_quadratic_graph(
                quadratic_graph,
                c0 = c0
            )
        self.wait(2)
        for c1 in 1, -1, 0:
            self.change_quadratic_graph(
                quadratic_graph,
                c1 = c1
            )
        self.wait(2)
        for c2 in -0.1, -1, -0.5:
            self.change_quadratic_graph(
                quadratic_graph,
                c2 = c2
            )
        self.wait(2)

class SimilarityOfChangeBehavior(ConstructQuadraticApproximation):
    def construct(self):
        colors = [YELLOW, WHITE]
        max_x = np.pi/2

        self.setup_axes()        
        cosine_graph = self.get_graph(np.cos, color = self.colors[0])
        quadratic_graph = self.get_quadratic_graph()
        graphs = VGroup(cosine_graph, quadratic_graph)
        dots = VGroup()
        for graph, color in zip(graphs, colors):
            dot = Dot(color = color)
            dot.move_to(self.input_to_graph_point(0, graph))
            dot.graph = graph
            dots.add(dot)

        def update_dot(dot, alpha):
            x = interpolate(0, max_x, alpha)
            dot.move_to(self.input_to_graph_point(x, dot.graph))
        dot_anims = [
            UpdateFromAlphaFunc(dot, update_dot, run_time = 3)
            for dot in dots
        ]
        tangent_lines = VGroup(*[
            self.get_tangent_line(0, graph, color)
            for graph, color in zip(graphs, colors)
        ])
        tangent_line_movements = [
            self.get_tangent_line_change_anim(
                line, max_x, graph,
                run_time = 5,
            )
            for line, graph in zip(tangent_lines, graphs)
        ]

        self.add(cosine_graph, quadratic_graph)
        self.play(FadeIn(dots))
        self.play(*dot_anims)
        self.play(
            FadeIn(tangent_lines),
            FadeOut(dots)
        )
        self.play(*tangent_line_movements + dot_anims, run_time = 6)
        self.play(*list(map(FadeOut, [tangent_lines, dots])))
        self.wait()

class MoreTerms(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "More terms!",
            target_mode = "surprised",
        )
        self.change_student_modes(*["hooray"]*3)
        self.wait(3)

class CubicAndQuarticApproximations(ConstructQuadraticApproximation):
    CONFIG = {
        "colors": [BLUE, YELLOW, GREEN, RED, MAROON_B],
    }
    def construct(self):
        self.add_background()
        self.take_third_derivative_of_cubic()
        self.show_third_derivative_of_cosine()
        self.set_c3_to_zero()
        self.show_cubic_curves()
        self.add_quartic_term()
        self.show_fourth_derivative_of_cosine()
        self.take_fourth_derivative_of_quartic()
        self.solve_for_c4()
        self.show_quartic_approximation()


    def add_background(self):
        self.setup_axes()
        self.cosine_graph = self.get_graph(
            np.cos, color = self.colors[0]
        )
        self.quadratic_graph = self.get_quadratic_graph()
        self.big_rect = Rectangle(
            height = FRAME_HEIGHT,
            width = FRAME_WIDTH,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 0.5,
        )
        self.add(
            self.cosine_graph, self.quadratic_graph,
            self.big_rect
        )

        self.cosine_label = TexMobject("\\cos", "(0)", "=1")
        self.cosine_label.set_color_by_tex("cos", self.colors[0])
        self.cosine_label.scale(0.75)
        self.cosine_label.to_corner(UP+LEFT)
        self.add(self.cosine_label)
        self.add(self.get_cosine_derivative())
        self.add(self.get_cosine_second_derivative())

        self.polynomial = TexMobject(
            "P(x)=", "1", "-\\frac{1}{2}", "x^2"
        )
        self.polynomial.set_color_by_tex("1", self.colors[0])
        self.polynomial.set_color_by_tex("-\\frac{1}{2}", self.colors[2])
        self.polynomial.to_corner(UP+RIGHT)
        self.polynomial.quadratic_part = VGroup(
            *self.polynomial[1:]
        )
        self.add(self.polynomial)

    def take_third_derivative_of_cubic(self):
        polynomial = self.polynomial
        plus_cubic_term = TexMobject("+\\,", "c_3", "x^3")
        plus_cubic_term.next_to(polynomial, RIGHT)
        plus_cubic_term.to_edge(RIGHT, buff = LARGE_BUFF)
        plus_cubic_term.set_color_by_tex("c_3", self.colors[3])
        plus_cubic_copy = plus_cubic_term.copy()

        polynomial.generate_target()
        polynomial.target.next_to(plus_cubic_term, LEFT)

        self.play(FocusOn(polynomial))
        self.play(
            MoveToTarget(polynomial),
            GrowFromCenter(plus_cubic_term)
        )
        self.wait()

        brace = Brace(polynomial.quadratic_part, DOWN)
        third_derivative = TexMobject(
            "\\frac{d^3 P}{dx^3}(x) = ", "0"
        )
        third_derivative.shift(
            brace.get_bottom() + MED_SMALL_BUFF*DOWN -\
            third_derivative.get_part_by_tex("0").get_top()
        )        

        self.play(Write(third_derivative[0]))
        self.play(GrowFromCenter(brace))
        self.play(ReplacementTransform(
            polynomial.quadratic_part.copy(),
            VGroup(third_derivative[1])
        ))
        self.wait(2)
        self.play(plus_cubic_copy.next_to, third_derivative, RIGHT)
        derivative_term = self.take_derivatives_of_monomial(
            VGroup(*plus_cubic_copy[1:])
        )
        third_derivative.add(plus_cubic_copy[0], derivative_term)

        self.plus_cubic_term = plus_cubic_term
        self.polynomial_third_derivative = third_derivative
        self.polynomial_third_derivative_brace = brace

    def show_third_derivative_of_cosine(self):
        cosine_third_derivative = self.get_cosine_third_derivative()
        dot = Dot(fill_opacity = 0.5)
        dot.move_to(self.polynomial_third_derivative)

        self.play(
            dot.move_to, cosine_third_derivative,
            dot.set_fill, None, 0
        )
        self.play(ReplacementTransform(
            self.cosine_second_derivative.copy(),
            cosine_third_derivative
        ))
        self.wait(2)
        dot.set_fill(opacity = 0.5)
        self.play(
            dot.move_to, self.polynomial_third_derivative.get_right(),
            dot.set_fill, None, 0,
        )
        self.wait()

    def set_c3_to_zero(self):
        c3s = VGroup(
            self.polynomial_third_derivative[-1][-1],
            self.plus_cubic_term.get_part_by_tex("c_3")
        )
        zeros = VGroup(*[
            TexMobject("0").move_to(c3)
            for c3 in c3s
        ])
        zeros.set_color(self.colors[3])
        zeros.shift(SMALL_BUFF*UP)
        zeros[0].shift(0.25*SMALL_BUFF*(UP+LEFT))

        self.play(Transform(
            c3s, zeros, 
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.wait(2)

    def show_cubic_curves(self):
        real_graph = self.quadratic_graph
        real_graph.save_state()
        graph = real_graph.copy()
        graph.save_state()
        alt_graphs = [
            self.get_graph(func, color = real_graph.get_color())
            for func in [
                lambda x : x*(x-1)*(x+1),
                lambda x : 1 - 0.5*(x**2) + 0.2*(x**3)
            ]
        ]

        self.play(FadeIn(graph))
        real_graph.set_stroke(width = 0)
        for alt_graph in alt_graphs:
            self.play(Transform(graph, alt_graph, run_time = 2))
            self.wait()
        self.play(graph.restore, run_time = 2)
        real_graph.restore()
        self.play(FadeOut(graph))

    def add_quartic_term(self):
        polynomial = self.polynomial
        plus_quartic_term = TexMobject("+\\,", "c_4", "x^4")
        plus_quartic_term.next_to(polynomial, RIGHT)
        plus_quartic_term.set_color_by_tex("c_4", self.colors[4])

        self.play(*list(map(FadeOut, [
            self.plus_cubic_term,
            self.polynomial_third_derivative,
            self.polynomial_third_derivative_brace,
        ])))
        self.play(Write(plus_quartic_term))
        self.wait()

        self.plus_quartic_term = plus_quartic_term

    def show_fourth_derivative_of_cosine(self):
        cosine_fourth_derivative = self.get_cosine_fourth_derivative()

        self.play(FocusOn(self.cosine_third_derivative))
        self.play(ReplacementTransform(
            self.cosine_third_derivative.copy(),
            cosine_fourth_derivative
        ))
        self.wait(3)

    def take_fourth_derivative_of_quartic(self):
        quartic_term = VGroup(*self.plus_quartic_term.copy()[1:])
        fourth_deriv_lhs = TexMobject("{d^4 P \\over dx^4}(x)", "=")
        fourth_deriv_lhs.next_to(
            self.polynomial, DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        alt_rhs = TexMobject("=", "24 \\cdot", "c_4")
        alt_rhs.next_to(
            fourth_deriv_lhs.get_part_by_tex("="), DOWN,
            buff = LARGE_BUFF,
            aligned_edge = LEFT
        )
        alt_rhs.set_color_by_tex("c_4", self.colors[4])

        self.play(Write(fourth_deriv_lhs))
        self.play(
            quartic_term.next_to, fourth_deriv_lhs, RIGHT
        )
        self.wait()
        fourth_deriv_rhs = self.take_derivatives_of_monomial(quartic_term)
        self.wait()
        self.play(Write(alt_rhs))
        self.wait()

        self.fourth_deriv_lhs = fourth_deriv_lhs
        self.fourth_deriv_rhs = fourth_deriv_rhs
        self.fourth_deriv_alt_rhs = alt_rhs

    def solve_for_c4(self):
        c4s = VGroup(
            self.fourth_deriv_alt_rhs.get_part_by_tex("c_4"),
            self.fourth_deriv_rhs[-1],
            self.plus_quartic_term.get_part_by_tex("c_4")
        )
        fraction = TexMobject("\\text{\\small $\\frac{1}{24}$}")
        fraction.set_color(self.colors[4])
        fractions = VGroup(*[
            fraction.copy().move_to(c4, LEFT)
            for c4 in c4s
        ])
        fractions.shift(SMALL_BUFF*UP)
        x_to_4 = self.plus_quartic_term.get_part_by_tex("x^4")
        x_to_4.generate_target()
        x_to_4.target.shift(MED_SMALL_BUFF*RIGHT)

        self.play(
            Transform(
                c4s, fractions,
                run_time = 3,
                lag_ratio = 0.5,
            ),
            MoveToTarget(x_to_4, run_time = 2)
        )
        self.wait(3)

    def show_quartic_approximation(self):
        real_graph = self.quadratic_graph
        graph = real_graph.copy()
        quartic_graph = self.get_graph(
            lambda x : 1 - (x**2)/2.0 + (x**4)/24.0,
            color = graph.get_color(),
        )
        tex_mobs = VGroup(*[
            self.polynomial,
            self.fourth_deriv_rhs,
            self.fourth_deriv_alt_rhs,
            self.cosine_label,
            self.cosine_derivative,
            self.cosine_second_derivative,
            self.cosine_third_derivative[1],
        ])
        for tex_mob in tex_mobs:
            tex_mob.add_to_back(BackgroundRectangle(tex_mob))


        self.play(FadeIn(graph))
        real_graph.set_stroke(width = 0)
        self.play(
            Transform(
                graph, quartic_graph,
                run_time = 3,
            ),
            Animation(tex_mobs)
        )
        self.wait(3)


    ####

    def take_derivatives_of_monomial(self, term, *added_anims):
        """
        Must be a group of pure TexMobjects,
        last part must be of the form x^n
        """
        n = int(term[-1].get_tex_string()[-1])
        curr_term = term
        added_anims_iter = iter(added_anims)
        for k in range(n, 0, -1):
            exponent = curr_term[-1][-1]
            exponent_copy = exponent.copy()
            front_num = TexMobject("%d \\cdot"%k)
            front_num.move_to(curr_term[0][0], LEFT)

            new_monomial = TexMobject("x^%d"%(k-1))
            new_monomial.replace(curr_term[-1])
            Transform(curr_term[-1], new_monomial).update(1)
            curr_term.generate_target()
            curr_term.target.shift(
                (front_num.get_width()+SMALL_BUFF)*RIGHT
            )
            curr_term[-1][-1].set_fill(opacity = 0)

            possibly_added_anims = []
            try:
                possibly_added_anims.append(next(added_anims_iter))
            except:
                pass

            self.play(
                ApplyMethod(
                    exponent_copy.replace, front_num[0],
                    path_arc = np.pi,
                ),
                Write(
                    front_num[1], 
                    rate_func = squish_rate_func(smooth, 0.5, 1)
                ),
                MoveToTarget(curr_term),
                *possibly_added_anims,
                run_time = 2
            )
            self.remove(exponent_copy)
            self.add(front_num)
            curr_term = VGroup(front_num, *curr_term)
        self.wait()
        self.play(FadeOut(curr_term[-1]))

        return VGroup(*curr_term[:-1])

    def get_cosine_third_derivative(self):
        if not hasattr(self, "cosine_second_derivative"):
            self.get_cosine_second_derivative()
        third_deriv = TexMobject(
            "{d^3(", "\\cos", ")", "\\over", "dx^3}", 
            "(", "0", ")",
        )
        third_deriv.set_color_by_tex("cos", self.colors[0])
        third_deriv.set_color_by_tex("-\\cos", self.colors[3])
        third_deriv.scale(0.75)
        third_deriv.add_background_rectangle()
        third_deriv.next_to(
            self.cosine_second_derivative, DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        rhs = TexMobject("=", "\\sin(0)", "=", "0")
        rhs.set_color_by_tex("sin", self.colors[3])
        rhs.scale(0.8)
        rhs.next_to(
            third_deriv, RIGHT, 
            align_using_submobjects = True
        )
        rhs.add_background_rectangle()
        rhs.background_rectangle.scale_in_place(1.2)

        self.cosine_third_derivative = VGroup(third_deriv, rhs)
        return self.cosine_third_derivative

    def get_cosine_fourth_derivative(self):
        if not hasattr(self, "cosine_third_derivative"):
            self.get_cosine_third_derivative()
        fourth_deriv = TexMobject(
            "{d^4(", "\\cos", ")", "\\over", "dx^4}", 
            "(", "0", ")",
        )
        fourth_deriv.set_color_by_tex("cos", self.colors[0])
        fourth_deriv.scale(0.75)
        fourth_deriv.add_background_rectangle()
        fourth_deriv.next_to(
            self.cosine_third_derivative, DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        rhs = TexMobject("=", "\\cos(0)", "=", "1")
        rhs.set_color_by_tex("cos", self.colors[4])
        rhs.scale(0.8)
        rhs.next_to(
            fourth_deriv, RIGHT, 
            align_using_submobjects = True
        )
        rhs.add_background_rectangle()
        rhs.background_rectangle.scale_in_place(1.2)

        self.cosine_fourth_derivative = VGroup(fourth_deriv, rhs)
        return self.cosine_fourth_derivative

class NoticeAFewThings(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Notice a few things",
            target_mode = "hesitant"
        )
        self.wait(3)

class FactorialTerms(CubicAndQuarticApproximations):
    def construct(self):
        lhs_list = [
            TexMobject(
                "{d%s"%s, "\\over", "dx%s}"%s, "(", "c_8", "x^8", ")="
            )
            for i in range(9)
            for s in ["^%d"%i if i > 1 else ""]
        ]
        for lhs in lhs_list:
            lhs.set_color_by_tex("c_8", YELLOW)
            lhs.next_to(ORIGIN, LEFT)
        lhs_list[0].set_fill(opacity = 0)
        added_anims = [
            ReplacementTransform(
                start_lhs, target_lhs,
                rate_func = squish_rate_func(smooth, 0, 0.5)
            )
            for start_lhs, target_lhs in zip(lhs_list, lhs_list[1:])
        ]

        term = TexMobject("c_8", "x^8")
        term.next_to(lhs[-1], RIGHT)
        term.set_color_by_tex("c_8", YELLOW)

        self.add(term)
        self.wait()
        result = self.take_derivatives_of_monomial(term, *added_anims)

        factorial_term = VGroup(*result[:-1])
        brace = Brace(factorial_term)
        eight_factorial = brace.get_text("$8!$")

        coefficient = result[-1]
        words = TextMobject(
            "Set", "$c_8$", 
            "$ = \\frac{\\text{Desired derivative value}}{8!}"
        )
        words.set_color_by_tex("c_8", YELLOW)
        words.shift(2*UP)

        self.play(
            GrowFromCenter(brace),
            Write(eight_factorial)
        )
        self.play(
            ReplacementTransform(
                coefficient.copy(),
                words.get_part_by_tex("c_8")
            ),
            Write(words),
        )
        self.wait(2)

class HigherTermsDontMessUpLowerTerms(Scene):
    CONFIG = {
        "colors" : CubicAndQuarticApproximations.CONFIG["colors"][::2],

    }
    def construct(self):
        self.add_polynomial()
        self.show_second_derivative()

    def add_polynomial(self):
        c0_tex = "1"
        c2_tex = "\\text{\\small $\\left(-\\frac{1}{2}\\right)$}"
        c4_tex = "c_4"

        polynomial = TexMobject(
            "P(x) = ", 
            c0_tex, "+", 
            c2_tex, "x^2", "+",
            c4_tex, "x^4",
        )
        polynomial.shift(2*LEFT + UP)
        c0, c2, c4 = [
            polynomial.get_part_by_tex(tex)
            for tex in (c0_tex, c2_tex, c4_tex)
        ]
        for term, color in zip([c0, c2, c4], self.colors):
            term.set_color(color)
        arrows = VGroup(*[
            Arrow(
                c4.get_top(), c.get_top(), 
                path_arc = arc,
                color = c.get_color()
            )
            for c, arc in [(c2, 0.9*np.pi), (c0, np.pi)]
        ])
        no_affect_words = TextMobject(
            "Doesn't affect \\\\ previous terms"
        )
        no_affect_words.next_to(arrows, RIGHT)
        no_affect_words.shift(MED_SMALL_BUFF*(UP+LEFT))

        self.add(*polynomial[:-2])
        self.wait()
        self.play(Write(VGroup(*polynomial[-2:])))
        self.play(
            Write(no_affect_words),
            ShowCreation(arrows),
            run_time = 3
        )
        self.wait(2)

        self.polynomial = polynomial
        self.c0_tex = c0_tex
        self.c2_tex = c2_tex
        self.c4_tex = c4_tex

    def show_second_derivative(self):
        second_deriv = TexMobject(
            "{d^2 P \\over dx^2}(", "0", ")", "=",
            "2", self.c2_tex, "+", 
            "3 \\cdot 4", self.c4_tex, "(", "0", ")", "^2"
        )
        second_deriv.set_color_by_tex(self.c2_tex, self.colors[1])
        second_deriv.set_color_by_tex(self.c4_tex, self.colors[2])
        second_deriv.set_color_by_tex("0", YELLOW)
        second_deriv.next_to(
            self.polynomial, DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        higher_terms = VGroup(*second_deriv[-6:])
        brace = Brace(higher_terms, DOWN)
        equals_zero = brace.get_text("=0")

        second_deriv.save_state()
        second_deriv.move_to(self.polynomial, LEFT)
        second_deriv.set_fill(opacity = 0)

        self.play(second_deriv.restore)
        self.wait()
        self.play(GrowFromCenter(brace))
        self.wait()
        self.play(Write(equals_zero))
        self.wait(3)

class EachTermControlsOneDerivative(Scene):
    def construct(self):
        colors = CubicAndQuarticApproximations.CONFIG["colors"]
        polynomial = TexMobject(
            "P(x) = ", "c_0", "+", "c_1", "x", *it.chain(*[
                ["+", "c_%d"%n, "x^%d"%n]
                for n in range(2, 5)
            ])
        )
        consts = polynomial.get_parts_by_tex("c")
        deriv_words = VGroup(*[
            TextMobject("Controls \\\\ $%s(0)$"%tex)
            for tex in [
                "P",
                "\\frac{dP}{dx}",
            ] + [
                "\\frac{d^%d P}{dx^%d}"%(n, n)
                for n in range(2, 5)
            ]
        ])
        deriv_words.arrange(
            RIGHT, 
            buff = LARGE_BUFF,
            aligned_edge = UP
        )
        deriv_words.set_width(FRAME_WIDTH - MED_LARGE_BUFF)
        deriv_words.to_edge(UP)

        for const, deriv, color in zip(consts, deriv_words, colors):
            for mob in const, deriv:
                mob.set_color(color)
            arrow = Arrow(
                const.get_top(),
                deriv.get_bottom(),
                # buff = SMALL_BUFF,
                color = color
            )
            deriv.arrow = arrow

        self.add(polynomial)
        for deriv in deriv_words:
            self.play(
                ShowCreation(deriv.arrow),
                FadeIn(deriv)
            )
            self.wait()

class ApproximateNearNewPoint(CubicAndQuarticApproximations):
    CONFIG = {
        "target_approx_centers" : [np.pi/2, np.pi],
    }
    def construct(self):
        self.setup_axes()
        self.add_cosine_graph()
        self.shift_approximation_center()
        self.show_polynomials()

    def add_cosine_graph(self):
        self.cosine_graph = self.get_graph(
            np.cos, self.colors[0]
        )
        self.add(self.cosine_graph)

    def shift_approximation_center(self):
        quartic_graph = self.get_quartic_approximation(0)
        dot = Dot(color = YELLOW)
        dot.move_to(self.coords_to_point(0, 1))

        v_line = self.get_vertical_line_to_graph(
            self.target_approx_centers[-1], self.cosine_graph,
            line_class = DashedLine,
            color = YELLOW
        )
        pi = self.x_axis_labels[1]
        pi.add_background_rectangle()

        self.play(
            ReplacementTransform(
                self.cosine_graph.copy(),
                quartic_graph,
            ),
            DrawBorderThenFill(dot, run_time = 1)
        )
        for target, rt in zip(self.target_approx_centers, [3, 4, 4]):
            self.change_approximation_center(
                quartic_graph, dot, target, run_time = rt
            )
        self.play(
            ShowCreation(v_line),
            Animation(pi)
        )
        self.wait()

    def change_approximation_center(self, graph, dot, target, **kwargs):
        start = self.x_axis.point_to_number(dot.get_center())
        def update_quartic(graph, alpha):
            new_a = interpolate(start, target, alpha)
            new_graph = self.get_quartic_approximation(new_a)
            Transform(graph, new_graph).update(1)
            return graph

        def update_dot(dot, alpha):
            new_x = interpolate(start, target, alpha)
            dot.move_to(self.input_to_graph_point(new_x, self.cosine_graph))

        self.play(
            UpdateFromAlphaFunc(graph, update_quartic),
            UpdateFromAlphaFunc(dot, update_dot),
            **kwargs
        )

    def show_polynomials(self):
        poly_around_pi = self.get_polynomial("(x-\\pi)", "\\pi")
        poly_around_pi.to_corner(UP+LEFT)

        randy = Randolph()
        randy.to_corner(DOWN+LEFT)

        self.play(FadeIn(
            poly_around_pi,
            run_time = 4,
            lag_ratio = 0.5
        ))
        self.wait(2)
        self.play(FadeIn(randy))
        self.play(randy.change, "confused", poly_around_pi)
        self.play(Blink(randy))
        self.wait(2)
        self.play(randy.change_mode, "happy")
        self.wait(2)

    ###

    def get_polynomial(self, arg, center_tex):
        result = TexMobject(
            "P_{%s}(x)"%center_tex, "=", "c_0", *it.chain(*[
                ["+", "c_%d"%d, "%s^%d"%(arg, d)]
                for d in range(1, 5)
            ])
        )
        for d, color in enumerate(self.colors):
            result.set_color_by_tex("c_%d"%d, color)
        result.scale(0.85)
        result.add_background_rectangle()
        return result

    def get_quartic_approximation(self, a):
        coefficients = [
            derivative(np.cos, a, n)
            for n in range(5)
        ]
        func = lambda x : sum([
            (c/math.factorial(n))*(x - a)**n
            for n, c in enumerate(coefficients)
        ])
        return self.get_graph(func, color = GREEN)

class OnAPhilosophicalLevel(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "And on a \\\\ philosophical level",
            run_time = 1
        )
        self.wait(3)

class TranslationOfInformation(CubicAndQuarticApproximations):
    def construct(self):
        self.add_background()
        self.mention_information_exchange()
        self.show_derivative_pattern()
        self.show_polynomial()
        self.name_taylor_polynomial()
        self.draw_new_function_graph()
        self.write_general_function_derivative()
        self.replace_coefficients_in_generality()
        self.walk_through_terms()
        self.show_polynomial_around_a()

    def add_background(self):
        self.setup_axes()
        self.cosine_graph = self.get_graph(
            np.cos, color = self.colors[0]
        )
        self.add(self.cosine_graph)

    def mention_information_exchange(self):
        deriv_info = TextMobject(
            "Derivative \\\\ information \\\\ at a point"
        )
        deriv_info.next_to(ORIGIN, LEFT, LARGE_BUFF)
        deriv_info.to_edge(UP)
        output_info = TextMobject(
            "Output \\\\ information \\\\ near that point"
        )
        output_info.next_to(ORIGIN, RIGHT, LARGE_BUFF)
        output_info.to_edge(UP)
        arrow = Arrow(deriv_info, output_info)

        center_v_line = self.get_vertical_line_to_graph(
            0, self.cosine_graph,
            line_class = DashedLine,
            color = YELLOW
        )
        outer_v_lines = VGroup(*[
            center_v_line.copy().shift(vect)
            for vect in (LEFT, RIGHT)
        ])
        outer_v_lines.set_color(GREEN)
        dot = Dot(color = YELLOW)
        dot.move_to(center_v_line.get_top())
        dot.save_state()
        dot.move_to(deriv_info)
        dot.set_fill(opacity = 0)

        quadratic_graph = self.get_quadratic_graph()


        self.play(Write(deriv_info, run_time = 2))
        self.play(dot.restore)
        self.play(ShowCreation(center_v_line))
        self.wait()
        self.play(ShowCreation(arrow))
        self.play(Write(output_info, run_time = 2))

        self.play(ReplacementTransform(
            VGroup(center_v_line).copy(), 
            outer_v_lines
        ))
        self.play(ReplacementTransform(
            self.cosine_graph.copy(),
            quadratic_graph
        ), Animation(dot))
        for x in -1, 1, 0:
            start_x = self.x_axis.point_to_number(dot.get_center())
            self.play(UpdateFromAlphaFunc(
                dot,
                lambda d, a : d.move_to(self.input_to_graph_point(
                    interpolate(start_x, x, a), 
                    self.cosine_graph
                )),
                run_time = 2
            ))
        self.wait()
        self.play(*list(map(FadeOut, [
            deriv_info, arrow, output_info, outer_v_lines
        ])))

        self.quadratic_graph = quadratic_graph
        self.v_line = center_v_line
        self.dot = dot

    def show_derivative_pattern(self):
        derivs_at_x, derivs_at_zero = [
            VGroup(*[
                TexMobject(tex, "(", arg, ")")
                for tex in [
                    "\\cos", "-\\sin", 
                    "-\\cos", "\\sin", "\\cos"
                ]
            ])
            for arg in ("x", "0")
        ]
        arrows = VGroup(*[
            Arrow(
                UP, ORIGIN, 
                color = WHITE,
                buff = 0,
                tip_length = MED_SMALL_BUFF
            ) 
            for d in derivs_at_x
        ])
        group = VGroup(*it.chain(*list(zip(
            derivs_at_x,
            arrows
        ))))
        group.add(TexMobject("\\vdots"))
        group.arrange(DOWN, buff = SMALL_BUFF)
        group.set_height(FRAME_HEIGHT - MED_LARGE_BUFF)
        group.to_edge(LEFT)
        for dx, d0, color in zip(derivs_at_x, derivs_at_zero, self.colors):
            for d in dx, d0:
                d.set_color(color)
            d0.replace(dx)
        rhs_group = VGroup(*[
            TexMobject("=", "%d"%d).scale(0.7).next_to(deriv, RIGHT)
            for deriv, d in zip(derivs_at_zero, [1, 0, -1, 0, 1])
        ])
        derivative_values = VGroup(*[
            rhs[1] for rhs in rhs_group
        ])
        for value, color in zip(derivative_values, self.colors):
            value.set_color(color)
        zeros = VGroup(*[
            deriv.get_part_by_tex("0")
            for deriv in derivs_at_zero
        ])

        self.play(FadeIn(derivs_at_x[0]))
        self.wait()
        for start_d, arrow, target_d in zip(group[::2], group[1::2], group[2::2]):
            self.play(
                ReplacementTransform(
                    start_d.copy(), target_d
                ),
                ShowCreation(arrow)
            )
            self.wait()
        self.wait()
        self.play(ReplacementTransform(
            derivs_at_x, derivs_at_zero
        ))
        self.wait()
        self.play(*list(map(Write, rhs_group)))
        self.wait()
        for rhs in rhs_group:
            self.play(Indicate(rhs[1]), color = WHITE)
        self.wait()
        self.play(*[
            ReplacementTransform(
                zero.copy(), self.dot,
                run_time = 3,
                rate_func = squish_rate_func(smooth, a, a+0.4)
            )
            for zero, a in zip(zeros, np.linspace(0, 0.6, len(zeros)))
        ])
        self.wait()

        self.cosine_derivative_group = VGroup(
            derivs_at_zero, arrows, group[-1], rhs_group
        )
        self.derivative_values = derivative_values

    def show_polynomial(self):
        derivative_values = self.derivative_values.copy()
        polynomial = self.get_polynomial("x", 1, 0, -1, 0, 1)
        polynomial.to_corner(UP+RIGHT)

        monomial = TexMobject("\\frac{1}{4!}", "x^4")
        monomial = VGroup(VGroup(monomial[0]), monomial[1])
        monomial.next_to(polynomial, DOWN, LARGE_BUFF)

        self.play(*[
            Transform(
                dv, pc,
                run_time = 2,
                path_arc = np.pi/2
            )
            for dv, pc, a in zip(
                derivative_values, 
                polynomial.coefficients,
                np.linspace(0, 0.6, len(derivative_values))
            )
        ])
        self.play(
            Write(polynomial, run_time = 5),
            Animation(derivative_values)
        )
        self.remove(derivative_values)
        self.wait(2)
        to_fade = self.take_derivatives_of_monomial(monomial)
        self.play(FadeOut(to_fade))
        self.wait()

        self.polynomial = polynomial

    def name_taylor_polynomial(self):
        brace = Brace(
            VGroup(
                self.polynomial.coefficients, 
                self.polynomial.factorials
            ),
            DOWN
        )
        name = brace.get_text("``Taylor polynomial''")
        name.shift(MED_SMALL_BUFF*RIGHT)
        quartic_graph = self.get_graph(
            lambda x : 1 - (x**2)/2.0 + (x**4)/24.0,
            color = GREEN,
            x_min = -3.2, 
            x_max = 3.2,
        )
        quartic_graph.set_color(self.colors[4])

        self.play(GrowFromCenter(brace))
        self.play(Write(name))
        self.wait()
        self.play(
            Transform(
                self.quadratic_graph, quartic_graph,
                run_time = 2
            ),
            Animation(self.dot)
        )
        self.wait(2)

        self.taylor_name_group = VGroup(brace, name)

    def draw_new_function_graph(self):
        def func(x):
            return (np.sin(x**2 + x)+0.5)*np.exp(-x**2)
        graph = self.get_graph(
            func, color = self.colors[0]
        )

        self.play(*list(map(FadeOut, [
            self.cosine_derivative_group,
            self.cosine_graph,
            self.quadratic_graph,
            self.v_line,
            self.dot
        ])))
        self.play(ShowCreation(graph))

        self.graph = graph

    def write_general_function_derivative(self):
        derivs_at_x, derivs_at_zero, derivs_at_a = deriv_lists = [
            VGroup(*[
                TexMobject("\\text{$%s$}"%args[0], *args[1:])
                for args in [
                    ("f", "(", arg, ")"),
                    ("\\frac{df}{dx}", "(", arg, ")"),
                    ("\\frac{d^2 f}{dx^2}", "(", arg, ")"),
                    ("\\frac{d^3 f}{dx^3}", "(", arg, ")"),
                    ("\\frac{d^4 f}{dx^4}", "(", arg, ")"),
                ]
            ])
            for arg in ("x", "0", "a")
        ]
        derivs_at_x.arrange(DOWN, buff = MED_LARGE_BUFF)
        derivs_at_x.set_height(FRAME_HEIGHT - MED_LARGE_BUFF)
        derivs_at_x.to_edge(LEFT)
        zeros = VGroup(*[
            deriv.get_part_by_tex("0")
            for deriv in derivs_at_zero
        ])
        self.dot.move_to(self.input_to_graph_point(0, self.graph))
        self.v_line.put_start_and_end_on(
            self.graph_origin, self.dot.get_center()
        )

        for color, dx, d0, da in zip(self.colors, *deriv_lists):
            for d in dx, d0, da:
                d.set_color(color)
                d.add_background_rectangle()
            d0.replace(dx)
            da.replace(dx)

        self.play(FadeIn(derivs_at_x[0]))
        self.wait()
        for start, target in zip(derivs_at_x, derivs_at_x[1:]):
            self.play(ReplacementTransform(
                start.copy(), target
            ))
            self.wait()
        self.wait()
        self.play(ReplacementTransform(
            derivs_at_x, derivs_at_zero,
        ))
        self.play(ReplacementTransform(
            zeros.copy(), self.dot,
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.play(ShowCreation(self.v_line))
        self.wait()

        self.derivs_at_zero = derivs_at_zero
        self.derivs_at_a = derivs_at_a

    def replace_coefficients_in_generality(self):
        new_polynomial = self.get_polynomial("x", *[
            tex_mob.get_tex_string()
            for tex_mob in self.derivs_at_zero[:-1]
        ])
        new_polynomial.to_corner(UP+RIGHT)
        polynomial_fourth_term = VGroup(
            *self.polynomial[-7:-1]
        )
        self.polynomial.remove(*polynomial_fourth_term)

        self.play(
            ReplacementTransform(
                self.polynomial, new_polynomial,
                run_time = 2,
                lag_ratio = 0.5
            ),
            FadeOut(polynomial_fourth_term),
            FadeOut(self.taylor_name_group),
        )
        self.polynomial = new_polynomial
        self.wait(3)

    def walk_through_terms(self):
        func = self.graph.underlying_function
        approx_graphs = [
            self.get_graph(
                taylor_approximation(func, n),
                color = WHITE
            )
            for n in range(7)
        ]
        for graph, color in zip(approx_graphs, self.colors):
            graph.set_color(color)

        left_mob = self.polynomial.coefficients[0]
        right_mobs = list(self.polynomial.factorials)
        right_mobs.append(self.polynomial[-1])
        braces = [
            Brace(
                VGroup(left_mob, *right_mobs[:n]),
                DOWN
            )
            for n in range(len(approx_graphs))
        ]
        brace = braces[0]
        brace.stretch_to_fit_width(MED_LARGE_BUFF)
        approx_graph = approx_graphs[0]

        self.polynomial.add_background_rectangle()

        self.play(GrowFromCenter(brace))
        self.play(ShowCreation(approx_graph))
        self.wait()
        for new_brace, new_graph in zip(braces[1:], approx_graphs[1:]):
            self.play(Transform(brace, new_brace))
            self.play(
                Transform(approx_graph, new_graph, run_time = 2),
                Animation(self.polynomial),
                Animation(self.dot),
            )
            self.wait()
        self.play(FadeOut(brace))

        self.approx_graph = approx_graph
        self.approx_order = len(approx_graphs) - 1

    def show_polynomial_around_a(self):
        new_polynomial = self.get_polynomial("(x-a)", *[
            tex_mob.get_tex_string()
            for tex_mob in self.derivs_at_a[:-2]
        ])
        new_polynomial.to_corner(UP+RIGHT)
        new_polynomial.add_background_rectangle()

        polynomial_third_term = VGroup(
            *self.polynomial[1][-7:-1]
        )
        self.polynomial[1].remove(*polynomial_third_term)

        group = VGroup(self.approx_graph, self.dot, self.v_line)
        def get_update_function(target_x):
            def update(group, alpha):
                graph, dot, line = group
                start_x = self.x_axis.point_to_number(dot.get_center())
                x = interpolate(start_x, target_x, alpha)
                graph_point = self.input_to_graph_point(x, self.graph)
                dot.move_to(graph_point)
                line.put_start_and_end_on(
                    self.coords_to_point(x, 0),
                    graph_point,
                )
                new_approx_graph = self.get_graph(
                    taylor_approximation(
                        self.graph.underlying_function,
                        self.approx_order,
                        center_point = x
                    ),
                    color = graph.get_color()
                )
                Transform(graph, new_approx_graph).update(1)
                return VGroup(graph, dot, line)
            return update

        self.play(
            UpdateFromAlphaFunc(
                group, get_update_function(1), run_time = 2
            ),
            Animation(self.polynomial),
            Animation(polynomial_third_term)
        )
        self.wait()
        self.play(Transform(
            self.derivs_at_zero, 
            self.derivs_at_a
        ))
        self.play(
            Transform(self.polynomial, new_polynomial),
            FadeOut(polynomial_third_term)
        )
        self.wait()
        for x in -1, np.pi/6:
            self.play(
                UpdateFromAlphaFunc(
                    group, get_update_function(x), 
                ),
                Animation(self.polynomial),
                run_time = 4,
            )
            self.wait()


    #####

    def get_polynomial(self, arg, *coefficients):
        result = TexMobject(
            "P(x) = ", str(coefficients[0]), *list(it.chain(*[
                ["+", str(c), "{%s"%arg, "^%d"%n, "\\over", "%d!}"%n]
                for n, c in zip(it.count(1), coefficients[1:])
            ])) + [
                "+ \\cdots"
            ]
        )
        result.scale(0.8)
        coefs = VGroup(result[1], *result[3:-1:6])
        for coef, color in zip(coefs, self.colors):
            coef.set_color(color)
        result.coefficients = coefs
        result.factorials = VGroup(*result[7::6])

        return result

class ThisIsAStandardFormula(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "You will see this \\\\ in your texts",
            run_time = 1
        )
        self.change_student_modes(
            *["sad"]*3,
            look_at_arg = FRAME_Y_RADIUS*UP
        )
        self.wait(2)

class ExpPolynomial(TranslationOfInformation, ExampleApproximationWithExp):
    CONFIG = {
        "x_tick_frequency" : 1,
        "x_leftmost_tick" : -3,
        "graph_origin" : 2*(DOWN+LEFT),
        "y_axis_label" : "",
    }
    def construct(self):
        self.setup_axes()
        self.add_graph()
        self.show_derivatives()
        self.show_polynomial()
        self.walk_through_terms()

    def add_graph(self):
        graph = self.get_graph(np.exp)
        e_to_x = self.get_graph_label(graph, "e^x")
    
        self.play(
            ShowCreation(graph),
            Write(
                e_to_x, 
                rate_func = squish_rate_func(smooth, 0.5, 1)
            ),
            run_time = 2
        )
        self.wait()

        self.graph = graph
        self.e_to_x = e_to_x

    def show_derivatives(self):
        self.e_to_x.generate_target()
        derivs_at_x, derivs_at_zero = [
            VGroup(*[
                TexMobject("e^%s"%s).set_color(c)
                for c in self.colors
            ])
            for s in ("x", "0")
        ]
        derivs_at_x.submobjects[0] = self.e_to_x.target
        arrows = VGroup(*[
            Arrow(
                UP, ORIGIN, 
                color = WHITE,
                buff = SMALL_BUFF,
                tip_length = 0.2,
            ) 
            for d in derivs_at_x
        ])
        group = VGroup(*it.chain(*list(zip(
            derivs_at_x,
            arrows
        ))))
        group.add(TexMobject("\\vdots"))
        group.arrange(DOWN, buff = 2*SMALL_BUFF)
        group.set_height(FRAME_HEIGHT - MED_LARGE_BUFF)
        group.to_edge(LEFT)
        for dx, d0 in zip(derivs_at_x, derivs_at_zero):
            for d in dx, d0:
                d.add_background_rectangle()
            d0.replace(dx)
        rhs_group = VGroup(*[
            TexMobject("=", "1").scale(0.7).next_to(deriv, RIGHT)
            for deriv in derivs_at_zero
        ])
        derivative_values = VGroup(*[
            rhs[1] for rhs in rhs_group
        ])
        for value, color in zip(derivative_values, self.colors):
            value.set_color(color)

        for arrow in arrows:
            d_dx = TexMobject("d/dx")
            d_dx.scale(0.5)
            d_dx.next_to(arrow, RIGHT, SMALL_BUFF)
            d_dx.shift(SMALL_BUFF*UP)
            arrow.add(d_dx)

        self.play(MoveToTarget(self.e_to_x))
        derivs_at_x.submobjects[0] = self.e_to_x
        for start_d, arrow, target_d in zip(group[::2], group[1::2], group[2::2]):
            self.play(
                ReplacementTransform(
                    start_d.copy(), target_d
                ),
                Write(arrow, run_time = 1)
            )
            self.wait()
        self.wait()
        self.play(ReplacementTransform(
            derivs_at_x, derivs_at_zero
        ))
        self.wait()
        self.play(*list(map(Write, rhs_group)))

        self.derivative_values = derivative_values

    def show_polynomial(self):
        derivative_values = self.derivative_values.copy()
        polynomial = self.get_polynomial("x", 1, 1, 1, 1, 1)
        polynomial.to_corner(UP+RIGHT)

        ##These are to make the walk_through_terms method work
        self.polynomial = polynomial.copy()
        self.dot = Dot(fill_opacity = 0)
        ###
        polynomial.add_background_rectangle()

        self.play(*[
            Transform(
                dv, pc,
                run_time = 2,
                path_arc = np.pi/2
            )
            for dv, pc in zip(
                derivative_values, 
                polynomial.coefficients,
            )
        ])
        self.play(
            Write(polynomial, run_time = 4),
            Animation(derivative_values)
        )

    ####

    def setup_axes(self):
        GraphScene.setup_axes(self)

class ShowSecondTerm(TeacherStudentsScene):
    def construct(self):
        colors = CubicAndQuarticApproximations.CONFIG["colors"]
        polynomial = TexMobject(
            "f(a)", "+", 
            "\\frac{df}{dx}(a)", "(x - a)", "+",
            "\\frac{d^2 f}{dx^2}(a)", "(x - a)^2"
        )
        for tex, color in zip(["f(a)", "df", "d^2 f"], colors):
            polynomial.set_color_by_tex(tex, color)
        polynomial.next_to(self.teacher, UP+LEFT)
        polynomial.shift(MED_LARGE_BUFF*UP)
        second_term = VGroup(*polynomial[-2:])
        box = Rectangle(color = colors[2])
        box.replace(second_term, stretch = True)
        box.stretch_in_place(1.1, 0)
        box.stretch_in_place(1.2, 1)
        words = TextMobject("Geometric view")
        words.next_to(box, UP)

        self.teacher_says(
            "Now for \\\\ something fun!",
            target_mode = "hooray"
        )
        self.wait(2)
        self.play(
            RemovePiCreatureBubble(
                self.teacher,
                target_mode = "raise_right_hand"
            ),
            Write(polynomial)
        )
        self.play(
            ShowCreation(box),
            FadeIn(words),
        )
        self.change_student_modes(*["pondering"]*3)
        self.wait(3)

class SecondTermIntuition(AreaIsDerivative):
    CONFIG = {
        "func" : lambda x : x*(x-1)*(x-2) + 2,
        "num_rects" : 300,
        "t_max" : 2.3,
        "x_max" : 4,
        "x_labeled_nums" : None,
        "x_axis_label" : "",
        "y_labeled_nums" : None,
        "y_axis_label" : "",
        "y_min" : -1,
        "y_max" : 5,
        "y_tick_frequency" : 1,
        "variable_point_label" : "x",
        "area_opacity" : 1,
        "default_riemann_start_color" : BLUE_E,
        "dx" : 0.15,
        "skip_reconfiguration" : False,
    }
    def setup(self):
        GraphScene.setup(self)
        ReconfigurableScene.setup(self)
        self.foreground_mobjects = []

    def construct(self):
        self.setup_axes()
        self.introduce_area()
        self.write_derivative()
        self.nudge_end_point()
        self.point_out_triangle()
        self.relabel_start_and_end()
        self.compute_triangle_area()
        self.walk_through_taylor_terms()

    def introduce_area(self):
        graph = self.v_graph = self.get_graph(
            self.func, color = WHITE,
        )
        self.foreground_mobjects.append(graph)
        area = self.area = self.get_area(0, self.t_max)

        func_name = TexMobject("f_{\\text{area}}(x)")
        func_name.move_to(self.coords_to_point(0.6, 1))
        self.foreground_mobjects.append(func_name)

        self.add(graph, area, func_name)
        self.add_T_label(self.t_max)

        if not self.skip_animations:
            for target in 1.6, 2.7, self.t_max:
                self.change_area_bounds(
                    new_t_max = target,
                    run_time = 3,
                )
        self.__name__ = func_name

    def write_derivative(self):
        deriv = TexMobject("\\frac{df_{\\text{area}}}{dx}(x)")
        deriv.next_to(
            self.input_to_graph_point(2.7, self.v_graph),
            RIGHT
        )
        deriv.shift_onto_screen()

        self.play(ApplyWave(self.v_graph, direction = UP))
        self.play(Write(deriv, run_time = 2))
        self.wait()

        self.deriv_label = deriv

    def nudge_end_point(self):
        dark_area = self.area.copy()
        dark_area.set_fill(BLACK, opacity = 0.5)
        curr_x = self.x_axis.point_to_number(self.area.get_right())
        new_x = curr_x + self.dx

        rect = Rectangle(
            stroke_width = 0,
            fill_color = YELLOW,
            fill_opacity = 0.75
        )
        rect.replace(
            VGroup(
                VectorizedPoint(self.coords_to_point(new_x, 0)),
                self.right_v_line,
            ),
            stretch = True
        )

        dx_brace = Brace(rect, DOWN, buff = 0)
        dx_label = dx_brace.get_text("$dx$", buff = SMALL_BUFF)
        dx_label_group = VGroup(dx_label, dx_brace)

        height_brace = Brace(rect, LEFT, buff = SMALL_BUFF)

        self.change_area_bounds(new_t_max = new_x)
        self.play(
            FadeIn(dark_area),
            *list(map(Animation, self.foreground_mobjects))
        )
        self.play(
            FadeOut(self.T_label_group),
            FadeIn(dx_label_group),
            FadeIn(rect),
            FadeIn(height_brace)
        )
        self.wait()
        if not self.skip_reconfiguration:
            self.transition_to_alt_config(
                dx = self.dx/10.0,
                run_time = 3,
            )
        self.play(FadeOut(height_brace))

        self.dx_label_group = dx_label_group
        self.rect = rect
        self.dark_area = dark_area

    def point_out_triangle(self):
        triangle = Polygon(LEFT, ORIGIN, UP)
        triangle.set_stroke(width = 0)
        triangle.set_fill(MAROON_B, opacity = 1)
        triangle.replace(
            Line(
                self.rect.get_corner(UP+LEFT),
                self.right_v_line.get_top()
            ),
            stretch = True
        )
        circle = Circle(color = RED)
        circle.set_height(triangle.get_height())
        circle.replace(triangle, dim_to_match = 1)
        circle.scale_in_place(1.3)

        self.play(DrawBorderThenFill(triangle))
        self.play(ShowCreation(circle))
        self.play(FadeOut(circle))

        self.triangle = triangle

    def relabel_start_and_end(self):
        dx_label, dx_brace = self.dx_label_group
        x_minus_a = TexMobject("(x-a)")
        x_minus_a.scale(0.7)
        x_minus_a.move_to(dx_label)
        labels = VGroup()
        arrows = VGroup()
        for vect, tex in (LEFT, "a"), (RIGHT, "x"):
            point = self.rect.get_corner(DOWN+vect)
            label = TexMobject(tex)
            label.next_to(point, DOWN+vect)
            label.shift(LARGE_BUFF*vect)
            arrow = Arrow(
                label.get_corner(UP-vect),
                point,
                buff = SMALL_BUFF,
                tip_length = 0.2,
                color = WHITE
            )
            labels.add(label)
            arrows.add(arrow)


        for label, arrow in zip(labels, arrows):
            self.play(
                Write(label),
                ShowCreation(arrow)
            )
            self.wait()
        self.wait()
        self.play(ReplacementTransform(
            dx_label, x_minus_a
        ))
        self.wait()

        self.x_minus_a = x_minus_a

    def compute_triangle_area(self):
        triangle = self.triangle.copy()
        tex_scale_factor = 0.7
        base_line = Line(*[
            triangle.get_corner(DOWN+vect)
            for vect in (LEFT, RIGHT)
        ])
        base_line.set_color(RED)
        base_label = TextMobject("Base = ", "$(x-a)$")
        base_label.scale(tex_scale_factor)
        base_label.next_to(base_line, DOWN+RIGHT, MED_LARGE_BUFF)
        base_label.shift(SMALL_BUFF*UP)
        base_term = base_label[1].copy()
        base_arrow = Arrow(
            base_label.get_left(), 
            base_line.get_center(),
            buff = SMALL_BUFF,
            color = base_line.get_color(),
            tip_length = 0.2
        )

        height_brace = Brace(triangle, RIGHT, buff = SMALL_BUFF)
        height_labels = [
            TexMobject("\\text{Height} = ", s, "(x-a)")
            for s in [
                "(\\text{Slope})", 
                "\\frac{d^2 f_{\\text{area}}}{dx^2}(a)"
            ]
        ]
        for label in height_labels:
            label.scale(tex_scale_factor)
            label.next_to(height_brace, RIGHT)
        height_term = VGroup(*height_labels[1][1:]).copy()

        self.play(
            FadeIn(base_label),
            ShowCreation(base_arrow),
            ShowCreation(base_line)
        )
        self.wait(2)
        self.play(
            GrowFromCenter(height_brace),
            Write(height_labels[0])
        )
        self.wait(2)
        self.play(ReplacementTransform(*height_labels))
        self.wait(2)

        #Show area formula
        equals_half = TexMobject("=\\frac{1}{2}")
        equals_half.scale(tex_scale_factor)
        group = VGroup(triangle, equals_half, height_term, base_term)
        group.generate_target()
        group.target.arrange(RIGHT, buff = SMALL_BUFF)
        group.target[-1].next_to(
            group.target[-2], RIGHT,
            buff = SMALL_BUFF,
            align_using_submobjects = True
        )
        group.target[1].shift(0.02*DOWN)
        group.target.to_corner(UP+RIGHT)
        exp_2 = TexMobject("2").scale(0.8*tex_scale_factor)
        exp_2.next_to(
            group.target[-2], UP+RIGHT,
            buff = 0,
            align_using_submobjects = True
        )
        equals_half.scale(0.1)
        equals_half.move_to(triangle)
        equals_half.set_fill(opacity = 0)

        self.play(
            FadeOut(self.deriv_label),
            MoveToTarget(group, run_time = 2)
        )
        self.wait(2)
        self.play(Transform(
            group[-1], exp_2
        ))
        self.wait(2)

    def walk_through_taylor_terms(self):
        mini_area, mini_rect, mini_triangle = [
            mob.copy()
            for mob in (self.dark_area, self.rect, self.triangle)
        ]
        mini_area.set_fill(BLUE_E, opacity = 1)
        mini_area.set_height(1)
        mini_rect.set_height(1)
        mini_triangle.set_height(0.5)

        geometric_taylor = VGroup(
            TexMobject("f(x) \\approx "), mini_area,
            TexMobject("+"), mini_rect,
            TexMobject("+"), mini_triangle,
        )
        geometric_taylor.arrange(
            RIGHT, buff = MED_SMALL_BUFF
        )
        geometric_taylor.to_corner(UP+LEFT)

        analytic_taylor = TexMobject(
            "f(x) \\approx", "f(a)", "+",
            "\\frac{df}{dx}(a)(x-a)", "+",
            "\\frac{1}{2}\\frac{d^2 f}{dx^2}(a)(x-a)^2"
        )
        analytic_taylor.set_color_by_tex("f(a)", BLUE)
        analytic_taylor.set_color_by_tex("df", YELLOW)
        analytic_taylor.set_color_by_tex("d^2 f", MAROON_B)
        analytic_taylor.scale(0.7)
        analytic_taylor.next_to(
            geometric_taylor, DOWN,
            aligned_edge = LEFT
        )
        for part in analytic_taylor:
            part.add_to_back(BackgroundRectangle(part))

        new_func_name = TexMobject("f_{\\text{area}}(a)")
        new_func_name.replace(self.__name__)

        self.play(FadeIn(
            geometric_taylor,
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.wait()
        self.play(
            FadeIn(VGroup(*analytic_taylor[:3])),
            self.dark_area.set_fill, BLUE_E, 1,
            Transform(self.__name__, new_func_name)
        )
        self.wait()
        self.play(
            self.rect.scale_in_place, 0.5,
            rate_func = there_and_back
        )
        self.play(FadeIn(VGroup(*analytic_taylor[3:5])))
        self.wait(2)
        self.play(
            self.triangle.scale_in_place, 0.5,
            rate_func = there_and_back
        )
        self.play(FadeIn(VGroup(*analytic_taylor[5:])))
        self.wait(3)

class EachTermHasMeaning(TeacherStudentsScene):
    def construct(self):
        self.get_pi_creatures().scale_in_place(0.8).shift(UP)
        self.teacher_says(
            "Each term \\\\ has meaning!",
            target_mode = "hooray",
            bubble_kwargs = {"height" : 3, "width" : 4}
        )
        self.change_student_modes(
            *["thinking"]*3,
            look_at_arg = 4*UP
        )
        self.wait(3)

class AskAboutInfiniteSum(TeacherStudentsScene):
    def construct(self):
        self.ask_question()
        self.name_taylor_series()
        self.be_careful()


    def ask_question(self):
        big_rect = Rectangle(
            width = FRAME_WIDTH,
            height = FRAME_HEIGHT,
            stroke_width = 0,
            fill_color =  BLACK,
            fill_opacity = 0.7,
        )
        randy = self.get_students()[1]
        series = TexMobject(
            "\\cos(x)", "\\approx", 
            "1 - \\frac{x^2}{2!} + \\frac{x^4}{4!}",
            " - \\frac{x^6}{6!}",
            "+\\cdots"
        )
        series.next_to(randy, UP, 2)
        series.shift_onto_screen()
        rhs = VGroup(*series[2:])
        arrow = Arrow(rhs.get_left(), rhs.get_right())
        arrow.next_to(rhs, UP)
        words = TextMobject("Add infinitely many")
        words.next_to(arrow, UP)

        self.teacher_says(
            "We could call \\\\ it an end here"
        )
        self.change_student_modes(*["erm"]*3)
        self.wait(3)
        self.play(
            RemovePiCreatureBubble(self.teacher),
            self.get_students()[0].change_mode, "plain",
            self.get_students()[2].change_mode, "plain",
            FadeIn(big_rect),
            randy.change_mode, "pondering"
        )
        crowd = VGroup(*self.get_pi_creatures())
        crowd.remove(randy)
        self.crowd_copy = crowd.copy()
        self.remove(crowd)
        self.add(self.crowd_copy, big_rect, randy)

        self.play(Write(series))
        self.play(
            ShowCreation(arrow),
            Write(words)
        )
        self.wait(3)

        self.arrow = arrow
        self.words = words
        self.series = series
        self.randy = randy

    def name_taylor_series(self):
        series_def = TextMobject(
            "Infinite sum $\\Leftrightarrow$ series"
        )
        taylor_series = TextMobject("Taylor series")
        for mob in series_def, taylor_series:
            mob.move_to(self.words)
        brace = Brace(self.series.get_part_by_tex("4!"), DOWN)
        taylor_polynomial = brace.get_text("Taylor polynomial")

        self.play(ReplacementTransform(
            self.words, series_def
        ))
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(taylor_polynomial)
        )
        self.wait(2)
        self.play(
            series_def.scale, 0.7,
            series_def.to_corner, UP+RIGHT,
            FadeIn(taylor_series)
        )
        self.play(self.randy.change, "thinking", taylor_series)
        self.wait()

    def be_careful(self):
        self.play(FadeIn(self.teacher))
        self.remove(self.crowd_copy[0])
        self.teacher_says(
            "Be careful",
            bubble_kwargs = {
                "width" : 3,
                "height" : 2
            },
            added_anims = [self.randy.change, "hesitant"]
        )
        self.wait(2)
        self.play(self.randy.change, "confused", self.series)
        self.wait(3)

class ConvergenceExample(Scene):
    def construct(self):
        max_shown_power = 6
        max_computed_power = 13
        series = TexMobject(*list(it.chain(*[
            ["\\frac{1}{%d}"%(3**n), "+"]
            for n in range(1, max_shown_power)
        ])) + ["\\cdots"])
        series_nums = [3**(-n) for n in range(1, max_computed_power)]
        partial_sums = np.cumsum(series_nums)
        braces = self.get_partial_sum_braces(series, partial_sums)

        convergence_words = TextMobject("``Converges'' to $\\frac{1}{2}$")
        convergence_words.next_to(series, UP, LARGE_BUFF)
        convergence_words.set_color(YELLOW)
        rhs = TexMobject("= \\frac{1}{2}")
        rhs.next_to(series, RIGHT)
        rhs.set_color(BLUE)

        brace = braces[0]
        self.add(series, brace)
        for i, new_brace in enumerate(braces[1:]):
            self.play(Transform(brace, new_brace))
            if i == 4:
                self.play(FadeIn(convergence_words))
            else:
                self.wait()
        self.play(
            FadeOut(brace),
            Write(rhs)
        )
        self.wait(2)

    def get_partial_sum_braces(self, series, partial_sums):
        braces = [
            Brace(VGroup(*series[:n]))
            for n in range(1, len(series)-1, 2)
        ]
        last_brace = braces[-1]
        braces += [
            braces[-1].copy().stretch_in_place(
                1 + 0.1 + 0.02*(n+1), dim = 0,
            ).move_to(last_brace, LEFT)
            for n in range(len(partial_sums) - len(braces))
        ]
        for brace, partial_sum in zip(braces, partial_sums):
            number = brace.get_text("%.7f"%partial_sum)
            number.set_color(YELLOW)
            brace.add(number)
        return braces

class ExpConvergenceExample(ConvergenceExample):
    def construct(self):
        e_to_x, series_with_x = x_group = self.get_series("x")
        x_group.to_edge(UP)
        e_to_1, series_with_1 = one_group = self.get_series("1")
        terms = [1./math.factorial(n) for n in range(11)]
        partial_sums = np.cumsum(terms)
        braces = self.get_partial_sum_braces(series_with_1, partial_sums)
        brace = braces[1]

        for lhs, s in (e_to_x, "x"), (e_to_1, "1"):
            new_lhs = TexMobject("e^%s"%s, "=")
            new_lhs.move_to(lhs, RIGHT)
            lhs.target = new_lhs

        self.add(x_group)
        self.wait()
        self.play(ReplacementTransform(x_group.copy(), one_group))
        self.play(FadeIn(brace))
        self.wait()
        for new_brace in braces[2:]:
            self.play(Transform(brace, new_brace))
            self.wait()
        self.wait()
        self.play(MoveToTarget(e_to_1))
        self.wait(2)

    def get_series(self, arg, n_terms = 5):
        series = TexMobject("1", "+", *list(it.chain(*[
            ["\\frac{%s^%d}{%d!}"%(arg, n, n), "+"]
            for n in range(1, n_terms+1)
        ])) + ["\\cdots"])
        colors = list(CubicAndQuarticApproximations.CONFIG["colors"])
        colors += [BLUE_C]
        for term, color in zip(series[::2], colors):
            term.set_color(color)

        lhs = TexMobject("e^%s"%arg, "\\rightarrow")
        lhs.arrange(RIGHT, buff = SMALL_BUFF)
        group = VGroup(lhs, series)
        group.arrange(RIGHT, buff = SMALL_BUFF)

        return group

class ExpGraphConvergence(ExpPolynomial, ExpConvergenceExample):
    CONFIG = {
        "example_input" : 2,
        "graph_origin" : 3*DOWN + LEFT,
        "n_iterations" : 8,
        "y_max" : 20,
        "num_graph_anchor_points" : 50,
        "func" : np.exp,
    }
    def construct(self):
        self.setup_axes()
        self.add_series()
        approx_graphs = self.get_approx_graphs()

        graph = self.get_graph(self.func, color = self.colors[0])
        v_line = self.get_vertical_line_to_graph(
            self.example_input, graph,
            line_class = DashedLine,
            color = YELLOW
        )
        dot = Dot(color = YELLOW)
        dot.to_corner(UP+LEFT)

        equals = TexMobject("=")
        equals.replace(self.arrow)
        equals.scale_in_place(0.8)

        brace = self.braces[1]
        approx_graph = approx_graphs[1]
        x = self.example_input
        self.add(graph, self.series)
        self.wait()
        self.play(dot.move_to, self.coords_to_point(x, 0))
        self.play(
            dot.move_to, self.input_to_graph_point(x, graph),
            ShowCreation(v_line)
        )
        self.wait()
        self.play(
            GrowFromCenter(brace),
            ShowCreation(approx_graph)
        )
        self.wait()
        for new_brace, new_graph in zip(self.braces[2:], approx_graphs[2:]):
            self.play(
                Transform(brace, new_brace),
                Transform(approx_graph, new_graph),
                Animation(self.series),
            )
            self.wait()
        self.play(FocusOn(equals))
        self.play(Transform(self.arrow, equals))
        self.wait(2)

    def add_series(self):
        series_group = self.get_series("x")
        e_to_x, series = series_group
        series_group.scale(0.8)
        series_group.to_corner(UP+LEFT)
        braces = self.get_partial_sum_braces(
            series, np.zeros(self.n_iterations)
        )
        for brace in braces:
            brace.remove(brace[-1])

        series.add_background_rectangle()
        self.add(series_group)

        self.braces = braces
        self.series = series
        self.arrow = e_to_x[1]

    def get_approx_graphs(self):
        def get_nth_approximation(n):
            return lambda x : sum([
                float(x**k)/math.factorial(k)
                for k in range(n+1)
            ])
        approx_graphs = [
            self.get_graph(get_nth_approximation(n))
            for n in range(self.n_iterations)
        ]

        colors = it.chain(self.colors, it.repeat(WHITE))
        for approx_graph, color in zip(approx_graphs, colors):
            approx_graph.set_color(color)
            dot = Dot(color = WHITE)
            dot.move_to(self.input_to_graph_point(
                self.example_input, approx_graph
            ))
            approx_graph.add(dot)

        return approx_graphs

class SecondExpGraphConvergence(ExpGraphConvergence):
    CONFIG = {
        "example_input" : 3,
        "n_iterations" : 12,
    }

class BoundedRadiusOfConvergence(CubicAndQuarticApproximations):
    CONFIG = {
        "num_graph_anchor_points" : 100,
    }
    def construct(self):
        self.setup_axes()
        func = lambda x : (np.sin(x**2 + x)+0.5)*(np.log(x+1.01)+1)*np.exp(-x)
        graph = self.get_graph(
            func, color = self.colors[0],
            x_min = -0.99,
            x_max = self.x_max,
        )
        v_line = self.get_vertical_line_to_graph(
            0, graph,
            line_class = DashedLine,
            color = YELLOW
        )
        dot = Dot(color = YELLOW).move_to(v_line.get_top())
        two_graph = self.get_graph(lambda x : 2)
        outer_v_lines = VGroup(*[
            DashedLine(
                self.coords_to_point(x, -2),
                self.coords_to_point(x, 2),
                color = WHITE
            )
            for x in (-1, 1)
        ])

        colors = list(self.colors) + [GREEN, MAROON_B, PINK]
        approx_graphs = [
            self.get_graph(
                taylor_approximation(func, n),
                color = color
            )
            for n, color in enumerate(colors)
        ]
        approx_graph = approx_graphs[1]

        self.add(graph, v_line, dot)
        self.play(ReplacementTransform(
            VGroup(v_line.copy()), outer_v_lines
        ))
        self.play(
            ShowCreation(approx_graph),
            Animation(dot)
        )
        self.wait()
        for new_graph in approx_graphs[2:]:
            self.play(
                Transform(approx_graph, new_graph),
                Animation(dot)
            )
            self.wait()
        self.wait()

class RadiusOfConvergenceForLnX(ExpGraphConvergence):
    CONFIG = {
        "x_min" : -1,
        "x_leftmost_tick" : None,
        "x_max" : 5,
        "y_min" : -2,
        "y_max" : 3,
        "graph_origin" : DOWN+2*LEFT,
        "func" : np.log,
        "num_graph_anchor_points" : 100,
        "initial_n_iterations" : 7,
        "n_iterations" : 11,
        "convergent_example" : 1.5,
        "divergent_example" : 2.5,
    }
    def construct(self):
        self.add_graph()
        self.add_series()
        self.show_bounds()
        self.show_converging_point()
        self.show_diverging_point()
        self.write_divergence()
        self.write_radius_of_convergence()

    def add_graph(self):
        self.setup_axes()
        self.graph = self.get_graph(
            self.func,
            x_min = 0.01
        )
        self.add(self.graph)

    def add_series(self):
        series = TexMobject(
            "\\ln(x) \\rightarrow", 
            "(x-1)", "-",
            "\\frac{(x-1)^2}{2}", "+",
            "\\frac{(x-1)^3}{3}", "-",
            "\\frac{(x-1)^4}{4}", "+",
            "\\cdots"
        )
        lhs = VGroup(*series[1:])
        series.add_background_rectangle()
        series.scale(0.8)
        series.to_corner(UP+LEFT)
        for n in range(4):
            lhs[2*n].set_color(self.colors[n+1])
        self.braces = self.get_partial_sum_braces(
            lhs, np.zeros(self.n_iterations)
        )
        for brace in self.braces:
            brace.remove(brace[-1])

        self.play(FadeIn(
            series, 
            run_time = 3,
            lag_ratio = 0.5
        ))
        self.wait()
        self.series = series
        self.foreground_mobjects = [series]

    def show_bounds(self):
        dot = Dot(fill_opacity = 0)
        dot.move_to(self.series)
        v_lines = [
            DashedLine(*[
                self.coords_to_point(x, y)
                for y in (-2, 2)
            ])
            for x in (0, 1, 2)
        ]
        outer_v_lines = VGroup(*v_lines[::2])
        center_v_line = VGroup(v_lines[1])
        input_v_line = Line(*[
            self.coords_to_point(self.convergent_example, y)
            for y in (-4, 3)
        ])
        input_v_line.set_stroke(WHITE, width = 2)

        self.play(
            dot.move_to, self.coords_to_point(1, 0),
            dot.set_fill, YELLOW, 1,
        )
        self.wait()
        self.play(
            GrowFromCenter(center_v_line),
            Animation(dot)
        )
        self.play(Transform(center_v_line, outer_v_lines))

        self.foreground_mobjects.append(dot)

    def show_converging_point(self):
        approx_graphs = [
            self.get_graph(
                taylor_approximation(self.func, n, 1),
                color = WHITE
            )
            for n in range(1, self.n_iterations+1)
        ]
        colors = it.chain(
            self.colors[1:],
            [GREEN, MAROON_B],
            it.repeat(PINK)
        )
        for graph, color in zip(approx_graphs, colors):
            graph.set_color(color)
        for graph in approx_graphs:
            dot = Dot(color = WHITE)
            dot.move_to(self.input_to_graph_point(
                self.convergent_example, graph
            ))
            graph.dot = dot
            graph.add(dot)

        approx_graph = approx_graphs[0].deepcopy()
        approx_dot = approx_graph.dot
        brace = self.braces[0].copy()

        self.play(*it.chain(
            list(map(FadeIn, [approx_graph, brace])),
            list(map(Animation, self.foreground_mobjects))
        ))
        self.wait()
        new_graphs = approx_graphs[1:self.initial_n_iterations]
        for new_graph, new_brace in zip(new_graphs, self.braces[1:]):
            self.play(
                Transform(approx_graph, new_graph),
                Transform(brace, new_brace),
                *list(map(Animation, self.foreground_mobjects))
            )
            self.wait()
        approx_graph.remove(approx_dot)
        self.play(
            approx_dot.move_to, self.coords_to_point(self.divergent_example, 0),
            *it.chain(
                list(map(FadeOut, [approx_graph, brace])),
                list(map(Animation, self.foreground_mobjects))
            )
        )
        self.wait()

        self.approx_graphs = approx_graphs
        self.approx_dot = approx_dot
        
    def show_diverging_point(self):
        for graph in self.approx_graphs:
            graph.dot.move_to(self.input_to_graph_point(
                self.divergent_example, graph
            ))

        approx_graph = self.approx_graphs[0].deepcopy()
        brace = self.braces[0].copy()

        self.play(
            ReplacementTransform(
                self.approx_dot, approx_graph.dot
            ),
            FadeIn(approx_graph[0]),
            FadeIn(brace),
            *list(map(Animation, self.foreground_mobjects))
        )

        new_graphs = self.approx_graphs[1:self.initial_n_iterations]
        for new_graph, new_brace in zip(self.approx_graphs[1:], self.braces[1:]):
            self.play(
                Transform(approx_graph, new_graph),
                Transform(brace, new_brace),
                *list(map(Animation, self.foreground_mobjects))
            )
            self.wait()

        self.approx_dot = approx_graph.dot
        self.approx_graph = approx_graph

    def write_divergence(self):
        word = TextMobject("``Diverges''")
        word.next_to(self.approx_dot, RIGHT, LARGE_BUFF)
        word.shift(MED_SMALL_BUFF*DOWN)
        word.add_background_rectangle()
        arrow = Arrow(
            word.get_left(), self.approx_dot,
            buff = SMALL_BUFF,
            color = WHITE
        )

        self.play(
            Write(word),
            ShowCreation(arrow)
        )
        self.wait()
        new_graphs = self.approx_graphs[self.initial_n_iterations:]
        for new_graph in new_graphs:
            self.play(
                Transform(self.approx_graph, new_graph),
                *list(map(Animation, self.foreground_mobjects))
            )
            self.wait()

    def write_radius_of_convergence(self):
        line = Line(*[
            self.coords_to_point(x, 0)
            for x in (1, 2)
        ])
        line.set_color(YELLOW)
        brace = Brace(line, DOWN)
        words = brace.get_text("``Radius of convergence''")
        words.add_background_rectangle()

        self.play(
            GrowFromCenter(brace),
            ShowCreation(line)
        )
        self.wait()
        self.play(Write(words))
        self.wait(3)

class MoreToBeSaid(TeacherStudentsScene):
    CONFIG = {
        "seconds_to_blink" : 4,
    }
    def construct(self):
        words = TextMobject(
            "Lagrange error bounds, ", 
            "convergence tests, ",
            "$\\dots$"
        )
        words[0].set_color(BLUE)
        words[1].set_color(GREEN)
        words.to_edge(UP)
        fade_rect = FullScreenFadeRectangle()
        rect = Rectangle(height = 9, width = 16)        
        rect.set_height(FRAME_Y_RADIUS)
        rect.to_corner(UP+RIGHT)
        randy = self.get_students()[1]

        self.teacher_says(
            "There's still \\\\ more to learn!",
            target_mode = "surprised",
            bubble_kwargs = {"height" : 3, "width" : 4}
        )
        for word in words:
            self.play(FadeIn(word))
            self.wait()
        self.teacher_says(
            "About everything",
        )
        self.change_student_modes(*["pondering"]*3)
        self.wait()
        self.remove()
        self.pi_creatures = []##Hack
        self.play(
            RemovePiCreatureBubble(self.teacher),
            FadeOut(words),
            FadeIn(fade_rect),
            randy.change, "happy", rect
        )
        self.pi_creatures = [randy]
        self.play(ShowCreation(rect))
        self.wait(4)

class Chapter10Thanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Ali Yahya",
            "CrypticSwarm",
            "Kaustuv DeBiswas",
            "Kathryn Schmiedicke",
            "Karan Bhargava",
            "Ankit Agarwal",
            "Yu Jun",
            "Dave Nicponski",
            "Damion Kistler",
            "Juan Benet",
            "Othman Alikhan",
            "Markus Persson",
            "Joseph John Cox",
            "Dan Buchoff",
            "Derek Dai",
            "Luc Ritchie",
            "Ahmad Bamieh",
            "Mark Govea",
            "Zac Wentzell",
            "Robert Teed",
            "Jason Hise",
            "Meshal Alshammari",
            "Bernd Sing",
            "Nils Schneider",
            "James Thornton",
            "Mustafa Mahdi",
            "Jonathan Eppele",
            "Mathew Bramson",
            "Jerry Ling",
            "Vecht",
            "Shimin Kuang",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ],
    }

class Thumbnail(ExampleApproximationWithSine):
    CONFIG = {
        "graph_origin" : DOWN,
        "x_axis_label" : "",
        "y_axis_label" : "",
        "x_axis_width" : 14,
        "graph_stroke_width" : 8,
    }
    def construct(self):
        self.setup_axes()

        cos_graph = self.get_graph(np.cos)
        cos_graph.set_stroke(BLUE, self.graph_stroke_width)
        quad_graph = self.get_graph(taylor_approximation(np.cos, 2))
        quad_graph.set_stroke(GREEN, self.graph_stroke_width)
        quartic = self.get_graph(taylor_approximation(np.cos, 4))
        quartic.set_stroke(PINK, self.graph_stroke_width)
        self.add(cos_graph, quad_graph, quartic)

        title = TextMobject("Taylor Series")
        title.set_width(1.5*FRAME_X_RADIUS)
        title.add_background_rectangle()
        title.to_edge(UP)
        self.add(title)















