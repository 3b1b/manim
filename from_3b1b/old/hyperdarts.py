from manimlib.imports import *


OUTPUT_DIRECTORY = "hyperdarts"
BROWN_PAPER = "#958166"


class HyperdartScene(MovingCameraScene):
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
        MovingCameraScene.setup(self)
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


class SimulateRealGame(HyperdartScene):
    CONFIG = {
        "circle_style": {
            # "fill_color": BROWN_PAPER,
        }
    }

    def construct(self):
        board = Dartboard()
        board.set_opacity(0.5)
        self.remove(self.square)
        self.square.set_opacity(0)
        self.add(board, self.circle)

        points = [
            0.5 * UP,
            2.0 * UP,
            1.9 * LEFT + 0.4 * DOWN,
        ]

        for point in points:
            self.show_full_hit_process(point)
        self.show_miss(1.8 * DL)
        self.show_game_over()


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
            axis_config={
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
            "x_min": -1,
            "x_max": 10,
            "x_axis_config": {
                "unit_size": 1.2,
                "tick_frequency": 1,
            },
            "y_min": 0,
            "y_max": 100,
            "y_axis_config": {
                "unit_size": 0.065,
                "tick_frequency": 10,
                "include_tip": False,
            },
        },
        "random_seed": 1,
    }

    def construct(self):
        # Add axes
        axes = self.get_axes()
        self.add(axes)

        # setup scores
        n_scores = 10000
        scores = np.array([self.get_random_score() for x in range(n_scores)])
        index_tracker = ValueTracker(n_scores)

        def get_index():
            value = np.clip(index_tracker.get_value(), 0, n_scores - 1)
            return int(value)

        # Setup histogram
        bars = self.get_histogram_bars(axes)
        bars.add_updater(
            lambda b: self.set_histogram_bars(
                b, scores[:get_index()], axes
            )
        )
        self.add(bars)

        # Add score label
        score_label = VGroup(
            TextMobject("Last score: "),
            Integer(1)
        )
        score_label.scale(1.5)
        score_label.arrange(RIGHT)
        score_label[1].align_to(score_label[0][0][-1], DOWN)

        score_label[1].add_updater(
            lambda m: m.set_value(scores[get_index() - 1])
        )
        score_label[1].add_updater(
            lambda m: m.set_fill(bars[scores[get_index() - 1]].get_fill_color())
        )

        n_trials_label = VGroup(
            TextMobject("\\# Games: "),
            Integer(0),
        )
        n_trials_label.scale(1.5)
        n_trials_label.arrange(RIGHT, aligned_edge=UP)
        n_trials_label[1].add_updater(
            lambda m: m.set_value(get_index())
        )

        n_trials_label.to_corner(UR, buff=LARGE_BUFF)
        score_label.next_to(
            n_trials_label, DOWN,
            buff=LARGE_BUFF,
            aligned_edge=LEFT,
        )

        self.add(score_label)
        self.add(n_trials_label)

        # Add curr_score_arrow
        curr_score_arrow = Arrow(0.25 * UP, ORIGIN, buff=0)
        curr_score_arrow.set_stroke(WHITE, 5)
        curr_score_arrow.add_updater(
            lambda m: m.next_to(bars[scores[get_index() - 1] - 1], UP, SMALL_BUFF)
        )
        self.add(curr_score_arrow)

        # Add mean bar
        mean_line = DashedLine(ORIGIN, 4 * UP)
        mean_line.set_stroke(YELLOW, 2)

        def get_mean():
            return np.mean(scores[:get_index()])

        mean_line.add_updater(
            lambda m: m.move_to(axes.c2p(get_mean(), 0), DOWN)
        )
        mean_label = VGroup(
            TextMobject("Mean = "),
            DecimalNumber(num_decimal_places=3),
        )
        mean_label.arrange(RIGHT)
        mean_label.match_color(mean_line)
        mean_label.add_updater(lambda m: m.next_to(mean_line, UP, SMALL_BUFF))
        mean_label[1].add_updater(lambda m: m.set_value(get_mean()))

        # Show many runs
        index_tracker.set_value(1)
        for value in [10, 100, 1000, 10000]:
            anims = [
                ApplyMethod(
                    index_tracker.set_value, value,
                    rate_func=linear,
                    run_time=5,
                ),
            ]
            if value == 10:
                anims.append(
                    FadeIn(
                        VGroup(mean_line, mean_label),
                        rate_func=squish_rate_func(smooth, 0.5, 1),
                        run_time=2,
                    ),
                )
            self.play(*anims)
        self.wait()

    #
    def get_axes(self):
        axes = Axes(**self.axes_config)
        axes.to_corner(DL)

        axes.x_axis.add_numbers(*range(1, 12))
        axes.y_axis.add_numbers(
            *range(20, 120, 20),
            number_config={
                "unit": "\\%"
            }
        )
        x_label = TextMobject("Score")
        x_label.next_to(axes.x_axis.get_right(), UR, buff=0.5)
        x_label.shift_onto_screen()
        axes.x_axis.add(x_label)

        y_label = TextMobject("Relative proportion")
        y_label.next_to(axes.y_axis.get_top(), RIGHT, buff=0.75)
        y_label.to_edge(UP, buff=MED_SMALL_BUFF)
        axes.y_axis.add(y_label)

        return axes

    def get_histogram_bars(self, axes):
        bars = VGroup()
        for x in range(1, 10):
            bar = Rectangle(width=axes.x_axis.unit_size)
            bar.move_to(axes.c2p(x, 0), DOWN)
            bar.x = x
            bars.add(bar)
        bars.set_fill(opacity=0.7)
        bars.set_color_by_gradient(BLUE, YELLOW, RED)
        bars.set_stroke(WHITE, 1)
        return bars

    def get_relative_proportion_map(self, all_scores):
        scores = set(all_scores)
        n_scores = len(all_scores)
        return dict([
            (s, np.sum(all_scores == s) / n_scores)
            for s in set(scores)
        ])

    def set_histogram_bars(self, bars, scores, axes):
        prop_map = self.get_relative_proportion_map(scores)
        epsilon = 1e-6
        for bar in bars:
            prop = prop_map.get(bar.x, epsilon)
            bar.set_height(
                prop * axes.y_axis.unit_size * 100,
                stretch=True,
                about_edge=DOWN,
            )

    def get_random_score(self):
        score = 1
        radius = 1
        while True:
            point = np.random.uniform(-1, 1, size=2)
            hit_radius = get_norm(point)
            if hit_radius > radius:
                return score
            else:
                score += 1
                radius = np.sqrt(radius**2 - hit_radius**2)


