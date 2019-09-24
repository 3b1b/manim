from manimlib.imports import *
import json
import numbers


OUTPUT_DIRECTORY = "spirals"
INV_113_MOD_710 = 377  # Inverse of 113 mode 710
INV_7_MOD_44 = 19


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


def get_gcd(x, y):
    while y > 0:
        x, y = y, x % y
    return x


def read_in_primes(max_N=None):
    if max_N is None:
        max_N = int(1e7)

    if max_N < 1e5:
        file = "primes_1e5.json"
    elif max_N < 1e6:
        file = "primes_1e5.json"
    else:
        file = "primes_1e7.json"

    with open(os.path.join("assets", file)) as fp:
        primes = np.array(json.load(fp))
    return primes[primes <= max_N]


class SpiralScene(MovingCameraScene):
    CONFIG = {
        "axes_config": {
            "number_line_config": {
                "stroke_width": 1.5,
            }
        },
        "default_dot_color": TEAL,
        "p_spiral_width": 6,
    }

    def setup(self):
        super().setup()
        self.axes = Axes(**self.axes_config)
        self.add(self.axes)

    def get_v_spiral(self, sequence, axes=None, box_width=None):
        if axes is None:
            axes = self.axes
        if box_width is None:
            unit = get_norm(axes.c2p(1, 0) - axes.c2p(0, 0)),
            box_width = max(
                0.2 / (-np.log10(unit) + 1),
                0.02,
            )

        return VGroup(*[
            Square(
                side_length=box_width,
                fill_color=self.default_dot_color,
                fill_opacity=1,
                stroke_width=0,
            ).move_to(self.get_polar_point(n, n, axes))
            for n in sequence
        ])

    def get_p_spiral(self, sequence, axes=None):
        if axes is None:
            axes = self.axes
        result = PMobject(
            color=self.default_dot_color,
            stroke_width=self.p_spiral_width,
        )
        result.add_points([
            self.get_polar_point(n, n, axes)
            for n in sequence
        ])
        return result

    def get_prime_v_spiral(self, max_N, **kwargs):
        primes = read_in_primes(max_N)
        return self.get_v_spiral(primes, **kwargs)

    def get_prime_p_spiral(self, max_N, **kwargs):
        primes = read_in_primes(max_N)
        return self.get_p_spiral(primes, **kwargs)

    def get_polar_point(self, r, theta, axes=None):
        if axes is None:
            axes = self.axes
        return axes.c2p(r * np.cos(theta), r * np.sin(theta))

    def set_scale(self, scale,
                  axes=None,
                  spiral=None,
                  to_shrink=None,
                  min_box_width=0.05,
                  target_p_spiral_width=None,
                  run_time=3):
        if axes is None:
            axes = self.axes
        sf = self.get_scale_factor(scale, axes)

        anims = []
        for mob in [axes, spiral, to_shrink]:
            if mob is None:
                continue
            mob.generate_target()
            mob.target.scale(sf, about_point=ORIGIN)
            if mob is spiral:
                if isinstance(mob, VMobject):
                    old_width = mob[0].get_width()
                    for submob in mob.target:
                        submob.set_width(max(
                            old_width * sf,
                            min_box_width,
                        ))
                elif isinstance(mob, PMobject):
                    if target_p_spiral_width is not None:
                        mob.target.set_stroke_width(target_p_spiral_width)
            anims.append(MoveToTarget(mob))

        if run_time == 0:
            for anim in anims:
                anim.begin()
                anim.update(1)
                anim.finish()
        else:
            self.play(
                *anims,
                run_time=run_time,
                rate_func=lambda t: interpolate(
                    smooth(t),
                    smooth(t)**(sf**(0.5)),
                    t,
                )
            )

    def get_scale_factor(self, target_scale, axes=None):
        if axes is None:
            axes = self.axes
        unit = get_norm(axes.c2p(1, 0) - axes.c2p(0, 0))
        return 1 / (target_scale * unit)

    def get_labels(self, sequence, scale_func=np.sqrt):
        labels = VGroup()
        for n in sequence:
            label = Integer(n)
            label.set_stroke(width=0, background=True)
            label.scale(scale_func(n))
            label.next_to(
                self.get_polar_point(n, n), UP,
                buff=0.5 * label.get_height(),
            )
            labels.add(label)
        return labels

    def get_prime_labels(self, max_N):
        primes = read_in_primes(max_N)
        return self.get_labels(primes)


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

        x = 3 * np.cos(PI / 6)
        y = 3 * np.sin(PI / 6)

        point = plane.c2p(x, y)
        xp = plane.c2p(x, 0)
        origin = plane.c2p(0, 0)

        x_color = self.x_color
        y_color = self.y_color

        x_line = Line(origin, xp, color=x_color)
        y_line = Line(xp, point, color=y_color)

        dot = Dot(point)

        coord_label = self.get_coord_label(0, 0, x_color, y_color)
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
            degree_label.scale, 0.9,
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
        self.play(
            theta_tracker.set_value, 3,
            Rotate(r_line, angle=1, about_point=ORIGIN),
        )
        self.wait()
        self.play(
            r_line.scale, 3 / 2, {"about_point": ORIGIN}
        )
        self.wait()

        # Finally 4
        self.play(
            theta_tracker.set_value, 4,
            Rotate(r_line, angle=1, about_point=ORIGIN),
        )
        self.wait()
        self.play(
            r_line.scale, 4 / 3, {"about_point": ORIGIN}
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
        coords = VGroup()
        for n in x, y:
            if isinstance(n, numbers.Number):
                coord = DecimalNumber(n, **decimal_kwargs)
            elif isinstance(n, str):
                coord = TexMobject(n)
            else:
                raise Exception("Invalid type")
            coords.add(coord)

        x_coord, y_coord = coords
        x_coord.set_color(x_color)
        y_coord.set_color(y_color)

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


class ReplacePolarCoordinatesWithPrimes(RefresherOnPolarCoordinates):
    def construct(self):
        coords, p_coords = [
            self.get_coord_label(
                *pair,
                x_color=self.r_color,
                y_color=self.theta_color,
            ).scale(2)
            for pair in [("r", "\\theta"), ("p", "p")]
        ]
        p_coords.x_coord.set_color(LIGHT_GREY)
        p_coords.y_coord.set_color(LIGHT_GREY)

        some_prime = TextMobject("Some prime")
        some_prime.scale(1.5)
        some_prime.next_to(p_coords, UP, buff=1.5)
        arrows = VGroup(*[
            Arrow(
                some_prime.get_bottom(), coord.get_top(),
                stroke_width=5,
                tip_length=0.4
            )
            for coord in [p_coords.x_coord, p_coords.y_coord]
        ])

        equals = TexMobject("=")
        equals.next_to(p_coords, LEFT)

        self.add(coords)
        self.wait()
        self.play(
            coords.next_to, equals, LEFT,
            FadeIn(equals),
            FadeIn(p_coords),
        )
        self.play(
            FadeInFromDown(some_prime),
            ShowCreation(arrows),
        )
        self.wait()


class IntroducePrimePatterns(SpiralScene):
    CONFIG = {
        "small_n_primes": 25000,
        "big_n_primes": 1000000,
        "axes_config": {
            "x_min": -25,
            "x_max": 25,
            "y_min": -25,
            "y_max": 25,
        },
        "spiral_scale": 3e3,
        "ray_scale": 1e5,
    }

    def construct(self):
        self.slowly_zoom_out()
        self.show_clumps_of_four()

    def slowly_zoom_out(self):
        zoom_time = 8

        prime_spiral = self.get_prime_p_spiral(self.small_n_primes)
        prime_spiral.set_stroke_width(25)
        self.add(prime_spiral)

        self.set_scale(3, spiral=prime_spiral)
        self.wait()
        self.set_scale(
            self.spiral_scale,
            spiral=prime_spiral,
            target_p_spiral_width=8,
            run_time=zoom_time,
        )
        self.wait()

        self.remove(prime_spiral)
        prime_spiral = self.get_prime_p_spiral(self.big_n_primes)
        prime_spiral.set_stroke_width(8)
        self.set_scale(
            self.ray_scale,
            spiral=prime_spiral,
            target_p_spiral_width=4,
            run_time=zoom_time,
        )
        self.wait()

    def show_clumps_of_four(self):
        line_groups = VGroup()
        for n in range(71):
            group = VGroup()
            for k in [-3, -1, 1, 3]:
                r = ((10 * n + k) * INV_113_MOD_710) % 710
                group.add(self.get_arithmetic_sequence_line(
                    710, r, self.big_n_primes
                ))
            line_groups.add(group)

        line_groups.set_stroke(YELLOW, 2, opacity=0.5)

        self.play(ShowCreation(line_groups[0]))
        for g1, g2 in zip(line_groups, line_groups[1:5]):
            self.play(
                FadeOut(g1),
                ShowCreation(g2)
            )

        self.play(
            FadeOut(line_groups[4]),
            LaggedStartMap(
                VFadeInThenOut,
                line_groups[4:],
                lag_ratio=0.5,
                run_time=5,
            )
        )
        self.wait()

    def get_arithmetic_sequence_line(self, N, r, max_val, skip_factor=5):
        line = VMobject()
        line.set_points_smoothly([
            self.get_polar_point(x, x)
            for x in range(r, max_val, skip_factor * N)
        ])
        return line


class AskWhat(TeacherStudentsScene):
    def construct(self):
        screen = self.screen
        self.student_says(
            "I'm sory,\\\\what?!?",
            target_mode="angry",
            look_at_arg=screen,
            student_index=2,
            added_anims=[
                self.teacher.change, "happy", screen,
                self.students[0].change, "confused", screen,
                self.students[1].change, "confused", screen,
            ]
        )
        self.wait(3)


class CountSpirals(IntroducePrimePatterns):
    CONFIG = {
        "count_sound": "pen_click.wav",
    }

    def construct(self):
        prime_spiral = self.get_prime_p_spiral(self.small_n_primes)

        self.add(prime_spiral)
        self.set_scale(
            self.spiral_scale,
            spiral=prime_spiral,
            run_time=0,
        )

        spiral_lines = self.get_all_primative_arithmetic_lines(
            44, self.small_n_primes, INV_7_MOD_44,
        )
        spiral_lines.set_stroke(YELLOW, 2, opacity=0.5)

        counts = VGroup()
        for n, spiral in zip(it.count(1), spiral_lines):
            count = Integer(n)
            count.move_to(spiral.point_from_proportion(0.25))
            counts.add(count)

        run_time = 3
        self.play(
            ShowIncreasingSubsets(spiral_lines),
            ShowSubmobjectsOneByOne(counts),
            run_time=run_time,
            rate_func=linear,
        )
        self.add_count_clicks(len(spiral_lines), run_time)
        self.play(
            counts[-1].scale, 3,
            counts[-1].set_stroke, BLACK, 5, {"background": True},
        )
        self.wait()

    def get_all_primative_arithmetic_lines(self, N, max_val, mult_factor):
        lines = VGroup()
        for r in range(1, N):
            if get_gcd(N, r) == 1:
                lines.add(
                    self.get_arithmetic_sequence_line(N, (mult_factor * r) % N, max_val)
                )
        return lines

    def add_count_clicks(self, N, time, rate_func=linear):
        alphas = np.arange(0, 1, 1 / N)
        if rate_func is linear:
            delays = time * alphas
        else:
            delays = time * np.array([
                binary_search(rate_func, alpha, 0, 1)
                for alpha in alphas
            ])

        for delay in delays:
            self.add_sound(
                self.count_sound,
                time_offset=-delay,
                gain=-15,
            )


class CountRays(CountSpirals):
    def construct(self):
        prime_spiral = self.get_prime_p_spiral(self.big_n_primes)

        self.add(prime_spiral)
        self.set_scale(
            self.ray_scale,
            spiral=prime_spiral,
            run_time=0,
        )

        spiral_lines = self.get_all_primative_arithmetic_lines(
            710, self.big_n_primes, INV_113_MOD_710,
        )
        spiral_lines.set_stroke(YELLOW, 2, opacity=0.5)

        counts = VGroup()
        for n, spiral in zip(it.count(1), spiral_lines):
            count = Integer(n)
            count.move_to(spiral.point_from_proportion(0.25))
            counts.add(count)

        run_time = 6
        self.play(
            ShowIncreasingSubsets(spiral_lines),
            ShowSubmobjectsOneByOne(counts),
            run_time=run_time,
            rate_func=smooth,
        )
        self.add_count_clicks(len(spiral_lines), run_time, rate_func=smooth)
        self.play(
            counts[-1].scale, 3,
            counts[-1].set_stroke, BLACK, 5, {"background": True},
        )
        self.wait()
        self.play(FadeOut(spiral_lines))
        self.wait()


class AskAboutRelationToPrimes(TeacherStudentsScene):
    def construct(self):
        numbers = TextMobject("20, 280")
        arrow = Arrow(LEFT, RIGHT)
        primes = TextMobject("2, 3, 5, 7, 11, \\dots")
        q_marks = TextMobject("???")
        q_marks.set_color(YELLOW)

        group = VGroup(numbers, arrow, primes)
        group.arrange(RIGHT)
        q_marks.next_to(arrow, UP)
        group.add(q_marks)
        group.scale(1.5)
        group.next_to(self.pi_creatures, UP, LARGE_BUFF)

        self.play(
            self.get_student_changes(
                *3 * ["maybe"],
                look_at_arg=numbers,
            ),
            self.teacher.change, "maybe", numbers,
            ShowCreation(arrow),
            FadeInFrom(numbers, RIGHT)
        )
        self.play(
            FadeInFrom(primes, LEFT),
        )
        self.play(
            LaggedStartMap(FadeInFromDown, q_marks[0]),
            Blink(self.teacher)
        )
        self.wait(3)


class ZoomOutOnPrimesWithNumbers(IntroducePrimePatterns):
    CONFIG = {
        "n_labeled_primes": 1000,
        "big_n_primes": int(5e6),
        "thicknesses": [8, 3, 2],
        "thicker_target": False,
    }

    def construct(self):
        zoom_time = 20

        prime_spiral = self.get_prime_p_spiral(self.big_n_primes)
        prime_spiral.set_stroke_width(25)

        prime_labels = self.get_prime_labels(self.n_labeled_primes)

        self.add(prime_spiral)
        self.add(prime_labels)

        scales = [self.spiral_scale, self.ray_scale, 5e5]
        thicknesses = self.thicknesses

        for scale, tp in zip(scales, thicknesses):
            kwargs = {
                "spiral": prime_spiral,
                "to_shrink": prime_labels,
                "run_time": zoom_time,
                "target_p_spiral_width": tp,
            }
            if self.thicker_target:
                kwargs["target_p_spiral_width"] += 1
            self.set_scale(scale, **kwargs)
            prime_spiral.set_stroke_width(tp)
            self.wait()
            self.remove(prime_labels)


class ThickZoomOutOnPrimesWithNumbers(ZoomOutOnPrimesWithNumbers):
    CONFIG = {
        # The only purpose of this scene is for overlay
        # with the last one to smooth things out.
        "thicker_target": True,
    }


class ShowSpiralsForWholeNumbers(CountSpirals):
    CONFIG = {
        "max_prime": 10000,
        "scale_44": 1e3,
        "scale_6": 10,
        "n_labels": 100,
        "axes_config": {
            "x_min": -50,
            "x_max": 50,
            "y_min": -50,
            "y_max": 50,
        },
    }

    def construct(self):
        self.zoom_out_with_whole_numbers()
        self.count_44_spirals()
        self.zoom_back_in_to_6()

    def zoom_out_with_whole_numbers(self):
        wholes = self.get_p_spiral(range(self.max_prime))
        primes = self.get_prime_p_spiral(self.max_prime)

        wholes.set_color(YELLOW)
        wholes.set_stroke_width(20)
        primes.set_stroke_width(20)
        spiral = PGroup(wholes, primes)

        labels = self.get_labels(range(1, self.n_labels))

        self.add(spiral, labels)
        self.set_scale(
            self.scale_44,
            spiral=spiral,
            to_shrink=labels,
            target_p_spiral_width=6,
            run_time=10,
        )
        self.wait(2)

        self.spiral = spiral
        self.labels = labels

    def count_44_spirals(self):
        curr_spiral = self.spiral

        new_spirals = PGroup(*[
            self.get_p_spiral(range(
                (INV_7_MOD_44 * k) % 44, self.max_prime, 44
            ))
            for k in range(44)
        ])
        new_spirals.set_color(YELLOW)

        counts = VGroup()
        for n, spiral in zip(it.count(1), new_spirals):
            count = Integer(n)
            count.scale(2)
            count.move_to(spiral.points[50])
            counts.add(count)

        self.remove(curr_spiral)
        run_time = 3
        self.play(
            ShowIncreasingSubsets(new_spirals),
            ShowSubmobjectsOneByOne(counts),
            run_time=run_time,
            rate_func=linear,
        )
        self.add_count_clicks(44, run_time)
        self.play(
            counts[-1].scale, 2, {"about_edge": DL},
            counts[-1].set_stroke, BLACK, 5, {"background": True},
        )
        self.wait()
        self.play(
            FadeOut(counts[-1]),
            FadeOut(new_spirals),
            FadeIn(curr_spiral),
        )

    def zoom_back_in_to_6(self):
        spiral = self.spiral

        self.rescale_labels(self.labels)
        self.set_scale(
            self.scale_6,
            spiral=spiral,
            to_shrink=self.labels,
            target_p_spiral_width=15,
            run_time=6,
        )
        self.wait()

    def rescale_labels(self, labels):
        for i, label in zip(it.count(1), labels):
            height = label.get_height()
            label.set_height(
                3 * height / (i**0.25),
                about_point=label.get_bottom() + 0.5 * label.get_height() * DOWN,
            )


class ExplainSixSpirals(ShowSpiralsForWholeNumbers):
    CONFIG = {
        "max_N": 150,
    }

    def construct(self):
        self.add_spirals_and_labels()
        self.comment_on_arms()
        self.talk_though_multiples_of_six()
        self.limit_to_primes()

    def add_spirals_and_labels(self):
        max_N = self.max_N

        spiral = self.get_v_spiral(range(max_N))
        primes = generate_prime_list(max_N)
        spiral.set_color(YELLOW)
        for n, box in enumerate(spiral):
            if n in primes:
                box.set_color(TEAL)

        labels = self.get_labels(range(max_N))

        self.add(spiral, labels)
        self.set_scale(
            spiral=spiral,
            scale=self.scale_6,
            to_shrink=labels,
            min_box_width=0.08,
            run_time=0,
        )
        self.rescale_labels(labels)

        self.spiral = spiral
        self.labels = labels

    def comment_on_arms(self):
        labels = self.labels
        spiral = self.spiral

        label_groups = VGroup(*[labels[k::6] for k in range(6)])
        spiral_groups = VGroup(*[spiral[k::6] for k in range(6)])
        six_groups = VGroup(*[
            VGroup(sg, lg)
            for sg, lg in zip(spiral_groups, label_groups)
        ])
        rect_groups = VGroup(*[
            VGroup(*[
                SurroundingRectangle(label, stroke_width=2, buff=0.05)
                for label in group
            ])
            for group in label_groups
        ])

        formula = VGroup(
            *TexMobject("6k", "+"),
            Integer(1)
        )
        formula.arrange(RIGHT, buff=SMALL_BUFF)
        formula.scale(2)
        formula.set_color(YELLOW)
        formula.to_corner(UL)
        formula_rect = SurroundingRectangle(formula, buff=MED_LARGE_BUFF - SMALL_BUFF)
        formula_rect.set_fill(DARK_GREY, opacity=1)
        formula_rect.set_stroke(WHITE, 1)

        # 6k
        self.add(six_groups, formula_rect)
        self.play(
            LaggedStartMap(ShowCreation, rect_groups[0]),
            FadeInFromDown(formula_rect),
            FadeInFromDown(formula[0]),
            *[
                ApplyMethod(group.set_opacity, 0.25)
                for group in six_groups[1:]
            ],
            run_time=2
        )
        self.play(
            LaggedStartMap(
                FadeOut, rect_groups[0],
                run_time=1,
            ),
        )
        self.wait()

        # 6k + 1
        self.play(
            six_groups[0].set_opacity, 0.25,
            six_groups[1].set_opacity, 1,
            FadeIn(formula[1:]),
        )
        self.wait(2)

        # 6k + m
        for m in [2, 3, 4, 5]:
            self.play(
                six_groups[m - 1].set_opacity, 0.25,
                six_groups[m].set_opacity, 1,
                ChangeDecimalToValue(formula[2], m),
            )
            self.wait()
        self.play(
            six_groups[5].set_opacity, 0.25,
            six_groups[0].set_opacity, 1,
            formula[1:].set_opacity, 0,
        )
        self.wait()

        self.six_groups = six_groups
        self.formula = VGroup(formula_rect, *formula)

    def talk_though_multiples_of_six(self):
        spiral = self.spiral
        labels = self.labels
        formula = self.formula

        # Zoom in
        self.add(spiral, labels, formula)
        self.set_scale(
            4.5,
            spiral=spiral,
            to_shrink=labels,
            run_time=2,
        )
        self.wait()

        boxes = VGroup(*[
            VGroup(b.copy(), l.copy())
            for b, l in zip(spiral, labels)
        ])
        boxes.set_opacity(1)

        lines = VGroup(*[
            Line(ORIGIN, box[0].get_center())
            for box in boxes
        ])
        lines.set_stroke(LIGHT_GREY, width=2)

        arcs = self.get_arcs(range(31))

        trash = VGroup()

        def show_steps(start, stop, added_anims=None, run_time=2):
            if added_anims is None:
                added_anims = []
            self.play(
                *[
                    ShowSubmobjectsOneByOne(group[start:stop + 1])
                    for group in [arcs, boxes, lines]
                ],
                *added_anims,
                rate_func=linear,
                run_time=run_time,
            )
            self.add_count_clicks(N=6, time=run_time)
            trash.add(VGroup(arcs[stop], boxes[stop], lines[stop]))

        # Writing next to the 6
        six = boxes[6][1]
        rhs = TexMobject(
            "\\text{radians}",
            "\\approx",
            "2\\pi",
            "\\text{ radians}"
        )
        rhs.next_to(six, RIGHT, 2 * SMALL_BUFF, aligned_edge=DOWN)
        rhs.add_background_rectangle()
        tau_value = TexMobject("{:.8}\\dots".format(TAU))
        tau_value.next_to(rhs[3], UP, aligned_edge=LEFT)

        # Animations
        show_steps(0, 6, run_time=3)
        self.wait()
        self.play(FadeIn(rhs))
        self.wait()
        self.play(FadeInFromDown(tau_value))
        self.wait(2)

        show_steps(6, 12)
        self.wait()

        show_steps(12, 18)
        self.wait()

        # Zoom out
        frame = self.camera_frame
        frame.add(formula)
        show_steps(18, 24, added_anims=[frame.scale, 2.5])
        self.wait()
        show_steps(24, 30)
        self.wait(2)

        self.play(
            FadeOut(trash),
            FadeOut(rhs),
            FadeOut(tau_value),
            spiral.set_opacity, 1,
            labels.set_opacity, 1,
            formula[1].set_opacity, 0,
        )

    def limit_to_primes(self):
        formula = self.formula
        formula_rect, six_k, plus, m_sym = formula
        spiral = self.spiral
        labels = self.labels
        six_groups = self.six_groups
        frame = self.camera_frame

        boxes = VGroup(*[
            VGroup(b, l)
            for b, l in zip(spiral, labels)
        ])
        prime_numbers = read_in_primes(self.max_N)
        primes = VGroup()
        non_primes = VGroup()
        for n, box in enumerate(boxes):
            if n in prime_numbers:
                primes.add(box)
            else:
                non_primes.add(box)

        prime_label = TextMobject("Primes")
        prime_label.set_color(TEAL)
        prime_label.match_width(VGroup(six_k, m_sym))
        prime_label.move_to(six_k, LEFT)

        # Show just primes
        self.add(primes, non_primes, formula)
        self.play(
            FadeIn(prime_label),
            non_primes.set_opacity, 0.25,
        )
        frame.add(prime_label)
        self.play(
            frame.scale, 1.5,
            run_time=2,
        )
        self.wait(2)

        cross_groups = VGroup()
        for group in six_groups:
            group.save_state()
            boxes, labels = group
            cross_group = VGroup()
            for label in labels:
                cross_group.add(Cross(label))
            cross_groups.add(cross_group)
        cross_groups.set_stroke(width=3)
        cross_groups[2].remove(cross_groups[2][0])
        cross_groups[3].remove(cross_groups[3][0])

        # Show multiples of 6
        for r in [0, 2, 4, 3]:
            arm = six_groups[r]
            crosses = cross_groups[r]
            self.add(arm, frame)

            anims = [arm.set_opacity, 1]
            if r == 0:
                anims += [
                    prime_label.set_opacity, 0,
                    six_k.set_opacity, 1
                ]
            elif r == 2:
                m_sym.set_value(2)
                anims += [
                    plus.set_opacity, 1,
                    m_sym.set_opacity, 1,
                ]
            else:
                anims.append(ChangeDecimalToValue(m_sym, r))
            self.play(*anims)
            self.add(*crosses, frame)
            self.play(
                LaggedStartMap(ShowCreation, crosses),
            )
            self.wait()

        # Fade forbidden groups
        to_fade = VGroup(*[
            VGroup(six_groups[r], cross_groups[r])
            for r in (0, 2, 3, 4)
        ])
        self.add(to_fade, frame)
        self.play(
            to_fade.set_opacity, 0.25,
            VGroup(six_k, plus, m_sym).set_opacity, 0,
            prime_label.set_opacity, 1,
        )
        self.wait()

    #
    def arc_func(self, t):
        r = 0.25 + 0.02 * t
        return r * np.array([np.cos(t), np.sin(t), 0])

    def get_arc(self, n):
        if n == 0:
            return VectorizedPoint()
        return ParametricFunction(
            self.arc_func,
            t_min=0,
            t_max=n,
            step_size=0.1,
            stroke_width=2,
            stroke_color=PINK,
        )

    def get_arcs(self, sequence):
        return VGroup(*map(self.get_arc, sequence))


class IntroduceResidueClassTerminology(Scene):
    def construct(self):
        self.add_title()
        self.add_sequences()
        self.add_terms()
        self.highlight_example()
        self.simple_english()

    def add_title(self):
        title = TextMobject("Overly-fancy terminology")
        title.scale(1.5)
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        underline = Line().match_width(title)
        underline.next_to(title, DOWN, SMALL_BUFF)
        title.add(underline)
        self.add(title)

        self.title = title
        self.underline = underline

    def add_sequences(self):
        sequences = VGroup()
        n_terms = 7

        for r in range(6):
            sequence = VGroup(*[
                Integer(6 * k + r)
                for k in range(n_terms)
            ])
            sequence.arrange(RIGHT, buff=0.4)
            sequences.add(sequence)

        sequences.arrange(DOWN, buff=0.7, aligned_edge=LEFT)
        for sequence in sequences:
            for s1, s2 in zip(sequence[:n_terms], sequences[-1]):
                s1.align_to(s2, RIGHT)
            commas = VGroup()
            for num in sequence[:-1]:
                comma = TextMobject(",")
                comma.next_to(num.get_corner(DR), RIGHT, SMALL_BUFF)
                commas.add(comma)
            dots = TexMobject("\\dots")
            dots.next_to(sequence.get_corner(DR), RIGHT, SMALL_BUFF)
            sequence.numbers = VGroup(*sequence)
            sequence.commas = commas
            sequence.dots = dots

            sequence.add(*commas)
            sequence.add(dots)
            sequence.sort(lambda p: p[0])

        labels = VGroup(*[
            TexMobject("6k + {}:".format(r))
            for r in range(6)
        ])
        labels.set_color(YELLOW)
        for label, sequence in zip(labels, sequences):
            label.next_to(sequence, LEFT, MED_LARGE_BUFF)

        group = VGroup(sequences, labels)
        group.to_edge(LEFT).to_edge(DOWN, buff=MED_LARGE_BUFF)

        self.add(labels)
        self.play(LaggedStart(*[
            LaggedStartMap(
                FadeInFrom, sequence,
                lambda m: (m, LEFT),
            )
            for sequence in sequences
        ], lag_ratio=0.3))
        self.wait()

        self.sequences = sequences
        self.sequence_labels = labels

    def add_terms(self):
        sequences = self.sequences

        terms = TextMobject(
            "``", "Residue\\\\",
            "classes\\\\",
            "mod ", "6''"
        )
        terms.scale(1.5)
        terms.set_color(YELLOW)
        terms.to_edge(RIGHT)

        res_brace = Brace(terms.get_part_by_tex("Residue"), UP)
        remainder = TextMobject("Remainder")
        remainder.next_to(res_brace, UP, SMALL_BUFF)

        mod_brace = Brace(terms.get_part_by_tex("mod"), DOWN)
        mod_def = TextMobject(
            "``where the thing\\\\you divide by is''"
        )
        mod_def.next_to(mod_brace, DOWN, SMALL_BUFF)

        arrows = VGroup(*[
            Arrow(terms.get_left(), sequence.get_right())
            for sequence in sequences
        ])
        arrows.set_color(YELLOW)

        self.play(
            FadeIn(terms),
            LaggedStartMap(ShowCreation, arrows),
        )
        self.wait()
        self.play(
            GrowFromCenter(res_brace),
            FadeInFromDown(remainder),
        )
        self.wait()
        self.play(GrowFromCenter(mod_brace))
        self.play(Write(mod_def))
        self.wait()

        self.terminology = VGroup(
            terms,
            res_brace, remainder,
            mod_brace, mod_def,
            arrows
        )

    def highlight_example(self):
        sequences = self.sequences
        labels = self.sequence_labels

        r = 2
        k = 2
        sequence = sequences[r]
        label = labels[r]
        r_tex = label[0][3]
        n_rects = VGroup(*[
            SurroundingRectangle(num)
            for num in sequence.numbers
        ])
        r_rect = SurroundingRectangle(r_tex)
        n_rects.set_color(RED)
        r_rect.set_color(RED)

        n_rect = n_rects.submobjects.pop(k)

        self.play(ShowCreation(n_rect))
        self.wait()
        self.play(
            TransformFromCopy(n_rect, r_rect, path_arc=30 * DEGREES)
        )
        self.wait()
        self.play(ShowCreation(n_rects))
        self.wait()
        self.play(
            ShowCreationThenFadeOut(
                self.underline.copy().set_color(PINK),
            )
        )

    def simple_english(self):
        terminology = self.terminology
        sequences = self.sequences

        randy = Randolph()
        randy.set_height(2)
        randy.flip()
        randy.to_corner(DR)

        new_phrase = TextMobject("Everything 2 above\\\\a multiple of 6")
        new_phrase.scale(1.2)
        new_phrase.set_color(RED_B)
        new_phrase.next_to(sequences[2])

        self.play(
            FadeOut(terminology),
            FadeIn(new_phrase),
            VFadeIn(randy),
            randy.change, "sassy"
        )
        self.wait()
        self.play(randy.change, "angry")
        for x in range(2):
            self.play(Blink(randy))
            self.wait()
        self.play(
            FadeOut(new_phrase),
            FadeIn(terminology),
            FadeOutAndShift(randy, DOWN)
        )
        self.wait()


class Explain44Spirals(ExplainSixSpirals):
    CONFIG = {
        "max_N": 3000,
        "initial_scale": 10,
        "zoom_factor_1": 7,
        "zoom_factor_2": 3,
    }

    def construct(self):
        self.add_spirals_and_labels()
        self.show_44_steps()
        self.show_top_right_arithmetic()
        self.show_pi_approx_arithmetic()
        self.count_by_44()

    def add_spirals_and_labels(self):
        max_N = self.max_N

        wholes = self.get_p_spiral(range(max_N))
        primes = self.get_prime_p_spiral(max_N)
        wholes.set_color(YELLOW)
        spiral = PGroup(wholes, primes)

        labels = self.get_labels(range(80))

        self.add(spiral, labels)
        self.set_scale(
            spiral=spiral,
            scale=self.initial_scale,
            to_shrink=labels,
            target_p_spiral_width=10,
            run_time=0,
        )
        self.rescale_labels(labels)

        self.spiral = spiral
        self.labels = labels

    def show_44_steps(self):
        labels = self.labels

        ns = range(45)
        points = [self.get_polar_point(n, n) for n in ns]
        lines = VGroup(*[
            Line(ORIGIN, point)
            for point in points
        ])
        lines.set_stroke(WHITE, 2)
        arcs = self.get_arcs(ns)

        opaque_labels = labels.copy()
        labels.set_opacity(0.25)

        trash = VGroup()

        def show_steps(start, stop, added_anims=None, run_time=2):
            if added_anims is None:
                added_anims = []

            def rate_func(t):
                return smooth(t, 2)

            self.play(
                *[
                    ShowSubmobjectsOneByOne(group[start:stop + 1])
                    for group in [arcs, opaque_labels, lines]
                ],
                *added_anims,
                rate_func=rate_func,
                run_time=run_time,
            )
            self.add_count_clicks(
                N=(stop - start), time=run_time,
                rate_func=rate_func
            )
            trash.add(arcs[stop], opaque_labels[stop], lines[stop])

        show_steps(0, 6)
        self.wait()
        show_steps(6, 44, added_anims=[FadeOut(trash)], run_time=4)
        self.wait()

        self.spiral_group = trash[-3:]

    def show_top_right_arithmetic(self):
        labels = self.labels
        ff = labels[44].copy()
        ff.generate_target()

        radians = TextMobject("radians")
        ff.target.scale(1.5)
        ff.target.set_opacity(1)

        unit_conversion = TexMobject(
            "/\\,", "\\left(", "2\\pi",
            "{\\text{radians}", "\\over", "\\text{rotations}}",
            "\\right)"
        )
        unit_conversion[1:].scale(0.7, about_edge=LEFT)

        top_line = VGroup(ff.target, radians, unit_conversion)
        top_line.arrange(RIGHT)
        ff.target.align_to(radians, DOWN)
        top_line.to_corner(UR, buff=0.4)

        next_line = TexMobject(
            "=", "44", "/", "2\\pi",
            "\\text{ rotations}"
        )
        next_line.next_to(top_line, DOWN, MED_LARGE_BUFF, aligned_edge=LEFT)

        brace = Brace(next_line[1:4], DOWN, buff=SMALL_BUFF)
        value = DecimalNumber(44 / TAU, num_decimal_places=8, show_ellipsis=True)
        value.next_to(brace, DOWN)

        rect = SurroundingRectangle(VGroup(top_line, value), buff=MED_SMALL_BUFF)
        rect.set_stroke(WHITE, 2)
        rect.set_fill(DARKER_GREY, 0.9)

        self.play(MoveToTarget(ff))
        top_line.add(ff)
        self.play(FadeInFrom(radians, LEFT))
        self.wait()
        self.add(rect, top_line, unit_conversion)
        self.play(
            FadeIn(rect),
            FadeIn(unit_conversion),
        )
        self.wait()
        self.play(
            TransformFromCopy(ff, next_line.get_part_by_tex("44")),
            FadeIn(next_line.get_part_by_tex("=")),
            TransformFromCopy(
                unit_conversion.get_part_by_tex("/"),
                next_line.get_part_by_tex("/"),
            ),
            TransformFromCopy(
                unit_conversion.get_part_by_tex("rotations"),
                next_line.get_part_by_tex("rotations"),
            ),
            TransformFromCopy(
                unit_conversion.get_part_by_tex("2\\pi"),
                next_line.get_part_by_tex("2\\pi"),
            ),
        )
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(value),
        )
        self.wait()

        self.right_arithmetic = VGroup(
            rect, top_line, next_line,
            brace, value
        )

    def show_pi_approx_arithmetic(self):
        ra = self.right_arithmetic
        ra_rect, ra_l1, ra_l2, ra_brace, ra_value = ra

        lines = VGroup(
            TexMobject("{44", "\\over", "2\\pi}", "\\approx", "7"),
            TexMobject("\\Leftrightarrow"),
            TexMobject("{44", "\\over", "7}", "\\approx", "2\\pi"),
            TexMobject("{22", "\\over", "7}", "\\approx", "\\pi"),
        )
        lines.arrange(RIGHT, buff=MED_SMALL_BUFF)
        lines.to_corner(UL)
        lines[3].move_to(lines[2], LEFT)

        rect = SurroundingRectangle(lines, buff=MED_LARGE_BUFF)
        rect.match_style(ra_rect)

        self.play(
            FadeIn(rect),
            LaggedStart(
                TransformFromCopy(ra_l2[1:4], lines[0][:3]),
                FadeIn(lines[0].get_part_by_tex("approx")),
                TransformFromCopy(ra_value[0], lines[0].get_part_by_tex("7")),
                run_time=2,
            )
        )
        self.wait()
        l0_copy = lines[0].copy()
        self.play(
            l0_copy.move_to, lines[2],
            Write(lines[1]),
        )
        self.play(
            LaggedStart(*[
                ReplacementTransform(
                    l0_copy.get_part_by_tex(tex),
                    lines[2].get_part_by_tex(tex),
                    path_arc=60 * DEGREES,
                )
                for tex in ["44", "\\over", "7", "approx", "2\\pi"]
            ], lag_ratio=0.1, run_time=2),
        )
        self.wait()
        self.play(Transform(lines[2], lines[3]))
        self.wait()

        left_arithmetic = VGroup(rect, lines[:3])
        self.play(
            LaggedStart(
                FadeOut(self.spiral_group[0]),
                FadeOut(left_arithmetic),
                FadeOut(self.right_arithmetic),
            )
        )

    def count_by_44(self):
        ff_label, ff_line = self.spiral_group[1:]
        faded_labels = self.labels
        frame = self.camera_frame

        n_values = 100
        mod = 44
        values = range(mod, n_values * mod, mod)
        points = [
            self.get_polar_point(n, n)
            for n in values
        ]

        p2l_tracker = ValueTracker(
            get_norm(ff_label.get_bottom() - points[0])
        )
        get_p2l = p2l_tracker.get_value
        l_height_ratio_tracker = ValueTracker(
            ff_label.get_height() / frame.get_height()
        )
        get_l_height_ratio = l_height_ratio_tracker.get_value

        n_labels = 10
        labels = VGroup(*[Integer(n) for n in values[:n_labels]])
        for label, point in zip(labels, points):
            label.point = point
            label.add_updater(
                lambda l: l.set_height(
                    frame.get_height() * get_l_height_ratio()
                )
            )
            label.add_updater(
                lambda l: l.move_to(
                    l.point + get_p2l() * UP,
                    DOWN,
                )
            )
        labels.set_stroke(BLACK, 2, background=True)

        lines = VGroup(ff_line)
        for p1, p2 in zip(points, points[1:]):
            lines.add(Line(p1, p2))
        lines.match_style(ff_line)

        self.remove(self.spiral_group)
        self.remove(faded_labels[44])
        self.play(
            frame.scale, self.zoom_factor_1,
            p2l_tracker.set_value, 1,
            l_height_ratio_tracker.set_value, 0.025,
            FadeOut(
                ff_label,
                rate_func=squish_rate_func(smooth, 0, 1 / 8),
            ),
            LaggedStart(
                *2 * [Animation(Group())],  # Weird and dumb
                *map(FadeIn, labels),
                lag_ratio=0.5,
            ),
            LaggedStart(
                *2 * [Animation(Group())],
                *map(ShowCreation, lines[:len(labels)]),
                lag_ratio=1,
            ),
            run_time=8,
        )
        self.play(
            frame.scale, self.zoom_factor_2,
            l_height_ratio_tracker.set_value, 0.01,
            ShowCreation(lines[len(labels):]),
            run_time=8,
        )

        self.ff_spiral_lines = lines
        self.ff_spiral_labels = labels

    #
    def arc_func(self, t):
        r = 0.1 * t
        return r * np.array([np.cos(t), np.sin(t), 0])


