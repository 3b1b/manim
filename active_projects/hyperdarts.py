from manimlib.imports import *


OUTPUT_DIRECTORY = "hyperdarts"


class HyperdartScene(Scene):
    CONFIG = {
        "square_width": 6,
        "square_style": {
            "stroke_width": 2,
            "fill_color": BLUE,
            "fill_opacity": 0.5,
        },
        "circle_style": {
            "fill_color": RED_E,
            "fill_opacity": 1,
            "stroke_width": 0,
        },
        "default_line_style": {
            "stroke_width": 2,
            "stroke_color": WHITE,
        },
        "default_dot_config": {
            "fill_color": WHITE,
            "background_stroke_width": 1,
            "background_stroke_color": BLACK,
        },
    }

    def setup(self):
        self.square = self.get_square()
        self.circle = self.get_circle()
        self.circle_center_dot = self.get_circle_center_dot()

        self.add(self.square)
        self.add(self.circle)
        self.add(self.circle_center_dot)

    def get_square(self):
        return Square(
            side_length=self.square_width,
            **self.square_style
        )

    def get_circle(self, square=None):
        square = square or self.square
        circle = Circle(**self.circle_style)
        circle.replace(square)
        return circle

    def get_circle_center_dot(self, circle=None):
        circle = circle or self.circle
        dot = Dot(circle.get_center())
        dot.set_width(0.02)
        dot.set_color(GREY)
        return dot

    def get_number_plane(self):
        square = self.square
        unit_size = square.get_width() / 2
        plane = NumberPlane(
            axis_config={
                "unit_size": unit_size,
            }
        )
        plane.add_coordinates()
        plane.shift(square.get_center() - plane.c2p(0, 0))
        return plane

    def get_random_points(self, n):
        square = self.square
        points = np.random.uniform(-1, 1, 3 * n).reshape((n, 3))

        points[:, 0] *= square.get_width() / 2
        points[:, 1] *= square.get_height() / 2
        points[:, 2] = 0
        points += square.get_center()
        return points

    def get_random_point(self):
        return self.get_random_points(1)[0]

    def get_dot(self, point):
        return Dot(point, **self.default_dot_config)

    # Hit transform rules
    def is_inside(self, point, circle=None):
        circle = circle or self.circle
        return get_norm(point - circle.get_center()) <= circle.get_width() / 2

    def get_new_radius(self, point, circle=None):
        circle = circle or self.circle
        center = circle.get_center()
        radius = circle.get_width() / 2
        p_dist = get_norm(point - center)
        return np.sqrt(radius**2 - p_dist**2)

    def get_hit_distance_line(self, point, circle=None):
        circle = circle or self.circle

        line = Line(
            circle.get_center(), point,
            **self.default_line_style
        )
        return line

    def get_chord(self, point, circle=None):
        circle = circle or self.circle

        center = circle.get_center()
        p_angle = angle_of_vector(point - center)
        chord = Line(DOWN, UP)
        new_radius = self.get_new_radius(point, circle)
        chord.scale(new_radius)
        chord.rotate(p_angle)
        chord.move_to(point)
        chord.set_style(**self.default_line_style)
        return chord

    def get_radii_to_chord(self, chord, circle=None):
        circle = circle or self.circle

        center = circle.get_center()
        radii = VGroup(*[
            DashedLine(center, point)
            for point in chord.get_start_and_end()
        ])
        radii.set_style(**self.default_line_style)
        return radii

    def get_all_hit_lines(self, point, circle=None):
        h_line = self.get_hit_distance_line(point, circle)
        chord = self.get_chord(point, circle)
        radii = self.get_radii_to_chord(chord, circle)
        return VGroup(h_line, chord, radii)

    # New circle
    def get_new_circle_from_point(self, point, circle=None):
        return self.get_new_circle(
            self.get_new_radius(point, circle),
            circle,
        )

    def get_new_circle_from_chord(self, chord, circle=None):
        return self.get_new_circle(
            chord.get_length() / 2,
            circle,
        )

    def get_new_circle(self, new_radius, circle=None):
        circle = circle or self.circle
        new_circle = self.get_circle()
        new_circle.set_width(2 * new_radius)
        new_circle.move_to(circle)
        return new_circle

    # Animations

    def show_hit(self, point, pace="slow", added_anims=None):
        assert(pace in ["slow", "fast"])
        if added_anims is None:
            added_anims = []

        dot = self.get_dot(point)
        if pace == "slow":
            self.play(
                FadeInFromLarge(dot, rate_func=rush_into),
                *added_anims,
                run_time=0.5,
            )
            self.wait(0.5)
        elif pace == "fast":
            self.add(dot)
        return dot

    def show_full_hit_process(self, point, pace="slow"):
        assert(pace in ["slow", "fast"])

        lines = self.get_all_hit_lines(point, self.circle)
        h_line, chord, radii = lines

        dot = self.show_hit(point)
        if pace == "slow":
            self.play(
                ShowCreation(h_line),
                GrowFromCenter(chord),
            )
            self.play(*map(ShowCreation, radii))
        elif pace == "fast":
            self.add(dot)
            self.play(
                ShowCreation(h_line),
                GrowFromCenter(chord),
                *map(ShowCreation, radii),
                run_time=0.5
            )

        new_chord = self.show_circle_shrink(chord, pace=pace)
        self.play(
            FadeOut(lines),
            FadeOut(new_chord),
            FadeOut(dot),
            run_time=(1 if pace == "slow" else 0.5)
        )

    def show_circle_shrink(self, chord, pace="slow"):
        circle = self.circle
        chord_copy = chord.copy()
        new_circle = self.get_new_circle_from_chord(chord)

        outline = VGroup(*[
            VMobject().pointwise_become_partial(new_circle, a, b)
            for (a, b) in [(0, 0.5), (0.5, 1)]
        ])
        outline.rotate(chord.get_angle())
        outline.set_fill(opacity=0)
        outline.set_stroke(YELLOW, 2)

        assert(pace in ["slow", "fast"])

        if pace == "slow":
            self.play(
                chord_copy.move_to, circle.get_center(),
                circle.set_opacity, 0.5,
            )
            self.play(
                Rotating(
                    chord_copy,
                    radians=PI,
                ),
                ShowCreation(
                    outline,
                    lag_ratio=0
                ),
                run_time=1,
                rate_func=smooth,
            )
            self.play(
                Transform(circle, new_circle),
                FadeOut(outline),
            )
        elif pace == "fast":
            outline = new_circle.copy()
            outline.set_fill(opacity=0)
            outline.set_stroke(YELLOW, 2)
            outline.move_to(chord)
            outline.generate_target()
            outline.target.move_to(circle)
            self.play(
                chord_copy.move_to, circle,
                Transform(circle, new_circle),
                # MoveToTarget(
                #     outline,
                #     remover=True
                # )
            )
            # circle.become(new_circle)
            # circle.become(new_circle)
            # self.remove(new_circle)

        return chord_copy

    def show_miss(self, point):
        square = self.square
        miss = TextMobject("Miss!")
        miss.next_to(point, DOWN)

        dot = self.show_hit(
            point,
            added_anims=[
                ApplyMethod(
                    square.set_color, YELLOW,
                    rate_func=there_and_back,
                ),
                GrowFromCenter(miss)
            ]
        )
        return VGroup(dot, miss)