class ExactBullseye(HyperdartScene):
    def construct(self):
        board = Dartboard()
        board.replace(self.square)

        lines = VGroup(Line(DOWN, UP), Line(LEFT, RIGHT))
        lines.set_stroke(WHITE, 1)
        lines.replace(self.square)

        self.add(board, lines)
        dart, dot = self.show_hit_with_dart(0.0037 * DOWN)
        self.play(FadeOut(dot))

        frame = self.camera_frame
        self.play(frame.scale, 0.02, run_time=5)
        self.wait()


class ShowProbabilityForFirstShot(HyperdartScene):
    def construct(self):
        square = self.square
        circle = self.circle
        VGroup(square, circle).to_edge(LEFT)

        r_line = DashedLine(circle.get_center(), circle.get_right())
        r_label = TexMobject("r = 1")
        r_label.next_to(r_line, DOWN, SMALL_BUFF)
        self.add(r_line, r_label)

        points = self.get_random_points(3000)
        dots = VGroup(*[Dot(point, radius=0.02) for point in points])
        dots.set_fill(WHITE, 0.5)

        p_label = TexMobject("P", "(S > 1)", "= ")
        square_frac = VGroup(
            circle.copy().set_height(0.5),
            Line(LEFT, RIGHT).set_width(0.7),
            square.copy().set_height(0.5).set_stroke(width=0)
        )
        square_frac.arrange(DOWN, buff=SMALL_BUFF)
        result = TexMobject("=", "{\\pi \\over 4}")

        equation = VGroup(p_label, square_frac, result)
        equation.arrange(RIGHT)
        equation.scale(1.4)
        equation.to_edge(RIGHT, buff=MED_LARGE_BUFF)

        brace = Brace(p_label[1], UP, buff=SMALL_BUFF)
        brace_label = brace.get_text("At least one\\\\``bullseye''")

        self.add(equation, brace, brace_label)
        self.play(
            LaggedStartMap(FadeInFromLarge, dots),
            run_time=5,
        )
        self.play(
            ReplacementTransform(
                circle.copy().set_fill(opacity=0).set_stroke(WHITE, 1),
                square_frac[0]
            ),
        )
        self.play(
            ReplacementTransform(
                square.copy().set_fill(opacity=0),
                square_frac[2]
            ),
        )
        self.wait(2)

        # Dar on the line
        x = np.random.random()
        y = np.sqrt(1 - x**2)
        unit = circle.get_width() / 2
        point = circle.get_center() + unit * x * RIGHT + unit * y * UP
        point += 0.004 * DOWN

        frame = self.camera_frame
        dart, dot = self.show_hit_with_dart(point)
        self.remove(dot)
        self.play(
            frame.scale, 0.05,
            frame.move_to, point,
            run_time=5,
        )


