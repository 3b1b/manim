from manimlib.imports import *
import json
import numbers


OUTPUT_DIRECTORY = "spirals"
INV_113_MOD_710 = 377  # Inverse of 113 mode 710
INV_7_MOD_44 = 19


def is_prime(n):
    if n < 2:
        return False
    for k in range(2, int(np.sqrt(n)) + 1):
        if n % k == 0:
            return False
    return True


def generate_prime_list(*args):
    if len(args) == 1:
        start, stop = 2, args[0]
    elif len(args) == 2:
        start, stop = args
        start = max(start, 2)
    else:
        raise TypeError("generate_prime_list takes 1 or 2 arguments")

    result = [
        n for n in range(start, stop)
        if is_prime(n)
    ]
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
        file = "primes_1e6.json"
    else:
        file = "primes_1e7.json"

    with open(os.path.join("assets", file)) as fp:
        primes = np.array(json.load(fp))
    return primes[primes <= max_N]


class SpiralScene(MovingCameraScene):
    CONFIG = {
        "axes_config": {
            "axis_config": {
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
                  added_anims=[],
                  run_time=3):
        if axes is None:
            axes = self.axes
        if added_anims is None:
            added_anims = []
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
        anims += added_anims

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

class AltTitle(Scene):
    def construct(self):
        title_text = """
            How pretty but pointless patterns\\\\
            in polar plots of primes\\\\
            prompt pretty important ponderings\\\\
            on properties of those primes.
        """
        words = [w + " " for w in title_text.split(" ") if w]
        title = TextMobject(*words)
        title.set_width(FRAME_WIDTH - 1)

        title[2:5].set_color(TEAL)
        title[12:15].set_color(YELLOW)
        title.set_stroke(BLACK, 5, background=True)

        image = ImageMobject("PrimeSpiral")
        image.set_height(FRAME_HEIGHT)
        rect = FullScreenFadeRectangle(fill_opacity=0.25)

        self.add(image, rect)

        for word in title:
            self.play(
                FadeIn(
                    word, run_time=0.05 * len(word),
                    lag_ratio=0.4,
                )
            )
        self.wait()


class HoldUpMathExchange(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Mathematics Stack Exchange")
        title.scale(1.5)
        title.to_edge(UP)

        self.add(title)
        self.play(self.teacher.change, "raise_right_hand", ORIGIN),
        self.change_all_student_modes("thinking", look_at_arg=ORIGIN)
        self.wait(3)
        self.change_all_student_modes("confused", look_at_arg=ORIGIN)
        self.wait(3)


class MathExchangeNames(Scene):
    def construct(self):
        names = VGroup(
            TextMobject("dwymark"),
            TextMobject("Greg Martin"),
        )
        names.arrange(DOWN, buff=1)
        for name in names:
            self.play(FadeInFrom(name, RIGHT))
            self.wait()


class MathExchange(ExternallyAnimatedScene):
    pass


class PrimesAndPi(Scene):
    def construct(self):
        self.show_primes()
        self.show_rational_approximations()

    def show_primes(self):
        n_rows = 10
        n_cols = 10
        matrix = IntegerMatrix([
            [n_cols * x + y for y in range(n_cols)]
            for x in range(n_rows)
        ])
        numbers = matrix.get_entries()
        primes = VGroup(*filter(
            lambda m: is_prime(m.get_value()),
            numbers,
        ))
        non_primes = VGroup(*filter(
            lambda m: not is_prime(m.get_value()),
            numbers
        ))

        self.add(numbers)

        self.play(
            LaggedStart(*[
                ApplyFunction(
                    lambda m: m.set_color(TEAL).scale(1.2),
                    prime
                )
                for prime in primes
            ]),
            non_primes.set_opacity, 0.25,
            run_time=2,
        )
        self.wait()

        self.numbers = numbers

    def show_rational_approximations(self):
        numbers = self.numbers

        approxs = TexMobject(
            "{22 \\over 7} &=", "{:.12}\\dots\\\\".format(22 / 7),
            "{355 \\over 113} &=", "{:.12}\\dots\\\\".format(355 / 113),
            "\\pi &=", "{:.12}\\dots\\\\".format(PI),
        )
        approxs[:2].shift(MED_LARGE_BUFF * UP)
        approxs[-2:].shift(MED_LARGE_BUFF * DOWN)
        approxs[-2:].set_color(YELLOW)
        approxs[1][:4].set_color(YELLOW)
        approxs[3][:8].set_color(YELLOW)
        approxs.scale(1.5)

        randy = Randolph(color=YELLOW, height=1)
        randy.move_to(approxs[-2][0], RIGHT)
        approxs[-2][0].set_opacity(0)

        self.play(
            LaggedStartMap(FadeOutAndShiftDown, numbers),
            LaggedStartMap(FadeIn, approxs),
            FadeIn(randy)
        )
        self.play(Blink(randy))
        self.play(randy.change, "pondering", UR)
        self.wait()


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
        theta_tracker = ValueTracker(0)
        theta_tracker.add_updater(
            lambda m: m.set_value(r_line.get_angle() % TAU)
        )
        self.add(theta_tracker)
        arc.add_updater(
            lambda m: m.become(
                self.get_arc(theta_tracker.get_value())
            )
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
            FadeOut(r_label),
            FadeOut(theta_label),
            FadeOut(radians_word),
            FadeOut(r_line),
            FadeOut(arc),
            FadeOut(dot),
        )

        self.dot = dot
        self.r_line = r_line
        self.arc = arc
        self.theta_tracker = theta_tracker

    def show_all_nn_tuples(self):
        dot = self.dot
        arc = self.arc
        r_line = self.r_line
        theta_tracker = self.theta_tracker

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
        dot.move_to(self.get_polar_point(1, 1))
        self.add(dot)
        theta_tracker.clear_updaters()
        theta_tracker.set_value(1)
        # r_line = Line(ORIGIN, one.dot.get_center())
        # r_line.set_color(self.r_color)
        # pre_arc = Line(RIGHT, UR, color=self.r_color)
        # theta_tracker = ValueTracker(1)
        # arc = always_redraw(lambda: self.get_arc(theta_tracker.get_value()))

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
            ReplacementTransform(
                Line(*r_line.get_start_and_end()), arc
            ),
            ReplacementTransform(one_r_rect, one_theta_rect)
        )
        self.add(arc, one, one_theta_rect)
        self.play(FadeOut(one_theta_rect))
        self.wait()

        # Talk about 2, 3 then 4
        for n in [2, 3, 4]:
            self.play(
                Rotate(dot, 1, about_point=ORIGIN),
                theta_tracker.set_value, n,
            )
            self.wait()
            self.play(dot.move_to, self.get_polar_point(n, n))
            self.wait()

        # Zoom out and show spiral
        big_anim = Succession(*3 * [Animation(Mobject())], *it.chain(*[
            [
                AnimationGroup(
                    Rotate(dot, 1, about_point=ORIGIN),
                    ApplyMethod(theta_tracker.set_value, n),
                ),
                ApplyMethod(dot.move_to, self.get_polar_point(n, n))
            ]
            for n in [5, 6, 7, 8, 9]
        ]))

        spiral = ParametricFunction(
            lambda t: self.get_polar_point(t, t),
            t_min=0,
            t_max=25,
            stroke_width=1.5,
        )

        # self.add(spiral, pp_points, np_points)

        self.polar_grid.generate_target()
        for mob in self.polar_grid:
            if not isinstance(mob[0], Integer):
                mob.set_stroke(width=1)

        self.play(
            frame.scale, 3,
            big_anim,
            run_time=10,
        )
        self.play(
            # ApplyMethod(
            #     frame.scale, 1.5,
            #     run_time=2,
            #     rate_func=lambda t: smooth(t, 2)
            # ),
            ShowCreation(
                spiral,
                run_time=4,
            ),
            FadeOut(r_line),
            FadeOut(arc),
            FadeOut(dot),
            # MoveToTarget(self.polar_grid)
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
        return ParametricFunction(
            lambda t: self.get_polar_point(1 + 0.025 * t, t),
            t_min=0,
            t_max=theta,
            dt=0.25,
            color=color,
            stroke_width=3,
        )
        # return Arc(
        #     angle=theta,
        #     radius=r,
        #     stroke_color=color,
        # )


class IntroducePolarPlot(RefresherOnPolarCoordinates):
    def construct(self):
        self.plane = NumberPlane()
        grid = self.get_polar_grid()
        title = TextMobject("Polar coordinates")
        title.scale(3)
        title.set_stroke(BLACK, 10, background=True)
        title.to_edge(UP)

        self.add(grid, title)
        self.play(
            ShowCreation(grid, lag_ratio=0.1),
            run_time=3,
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
        some_prime.next_to(p_coords.get_left(), DOWN, buff=1.5)
        arrows = VGroup(*[
            Arrow(
                some_prime.get_top(), coord.get_bottom(),
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
            "I'm sorry,\\\\what?!?",
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

        group = VGroup(primes, arrow, numbers)
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


class HighlightGapsInSpirals(IntroducePrimePatterns):
    def construct(self):
        self.setup_spiral()

        max_n_tracker = ValueTracker(0)
        get_max_n = max_n_tracker.get_value
        gaps = always_redraw(lambda: VGroup(*[
            self.get_highlighted_gap(n - 1, n + 1, get_max_n())
            for n in [11, 33]
        ]))

        self.add(gaps)
        self.play(max_n_tracker.set_value, 25000, run_time=5)
        gaps.clear_updaters()
        self.play(FadeOut(gaps))

    def setup_spiral(self):
        p_spiral = self.get_p_spiral(read_in_primes(self.small_n_primes))
        self.add(p_spiral)
        self.set_scale(
            scale=self.spiral_scale,
            spiral=p_spiral,
            target_p_spiral_width=8,
            run_time=0,
        )

    def get_highlighted_gap(self, n1, n2, max_n):
        l1, l2 = [
            [
                self.get_polar_point(k, k)
                for k in range(INV_7_MOD_44 * n, int(max_n), 5 * 44)
            ]
            for n in (n1, n2)
        ]

        if len(l1) == 0 or len(l2) == 0:
            return VectorizedPoint()

        result = VMobject()
        result.set_points_as_corners(
            [*l1, *reversed(l2)]
        )
        result.make_smooth()

        result.set_stroke(GREY, width=0)
        result.set_fill(DARK_GREY, 1)

        return result


class QuestionIsMisleading(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Whoa, is this some\\\\divine hidden structure\\\\in the primes?",
            target_mode="surprised",
            student_index=0,
            added_anims=[
                self.students[1].change, "pondering",
                self.students[2].change, "pondering",
            ]
        )
        self.wait(2)

        self.students[0].bubble = None
        self.teacher_says(
            "Er...not exactly",
            bubble_kwargs={"width": 3, "height": 2},
            target_mode="guilty"
        )
        self.wait(3)


class JustPrimesLabel(Scene):
    def construct(self):
        text = TextMobject("Just the primes")
        text.scale(2)
        text.to_corner(UL)
        self.play(Write(text))
        self.wait(3)
        self.play(FadeOutAndShift(text, DOWN))


class DirichletComingUp(Scene):
    def construct(self):
        image = ImageMobject("Dirichlet")
        image.set_height(3)
        words = TextMobject(
            "Coming up: \\\\", "Dirichlet's theorem",
            alignment="",
        )
        words.set_color_by_tex("Dirichlet's", YELLOW)
        words.scale(1.5)
        words.next_to(image, RIGHT)
        words.set_stroke(BLACK, 8, background=True)
        Group(words, image).center()

        self.play(
            FadeInFrom(image, RIGHT),
            FadeInFrom(words, LEFT),
        )
        self.wait()


class ImagineYouFoundIt(TeacherStudentsScene):
    def construct(self):
        you = self.students[1]
        others = VGroup(
            self.students[0],
            self.students[2],
            self.teacher,
        )
        bubble = you.get_bubble(direction=LEFT)
        bubble[-1].set_fill(GREEN_SCREEN, 1)

        you_label = TextMobject("You")
        arrow = Vector(DOWN)
        arrow.next_to(you, UP)
        you_label.next_to(arrow, UP)

        self.play(
            you.change, "hesitant", you_label,
            FadeInFromDown(you_label),
            GrowArrow(arrow),
            others.set_opacity, 0.25,
        )
        self.play(Blink(you))
        self.play(
            FadeIn(bubble),
            FadeOut(you_label),
            FadeOut(arrow),
            you.change, "pondering",
        )
        self.play(you.look_at, bubble.get_corner(UR))
        self.play(Blink(you))
        self.wait()
        self.play(you.change, "hooray")
        self.play(Blink(you))
        self.wait()
        self.play(you.change, "sassy", bubble.get_top())
        self.wait(6)


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


class PrimeSpiralsAtScale1000(SpiralScene):
    def construct(self):
        spiral = self.get_prime_p_spiral(10000)
        self.add(spiral)
        self.set_scale(
            scale=1000,
            spiral=spiral,
            target_p_spiral_width=15,
            run_time=0,
        )


class SeparateIntoTwoQuestions(Scene):
    def construct(self):
        top_q = TextMobject("Why do", " primes", " cause", " spirals", "?")
        top_q.scale(2)
        top_q.to_edge(UP)

        q1 = TextMobject("Where do the\\\\", "spirals", " come from?")
        q2 = TextMobject("What happens when\\\\", "filtering to", " primes", "?")
        for q in q1, q2:
            q.scale(1.3)
            q.next_to(top_q, DOWN, LARGE_BUFF)
        q1.to_edge(LEFT)
        q1.set_color(YELLOW)
        q2.to_edge(RIGHT)
        q2.set_color(TEAL)

        v_line = DashedLine(
            top_q.get_bottom() + MED_SMALL_BUFF * DOWN,
            FRAME_HEIGHT * DOWN / 2,
        )

        self.add(top_q)
        self.wait()

        for q, text in [(q1, "spirals"), (q2, "primes")]:
            self.play(
                top_q.get_part_by_tex(text).set_color, q.get_color(),
                TransformFromCopy(
                    top_q.get_part_by_tex(text),
                    q.get_part_by_tex(text),
                ),
                LaggedStartMap(
                    FadeIn,
                    filter(
                        lambda m: m is not q.get_part_by_tex(text),
                        q,
                    )
                ),
            )
        self.wait()
        self.play(ShowCreation(v_line))
        self.wait()


class TopQuestionCross(Scene):
    def construct(self):
        top_q = TextMobject("Why do", " primes", " cause", " spirals", "?")
        top_q.scale(2)
        top_q.to_edge(UP)
        cross = Cross(top_q)

        self.play(ShowCreation(cross))
        self.wait()


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
        title = TextMobject("Overly-fancy ", "terminology")
        title.scale(1.5)
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        underline = Line().match_width(title)
        underline.next_to(title, DOWN, SMALL_BUFF)

        pre_title = TextMobject("Terminology")
        pre_title.replace(title, dim_to_match=1)

        self.play(FadeInFromDown(pre_title))
        self.wait()
        title[0].set_color(BLUE)
        underline.set_color(BLUE)
        self.play(
            ReplacementTransform(pre_title[0], title[1]),
            FadeInFrom(title[0], RIGHT),
            GrowFromCenter(underline)
        )
        self.play(
            title[0].set_color, WHITE,
            underline.set_color, WHITE,
        )
        self.wait()

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
        k = 3
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
        self.wait(6)


class SimpleLongDivision(MovingCameraScene):
    CONFIG = {
        "camera_config": {
            "background_color": DARKER_GREY
        }
    }

    def construct(self):
        divisor = Integer(6)
        num = Integer(20)
        quotient = Integer(num.get_value() // divisor.get_value())
        to_subtract = Integer(-1 * quotient.get_value() * divisor.get_value())
        remainder = Integer(num.get_value() + to_subtract.get_value())

        div_sym = VMobject()
        div_sym.set_points_as_corners([0.2 * UP, UP, UP + 3 * RIGHT])

        divisor.next_to(div_sym, LEFT, MED_SMALL_BUFF)
        num.next_to(divisor, RIGHT, MED_LARGE_BUFF)
        to_subtract.next_to(num, DOWN, buff=MED_LARGE_BUFF, aligned_edge=RIGHT)
        h_line = Line(LEFT, RIGHT)
        h_line.next_to(to_subtract, DOWN, buff=MED_SMALL_BUFF)
        remainder.next_to(to_subtract, DOWN, buff=MED_LARGE_BUFF, aligned_edge=RIGHT)
        quotient.next_to(num, UP, buff=MED_LARGE_BUFF, aligned_edge=RIGHT)

        remainder_rect = SurroundingRectangle(remainder)
        remainder_rect.set_color(RED)

        frame = self.camera_frame
        frame.scale(0.7, about_point=ORIGIN)

        divisor.set_color(YELLOW)
        num.set_color(RED)

        self.add(divisor)
        self.add(div_sym)
        self.add(num)
        self.play(FadeInFromDown(quotient))
        self.play(
            TransformFromCopy(divisor, to_subtract.copy()),
            TransformFromCopy(quotient, to_subtract),
        )
        self.play(ShowCreation(h_line))
        self.play(Write(remainder))
        self.play(ShowCreation(remainder_rect))
        self.wait()
        self.play(FadeOut(remainder_rect))


class ZoomOutWords(Scene):
    def construct(self):
        words = TextMobject("Zoom out!")
        words.scale(3)
        self.play(FadeInFromLarge(words))
        self.wait()


class Explain44Spirals(ExplainSixSpirals):
    CONFIG = {
        "max_N": 3000,
        "initial_scale": 10,
        "zoom_factor_1": 7,
        "zoom_factor_2": 3,
        "n_labels": 80,
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

        labels = self.get_labels(range(self.n_labels))

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
                box.n = n
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
            if n > 2:
                r_label.set_opacity(0)

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
    CONFIG = {
        "max_N": 7000,
    }

    def construct(self):
        self.setup_spirals()
        self.eliminate_classes()
        self.zoom_out()
        self.filter_to_primes()

    def eliminate_classes(self):
        spirals = self.spirals
        labels = self.get_spiral_arm_labels(spirals)

        # Eliminate factors of 2
        self.play(
            spirals[1:].set_opacity, 0.5,
            FadeIn(labels[0]),
        )
        self.wait()
        self.play(
            FadeOut(spirals[0]),
            FadeOut(labels[0]),
        )
        for n in range(2, 8, 2):
            self.play(
                FadeIn(labels[n]),
                spirals[n].set_opacity, 1,
            )
            self.play(FadeOut(VGroup(labels[n], spirals[n])))

        words = TextMobject("All even numbers")
        words.scale(1.5)
        words.to_corner(UL)
        self.play(
            LaggedStart(*[
                ApplyMethod(spiral.set_opacity, 1)
                for spiral in spirals[8::2]
            ], lag_ratio=0.01),
            FadeIn(words),
        )
        self.play(
            FadeOut(words),
            FadeOut(spirals[8::2])
        )
        self.wait()

        # Eliminate factors of 11
        for k in [11, 33]:
            self.play(
                spirals[k].set_opacity, 1,
                FadeIn(labels[k])
            )
            self.wait()
            self.play(
                FadeOut(spirals[k]),
                FadeOut(labels[k]),
            )

        admissible_spirals = VGroup(*[
            spiral
            for n, spiral in enumerate(spirals)
            if n % 2 != 0 and n % 11 != 0

        ])

        self.play(admissible_spirals.set_opacity, 1)

        self.admissible_spirals = admissible_spirals

    def zoom_out(self):
        frame = self.camera_frame
        admissible_spirals = self.admissible_spirals
        admissible_spirals.generate_target()
        for spiral in admissible_spirals.target:
            for box in spiral:
                box.scale(3)

        self.play(
            frame.scale, 4,
            MoveToTarget(admissible_spirals),
            run_time=3,
        )

    def filter_to_primes(self):
        admissible_spirals = self.admissible_spirals
        frame = self.camera_frame
        primes = read_in_primes(self.max_N)

        to_fade = VGroup(*[
            box
            for spiral in admissible_spirals
            for box in spiral
            if box.n not in primes
        ])
        words = TextMobject("Just the primes")
        words.set_height(0.1 * frame.get_height())
        words.next_to(frame.get_corner(UL), DR, LARGE_BUFF)

        self.play(
            LaggedStartMap(FadeOut, to_fade, lag_ratio=2 / len(to_fade)),
            FadeIn(words),
        )
        self.wait()


class IntroduceTotientJargon(TeacherStudentsScene):
    def construct(self):
        self.add_title()
        self.eliminate_non_coprimes()

    def add_title(self):
        self.teacher_says(
            "More jargon!",
            target_mode="hooray",
        )
        self.change_all_student_modes("erm")
        words = self.teacher.bubble.content

        words.generate_target()
        words.target.scale(1.5)
        words.target.center().to_edge(UP, buff=MED_SMALL_BUFF)
        words.target.set_color(BLUE)
        underline = Line(LEFT, RIGHT)
        underline.match_width(words.target)
        underline.next_to(words.target, DOWN, SMALL_BUFF)
        underline.scale(1.2)

        self.play(
            MoveToTarget(words),
            FadeOut(self.teacher.bubble),
            LaggedStart(*[
                FadeOutAndShift(pi, 4 * DOWN)
                for pi in self.pi_creatures
            ]),
            ShowCreation(underline)
        )

    def eliminate_non_coprimes(self):
        number_grid = VGroup(*[
            VGroup(*[
                Integer(n) for n in range(11 * k, 11 * (k + 1))
            ]).arrange(DOWN)
            for k in range(4)
        ]).arrange(RIGHT, buff=1)
        numbers = VGroup(*it.chain(*number_grid))
        numbers.set_height(6)
        numbers.move_to(4 * LEFT)
        numbers.to_edge(DOWN)

        evens = VGroup(*filter(
            lambda nm: nm.get_value() % 2 == 0,
            numbers
        ))
        div11 = VGroup(*filter(
            lambda nm: nm.get_value() % 11 == 0,
            numbers
        ))
        coprimes = VGroup(*filter(
            lambda nm: nm not in evens and nm not in div11,
            numbers
        ))

        words = TextMobject(
            "Which ones ", "don't\\\\",
            "share any factors\\\\",
            "with ", "44",
            alignment=""
        )
        words.scale(1.5)
        words.next_to(ORIGIN, RIGHT)

        ff = words.get_part_by_tex("44")
        ff.set_color(YELLOW)
        ff.generate_target()

        # Show coprimes
        self.play(
            ShowIncreasingSubsets(numbers, run_time=3),
            FadeInFrom(words, LEFT)
        )
        self.wait()
        for group in evens, div11:
            rects = VGroup(*[
                SurroundingRectangle(number, color=RED)
                for number in group
            ])
            self.play(LaggedStartMap(ShowCreation, rects, run_time=1))
            self.play(
                LaggedStart(*[
                    ApplyMethod(number.set_opacity, 0.2)
                    for number in group
                ]),
                LaggedStartMap(FadeOut, rects),
                run_time=1
            )
            self.wait()

        # Rearrange words
        dsf = words[1:3]
        dsf.generate_target()
        dsf.target.arrange(RIGHT)
        dsf.target[0].align_to(dsf.target[1][0], DOWN)

        example = numbers[35].copy()
        example.generate_target()
        example.target.match_height(ff)
        num_pair = VGroup(
            ff.target,
            TextMobject("and").scale(1.5),
            example.target,
        )
        num_pair.arrange(RIGHT)
        num_pair.move_to(words.get_top(), DOWN)
        dsf.target.next_to(num_pair, DOWN, MED_LARGE_BUFF)

        phrase1 = TextMobject("are ", "``relatively prime''")
        phrase2 = TextMobject("are ", "``coprime''")
        for phrase in phrase1, phrase2:
            phrase.scale(1.5)
            phrase.move_to(dsf.target)
            phrase[1].set_color(BLUE)
            phrase.arrow = TexMobject("\\Updownarrow")
            phrase.arrow.scale(1.5)
            phrase.arrow.next_to(phrase, DOWN, 2 * SMALL_BUFF)
            phrase.rect = SurroundingRectangle(phrase[1])
            phrase.rect.set_stroke(BLUE)

        self.play(
            FadeOut(words[0]),
            FadeOut(words[3]),
            MoveToTarget(dsf),
            MoveToTarget(ff),
            GrowFromCenter(num_pair[1]),
        )
        self.play(
            MoveToTarget(example, path_arc=30 * DEGREES),
        )
        self.wait()
        self.play(
            dsf.next_to, phrase1.arrow, DOWN, SMALL_BUFF,
            GrowFromEdge(phrase1.arrow, UP),
            GrowFromCenter(phrase1),
            ShowCreation(phrase1.rect)
        )
        self.play(FadeOut(phrase1.rect))
        self.wait()
        self.play(
            VGroup(dsf, phrase1, phrase1.arrow).next_to,
            phrase2.arrow, DOWN, SMALL_BUFF,
            GrowFromEdge(phrase2.arrow, UP),
            GrowFromCenter(phrase2),
            ShowCreation(phrase2.rect)
        )
        self.play(FadeOut(phrase2.rect))
        self.wait()

        # Count through coprimes
        coprime_rects = VGroup(*map(SurroundingRectangle, coprimes))
        coprime_rects.set_stroke(BLUE, 2)
        example_anim = UpdateFromFunc(
            example, lambda m: m.set_value(coprimes[len(coprime_rects) - 1].get_value())
        )
        self.play(
            ShowIncreasingSubsets(coprime_rects, int_func=np.ceil),
            example_anim,
            run_time=3,
            rate_func=linear,
        )
        self.wait()

        # Show totient function
        words_to_keep = VGroup(ff, num_pair[1], example, phrase2)
        to_fade = VGroup(phrase2.arrow, phrase1, phrase1.arrow, dsf)

        totient = TexMobject("\\phi", "(", "44", ")", "=", "20")
        totient.set_color_by_tex("44", YELLOW)
        totient.scale(1.5)
        totient.move_to(num_pair, UP)
        phi = totient.get_part_by_tex("phi")
        rhs = Integer(20)
        rhs.replace(totient[-1], dim_to_match=1)
        totient.submobjects[-1] = rhs

        self.play(
            words_to_keep.to_edge, DOWN,
            MaintainPositionRelativeTo(to_fade, words_to_keep),
            VFadeOut(to_fade),
        )
        self.play(FadeIn(totient))
        self.wait()

        # Label totient
        brace = Brace(phi, DOWN)
        etf = TextMobject("Euler's totient function")
        etf.next_to(brace, DOWN)
        etf.shift(RIGHT)

        self.play(
            GrowFromCenter(brace),
            FadeInFrom(etf, UP)
        )
        self.wait()
        self.play(
            ShowIncreasingSubsets(coprime_rects),
            UpdateFromFunc(
                rhs, lambda m: m.set_value(len(coprime_rects)),
            ),
            example_anim,
            rate_func=linear,
            run_time=3,
        )
        self.wait()

        # Show totatives
        totient_group = VGroup(totient, brace, etf)
        for cp, rect in zip(coprimes, coprime_rects):
            cp.add(rect)

        self.play(
            coprimes.arrange, RIGHT, {"buff": SMALL_BUFF},
            coprimes.set_width, FRAME_WIDTH - 1,
            coprimes.move_to, 2 * UP,
            FadeOut(evens),
            FadeOut(div11[1::2]),
            FadeOutAndShiftDown(words_to_keep),
            totient_group.center,
            totient_group.to_edge, DOWN,
        )

        totatives = TextMobject("``Totatives''")
        totatives.scale(2)
        totatives.set_color(BLUE)
        totatives.move_to(ORIGIN)
        arrows = VGroup(*[
            Arrow(totatives.get_top(), coprime.get_bottom())
            for coprime in coprimes
        ])
        arrows.set_color(WHITE)

        self.play(
            FadeIn(totatives),
            LaggedStartMap(VFadeInThenOut, arrows, run_time=4, lag_ratio=0.05)
        )
        self.wait(2)


class TwoUnrelatedFacts(Scene):
    def construct(self):
        self.add_title()
        self.show_columns()

    def add_title(self):
        title = TextMobject("Two (unrelated) bits of number theory")
        title.set_width(FRAME_WIDTH - 1)
        title.to_edge(UP)
        h_line = Line()
        h_line.match_width(title)
        h_line.next_to(title, DOWN, SMALL_BUFF)
        h_line.set_stroke(LIGHT_GREY)

        self.play(
            FadeIn(title),
            ShowCreation(h_line),
        )

        self.h_line = h_line

    def show_columns(self):
        h_line = self.h_line
        v_line = Line(
            h_line.get_center() + MED_SMALL_BUFF * DOWN,
            FRAME_HEIGHT * DOWN / 2,
        )
        v_line.match_style(h_line)

        approx = TexMobject(
            "{44 \\over 7} \\approx 2\\pi"
        )
        approx.scale(1.5)
        approx.next_to(
            h_line.point_from_proportion(0.25),
            DOWN, MED_LARGE_BUFF,
        )

        mod = 44
        n_terms = 9
        residue_classes = VGroup()
        prime_numbers = read_in_primes(1000)
        primes = VGroup()
        non_primes = VGroup()
        for r in range(mod):
            if r <= 11 or r == 43:
                row = VGroup()
                for n in range(r, r + n_terms * mod, mod):
                    elem = Integer(n)
                    comma = TexMobject(",")
                    comma.next_to(
                        elem.get_corner(DR),
                        RIGHT, SMALL_BUFF
                    )
                    elem.add(comma)
                    row.add(elem)
                    if n in prime_numbers:
                        primes.add(elem)
                    else:
                        non_primes.add(elem)
                row.arrange(RIGHT, buff=0.3)
                dots = TexMobject("\\dots")
                dots.next_to(row.get_corner(DR), RIGHT, SMALL_BUFF)
                dots.shift(SMALL_BUFF * UP)
                row.add(dots)
                row.r = r
            if r == 12:
                row = TexMobject("\\vdots")
            residue_classes.add(row)

        residue_classes.arrange(DOWN)
        residue_classes[-2].align_to(residue_classes, LEFT)
        residue_classes[-2].shift(MED_SMALL_BUFF * RIGHT)
        residue_classes.set_height(6)
        residue_classes.next_to(ORIGIN, RIGHT)
        residue_classes.to_edge(DOWN, buff=MED_SMALL_BUFF)

        def get_line(row):
            return Line(
                row.get_left(), row.get_right(),
                stroke_color=RED,
                stroke_width=4,
            )

        even_lines = VGroup(*[
            get_line(row)
            for row in residue_classes[:12:2]
        ])
        eleven_line = get_line(residue_classes[11])
        eleven_line.set_color(PINK)
        for line in [even_lines[1], eleven_line]:
            line.scale(0.93, about_edge=RIGHT)

        self.play(ShowCreation(v_line))
        self.wait()
        self.play(FadeInFrom(approx, DOWN))
        self.wait()
        self.play(FadeIn(residue_classes))
        self.wait()
        self.play(
            LaggedStartMap(ShowCreation, even_lines),
        )
        self.wait()
        self.play(ShowCreation(eleven_line))
        self.wait()
        self.play(
            primes.set_color, TEAL,
            non_primes.set_opacity, 0.25,
            even_lines.set_opacity, 0.25,
            eleven_line.set_opacity, 0.25,
        )
        self.wait()


class ExplainRays(Explain44Spirals):
    CONFIG = {
        "max_N": int(5e5),
        "axes_config": {
            "x_min": -1000,
            "x_max": 1000,
            "y_min": -1000,
            "y_max": 1000,
            "axis_config": {
                "tick_frequency": 50,
            },
        },
    }

    def construct(self):
        self.add_spirals_and_labels()
        self.show_710th_point()
        self.show_arithmetic()
        self.zoom_and_count()

    def show_710th_point(self):
        spiral = self.spiral
        axes = self.axes
        labels = self.labels

        scale_factor = 12

        fade_rect = FullScreenFadeRectangle()
        fade_rect.scale(scale_factor)

        new_ns = list(range(711))
        bright_boxes = self.get_v_spiral(new_ns)
        bright_boxes.set_color(YELLOW)
        for n, box in enumerate(bright_boxes):
            box.set_height(0.02 * np.sqrt(n))

        big_labels = self.get_labels(new_ns)

        index_tracker = ValueTracker(44)

        labeled_box = VGroup(Square(), Integer(0))

        def update_labeled_box(mob):
            index = int(index_tracker.get_value())
            labeled_box[0].become(bright_boxes[index])
            labeled_box[1].become(big_labels[index])

        labeled_box.add_updater(update_labeled_box)

        self.set_scale(
            scale=120,
            spiral=spiral,
            to_shrink=labels,
        )

        box_710 = self.get_v_spiral([710])[0]
        box_710.scale(2)
        box_710.set_color(YELLOW)
        label_710 = Integer(710)
        label_710.scale(1.5)
        label_710.next_to(box_710, UP)

        arrow = Arrow(
            ORIGIN, DOWN,
            stroke_width=6,
            max_tip_length_to_length_ratio=0.35,
            max_stroke_width_to_length_ratio=10,
            tip_length=0.35
        )
        arrow.match_color(box_710)
        arrow.next_to(box_710, UP, SMALL_BUFF)
        label_710.next_to(arrow, UP, SMALL_BUFF)

        self.add(spiral, fade_rect, axes, labels)
        self.play(
            FadeIn(fade_rect),
            FadeOut(labels),
            FadeInFromLarge(box_710),
            FadeInFrom(label_710, DOWN),
            ShowCreation(arrow),
        )
        self.wait()

        self.fade_rect = fade_rect
        self.box_710 = box_710
        self.label_710 = label_710
        self.arrow = arrow

    def show_arithmetic(self):
        label_710 = self.label_710

        equation = TexMobject(
            "710", "\\text{ radians}", "=",
            "(710 / 2\\pi)", "\\text{ rotations}",
        )
        equation.to_corner(UL)
        frac = equation.get_part_by_tex("710 / 2\\pi")
        brace = Brace(frac, DOWN, buff=SMALL_BUFF)
        value = TextMobject("{:.15}".format(710 / TAU))
        value.next_to(brace, DOWN, SMALL_BUFF)
        values = VGroup(*[
            value[0][:n].deepcopy().next_to(brace, DOWN, SMALL_BUFF)
            for n in [3, *range(5, 13)]
        ])

        group = VGroup(equation, brace, value)
        rect = SurroundingRectangle(group, buff=MED_SMALL_BUFF)
        rect.set_stroke(WHITE, 2)
        rect.set_fill(DARK_GREY, 1)

        approx = TexMobject(
            "{710", "\\over", "113}",
            "\\approx", "2\\pi",
        )
        approx.next_to(rect, DOWN)
        approx.align_to(equation, LEFT)

        approx2 = TexMobject(
            "{355", "\\over", "113}",
            "\\approx", "\\pi",
        )
        approx2.next_to(approx, RIGHT, LARGE_BUFF)

        self.play(
            FadeIn(rect),
            TransformFromCopy(label_710, equation[0]),
            FadeIn(equation[1:3]),
        )
        self.play(
            FadeInFrom(equation[3:], LEFT)
        )
        self.play(GrowFromCenter(brace))
        self.play(
            ShowSubmobjectsOneByOne(values),
            run_time=3,
            rate_func=linear,
        )
        self.wait()
        self.play(
            rect.stretch, 2, 1, {"about_edge": UP},
            LaggedStart(
                TransformFromCopy(  # 710
                    equation[3][1:4],
                    approx[0],
                ),
                FadeIn(approx[1][0]),
                TransformFromCopy(  # 113
                    values[-1][:3],
                    approx[2],
                ),
                FadeIn(approx[3]),
                TransformFromCopy(  # 2pi
                    equation[3][5:7],
                    approx[4],
                ),
                run_time=2,
            )
        )
        self.wait()
        self.play(
            TransformFromCopy(approx, approx2),
        )
        self.wait()
        self.play(
            FadeOut(VGroup(
                rect, equation, brace, values[-1],
                approx, approx2
            )),
            self.fade_rect.set_opacity, 0.25,
        )

    def zoom_and_count(self):
        label = self.label_710
        arrow = self.arrow
        box = self.box_710
        axes = self.axes
        spiral = self.spiral

        times = TexMobject("\\times")
        times.next_to(label, LEFT, SMALL_BUFF)
        k_label = Integer(1)
        k_label.match_height(label)
        k_label.set_color(YELLOW)
        k_label.next_to(times, LEFT)

        boxes = VGroup(*[box.copy() for x in range(150)])
        box_height_tracker = ValueTracker(box.get_height())

        def get_k():
            max_x = axes.x_axis.p2n(label.get_center())
            return max(1, int(max_x / 710))

        def get_k_point(k):
            return self.get_polar_point(710 * k, 710 * k)

        def update_arrow(arrow):
            point = get_k_point(get_k())
            arrow.put_start_and_end_on(
                label.get_bottom() + SMALL_BUFF * DOWN,
                point + SMALL_BUFF * UP
            )

        def get_unit():
            return get_norm(axes.c2p(1, 0) - axes.c2p(0, 0))

        def update_boxes(boxes):
            box_height = box_height_tracker.get_value()
            for k, box in enumerate(boxes):
                box.set_height(box_height)
                box.move_to(get_k_point(k))

        arrow.add_updater(update_arrow)
        boxes.add_updater(update_boxes)
        k_label.add_updater(
            lambda d: d.set_value(get_k()).next_to(
                times, LEFT, SMALL_BUFF
            )
        )

        self.remove(box)
        self.add(times, k_label, boxes)
        self.set_scale(
            scale=10000,
            spiral=self.spiral,
            run_time=8,
            target_p_spiral_width=2,
            added_anims=[
                box_height_tracker.set_value, 0.035,
            ]
        )
        self.wait()

        # Show other residue classes
        new_label = TexMobject(
            "710", "k", "+",
            tex_to_color_map={"k": YELLOW}
        )
        new_label.match_height(label)
        new_label.next_to(boxes, UP, SMALL_BUFF)
        new_label.to_edge(RIGHT)
        new_label[2].set_opacity(0)

        r_label = Integer(1)
        r_label.match_height(new_label)
        r_label.set_opacity(0)
        r_label.add_updater(
            lambda m: m.next_to(new_label, RIGHT, SMALL_BUFF)
        )

        k_label.clear_updaters()
        self.play(
            FadeOut(times),
            ReplacementTransform(label, new_label[0]),
            ReplacementTransform(k_label, new_label[1]),
            FadeOut(arrow)
        )

        boxes.clear_updaters()
        for r in range(1, 12):
            if r in [3, 6]:
                vect = UR
            else:
                vect = RIGHT
            point = rotate_vector(boxes[40].get_center(), 1)
            new_boxes = boxes.copy()
            new_boxes.rotate(1, about_point=ORIGIN)
            for box in new_boxes:
                box.rotate(-1)
            self.play(
                FadeOut(boxes),
                LaggedStartMap(FadeIn, new_boxes, lag_ratio=0.01),
                new_label.set_opacity, 1,
                new_label.next_to, point, vect,
                r_label.set_opacity, 1,
                ChangeDecimalToValue(r_label, r),
                run_time=1,
            )
            self.remove(boxes)
            boxes = new_boxes
            self.add(boxes)
            self.wait()

        # Show just the primes
        self.play(
            FadeOut(boxes),
            FadeOut(new_label),
            FadeOut(r_label),
            FadeOut(self.fade_rect)
        )
        self.set_scale(
            30000,
            spiral=spiral,
            run_time=4,
        )
        self.wait()
        self.remove(spiral)
        self.add(spiral[1])
        self.wait()


class CompareTauToApprox(Scene):
    def construct(self):
        eqs = VGroup(
            TexMobject("2\\pi", "=", "{:.10}\\dots".format(TAU)),
            TexMobject("\\frac{710}{113}", "=", "{:.10}\\dots".format(710 / 113)),
        )
        eqs.arrange(DOWN, buff=LARGE_BUFF)
        eqs[1].shift((eqs[0][2].get_left()[0] - eqs[1][2].get_left()[0]) * RIGHT)

        eqs.generate_target()
        for eq in eqs.target:
            eq[2][:8].set_color(RED)
            eq.set_stroke(BLACK, 8, background=True)

        self.play(LaggedStart(
            FadeInFrom(eqs[0], DOWN),
            FadeInFrom(eqs[1], UP),
        ))
        self.play(MoveToTarget(eqs))
        self.wait()


class RecommendedMathologerVideo(Scene):
    def construct(self):
        full_rect = FullScreenFadeRectangle()
        full_rect.set_fill(DARK_GREY, 1)
        self.add(full_rect)

        title = TextMobject("Recommended Mathologer video")
        title.set_width(FRAME_WIDTH - 1)
        title.to_edge(UP)
        screen_rect = SurroundingRectangle(ScreenRectangle(height=5.9), buff=SMALL_BUFF)
        screen_rect.next_to(title, DOWN)
        screen_rect.set_fill(BLACK, 1)
        screen_rect.set_stroke(WHITE, 3)

        self.add(screen_rect)
        self.play(Write(title))
        self.wait()


class ShowClassesOfPrimeRays(SpiralScene):
    CONFIG = {
        "max_N": int(1e6),
        "scale": 1e5
    }

    def construct(self):
        self.setup_rays()
        self.show_classes()

    def setup_rays(self):
        spiral = self.get_prime_p_spiral(self.max_N)
        self.add(spiral)
        self.set_scale(
            scale=self.scale,
            spiral=spiral,
            target_p_spiral_width=3,
            run_time=0
        )

    def show_classes(self):
        max_N = self.max_N
        mod = 710
        primes = read_in_primes(max_N)

        rect = FullScreenFadeRectangle()
        rect.set_opacity(0)
        self.add(rect)

        last_ray = PMobject()
        last_label = VGroup(*[VectorizedPoint() for x in range(3)])
        for i in range(40):
            if get_gcd(i, mod) != 1:
                continue

            r = (INV_113_MOD_710 * i) % mod

            sequence = filter(
                lambda x: x in primes,
                range(r, max_N, mod)
            )
            ray = self.get_v_spiral(sequence, box_width=0.03)
            ray.set_color(GREEN)
            ray.set_opacity(0.9)

            label = VGroup(
                *TexMobject("710k", "+"),
                Integer(r)
            )
            label.arrange(RIGHT, buff=SMALL_BUFF)
            label.next_to(ray[100], UL, SMALL_BUFF)

            label[2].save_state()
            label[2].set_opacity(0)
            label[2].move_to(last_label, RIGHT)

            self.play(
                rect.set_opacity, 0.5,
                ShowCreation(ray),
                LaggedStartMap(FadeOut, last_ray),
                ReplacementTransform(last_label[:2], label[:2]),
                Restore(label[2]),
                last_label[2].move_to, label[2].saved_state,
                last_label[2].set_opacity, 0,
            )
            self.remove(last_label)
            self.add(label)
            self.wait()

            last_ray = ray
            last_label = label


class ShowFactorsOf710(Scene):
    def construct(self):
        equation = TexMobject(
            "710", "=",
            "71", "\\cdot",
            "5", "\\cdot",
            "2",
        )
        equation.scale(1.5)
        equation.to_corner(UL)
        ten = TexMobject("10")
        ten.match_height(equation)
        ten.move_to(equation.get_part_by_tex("5"), LEFT)

        self.add(equation[0])
        self.wait()
        self.play(
            TransformFromCopy(
                equation[0][:2],
                equation[2],
            ),
            FadeIn(equation[1]),
            FadeIn(equation[3]),
            TransformFromCopy(
                equation[0][2:],
                ten,
            )
        )
        self.wait()
        self.remove(ten)
        self.play(*[
            TransformFromCopy(ten, mob)
            for mob in equation[4:]
        ])
        self.wait()

        # Circle factors
        colors = [RED, BLUE, PINK]
        for factor, color in zip(equation[:-6:-2], colors):
            rect = SurroundingRectangle(factor)
            rect.set_color(color)
            self.play(ShowCreation(rect))
            self.wait()
            self.play(FadeOut(rect))


class LookAtRemainderMod710(Scene):
    def construct(self):
        t2c = {
            "n": YELLOW,
            "r": GREEN
        }
        equation = TexMobject(
            "n", "=", "710", "k", "+", "r",
            tex_to_color_map=t2c,
        )
        equation.scale(1.5)

        n_arrow = Vector(UP).next_to(equation.get_part_by_tex("n"), DOWN)
        r_arrow = Vector(UP).next_to(equation.get_part_by_tex("r"), DOWN)
        n_arrow.set_color(t2c["n"])
        r_arrow.set_color(t2c["r"])

        n_label = TextMobject("Some\\\\number")
        r_label = TextMobject("Remainder")
        VGroup(n_label, r_label).scale(1.5)
        n_label.next_to(n_arrow, DOWN)
        n_label.match_color(n_arrow)
        r_label.next_to(r_arrow, DOWN)
        r_label.match_color(r_arrow)

        self.add(equation)
        self.play(
            FadeInFrom(n_label, UP),
            ShowCreation(n_arrow),
        )
        self.wait()
        self.play(
            FadeInFrom(r_label, DOWN),
            ShowCreation(r_arrow),
        )
        self.wait()


class EliminateNonPrimative710Residues(ShowClassesOfPrimeRays):
    CONFIG = {
        "max_N": int(5e5),
        "scale": 5e4,
    }

    def construct(self):
        self.setup_rays()
        self.eliminate_classes()

    def setup_rays(self):
        mod = 710
        rays = PGroup(*[
            self.get_p_spiral(range(r, self.max_N, mod))
            for r in range(mod)
        ])
        rays.set_color(YELLOW)
        self.add(rays)
        self.set_scale(
            scale=self.scale,
            spiral=rays,
            target_p_spiral_width=1,
            run_time=0,
        )

        self.rays = rays

    def eliminate_classes(self):
        rays = self.rays
        rect = FullScreenFadeRectangle()
        rect.set_opacity(0)

        for r, ray in enumerate(rays):
            ray.r = r

        mod = 710
        odds = PGroup(*[rays[i] for i in range(1, mod, 2)])
        mult5 = PGroup(*[rays[i] for i in range(0, mod, 5) if i % 2 != 0])
        mult71 = PGroup(*[rays[i] for i in range(0, mod, 71) if (i % 2 != 0 and i % 5 != 0)])
        colors = [RED, BLUE, PINK]

        pre_label, r_label = label = VGroup(
            TexMobject("710k + "),
            Integer(100)
        )
        label.scale(1.5)
        label.arrange(RIGHT, buff=SMALL_BUFF)
        label.set_stroke(BLACK, 5, background=True, family=True)
        label.next_to(ORIGIN, DOWN)

        r_label.group = odds
        r_label.add_updater(
            lambda m: m.set_value(m.group[-1].r if len(m.group) > 0 else 1),
        )

        self.remove(rays)
        # Odds
        odds.set_stroke_width(3)
        self.add(odds, label)
        self.play(
            ShowIncreasingSubsets(odds, int_func=np.ceil),
            run_time=10,
        )
        self.play(FadeOut(label))
        self.remove(odds)
        self.add(*odds)
        self.wait()

        # Multiples of 5 then 71
        for i, group in [(1, mult5), (2, mult71)]:
            group_copy = group.copy()
            group_copy.set_color(colors[i])
            group_copy.set_stroke_width(4)
            r_label.group = group_copy
            self.add(group_copy, label)
            self.play(
                ShowIncreasingSubsets(group_copy, int_func=np.ceil, run_time=10),
            )
            self.play(FadeOut(label))
            self.wait()
            self.remove(group_copy, *group)
            self.wait()


class Show280Computation(Scene):
    def construct(self):
        equation = TexMobject(
            "\\phi(710) = ",
            "710",
            "\\left({1 \\over 2}\\right)",
            "\\left({4 \\over 5}\\right)",
            "\\left({70 \\over 71}\\right)",
            "=",
            "280",
        )
        equation.set_width(FRAME_WIDTH - 1)
        equation.move_to(UP)
        words = VGroup(
            TextMobject("Filter out\\\\evens"),
            TextMobject("Filter out\\\\multiples of 5"),
            TextMobject("Filter out\\\\multiples of 71"),
        )
        vects = [DOWN, UP, DOWN]
        colors = [RED, BLUE, LIGHT_PINK]
        for part, word, vect, color in zip(equation[2:5], words, vects, colors):
            brace = Brace(part, vect)
            brace.stretch(0.8, 0)
            word.brace = brace
            word.next_to(brace, vect)
            part.set_color(color)
            word.set_color(color)
            word.set_stroke(BLACK, 5, background=True)
        equation.set_stroke(BLACK, 5, background=True)

        etf_label = TextMobject("Euler's totient function")
        etf_label.to_corner(UL)
        arrow = Arrow(etf_label.get_bottom(), equation[0][0].get_top())
        equation[0][0].set_color(YELLOW)
        etf_label.set_color(YELLOW)

        rect = FullScreenFadeRectangle(fill_opacity=0.9)
        self.play(
            FadeIn(rect),
            FadeInFromDown(equation),
            FadeIn(etf_label),
            GrowArrow(arrow),
        )
        self.wait()
        for word in words:
            self.play(
                FadeIn(word),
                GrowFromCenter(word.brace),
            )
            self.wait()


class TeacherHoldUp(TeacherStudentsScene):
    def construct(self):
        self.change_all_student_modes(
            "pondering", look_at_arg=2 * UP,
            added_anims=[
                self.teacher.change, "raise_right_hand"
            ]
        )
        self.wait(8)


class DiscussPrimesMod10(Scene):
    def construct(self):
        labels = VGroup(*[
            TextMobject(str(n), " mod 10:")
            for n in range(10)
        ])
        labels.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        labels.to_edge(LEFT)
        # digits = VGroup(*[l[0] for l in labels])
        labels.set_submobject_colors_by_gradient(YELLOW, BLUE)

        sequences = VGroup(*[
            VGroup(*[
                Integer(n).shift((n // 10) * RIGHT)
                for n in range(r, 100 + r, 10)
            ])
            for r in range(10)
        ])
        for sequence, label in zip(sequences, labels):
            sequence.next_to(label, RIGHT, buff=MED_LARGE_BUFF)
            for item in sequence:
                if item is sequence[-1]:
                    punc = TexMobject("\\dots")
                else:
                    punc = TextMobject(",")
                punc.next_to(item.get_corner(DR), RIGHT, SMALL_BUFF)
                item.add(punc)

        # Introduce everything
        self.play(LaggedStart(*[
            FadeInFrom(label, UP)
            for label in labels
        ]))
        self.wait()
        self.play(
            LaggedStart(*[
                LaggedStart(*[
                    FadeInFrom(item, LEFT)
                    for item in sequence
                ])
                for sequence in sequences
            ])
        )
        self.wait()

        # Highlight 0's then 1's
        for sequence in sequences[:2]:
            lds = VGroup(*[item[-2] for item in sequence])
            rects = VGroup(*[
                SurroundingRectangle(ld, buff=0.05)
                for ld in lds
            ])
            rects.set_color(YELLOW)
            self.play(
                LaggedStartMap(
                    ShowCreationThenFadeOut, rects
                )
            )
            self.wait()

        # Eliminate certain residues
        two = sequences[2][0]
        five = sequences[5][0]
        evens = VGroup(*it.chain(*sequences[::2]))
        evens.remove(two)
        div5 = sequences[5][1:]
        prime_numbers = read_in_primes(100)

        primes = VGroup(*[
            item
            for seq in sequences
            for item in seq
            if int(item.get_value()) in prime_numbers
        ])
        non_primes = VGroup(*[
            item
            for seq in sequences
            for item in seq
            if reduce(op.and_, [
                int(item.get_value()) not in prime_numbers,
                item.get_value() % 2 != 0,
                item.get_value() % 5 != 0,
            ])
        ])

        for prime, group in [(two, evens), (five, div5)]:
            self.play(ShowCreationThenFadeAround(prime))
            self.play(LaggedStart(*[
                ApplyMethod(item.set_opacity, 0.2)
                for item in group
            ]))
            self.wait()

        # Highlight primes
        self.play(
            LaggedStart(*[
                ApplyFunction(
                    lambda m: m.scale(1.2).set_color(TEAL),
                    prime
                )
                for prime in primes
            ]),
            LaggedStart(*[
                ApplyFunction(
                    lambda m: m.scale(0.8).set_opacity(0.8),
                    non_prime
                )
                for non_prime in non_primes
            ]),
        )
        self.wait()

        # Highlight coprime residue classes
        rects = VGroup(*[
            SurroundingRectangle(VGroup(labels[r], sequences[r]))
            for r in [1, 3, 7, 9]
        ])
        for rect in rects:
            rect.reverse_points()

        fade_rect = FullScreenFadeRectangle()
        fade_rect.scale(1.1)
        new_fade_rect = fade_rect.copy()
        fade_rect.append_vectorized_mobject(rects[0])
        for rect in rects:
            new_fade_rect.append_vectorized_mobject(rect)

        self.play(DrawBorderThenFill(fade_rect))
        self.wait()
        self.play(
            FadeOut(fade_rect),
            FadeIn(new_fade_rect),
        )
        self.wait()


class BucketPrimesByLastDigit(Scene):
    CONFIG = {
        "bar_colors": [YELLOW, BLUE],
        "mod": 10,
        "max_n": 10000,
        "n_to_animate": 20,
        "n_to_show": 1000,
        "x_label_scale_factor": 1,
        "x_axis_label": "Last digit",
        "bar_width": 0.5,
    }

    def construct(self):
        self.add_axes()
        self.add_bars()
        self.bucket_primes()

    def add_axes(self):
        mod = self.mod

        axes = Axes(
            x_min=0,
            x_max=mod + 0.5,
            x_axis_config={
                "unit_size": 10 / mod,
                "include_tip": False,
            },
            y_min=0,
            y_max=100,
            y_axis_config={
                "unit_size": 0.055,
                "tick_frequency": 12.5,
                "include_tip": False,
            },
        )

        x_labels = VGroup()
        for x in range(mod):
            digit = Integer(x)
            digit.scale(self.x_label_scale_factor)
            digit.next_to(axes.x_axis.n2p(x + 1), DOWN, MED_SMALL_BUFF)
            x_labels.add(digit)
        self.modify_x_labels(x_labels)
        x_labels.set_submobject_colors_by_gradient(*self.bar_colors)
        axes.add(x_labels)
        axes.x_labels = x_labels

        y_labels = VGroup()
        for y in range(25, 125, 25):
            label = Integer(y, unit="\\%")
            label.next_to(axes.y_axis.n2p(y), LEFT, MED_SMALL_BUFF)
            y_labels.add(label)
        axes.add(y_labels)

        x_axis_label = TextMobject(self.x_axis_label)
        x_axis_label.next_to(axes.x_axis.get_end(), RIGHT, buff=MED_LARGE_BUFF)
        axes.add(x_axis_label)

        y_axis_label = TextMobject("Proportion")
        y_axis_label.next_to(axes.y_axis.get_end(), UP, buff=MED_LARGE_BUFF)
        # y_axis_label.set_color(self.bar_colors[0])
        axes.add(y_axis_label)

        axes.center()
        axes.set_width(FRAME_WIDTH - 1)
        axes.to_edge(DOWN)

        self.axes = axes
        self.add(axes)

    def add_bars(self):
        axes = self.axes
        mod = self.mod

        count_trackers = Group(*[
            ValueTracker(0)
            for x in range(mod)
        ])

        bars = VGroup()
        for x in range(mod):
            bar = Rectangle(
                height=1,
                width=self.bar_width,
                fill_opacity=1,
            )
            bar.bottom = axes.x_axis.n2p(x + 1)
            bars.add(bar)
        bars.set_submobject_colors_by_gradient(*self.bar_colors)
        bars.set_stroke(WHITE, 1)

        def update_bars(bars):
            values = [ct.get_value() for ct in count_trackers]
            total = sum(values)
            if total == 0:
                props = [0 for x in range(mod)]
            elif total < 1:
                props = values
            else:
                props = [value / total for value in values]

            for bar, prop in zip(bars, props):
                bar.set_height(
                    max(
                        1e-5,
                        100 * prop * axes.y_axis.unit_size,
                    ),
                    stretch=True
                )
                # bar.set_height(1)
                bar.move_to(bar.bottom, DOWN)

        bars.add_updater(update_bars)

        self.add(count_trackers)
        self.add(bars)

        self.bars = bars
        self.count_trackers = count_trackers

    def bucket_primes(self):
        bars = self.bars
        count_trackers = self.count_trackers

        max_n = self.max_n
        n_to_animate = self.n_to_animate
        n_to_show = self.n_to_show
        mod = self.mod

        primes = VGroup(*[
            Integer(prime).scale(2).to_edge(UP, buff=LARGE_BUFF)
            for prime in read_in_primes(max_n)
        ])

        arrow = Arrow(ORIGIN, DOWN)
        x_labels = self.axes.x_labels
        rects = VGroup(*map(SurroundingRectangle, x_labels))
        rects.set_color(RED)

        self.play(FadeIn(primes[0]))
        for i, p, np in zip(it.count(), primes[:n_to_show], primes[1:]):
            d = int(p.get_value()) % mod
            self.add(rects[d])
            if i < n_to_animate:
                self.play(
                    p.scale, 0.5,
                    p.move_to, bars[d].get_top(),
                    p.set_opacity, 0,
                    FadeIn(np),
                    count_trackers[d].increment_value, 1,
                )
                self.remove(p)
            else:
                arrow.next_to(bars[d], UP)
                self.add(arrow)
                self.add(p)
                count_trackers[d].increment_value(1)
                self.wait(0.1)
                self.remove(p)
            self.remove(rects[d])

    #
    def modify_x_labels(self, labels):
        pass


class PhraseDirichletsTheoremFor10(TeacherStudentsScene):
    def construct(self):
        expression = TexMobject(
            "\\lim_{x \\to \\infty}",
            "\\left(",
            "{\\text{\\# of primes $p$ where $p \\le x$} \\text{ and $p \\equiv 1$ mod 10}",
            "\\over",
            "\\text{\\# of primes $p$ where $p \\le x$}}",
            "\\right)",
            "=",
            "\\frac{1}{4}",
        )
        lim, lp, num, over, denom, rp, eq, fourth = expression
        expression.shift(UP)

        denom.save_state()
        denom.move_to(self.hold_up_spot, DOWN)
        denom.shift_onto_screen()

        num[len(denom):].set_color(YELLOW)

        x_example = VGroup(
            TextMobject("Think, for example, $x = $"),
            Integer(int(1e6)),
        )
        x_example.arrange(RIGHT)
        x_example.scale(1.5)
        x_example.to_edge(UP)

        #
        teacher = self.teacher
        students = self.students
        self.play(
            FadeInFromDown(denom),
            teacher.change, "raise_right_hand",
            self.get_student_changes(*["pondering"] * 3),
        )
        self.wait()
        self.play(FadeInFromDown(x_example))
        self.wait()
        self.play(
            Restore(denom),
            teacher.change, "thinking",
        )
        self.play(
            TransformFromCopy(denom, num[:len(denom)]),
            Write(over),
        )
        self.play(
            Write(num[len(denom):]),
            students[0].change, "confused",
            students[2].change, "erm",
        )
        self.wait(2)
        self.play(
            Write(lp),
            Write(rp),
            Write(eq),
        )
        self.play(FadeInFrom(fourth, LEFT))
        self.play(FadeInFrom(lim, RIGHT))
        self.play(
            ChangeDecimalToValue(
                x_example[1], int(1e7),
                run_time=8,
                rate_func=linear,
            ),
            VFadeOut(x_example, run_time=8),
            self.get_student_changes(*["thinking"] * 3),
            Blink(
                teacher,
                run_time=4,
                rate_func=squish_rate_func(there_and_back, 0.65, 0.7)
            ),
        )


class InsertNewResidueClasses(Scene):
    def construct(self):
        nums = VGroup(*map(Integer, [3, 7, 9]))
        colors = [GREEN, TEAL, BLUE]
        for num, color in zip(nums, colors):
            num.set_color(color)
            num.add_background_rectangle(buff=SMALL_BUFF, opacity=1)
            self.play(FadeInFrom(num, UP))
            self.wait()


class BucketPrimesBy44(BucketPrimesByLastDigit):
    CONFIG = {
        "mod": 44,
        "n_to_animate": 5,
        "x_label_scale_factor": 0.5,
        "x_axis_label": "r mod 44",
        "bar_width": 0.1,
    }

    def modify_x_labels(self, labels):
        labels[::2].set_opacity(0)


class BucketPrimesBy9(BucketPrimesByLastDigit):
    CONFIG = {
        "mod": 9,
        "n_to_animate": 5,
        "x_label_scale_factor": 1,
        "x_axis_label": "r mod 9",
        "bar_width": 1,
    }

    def modify_x_labels(self, labels):
        pass


class DirichletIn1837(MovingCameraScene):
    def construct(self):
        # Add timeline
        dates = list(range(1780, 2030, 10))
        timeline = NumberLine(
            x_min=1700,
            x_max=2020,
            tick_frequency=1,
            numbers_with_elongated_ticks=dates,
            unit_size=0.2,
            stroke_color=GREY,
            stroke_width=2,
        )
        timeline.add_numbers(
            *dates,
            number_config={"group_with_commas": False},
        )
        timeline.numbers.shift(SMALL_BUFF * DOWN)
        timeline.to_edge(RIGHT)

        # Special dates
        d_arrow, rh_arrow, pnt_arrow = arrows = VGroup(*[
            Vector(DOWN).next_to(timeline.n2p(date), UP)
            for date in [1837, 1859, 1896]
        ])
        d_label, rh_label, pnt_label = labels = VGroup(*[
            TextMobject(text).next_to(arrow, UP)
            for arrow, text in zip(arrows, [
                "Dirichlet's\\\\theorem\\\\1837",
                "Riemann\\\\hypothesis\\\\1859",
                "Prime number\\\\theorem\\\\1896",
            ])
        ])

        # Back in time
        frame = self.camera_frame
        self.add(timeline, arrows, labels)
        self.play(
            frame.move_to, timeline.n2p(1837),
            run_time=4,
        )
        self.wait()

        # Show picture
        image = ImageMobject("Dirichlet")
        image.set_height(3)
        image.next_to(d_label, LEFT)
        self.play(FadeInFrom(image, RIGHT))
        self.wait()

        # Flash
        self.play(
            Flash(
                d_label.get_center(),
                num_lines=12,
                line_length=0.25,
                flash_radius=1.5,
                line_stroke_width=3,
                lag_ratio=0.05,
            )
        )
        self.wait()

        # Transition title
        title, underline = self.get_title_and_underline()
        n = len(title[0])
        self.play(
            ReplacementTransform(d_label[0][:n], title[0][:n]),
            FadeOut(d_label[0][n:]),
            LaggedStartMap(
                FadeOutAndShiftDown, Group(
                    image, d_arrow,
                    rh_label, rh_arrow,
                    pnt_label, pnt_arrow,
                    *timeline,
                )
            ),
        )
        self.play(ShowCreation(underline))
        self.wait()

    def get_title_and_underline(self):
        frame = self.camera_frame
        title = TextMobject("Dirichlet's theorem")
        title.scale(1.5)
        title.next_to(frame.get_top(), DOWN, buff=MED_LARGE_BUFF)
        underline = Line()
        underline.match_width(title)
        underline.next_to(title, DOWN, SMALL_BUFF)
        return title, underline


class PhraseDirichletsTheorem(DirichletIn1837):
    def construct(self):
        self.add(*self.get_title_and_underline())

        # Copy-pasted, which isn't great
        expression = TexMobject(
            "\\lim_{x \\to \\infty}",
            "\\left(",
            "{\\text{\\# of primes $p$ where $p \\le x$} \\text{ and $p \\equiv 1$ mod 10}",
            "\\over",
            "\\text{\\# of primes $p$ where $p \\le x$}}",
            "\\right)",
            "=",
            "\\frac{1}{4}",
        )
        lim, lp, num, over, denom, rp, eq, fourth = expression
        expression.shift(1.5 * UP)
        expression.to_edge(LEFT, MED_SMALL_BUFF)
        num[len(denom):].set_color(YELLOW)
        #

        # Terms and labels
        ten = num[-2:]
        one = num[-6]
        four = fourth[-1]

        N = TexMobject("N")
        r = TexMobject("r")
        one_over_phi_N = TexMobject("1", "\\over", "\\phi(", "N", ")")

        N.set_color(MAROON_B)
        r.set_color(BLUE)
        one_over_phi_N.set_color_by_tex("N", N.get_color())

        N.move_to(ten, DL)
        r.move_to(one, DOWN)
        one_over_phi_N.move_to(fourth, LEFT)

        N_label = TextMobject("$N$", " is any number")
        N_label.set_color_by_tex("N", N.get_color())
        N_label.next_to(expression, DOWN, LARGE_BUFF)

        r_label = TextMobject("$r$", " is coprime to ", "$N$")
        r_label[0].set_color(r.get_color())
        r_label[2].set_color(N.get_color())
        r_label.next_to(N_label, DOWN, MED_LARGE_BUFF)

        phi_N_label = TexMobject(
            "\\phi({10}) = ",
            "\\#\\{1, 3, 7, 9\\} = 4",
            tex_to_color_map={
                "{10}": N.get_color(),
            }
        )
        phi_N_label[-1][2:9:2].set_color(r.get_color())
        phi_N_label.next_to(r_label, DOWN, MED_LARGE_BUFF)
        #

        self.play(
            LaggedStart(*[
                FadeIn(denom),
                ShowCreation(over),
                FadeIn(num),
                Write(VGroup(lp, rp)),
                FadeIn(lim),
                Write(VGroup(eq, fourth)),
            ]),
            run_time=3,
            lag_ratio=0.7,
        )
        self.wait()
        for mob in denom, num:
            self.play(ShowCreationThenFadeAround(mob))
            self.wait()
        self.play(
            FadeInFrom(r, DOWN),
            FadeOutAndShift(one, UP),
        )
        self.play(
            FadeInFrom(N, DOWN),
            FadeOutAndShift(ten, UP),
        )
        self.wait()
        self.play(
            TransformFromCopy(N, N_label[0]),
            FadeIn(N_label[1:], DOWN)
        )
        self.wait()
        self.play(
            FadeIn(r_label[1:-1], DOWN),
            TransformFromCopy(r, r_label[0]),
        )
        self.play(
            TransformFromCopy(N_label[0], r_label[-1]),
        )
        self.wait()

        self.play(
            ShowCreationThenFadeAround(fourth),
        )
        self.play(
            FadeInFrom(one_over_phi_N[2:], LEFT),
            FadeOutAndShift(four, RIGHT),
            ReplacementTransform(fourth[0], one_over_phi_N[0][0]),
            ReplacementTransform(fourth[1], one_over_phi_N[1][0]),
        )
        self.play(
            FadeInFrom(phi_N_label, DOWN)
        )
        self.wait()

        # Fancier version
        new_expression = TexMobject(
            "\\lim_{x \\to \\infty}",
            "\\left(",
            "{\\pi(x; {N}, {r})",
            "\\over",
            "\\pi(x)}",
            "\\right)",
            "=",
            "\\frac{1}{\\phi({N})}",
            tex_to_color_map={
                "{N}": N.get_color(),
                "{r}": r.get_color(),
                "\\pi": WHITE,
            }
        )
        pis = new_expression.get_parts_by_tex("\\pi")

        randy = Randolph(height=2)
        randy.next_to(new_expression, LEFT, buff=LARGE_BUFF)
        randy.shift(0.75 * DOWN)

        new_expression.next_to(expression, DOWN, LARGE_BUFF)
        ne_rect = SurroundingRectangle(new_expression, color=BLUE)

        label_group = VGroup(N_label, r_label)
        label_group.generate_target()
        label_group.target.arrange(RIGHT, buff=LARGE_BUFF)
        label_group.target.next_to(new_expression, DOWN, buff=LARGE_BUFF)

        self.play(
            FadeIn(randy),
        )
        self.play(
            randy.change, "hooray", expression
        )
        self.play(Blink(randy))
        self.wait()
        self.play(
            FadeIn(new_expression),
            MoveToTarget(label_group),
            phi_N_label.to_edge, DOWN, MED_LARGE_BUFF,
            randy.change, "horrified", new_expression,
        )
        self.play(ShowCreation(ne_rect))
        self.play(randy.change, "confused")
        self.play(Blink(randy))
        self.wait()
        self.play(
            LaggedStartMap(
                ShowCreationThenFadeAround, pis,
            ),
            randy.change, "angry", new_expression
        )
        self.wait()
        self.play(Blink(randy))
        self.wait()


class MoreModestDirichlet(Scene):
    def construct(self):
        ed = TextMobject(
            "Each (coprime) residue class ",
            "is equally dense with ",
            "primes."
        )
        inf = TextMobject(
            "Each (coprime) residue class ",
            "has infinitely many ",
            "primes."
        )
        ed[1].set_color(BLUE)
        inf[1].set_color(GREEN)

        for mob in [*ed, *inf]:
            mob.save_state()

        cross = Cross(ed[1])
        c_group = VGroup(ed[1], cross)

        self.add(ed)
        self.wait()
        self.play(ShowCreation(cross))
        self.play(
            c_group.shift, DOWN,
            c_group.set_opacity, 0.5,
            ReplacementTransform(ed[::2], inf[::2]),
            FadeIn(inf[1])
        )
        self.wait()
        self.remove(*inf)
        self.play(
            inf[1].shift, UP,
            Restore(ed[0]),
            Restore(ed[1]),
            Restore(ed[2]),
            FadeOut(cross),
        )
        self.wait()


class TalkAboutProof(TeacherStudentsScene):
    def construct(self):
        teacher = self.teacher
        students = self.students

        # Ask question
        self.student_says(
            "So how'd he\\\\prove it?",
            student_index=0,
        )
        bubble = students[0].bubble
        students[0].bubble = None
        self.play(
            teacher.change, "hesitant",
            students[1].change, "happy",
            students[2].change, "happy",
        )
        self.wait()
        self.teacher_says(
            "...er...it's a\\\\bit complicated",
            target_mode="guilty",
        )
        self.change_all_student_modes(
            "tired",
            look_at_arg=teacher.bubble,
            lag_ratio=0.1,
        )
        self.play(
            FadeOut(bubble),
            FadeOut(bubble.content),
        )
        self.wait(3)

        # Bring up complex analysis
        ca = TextMobject("Complex ", "Analysis")
        ca.move_to(self.hold_up_spot, DOWN)

        self.play(
            teacher.change, "raise_right_hand",
            FadeInFromDown(ca),
            FadeOut(teacher.bubble),
            FadeOut(teacher.bubble.content),
            self.get_student_changes(*["pondering"] * 3),
        )
        self.wait()
        self.play(
            ca.scale, 2,
            ca.center,
            ca.to_edge, UP,
            teacher.change, "happy",
        )
        self.play(ca[1].set_color, GREEN)
        self.wait(2)
        self.play(ca[0].set_color, YELLOW)
        self.wait(2)
        self.change_all_student_modes(
            "confused", look_at_arg=ca,
        )
        self.wait(4)


class HighlightTwinPrimes(Scene):
    def construct(self):
        self.add_paper_titles()
        self.show_twin_primes()

    def add_paper_titles(self):
        gpy = TextMobject(
            "Goldston, Pintz, Yildirim\\\\",
            "2005",
        )
        zhang = TextMobject("Zhang\\\\2014")

        gpy.move_to(FRAME_WIDTH * LEFT / 4)
        gpy.to_edge(UP)
        zhang.move_to(FRAME_WIDTH * RIGHT / 4)
        zhang.to_edge(UP)

        self.play(LaggedStartMap(
            FadeInFromDown, VGroup(gpy, zhang),
            lag_ratio=0.3,
        ))

    def show_twin_primes(self):
        max_x = 300
        line = NumberLine(
            x_min=0,
            x_max=max_x,
            unit_size=0.5,
            numbers_with_elongated_ticks=range(10, max_x, 10),
        )
        line.move_to(2.5 * DOWN + 7 * LEFT, LEFT)
        line.add_numbers(*range(10, max_x, 10))

        primes = read_in_primes(max_x)
        prime_mobs = VGroup(*[
            Integer(p).next_to(line.n2p(p), UP)
            for p in primes
        ])
        dots = VGroup(*[Dot(line.n2p(p)) for p in primes])

        arcs = VGroup()
        for pm, npm in zip(prime_mobs, prime_mobs[1:]):
            p = pm.get_value()
            np = npm.get_value()
            if np - p == 2:
                angle = 30 * DEGREES
                arc = Arc(
                    start_angle=angle,
                    angle=PI - 2 * angle,
                    color=RED,
                )
                arc.set_width(
                    get_norm(npm.get_center() - pm.get_center())
                )
                arc.next_to(VGroup(pm, npm), UP, SMALL_BUFF)
                arcs.add(arc)

        dots.set_color(TEAL)
        prime_mobs.set_color(TEAL)

        line.add(dots)

        self.play(
            FadeIn(line, lag_ratio=0.9),
            LaggedStartMap(FadeInFromDown, prime_mobs),
            run_time=2,
        )
        line.add(prime_mobs)
        self.wait()

        self.play(FadeIn(arcs))
        self.play(
            line.shift, 100 * LEFT,
            arcs.shift, 100 * LEFT,
            run_time=20,
            rate_func=lambda t: smooth(t, 5)
        )
        self.wait()


class RandomToImportant(PiCreatureScene):
    CONFIG = {
        "default_pi_creature_kwargs": {
            "color": GREY_BROWN,
        },
        "camera_config": {
            "background_color": DARKER_GREY,
        }
    }

    def construct(self):
        morty = self.pi_creature
        morty.center().to_edge(DOWN)

        left_comment = TextMobject("Arbitrary question")
        left_comment.to_edge(UP)
        left_comment.shift(3.5 * LEFT)

        right_comment = TextMobject("Deep fact")
        right_comment.to_edge(UP)
        right_comment.shift(3.5 * RIGHT)

        arrow = Arrow(
            left_comment.get_right(),
            right_comment.get_left(),
            buff=0.5,
        )

        self.play(
            morty.change, "raise_left_hand", left_comment,
            FadeInFromDown(left_comment)
        )
        self.wait(2)
        self.play(
            morty.change, "raise_right_hand", right_comment,
            FadeInFromDown(right_comment)
        )
        self.play(
            ShowCreation(arrow),
            morty.look_at, right_comment,
        )
        self.wait(2)


class RandomWalkOfTopics(Scene):
    CONFIG = {
        "n_dots": 30,
        "n_edge_range": [2, 4],
        "super_dot_n_edges": 20,
        "isolated_threashold": 0.5,
    }

    def construct(self):
        self.setup_network()
        self.define_important()
        self.perform_walk()

    def setup_network(self):
        n_dots = self.n_dots
        dots = VGroup()

        while len(dots) < n_dots:
            point = np.random.uniform(-1, 1, size=3)
            point[2] = 0
            point[0] *= 7
            point[1] *= 3
            isolated = True
            for dot in dots:
                if get_norm(dot.get_center() - point) < self.isolated_threashold:
                    isolated = False
            if not isolated:
                continue
            dot = Dot(point)
            dot.edges = VGroup()
            dot.neighbors = VGroup()
            dots.add(dot)
        super_dot = dots[len(dots) // 2]

        all_edges = VGroup()

        def add_edge(d1, d2):
            if d1 is d2:
                return
            edge = Line(
                d1.get_center(), d2.get_center(),
                buff=d1.get_width() / 2
            )
            d1.edges.add(edge)
            d2.edges.add(edge)
            d1.neighbors.add(d2)
            d2.neighbors.add(d1)
            all_edges.add(edge)

        for dot in dots:
            # others = list(dots[i + 1:])
            others = [d for d in dots if d is not dot]
            others.sort(key=lambda d: get_norm(d.get_center() - dot.get_center()))
            n_edges = np.random.randint(*self.n_edge_range)
            for other in others[:n_edges]:
                if dot in other.neighbors:
                    continue
                add_edge(dot, other)

        for dot in dots:
            if len(super_dot.neighbors) > self.super_dot_n_edges:
                break
            elif dot in super_dot.neighbors:
                continue
            add_edge(super_dot, dot)

        dots.sort(lambda p: p[0])

        all_edges.set_stroke(WHITE, 2)
        dots.set_fill(LIGHT_GREY, 1)

        VGroup(dots, all_edges).to_edge(DOWN, buff=MED_SMALL_BUFF)

        self.dots = dots
        self.edges = all_edges
        self.super_dot = super_dot

    def define_important(self):
        sd = self.super_dot
        dots = self.dots
        edges = self.edges

        sd.set_color(RED)
        for mob in [*dots, *edges]:
            mob.save_state()
            mob.set_opacity(0)

        sd.set_opacity(1)
        sd.edges.set_opacity(1)
        sd.neighbors.set_opacity(1)

        # angles = np.arange(0, TAU, TAU / len(sd.neighbors))
        # center = 0.5 * DOWN
        # sd.move_to(center)
        # for dot, edge, angle in zip(sd.neighbors, sd.edges, angles):
        #     dot.move_to(center + rotate_vector(2.5 * RIGHT, angle))
        #     if edge.get_length() > 0:
        #         edge.put_start_and_end_on(
        #             sd.get_center(),
        #             dot.get_center()
        #         )
        #     rad = dot.get_width() / 2
        #     llen = edge.get_length()
        #     edge.scale((llen - 2 * rad) / llen)

        title = VGroup(
            TextMobject("Important"),
            TexMobject("\\Leftrightarrow"),
            TextMobject("Many connections"),
        )
        title.scale(1.5)
        title.arrange(RIGHT, buff=MED_LARGE_BUFF)
        title.to_edge(UP)

        arrow_words = TextMobject("(in my view)")
        arrow_words.set_width(2 * title[1].get_width())
        arrow_words.next_to(title[1], UP, SMALL_BUFF)

        title[0].save_state()
        title[0].set_x(0)

        self.add(title[0])
        self.play(
            FadeInFromLarge(sd),
            title[0].set_color, RED,
        )
        title[0].saved_state.set_color(RED)
        self.play(
            Restore(title[0]),
            GrowFromCenter(title[1]),
            FadeIn(arrow_words),
            FadeInFrom(title[2], LEFT),
            LaggedStartMap(
                ShowCreation, sd.edges,
                run_time=3,
            ),
            LaggedStartMap(
                GrowFromPoint, sd.neighbors,
                lambda m: (m, sd.get_center()),
                run_time=3,
            ),
        )
        self.wait()
        self.play(*map(Restore, [*dots, *edges]))
        self.wait()

    def perform_walk(self):
        # dots = self.dots
        # edges = self.edges
        sd = self.super_dot

        path = VGroup(sd)
        random.seed(1)
        for x in range(3):
            new_choice = None
            while new_choice is None or new_choice in path:
                new_choice = random.choice(path[0].neighbors)
            path.add_to_back(new_choice)

        for d1, d2 in zip(path, path[1:]):
            self.play(Flash(d1.get_center()))
            self.play(
                ShowCreationThenDestruction(
                    Line(
                        d1.get_center(),
                        d2.get_center(),
                        color=YELLOW,
                    )
                )
            )

        self.play(Flash(sd))
        self.play(LaggedStart(*[
            ApplyMethod(
                edge.set_stroke, YELLOW, 5,
                rate_func=there_and_back,
            )
            for edge in sd.edges
        ]))
        self.wait()


class DeadEnds(RandomWalkOfTopics):
    CONFIG = {
        "n_dots": 20,
        "n_edge_range": [2, 4],
        "super_dot_n_edges": 2,
        "random_seed": 1,
    }

    def construct(self):
        self.setup_network()
        dots = self.dots
        edges = self.edges

        self.add(dots, edges)

        VGroup(
            edges[3],
            edges[4],
            edges[7],
            edges[10],
            edges[12],
            edges[15],
            edges[27],
            edges[30],
            edges[33],
        ).set_opacity(0)

        # for i, edge in enumerate(edges):
        #     self.add(Integer(i).move_to(edge))


class Rediscovery(Scene):
    def construct(self):
        randy = Randolph()
        randy.to_edge(DOWN)
        randy.shift(2 * RIGHT)

        lightbulb = Lightbulb()
        lightbulb.set_stroke(width=4)
        lightbulb.scale(1.5)
        lightbulb.next_to(randy, UP)

        rings = self.get_rings(
            lightbulb.get_center(),
            max_radius=10.0,
            delta_r=0.1,
        )

        bubble = ThoughtBubble()
        bubble.pin_to(randy)
        # bubble[-1].set_fill(GREEN_SCREEN, 0.5)
        self.play(
            randy.change, "pondering",
            ShowCreation(bubble),
            FadeInFromDown(lightbulb),
        )
        self.add(rings, bubble)
        self.play(
            randy.change, "thinking",
            LaggedStartMap(
                VFadeInThenOut,
                rings,
                lag_ratio=0.002,
                run_time=3,
            )
        )
        self.wait(4)

    def get_rings(self, center, max_radius, delta_r):
        radii = np.arange(0, max_radius, delta_r)
        rings = VGroup(*[
            Annulus(
                inner_radius=r1,
                outer_radius=r2,
                fill_opacity=0.75 * (1 - fdiv(r1, max_radius)),
                fill_color=YELLOW
            )
            for r1, r2 in zip(radii, radii[1:])
        ])
        rings.move_to(center)
        return rings


class BePlayful(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "So be playful!",
            target_mode="hooray",
        )
        self.change_student_modes("thinking", "hooray", "happy")
        self.wait(3)


class SpiralsPatronThanks(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "Juan Benet",
            "Kurt Dicus",
            "Vassili Philippov",
            "Burt Humburg",
            "Matt Russell",
            "Scott Gray",
            "soekul",
            "Tihan Seale",
            "D. Sivakumar",
            "Ali Yahya",
            "Arthur Zey",
            "dave nicponski",
            "Joseph Kelly",
            "Kaustuv DeBiswas",
            "kkm",
            "Lambda AI Hardware",
            "Lukas Biewald",
            "Mark Heising",
            "Nicholas Cahill",
            "Peter Mcinerney",
            "Quantopian",
            "Scott Walter, Ph.D.",
            "Tauba Auerbach",
            "Yana Chernobilsky",
            "Yu Jun",
            "Jordan Scales",
            "Lukas -krtek.net- Novy",
            "Andrew Weir",
            "Britt Selvitelle",
            "Britton Finley",
            "David Gow",
            "J",
            "Jonathan Wilson",
            "Joseph John Cox",
            "Magnus Dahlström",
            "Mattéo Delabre",
            "Randy C. Will",
            "Ryan Atallah",
            "Luc Ritchie",
            "1stViewMaths",
            "Aidan Shenkman",
            "Alex Mijalis",
            "Alexis Olson",
            "Andreas Benjamin Brössel",
            "Andrew Busey",
            "Andrew R. Whalley",
            "Ankalagon",
            "Anthony Turvey",
            "Antoine Bruguier",
            "Antonio Juarez",
            "Arjun Chakroborty",
            "Art Ianuzzi",
            "Austin Goodman",
            "Avi Finkel",
            "Awoo",
            "Azeem Ansar",
            "AZsorcerer",
            "Barry Fam",
            "Bernd Sing",
            "Boris Veselinovich",
            "Bradley Pirtle",
            "Brian Staroselsky",
            "Calvin Lin",
            "Charles Southerland",
            "Charlie N",
            "Chris Connett",
            "Christian Kaiser",
            "Clark Gaebel",
            "Danger Dai",
            "Daniel Herrera C",
            "Daniel Pang",
            "Dave B",
            "Dave Kester",
            "David B. Hill",
            "David Clark",
            "DeathByShrimp",
            "Delton Ding",
            "Dominik Wagner",
            "eaglle",
            "emptymachine",
            "Eric Younge",
            "Ero Carrera",
            "Eryq Ouithaqueue",
            "Federico Lebron",
            "Fernando Via Canel",
            "Frank R. Brown, Jr.",
            "Giovanni Filippi",
            "Hal Hildebrand",
            "Hause Lin",
            "Hitoshi Yamauchi",
            "Ivan Sorokin",
            "j eduardo perez",
            "Jacob Baxter",
            "Jacob Harmon",
            "Jacob Hartmann",
            "Jacob Magnuson",
            "Jameel Syed",
            "James Stevenson",
            "Jason Hise",
            "Jeff Linse",
            "Jeff Straathof",
            "John C. Vesey",
            "John Griffith",
            "John Haley",
            "John V Wertheim",
            "Jonathan Eppele",
            "Josh Kinnear",
            "Joshua Claeys",
            "Kai-Siang Ang",
            "Kanan Gill",
            "Kartik Cating-Subramanian",
            "L0j1k",
            "Lee Redden",
            "Linh Tran",
            "Ludwig Schubert",
            "Magister Mugit",
            "Mark B Bahu",
            "Mark Mann",
            "Martin Price",
            "Mathias Jansson",
            "Matt Langford",
            "Matt Roveto",
            "Matthew Bouchard",
            "Matthew Cocke",
            "Michael Faust",
            "Michael Hardel",
            "Michele Donadoni",
            "Mirik Gogri",
            "Mustafa Mahdi",
            "Márton Vaitkus",
            "Nero Li",
            "Nikita Lesnikov",
            "Omar Zrien",
            "Owen Campbell-Moore",
            "Patrick Lucas",
            "Pedro Igor Salomão Budib",
            "Peter Ehrnstrom",
            "RedAgent14",
            "rehmi post",
            "Rex Godby",
            "Richard Barthel",
            "Ripta Pasay",
            "Rish Kundalia",
            "Roman Sergeychik",
            "Roobie",
            "Ryan Williams",
            "Sebastian Garcia",
            "Solara570",
            "Steven Siddals",
            "Stevie Metke",
            "Suthen Thomas",
            "Tal Einav",
            "Ted Suzman",
            "The Responsible One",
            "Thomas Tarler",
            "Tianyu Ge",
            "Tom Fleming",
            "Tyler VanValkenburg",
            "Valeriy Skobelev",
            "Veritasium",
            "Vinicius Reis",
            "Xuanji Li",
            "Yavor Ivanov",
            "YinYangBalance.Asia",
        ]
    }


class Thumbnail(SpiralScene):
    CONFIG = {
        "max_N": 8000,
        "just_show": True,
    }

    def construct(self):
        self.add_dots()
        if not self.just_show:
            pass

    def add_dots(self):
        self.set_scale(scale=1e3)

        p_spiral = self.get_prime_p_spiral(self.max_N)
        dots = VGroup(*[
            Dot(
                point,
                radius=interpolate(0.01, 0.07, min(0.5 * get_norm(point), 1)),
                fill_color=TEAL,
                # fill_opacity=interpolate(0.5, 1, min(get_norm(point), 1))
            )
            for point in p_spiral.points
        ])
        dots.set_fill([TEAL_E, TEAL_A])
        dots.set_stroke(BLACK, 1)

        label = TextMobject(
            "($p$, $p$) for all primes $p$,\\\\",
            "in polar coordinates",
            tex_to_color_map={
                "$p$": YELLOW,
            },
        )

        label.scale(2)
        label.set_stroke(BLACK, 10, background=True)
        label.add_background_rectangle_to_submobjects()
        label.to_corner(DL, MED_LARGE_BUFF)

        self.add(dots)
        # self.add(label)

        self.dots = dots
