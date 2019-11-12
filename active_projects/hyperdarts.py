from manimlib.imports import *


OUTPUT_DIRECTORY = "hyperdarts"
BROWN_PAPER = "#958166"


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
        "circle_center_dot_radius": 0.025,
        "default_line_style": {
            "stroke_width": 2,
            "stroke_color": WHITE,
        },
        "default_dot_config": {
            "fill_color": WHITE,
            "background_stroke_width": 1,
            "background_stroke_color": BLACK,
            "radius": 0.5 * DEFAULT_DOT_RADIUS,
        },
        "dart_sound": "dart_low",
        "default_bullseye_shadow_opacity": 0.35,
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
        return Dot(
            circle.get_center(),
            radius=self.circle_center_dot_radius,
            fill_color=BLACK,
        )

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
        # radii = self.get_radii_to_chord(chord, circle)

        elbow = Elbow(width=0.15)
        elbow.set_stroke(WHITE, 2)
        elbow.rotate(h_line.get_angle() - PI, about_point=ORIGIN)
        elbow.shift(point)

        return VGroup(h_line, chord, elbow)

    def get_dart(self, length=1.5):
        dart = SVGMobject(file_name="dart")
        dart.rotate(135 * DEGREES)
        dart.set_width(length)
        dart.rotate(45 * DEGREES, UP)
        dart.rotate(-10 * DEGREES)

        dart.set_fill(GREY)
        dart.set_sheen(2, UL)
        dart.set_stroke(BLACK, 0.5, background=True)
        dart.set_stroke(width=0)
        return dart

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

    # Sound
    def add_dart_sound(self, time_offset=0, gain=-20, **kwargs):
        self.add_sound(
            self.dart_sound,
            time_offset=time_offset,
            gain=-20,
            **kwargs,
        )

    # Animations
    def show_full_hit_process(self, point, pace="slow", with_dart=True):
        assert(pace in ["slow", "fast"])

        to_fade = VGroup()

        if with_dart:
            dart, dot = self.show_hit_with_dart(point)
            to_fade.add(dart, dot)
        else:
            dot = self.show_hit(point)
            to_fade.add(dot)

        if pace == "slow":
            self.wait(0.5)

        # TODO, automatically act based on hit or miss?

        lines = self.show_geometry(point, pace)
        chord_and_shadow = self.show_circle_shrink(lines[1], pace=pace)

        to_fade.add_to_back(chord_and_shadow, lines)

        self.play(
            FadeOut(to_fade),
            run_time=(1 if pace == "slow" else 0.5)
        )

    def show_hits_with_darts(self, points, run_time=0.5, added_anims=None):
        if added_anims is None:
            added_anims = []

        darts = VGroup(*[
            self.get_dart().move_to(point, DR)
            for point in points
        ])
        dots = VGroup(*[
            self.get_dot(point)
            for point in points
        ])

        for dart in darts:
            dart.save_state()
            dart.set_x(-(FRAME_WIDTH + dart.get_width()) / 2)
            dart.rotate(20 * DEGREES)

        n_points = len(points)
        self.play(
            ShowIncreasingSubsets(
                dots,
                rate_func=squish_rate_func(linear, 0.5, 1),
            ),
            LaggedStart(*[
                Restore(
                    dart,
                    path_arc=-20 * DEGREES,
                    rate_func=linear,
                    run_time=run_time,
                )
                for dart in darts
            ], lag_ratio=(1 / n_points)),
            *added_anims,
            run_time=run_time
        )
        for n in range(n_points):
            self.add_dart_sound(
                time_offset=(-n / (2 * n_points))
            )

        return darts, dots

    def show_hit_with_dart(self, point, run_time=0.25, **kwargs):
        darts, dots = self.show_hits_with_darts([point], run_time, **kwargs)
        return darts[0], dots[0]

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
        elif pace == "fast":
            self.add(dot)
        # self.add_dart_sound()
        return dot

    def show_geometry(self, point, pace="slow"):
        assert(pace in ["slow", "fast"])

        lines = self.get_all_hit_lines(point, self.circle)
        h_line, chord, elbow = lines

        # Note, note animating radii anymore...does that mess anything up?
        if pace == "slow":
            self.play(
                ShowCreation(h_line),
                GrowFromCenter(chord),
            )
            self.play(ShowCreation(elbow))
        elif pace == "fast":
            self.play(
                ShowCreation(h_line),
                GrowFromCenter(chord),
                ShowCreation(elbow),
                run_time=0.5
            )
        # return VGroup(h_line, chord)
        return lines

    def show_circle_shrink(self, chord, pace="slow", shadow_opacity=None):
        circle = self.circle
        chord_copy = chord.copy()
        new_circle = self.get_new_circle_from_chord(chord)
        to_fade = VGroup(chord_copy)

        if shadow_opacity is None:
            shadow_opacity = self.default_bullseye_shadow_opacity
        if shadow_opacity > 0:
            shadow = circle.copy()
            shadow.set_opacity(shadow_opacity)
            to_fade.add_to_back(shadow)
            if circle in self.mobjects:
                index = self.mobjects.index(circle)
                self.mobjects.insert(index, shadow)
            else:
                self.add(shadow, self.circle_center_dot)

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
        return to_fade

    def show_miss(self, point, with_dart=True):
        square = self.square
        miss = TextMobject("Miss!")
        miss.next_to(point, UP)
        to_fade = VGroup(miss)

        if with_dart:
            dart, dot = self.show_hit_with_dart(point)
            to_fade.add(dart, dot)
        else:
            dot = self.show_hit(point)
            to_fade.add(dot)
        self.play(
            ApplyMethod(
                square.set_color, YELLOW,
                rate_func=lambda t: (1 - t),
            ),
            GrowFromCenter(miss),
            run_time=0.25
        )
        return to_fade

    def show_game_over(self):
        game_over = TextMobject("GAME OVER")
        game_over.set_width(FRAME_WIDTH - 1)
        rect = FullScreenFadeRectangle(opacity=0.25)

        self.play(
            FadeIn(rect),
            FadeInFromLarge(game_over),
        )
        return VGroup(rect, game_over)