class SamplingFourRandomNumbers(Scene):
    CONFIG = {
        "n_terms": 4,
        "title_tex": "P\\left(x_0{}^2 + y_0{}^2 + x_1{}^2 + y_1{}^2 < 1\\right) = \\, ???",
        "nl_to_nl_buff": 0.75,
        "to_floor_buff": 0.5,
        "tip_scale_factor": 0.75,
        "include_half_labels": True,
        "include_title": True,
    }

    def construct(self):
        texs = ["x_0", "y_0", "x_1", "y_1", "x_2", "y_2"][:self.n_terms]
        colors = [BLUE, YELLOW, BLUE_B, YELLOW_B, BLUE_A, YELLOW_A][:self.n_terms]
        t2c = dict([(t, c) for t, c in zip(texs, colors)])

        # Title
        if self.include_title:
            title = TexMobject(
                self.title_tex,
                tex_to_color_map=t2c
            )
            title.scale(1.5)
            title.to_edge(UP)

            h_line = DashedLine(title.get_left(), title.get_right())
            h_line.next_to(title, DOWN, MED_SMALL_BUFF)

            self.add(title, h_line)

        # Number lines
        number_lines = VGroup(*[
            NumberLine(
                x_min=-1,
                x_max=1,
                tick_frequency=0.25,
                unit_size=3,
            )
            for x in range(self.n_terms)
        ])
        for line in number_lines:
            line.add_numbers(-1, 0, 1)
            if self.include_half_labels:
                line.add_numbers(
                    -0.5, 0.5,
                    number_config={"num_decimal_places": 1},
                )
        number_lines.arrange(DOWN, buff=self.nl_to_nl_buff)
        number_lines.to_edge(LEFT, buff=0.5)
        number_lines.to_edge(DOWN, buff=self.to_floor_buff)

        self.add(number_lines)

        # Trackers
        trackers = Group(*[ValueTracker(0) for x in range(self.n_terms)])
        tips = VGroup(*[
            ArrowTip(
                start_angle=-PI / 2,
                color=color
            ).scale(self.tip_scale_factor)
            for color in colors
        ])
        labels = VGroup(*[
            TexMobject(tex)
            for tex in texs
        ])

        for tip, tracker, line, label in zip(tips, trackers, number_lines, labels):
            tip.line = line
            tip.tracker = tracker
            tip.add_updater(lambda t: t.move_to(
                t.line.n2p(t.tracker.get_value()), DOWN
            ))

            label.tip = tip
            label.match_color(tip)
            label.arrange(RIGHT, buff=MED_SMALL_BUFF)
            label.add_updater(lambda l: l.next_to(l.tip, UP, SMALL_BUFF))
            # label.add_updater(lambda l: l[1].set_value(l.tip.tracker.get_value()))

        self.add(tips, labels)

        # Write bit sum
        summands = VGroup(*[
            TexMobject("\\big(", "+0.00", "\\big)^2").set_color(color)
            for color in colors
        ])
        summands.arrange(DOWN)
        summands.to_edge(RIGHT, buff=3)
        for summand, tracker in zip(summands, trackers):
            dec = DecimalNumber(include_sign=True)
            dec.match_color(summand)
            dec.tracker = tracker
            dec.add_updater(lambda d: d.set_value(d.tracker.get_value()))
            dec.move_to(summand[1])
            summand.submobjects[1] = dec

        h_line = Line(LEFT, RIGHT)
        h_line.set_width(3)
        h_line.next_to(summands, DOWN, aligned_edge=RIGHT)
        plus = TexMobject("+")
        plus.next_to(h_line.get_left(), UR)
        h_line.add(plus)

        total = DecimalNumber()
        total.scale(1.5)
        total.next_to(h_line, DOWN)
        total.match_x(summands)
        total.add_updater(lambda d: d.set_value(np.sum([
            t.get_value()**2 for t in trackers
        ])))

        VGroup(summands, h_line, total).shift_onto_screen()
        self.add(summands, h_line, total)

        # < or > 1
        lt, gt = signs = VGroup(
            TexMobject("< 1 \\quad \\checkmark"),
            TexMobject("\\ge 1 \\quad"),
        )
        for sign in signs:
            sign.scale(1.5)
            sign.next_to(total, RIGHT, MED_LARGE_BUFF)
        lt.set_color(GREEN)
        gt.set_color(RED)

        def update_signs(signs):
            i = int(total.get_value() > 1)
            signs[1 - i].set_opacity(0)
            signs[i].set_opacity(1)

        signs.add_updater(update_signs)

        self.add(signs)

        # Run simulation
        for x in range(9):
            trackers.generate_target()
            for t in trackers.target:
                t.set_value(np.random.uniform(-1, 1))

            if x == 8:
                for t in trackers.target:
                    t.set_value(np.random.uniform(-0.5, 0.5))

            self.remove(signs)
            self.play(MoveToTarget(trackers))
            self.add(signs)
            self.wait()

        # Less than 0.5
        nl = number_lines[0]
        line = Line(nl.n2p(-0.5), nl.n2p(0.5))
        rect = Rectangle(height=0.25)
        rect.set_stroke(width=0)
        rect.set_fill(GREEN, 0.5)
        rect.match_width(line, stretch=True)
        rects = VGroup(*[
            rect.copy().move_to(line.n2p(0))
            for line in number_lines
        ])

        self.play(LaggedStartMap(GrowFromCenter, rects))
        self.wait()
        self.play(LaggedStartMap(FadeOut, rects))

        # Set one to 0.5
        self.play(trackers[0].set_value, 0.9)
        self.play(ShowCreationThenFadeAround(summands[0]))
        self.wait()
        self.play(LaggedStart(*[
            ShowCreationThenFadeAround(summand)
            for summand in summands[1:]
        ]))
        self.play(*[
            ApplyMethod(tracker.set_value, 0.1)
            for tracker in trackers[1:]
        ])
        self.wait(10)


class SamplingTwoRandomNumbers(SamplingFourRandomNumbers):
    CONFIG = {
        "n_terms": 2,
        "title_tex": "P\\left(x_0{}^2 + y_0{}^2 < 1\\right) = \\, ???",
        "nl_to_nl_buff": 1,
        "to_floor_buff": 2,
        "random_seed": 1,
    }


class SamplingSixRandomNumbers(SamplingFourRandomNumbers):
    CONFIG = {
        "n_terms": 6,
        "nl_to_nl_buff": 0.5,
        "include_half_labels": False,
        "include_title": False,
        "tip_scale_factor": 0.5,
    }


