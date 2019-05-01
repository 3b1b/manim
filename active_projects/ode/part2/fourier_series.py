from big_ol_pile_of_manim_imports import *
# import scipy


class FourierCirclesScene(Scene):
    CONFIG = {
        "n_circles": 10,
        "big_radius": 2,
        "colors": [
            BLUE_D,
            BLUE_C,
            BLUE_E,
            GREY_BROWN,
        ],
        "circle_style": {
            "stroke_width": 2,
        },
        "arrow_config": {
            "buff": 0,
            "max_tip_length_to_length_ratio": 0.35,
            "tip_length": 0.15,
            "max_stroke_width_to_length_ratio": 10,
            "stroke_width": 2,
        },
        "use_vectors": True,
        "base_frequency": 1,
        "slow_factor": 0.25,
        "center_point": ORIGIN,
        "parametric_function_step_size": 0.001,
    }

    def setup(self):
        self.slow_factor_tracker = ValueTracker(
            self.slow_factor
        )

    def get_slow_factor(self):
        return self.slow_factor_tracker.get_value()

    #
    def get_freqs(self):
        n = self.n_circles
        all_freqs = list(range(n // 2, -n // 2, -1))
        all_freqs.sort(key=abs)
        return all_freqs

    def get_coefficients(self):
        return [complex(0) for x in range(self.n_circles)]

    def get_color_iterator(self):
        return it.cycle(self.colors)

    def get_circles(self, freqs=None, coefficients=None):
        circles = VGroup()
        color_iterator = self.get_color_iterator()
        self.center_tracker = VectorizedPoint(self.center_point)

        if freqs is None:
            freqs = self.get_freqs()
        if coefficients is None:
            coefficients = self.get_coefficients()

        last_circle = None
        for freq, coefficient in zip(freqs, coefficients):
            if last_circle:
                center_func = last_circle.get_start
            else:
                center_func = self.center_tracker.get_location
            circle = self.get_circle(
                coefficient=coefficient,
                freq=freq,
                color=next(color_iterator),
                center_func=center_func,
            )
            circles.add(circle)
            last_circle = circle
        return circles

    def get_circle(self, coefficient, freq, color, center_func):
        radius = abs(coefficient)
        phase = np.log(coefficient).imag
        circle = Circle(
            radius=radius,
            color=color,
            **self.circle_style,
        )
        line_points = (
            circle.get_center(),
            circle.get_start(),
        )
        if self.use_vectors:
            circle.radial_line = Arrow(
                *line_points,
                **self.arrow_config,
            )
        else:
            circle.radial_line = Line(
                *line_points,
                color=WHITE,
                **self.circle_style,
            )
        circle.add(circle.radial_line)
        circle.freq = freq
        circle.phase = phase
        circle.rotate(phase)
        circle.coefficient = coefficient
        circle.center_func = center_func
        circle.add_updater(self.update_circle)
        return circle

    def update_circle(self, circle, dt):
        circle.rotate(
            self.get_slow_factor() * circle.freq * dt * TAU
        )
        circle.move_to(circle.center_func())
        return circle

    def get_rotating_vectors(self, circles):
        return VGroup(*[
            self.get_rotating_vector(circle)
            for circle in circles
        ])

    def get_rotating_vector(self, circle):
        vector = Vector(RIGHT, color=WHITE)
        vector.add_updater(lambda v, dt: v.put_start_and_end_on(
            circle.get_center(),
            circle.get_start(),
        ))
        circle.vector = vector
        return vector

    def get_circle_end_path(self, circles, color=YELLOW):
        coefs = [c.coefficient for c in circles]
        freqs = [c.freq for c in circles]
        center = circles[0].get_center()

        path = ParametricFunction(
            lambda t: center + reduce(op.add, [
                complex_to_R3(
                    coef * np.exp(TAU * 1j * freq * t)
                )
                for coef, freq in zip(coefs, freqs)
            ]),
            t_min=0,
            t_max=1,
            color=color,
            step_size=self.parametric_function_step_size,
        )
        return path

    # TODO, this should be a general animated mobect
    def get_drawn_path(self, circles, stroke_width=2, **kwargs):
        path = self.get_circle_end_path(circles, **kwargs)
        broken_path = CurvesAsSubmobjects(path)
        broken_path.curr_time = 0

        def update_path(path, dt):
            alpha = path.curr_time * self.get_slow_factor()
            n_curves = len(path)
            for a, sp in zip(np.linspace(0, 1, n_curves), path):
                b = alpha - a
                if b < 0:
                    width = 0
                else:
                    width = stroke_width * (1 - (b % 1))
                sp.set_stroke(width=width)
            path.curr_time += dt
            return path

        broken_path.set_color(YELLOW)
        broken_path.add_updater(update_path)
        return broken_path

    def get_y_component_wave(self,
                             circles,
                             left_x=1,
                             color=PINK,
                             n_copies=2,
                             right_shift_rate=5):
        path = self.get_circle_end_path(circles)
        wave = ParametricFunction(
            lambda t: op.add(
                right_shift_rate * t * LEFT,
                path.function(t)[1] * UP
            ),
            t_min=path.t_min,
            t_max=path.t_max,
            color=color,
        )
        wave_copies = VGroup(*[
            wave.copy()
            for x in range(n_copies)
        ])
        wave_copies.arrange(RIGHT, buff=0)
        top_point = wave_copies.get_top()
        wave.creation = ShowCreation(
            wave,
            run_time=(1 / self.get_slow_factor()),
            rate_func=linear,
        )
        cycle_animation(wave.creation)
        wave.add_updater(lambda m: m.shift(
            (m.get_left()[0] - left_x) * LEFT
        ))

        def update_wave_copies(wcs):
            index = int(
                wave.creation.total_time * self.get_slow_factor()
            )
            wcs[:index].match_style(wave)
            wcs[index:].set_stroke(width=0)
            wcs.next_to(wave, RIGHT, buff=0)
            wcs.align_to(top_point, UP)
        wave_copies.add_updater(update_wave_copies)

        return VGroup(wave, wave_copies)

    def get_wave_y_line(self, circles, wave):
        return DashedLine(
            circles[-1].get_start(),
            wave[0].get_end(),
            stroke_width=1,
            dash_length=DEFAULT_DASH_LENGTH * 0.5,
        )

    # Computing Fourier series
    def get_coefficients_of_path(self, path, n_samples=10000, freqs=None):
        if freqs is None:
            freqs = self.get_freqs()
        dt = 1 / n_samples
        ts = np.arange(0, 1, dt)
        samples = np.array([
            path.point_from_proportion(t)
            for t in ts
        ])
        samples -= self.center_point
        complex_samples = samples[:, 0] + 1j * samples[:, 1]

        result = []
        for freq in freqs:
            riemann_sum = np.array([
                np.exp(-TAU * 1j * freq * t) * cs
                for t, cs in zip(ts, complex_samples)
            ]).sum() * dt
            result.append(riemann_sum)

        return result


class FourierSeriesIntroBackground4(FourierCirclesScene):
    CONFIG = {
        "n_circles": 4,
        "center_point": 4 * LEFT,
        "run_time": 30,
        "big_radius": 1.5,
    }

    def construct(self):
        circles = self.get_circles()
        path = self.get_drawn_path(circles)
        wave = self.get_y_component_wave(circles)
        h_line = always_redraw(
            lambda: self.get_wave_y_line(circles, wave)
        )

        # Why?
        circles.update(-1 / self.camera.frame_rate)
        #
        self.add(circles, path, wave, h_line)
        self.wait(self.run_time)

    def get_ks(self):
        return np.arange(1, 2 * self.n_circles + 1, 2)

    def get_freqs(self):
        return self.base_frequency * self.get_ks()

    def get_coefficients(self):
        return self.big_radius / self.get_ks()


class FourierSeriesIntroBackground8(FourierSeriesIntroBackground4):
    CONFIG = {
        "n_circles": 8,
    }


class FourierSeriesIntroBackground12(FourierSeriesIntroBackground4):
    CONFIG = {
        "n_circles": 12,
    }


class FourierSeriesIntroBackground20(FourierSeriesIntroBackground4):
    CONFIG = {
        "n_circles": 20,
    }


class FourierOfPiSymbol(FourierCirclesScene):
    CONFIG = {
        "n_circles": 50,
        "center_point": ORIGIN,
        "slow_factor": 0.1,
        "run_time": 30,
        "tex": "\\pi",
        "start_drawn": False,
    }

    def construct(self):
        path = self.get_path()
        coefs = self.get_coefficients_of_path(path)

        circles = self.get_circles(coefficients=coefs)
        for k, circle in zip(it.count(1), circles):
            circle.set_stroke(width=max(
                1 / np.sqrt(k),
                1,
            ))

        # approx_path = self.get_circle_end_path(circles)
        drawn_path = self.get_drawn_path(circles)
        if self.start_drawn:
            drawn_path.curr_time = 1 / self.slow_factor

        self.add(path)
        self.add(circles)
        self.add(drawn_path)
        self.wait(self.run_time)

    def get_path(self):
        tex_mob = TexMobject(self.tex)
        tex_mob.set_height(6)
        path = tex_mob.family_members_with_points()[0]
        path.set_fill(opacity=0)
        path.set_stroke(WHITE, 1)
        return path


class FourierOfPiSymbol5(FourierOfPiSymbol):
    CONFIG = {
        "n_circles": 5,
        "run_time": 10,
    }


class FourierOfTrebleClef(FourierOfPiSymbol):
    CONFIG = {
        "n_circles": 100,
        "run_time": 10,
        "start_drawn": True,
        "file_name": "TrebleClef",
        "height": 7.5,
    }

    def get_shape(self):
        shape = SVGMobject(self.file_name)
        return shape

    def get_path(self):
        shape = self.get_shape()
        path = shape.family_members_with_points()[0]
        path.set_height(self.height)
        path.set_fill(opacity=0)
        path.set_stroke(WHITE, 0)
        return path


class FourierOfIP(FourierOfTrebleClef):
    CONFIG = {
        "file_name": "IP_logo2",
        "height": 6,
        "n_circles": 100,
    }

    # def construct(self):
    #     path = self.get_path()
    #     self.add(path)

    def get_shape(self):
        shape = SVGMobject(self.file_name)
        return shape

    def get_path(self):
        shape = self.get_shape()
        path = shape.family_members_with_points()[0]
        path.add_line_to(path.get_start())
        # path.make_smooth()

        path.set_height(self.height)
        path.set_fill(opacity=0)
        path.set_stroke(WHITE, 0)
        return path


class FourierOfEighthNote(FourierOfTrebleClef):
    CONFIG = {
        "file_name": "EighthNote"
    }


class FourierOfN(FourierOfTrebleClef):
    CONFIG = {
        "height": 6,
        "n_circles": 1000,
    }

    def get_shape(self):
        return TexMobject("N")


class FourierNailAndGear(FourierOfTrebleClef):
    CONFIG = {
        "height": 6,
        "n_circles": 200,
        "run_time": 100,
        "slow_factor": 0.01,
        "parametric_function_step_size": 0.0001,
        "arrow_config": {
            "tip_length": 0.1,
            "stroke_width": 2,
        }
    }

    def get_shape(self):
        shape = SVGMobject("Nail_And_Gear")[1]
        return shape


class FourierBatman(FourierOfTrebleClef):
    CONFIG = {
        "height": 4,
        "n_circles": 100,
        "run_time": 10,
        "arrow_config": {
            "tip_length": 0.1,
            "stroke_width": 2,
        }
    }

    def get_shape(self):
        shape = SVGMobject("BatmanLogo")[1]
        return shape


class FourierHeart(FourierOfTrebleClef):
    CONFIG = {
        "height": 4,
        "n_circles": 100,
        "run_time": 10,
        "arrow_config": {
            "tip_length": 0.1,
            "stroke_width": 2,
        }
    }

    def get_shape(self):
        shape = SuitSymbol("hearts")
        return shape

    def get_drawn_path(self, *args, **kwargs):
        kwargs["stroke_width"] = 5
        path = super().get_drawn_path(*args, **kwargs)
        path.set_color(PINK)
        return path


class FourierNDQ(FourierOfTrebleClef):
    CONFIG = {
        "height": 4,
        "n_circles": 1000,
        "run_time": 10,
        "arrow_config": {
            "tip_length": 0.1,
            "stroke_width": 2,
        }
    }

    def get_shape(self):
        path = VMobject()
        shape = TexMobject("Hayley")
        for sp in shape.family_members_with_points():
            path.append_points(sp.points)
        return path


class FourierGoogleG(FourierOfTrebleClef):
    CONFIG = {
        "n_circles": 10,
        "height": 5,
        "g_colors": [
            "#4285F4",
            "#DB4437",
            "#F4B400",
            "#0F9D58",
        ]
    }

    def get_shape(self):
        g = SVGMobject("google_logo")[5]
        g.center()
        self.add(g)
        return g

    def get_drawn_path(self, *args, **kwargs):
        kwargs["stroke_width"] = 7
        path = super().get_drawn_path(*args, **kwargs)

        blue, red, yellow, green = self.g_colors

        path[:250].set_color(blue)
        path[250:333].set_color(green)
        path[333:370].set_color(yellow)
        path[370:755].set_color(red)
        path[755:780].set_color(yellow)
        path[780:860].set_color(green)
        path[860:].set_color(blue)

        return path


class ExplainCircleAnimations(FourierCirclesScene):
    CONFIG = {
        "n_circles": 100,
        "center_point": 2 * DOWN,
        "n_top_circles": 9,
        "path_height": 3,
    }

    def construct(self):
        self.add_path()
        self.add_circles()
        self.wait(8)
        self.organize_circles_in_a_row()
        self.show_frequencies()
        self.show_examples_for_frequencies()
        self.show_as_vectors()
        self.show_vector_sum()
        self.tweak_starting_vectors()

    def add_path(self):
        self.path = self.get_path()
        self.add(self.path)

    def add_circles(self):
        coefs = self.get_coefficients_of_path(self.path)
        self.circles = self.get_circles(coefficients=coefs)

        self.add(self.circles)
        self.drawn_path = self.get_drawn_path(self.circles)
        self.add(self.drawn_path)

    def organize_circles_in_a_row(self):
        circles = self.circles
        top_circles = circles[:self.n_top_circles].copy()

        center_trackers = VGroup()
        for circle in top_circles:
            tracker = VectorizedPoint(circle.center_func())
            circle.center_func = tracker.get_location
            center_trackers.add(tracker)
            tracker.freq = circle.freq
            tracker.circle = circle

        center_trackers.submobjects.sort(
            key=lambda m: m.freq
        )
        center_trackers.generate_target()
        right_buff = 1.45
        center_trackers.target.arrange(RIGHT, buff=right_buff)
        center_trackers.target.to_edge(UP, buff=1.25)

        self.add(top_circles)
        self.play(
            MoveToTarget(center_trackers),
            run_time=2
        )
        self.wait(4)

        self.top_circles = top_circles
        self.center_trackers = center_trackers

    def show_frequencies(self):
        center_trackers = self.center_trackers

        freq_numbers = VGroup()
        for ct in center_trackers:
            number = Integer(ct.freq)
            number.next_to(ct, DOWN, buff=1)
            freq_numbers.add(number)
            ct.circle.number = number

        ld, rd = [
            TexMobject("\\dots")
            for x in range(2)
        ]
        ld.next_to(freq_numbers, LEFT, MED_LARGE_BUFF)
        rd.next_to(freq_numbers, RIGHT, MED_LARGE_BUFF)
        freq_numbers.add_to_back(ld)
        freq_numbers.add(rd)

        freq_word = TextMobject("Frequencies")
        freq_word.scale(1.5)
        freq_word.set_color(YELLOW)
        freq_word.next_to(freq_numbers, DOWN, MED_LARGE_BUFF)

        self.play(
            LaggedStartMap(
                FadeInFromDown, freq_numbers
            )
        )
        self.play(
            Write(freq_word),
            LaggedStartMap(
                ShowCreationThenFadeAround, freq_numbers,
            )
        )
        self.wait(2)

        self.freq_numbers = freq_numbers
        self.freq_word = freq_word

    def show_examples_for_frequencies(self):
        top_circles = self.top_circles
        c1, c2, c3 = [
            list(filter(
                lambda c: c.freq == k,
                top_circles
            ))[0]
            for k in (1, 2, 3)
        ]

        neg_circles = VGroup(*filter(
            lambda c: c.freq < 0,
            top_circles
        ))

        for c in [c1, c2, c3, *neg_circles]:
            c.rect = SurroundingRectangle(c)

        self.play(
            ShowCreation(c2.rect),
            WiggleOutThenIn(c2.number),
        )
        self.wait(2)
        self.play(
            ReplacementTransform(c2.rect, c1.rect),
        )
        self.play(FadeOut(c1.rect))
        self.wait()
        self.play(
            ShowCreation(c3.rect),
            WiggleOutThenIn(c3.number),
        )
        self.play(
            FadeOut(c3.rect),
        )
        self.wait(2)
        self.play(
            LaggedStart(*[
                ShowCreationThenFadeOut(c.rect)
                for c in neg_circles
            ])
        )
        self.wait(3)
        self.play(FadeOut(self.freq_word))

    def show_as_vectors(self):
        top_circles = self.top_circles
        top_vectors = self.get_rotating_vectors(top_circles)
        top_vectors.set_color(WHITE)

        original_circles = top_circles.copy()
        self.play(
            FadeIn(top_vectors),
            top_circles.set_opacity, 0,
        )
        self.wait(3)
        self.play(
            top_circles.match_style, original_circles
        )
        self.remove(top_vectors)

        self.top_vectors = top_vectors

    def show_vector_sum(self):
        trackers = self.center_trackers.copy()
        trackers.sort(
            submob_func=lambda t: abs(t.circle.freq - 0.1)
        )
        plane = self.plane = NumberPlane(
            x_min=-3,
            x_max=3,
            y_min=-2,
            y_max=2,
            axis_config={
                "stroke_color": LIGHT_GREY,
            }
        )
        plane.set_stroke(width=1)
        plane.fade(0.5)
        plane.move_to(self.center_point)

        self.play(
            FadeOut(self.drawn_path),
            FadeOut(self.circles),
            self.slow_factor_tracker.set_value, 0.05,
        )
        self.add(plane, self.path)
        self.play(FadeIn(plane))

        new_circles = VGroup()
        last_tracker = None
        for tracker in trackers:
            if last_tracker:
                tracker.new_location_func = last_tracker.circle.get_start
            else:
                tracker.new_location_func = lambda: self.center_point

            original_circle = tracker.circle
            tracker.circle = original_circle.copy()
            tracker.circle.center_func = tracker.get_location
            new_circles.add(tracker.circle)

            self.add(tracker, tracker.circle)
            start_point = tracker.get_location()
            self.play(
                UpdateFromAlphaFunc(
                    tracker, lambda t, a: t.move_to(
                        interpolate(
                            start_point,
                            tracker.new_location_func(),
                            a,
                        )
                    ),
                    run_time=2
                )
            )
            tracker.add_updater(lambda t: t.move_to(
                t.new_location_func()
            ))
            self.wait(2)
            last_tracker = tracker

        self.wait(3)

        self.clear()
        self.slow_factor_tracker.set_value(0.1)
        self.add(
            self.top_circles,
            self.freq_numbers,
            self.path,
        )
        self.add_circles()
        for tc in self.top_circles:
            for c in self.circles:
                if c.freq == tc.freq:
                    tc.rotate(
                        angle_of_vector(c.get_start() - c.get_center()) -
                        angle_of_vector(tc.get_start() - tc.get_center())
                    )
        self.wait(10)

    def tweak_starting_vectors(self):
        top_circles = self.top_circles
        circles = self.circles
        path = self.path
        drawn_path = self.drawn_path

        new_path = self.get_new_path()
        new_coefs = self.get_coefficients_of_path(new_path)
        new_circles = self.get_circles(coefficients=new_coefs)

        new_top_circles = VGroup()
        new_top_vectors = VGroup()
        for top_circle in top_circles:
            for circle in new_circles:
                if circle.freq == top_circle.freq:
                    new_top_circle = circle.copy()
                    new_top_circle.center_func = top_circle.get_center
                    new_top_vector = self.get_rotating_vector(
                        new_top_circle
                    )
                    new_top_circles.add(new_top_circle)
                    new_top_vectors.add(new_top_vector)

        self.play(
            self.slow_factor_tracker.set_value, 0,
            FadeOut(drawn_path)
        )
        self.wait()
        self.play(
            ReplacementTransform(top_circles, new_top_circles),
            ReplacementTransform(circles, new_circles),
            FadeOut(path),
            run_time=3,
        )
        new_drawn_path = self.get_drawn_path(
            new_circles, stroke_width=4,
        )
        self.add(new_drawn_path)
        self.slow_factor_tracker.set_value(0.1)
        self.wait(20)

    #
    def configure_path(self, path):
        path.set_stroke(WHITE, 1)
        path.set_fill(BLACK, opacity=1)
        path.set_height(self.path_height)
        path.move_to(self.center_point)
        return path

    def get_path(self):
        tex = TexMobject("f")
        path = tex.family_members_with_points()[0]
        self.configure_path(path)
        return path
        # return Square().set_height(3)

    def get_new_path(self):
        shape = SVGMobject("TrebleClef")
        path = shape.family_members_with_points()[0]
        self.configure_path(path)
        path.scale(1.5, about_edge=DOWN)
        return path
