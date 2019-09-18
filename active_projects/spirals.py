from manimlib.imports import *


OUTPUT_DIRECTORY = "spirals"


def generate_prime_list(*args):
    if len(args) == 1:
        start, stop = 2, args[0]
    elif len(args) == 2:
        start, stop = args
        start = max(start, 2)
    else:
        raise TypeError("generate_prime_list takes 1 or 2 arguments")

    result = []
    for n in range(start, stop):
        include = True
        for k in range(2, int(np.sqrt(n)) + 1):
            if n % k == 0:
                include = False
                break
        if include:
            result.append(n)
    return result


class SpiralScene(Scene):
    CONFIG = {
        "axes_config": {
            "number_line_config": {
                "stroke_width": 1.5,
            }
        }
    }

    def setup(self):
        self.axes = Axes(**self.axes_config)
        self.add(self.axes)

    def get_dots_in_spiral(self, sequence, axes=None, dot_radius=None):
        if axes is None:
            axes = self.axes
        if dot_radius is None:
            unit = get_norm(axes.c2p(1, 0) - axes.c2p(0, 0)),
            dot_radius = max(
                0.1 / (-np.log10(unit) + 1),
                0.01,
            )

        return VGroup(*[
            Dot(
                self.get_polar_point(n, n, axes),
                radius=dot_radius,
                fill_color=TEAL,
            )
            for n in sequence
        ])

    def get_polar_point(self, r, theta, axes):
        return axes.c2p(r * np.cos(theta), r * np.sin(theta))

    def set_scale(self, scale, exceptions=None, run_time=3):
        axes = self.axes
        if exceptions is None:
            exceptions = []

        unit = get_norm(axes.c2p(1, 0) - axes.c2p(0, 0))
        sf = unit / scale

        self.remove(*exceptions)
        self.play(*[
            ApplyMethod(
                mob.scale, sf,
                about_point=ORIGIN,
                run_time=run_time,
            )
            for mob in self.get_top_level_mobjects()
        ])


# Scenes