class SamplePointIn3d(SpecialThreeDScene):
    def construct(self):
        axes = self.axes = self.get_axes()
        sphere = self.get_sphere()
        sphere.set_fill(BLUE_E, 0.25)
        sphere.set_stroke(opacity=0.5)

        cube = Cube()
        cube.replace(sphere)
        cube.set_fill(GREY, 0.2)
        cube.set_stroke(WHITE, 1, opacity=0.5)

        self.set_camera_orientation(
            phi=80 * DEGREES,
            theta=-120 * DEGREES,
        )
        self.begin_ambient_camera_rotation(rate=0.03)

        dot = Sphere()
        # dot = Dot()
        dot.set_shade_in_3d(True)
        dot.set_width(0.1)

        dot.move_to(axes.c2p(*np.random.uniform(0, 1, size=3)))
        lines = always_redraw(lambda: self.get_lines(dot.get_center()))
        labels = always_redraw(lambda: self.get_labels(lines))

        self.add(axes)
        self.add(cube)

        for line, label in zip(lines, labels):
            self.play(
                ShowCreation(line),
                FadeIn(label)
            )
        self.add(lines, labels)
        self.play(GrowFromCenter(dot))
        self.play(DrawBorderThenFill(sphere, stroke_width=1))
        self.wait(2)

        n_points = 3000
        points = [
            axes.c2p(*np.random.uniform(-1, 1, 3))
            for x in range(n_points)
        ]
        # point_cloud = PMobject().add_points(points)
        dots = VGroup(*[
            Dot(
                point,
                radius=0.01,
                shade_in_3d=True,
            )
            for point in points
        ])
        dots.set_stroke(WHITE, 2)
        dots.set_opacity(0.5)
        self.play(ShowIncreasingSubsets(dots, run_time=9))
        # self.play(ShowCreation(point_cloud, run_time=3))
        self.wait(4)
        return

        for x in range(6):
            self.play(
                point.move_to,
                axes.c2p(*np.random.uniform(-1, 1, size=3))
            )
            self.wait(2)
        self.wait(7)

    def get_lines(self, point):
        axes = self.axes
        x, y, z = axes.p2c(point)
        p0 = axes.c2p(0, 0, 0)
        p1 = axes.c2p(x, 0, 0)
        p2 = axes.c2p(x, y, 0)
        p3 = axes.c2p(x, y, z)
        x_line = DashedLine(p0, p1, color=GREEN)
        y_line = DashedLine(p1, p2, color=RED)
        z_line = DashedLine(p2, p3, color=BLUE)
        lines = VGroup(x_line, y_line, z_line)
        lines.set_shade_in_3d(True)
        return lines

    def get_labels(self, lines):
        x_label = TexMobject("x")
        y_label = TexMobject("y")
        z_label = TexMobject("z")
        result = VGroup(x_label, y_label, z_label)
        result.rotate(90 * DEGREES, RIGHT)
        result.set_shade_in_3d(True)

        x_line, y_line, z_line = lines

        x_label.match_color(x_line)
        y_label.match_color(y_line)
        z_label.match_color(z_line)

        x_label.next_to(x_line, IN, SMALL_BUFF)
        y_label.next_to(y_line, RIGHT + OUT, SMALL_BUFF)
        z_label.next_to(z_line, RIGHT, SMALL_BUFF)

        return result


class OverlayToPointIn3d(Scene):
    def construct(self):
        t2c = {
            "{x}": GREEN,
            "{y}": RED,
            "{z}": BLUE,
        }
        ineq = TexMobject(
            "{x}^2 + {y}^2 + {z}^2 < 1",
            tex_to_color_map=t2c,
        )
        ineq.scale(1.5)
        ineq.move_to(FRAME_WIDTH * LEFT / 4)
        ineq.to_edge(UP)

        equiv = TexMobject("\\Leftrightarrow")
        equiv.scale(2)
        equiv.match_y(ineq)

        rhs = TextMobject(
            "$({x}, {y}, {z})$",
            " lies within a\\\\sphere with radius 1"
        )
        rhs[0][1].set_color(GREEN)
        rhs[0][3].set_color(RED)
        rhs[0][5].set_color(BLUE)
        rhs.scale(1.3)
        rhs.next_to(equiv, RIGHT)
        rhs.to_edge(UP)

        self.add(ineq)
        self.wait()
        self.play(Write(equiv))
        self.wait()
        self.play(FadeIn(rhs))
        self.wait()


class TwoDPlusTwoDEqualsFourD(HyperdartScene):
    def construct(self):
        board = VGroup(*self.mobjects)

        unit_size = 1.5
        axes = Axes(
            x_min=-1.25,
            x_max=1.25,
            y_min=-1.25,
            y_max=1.25,
            axis_config={
                "unit_size": unit_size,
                "tick_frequency": 0.5,
                "include_tip": False,
            }
        )
        board.set_height(2 * unit_size)
        axes.move_to(board)
        axes.set_stroke(width=1)

        board.add(axes)
        board.to_edge(LEFT)
        self.add(board)

        # Set up titles
        kw = {
            "tex_to_color_map": {
                "x_0": WHITE,
                "y_0": WHITE,
                "x_1": WHITE,
                "y_1": WHITE,
            }
        }
        title1 = VGroup(
            TextMobject("First shot"),
            TexMobject("(x_0, y_0)", **kw),
        )
        title2 = VGroup(
            TextMobject("Second shot"),
            TexMobject("(x_1, y_1)", **kw),
        )
        title3 = VGroup(
            TextMobject("Point in 4d space"),
            TexMobject("(x_0, y_0, x_1, y_1)", **kw)
        )
        titles = VGroup(title1, title2, title3)
        for title in titles:
            title.arrange(DOWN)
        plus = TexMobject("+").scale(2)
        equals = TexMobject("=").scale(2)

        label1 = TexMobject("(x_0, y_0)")
        label2 = TexMobject("(x_1, y_1)")
        VGroup(label1, label2).scale(0.8)

        title1.next_to(board, UP)

        # First hit
        point1 = axes.c2p(0.5, 0.7)
        dart1, dot1 = self.show_hit_with_dart(point1)
        label1.next_to(dot1, UR, buff=0)
        self.add(title1, label1)
        # lines1 = self.show_geometry(point1, pace="fast")
        # chord_and_shadow1 = self.show_circle_shrink(lines1[1], pace="fast")

        board_copy = board.copy()
        board_copy.next_to(board, RIGHT, buff=LARGE_BUFF)
        self.square = board_copy[0]

        title2.next_to(board_copy, UP)
        plus.move_to(titles[:2])

        self.play(ReplacementTransform(board.copy().fade(1), board_copy))
        point2 = self.get_random_point()
        dart2, dot2 = self.show_hit_with_dart(point2)
        label2.next_to(dot2, UR, buff=0)
        self.add(plus, title2, label2)
        self.wait()

        # Set up the other titles
        title3.to_edge(RIGHT)
        title3.match_y(title2)

        equals.move_to(midpoint(title2.get_right(), title3.get_left()))

        randy = Randolph(height=2.5)
        randy.next_to(title3, DOWN, buff=LARGE_BUFF)
        randy.look_at(title3)

        kw = {"path_arc": -20 * DEGREES}
        self.play(
            LaggedStart(
                *[
                    TransformFromCopy(
                        title1[1].get_part_by_tex(tex),
                        title3[1].get_part_by_tex(tex),
                        **kw
                    )
                    for tex in ["(", "x_0", ",", "y_0"]
                ],
                *[
                    TransformFromCopy(
                        title2[1].get_part_by_tex(tex),
                        title3[1].get_parts_by_tex(tex)[-1],
                        **kw
                    )
                    for tex in ["x_1", ",", "y_1", ")"]
                ],
                TransformFromCopy(
                    title2[1].get_part_by_tex(","),
                    title3[1].get_parts_by_tex(",")[1],
                    **kw
                ),
                lag_ratio=0.01,
            ),
            Write(equals),
        )
        self.play(
            FadeInFromDown(title3[0]),
            FadeIn(randy),
        )
        self.play(randy.change, "horrified")
        self.play(Blink(randy))
        self.wait()
        self.play(randy.change, "confused")
        self.play(Blink(randy))
        self.wait()