class Dartboard(VGroup):
    CONFIG = {
        "radius": 3,
        "n_sectors": 20,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        n_sectors = self.n_sectors
        angle = TAU / n_sectors

        segments = VGroup(*[
            VGroup(*[
                AnnularSector(
                    inner_radius=in_r,
                    outer_radius=out_r,
                    start_angle=n * angle,
                    angle=angle,
                    color=color,
                )
                for n, color in zip(
                    range(n_sectors),
                    it.cycle(colors)
                )
            ])
            for colors, in_r, out_r in [
                ([LIGHT_GREY, DARKER_GREY], 0, 1),
                ([GREEN_E, RED_E], 0.5, 0.55),
                ([GREEN_E, RED_E], 0.95, 1),
            ]
        ])
        segments.rotate(-angle / 2)
        bullseyes = VGroup(*[
            Circle(radius=r)
            for r in [0.07, 0.035]
        ])
        bullseyes.set_fill(opacity=1)
        bullseyes.set_stroke(width=0)
        bullseyes[0].set_color(GREEN_E)
        bullseyes[1].set_color(RED_E)

        self.bullseye = bullseyes[1]
        self.add(*segments, *bullseyes)
        self.scale(self.radius)


# Scenes to overlay on Numerphile

class TableOfContents(Scene):
    def construct(self):
        rect = FullScreenFadeRectangle(opacity=0.75)
        self.add(rect)

        parts = VGroup(
            TextMobject("The game"),
            TextMobject("The puzzle"),
            TextMobject("The micropuzzles"),
            TextMobject("The answer"),
        )

        parts.scale(1.5)
        parts.arrange(DOWN, buff=LARGE_BUFF, aligned_edge=LEFT)
        parts.to_edge(LEFT, buff=2)

        parts.set_opacity(0.5)
        self.add(parts)

        for part in parts:
            dot = Dot()
            dot.next_to(part, LEFT, SMALL_BUFF)
            dot.match_style(part)
            self.add(dot)

        last_part = VMobject()
        last_part.save_state()

        for part in parts:
            part.save_state()
            self.play(
                part.scale, 1.5, {"about_edge": LEFT},
                part.set_opacity, 1,
                Restore(last_part)
            )
            self.wait()
            last_part = part


class ShowGiantBullseye(HyperdartScene):
    def construct(self):
        square = self.square
        circle = self.circle

        self.remove(square, circle)
        board = Dartboard()
        board.replace(circle)
        bullseye = board.bullseye
        bullseye_border = bullseye.copy()
        bullseye_border.set_fill(opacity=0)
        bullseye_border.set_stroke(YELLOW, 3)

        self.add(board)

        # Label
        label = TextMobject("``", "Bullseye", "''")
        label.scale(1.5)
        label.next_to(square, LEFT, aligned_edge=UP)
        label.set_color(RED)
        arrow = Arrow(
            label.get_bottom(),
            bullseye.get_corner(DR)
        )

        self.play(
            FadeInFromDown(label[1]),
            ShowCreation(arrow),
        )
        self.play(
            bullseye.match_width, board,
            ApplyMethod(
                arrow.scale, 0.4,
                {"about_point": arrow.get_start()}
            ),
            run_time=2,
        )
        self.play(Write(label[::2]))
        self.wait()


class ShowExampleHit(HyperdartScene):
    def construct(self):
        square = self.square
        circle = self.circle
        circle.set_fill(BROWN_PAPER, opacity=0.95)
        old_board = VGroup(square, circle)
        self.remove(square)

        board = Dartboard()
        board.replace(old_board)
        self.add(board, circle)

        # Show hit
        point = 0.75 * UP
        dart, dot = self.show_hit_with_dart(point)

        # Draw lines (with labels)
        lines = self.get_all_hit_lines(point)
        h_line, chord, elbow = lines
        h_label = TexMobject("h")
        h_label.next_to(h_line, LEFT, SMALL_BUFF)

        chord_word = TextMobject("Chord")
        chord_word.next_to(chord.get_center(), UR, SMALL_BUFF)

        self.add(h_line, dot)
        self.play(ShowCreation(h_line))
        self.play(Write(h_label))
        self.wait()
        self.play(
            ShowCreation(chord),
            ShowCreation(elbow),
            Write(chord_word, run_time=1)
        )
        self.wait()

        # Show shrinkage
        chord_copy = chord.copy()
        chord_copy.move_to(ORIGIN)
        new_circle = circle.copy()
        new_circle.set_fill(RED, 1)
        new_circle.match_width(chord_copy)
        new_circle.move_to(ORIGIN)

        new_diam_word = TextMobject("New diameter")
        new_diam_word.next_to(chord_copy, DOWN, SMALL_BUFF)

        outline = VGroup(
            Arc(start_angle=0, angle=PI),
            Arc(start_angle=PI, angle=PI),
        )
        outline.set_stroke(YELLOW, 3)
        outline.set_fill(opacity=0)
        outline.replace(new_circle)

        self.play(
            circle.set_color, DARK_GREY,
            TransformFromCopy(chord, chord_copy),
            FadeInFrom(new_diam_word, UP)
        )
        self.play(
            Rotate(chord_copy, PI),
            ShowCreation(outline, lag_ratio=0),
        )
        self.play()

        # Show variable hit_point
        self.remove(lines)
        point_tracker = VectorizedPoint(point)
        self.remove(lines, *lines)
        lines = always_redraw(
            lambda: self.get_all_hit_lines(point_tracker.get_location())
        )
        dot.add_updater(lambda m: m.move_to(point_tracker))
        dart.add_updater(lambda m: m.move_to(point_tracker, DR))
        chord_copy.add_updater(
            lambda m: m.match_width(lines[1]).move_to(ORIGIN)
        )
        new_circle.add_updater(lambda m: m.match_width(chord_copy).move_to(ORIGIN))
        h_label.add_updater(lambda m: m.next_to(lines[0], LEFT, SMALL_BUFF))

        chord_word.add_updater(lambda m: m.next_to(lines[1].get_center(), UR, SMALL_BUFF))
        ndw_width = new_diam_word.get_width()
        new_diam_word.add_updater(
            lambda m: m.set_width(
                min(ndw_width, chord_copy.get_width())
            ).next_to(chord_copy, DOWN, SMALL_BUFF)
        )

        self.add(new_circle, chord_copy, lines, h_label, dart, dot, chord_word, new_diam_word)
        self.play(
            FadeOut(outline),
            FadeIn(new_circle)
        )
        self.wait()

        self.play(
            point_tracker.shift, 2.1 * UP,
            run_time=9,
            rate_func=there_and_back_with_pause,
        )


class QuicklyAnimatedShrinking(HyperdartScene):
    def construct(self):
        # square = self.square
        # circle = self.circle

        for x in range(5):
            point = self.get_random_point()
            while not self.is_inside(point):
                point = self.get_random_point()
            self.show_full_hit_process(point, pace="fast")
        # self.show_game_over()


class GameOver(HyperdartScene):
    def construct(self):
        self.clear()
        self.show_game_over()


class SquareAroundTheDartBoard(HyperdartScene):
    def construct(self):
        square = self.square
        circle = self.circle
        VGroup(square, circle).to_edge(DOWN, MED_SMALL_BUFF)
        self.clear()
        board = Dartboard()
        board.replace(square)

        title = TextMobject("Square around the dart board")
        title.scale(1.5)
        title.next_to(square, UP, MED_LARGE_BUFF)

        self.add(board)
        self.play(FadeInFromDown(title))
        self.add(square, board)
        self.play(DrawBorderThenFill(square, run_time=2))
        self.wait()


class ContrastDistributions(HyperdartScene):
    def construct(self):
        square = self.square
        circle = self.circle
        board = Dartboard()
        board.replace(circle)

        group = VGroup(square, circle, board)
        group.to_edge(LEFT)
        group.scale(0.8, about_edge=DOWN)

        group_copy = group.copy()
        square_copy, circle_copy, board_copy = group_copy
        group_copy.set_x(-group.get_center()[0])

        v_line = DashedLine(FRAME_HEIGHT * UP / 2, FRAME_HEIGHT * DOWN / 2)

        left_label = TextMobject("Our distribution\\\\(uniform in the square)")
        left_label.match_x(group)
        left_label.to_edge(UP)
        right_label = TextMobject("More realistic distribution")
        right_label.match_x(group_copy)
        right_label.to_edge(UP)

        n_points = 2000
        left_points = self.get_random_points(n_points)
        right_points = np.random.multivariate_normal(
            mean=board_copy.get_center(),
            cov=0.6 * np.identity(3),
            size=n_points
        )

        left_dots, right_dots = [
            VGroup(*[
                Dot(p, radius=0.02) for p in points
            ])
            for points in [left_points, right_points]
        ]

        left_rect = FullScreenFadeRectangle(opacity=0.75)
        left_rect.stretch(0.49, 0, about_edge=LEFT)
        right_rect = left_rect.copy()
        right_rect.to_edge(RIGHT, buff=0)

        self.add(group, board_copy)
        self.add(left_label, right_label)
        self.add(v_line)
        self.add(left_rect)

        self.play(
            LaggedStartMap(FadeInFromLarge, right_dots),
            run_time=5
        )
        self.wait()
        self.play(
            FadeOut(left_rect),
            FadeIn(right_rect),
        )
        self.play(
            LaggedStartMap(FadeInFromLarge, left_dots),
            run_time=5
        )
        self.wait()


class ChooseXThenYUniformly(Scene):
    def construct(self):
        # Setup
        unit_size = 3
        axes = Axes(
            x_min=-1.25,
            x_max=1.25,
            y_min=-1.25,
            y_max=1.25,
            number_line_config={
                "tick_frequency": 0.25,
                "unit_size": unit_size,
            },
        )
        numbers = [-1, -0.5, 0.5, 1]
        num_config = {
            "num_decimal_places": 1,
            "background_stroke_width": 3,
        }
        axes.x_axis.add_numbers(
            *numbers,
            number_config=num_config,
        )
        axes.y_axis.add_numbers(
            *numbers,
            number_config=num_config,
            direction=LEFT,
        )

        circle = Circle(radius=unit_size)
        circle.set_stroke(WHITE, 0)
        circle.set_fill(RED, 0.7)

        square = Square()
        square.replace(circle)
        square.set_stroke(LIGHT_GREY, 1)
        square = DashedVMobject(square, num_dashes=101)

        self.add(square, circle)
        self.add(axes)

        # x and y stuff
        x_tracker = ValueTracker(-1)
        y_tracker = ValueTracker(-1)

        get_x = x_tracker.get_value
        get_y = y_tracker.get_value

        x_tip = ArrowTip(start_angle=PI / 2, color=BLUE)
        y_tip = ArrowTip(start_angle=0, color=YELLOW)
        for tip in [x_tip, y_tip]:
            tip.scale(0.5)
        x_tip.add_updater(lambda m: m.move_to(axes.c2p(get_x(), 0), UP))
        y_tip.add_updater(lambda m: m.move_to(axes.c2p(0, get_y()), RIGHT))

        x_eq = VGroup(TexMobject("x = "), DecimalNumber(0))
        x_eq.arrange(RIGHT, SMALL_BUFF)
        x_eq[1].match_y(x_eq[0][0][1])
        x_eq[1].add_updater(lambda m: m.set_value(get_x()))
        x_eq.match_color(x_tip)

        y_eq = VGroup(TexMobject("y = "), DecimalNumber(0))
        y_eq.arrange(RIGHT, SMALL_BUFF)
        y_eq[1].match_y(y_eq[0][0][1])
        y_eq[1].add_updater(lambda m: m.set_value(get_y()))
        y_eq.match_color(y_tip)

        eqs = VGroup(x_eq, y_eq)
        eqs.arrange(DOWN, buff=MED_LARGE_BUFF)
        eqs.to_edge(UR)

        self.add(x_tip)
        self.add(x_eq)

        # Choose x
        self.play(
            x_tracker.set_value, 1,
            run_time=2,
        )
        self.play(
            x_tracker.set_value, np.random.random(),
            run_time=1,
        )

        # Choose y
        self.play(
            FadeIn(y_tip),
            FadeIn(y_eq),
        )
        self.play(
            y_tracker.set_value, 1,
            run_time=2,
        )
        self.play(
            y_tracker.set_value, np.random.random(),
            run_time=1,
        )

        point = axes.c2p(get_x(), get_y())
        dot = Dot(point)
        x_line = DashedLine(axes.c2p(0, get_y()), point)
        y_line = DashedLine(axes.c2p(get_x(), 0), point)
        lines = VGroup(x_line, y_line)
        lines.set_stroke(WHITE, 2)

        self.play(*map(ShowCreation, lines))
        self.play(DrawBorderThenFill(dot))
        self.wait()

        points = [
            axes.c2p(*np.random.uniform(-1, 1, size=2))
            for n in range(2000)
        ]
        dots = VGroup(*[
            Dot(point, radius=0.02)
            for point in points
        ])
        self.play(
            LaggedStartMap(FadeInFromLarge, dots),
            run_time=3,
        )
        self.wait()


class ShowDistributionOfScores(Scene):
    CONFIG = {
        "axes_config": {
            ""
        }
    }

    def construct(self):
        self.add_axes()
        self.add_score_label()
        self.setup_histogram()
        self.show_many_runs()

    def add_axes(self):
        axes = Axes(**self.axes_config)

    def add_score_label(self):
        pass

    def setup_histogram(self):
        pass

    def show_many_runs(self):
        pass


    #
    def add_one_run(self, animate=True):
        pass

    def get_random_score(self):
        pass


# Old scenes, before decision to collaborate with numberphile
class IntroduceGame(HyperdartScene):
    CONFIG = {
        "random_seed": 0,
        "square_width": 5,
        "num_darts_in_initial_flurry": 5,
    }

    def construct(self):
        self.show_flurry_of_points()
        self.show_board_dimensions()
        self.introduce_bullseye()
        self.show_miss_example()
        self.show_shrink_rule()

    def show_flurry_of_points(self):
        square = self.square
        circle = self.circle

        title = TextMobject("Hyperdarts")
        title.scale(1.5)
        title.to_edge(UP)

        n = self.num_darts_in_initial_flurry
        points = np.random.normal(size=n * 3).reshape((n, 3))
        points[:, 2] = 0
        points *= 0.75

        board = Dartboard()
        board.match_width(square)
        board.move_to(square)

        pre_square = Circle(color=WHITE)
        pre_square.replace(square)

        self.remove(circle, square)
        self.add(board)

        darts, dots = self.show_hits_with_darts(
            points,
            added_anims=[FadeInFromDown(title)]
        )
        self.wait()

        def func(p):
            theta = angle_of_vector(p) % (TAU / 4)
            if theta > TAU / 8:
                theta = TAU / 4 - theta
            p *= 1 / np.cos(theta)
            return p

        self.play(
            *[
                ApplyPointwiseFunction(func, pieces, run_time=1)
                for pieces in [*board[:3], *dots]
            ],
            *[
                MaintainPositionRelativeTo(dart, dot)
                for dart, dot in zip(darts, dots)
            ]
        )

        self.flurry_dots = dots
        self.darts = darts
        self.title = title
        self.board = board

    def show_board_dimensions(self):
        square = self.square

        labels = VGroup(*[
            TextMobject("2 ft").next_to(
                square.get_edge_center(vect), vect,
            )
            for vect in [DOWN, RIGHT]
        ])
        labels.set_color(YELLOW)

        h_line, v_line = lines = VGroup(*[
            DashedLine(
                square.get_edge_center(v1),
                square.get_edge_center(-v1),
            ).next_to(label, v2)
            for label, v1, v2 in zip(labels, [LEFT, UP], [UP, LEFT])
        ])
        lines.match_color(labels)

        self.play(
            LaggedStartMap(ShowCreation, lines),
            LaggedStartMap(FadeInFromDown, labels),
            lag_ratio=0.5
        )
        self.wait()

        self.square_dimensions = VGroup(lines, labels)

    def introduce_bullseye(self):
        square = self.square
        circle = self.circle
        board = self.board
        circle.save_state()
        circle.replace(board[-1])

        label = TextMobject("Bullseye")
        label.scale(1.5)
        label.next_to(square, LEFT, aligned_edge=UP)
        label.set_color(RED)
        arrow = Arrow(
            label.get_bottom(),
            circle.get_corner(DR)
        )

        radius = DashedLine(
            square.get_center(),
            square.get_left(),
            stroke_width=2,
        )
        radius_label = TextMobject("1 ft")
        radius_label.next_to(radius, DOWN, SMALL_BUFF)

        self.add(circle, self.square_dimensions)
        self.play(
            FadeInFromLarge(circle),
            FadeInFromDown(label),
            ShowCreation(arrow),
            LaggedStartMap(FadeOut, self.flurry_dots, run_time=1),
            LaggedStartMap(FadeOut, self.darts, run_time=1),
        )
        self.wait()
        self.add(square, board, arrow, circle)
        self.play(
            Restore(circle),
            ApplyMethod(
                arrow.scale, 0.4,
                {"about_point": arrow.get_start()}
            ),
        )
        self.add(radius, self.circle_center_dot)
        self.play(
            ShowCreation(radius),
            FadeInFrom(radius_label, RIGHT),
            FadeIn(self.circle_center_dot),
        )
        self.play(
            FadeOut(label),
            Uncreate(arrow),
            FadeOut(board)
        )
        self.wait()

        s_lines, s_labels = self.square_dimensions
        self.play(
            FadeOut(s_lines),
            FadeOut(radius),
            FadeOut(radius_label),
            FadeOut(self.title),
        )

        self.circle_dimensions = VGroup(
            radius, radius_label,
        )

    def show_miss_example(self):
        square = self.square
        point = square.get_corner(UL) + 0.5 * DR

        miss_word = TextMobject("Miss!")
        miss_word.scale(1.5)
        miss_word.next_to(point, UP, LARGE_BUFF)

        dart, dot = self.show_hit_with_dart(point)
        self.play(FadeInFromDown(miss_word))
        self.wait()
        game_over = self.show_game_over()
        self.wait()
        self.play(
            *map(FadeOut, [dart, dot, miss_word, game_over])
        )

    def show_shrink_rule(self):
        circle = self.circle
        point = 0.5 * circle.point_from_proportion(0.2)

        # First example
        self.show_full_hit_process(point)
        self.wait()

        # Close to border
        label = TextMobject("Bad shot $\\Rightarrow$ much shrinkage")
        label.scale(1.5)
        label.to_edge(UP)

        point = 0.98 * circle.point_from_proportion(3 / 8)
        circle.save_state()
        self.play(FadeInFromDown(label))
        self.show_full_hit_process(point)
        self.wait()
        self.play(Restore(circle))

        # Close to center
        new_label = TextMobject("Good shot $\\Rightarrow$ less shrinkage")
        new_label.scale(1.5)
        new_label.to_edge(UP)
        point = 0.2 * circle.point_from_proportion(3 / 8)
        self.play(
            FadeInFromDown(new_label),
            FadeOutAndShift(label, UP),
        )
        self.show_full_hit_process(point)
        self.wait()
        self.play(FadeOut(new_label))

        # Play on
        for x in range(3):
            r1, r2 = np.random.random(size=2)
            point = r1 * circle.point_from_proportion(r2)
            self.show_full_hit_process(point)
        point = circle.get_right() + 0.5 * UR
        self.show_miss(point)
        self.wait()
        self.show_game_over()


class ShowScoring(HyperdartScene):
    def setup(self):
        super().setup()
        self.add_score_counter()

    def construct(self):
        self.comment_on_score()
        self.show_several_hits()

    def comment_on_score(self):
        score_label = self.score_label
        comment = TextMobject("\\# Bullseyes")
        # rect = SurroundingRectangle(comment)
        # rect.set_stroke(width=1)
        # comment.add(rect)
        comment.set_color(YELLOW)
        comment.next_to(score_label, DOWN, LARGE_BUFF)
        comment.set_x(midpoint(
            self.square.get_left(),
            LEFT_SIDE,
        )[0])
        arrow = Arrow(
            comment.get_top(),
            score_label[1].get_bottom(),
            buff=0.2,
        )
        arrow.match_color(comment)

        self.play(
            FadeInFromDown(comment),
            GrowArrow(arrow),
        )

    def show_several_hits(self):
        points = [UR, DL, 0.5 * UL, 0.5 * DR]
        for point in points:
            self.show_full_hit_process(point, pace="fast")
        self.show_miss(2 * UR)
        self.wait()

    #
    def add_score_counter(self):
        score = Integer(0)
        score_label = VGroup(
            TextMobject("Score: "),
            score
        )
        score_label.arrange(RIGHT, aligned_edge=DOWN)
        score_label.scale(1.5)
        score_label.to_corner(UL)

        self.add(score_label)

        self.score = score
        self.score_label = score_label

    def increment_score(self):
        score = self.score
        new_score = score.copy()
        new_score.increment_value(1)
        self.play(
            FadeOutAndShift(score, UP),
            FadeInFrom(new_score, DOWN),
            run_time=1,
        )
        self.remove(new_score)
        score.increment_value()
        score.move_to(new_score)
        self.add(score)

    def show_hit(self, point, *args, **kwargs):
        result = super().show_hit(point, *args, **kwargs)
        if self.is_inside(point):
            self.increment_score()
        return result

    def show_hit_with_dart(self, point, *args, **kwargs):
        result = super().show_hit_with_dart(point, *args, **kwargs)
        if self.is_inside(point):
            self.increment_score()
        return result


class ShowSeveralRounds(ShowScoring):
    CONFIG = {
        "n_rounds": 5,
    }

    def construct(self):
        for x in range(self.n_rounds):
            self.show_single_round()
            self.reset_board()

    def show_single_round(self, pace="fast"):
        while True:
            point = self.get_random_point()
            if self.is_inside(point):
                self.show_full_hit_process(point, pace=pace)
            else:
                to_fade = self.show_miss(point)
                self.wait(0.5)
                self.play(
                    ShowCreationThenFadeAround(self.score_label),
                    FadeOut(to_fade)
                )
                return

    def reset_board(self):
        score = self.score
        new_score = score.copy()
        new_score.set_value(0)
        self.play(
            self.circle.match_width, self.square,
            FadeOutAndShift(score, UP),
            FadeInFrom(new_score, DOWN),
        )
        score.set_value(0)
        self.add(score)
        self.remove(new_score)


class ShowSeveralRoundsQuickly(ShowSeveralRounds):
    CONFIG = {
        "n_rounds": 15,
    }

    def show_full_hit_process(self, point, *args, **kwargs):
        lines = self.get_all_hit_lines(point)

        dart = self.show_hit_with_dart(point)
        self.add(lines)
        self.score.increment_value(1)
        to_fade = self.show_circle_shrink(lines[1], pace="fast")
        to_fade.add(*lines, *dart)
        self.play(FadeOut(to_fade), run_time=0.5)

    def increment_score(self):
        pass  # Handled elsewhere


class ShowSeveralRoundsVeryQuickly(ShowSeveralRoundsQuickly):
    def construct(self):
        pass


class ShowUniformDistribution(HyperdartScene):
    CONFIG = {
        "dart_sound": "dart_high",
        "n_points": 1000,
    }

    def construct(self):
        self.add_title()
        self.show_random_points()
        self.exchange_titles()
        self.show_random_points()

    def get_square(self):
        return super().get_square().to_edge(DOWN)

    def add_title(self):
        # square = self.square
        title = TextMobject("All points in the square are equally likely")
        title.scale(1.5)
        title.to_edge(UP)

        new_title = TextMobject("``Uniform distribution'' on the square")
        new_title.scale(1.5)
        new_title.to_edge(UP)

        self.play(FadeInFromDown(title))

        self.title = title
        self.new_title = new_title

    def show_random_points(self):
        points = self.get_random_points(self.n_points)
        dots = VGroup(*[
            Dot(point, radius=0.02)
            for point in points
        ])
        dots.set_fill(opacity=0.75)

        run_time = 5
        self.play(LaggedStartMap(
            FadeInFromLarge, dots,
            run_time=run_time,
        ))
        for x in range(1000):
            self.add_dart_sound(
                time_offset=-run_time * np.random.random(),
                gain=-10,
                gain_to_background=-5,
            )
        self.wait()

    def exchange_titles(self):
        self.play(
            FadeInFromDown(self.new_title),
            FadeOutAndShift(self.title, UP),
        )


class ExpectedScoreEqualsQMark(Scene):
    def construct(self):
        equation = TextMobject(
            "\\textbf{E}[Score] = ???",
            tex_to_color_map={
                "???": YELLOW,
            }
        )
        aka = TextMobject("a.k.a. Long-term average")
        aka.next_to(equation, DOWN)

        self.play(Write(equation))
        self.wait(2)
        self.play(FadeInFrom(aka, UP))
        self.wait()