class RefresherOnPolarCoordinates(MovingCameraScene):
    CONFIG = {
        "x_color": GREEN,
        "y_color": RED,
        "r_color": YELLOW,
        "theta_color": LIGHT_PINK,
    }

    def construct(self):
        self.show_xy_coordinates()
        self.transition_to_polar_grid()
        self.show_polar_coordinates()

        self.show_all_nn_tuples()

    def show_xy_coordinates(self):
        plane = NumberPlane()
        plane.add_coordinates()

        x, y = 3, 2
        point = plane.c2p(x, y)
        xp = plane.c2p(x, 0)
        origin = plane.c2p(0, 0)

        x_color = self.x_color
        y_color = self.y_color

        x_line = Line(origin, xp, color=x_color)
        y_line = Line(xp, point, color=y_color)

        dot = Dot(point)

        coord_label = self.get_coord_label(x, y, x_color, y_color)
        x_coord = coord_label.x_coord
        y_coord = coord_label.y_coord

        coord_label.next_to(dot, UR, SMALL_BUFF)

        x_brace = Brace(x_coord, UP)
        y_brace = Brace(y_coord, UP)
        x_brace.add(x_brace.get_tex("x").set_color(x_color))
        y_brace.add(y_brace.get_tex("y").set_color(y_color))
        x_brace.add_updater(lambda m: m.next_to(x_coord, UP, SMALL_BUFF))
        y_brace.add_updater(lambda m: m.next_to(y_coord, UP, SMALL_BUFF))

        self.add(plane)
        self.add(dot, coord_label)
        self.add(x_brace, y_brace)

        coord_label.add_updater(
            lambda m: m.next_to(dot, UR, SMALL_BUFF)
        )

        self.play(
            ShowCreation(x_line),
            ChangeDecimalToValue(x_coord, x),
            UpdateFromFunc(
                dot,
                lambda d: d.move_to(x_line.get_end()),
            ),
            run_time=2,
        )
        self.play(
            ShowCreation(y_line),
            ChangeDecimalToValue(y_coord, y),
            UpdateFromFunc(
                dot,
                lambda d: d.move_to(y_line.get_end()),
            ),
            run_time=2,
        )
        self.wait()

        self.xy_coord_mobjects = VGroup(
            x_line, y_line, coord_label,
            x_brace, y_brace,
        )
        self.plane = plane
        self.dot = dot

    def transition_to_polar_grid(self):
        self.polar_grid = self.get_polar_grid()
        self.add(self.polar_grid, self.dot)
        self.play(
            FadeOut(self.xy_coord_mobjects),
            FadeOut(self.plane),
            ShowCreation(self.polar_grid, run_time=2),
        )
        self.wait()

    def show_polar_coordinates(self):
        dot = self.dot
        plane = self.plane
        origin = plane.c2p(0, 0)

        r_color = self.r_color
        theta_color = self.theta_color

        r_line = Line(origin, dot.get_center())
        r_line.set_color(r_color)
        r_value = r_line.get_length()
        theta_value = r_line.get_angle()

        coord_label = self.get_coord_label(r_value, theta_value, r_color, theta_color)
        r_coord = coord_label.x_coord
        theta_coord = coord_label.y_coord

        coord_label.add_updater(lambda m: m.next_to(dot, UP, buff=SMALL_BUFF))
        r_coord.add_updater(lambda d: d.set_value(
            get_norm(dot.get_center())
        ))
        theta_coord.add_background_rectangle()
        theta_coord.add_updater(lambda d: d.set_value(
            (angle_of_vector(dot.get_center()) % TAU)
        ))
        coord_label[-1].add_updater(
            lambda m: m.next_to(theta_coord, RIGHT, SMALL_BUFF)
        )

        non_coord_parts = VGroup(*[
            part
            for part in coord_label
            if part not in [r_coord, theta_coord]
        ])

        r_label = TexMobject("r")
        r_label.set_color(r_color)
        r_label.add_updater(lambda m: m.next_to(r_coord, UP))
        theta_label = TexMobject("\\theta")
        theta_label.set_color(theta_color)
        theta_label.add_updater(lambda m: m.next_to(theta_coord, UP))

        r_coord_copy = r_coord.copy()
        r_coord_copy.add_updater(
            lambda m: m.next_to(r_line.get_center(), UL, buff=0)
        )

        degree_label = DecimalNumber(0, num_decimal_places=1, unit="^\\circ")
        arc = Arc(radius=1, angle=theta_value)
        arc.set_color(theta_color)
        degree_label.set_color(theta_color)

        # Show r
        self.play(
            ShowCreation(r_line, run_time=2),
            ChangeDecimalToValue(r_coord_copy, r_value, run_time=2),
            VFadeIn(r_coord_copy, run_time=0.5),
        )
        r_coord.set_value(r_value)
        self.add(non_coord_parts, r_coord_copy)
        self.play(
            FadeIn(non_coord_parts),
            ReplacementTransform(r_coord_copy, r_coord),
            FadeInFromDown(r_label),
        )
        self.wait()

        # Show theta
        degree_label.next_to(arc.get_start(), UR, SMALL_BUFF)
        line = r_line.copy()
        line.rotate(-theta_value, about_point=ORIGIN)
        line.set_color(theta_color)
        self.play(
            ShowCreation(arc),
            Rotate(line, theta_value, about_point=ORIGIN),
            VFadeInThenOut(line),
            ChangeDecimalToValue(degree_label, theta_value / DEGREES),
        )
        self.play(
            degree_label.move_to, theta_coord,
            FadeInFromDown(theta_label),
        )
        self.wait()

        degree_cross = Cross(degree_label)
        radians_word = TextMobject("in radians")
        radians_word.scale(0.9)
        radians_word.set_color(theta_color)
        radians_word.add_background_rectangle()
        radians_word.add_updater(
            lambda m: m.next_to(theta_label, RIGHT, aligned_edge=DOWN)
        )

        self.play(ShowCreation(degree_cross))
        self.play(
            FadeOutAndShift(
                VGroup(degree_label, degree_cross),
                DOWN
            ),
            FadeIn(theta_coord)
        )
        self.play(FadeIn(radians_word))
        self.wait()

        # Move point around
        r_line.add_updater(
            lambda l: l.put_start_and_end_on(ORIGIN, dot.get_center())
        )
        arc.add_updater(
            lambda m: m.become(Arc(
                angle=(r_line.get_angle() % TAU),
                color=theta_color,
                radius=1,
            ))
        )

        self.add(coord_label)
        for angle in [PI - theta_value, PI - 0.001, -TAU + 0.002]:
            self.play(
                Rotate(dot, angle, about_point=ORIGIN),
                run_time=3,
            )
            self.wait()
        self.play(
            FadeOut(coord_label),
            FadeOut(r_line),
            FadeOut(arc),
            FadeOut(r_label),
            FadeOut(theta_label),
            FadeOut(radians_word),
            FadeOut(dot),
        )

    def show_all_nn_tuples(self):
        self.remove(self.dot)
        primes = generate_prime_list(20)
        non_primes = list(range(1, 20))
        for prime in primes:
            non_primes.remove(prime)

        pp_points = VGroup(*map(self.get_nn_point, primes))
        pp_points[0][1].shift(0.3 * LEFT + SMALL_BUFF * UP)
        np_points = VGroup(*map(self.get_nn_point, non_primes))
        pp_points.set_color(TEAL)
        np_points.set_color(WHITE)
        pp_points.set_stroke(BLACK, 4, background=True)
        np_points.set_stroke(BLACK, 4, background=True)

        frame = self.camera_frame
        self.play(
            ApplyMethod(frame.scale, 2),
            LaggedStartMap(
                FadeInFromDown, pp_points
            ),
            run_time=2
        )
        self.wait()
        self.play(LaggedStartMap(FadeIn, np_points))
        self.play(frame.scale, 0.5)
        self.wait()

        # Talk about 1
        one = np_points[0]
        r_line = Line(ORIGIN, one.dot.get_center())
        r_line.set_color(self.r_color)
        # pre_arc = Line(RIGHT, UR, color=self.r_color)
        theta_tracker = ValueTracker(1)
        arc = always_redraw(lambda: self.get_arc(theta_tracker.get_value()))

        one_rect = SurroundingRectangle(one)
        one_r_rect = SurroundingRectangle(one.label[1])
        one_theta_rect = SurroundingRectangle(one.label[3])
        one_theta_rect.set_color(self.theta_color)

        self.play(ShowCreation(one_rect))
        self.add(r_line, np_points, pp_points, one_rect)
        self.play(
            ReplacementTransform(one_rect, one_r_rect),
            ShowCreation(r_line)
        )
        self.wait()
        # self.play(TransformFromCopy(r_line, pre_arc))
        # self.add(pre_arc, one)
        self.play(
            TransformFromCopy(r_line, arc),
            ReplacementTransform(one_r_rect, one_theta_rect)
        )
        self.add(arc, one, one_theta_rect)
        self.play(FadeOut(one_theta_rect))
        self.wait()

        # Talk about 2
        self.play(theta_tracker.set_value, 2)
        self.wait()
        self.play(Rotate(r_line, angle=1, about_point=ORIGIN))
        self.play(r_line.scale, 2, {'about_point': ORIGIN})
        self.wait()

        # And now 3
        self.play(theta_tracker.set_value, 3)
        self.play(
            Transform(arc, self.get_arc(3)),
            Rotate(r_line, angle=1, about_point=ORIGIN),
        )
        self.wait()
        self.play(
            r_line.scale, 3 / 2, {"about_point": ORIGIN}
        )
        self.wait()

        # Zoom out and show spiral
        spiral = ParametricFunction(
            lambda t: self.get_polar_point(t, t),
            t_min=0,
            t_max=25,
            stroke_width=1.5,
        )

        self.add(spiral, pp_points, np_points)

        self.polar_grid.generate_target()
        for mob in self.polar_grid:
            if not isinstance(mob[0], Integer):
                mob.set_stroke(width=1)

        self.play(
            ApplyMethod(
                frame.scale, 3,
                run_time=5,
                rate_func=lambda t: smooth(t, 2)
            ),
            ShowCreation(
                spiral,
                run_time=6,
            ),
            FadeOut(r_line),
            FadeOut(arc),
            MoveToTarget(self.polar_grid)
        )
        self.wait()

    #
    def get_nn_point(self, n):
        point = self.get_polar_point(n, n)
        dot = Dot(point)
        coord_label = self.get_coord_label(
            n, n,
            include_background_rectangle=False,
            num_decimal_places=0
        )
        coord_label.next_to(dot, UR, buff=0)
        result = VGroup(dot, coord_label)
        result.dot = dot
        result.label = coord_label
        return result

    def get_polar_grid(self, radius=25):
        plane = self.plane
        axes = VGroup(
            Line(radius * DOWN, radius * UP),
            Line(radius * LEFT, radius * RIGHT),
        )
        axes.set_stroke(width=2)
        circles = VGroup(*[
            Circle(color=BLUE, stroke_width=1, radius=r)
            for r in range(1, int(radius))
        ])
        rays = VGroup(*[
            Line(
                ORIGIN, radius * RIGHT,
                color=BLUE,
                stroke_width=1,
            ).rotate(angle, about_point=ORIGIN)
            for angle in np.arange(0, TAU, TAU / 16)
        ])
        labels = VGroup(*[
            Integer(n).scale(0.5).next_to(
                plane.c2p(n, 0), DR, SMALL_BUFF
            )
            for n in range(1, int(radius))
        ])

        return VGroup(
            circles, rays, labels, axes,
        )

    def get_coord_label(self,
                        x=0,
                        y=0,
                        x_color=WHITE,
                        y_color=WHITE,
                        include_background_rectangle=True,
                        **decimal_kwargs):
        x_coord = DecimalNumber(x, **decimal_kwargs)
        y_coord = DecimalNumber(y, **decimal_kwargs)

        coord_label = VGroup(
            TexMobject("("), x_coord,
            TexMobject(","), y_coord,
            TexMobject(")")
        )
        coord_label.arrange(RIGHT, buff=SMALL_BUFF)
        coord_label[2].align_to(coord_label[0], DOWN)

        coord_label.x_coord = x_coord
        coord_label.y_coord = y_coord
        if include_background_rectangle:
            coord_label.add_background_rectangle()
        return coord_label

    def get_polar_point(self, r, theta):
        plane = self.plane
        return plane.c2p(r * np.cos(theta), r * np.sin(theta))

    def get_arc(self, theta, r=1, color=None):
        if color is None:
            color = self.theta_color
        return Arc(
            angle=theta,
            radius=r,
            stroke_color=color,
        )


class SpiralSceneTest(SpiralScene):
    def construct(self):
        N = 1 * 10**4
        axes = self.axes

        primes = generate_prime_list(N)
        prime_dots = self.get_dots_in_spiral(primes)

        scale_factor = TAU / N

        axes.generate_target(use_deepcopy=True)
        axes.target.scale(scale_factor, about_point=ORIGIN)
        prime_dots.target = self.get_dots_in_spiral(primes, axes.target)

        self.add(prime_dots)
        self.wait()
        self.set_scale(0.1)

        # self.add(ParametricFunction(
        #     lambda t: axes.c2p(t * np.cos(t), t * np.sin(t)),
        #     t_min=0,
        #     t_max=30,
        # ))

        return

        ap_dots = self.get_dots_in_spiral(range(0, N, 666))
        ap_dots.set_color(YELLOW)
        self.play(ShowIncreasingSubsets(ap_dots))
        self.wait()