class ExpectedValueComputation(Scene):
    def construct(self):
        t2c = {
            "0": MAROON_C,
            "1": BLUE,
            "2": GREEN,
            "3": YELLOW,
            "4": RED,
        }

        line1 = TexMobject(
            "E[S]", "=",
            "1 \\cdot", "P(S = 1)", "+",
            "2 \\cdot", "P(S = 2)", "+",
            "3 \\cdot", "P(S = 3)", "+",
            "\\cdots",
            tex_to_color_map=t2c
        )
        line2 = TexMobject(
            "=&\\phantom{-}",
            "1 \\cdot", "\\big(", "P(S > 0)", "-", "P(S > 1)", "\\big)", "\\\\&+",
            "2 \\cdot", "\\big(", "P(S > 1)", "-", "P(S > 2)", "\\big)", "\\\\&+",
            "3 \\cdot", "\\big(", "P(S > 2)", "-", "P(S > 3)", "\\big)", "\\\\&+",
            "\\cdots",
            tex_to_color_map=t2c
        )
        line2[1:12].align_to(line2[13], LEFT)
        line3 = TexMobject(
            "=",
            "P(S > 0)", "+",
            "P(S > 1)", "+",
            "P(S > 2)", "+",
            "P(S > 3)", "+",
            "\\cdots",
            tex_to_color_map=t2c,
        )

        line1.to_corner(UL)
        line2.next_to(line1, DOWN, buff=MED_LARGE_BUFF)
        line2.align_to(line1[1], LEFT)
        line3.next_to(line2, DOWN, buff=MED_LARGE_BUFF)
        line3.align_to(line1[1], LEFT)

        # Write line 1
        self.add(line1[:2])
        self.play(Write(line1[2:7]))
        self.wait()
        self.play(FadeIn(line1[7]))
        self.play(Write(line1[8:13]))
        self.wait()
        self.play(FadeIn(line1[13]))
        self.play(Write(line1[14:19]))
        self.wait()
        self.play(Write(line1[19:]))
        self.wait()

        # line 2 scaffold
        kw = {
            "path_arc": 90 * DEGREES
        }
        bigs = line2.get_parts_by_tex("big")
        self.play(
            LaggedStart(
                TransformFromCopy(
                    line1.get_part_by_tex("="),
                    line2.get_part_by_tex("="),
                    **kw
                ),
                TransformFromCopy(
                    line1.get_parts_by_tex("\\cdot"),
                    line2.get_parts_by_tex("\\cdot"),
                    **kw
                ),
                TransformFromCopy(
                    line1.get_parts_by_tex("+"),
                    line2.get_parts_by_tex("+"),
                    **kw
                ),
                TransformFromCopy(
                    line1.get_part_by_tex("1"),
                    line2.get_part_by_tex("1"),
                    **kw
                ),
                TransformFromCopy(
                    line1.get_part_by_tex("2"),
                    line2.get_part_by_tex("2"),
                    **kw
                ),
                TransformFromCopy(
                    line1.get_part_by_tex("3"),
                    line2.get_part_by_tex("3"),
                    **kw
                ),
                run_time=3,
                lag_ratio=0,
            ),
            LaggedStart(*[
                GrowFromCenter(bigs[i:i + 2])
                for i in range(0, len(bigs), 2)
            ])
        )
        self.wait()

        # Expand out sum
        for n in range(3):
            i = 6 * n
            j = 12 * n

            rect1 = SurroundingRectangle(line1[i + 4:i + 7])
            rect2 = SurroundingRectangle(line2[j + 4:j + 11])
            color = line1[i + 5].get_color()
            VGroup(rect1, rect2).set_stroke(color, 2)

            self.play(ShowCreation(rect1))
            self.play(
                TransformFromCopy(
                    line1[i + 4:i + 7],
                    line2[j + 4:j + 7],
                ),
                TransformFromCopy(
                    line1[i + 4:i + 7],
                    line2[j + 8:j + 11],
                ),
                FadeIn(line2[j + 7]),
                ReplacementTransform(rect1, rect2),
            )
            self.play(FadeOut(rect2))

        # Show telescoping
        line2.generate_target()
        line2.target.set_opacity(0.2)
        line2.target[4:7].set_opacity(1)

        self.play(MoveToTarget(line2))
        self.wait()
        self.play(
            TransformFromCopy(line2[0], line3[0]),
            TransformFromCopy(line2[4:7], line3[1:4]),
        )
        self.wait()

        line2.target.set_opacity(0.2)
        VGroup(
            line2.target[1:4],
            line2.target[7:12],
            line2.target[12:19],
            line2.target[23],
        ).set_opacity(1)

        self.play(MoveToTarget(line2))
        self.wait()
        self.play(
            TransformFromCopy(line2[12], line3[4]),
            TransformFromCopy(line2[16:19], line3[5:8]),
        )
        self.wait()

        n = 12
        line2.target.set_opacity(0.2)
        VGroup(
            line2.target[n + 1:n + 4],
            line2.target[n + 7:n + 12],
            line2.target[n + 12:n + 19],
            line2.target[n + 23],
        ).set_opacity(1)

        self.play(MoveToTarget(line2))
        self.wait()
        self.play(
            TransformFromCopy(line2[n + 12], line3[8]),
            TransformFromCopy(line2[n + 16:n + 19], line3[9:12]),
        )
        self.wait()
        self.play(Write(line3[12:]))
        self.wait()

        rect = SurroundingRectangle(line3, buff=MED_SMALL_BUFF)
        rect.set_stroke(WHITE, 2)
        self.play(ShowCreation(rect))
        self.wait()

        self.wait(3)