class Label44Spirals(Explain44Spirals):
    def construct(self):
        self.setup_spirals()
        self.enumerate_spirals()

    def setup_spirals(self):
        max_N = self.max_N
        mod = 44
        primes = read_in_primes(max_N)
        spirals = VGroup()
        for r in range(mod):
            ns = range(r, max_N, mod)
            spiral = self.get_v_spiral(ns, box_width=1)
            for box, n in zip(spiral, ns):
                if n in primes:
                    box.set_color(TEAL)
                else:
                    box.set_color(YELLOW)
            spirals.add(spiral)

        self.add(spirals)
        scale = np.prod([
            self.initial_scale,
            self.zoom_factor_1,
            self.zoom_factor_2,
        ])
        self.set_scale(
            spiral=VGroup(*it.chain(*spirals)),
            scale=scale,
            run_time=0
        )

        self.spirals = spirals

    def enumerate_spirals(self):
        spirals = self.spirals
        labels = self.get_spiral_arm_labels(spirals)

        self.play(
            spirals[1:].set_opacity, 0.25,
            FadeIn(labels[0]),
        )
        self.wait()

        for n in range(10):
            arc = Arc(
                start_angle=n + 0.2,
                angle=0.9,
                radius=1.5,
            )
            arc.add_tip()
            mid_point = arc.point_from_proportion(0.5)
            r_label = TextMobject("1 radian")
            # r_label.rotate(
            #     angle_of_vector(arc.get_end() - arc.get_start()) - PI

            # )
            r_label.next_to(mid_point, normalize(mid_point))

            self.play(
                ShowCreation(arc),
                FadeIn(r_label),
                spirals[n + 1].set_opacity, 1,
                TransformFromCopy(labels[n], labels[n + 1])
            )
            self.play(
                FadeOut(arc),
                FadeOut(r_label),
                spirals[n].set_opacity, 0.25,
                FadeOut(labels[n]),
            )

    #
    def get_spiral_arm_labels(self, spirals, index=15):
        mod = 44
        labels = VGroup(*[
            VGroup(
                *TexMobject("44k", "+"),
                Integer(n)
            ).arrange(RIGHT, buff=SMALL_BUFF)
            for n in range(mod)
        ])
        labels[0][1:].set_opacity(0)
        labels.scale(1.5)
        labels.set_color(YELLOW)

        for label, spiral in zip(labels, spirals):
            box = spiral[index]
            vect = rotate_vector(box.get_center(), 90 * DEGREES)
            label.next_to(box, normalize(vect), SMALL_BUFF)
        labels[0].shift(UR + 1.25 * RIGHT)
        return labels


class ResidueClassMod44Label(Scene):
    def construct(self):
        text = TextMobject(
            "``Residue class mod 44''"
        )
        text.scale(2)
        text.to_corner(UL)

        self.play(Write(text))
        self.wait()


class EliminateNonPrimativeResidueClassesOf44(Label44Spirals):
    def construct(self):
        pass
