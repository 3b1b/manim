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
        "base_frequency": 1,
        "slow_factor": 0.25,
        "center_point": ORIGIN,
        "parametric_function_step_size": 0.001,
    }

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
        circle.radial_line = Line(
            circle.get_center(),
            circle.get_start(),
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
            self.slow_factor * circle.freq * dt * TAU
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
        vector.add_updater(lambda v: v.put_start_and_end_on(
            *circle.radial_line.get_start_and_end()
        ))
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
    def get_drawn_path(self, circles, **kwargs):
        path = self.get_circle_end_path(circles, **kwargs)
        broken_path = CurvesAsSubmobjects(path)
        broken_path.curr_time = 0

        def update_path(path, dt):
            alpha = path.curr_time * self.slow_factor
            n_curves = len(path)
            for a, sp in zip(np.linspace(0, 1, n_curves), path):
                b = alpha - a
                if b < 0:
                    width = 0
                else:
                    width = 2 * (1 - (b % 1))
                sp.set_stroke(YELLOW, width=width)
            path.curr_time += dt
            return path

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
            run_time=(1 / self.slow_factor),
            rate_func=linear,
        )
        cycle_animation(wave.creation)
        wave.add_updater(lambda m: m.shift(
            (m.get_left()[0] - left_x) * LEFT
        ))

        def update_wave_copies(wcs):
            index = int(
                wave.creation.total_time * self.slow_factor
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
            print(circle.freq, abs(circle.coefficient))

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
    }

    def get_path(self):
        path = SVGMobject("TrebleClef")
        path = path.family_members_with_points()[0]
        path.set_height(7.5)
        path.set_fill(opacity=0)
        path.set_stroke(WHITE, 0)
        return path


class ExplainCircleAnimations(FourierCirclesScene):
    CONFIG = {
        # "n_circles": 100,
        "n_circles": 20,
        "center_point": 2 * DOWN,
        "n_top_circles": 9,
        # "slow_factor": 0.1,
        "path_height": 3,
    }

    def construct(self):
        self.add_path()
        self.add_circles()
        self.organize_circles_in_a_row()
        self.show_frequencies()
        self.show_examples_for_frequencies()
        self.show_as_vectors()
        self.show_vector_sum()
        self.moons_of_moons_of_moons()
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

        self.wait(8)

    def organize_circles_in_a_row(self):
        circles = self.circles
        top_circles = circles[:self.n_top_circles].deepcopy()

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

    def show_as_vectors(self):
        top_circles = self.top_circles
        top_vectors = self.get_rotating_vectors(top_circles)

        self.play(
            top_circles.set_stroke, {"width": 0.5},
            FadeIn(top_vectors),
        )
        self.wait(3)

        self.top_vectors = top_vectors

    def show_vector_sum(self):
        top_circles = self.top_circles
        top_circles = self.top_circles

        self.play(
            FadeOut(self.path),
            FadeOut(self.circles),
        )

    def moons_of_moons_of_moons(self):
        pass

    def tweak_starting_vectors(self):
        pass

    #
    def get_path(self):
        tex = TexMobject("f")
        path = tex.family_members_with_points()[0]
        path.set_stroke(WHITE, 1)
        path.set_fill(opacity=0)
        path.set_height(self.path_height)
        path.move_to(self.center_point)
        return path
        # return Square().set_height(3)