class SubtractHistogramParts(ShowDistributionOfScores):
    def construct(self):
        n_scores = 10000
        scores = np.array([self.get_random_score() for x in range(n_scores)])
        axes = self.get_axes()
        bars = self.get_histogram_bars(axes)
        self.set_histogram_bars(bars, scores, axes)

        self.add(axes)
        self.add(bars)

        # P(S = 2)
        p2_arrow = Vector(
            0.75 * DOWN,
            max_stroke_width_to_length_ratio=10,
            max_tip_length_to_length_ratio=0.35,
        )
        p2_arrow.next_to(bars[1], UP, SMALL_BUFF)
        p2_arrow = VGroup(
            p2_arrow.copy().set_stroke(BLACK, 9),
            p2_arrow,
        )

        p2_label = TexMobject("P(S = 2)")
        p2_label.next_to(p2_arrow, UP, SMALL_BUFF)
        p2_label.set_color(bars[1].get_fill_color())

        self.play(
            GrowFromPoint(p2_arrow, p2_arrow.get_top()),
            FadeInFromDown(p2_label),
            bars[0].set_opacity, 0.1,
            bars[2:].set_opacity, 0.1,
        )
        self.wait()

        # Culumative probabilities
        rhs = TexMobject("=", "P(S > 1)", "-", "P(S > 2)")
        rhs[1].set_color(YELLOW)
        rhs[3].set_color(bars[2].get_fill_color())
        rhs[2:].set_opacity(0.2)
        rhs.next_to(p2_label, RIGHT)

        brace1 = Brace(bars[1:5], UP)[0]
        brace1.next_to(rhs[1], DOWN)
        brace1.match_color(rhs[1])

        rf = 3.5
        lf = 1.4
        brace1[:2].stretch(rf, 0, about_edge=LEFT)
        brace1[0].stretch(1 / rf, 0, about_edge=LEFT)
        brace1[4:].stretch(lf, 0, about_edge=RIGHT)
        brace1[5:].stretch(1 / lf, 0, about_edge=RIGHT)

        brace2 = Brace(bars[2:], UP)
        brace2.match_color(rhs[3])
        brace2.set_width(10, about_edge=LEFT)
        brace2.shift(1.5 * UP)

        self.add(brace1, p2_arrow)
        self.play(
            FadeIn(rhs),
            bars[2:].set_opacity, 1,
            GrowFromPoint(brace1, rhs[1].get_bottom()),
            p2_arrow.set_opacity, 0.5,
        )
        self.wait()
        self.play(
            rhs[:2].set_opacity, 0.2,
            brace1.set_opacity, 0.2,
            rhs[2:].set_opacity, 1,
            bars[1].set_opacity, 0.1,
            GrowFromCenter(brace2),
        )
        self.wait()

        self.play(
            bars[2:].set_opacity, 0.1,
            bars[1].set_opacity, 1,
            rhs.set_opacity, 1,
            brace1.set_opacity, 1,
            p2_arrow.set_opacity, 1,
        )
        self.wait()


        # for i, part in enumerate(brace1):
        #     self.add(Integer(i).scale(0.5).move_to(part))


class GameWithSpecifiedScore(HyperdartScene):
    CONFIG = {
        "score": 1,
        "random_seed": 1,
    }

    def construct(self):
        board = VGroup(self.square, self.circle, self.circle_center_dot)
        board.to_edge(DOWN, buff=0.5)

        score_label = VGroup(
            TextMobject("Score: "),
            Integer(1)
        )
        score_label.scale(2)
        score_label.arrange(RIGHT, aligned_edge=DOWN)
        score_label.to_edge(UP, buff=0.25)

        self.add(score_label)

        score = 1
        pace = "fast"
        while True:
            point = self.get_random_point()
            want_to_continue = (score < self.score)
            if want_to_continue:
                while not self.is_inside(point):
                    point = self.get_random_point()

                dart, dot = self.show_hit_with_dart(point)
                score_label[1].increment_value()
                lines = self.show_geometry(point, pace)
                chord_and_shadow = self.show_circle_shrink(lines[1], pace=pace)

                self.play(
                    FadeOut(VGroup(dart, dot, lines, chord_and_shadow)),
                    run_time=0.5,
                )
                score += 1
            else:
                while self.is_inside(point):
                    point = self.get_random_point()
                self.show_miss(point)
                self.play(ShowCreationThenFadeAround(score_label[1]))
                self.wait()
                return


class Score1Game(GameWithSpecifiedScore):
    CONFIG = {
        "score": 1,
    }


class Score2Game(GameWithSpecifiedScore):
    CONFIG = {
        "score": 2,
    }


class Score3Game(GameWithSpecifiedScore):
    CONFIG = {
        "score": 3,
    }


class Score4Game(GameWithSpecifiedScore):
    CONFIG = {
        "score": 4,
    }


