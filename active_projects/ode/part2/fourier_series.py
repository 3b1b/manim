from big_ol_pile_of_manim_imports import *


class CirclesDrawing(Scene):
    CONFIG = {
        "n_circles": 4,
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
        "base_frequency": 0.25 * TAU,
        "center_point": ORIGIN,
    }

    #
    def get_freqs_and_radii(self):
        raise Exception("Not implemented")

    def get_color_iterator(self):
        return it.cycle(self.colors)

    def get_circles(self):
        circles = VGroup()
        color_iterator = self.get_color_iterator()
        self.center_tracker = VectorizedPoint(self.center_point)
        last_circle = None
        for freq, radius in self.get_freqs_and_radii():
            if last_circle:
                center_func = last_circle.get_start
            else:
                center_func = self.center_tracker.get_location
            circle = self.get_circle(
                radius=radius,
                color=next(color_iterator),
                freq=freq,
                center_func=center_func
            )
            circles.add(circle)
            last_circle = circle
        return circles

    def get_circle(self, radius, color, freq, center_func):
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
        circle.center_func = center_func
        circle.add_updater(self.update_circle)
        return circle

    def update_circle(self, circle, dt):
        circle.rotate(circle.freq * dt)
        circle.move_to(circle.center_func())
        return circle

    def get_circle_end_path(self, circles, color=YELLOW):
        freqs = [c.freq for c in circles]
        radii = [c.radius for c in circles]
        total_time = TAU / self.base_frequency
        center = circles[0].get_center()

        return ParametricFunction(
            lambda t: center + reduce(op.add, [
                radius * rotate_vector(RIGHT, freq * t)
                for freq, radius in zip(freqs, radii)
            ]),
            t_min=0,
            t_max=total_time,
            color=color,
            step_size=0.005,
        )

    # TODO, this should be a general animated mobect
    def get_drawn_path(self, circles, **kwargs):
        path = self.get_circle_end_path(circles, **kwargs)
        total_time = path.t_max
        broken_path = CurvesAsSubmobjects(path)
        broken_path.curr_time = 0

        def update_path(path, dt):
            alpha = (path.curr_time / total_time)
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
                             color=BLUE,
                             n_copies=2,
                             right_shift_rate=1.5):
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
            run_time=wave.t_max,
            rate_func=linear,
        )
        cycle_animation(wave.creation)
        wave.add_updater(lambda m: m.shift(
            (m.get_left()[0] - left_x) * LEFT
        ))

        def update_wave_copies(wcs):
            index = int(np.ceil(wave.creation.total_time / wave.t_max)) - 1
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
        )


class CirclesDrawingWave(CirclesDrawing):
    CONFIG = {
        "n_circles": 4,
        "center_point": 3 * LEFT,
    }

    def construct(self):
        circles = self.get_circles()
        path = self.get_drawn_path(circles)
        wave = self.get_y_component_wave(circles)

        # small_path = self.get_drawn_path(circles[:1])
        wave1 = self.get_y_component_wave(circles[:1], color=PINK)
        wave2 = self.get_y_component_wave(circles[:2], color=RED)
        # Why?
        circles.update(-1 / self.camera.frame_rate)
        #
        h_line = always_redraw(
            lambda: self.get_wave_y_line(circles, wave)
        )
        self.add(circles, path, wave, h_line)
        self.add(wave1, wave2)
        self.wait(10)

    def get_freqs_and_radii(self):
        return [
            (k * self.base_frequency, self.big_radius / k)
            for k in range(1, 2 * self.n_circles + 1, 2)
        ]