# Problem statement

class IntroduceGame(HyperdartScene):
    CONFIG = {
        "random_seed": 1,
        "square_width": 5,
        # "num_darts_in_initial_flurry": 1000,
        "num_darts_in_initial_flurry": 100,
    }

    def construct(self):
        self.add_real_dartboard()
        self.show_flurry_of_points()
        self.show_board_dimensions()
        self.introduce_bullseye()
        self.show_shrink_rule()

    def add_real_dartboard(self):
        pass

    def show_flurry_of_points(self):
        title = TextMobject("Hyperdarts")
        title.scale(1.5)
        title.to_edge(UP)

        n = self.num_darts_in_initial_flurry
        points = np.random.normal(size=n * 3).reshape((n, 3))
        points[:, 2] = 0
        points *= 0.75
        dots = VGroup(*[
            Dot(point, radius=0.01)
            for point in points
        ])

        self.remove(self.circle)
        self.play(
            FadeInFromDown(title),
            LaggedStartMap(FadeInFromLarge, dots)
        )
        self.wait()

        self.flurry_dots = dots

    def show_board_dimensions(self):
        square = self.square

        labels = VGroup(*[
            TextMobject("2ft").next_to(
                square.get_edge_center(vect), -vect, SMALL_BUFF
            )
            for vect in [UP, RIGHT]
        ])
        labels.set_color(YELLOW)

        h_line, v_line = lines = VGroup(*[
            DashedLine(
                square.get_edge_center(v1),
                square.get_edge_center(-v1),
            ).next_to(label, -v2, buff=SMALL_BUFF)
            for label, v1, v2 in zip(labels, [LEFT, UP], [UP, RIGHT])
        ])
        lines.match_color(labels)

        self.play(
            LaggedStartMap(ShowCreation, lines),
            LaggedStartMap(FadeInFromDown, labels),
            lag_ratio=0.5
        )

    def introduce_bullseye(self):
        pass

    def show_shrink_rule(self):
        pass