class HistogramScene(ShowDistributionOfScores):
    CONFIG = {
        "n_scores": 10000,
        "mean_line_height": 4,
    }

    def setup(self):
        self.scores = np.array([
            self.get_random_score()
            for x in range(self.n_scores)
        ])
        self.axes = self.get_axes()
        self.bars = self.get_histogram_bars(self.axes)
        self.set_histogram_bars(self.bars, self.scores, self.axes)

        self.add(self.axes)
        self.add(self.bars)

    def get_mean_label(self):
        mean_line = DashedLine(ORIGIN, self.mean_line_height * UP)
        mean_line.set_stroke(YELLOW, 2)

        mean = np.mean(self.scores)
        mean_line.move_to(self.axes.c2p(mean, 0), DOWN)
        mean_label = VGroup(
            *TextMobject("E[S]", "="),
            DecimalNumber(mean, num_decimal_places=3),
        )
        mean_label.arrange(RIGHT)
        mean_label.match_color(mean_line)
        mean_label.next_to(
            mean_line.get_end(), UP, SMALL_BUFF,
            index_of_submobject_to_align=0,
        )

        return VGroup(mean_line, *mean_label)


class ExpectedValueFromBars(HistogramScene):
    def construct(self):
        axes = self.axes
        bars = self.bars
        mean_label = self.get_mean_label()
        mean_label.remove(mean_label[-1])

        equation = TexMobject(
            "P(S = 1)", "\\cdot", "1", "+",
            "P(S = 2)", "\\cdot", "2", "+",
            "P(S = 3)", "\\cdot", "3", "+",
            "\\cdots"
        )
        equation.scale(0.9)
        equation.next_to(mean_label[-1], RIGHT)
        equation.shift(LEFT)

        for i in range(3):
            equation.set_color_by_tex(
                str(i + 1), bars[i].get_fill_color()
            )

        equation[4:].set_opacity(0.2)

        self.add(mean_label)
        self.play(
            mean_label[1:].shift, LEFT,
            FadeInFrom(equation, LEFT)
        )

        p_parts = VGroup()
        p_part_copies = VGroup()
        for i in range(3):
            bar = bars[i]
            num = axes.x_axis.numbers[i]
            p_part = equation[4 * i]
            s_part = equation[4 * i + 2]

            p_part_copy = p_part.copy()
            p_part_copy.set_width(0.8 * bar.get_width())
            p_part_copy.next_to(bar, UP, SMALL_BUFF)
            p_part_copy.set_opacity(1)

            self.remove(mean_label[0])
            self.play(
                bars[:i + 1].set_opacity, 1,
                bars[i + 1:].set_opacity, 0.2,
                equation[:4 * (i + 1)].set_opacity, 1,
                FadeInFromDown(p_part_copy),
                Animation(mean_label[0]),
            )
            kw = {
                "surrounding_rectangle_config": {
                    "color": bar.get_fill_color(),
                    "buff": 0.5 * SMALL_BUFF,
                }
            }
            self.play(
                LaggedStart(
                    AnimationGroup(
                        ShowCreationThenFadeAround(p_part, **kw),
                        ShowCreationThenFadeAround(p_part_copy, **kw),
                    ),
                    AnimationGroup(
                        ShowCreationThenFadeAround(s_part, **kw),
                        ShowCreationThenFadeAround(num, **kw),
                    ),
                    lag_ratio=0.5,
                )
            )
            self.wait()
            p_parts.add(p_part)
            p_part_copies.add(p_part_copy)

        self.add(bars, mean_label)
        self.play(
            bars.set_opacity, 1,
            equation.set_opacity, 1,
            FadeOut(p_part_copies)
        )

        braces = VGroup(*[
            Brace(p_part, UP)
            for p_part in p_parts
        ])
        for brace in braces:
            brace.add(brace.get_text("???"))

        self.play(LaggedStartMap(FadeIn, braces))
        self.wait()


class ProbabilitySGtOne(HistogramScene):
    def construct(self):
        axes = self.axes
        bars = self.bars

        brace = Brace(bars[1:], UP)
        label = brace.get_tex("P(S > 1)")
        brace[0][:2].stretch(1.5, 0, about_edge=LEFT)

        outlines = bars[1:].copy()
        for bar in outlines:
            bar.set_stroke(bar.get_fill_color(), 2)
            bar.set_fill(opacity=0)

        self.play(
            GrowFromEdge(brace, LEFT),
            bars[0].set_opacity, 0.2,
            bars[1:].set_opacity, 0.8,
            ShowCreationThenFadeOut(outlines),
            FadeInFrom(label, LEFT),
        )
        self.wait()

        square = Square()
        square.set_fill(BLUE, 0.75)
        square.set_stroke(WHITE, 1)
        square.set_height(0.5)

        circle = Circle()
        circle.set_fill(RED, 0.75)
        circle.set_stroke(WHITE, 1)
        circle.set_height(0.5)

        bar = Line(LEFT, RIGHT)
        bar.set_stroke(WHITE, 3)
        bar.set_width(0.5)

        geo_frac = VGroup(circle, bar, square)
        geo_frac.arrange(DOWN, SMALL_BUFF, buff=SMALL_BUFF)

        rhs = VGroup(
            TexMobject("="),
            geo_frac,
            TexMobject("= \\frac{\\pi}{4}")
        )
        rhs.arrange(RIGHT)
        rhs.next_to(label)

        shift_val = 2.05 * LEFT + 0.25 * UP
        rhs.shift(shift_val)

        self.play(
            label.shift, shift_val,
            FadeInFrom(rhs, LEFT)
        )
        self.wait()

        # P(S > 2)
        new_brace = brace.copy()
        new_brace.next_to(
            bars[2], UP,
            buff=SMALL_BUFF,
            aligned_edge=LEFT,
        )
        self.add(new_brace)

        new_label = TexMobject(
            "P(S > 2)", "=", "\\,???"
        )
        new_label.next_to(new_brace[0][2], UP)

        self.play(
            bars[1].set_opacity, 0.2,
            label.set_opacity, 0.5,
            rhs.set_opacity, 0.5,
            brace.set_opacity, 0.5,
            GrowFromEdge(new_brace, LEFT),
            ReplacementTransform(
                new_label.copy().fade(1).move_to(label, LEFT),
                new_label,
            )
        )
        self.wait()

        new_rhs = TexMobject(
            "{\\text{4d ball}", " \\over", " \\text{4d cube}}",
            # "=",
            # "{\\pi^2 / 2", "\\over", "2^4}"
        )
        new_rhs[0].set_color(RED)
        new_rhs[2].set_color(BLUE)
        new_rhs.move_to(new_label[-1], LEFT)
        shift_val = 0.75 * LEFT + 0.15 * UP

        new_rhs.shift(shift_val)

        new_label.generate_target()
        new_label.target.shift(shift_val)
        new_label.target[-1].set_opacity(0)

        self.play(
            MoveToTarget(new_label),
            FadeInFrom(new_rhs, LEFT)
        )
        self.wait()

        # P(S > 3)
        final_brace = brace.copy()
        final_brace.set_opacity(1)
        final_brace.next_to(
            bars[3], UP,
            buff=SMALL_BUFF,
            aligned_edge=LEFT,
        )
        self.add(final_brace)

        final_label = TexMobject("P(S > 3)")
        final_label.next_to(final_brace[0][2], UP, SMALL_BUFF)

        self.play(
            bars[2].set_opacity, 0.2,
            new_label[:-1].set_opacity, 0.5,
            new_rhs.set_opacity, 0.5,
            new_brace.set_opacity, 0.5,
            GrowFromEdge(final_brace, LEFT),
            ReplacementTransform(
                final_label.copy().fade(1).move_to(new_label, LEFT),
                final_label,
            ),
            axes.x_axis[-1].set_opacity, 0,
        )
        self.wait()


