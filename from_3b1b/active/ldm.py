from manimlib.imports import *
from from_3b1b.active.bayes.beta_helpers import *
import math


class StreamIntro(Scene):
    def construct(self):
        # Add logo
        logo = Logo()
        spikes = VGroup(*[
            spike
            for layer in logo.spike_layers
            for spike in layer
        ])
        self.add(*logo.family_members_with_points())

        # Add label
        label = TextMobject("The lesson will\\\\begin shortly")
        label.scale(2)
        label.next_to(logo, DOWN)
        self.add(label)

        self.camera.frame.move_to(DOWN)

        for spike in spikes:
            point = spike.get_start()
            spike.angle = angle_of_vector(point)

        anims = []
        for spike in spikes:
            anims.append(Rotate(
                spike, spike.angle * 28 * 2,
                about_point=ORIGIN,
                rate_func=linear,
            ))
        self.play(*anims, run_time=60 * 5)
        self.wait(20)


class OldStreamIntro(Scene):
    def construct(self):
        morty = Mortimer()
        morty.flip()
        morty.set_height(2)
        morty.to_corner(DL)
        self.play(PiCreatureSays(
            morty, "The lesson will\\\\begin soon.",
            bubble_kwargs={
                "height": 2,
                "width": 3,
            },
            target_mode="hooray",
        ))
        bound = AnimatedBoundary(morty.bubble.content, max_stroke_width=1)
        self.add(bound, morty.bubble, morty.bubble.content)
        self.remove(morty.bubble.content)
        morty.bubble.set_fill(opacity=0)

        self.camera.frame.scale(0.6, about_edge=DL)

        self.play(Blink(morty))
        self.wait(5)
        self.play(Blink(morty))
        self.wait(3)
        return

        text = TextMobject("The lesson will\\\\begin soon.")
        text.set_height(1.5)
        text.to_corner(DL, buff=LARGE_BUFF)
        self.add(text)