class VolumsOfNBalls(Scene):
    def construct(self):
        title, alt_title = [
            TextMobject(
                "Volumes of " + tex + "-dimensional balls",
                tex_to_color_map={tex: YELLOW},
            )
            for tex in ["$N$", "$2n$"]
        ]
        for mob in [title, alt_title]:
            mob.scale(1.5)
            mob.to_edge(UP)

        formulas = VGroup(*[
            TexMobject(
                tex,
                tex_to_color_map={"R": WHITE}
            )
            for tex in [
                "2R",
                "\\pi R^2",
                "\\frac{4}{3} \\pi R^3",
                "\\frac{1}{2} \\pi^2 R^4",
                "\\frac{8}{15} \\pi^2 R^5",
                "\\frac{1}{6} \\pi^3 R^6",
                "\\frac{16}{105} \\pi^3 R^7",
                "\\frac{1}{24} \\pi^4 R^8",
                "\\frac{32}{945} \\pi^4 R^9",
                "\\frac{1}{120} \\pi^5 R^{10}",
                "\\frac{64}{10{,}395} \\pi^5 R^{11}",
                "\\frac{1}{720} \\pi^6 R^{12}",
            ]
        ])

        formulas.arrange(RIGHT, buff=LARGE_BUFF)
        formulas.scale(0.9)
        formulas.to_edge(LEFT)

        lines = VGroup()
        d_labels = VGroup()
        for dim, formula in zip(it.count(1), formulas):
            label = VGroup(Integer(dim), TexMobject("D"))
            label.arrange(RIGHT, buff=0, aligned_edge=DOWN)
            label[0].set_color(YELLOW)
            label.move_to(formula)
            label.shift(UP)

            line = Line(UP, DOWN)
            line.set_stroke(WHITE, 1)
            line.next_to(formula, RIGHT, buff=MED_LARGE_BUFF)
            line.shift(0.5 * UP)

            d_labels.add(label)
            lines.add(line)
            # coefs.add(formula[0])
            formula[0].set_color(BLUE_B)
        lines.remove(lines[-1])
        line = Line(formulas.get_left(), formulas.get_right())
        line.set_stroke(WHITE, 1)
        line.next_to(d_labels, DOWN, MED_SMALL_BUFF)
        lines.add(line)

        chart = VGroup(lines, d_labels, formulas)
        chart.save_state()

        self.add(title)
        self.add(d_labels)
        self.add(lines)

        self.play(LaggedStartMap(FadeInFromDown, formulas, run_time=3, lag_ratio=0.1))
        self.play(chart.to_edge, RIGHT, {"buff": MED_SMALL_BUFF}, run_time=5)
        self.wait()
        self.play(Restore(chart))
        self.play(FadeOut(formulas[4:]))

        rect1 = SurroundingRectangle(formulas[2][0][-1])
        rect2 = SurroundingRectangle(formulas[3][0][-2:])
        self.play(ShowCreation(rect1))
        self.play(TransformFromCopy(rect1, rect2))
        self.play(FadeOut(VGroup(rect1, rect2)))

        arrows = VGroup(*[
            Arrow(
                formulas[i].get_bottom(),
                formulas[i + 1].get_bottom(),
                path_arc=150 * DEGREES,
            )
            for i in (1, 2)
        ])

        for arrow in arrows:
            self.play(ShowCreation(arrow))
        self.wait()
        self.play(
            FadeOut(arrows),
            FadeIn(formulas[4:]),
        )

        # General formula for even dimensions
        braces = VGroup(*[
            Brace(formula, DOWN)
            for formula in formulas[1::2]
        ])
        gen_form = TexMobject("{\\pi^n \\over n!}", "R^{2n}")
        gen_form[0].set_color(BLUE_B)
        gen_form.scale(1.5)
        gen_form.to_edge(DOWN)

        self.play(
            formulas[::2].set_opacity, 0.25,
            ReplacementTransform(title, alt_title)
        )
        for brace in braces[:3]:
            self.play(GrowFromCenter(brace))
        self.wait()
        self.play(
            FadeOut(braces[:3]),
            FadeInFrom(gen_form, UP),
        )
        self.wait()


class RepeatedSamplesGame(Scene):
    def construct(self):
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