class QuadraticFormula(TeacherStudentsScene):
    def construct(self):
        formula = TexMobject(
            "\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
        )
        formula.next_to(self.students, UP, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        self.add(formula)

        self.change_student_modes(
            "angry", "tired", "sad",
            look_at_arg=formula,
        )
        self.teacher_says(
            "It doesn't have\\\\to be this way.",
            bubble_kwargs={
                "width": 4,
                "height": 3,
            }
        )
        self.wait(5)
        self.change_student_modes(
            "pondering", "thinking", "erm",
            look_at_arg=formula
        )
        self.wait(12)


class SimplerQuadratic(Scene):
    def construct(self):
        tex = TexMobject("m \\pm \\sqrt{m^2 - p}")
        tex.set_stroke(BLACK, 12, background=True)
        tex.scale(1.5)
        self.add(tex)


class CosGraphs(Scene):
    def construct(self):
        axes = Axes(
            x_min=-0.75 * TAU,
            x_max=0.75 * TAU,
            y_min=-1.5,
            y_max=1.5,
            x_axis_config={
                "tick_frequency": PI / 4,
                "include_tip": False,
            },
            y_axis_config={
                "tick_frequency": 0.5,
                "include_tip": False,
                "unit_size": 1.5,
            }
        )

        graph1 = axes.get_graph(np.cos)
        graph2 = axes.get_graph(lambda x: np.cos(x)**2)

        graph1.set_stroke(YELLOW, 5)
        graph2.set_stroke(BLUE, 5)

        label1 = TexMobject("\\cos(x)")
        label2 = TexMobject("\\cos^2(x)")

        label1.match_color(graph1)
        label1.set_height(0.75)
        label1.next_to(axes.input_to_graph_point(-PI, graph1), DOWN)

        label2.match_color(graph2)
        label2.set_height(0.75)
        label2.next_to(axes.input_to_graph_point(PI, graph2), UP)

        for mob in [graph1, graph2, label1, label2]:
            mc = mob.copy()
            mc.set_stroke(BLACK, 10, background=True)
            self.add(mc)

        self.add(axes)
        self.add(graph1)
        self.add(graph2)
        self.add(label1)
        self.add(label2)

        self.embed()


class SineWave(Scene):
    def construct(self):
        w_axes = self.get_wave_axes()
        square, circle, c_axes = self.get_edge_group()

        self.add(w_axes)
        self.add(square, circle, c_axes)

        theta_tracker = ValueTracker(0)
        c_dot = Dot(color=YELLOW)
        c_line = Line(DOWN, UP, color=GREEN)
        w_dot = Dot(color=YELLOW)
        w_line = Line(DOWN, UP, color=GREEN)

        def update_c_dot(dot, axes=c_axes, tracker=theta_tracker):
            theta = tracker.get_value()
            dot.move_to(axes.c2p(
                np.cos(theta),
                np.sin(theta),
            ))

        def update_c_line(line, axes=c_axes, tracker=theta_tracker):
            theta = tracker.get_value()
            x = np.cos(theta)
            y = np.sin(theta)
            if y == 0:
                y = 1e-6
            line.put_start_and_end_on(
                axes.c2p(x, 0),
                axes.c2p(x, y),
            )

        def update_w_dot(dot, axes=w_axes, tracker=theta_tracker):
            theta = tracker.get_value()
            dot.move_to(axes.c2p(theta, np.sin(theta)))

        def update_w_line(line, axes=w_axes, tracker=theta_tracker):
            theta = tracker.get_value()
            x = theta
            y = np.sin(theta)
            if y == 0:
                y = 1e-6
            line.put_start_and_end_on(
                axes.c2p(x, 0),
                axes.c2p(x, y),
            )

        def get_partial_circle(circle=circle, tracker=theta_tracker):
            result = circle.copy()
            theta = tracker.get_value()
            result.pointwise_become_partial(
                circle, 0, clip(theta / TAU, 0, 1),
            )
            result.set_stroke(RED, width=3)
            return result

        def get_partial_wave(axes=w_axes, tracker=theta_tracker):
            theta = tracker.get_value()
            graph = axes.get_graph(np.sin, x_min=0, x_max=theta, step_size=0.025)
            graph.set_stroke(BLUE, 3)
            return graph

        def get_h_line(axes=w_axes, tracker=theta_tracker):
            theta = tracker.get_value()
            return Line(
                axes.c2p(0, 0),
                axes.c2p(theta, 0),
                stroke_color=RED
            )

        c_dot.add_updater(update_c_dot)
        c_line.add_updater(update_c_line)
        w_dot.add_updater(update_w_dot)
        w_line.add_updater(update_w_line)
        partial_circle = always_redraw(get_partial_circle)
        partial_wave = always_redraw(get_partial_wave)
        h_line = always_redraw(get_h_line)

        self.add(partial_circle)
        self.add(partial_wave)
        self.add(h_line)
        self.add(c_line, c_dot)
        self.add(w_line, w_dot)

        sin_label = TexMobject(
            "\\sin\\left(\\theta\\right)",
            tex_to_color_map={"\\theta": RED}
        )
        sin_label.next_to(w_axes.get_top(), UR)
        self.add(sin_label)

        self.play(
            theta_tracker.set_value, 1.25 * TAU,
            run_time=15,
            rate_func=linear,
        )

    def get_wave_axes(self):
        wave_axes = Axes(
            x_min=0,
            x_max=1.25 * TAU,
            y_min=-1.0,
            y_max=1.0,
            x_axis_config={
                "tick_frequency": TAU / 8,
                "unit_size": 1.0,
            },
            y_axis_config={
                "tick_frequency": 0.5,
                "include_tip": False,
                "unit_size": 1.5,
            }
        )
        wave_axes.y_axis.add_numbers(
            -1, 1, number_config={"num_decimal_places": 1}
        )
        wave_axes.to_edge(RIGHT, buff=MED_SMALL_BUFF)

        pairs = [
            (PI / 2, "\\frac{\\pi}{2}"),
            (PI, "\\pi"),
            (3 * PI / 2, "\\frac{3\\pi}{2}"),
            (2 * PI, "2\\pi"),
        ]
        syms = VGroup()
        for val, tex in pairs:
            sym = TexMobject(tex)
            sym.scale(0.5)
            sym.next_to(wave_axes.c2p(val, 0), DOWN, MED_SMALL_BUFF)
            syms.add(sym)
        wave_axes.add(syms)

        theta = TexMobject("\\theta")
        theta.set_color(RED)
        theta.next_to(wave_axes.x_axis.get_end(), UP)
        wave_axes.add(theta)

        return wave_axes

    def get_edge_group(self):
        axes_max = 1.25
        radius = 1.5
        axes = Axes(
            x_min=-axes_max,
            x_max=axes_max,
            y_min=-axes_max,
            y_max=axes_max,
            axis_config={
                "tick_frequency": 0.5,
                "include_tip": False,
                "numbers_with_elongated_ticks": [-1, 1],
                "tick_size": 0.05,
                "unit_size": radius,
            },
        )
        axes.to_edge(LEFT, buff=MED_LARGE_BUFF)

        background = SurroundingRectangle(axes, buff=MED_SMALL_BUFF)
        background.set_stroke(WHITE, 1)
        background.set_fill(GREY_E, 1)

        circle = Circle(radius=radius)
        circle.move_to(axes)
        circle.set_stroke(WHITE, 1)

        nums = VGroup()
        for u in 1, -1:
            num = Integer(u)
            num.set_height(0.2)
            num.set_stroke(BLACK, 3, background=True)
            num.next_to(axes.c2p(u, 0), DOWN + u * RIGHT, SMALL_BUFF)
            nums.add(num)

        axes.add(nums)

        return background, circle, axes


class CosWave(SineWave):
    CONFIG = {
        "include_square": False,
    }

    def construct(self):
        w_axes = self.get_wave_axes()
        square, circle, c_axes = self.get_edge_group()

        self.add(w_axes)
        self.add(square, circle, c_axes)

        theta_tracker = ValueTracker(0)
        c_dot = Dot(color=YELLOW)
        c_line = Line(DOWN, UP, color=GREEN)
        w_dot = Dot(color=YELLOW)
        w_line = Line(DOWN, UP, color=GREEN)

        def update_c_dot(dot, axes=c_axes, tracker=theta_tracker):
            theta = tracker.get_value()
            dot.move_to(axes.c2p(
                np.cos(theta),
                np.sin(theta),
            ))

        def update_c_line(line, axes=c_axes, tracker=theta_tracker):
            theta = tracker.get_value()
            x = np.cos(theta)
            y = np.sin(theta)
            line.set_points_as_corners([
                axes.c2p(0, y),
                axes.c2p(x, y),
            ])

        def update_w_dot(dot, axes=w_axes, tracker=theta_tracker):
            theta = tracker.get_value()
            dot.move_to(axes.c2p(theta, np.cos(theta)))

        def update_w_line(line, axes=w_axes, tracker=theta_tracker):
            theta = tracker.get_value()
            x = theta
            y = np.cos(theta)
            if y == 0:
                y = 1e-6
            line.set_points_as_corners([
                axes.c2p(x, 0),
                axes.c2p(x, y),
            ])

        def get_partial_circle(circle=circle, tracker=theta_tracker):
            result = circle.copy()
            theta = tracker.get_value()
            result.pointwise_become_partial(
                circle, 0, clip(theta / TAU, 0, 1),
            )
            result.set_stroke(RED, width=3)
            return result

        def get_partial_wave(axes=w_axes, tracker=theta_tracker):
            theta = tracker.get_value()
            graph = axes.get_graph(np.cos, x_min=0, x_max=theta, step_size=0.025)
            graph.set_stroke(PINK, 3)
            return graph

        def get_h_line(axes=w_axes, tracker=theta_tracker):
            theta = tracker.get_value()
            return Line(
                axes.c2p(0, 0),
                axes.c2p(theta, 0),
                stroke_color=RED
            )

        def get_square(line=c_line):
            square = Square()
            square.set_stroke(WHITE, 1)
            square.set_fill(MAROON_B, opacity=0.5)
            square.match_width(line)
            square.move_to(line, DOWN)
            return square

        def get_square_graph(axes=w_axes, tracker=theta_tracker):
            theta = tracker.get_value()
            graph = axes.get_graph(
                lambda x: np.cos(x)**2, x_min=0, x_max=theta, step_size=0.025
            )
            graph.set_stroke(MAROON_B, 3)
            return graph

        c_dot.add_updater(update_c_dot)
        c_line.add_updater(update_c_line)
        w_dot.add_updater(update_w_dot)
        w_line.add_updater(update_w_line)
        h_line = always_redraw(get_h_line)
        partial_circle = always_redraw(get_partial_circle)
        partial_wave = always_redraw(get_partial_wave)

        self.add(partial_circle)
        self.add(partial_wave)
        self.add(h_line)
        self.add(c_line, c_dot)
        self.add(w_line, w_dot)

        if self.include_square:
            self.add(always_redraw(get_square))
            self.add(always_redraw(get_square_graph))

        cos_label = TexMobject(
            "\\cos\\left(\\theta\\right)",
            tex_to_color_map={"\\theta": RED}
        )
        cos_label.next_to(w_axes.get_top(), UR)
        self.add(cos_label)

        self.play(
            theta_tracker.set_value, 1.25 * TAU,
            run_time=15,
            rate_func=linear,
        )


class CosSquare(CosWave):
    CONFIG = {
        "include_square": True
    }


class ComplexNumberPreview(Scene):
    def construct(self):
        plane = ComplexPlane(axis_config={"stroke_width": 4})
        plane.add_coordinates()

        z = complex(2, 1)
        dot = Dot()
        dot.move_to(plane.n2p(z))
        label = TexMobject("2+i")
        label.set_color(YELLOW)
        dot.set_color(YELLOW)
        label.next_to(dot, UR, SMALL_BUFF)
        label.set_stroke(BLACK, 5, background=True)

        line = Line(plane.n2p(0), plane.n2p(z))
        arc = Arc(start_angle=0, angle=np.log(z).imag, radius=0.5)

        self.add(plane)
        self.add(line, arc)
        self.add(dot)
        self.add(label)

        self.embed()


class ComplexMultiplication(Scene):
    def construct(self):
        # Add plane
        plane = ComplexPlane()
        plane.add_coordinates()

        z = complex(2, 1)
        z_dot = Dot(color=PINK)
        z_dot.move_to(plane.n2p(z))
        z_label = TexMobject("z")
        z_label.next_to(z_dot, UR, buff=0.5 * SMALL_BUFF)
        z_label.match_color(z_dot)

        self.add(plane)
        self.add(z_dot)
        self.add(z_label)

        # Show 1
        one_vect = Vector(RIGHT)
        one_vect.set_color(YELLOW)
        one_vect.target = Vector(plane.n2p(z))
        one_vect.target.match_style(one_vect)

        z_rhs = TexMobject("=", "z \\cdot 1")
        z_rhs[1].match_color(one_vect)
        z_rhs.next_to(z_label, RIGHT, 1.5 * SMALL_BUFF, aligned_edge=DOWN)
        z_rhs.set_stroke(BLACK, 3, background=True)

        one_label, i_label = [l for l in plane.coordinate_labels if l.get_value() == 1]

        self.play(GrowArrow(one_vect))
        self.wait()
        self.add(one_vect, z_dot)
        self.play(
            MoveToTarget(one_vect),
            TransformFromCopy(one_label, z_rhs),
        )
        self.wait()

        # Show i
        i_vect = Vector(UP, color=GREEN)
        zi_point = plane.n2p(z * complex(0, 1))
        i_vect.target = Vector(zi_point)
        i_vect.target.match_style(i_vect)
        i_vect_label = TexMobject("z \\cdot i")
        i_vect_label.match_color(i_vect)
        i_vect_label.set_stroke(BLACK, 3, background=True)
        i_vect_label.next_to(zi_point, UL, SMALL_BUFF)

        self.play(GrowArrow(i_vect))
        self.wait()
        self.play(
            MoveToTarget(i_vect),
            TransformFromCopy(i_label, i_vect_label),
            run_time=1,
        )
        self.wait()

        self.play(
            TransformFromCopy(one_vect, i_vect.target, path_arc=-90 * DEGREES),
        )
        self.wait()

        # Transform plane
        plane.generate_target()
        for mob in plane.target.family_members_with_points():
            if isinstance(mob, Line):
                mob.set_stroke(GREY, opacity=0.5)
        new_plane = ComplexPlane(faded_line_ratio=0)

        self.remove(plane)
        self.add(plane, new_plane, *self.mobjects)

        new_plane.generate_target()
        new_plane.target.apply_complex_function(lambda w, z=z: w * z)

        self.play(
            MoveToTarget(plane),
            MoveToTarget(new_plane),
            run_time=6,
            rate_func=there_and_back_with_pause
        )
        self.wait()

        # Show Example Point
        w = complex(2, -1)
        w_dot = Dot(plane.n2p(w), color=WHITE)
        one_vects = VGroup(*[Vector(RIGHT) for x in range(2)])
        one_vects.arrange(RIGHT, buff=0)
        one_vects.move_to(plane.n2p(0), LEFT)
        one_vects.set_color(YELLOW)
        new_i_vect = Vector(DOWN)
        new_i_vect.move_to(plane.n2p(2), UP)
        new_i_vect.set_color(GREEN)
        vects = VGroup(*one_vects, new_i_vect)
        vects.set_opacity(0.8)

        w_group = VGroup(*vects, w_dot)
        w_group.target = VGroup(
            one_vect.copy().set_opacity(0.8),
            one_vect.copy().shift(plane.n2p(z)).set_opacity(0.8),
            i_vect.copy().rotate(PI, about_point=ORIGIN).shift(2 * plane.n2p(z)).set_opacity(0.8),
            Dot(plane.n2p(w * z), color=WHITE)
        )

        self.play(FadeInFromLarge(w_dot))
        self.wait()
        self.play(ShowCreation(vects))
        self.wait()

        self.play(
            MoveToTarget(plane),
            MoveToTarget(new_plane),
            MoveToTarget(w_group),
            run_time=2,
            path_arc=np.log(z).imag,
        )
        self.wait()


class RotatePiCreature(Scene):
    def construct(self):
        randy = Randolph(mode="thinking")
        randy.set_height(6)

        plane = ComplexPlane(x_min=-12, x_max=12)
        plane.add_coordinates()

        self.camera.frame.move_to(3 * RIGHT)

        self.add(randy)
        self.wait()
        self.play(Rotate(randy, 30 * DEGREES, run_time=3))
        self.wait()
        self.play(Rotate(randy, -30 * DEGREES))

        self.add(plane, randy)
        self.play(
            ShowCreation(plane),
            randy.set_opacity, 0.75,
        )
        self.wait()

        dots = VGroup()
        for mob in randy.family_members_with_points():
            for point in mob.get_anchors():
                dot = Dot(point)
                dot.set_height(0.05)
                dots.add(dot)

        self.play(ShowIncreasingSubsets(dots))
        self.wait()

        label = VGroup(
            TexMobject("(x + iy)"),
            Vector(DOWN),
            TexMobject("(\\cos(30^\\circ) + i\\sin(30^\\circ))", "(x + iy)"),
        )
        label[2][0].set_color(YELLOW)
        label.arrange(DOWN)
        label.to_corner(DR)
        label.shift(3 * RIGHT)

        for mob in label:
            mob.add_background_rectangle()

        self.play(FadeIn(label))
        self.wait()

        randy.add(dots)
        self.play(Rotate(randy, 30 * DEGREES), run_time=3)
        self.wait()


class ExpMeaning(Scene):
    CONFIG = {
        "include_circle": True
    }

    def construct(self):
        # Plane
        plane = ComplexPlane(y_min=-6, y_max=6)
        plane.shift(1.5 * DOWN)
        plane.add_coordinates()
        if self.include_circle:
            circle = Circle(radius=1)
            circle.set_stroke(RED, 1)
            circle.move_to(plane.n2p(0))
            plane.add(circle)

        # Equation
        equation = TexMobject(
            "\\text{exp}(i\\theta) = ",
            "1 + ",
            "i\\theta + ",
            "{(i\\theta)^2 \\over 2} + ",
            "{(i\\theta)^3 \\over 6} + ",
            "{(i\\theta)^4 \\over 24} + ",
            "\\cdots",
            tex_to_color_map={
                "\\theta": YELLOW,
                "i": GREEN,
            },
        )
        equation.add_background_rectangle(buff=MED_SMALL_BUFF, opacity=1)
        equation.to_edge(UL, buff=0)

        # Label
        theta_tracker = ValueTracker(0)
        theta_label = VGroup(
            TexMobject("\\theta = "),
            DecimalNumber(0, num_decimal_places=4)
        )
        theta_decimal = theta_label[1]
        theta_decimal.add_updater(
            lambda m, tt=theta_tracker: m.set_value(tt.get_value())
        )
        theta_label.arrange(RIGHT, buff=SMALL_BUFF)
        theta_label.set_color(YELLOW)
        theta_label.add_to_back(BackgroundRectangle(
            theta_label,
            buff=MED_SMALL_BUFF,
            fill_opacity=1,
        ))
        theta_label.next_to(equation, DOWN, aligned_edge=LEFT, buff=0)

        # Vectors
        def get_vectors(n_vectors=20, plane=plane, tracker=theta_tracker):
            last_tip = plane.n2p(0)
            z = complex(0, tracker.get_value())
            vects = VGroup()
            colors = color_gradient([GREEN, YELLOW, RED], 6)
            for i, color in zip(range(n_vectors), it.cycle(colors)):
                vect = Vector(complex_to_R3(z**i / math.factorial(i)))
                vect.set_color(color)
                vect.shift(last_tip)
                last_tip = vect.get_end()
                vects.add(vect)
            return vects

        vectors = always_redraw(get_vectors)
        dot = Dot()
        dot.set_height(0.03)
        dot.add_updater(lambda m, vs=vectors: m.move_to(vs[-1].get_end()))

        self.add(plane)
        self.add(vectors)
        self.add(dot)
        self.add(equation)
        self.add(theta_label)

        self.play(
            theta_tracker.set_value, 1,
            run_time=3,
            rate_func=smooth,
        )
        self.wait()
        for target in PI, TAU:
            self.play(
                theta_tracker.set_value, target,
                run_time=10,
            )
            self.wait()

        self.embed()


class ExpMeaningWithoutCircle(ExpMeaning):
    CONFIG = {
        "include_circle": False,
    }


class PositionAndVelocityExample(Scene):
    def construct(self):
        plane = NumberPlane()

        self.add(plane)

        self.embed()


class EulersFormula(Scene):
    def construct(self):
        kw = {"tex_to_color_map": {"\\theta": YELLOW}}
        formula = TexMobject(
            "&e^{i\\theta} = \\\\ &\\cos\\left(\\theta\\right) + i\\cdot\\sin\\left(\\theta\\right)",
        )[0]
        formula[:4].scale(2, about_edge=UL)
        formula[:4].shift(SMALL_BUFF * RIGHT + MED_LARGE_BUFF * UP)
        VGroup(formula[2], formula[8], formula[17]).set_color(YELLOW)
        formula.scale(1.5)
        formula.set_stroke(BLACK, 5, background=True)
        self.add(formula)


class EtoILimit(Scene):
    def construct(self):
        tex = TexMobject(
            "\\lim_{n \\to \\infty} \\left(1 + \\frac{it}{n}\\right)^n",
        )[0]
        VGroup(tex[3], tex[12], tex[14]).set_color(YELLOW)
        tex[9].set_color(BLUE)
        tex.scale(1.5)
        tex.set_stroke(BLACK, 5, background=True)
        # self.add(tex)

        text = TextMobject("Interest rate\\\\of ", "$\\sqrt{-1}$")
        text[1].set_color(BLUE) 
        text.scale(1.5)
        text.set_stroke(BLACK, 5, background=True)
        self.add(text)


class ImaginaryInterestRates(Scene):
    def construct(self):
        plane = ComplexPlane(x_min=-20, x_max=20, y_min=-20, y_max=20)
        plane.add_coordinates()
        circle = Circle(radius=1)
        circle.set_stroke(YELLOW, 1)
        self.add(plane, circle)

        frame = self.camera.frame
        frame.save_state()
        frame.generate_target()
        frame.target.set_width(25)
        frame.target.move_to(8 * RIGHT + 2 * DOWN)

        dt_tracker = ValueTracker(1)

        def get_vectors(tracker=dt_tracker, plane=plane, T=8):
            dt = tracker.get_value()
            last_z = 1
            vects = VGroup()
            for t in np.arange(0, T, dt):
                next_z = last_z + complex(0, 1) * last_z * dt
                vects.add(Arrow(
                    plane.n2p(last_z),
                    plane.n2p(next_z),
                    buff=0,
                ))
                last_z = next_z
            vects.set_submobject_colors_by_gradient(YELLOW, GREEN, BLUE)
            return vects

        vects = get_vectors()

        line = Line()
        line.add_updater(lambda m, v=vects: m.put_start_and_end_on(
            ORIGIN, v[-1].get_start() if len(v) > 0 else RIGHT,
        ))

        self.add(line)
        self.play(
            ShowIncreasingSubsets(
                vects,
                rate_func=linear,
                int_func=np.ceil,
            ),
            MoveToTarget(
                frame,
                rate_func=squish_rate_func(smooth, 0.5, 1),
            ),
            run_time=8,
        )
        self.wait()
        self.play(FadeOut(line))

        self.remove(vects)
        vects = always_redraw(get_vectors)
        self.add(vects)
        self.play(
            Restore(frame),
            dt_tracker.set_value, 0.2,
            run_time=5,
        )
        self.wait()
        self.play(dt_tracker.set_value, 0.01, run_time=3)
        vects.clear_updaters()
        self.wait()

        theta_tracker = ValueTracker(0)

        def get_arc(tracker=theta_tracker):
            theta = tracker.get_value()
            arc = Arc(
                radius=1,
                stroke_width=3,
                stroke_color=RED,
                start_angle=0,
                angle=theta
            )
            return arc

        arc = always_redraw(get_arc)
        dot = Dot()
        dot.add_updater(lambda m, arc=arc: m.move_to(arc.get_end()))

        label = VGroup(
            DecimalNumber(0, num_decimal_places=3),
            TextMobject("Years")
        )
        label.arrange(RIGHT, aligned_edge=DOWN)
        label.move_to(3 * LEFT + 1.5 * UP)

        label[0].set_color(RED)
        label[0].add_updater(lambda m, tt=theta_tracker: m.set_value(tt.get_value()))

        self.add(BackgroundRectangle(label), label, arc, dot)
        for n in range(1, 5):
            target = n * PI / 2
            self.play(
                theta_tracker.set_value, target,
                run_time=3
            )
            self.wait(2)


class Logs(Scene):
    def construct(self):
        log = TexMobject(
            "&\\text{log}(ab) = \\\\ &\\text{log}(a) + \\text{log}(b)",
            tex_to_color_map={"a": BLUE, "b": YELLOW},
            alignment="",
        )
        
        log.scale(1.5)
        log.set_stroke(BLACK, 5, background=True)

        self.add(log)


class LnX(Scene):
    def construct(self):
        sym = TexMobject("\\ln(x)")
        sym.scale(3)
        sym.shift(UP)
        sym.set_stroke(BLACK, 5, background=True)

        word = TextMobject("Natural?")
        word.scale(1.5)
        word.set_color(YELLOW)
        word.set_stroke(BLACK, 5, background=True)
        word.next_to(sym, DOWN, buff=0.5)
        arrow = Arrow(word.get_top(), sym[0][1].get_bottom())

        self.add(sym, word, arrow)


class HarmonicSum(Scene):
    def construct(self):
        axes = Axes(
            x_min=0,
            x_max=13,
            y_min=0,
            y_max=1.25,
            y_axis_config={
                "unit_size": 4,
                "tick_frequency": 0.25,
            }
        )
        axes.to_corner(DL, buff=1)
        axes.x_axis.add_numbers()
        axes.y_axis.add_numbers(
            *np.arange(0.25, 1.25, 0.25),
            number_config={"num_decimal_places": 2},
        )
        self.add(axes)

        graph = axes.get_graph(lambda x: 1 / x, x_min=0.1, x_max=15)
        graph_fill = graph.copy()
        graph_fill.add_line_to(axes.c2p(15, 0))
        graph_fill.add_line_to(axes.c2p(1, 0))
        graph_fill.add_line_to(axes.c2p(1, 1))
        graph.set_stroke(WHITE, 3)
        graph_fill.set_fill(BLUE_E, 0.5)
        graph_fill.set_stroke(width=0)
        self.add(graph, graph_fill)

        bars = VGroup()
        bar_labels = VGroup()
        for x in range(1, 15):
            line = Line(axes.c2p(x, 0), axes.c2p(x + 1, 1 / x))
            bar = Rectangle()
            bar.set_fill(GREEN_E, 1)
            bar.replace(line, stretch=True)
            bars.add(bar)

            label = TexMobject(f"1 \\over {x}")
            label.set_height(0.7)
            label.next_to(bar, UP, SMALL_BUFF)
            bar_labels.add(label)

        bars.set_submobject_colors_by_gradient(GREEN_C, GREEN_E)
        bars.set_stroke(WHITE, 1)
        bars.set_fill(opacity=0.25)

        self.add(bars)
        self.add(bar_labels)


        self.embed()


class PowerTower(Scene):
    def construct(self):
        mob = TexMobject("4 = x^{x^{{x^{x^{x^{\cdot^{\cdot^{\cdot}}}}}}}}")
        mob[0][-1].shift(0.1 * DL)
        mob[0][-2].shift(0.05 * DL)

        mob.set_height(4)
        mob.set_stroke(BLACK, 5, background=True)

        self.add(mob)


class ItoTheI(Scene):
    def construct(self):
        tex = TexMobject("i^i")
        # tex = TexMobject("\\sqrt{-1}^{\\sqrt{-1}}")
        tex.set_height(3)
        tex.set_stroke(BLACK, 8, background=True)
        self.add(tex)


class ComplexExponentialPlay(Scene):
    def setup(self):
        self.transform_alpha = 0

    def construct(self):
        # Plane
        plane = ComplexPlane(
            x_min=-2 * FRAME_WIDTH,
            x_max=2 * FRAME_WIDTH,
            y_min=-2 * FRAME_HEIGHT,
            y_max=2 * FRAME_HEIGHT,
        )
        plane.add_coordinates()
        self.add(plane)

        # R Dot
        r_dot = Dot(color=YELLOW)

        def update_r_dot(dot, point_tracker=self.mouse_drag_point):
            point = point_tracker.get_location()
            if abs(point[0]) < 0.1:
                point[0] = 0
            if abs(point[1]) < 0.1:
                point[1] = 0
            dot.move_to(point)

        r_dot.add_updater(update_r_dot)
        self.mouse_drag_point.move_to(plane.n2p(1))

        # Transformed sample dots
        def func(z, dot=r_dot, plane=plane):
            r = plane.p2n(dot.get_center())
            result = np.exp(r * z)
            if abs(result) > 20:
                result *= 20 / abs(result)
            return result

        sample_dots = VGroup()
        dot_template = Dot(radius=0.05)
        dot_template.set_opacity(0.8)
        spacing = 0.05
        for x in np.arange(-7, 7, spacing):
            dot = dot_template.copy()
            dot.set_color(TEAL)
            dot.z = x
            dot.move_to(plane.n2p(dot.z))
            sample_dots.add(dot)
        for y in np.arange(-6, 6, spacing):
            dot = dot_template.copy()
            dot.set_color(MAROON)
            dot.z = complex(0, y)
            dot.move_to(plane.n2p(dot.z))
            sample_dots.add(dot)

        special_values = [1, complex(0, 1), -1, complex(0, -1)]
        special_dots = VGroup(*[
            list(filter(lambda d: abs(d.z - x) < 0.01, sample_dots))[0]
            for x in special_values
        ])
        for dot in special_dots:
            dot.set_fill(opacity=1)
            dot.scale(1.2)
            dot.set_stroke(WHITE, 2)

        sample_dots.save_state()

        def update_sample(sample, f=func, plane=plane, scene=self):
            sample.restore()
            sample.apply_function_to_submobject_positions(
                lambda p: interpolate(
                    p,
                    plane.n2p(f(plane.p2n(p))),
                    scene.transform_alpha,
                )
            )
            return sample

        sample_dots.add_updater(update_sample)

        # Sample lines
        x_line = Line(plane.n2p(plane.x_min), plane.n2p(plane.x_max))
        y_line = Line(plane.n2p(plane.y_min), plane.n2p(plane.y_max))
        y_line.rotate(90 * DEGREES)
        x_line.set_color(GREEN)
        y_line.set_color(PINK)
        axis_lines = VGroup(x_line, y_line)
        for line in axis_lines:
            line.insert_n_curves(50)
        axis_lines.save_state()

        def update_axis_liens(lines=axis_lines, f=func, plane=plane, scene=self):
            lines.restore()
            lines.apply_function(
                lambda p: interpolate(
                    p,
                    plane.n2p(f(plane.p2n(p))),
                    scene.transform_alpha,
                )
            )
            lines.make_smooth()

        axis_lines.add_updater(update_axis_liens)

        # Labels
        labels = VGroup(
            TexMobject("f(1)"),
            TexMobject("f(i)"),
            TexMobject("f(-1)"),
            TexMobject("f(-i)"),
        )
        for label, dot in zip(labels, special_dots):
            label.set_height(0.3)
            label.match_color(dot)
            label.set_stroke(BLACK, 3, background=True)
            label.add_background_rectangle(opacity=0.5)

        def update_labels(labels, dots=special_dots, scene=self):
            for label, dot in zip(labels, dots):
                label.next_to(dot, UR, 0.5 * SMALL_BUFF)
                label.set_opacity(self.transform_alpha)

        labels.add_updater(update_labels)

        # Titles
        title = TexMobject(
            "f(x) =", "\\text{exp}(r\\cdot x)",
            tex_to_color_map={"r": YELLOW}
        )
        title.to_corner(UL)
        title.set_stroke(BLACK, 5, background=True)
        brace = Brace(title[1:], UP, buff=SMALL_BUFF)
        e_pow = TexMobject("e^{rx}", tex_to_color_map={"r": YELLOW})
        e_pow.add_background_rectangle()
        e_pow.next_to(brace, UP, buff=SMALL_BUFF)
        title.add(brace, e_pow)

        r_eq = VGroup(
            TexMobject("r=", tex_to_color_map={"r": YELLOW}),
            DecimalNumber(1)
        )
        r_eq.arrange(RIGHT, aligned_edge=DOWN)
        r_eq.next_to(title, DOWN, aligned_edge=LEFT)
        r_eq[0].set_stroke(BLACK, 5, background=True)
        r_eq[1].set_color(YELLOW)
        r_eq[1].add_updater(lambda m: m.set_value(plane.p2n(r_dot.get_center())))

        self.add(title)
        self.add(r_eq)

        # self.add(axis_lines)
        self.add(sample_dots)
        self.add(r_dot)
        self.add(labels)

        # Animations
        def update_transform_alpha(mob, alpha, scene=self):
            scene.transform_alpha = alpha

        frame = self.camera.frame
        frame.set_height(10)
        r_dot.clear_updaters()
        r_dot.move_to(plane.n2p(1))

        self.play(
            UpdateFromAlphaFunc(
                VectorizedPoint(),
                update_transform_alpha,
            )
        )
        self.play(r_dot.move_to, plane.n2p(2))
        self.wait()
        self.play(r_dot.move_to, plane.n2p(PI))
        self.wait()
        self.play(r_dot.move_to, plane.n2p(np.log(2)))
        self.wait()
        self.play(r_dot.move_to, plane.n2p(complex(0, np.log(2))), path_arc=90 * DEGREES, run_time=2)
        self.wait()
        self.play(r_dot.move_to, plane.n2p(complex(0, PI / 2)))
        self.wait()
        self.play(r_dot.move_to, plane.n2p(np.log(2)), run_time=2)
        self.wait()
        self.play(frame.set_height, 14)
        self.play(r_dot.move_to, plane.n2p(complex(np.log(2), PI)), run_time=3)
        self.wait()
        self.play(r_dot.move_to, plane.n2p(complex(np.log(2), TAU)), run_time=3)
        self.wait()

        self.embed()

    def on_mouse_scroll(self, point, offset):
        frame = self.camera.frame
        if self.zoom_on_scroll:
            factor = 1 + np.arctan(10 * offset[1])
            frame.scale(factor, about_point=ORIGIN)
        else:
            self.transform_alpha = clip(self.transform_alpha + 5 * offset[1], 0, 1)


class LDMEndScreen(PatreonEndScreen):
    CONFIG = {
        "scroll_time": 20,
        "specific_patrons": [
            "1stViewMaths",
            "Adam Dřínek",
            "Adam Margulies",
            "Aidan Shenkman",
            "Alan Stein",
            "Alex Mijalis",
            "Alexander Mai",
            "Alexis Olson",
            "Ali Yahya",
            "Andreas Snekloth Kongsgaard",
            "Andrew Busey",
            "Andrew Cary",
            "Andrew R. Whalley",
            "Anthony Losego",
            "Aravind C V",
            "Arjun Chakroborty",
            "Arthur Zey",
            "Ashwin Siddarth",
            "Augustine Lim",
            "Austin Goodman",
            "Avi Finkel",
            "Awoo",
            "Axel Ericsson",
            "Ayan Doss",
            "AZsorcerer",
            "Barry Fam",
            "Bartosz Burclaf",
            "Ben Delo",
            "Bernd Sing",
            "Bill Gatliff",
            "Bob Sanderson",
            "Boris Veselinovich",
            "Bradley Pirtle",
            "Brandon Huang",
            "Brendan Shah",
            "Brian Cloutier",
            "Brian Staroselsky",
            "Britt Selvitelle",
            "Britton Finley",
            "Burt Humburg",
            "Calvin Lin",
            "Charles Southerland",
            "Charlie N",
            "Chenna Kautilya",
            "Chris Connett",
            "Chris Druta",
            "Christian Kaiser",
            "cinterloper",
            "Clark Gaebel",
            "Colwyn Fritze-Moor",
            "Cooper Jones",
            "Corey Ogburn",
            "D. Sivakumar",
            "Dan Herbatschek",
            "Daniel Herrera C",
            "Darrell Thomas",
            "Dave B",
            "Dave Cole",
            "Dave Kester",
            "dave nicponski",
            "David B. Hill",
            "David Clark",
            "David Gow",
            "Delton Ding",
            "Eduardo Rodriguez",
            "Emilio Mendoza Palafox",
            "emptymachine",
            "Eric Younge",
            "Eryq Ouithaqueue",
            "Federico Lebron",
            "Fernando Via Canel",
            "Frank R. Brown, Jr.",
            "Giovanni Filippi",
            "Goodwine",
            "Hal Hildebrand",
            "Heptonion",
            "Hitoshi Yamauchi",
            "Ivan Sorokin",
            "Jacob Baxter",
            "Jacob Harmon",
            "Jacob Hartmann",
            "Jacob Magnuson",
            "Jalex Stark",
            "Jameel Syed",
            "James Beall",
            "Jason Hise",
            "Jayne Gabriele",
            "Jean-Manuel Izaret",
            "Jeff Dodds",
            "Jeff Linse",
            "Jeff Straathof",
            "Jeffrey Wolberg",
            "Jimmy Yang",
            "Joe Pregracke",
            "Johan Auster",
            "John C. Vesey",
            "John Camp",
            "John Haley",
            "John Le",
            "John Luttig",
            "John Rizzo",
            "John V Wertheim",
            "Jonathan Heckerman",
            "Jonathan Wilson",
            "Joseph John Cox",
            "Joseph Kelly",
            "Josh Kinnear",
            "Joshua Claeys",
            "Joshua Ouellette",
            "Juan Benet",
            "Julien Dubois",
            "Kai-Siang Ang",
            "Kanan Gill",
            "Karl Niu",
            "Kartik Cating-Subramanian",
            "Kaustuv DeBiswas",
            "Killian McGuinness",
            "kkm",
            "Klaas Moerman",
            "Kristoffer Börebäck",
            "Kros Dai",
            "L0j1k",
            "Lael S Costa",
            "LAI Oscar",
            "Lambda GPU Workstations",
            "Laura Gast",
            "Lee Redden",
            "Linh Tran",
            "Luc Ritchie",
            "Ludwig Schubert",
            "Lukas Biewald",
            "Lukas Zenick",
            "Magister Mugit",
            "Magnus Dahlström",
            "Magnus Hiie",
            "Manoj Rewatkar",
            "Mark B Bahu",
            "Mark Heising",
            "Mark Hopkins",
            "Mark Mann",
            "Martin Price",
            "Mathias Jansson",
            "Matt Godbolt",
            "Matt Langford",
            "Matt Roveto",
            "Matt Russell",
            "Matteo Delabre",
            "Matthew Bouchard",
            "Matthew Cocke",
            "Maxim Nitsche",
            "Michael Bos",
            "Michael Day",
            "Michael Hardel",
            "Michael W White",
            "Mihran Vardanyan",
            "Mirik Gogri",
            "Molly Mackinlay",
            "Mustafa Mahdi",
            "Márton Vaitkus",
            "Nate Heckmann",
            "Nero Li",
            "Nicholas Cahill",
            "Nikita Lesnikov",
            "Oleg Leonov",
            "Oliver Steele",
            "Omar Zrien",
            "Omer Tuchfeld",
            "Patrick Lucas",
            "Pavel Dubov",
            "Pesho Ivanov",
            "Petar Veličković",
            "Peter Ehrnstrom",
            "Peter Francis",
            "Peter Mcinerney",
            "Pierre Lancien",
            "Pradeep Gollakota",
            "Rafael Bove Barrios",
            "Raghavendra Kotikalapudi",
            "Randy C. Will",
            "rehmi post",
            "Rex Godby",
            "Ripta Pasay",
            "Rish Kundalia",
            "Roman Sergeychik",
            "Roobie",
            "Ryan Atallah",
            "Samuel Judge",
            "SansWord Huang",
            "Scott Gray",
            "Scott Walter, Ph.D.",
            "soekul",
            "Solara570",
            "Stephen Shanahan",
            "Steve Huynh",
            "Steve Muench",
            "Steve Sperandeo",
            "Steven Siddals",
            "Stevie Metke",
            "Sundar Subbarayan",
            "Sunil Nagaraj",
            "supershabam",
            "Suteerth Vishnu",
            "Suthen Thomas",
            "Tal Einav",
            "Taras Bobrovytsky",
            "Tauba Auerbach",
            "Ted Suzman",
            "Thomas J Sargent",
            "Thomas Tarler",
            "Tianyu Ge",
            "Tihan Seale",
            "Tim Erbes",
            "Tim Kazik",
            "Tomasz Legutko",
            "Tyler Herrmann",
            "Tyler Parcell",
            "Tyler VanValkenburg",
            "Tyler Veness",
            "Vassili Philippov",
            "Vasu Dubey",
            "Veritasium",
            "Vignesh Ganapathi Subramanian",
            "Vinicius Reis",
            "Vladimir Solomatin",
            "Wooyong Ee",
            "Xuanji Li",
            "Yana Chernobilsky",
            "Yavor Ivanov",
            "YinYangBalance.Asia",
            "Yu Jun",
            "Yurii Monastyrshyn",
        ],
    }
