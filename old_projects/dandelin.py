from manimlib.imports import *

from old_projects.lost_lecture import Orbiting
from old_projects.lost_lecture import ShowWord


class LogoGeneration(LogoGenerationTemplate):
    CONFIG = {
        "random_seed": 2,
    }

    def get_logo_animations(self, logo):
        layers = logo.spike_layers
        for layer in layers:
            random.shuffle(layer.submobjects)
            for spike in layer:
                spike.save_state()
                spike.scale(0.5)
                spike.apply_complex_function(np.log)
                spike.rotate(-90 * DEGREES, about_point=ORIGIN)
                spike.set_fill(opacity=0)

        return [
            FadeIn(
                logo.iris_background,
                rate_func=squish_rate_func(smooth, 0.25, 1),
                run_time=3,
            ),
            AnimationGroup(*[
                LaggedStartMap(
                    Restore, layer,
                    run_time=3,
                    path_arc=180 * DEGREES,
                    rate_func=squish_rate_func(smooth, a / 3.0, (a + 0.9) / 3.0),
                    lag_ratio=0.8,
                )
                for layer, a in zip(layers, [0, 2, 1, 0])
            ]),
            Animation(logo.pupil),
        ]


class ThinkingAboutAProof(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature
        randy.scale(0.5, about_edge=DL)
        bubble = ThoughtBubble()
        bubble.pin_to(randy)
        bubble.shift(MED_SMALL_BUFF * RIGHT)
        cloud = bubble[-1]
        cloud.rotate(90 * DEGREES)
        cloud.set_height(FRAME_HEIGHT - 0.5)
        cloud.stretch(2.8, 0)
        cloud.next_to(bubble[2], RIGHT)
        cloud.to_edge(UP, buff=0.25)
        bubble[1].shift(0.25 * UL)

        you_arrow = Vector(LEFT, color=WHITE)
        you_arrow.next_to(randy, RIGHT)
        you = TextMobject("You")
        you.next_to(you_arrow, RIGHT)
        lm_arrow = Vector(DOWN, color=WHITE)
        lm_arrow.next_to(randy, UP)
        love_math = TextMobject("Love math")
        love_math.next_to(lm_arrow, UP)
        love_math.shift_onto_screen()

        self.add(bubble)
        self.play(
            FadeInFrom(you, LEFT),
            GrowArrow(you_arrow),
        )
        self.play(
            FadeInFromDown(love_math),
            GrowArrow(lm_arrow),
            randy.change, "erm"
        )
        self.wait(2)
        self.play(
            randy.change, "pondering", cloud
        )
        self.wait(10)


class SumOfIntegersProof(Scene):
    CONFIG = {
        "n": 6,
    }

    def construct(self):
        equation = TexMobject(
            "1", "+", "2", "+", "3", "+",
            "\\cdots", "+", "n",
            "=", "\\frac{n(n+1)}{2}"
        )
        equation.scale(1.5)
        equation.to_edge(UP)
        one, two, three, dots, n = numbers = VGroup(*[
            equation.get_part_by_tex(tex, substring=False).copy()
            for tex in ("1", "2", "3", "\\cdots", "n",)
        ])
        for number in numbers:
            number.generate_target()
            number.target.scale(0.75)

        rows = self.get_rows()
        rows.next_to(equation, DOWN, buff=MED_LARGE_BUFF)
        flipped_rows = self.get_flipped_rows(rows)

        for row, num in zip(rows, [one, two, three]):
            num.target.next_to(row, LEFT)
        dots.target.rotate(90 * DEGREES)
        dots.target.next_to(rows[3:-1], LEFT)
        dots.target.align_to(one.target, LEFT)
        n.target.next_to(rows[-1], LEFT)

        for row in rows:
            row.save_state()
            for square in row:
                square.stretch(0, 0)
                square.move_to(row, LEFT)
            row.fade(1)

        self.play(LaggedStartMap(FadeInFromDown, equation[:-1]))
        self.wait()
        self.play(
            LaggedStartMap(
                MoveToTarget, numbers,
                path_arc=-90 * DEGREES,
                lag_ratio=1,
                run_time=1
            )
        )
        self.play(LaggedStartMap(Restore, rows))
        self.wait()
        self.play(
            ReplacementTransform(
                rows.copy().set_fill(opacity=0), flipped_rows,
                path_arc=-PI,
                run_time=2
            )
        )
        self.wait()
        self.play(Write(equation[-1]))
        self.wait(5)

    def get_rows(self):
        rows = VGroup()
        for count in range(1, self.n + 1):
            row = VGroup(*[Square() for k in range(count)])
            row.arrange(RIGHT, buff=0)
            rows.add(row)
        rows.arrange(DOWN, buff=0, aligned_edge=LEFT)
        rows.set_height(5)
        rows.set_stroke(WHITE, 3)
        rows.set_fill(BLUE, 0.5)
        return rows

    def get_flipped_rows(self, rows):
        result = rows.copy()
        result.rotate(PI)
        result.set_fill(RED_D, 0.5)
        result.move_to(rows, LEFT)
        result.shift(rows[0][0].get_width() * RIGHT)
        return result


class FeynmansLostLectureWrapper(Scene):
    def construct(self):
        title = TextMobject("Feynman's Lost Lecture")
        title.scale(1.5)
        title.to_edge(UP)
        rect = ScreenRectangle(height=6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()


class HoldUpProof(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("One of my all-time favorite proofs")
        title.to_edge(UP)
        self.add(title)

        self.play(
            self.teacher.change, "raise_right_hand", self.screen,
            self.get_student_changes(
                "pondering", "confused", "maybe",
                look_at_arg=title
            )
        )
        self.look_at(title)
        self.wait(5)
        self.change_student_modes(
            "happy", "thinking", "hooray",
            look_at_arg=title
        )
        self.wait(5)


class MultipleDefinitionsOfAnEllipse(Scene):
    def construct(self):
        title = Title("Multiple definitions of ``ellipse''")
        self.add(title)

        definitions = VGroup(
            TextMobject("1. Stretch a circle"),
            TextMobject("2. Thumbtack \\\\ \\quad\\, construction"),
            TextMobject("3. Slice a cone"),
        )
        definitions.arrange(
            DOWN, buff=LARGE_BUFF,
            aligned_edge=LEFT
        )
        definitions.next_to(title, DOWN, LARGE_BUFF)
        definitions.to_edge(LEFT)

        for definition in definitions:
            definition.saved_state = definition.copy()
            definition.saved_state.set_fill(LIGHT_GREY, 0.5)

        self.play(LaggedStartMap(
            FadeInFrom, definitions,
            lambda m: (m, RIGHT),
            run_time=4
        ))
        self.wait()
        for definition in definitions:
            others = [d for d in definitions if d is not definition]
            self.play(
                definition.set_fill, WHITE, 1,
                definition.scale, 1.2, {"about_edge": LEFT},
                *list(map(Restore, others))
            )
            self.wait(2)


class StretchACircle(Scene):
    def construct(self):
        plane = NumberPlane(
            x_unit_size=2,
            y_unit_size=2
        )

        circle = Circle(radius=2)
        circle.set_stroke(YELLOW, 5)
        circle_ghost = circle.copy()
        circle_ghost.set_stroke(width=1)

        plane_circle_group = VGroup(plane, circle)
        plane_circle_group.save_state()

        arrows = self.get_arrows()

        prop = 1.0 / 8
        start_point = Dot(circle.point_from_proportion(prop))
        end_point = start_point.copy().stretch(2, 0, about_point=ORIGIN)
        end_point.stretch(0.5, 0)
        end_point.set_color(RED)

        xy = TexMobject("(x, y)")
        cxy = TexMobject("(c \\cdot x, y)")
        cxy[1].set_color(RED)
        for tex in xy, cxy:
            tex.scale(1.5)
            tex.add_background_rectangle()

        xy_arrow = Vector(DOWN, color=WHITE)
        cxy_arrow = Vector(DL, color=WHITE)
        xy_arrow.next_to(start_point, UP, SMALL_BUFF)
        xy.next_to(xy_arrow, UP, SMALL_BUFF)
        cxy_arrow.next_to(end_point, UR, SMALL_BUFF)
        cxy.next_to(cxy_arrow, UR, SMALL_BUFF)

        self.add(plane_circle_group)
        self.wait()
        self.play(
            ApplyMethod(
                plane_circle_group.stretch, 2, 0,
                run_time=2,
            ),
            LaggedStartMap(
                GrowArrow, arrows,
                run_time=1,
                lag_ratio=1
            ),
        )
        self.play(FadeOut(arrows))
        self.wait()
        self.play(Restore(plane_circle_group))
        self.play(
            GrowArrow(xy_arrow),
            Write(xy),
            FadeInFrom(start_point, UP),
        )
        self.wait()
        self.add(circle_ghost)
        self.play(
            circle.stretch, 2, 0,
            ReplacementTransform(start_point.copy(), end_point),
            run_time=2
        )
        self.play(
            GrowArrow(cxy_arrow),
            Write(cxy)
        )
        self.wait(2)

    def get_arrows(self):
        result = VGroup()
        for vect in [LEFT, RIGHT]:
            for y in range(-3, 4):
                arrow = Vector(vect)
                arrow.move_to(2 * vect + y * UP)
                result.add(arrow)
        result.set_color(RED)
        return result


class ShowArrayOfEccentricities(Scene):
    def construct(self):
        eccentricities = np.linspace(0, 0.99, 6)
        eccentricity_labels = VGroup(*list(map(
            DecimalNumber, eccentricities
        )))
        ellipses = self.get_ellipse_row(eccentricities)
        ellipses.set_color_by_gradient(BLUE, YELLOW)
        ellipses.move_to(DOWN)

        for label, ellipse in zip(eccentricity_labels, ellipses):
            label.next_to(ellipse, UP)

        name = TextMobject("Eccentricity")
        name.scale(1.5)
        name.to_edge(UP)
        alt_name = TextMobject("(read ``squishification'')")
        alt_name.set_color(YELLOW)
        alt_name.next_to(name, RIGHT)
        alt_name.shift_onto_screen()
        name.generate_target()
        name.target.next_to(alt_name, LEFT)

        arrows = VGroup(*[
            Arrow(name.get_bottom(), label.get_top())
            for label in eccentricity_labels
        ])
        arrows.set_color_by_gradient(BLUE, YELLOW)

        for label, arrow in zip(eccentricity_labels, arrows):
            label.save_state()
            label.fade(1)
            label.scale(0.1)
            label.move_to(arrow.get_start())

        morty = Mortimer(height=2)
        morty.next_to(alt_name, DOWN)

        self.add(ellipses[0])
        for e1, e2 in zip(ellipses[:-1], ellipses[1:]):
            self.play(ReplacementTransform(
                e1.copy(), e2,
                path_arc=10 * DEGREES
            ))
        self.wait()

        self.play(
            Write(name),
            LaggedStartMap(GrowArrow, arrows),
            LaggedStartMap(Restore, eccentricity_labels)
        )
        self.wait()
        self.play(
            Write(alt_name),
            MoveToTarget(name),
            morty.change, "hooray", alt_name,
            VFadeIn(morty),
        )
        self.play(Blink(morty))
        self.play(morty.change, "thinking", ellipses)
        self.wait()
        self.play(Blink(morty))

        for i in 0, -1:
            e_copy = ellipses[i].copy()
            e_copy.set_color(RED)
            self.play(ShowCreation(e_copy))
            self.play(
                ShowCreationThenFadeAround(
                    eccentricity_labels[i],
                ),
                FadeOut(e_copy)
            )
        self.wait()

        circle = ellipses[0]
        group = VGroup(*it.chain(
            eccentricity_labels,
            ellipses[1:],
            arrows,
            name,
            alt_name,
            [morty]
        ))
        self.play(
            LaggedStartMap(FadeOutAndShiftDown, group),
            circle.set_height, 5,
            circle.center,
        )

    def get_ellipse(self, eccentricity, width=2):
        result = Circle(color=WHITE)
        result.set_width(width)
        a = width / 2.0
        c = eccentricity * a
        b = np.sqrt(a**2 - c**2)
        result.stretch(b / a, 1)
        result.shift(c * LEFT)

        result.eccentricity = eccentricity
        return result

    def get_ellipse_row(self, eccentricities, buff=MED_SMALL_BUFF, **kwargs):
        result = VGroup(*[
            self.get_ellipse(e, **kwargs)
            for e in eccentricities
        ])
        result.arrange(RIGHT, buff=buff)
        return result

    def get_eccentricity(self, ellipse):
        """
        Assumes that it's major/minor axes line up
        with x and y axes
        """
        a = ellipse.get_width()
        b = ellipse.get_height()
        if b > a:
            a, b = b, a
        c = np.sqrt(a**2 - b**2)
        return fdiv(c, a)


class ShowOrbits(ShowArrayOfEccentricities):
    CONFIG = {"camera_config": {"background_opacity": 1}}

    def construct(self):
        earth_eccentricity = 0.0167
        comet_eccentricity = 0.9671
        earth_orbit = self.get_ellipse(eccentricity=earth_eccentricity)
        comet_orbit = self.get_ellipse(eccentricity=comet_eccentricity)
        earth_orbit.set_height(5)
        comet_orbit.set_width(
            0.7 * FRAME_WIDTH,
            about_point=ORIGIN,
        )

        sun = ImageMobject("Sun")
        earth = ImageMobject("Earth")
        comet = ImageMobject("Comet")
        sun.set_height(1)
        earth.set_height(0.5)
        comet.set_height(0.1)

        earth_parts = VGroup(sun, earth_orbit, earth)

        eccentricity_label = DecimalNumber(
            earth_eccentricity,
            num_decimal_places=4
        )
        eccentricity_equals = TextMobject(
            "Eccentricity = "
        )
        earth_orbit_words = TextMobject("Earth's orbit")
        earth_orbit_words.set_color(BLUE)
        full_label = VGroup(
            earth_orbit_words,
            eccentricity_equals, eccentricity_label
        )
        full_label.arrange(RIGHT, SMALL_BUFF)
        earth_orbit_words.shift(0.5 * SMALL_BUFF * UL)
        full_label.to_edge(UP)

        comet_orbit_words = TextMobject("Halley's comet orbit")
        comet_orbit_words.set_color(LIGHT_GREY)
        comet_orbit_words.move_to(earth_orbit_words, RIGHT)

        orbiting_earth = Orbiting(earth, sun, earth_orbit)
        orbiting_comet = Orbiting(comet, sun, comet_orbit)

        self.add(full_label, earth_orbit_words)
        self.add(sun, earth_orbit, orbiting_earth)
        self.wait(10)
        orbiting_earth.rate = 1.5
        orbiting_comet.rate = 1.5
        self.play(
            earth_parts.set_height,
            comet_orbit.get_height() / 4.53,
            earth_parts.shift, 3 * RIGHT
        )
        comet_orbit.shift(3 * RIGHT)
        comet_orbit.save_state()
        Transform(comet_orbit, earth_orbit).update(1)
        self.play(
            Restore(comet_orbit, run_time=2),
            ChangingDecimal(
                eccentricity_label,
                lambda a: self.get_eccentricity(comet_orbit)
            ),
            FadeOutAndShift(earth_orbit_words, UP),
            FadeInFromDown(comet_orbit_words)
        )
        self.add(orbiting_comet)
        self.wait(10)


class EccentricityInThumbtackCase(ShowArrayOfEccentricities):
    def construct(self):
        ellipse = self.get_ellipse(0.2, width=5)
        ellipse_target = self.get_ellipse(0.9, width=5)
        ellipse_target.scale(fdiv(
            sum(self.get_abc(ellipse)),
            sum(self.get_abc(ellipse_target)),
        ))
        for mob in ellipse, ellipse_target:
            mob.center()
            mob.set_color(BLUE)
        thumbtack_update = self.get_thumbtack_update(ellipse)
        ellipse_point_update = self.get_ellipse_point_update(ellipse)
        focal_lines_update = self.get_focal_lines_update(
            ellipse, ellipse_point_update.mobject
        )
        focus_to_focus_line_update = self.get_focus_to_focus_line_update(ellipse)
        eccentricity_label = self.get_eccentricity_label()
        eccentricity_value_update = self.get_eccentricity_value_update(
            eccentricity_label, ellipse,
        )
        inner_brace_update = self.get_focus_line_to_focus_line_brace_update(
            focus_to_focus_line_update.mobject
        )
        outer_lines = self.get_outer_dashed_lines(ellipse)
        outer_lines_brace = Brace(outer_lines, DOWN)

        focus_distance = TextMobject("Focus distance")
        focus_distance.set_color(GREEN)
        focus_distance.next_to(inner_brace_update.mobject, DOWN, SMALL_BUFF)
        focus_distance.add_to_back(focus_distance.copy().set_stroke(BLACK, 5))
        focus_distance_update = Mobject.add_updater(
            focus_distance,
            lambda m: m.set_width(
                inner_brace_update.mobject.get_width(),
            ).next_to(inner_brace_update.mobject, DOWN, SMALL_BUFF)
        )
        diameter = TextMobject("Diameter")
        diameter.set_color(RED)
        diameter.next_to(outer_lines_brace, DOWN, SMALL_BUFF)

        fraction = TexMobject(
            "{\\text{Focus distance}", "\\over",
            "\\text{Diameter}}"
        )
        numerator = fraction.get_part_by_tex("Focus")
        numerator.set_color(GREEN)
        fraction.set_color_by_tex("Diameter", RED)
        fraction.move_to(2 * UP)
        fraction.to_edge(RIGHT, buff=MED_LARGE_BUFF)
        numerator_update = Mobject.add_updater(
            numerator,
            lambda m: m.set_width(focus_distance.get_width()).next_to(
                fraction[1], UP, MED_SMALL_BUFF
            )
        )

        fraction_arrow = Arrow(
            eccentricity_label.get_right(),
            fraction.get_top() + MED_SMALL_BUFF * UP,
            path_arc=-60 * DEGREES,
        )
        fraction_arrow.pointwise_become_partial(fraction_arrow, 0, 0.95)

        ellipse_transformation = Transform(
            ellipse, ellipse_target,
            rate_func=there_and_back,
            run_time=8,
        )

        self.add(ellipse)
        self.add(thumbtack_update)
        self.add(ellipse_point_update)
        self.add(focal_lines_update)
        self.add(focus_to_focus_line_update)
        self.add(eccentricity_label)
        self.add(eccentricity_value_update)

        self.play(ellipse_transformation)

        self.add(inner_brace_update)
        self.add(outer_lines)
        self.add(outer_lines_brace)

        self.add(fraction)
        self.add(fraction_arrow)
        self.add(focus_distance)
        self.add(diameter)

        self.add(focus_distance_update)
        self.add(numerator_update)

        self.play(
            ellipse_transformation,
            VFadeIn(inner_brace_update.mobject),
            VFadeIn(outer_lines),
            VFadeIn(outer_lines_brace),
            VFadeIn(fraction),
            VFadeIn(fraction_arrow),
            VFadeIn(focus_distance),
            VFadeIn(diameter),
        )

    def get_thumbtack_update(self, ellipse):
        thumbtacks = VGroup(*[
            self.get_thumbtack()
            for x in range(2)
        ])

        def update_thumbtacks(thumbtacks):
            foci = self.get_foci(ellipse)
            for thumbtack, focus in zip(thumbtacks, foci):
                thumbtack.move_to(focus, DR)
            return thumbtacks

        return Mobject.add_updater(thumbtacks, update_thumbtacks)

    def get_ellipse_point_update(self, ellipse):
        dot = Dot(color=RED)
        return cycle_animation(MoveAlongPath(
            dot, ellipse,
            run_time=5,
            rate_func=linear
        ))

    def get_focal_lines_update(self, ellipse, ellipse_point):
        lines = VGroup(*[Line(LEFT, RIGHT) for x in range(2)])
        lines.set_color_by_gradient(YELLOW, PINK)

        def update_lines(lines):
            foci = self.get_foci(ellipse)
            Q = ellipse_point.get_center()
            for line, focus in zip(lines, foci):
                line.put_start_and_end_on(focus, Q)
            return lines

        return Mobject.add_updater(lines, update_lines)

    def get_focus_to_focus_line_update(self, ellipse):
        return Mobject.add_updater(
            Line(LEFT, RIGHT, color=WHITE),
            lambda m: m.put_start_and_end_on(*self.get_foci(ellipse))
        )

    def get_focus_line_to_focus_line_brace_update(self, line):
        brace = Brace(Line(LEFT, RIGHT))
        brace.add_to_back(brace.copy().set_stroke(BLACK, 5))
        return Mobject.add_updater(
            brace,
            lambda b: b.match_width(line, stretch=True).next_to(
                line, DOWN, buff=SMALL_BUFF
            )
        )

    def get_eccentricity_label(self):
        words = TextMobject("Eccentricity = ")
        decimal = DecimalNumber(0, num_decimal_places=2)
        group = VGroup(words, decimal)
        group.arrange(RIGHT)
        group.to_edge(UP)
        return group

    def get_eccentricity_value_update(self, eccentricity_label, ellipse):
        decimal = eccentricity_label[1]
        decimal.add_updater(lambda d: d.set_value(
            self.get_eccentricity(ellipse)
        ))
        return decimal

    def get_outer_dashed_lines(self, ellipse):
        line = DashedLine(2.5 * UP, 2.5 * DOWN)
        return VGroup(
            line.move_to(ellipse, RIGHT),
            line.copy().move_to(ellipse, LEFT),
        )

    #
    def get_abc(self, ellipse):
        a = ellipse.get_width() / 2
        b = ellipse.get_height() / 2
        c = np.sqrt(a**2 - b**2)
        return a, b, c

    def get_foci(self, ellipse):
        a, b, c = self.get_abc(ellipse)
        return [
            ellipse.get_center() + c * RIGHT,
            ellipse.get_center() + c * LEFT,
        ]

    def get_thumbtack(self):
        angle = 10 * DEGREES
        result = SVGMobject(file_name="push_pin")
        result.set_height(0.5)
        result.set_fill(LIGHT_GREY)
        result.rotate(angle)
        return result


class EccentricityForSlicedConed(Scene):
    def construct(self):
        equation = TexMobject(
            "\\text{Eccentricity} = ",
            "{\\sin(", "\\text{angle of plane}", ")", "\\over",
            "\\sin(", "\\text{angle of cone slant}", ")}"
        )
        equation.set_color_by_tex("plane", YELLOW)
        equation.set_color_by_tex("cone", BLUE)
        equation.to_edge(LEFT)
        self.play(FadeInFromDown(equation))


class AskWhyAreTheyTheSame(TeacherStudentsScene):
    def construct(self):
        morty = self.teacher
        self.student_says(
            "Why on earth \\\\ are these the same?",
            student_index=2,
            target_mode="sassy",
            bubble_kwargs={"direction": LEFT}
        )
        bubble = self.students[2].bubble
        self.play(
            morty.change, "awe",
            self.get_student_changes("confused", "confused", "sassy")
        )
        self.look_at(self.screen)
        self.wait(3)
        self.play(morty.change, "thinking", self.screen)
        self.change_student_modes("maybe", "erm", "confused")
        self.look_at(self.screen)
        self.wait(3)

        baby_morty = BabyPiCreature()
        baby_morty.match_style(morty)
        baby_morty.to_corner(DL)

        self.play(
            FadeOutAndShift(bubble),
            FadeOutAndShift(bubble.content),
            LaggedStartMap(
                FadeOutAndShift, self.students,
                lambda m: (m, 3 * DOWN),
            ),
            ReplacementTransform(
                morty, baby_morty,
                path_arc=30 * DEGREES,
                run_time=2,
            )
        )
        self.pi_creatures = VGroup(baby_morty)
        bubble = ThoughtBubble(height=6, width=7)
        bubble.set_fill(DARK_GREY, 0.5)
        bubble.pin_to(baby_morty)

        egg = Circle(radius=0.4)
        egg.stretch(0.75, 1)
        egg.move_to(RIGHT)
        egg.apply_function(
            lambda p: np.array([
                p[0], p[0] * p[1], p[2]
            ])
        )
        egg.flip()
        egg.set_width(3)
        egg.set_stroke(RED, 5)
        egg.move_to(bubble.get_bubble_center())

        self.play(baby_morty.change, "confused", 2 * DOWN)
        self.wait(2)
        self.play(
            baby_morty.change, "thinking",
            LaggedStartMap(DrawBorderThenFill, bubble)
        )
        self.play(ShowCreation(egg))
        self.wait(3)

        bubble_group = VGroup(bubble, egg)
        self.play(
            ApplyMethod(
                bubble_group.shift, FRAME_WIDTH * LEFT,
                rate_func=running_start,
            ),
            baby_morty.change, "awe"
        )
        self.play(Blink(baby_morty))
        self.wait()


class TriangleOfEquivalences(Scene):
    def construct(self):
        title = Title("How do you prove this\\textinterrobang.")
        self.add(title)
        rects = VGroup(*[ScreenRectangle() for x in range(3)])
        rects.set_height(2)
        rects[:2].arrange(RIGHT, buff=2)
        rects[2].next_to(rects[:2], DOWN, buff=1.5)
        rects.next_to(title, DOWN)

        arrows = VGroup(*[
            TexMobject("\\Leftrightarrow")
            for x in range(3)
        ])
        arrows.scale(2)
        arrows[0].move_to(rects[:2])
        arrows[1].rotate(60 * DEGREES)
        arrows[1].move_to(rects[1:])
        arrows[2].rotate(-60 * DEGREES)
        arrows[2].move_to(rects[::2])
        arrows[1:].shift(0.5 * DOWN)

        self.play(LaggedStartMap(
            DrawBorderThenFill, arrows,
            lag_ratio=0.7,
            run_time=3,
        ))
        self.wait()
        self.play(FadeOutAndShift(arrows[1:]))
        self.wait()


class SliceCone(ExternallyAnimatedScene):
    pass


class TiltPlane(ExternallyAnimatedScene):
    pass


class IntroduceConeEllipseFocalSum(ExternallyAnimatedScene):
    pass


class ShowMeasurementBook(TeacherStudentsScene):
    CONFIG = {"camera_config": {"background_opacity": 1}}

    def construct(self):
        measurement = ImageMobject("MeasurementCover")
        measurement.set_height(3.5)
        measurement.move_to(self.hold_up_spot, DOWN)

        words = TextMobject("Highly recommended")
        arrow = Vector(RIGHT, color=WHITE)
        arrow.next_to(measurement, LEFT)
        words.next_to(arrow, LEFT)

        self.play(
            self.teacher.change, "raise_right_hand",
            FadeInFromDown(measurement)
        )
        self.change_all_student_modes("hooray")
        self.wait()
        self.play(
            GrowArrow(arrow),
            FadeInFrom(words, RIGHT),
            self.get_student_changes(
                "thinking", "happy", "pondering",
                look_at_arg=arrow
            )
        )
        self.wait(3)


class IntroduceSpheres(ExternallyAnimatedScene):
    pass


class TangencyAnimation(Scene):
    def construct(self):
        rings = VGroup(*[
            Circle(color=YELLOW, stroke_width=3, radius=0.5)
            for x in range(5)
        ])
        for ring in rings:
            ring.save_state()
            ring.scale(0)
            ring.saved_state.set_stroke(width=0)

        self.play(LaggedStartMap(
            Restore, rings,
            run_time=2,
            lag_ratio=0.7
        ))


class TwoSpheresRotating(ExternallyAnimatedScene):
    pass


class TiltSlopeWithOnlySpheres(ExternallyAnimatedScene):
    pass


class TiltSlopeWithOnlySpheresSideView(ExternallyAnimatedScene):
    pass


class AskAboutWhyYouWouldAddSpheres(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature
        randy.flip()
        randy.set_height(2)
        randy.set_color(BLUE_C)
        randy.to_edge(RIGHT)
        randy.shift(2 * UP)
        randy.look(UP)

        graph_spot = VectorizedPoint()

        why = TextMobject("...why?")
        why.next_to(randy, UP)

        bubble = ThoughtBubble(height=2, width=2)
        bubble.pin_to(randy)

        self.play(FadeInFromDown(randy))
        self.play(
            Animation(graph_spot),
            randy.change, "maybe",
            Write(why),
        )
        self.wait(3)
        self.play(randy.change, "pondering")
        self.play(
            why.to_corner, DR,
            why.set_fill, LIGHT_GREY, 0.5,
        )
        self.wait()
        self.play(
            ShowCreation(bubble),
            randy.change, "thinking"
        )
        self.wait()
        self.look_at(graph_spot)
        self.wait(2)


class ShowTangencyPoints(ExternallyAnimatedScene):
    pass


class ShowFocalLinesAsTangent(ExternallyAnimatedScene):
    pass


class UseDefiningFeatures(Scene):
    def construct(self):
        title = TextMobject("Problem-solving tip:")
        title.scale(1.5)
        title.to_edge(UP)
        tip = TextMobject(
            """
            - Make sure you're using all the \\\\
            \\phantom{-} defining features of the objects \\\\
            \\phantom{-} involved.
            """,
            alignment=""
        )
        tip.next_to(title, DOWN, MED_LARGE_BUFF)
        tip.shift(MED_SMALL_BUFF * RIGHT)
        tip.set_color(YELLOW)

        self.add(title)
        self.play(Write(tip, run_time=4))
        self.wait()


class RemindAboutTangencyToCone(ExternallyAnimatedScene):
    pass


class ShowCircleToCircleLine(ExternallyAnimatedScene):
    pass


class ShowSegmentSplit(Scene):
    CONFIG = {
        "include_image": True,
    }

    def construct(self):
        if self.include_image:
            image = ImageMobject("ShowCircleToCircleLine")
            image.set_height(FRAME_HEIGHT)
            self.add(image)

        brace1 = Brace(Line(ORIGIN, 1.05 * UP), LEFT)
        brace2 = Brace(Line(1.7 * DOWN, ORIGIN), LEFT)
        braces = VGroup(brace1, brace2)
        braces.rotate(-14 * DEGREES)
        braces.move_to(0.85 * UP + 1.7 * LEFT)

        words = VGroup(
            TextMobject("Top segment"),
            TextMobject("Bottom segment")
        )
        for word, brace in zip(words, braces):
            word.next_to(
                brace.get_center(), LEFT,
                buff=0.35
            )
        words[0].set_color(PINK)
        words[1].set_color(GOLD)

        for mob in it.chain(braces, words):
            mob.add_to_back(mob.copy().set_stroke(BLACK, 5))

        for brace in braces:
            brace.save_state()
            brace.set_stroke(width=0)
            brace.scale(0)

        self.play(
            LaggedStartMap(
                Restore, braces,
                lag_ratio=0.7
            ),
        )
        for word in words:
            self.play(Write(word, run_time=1))
        self.wait()


class ShowSegmentSplitWithoutImage(ShowSegmentSplit):
    CONFIG = {
        "include_image": False,
    }


class ShowCircleToCircleLineAtMultiplePoints(ExternallyAnimatedScene):
    pass


class ConjectureLineEquivalence(ExternallyAnimatedScene):
    pass


class WriteConjecture(Scene):
    CONFIG = {
        "image_name": "ConjectureLineEquivalenceBigSphere",
        "q_coords": 1.28 * UP + 0.15 * LEFT,
        "circle_point_coords": 0.84 * RIGHT + 0.05 * DOWN,
        "tangent_point_coords": 0.85 * UP + 1.75 * LEFT,
        "plane_line_color": GOLD,
        "text_scale_factor": 0.75,
        "shift_plane_word_down": False,
        "include_image": False,
    }

    def construct(self):
        if self.include_image:
            image = ImageMobject(self.image_name)
            image.set_height(FRAME_HEIGHT)
            self.add(image)

        title = TextMobject("Conjecture:")
        title.to_corner(UR)

        cone_line = Line(self.q_coords, self.circle_point_coords)
        plane_line = Line(self.q_coords, self.tangent_point_coords)
        plane_line.set_color(self.plane_line_color)
        lines = VGroup(cone_line, plane_line)

        cone_line_words = TextMobject("Cone line")
        plane_line_words = TextMobject("Plane line")
        plane_line_words.set_color(self.plane_line_color)
        words = VGroup(cone_line_words, plane_line_words)

        for word in words:
            word.add_to_back(word.copy().set_stroke(BLACK, 5))
            word.in_equation = word.copy()

        equation = VGroup(
            TexMobject("||"),
            words[0].in_equation,
            TexMobject("||"),
            TexMobject("="),
            TexMobject("||"),
            words[1].in_equation,
            TexMobject("||"),
        )
        equation.arrange(RIGHT, buff=SMALL_BUFF)
        equation.scale(0.75)
        equation.next_to(title, DOWN, MED_LARGE_BUFF)
        equation.shift_onto_screen()
        title.next_to(equation, UP)

        for word, line in zip(words, lines):
            word.scale(self.text_scale_factor)
            word.next_to(ORIGIN, UP, SMALL_BUFF)
            if self.shift_plane_word_down and (word is plane_line_words):
                word.next_to(ORIGIN, DOWN, SMALL_BUFF)
            angle = line.get_angle()
            if abs(angle) > 90 * DEGREES:
                angle += PI
            word.rotate(angle, about_point=ORIGIN)
            word.shift(line.get_center())

        self.play(LaggedStartMap(
            FadeInFromDown,
            VGroup(title, equation),
            lag_ratio=0.7
        ))
        self.wait()
        for word, line in zip(words, lines):
            self.play(ShowCreation(line))
            self.play(WiggleOutThenIn(line))
            self.play(ReplacementTransform(
                word.in_equation.copy(), word
            ))
            self.wait()


class WriteConjectureV2(WriteConjecture):
    CONFIG = {
        "image_name": "ConjectureLineEquivalenceSmallSphere",
        "q_coords": 2.2 * LEFT + 1.3 * UP,
        "circle_point_coords": 1.4 * LEFT + 2.25 * UP,
        "tangent_point_coords": 0.95 * LEFT + 1.51 * UP,
        "plane_line_color": PINK,
        "text_scale_factor": 0.5,
        "shift_plane_word_down": True,
        "include_image": False,
    }


class ShowQ(Scene):
    def construct(self):
        mob = TexMobject("Q")
        mob.scale(2)
        mob.add_to_back(mob.copy().set_stroke(BLACK, 5))
        self.play(FadeInFromDown(mob))
        self.wait()


class ShowBigSphereTangentLines(ExternallyAnimatedScene):
    pass


class LinesTangentToSphere(ExternallyAnimatedScene):
    pass


class QuickGeometryProof(Scene):
    def construct(self):
        radius = 2
        circle = Circle(color=BLUE, radius=radius)
        circle.shift(0.5 * DOWN)
        angle = 60 * DEGREES
        O = circle.get_center()
        p1 = circle.point_from_proportion(angle / TAU)
        p2 = circle.point_from_proportion(1 - angle / TAU)
        Q = O + (radius / np.cos(angle)) * RIGHT

        O_p1 = Line(O, p1)
        O_p2 = Line(O, p2)
        p1_Q = Line(p1, Q, color=MAROON_B)
        p2_Q = Line(p2, Q, color=MAROON_B)
        O_Q = DashedLine(O, Q)

        elbow = VGroup(Line(RIGHT, UR), Line(UR, UP))
        elbow.set_stroke(WHITE, 1)
        elbow.scale(0.2, about_point=ORIGIN)

        ticks = VGroup(Line(DOWN, UP), Line(DOWN, UP))
        ticks.scale(0.1)
        ticks.arrange(RIGHT, buff=SMALL_BUFF)

        equation = TexMobject(
            "\\Delta OP_1Q \\cong \\Delta OP_2Q",
            tex_to_color_map={
                "O": BLUE,
                "P_1": MAROON_B,
                "P_2": MAROON_B,
                "Q": YELLOW,
            }
        )
        equation.to_edge(UP)
        self.add(*equation)

        self.add(circle)
        self.add(
            TexMobject("O").next_to(O, LEFT),
            TexMobject("P_1").next_to(p1, UP).set_color(MAROON_B),
            TexMobject("P_2").next_to(p2, DOWN).set_color(MAROON_B),
            TexMobject("Q").next_to(Q, RIGHT).set_color(YELLOW),
        )
        self.add(O_p1, O_p2, p1_Q, p2_Q, O_Q)
        self.add(
            Dot(O, color=BLUE),
            Dot(p1, color=MAROON_B),
            Dot(p2, color=MAROON_B),
            Dot(Q, color=YELLOW)
        )
        self.add(
            elbow.copy().rotate(angle + PI, about_point=ORIGIN).shift(p1),
            elbow.copy().rotate(-angle + PI / 2, about_point=ORIGIN).shift(p2),
        )
        self.add(
            ticks.copy().rotate(angle).move_to(O_p1),
            ticks.copy().rotate(-angle).move_to(O_p2),
        )

        everything = VGroup(*self.mobjects)

        self.play(LaggedStartMap(
            GrowFromCenter, everything,
            lag_ratio=0.25,
            run_time=4
        ))


class ShowFocalSumEqualsCircleDistance(ExternallyAnimatedScene):
    pass


class FinalMovingEllipsePoint(ExternallyAnimatedScene):
    pass


class TiltPlaneWithSpheres(ExternallyAnimatedScene):
    pass


class NameDandelin(Scene):
    CONFIG = {"camera_config": {"background_opacity": 1}}

    def construct(self):
        title = TextMobject(
            "Proof by\\\\",
            "Germinal Pierre Dandelin (1822)"
        )
        title.to_edge(UP)

        portrait = ImageMobject("GerminalDandelin")
        portrait.set_height(5)
        portrait.next_to(title, DOWN)

        google_result = ImageMobject("GoogleDandelin")
        google_result.set_height(4)
        google_result.center()
        google_result.to_corner(DR)

        cmon_google = TextMobject("C'mon Google...")
        cmon_google.set_color(RED)
        cmon_google.next_to(google_result, RIGHT)
        cmon_google.next_to(google_result, UP, aligned_edge=RIGHT)

        dandelion = ImageMobject("DandelionSphere", height=1.5)
        dandelion.to_edge(LEFT, buff=LARGE_BUFF)
        dandelion.shift(UP)
        big_dandelion = dandelion.copy().scale(2)
        big_dandelion.next_to(dandelion, DOWN, buff=0)
        dandelions = Group(dandelion, big_dandelion)

        self.add(title[0])
        self.play(FadeInFromDown(portrait))
        self.play(Write(title[1]))
        self.wait()
        self.play(FadeInFrom(google_result, LEFT))
        self.play(Write(cmon_google, run_time=1))
        self.wait()

        self.play(LaggedStartMap(
            FadeInFromDown, dandelions,
            lag_ratio=0.7,
            run_time=1
        ))
        self.wait()


class DandelinSpheresInCylinder(ExternallyAnimatedScene):
    pass


class ProjectCircleOntoTiltedPlane(ExternallyAnimatedScene):
    pass


class CylinderDandelinSpheresChangingSlope(ExternallyAnimatedScene):
    pass


class DetailsLeftAsHomework(PiCreatureScene):
    CONFIG = {
        "default_pi_creature_kwargs": {
            "color": GREY_BROWN,
            "flip_at_start": False,
        },
        "default_pi_creature_start_corner": DL,
    }

    def construct(self):
        # morty = self.pi_creature
        self.pi_creature_says(
            "Details left \\\\ as homework",
            target_mode="hooray"
        )
        self.wait(3)


class AskWhyYouWouldChooseThisProof(PiCreatureScene):
    def construct(self):
        randy, other = self.pi_creatures
        screen = ScreenRectangle(height=4).to_edge(UP)

        for pi, vect, word in (randy, UP, "You"), (other, LEFT, "Non-math \\\\ enthusiast"):
            arrow = Vector(-vect, color=WHITE)
            arrow.next_to(pi, vect)
            label = TextMobject(word)
            label.next_to(arrow, vect)
            pi.arrow = arrow
            pi.label = label

        for pi, mode in (randy, "hooray"), (other, "tired"):
            self.play(
                GrowArrow(pi.arrow),
                FadeInFrom(pi.label, RIGHT),
                pi.change, mode,
            )
        self.play(
            randy.change, "raise_right_hand", screen,
            other.look_at, screen,
        )
        self.wait()
        self.play(other.change, "thinking", screen)
        self.wait(5)

    def create_pi_creatures(self):
        randy = Randolph(color=BLUE_C)
        other = PiCreature(color=RED_D)
        other.flip()
        group = VGroup(randy, other)
        group.arrange(RIGHT, buff=5)
        group.to_edge(DOWN)
        return group


class CreativeConstruction(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature
        self.remove(randy)

        dandelin = ImageMobject("GerminalDandelin")
        dandelin.set_height(4)
        dandelin.move_to(FRAME_WIDTH * RIGHT / 4)

        lightbulb = Lightbulb()
        lightbulb.next_to(dandelin, UP)

        kant = ImageMobject("Kant")
        kant.set_height(3)
        bubble = ThoughtBubble(height=3, width=4)
        bubble.pin_to(kant)
        kant_words = TextMobject(
            "How is synthetic a priori\\\\" +
            "reasoning possible?"
        )
        kant_words.scale(0.75)
        bubble.position_mobject_inside(kant_words)
        kant_group = VGroup(bubble, kant_words, kant)
        kant_group.to_corner(UR)

        self.add(dandelin)
        self.add(lightbulb)
        self.play(
            Write(lightbulb, run_time=1),
            self.get_light_shine(lightbulb)
        )
        self.wait()
        self.play(
            lightbulb.next_to, randy, RIGHT,
            {"buff": LARGE_BUFF, "aligned_edge": UP},
            randy.change, "pondering",
            VFadeIn(randy),
            FadeOutAndShift(dandelin, DOWN),
        )

        self.play(
            self.get_light_shine(lightbulb),
            Blink(randy),
        )
        self.wait()
        self.play(
            FadeInFromDown(kant),
            Write(bubble),
            Write(kant_words),
        )

        lightbulb.generate_target()
        q_marks = VGroup()
        for submob in lightbulb.target.family_members_with_points():
            if True or get_norm(submob.get_center() - lightbulb.get_center()) > 0.25:
                q_mark = TexMobject("?")
                q_mark.set_height(0.25)
                q_mark.move_to(submob)
                Transform(submob, q_mark).update(1)
                q_marks.add(submob)
        q_marks.space_out_submobjects(2)

        self.wait()
        self.play(randy.change, 'confused', lightbulb)
        self.play(MoveToTarget(
            lightbulb,
            run_time=3,
            rate_func=there_and_back,
            lag_ratio=0.5
        ))
        self.play(Blink(randy))
        self.wait()

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

    def get_light_shine(self, lightbulb, max_radius=15.0, delta_r=0.025):
        rings = self.get_rings(
            lightbulb.get_center(),
            max_radius=15.0,
            delta_r=0.025,
        )
        return LaggedStartMap(
            FadeIn, rings,
            rate_func=there_and_back,
            run_time=2,
            lag_ratio=0.5
        )


class LockhartQuote(Scene):
    CONFIG = {
        "camera_config": {"background_opacity": 1}
    }

    def construct(self):
        mb_string = "Madame\\,\\,Bovary"
        ml_string = "Mona\\,\\,Lisa."
        strings = (mb_string, ml_string)
        quote_text = """
            \\large
            How do people come up with such ingenious arguments?
            It's the same way people come up with %s or %s
            I have no idea how it happens.  I only know that
            when it happens to me, I feel very fortunate.
        """ % strings
        quote_parts = [s for s in quote_text.split(" ") if s]
        quote = TextMobject(
            *quote_parts,
            tex_to_color_map={
                mb_string: BLUE,
                ml_string: YELLOW,
            },
            alignment=""
        )
        quote.set_width(FRAME_WIDTH - 2)
        quote.to_edge(UP)

        measurement = ImageMobject("MeasurementCover")
        madame_bovary = ImageMobject("MadameBovary")
        mona_lisa = ImageMobject("MonaLisa")
        pictures = Group(measurement, madame_bovary, mona_lisa)
        for picture in pictures:
            picture.set_height(4)
        pictures.arrange(RIGHT, buff=LARGE_BUFF)
        pictures.to_edge(DOWN)

        measurement.save_state()
        measurement.set_width(FRAME_WIDTH)
        measurement.center()
        measurement.fade(1)
        self.play(Restore(measurement))
        self.wait()
        for word in quote:
            anims = [ShowWord(word)]
            for text, picture in zip(strings, pictures[1:]):
                if word is quote.get_part_by_tex(text):
                    anims.append(FadeInFromDown(
                        picture, run_time=1
                    ))
            self.play(*anims)
            self.wait(0.005 * len(word)**1.5)
        self.wait(2)
        self.play(
            LaggedStartMap(
                FadeOutAndShiftDown, quote,
                lag_ratio=0.2,
                run_time=5,
            ),
            LaggedStartMap(
                FadeOutAndShiftDown, pictures,
                run_time=3,
            ),
        )


class ImmersedInGeometryProblems(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature
        randy.center().to_edge(DOWN)

        for vect in compass_directions(start_vect=UL):
            self.play(randy.change, "pondering", 4 * vect)
            self.wait(2)


class ShowApollonianCircles(Scene):
    def construct(self):
        radii = [1.0, 2.0, 3.0]
        curvatures = [1.0 / r for r in radii]
        k4 = sum(curvatures) - 2 * np.sqrt(
            sum([
                k1 * k2
                for k1, k2 in it.combinations(curvatures, 2)
            ])
        )
        radii.append(1.0 / k4)
        centers = [
            ORIGIN, 3 * RIGHT, 4 * UP,
            4 * UP + 3 * RIGHT,
        ]
        circles = VGroup(*[
            Circle(radius=r).shift(c)
            for r, c in zip(radii, centers)
        ])

        circles.set_height(FRAME_HEIGHT - 3)
        circles.center().to_edge(DOWN)
        # circles.set_fill(opacity=1)
        circles.submobjects.reverse()
        circles.set_stroke(width=5)
        circles.set_color_by_gradient(BLUE, YELLOW)

        equation = TexMobject("""
            \\left(
            {1 \\over r_1} + {1 \\over r_2} +
            {1 \\over r_3} + {1 \\over r_4}
            \\right)^2 = 
            2\\left(
            {1 \\over r_1^2} + {1 \\over r_2^2} +
            {1 \\over r_3^2} + {1 \\over r_4^2}
            \\right)
        """)
        # equation.scale(1.5)
        equation.next_to(circles, UP)

        self.add(equation)
        self.play(LaggedStartMap(
            DrawBorderThenFill, circles
        ))
        self.wait()


class EllipseLengthsLinedUp(EccentricityInThumbtackCase):
    def construct(self):
        ellipse = self.get_ellipse(eccentricity=0.6)
        ellipse.scale(2)
        foci = self.get_foci(ellipse)

        point = VectorizedPoint()
        point_movement = cycle_animation(
            MoveAlongPath(
                point, ellipse,
                run_time=5,
                rate_func=linear,
            )
        )

        arrow = Vector(RIGHT, color=WHITE)
        arrow.to_edge(LEFT)
        q_mark = TexMobject("?")
        q_mark.next_to(arrow, UP)

        lines = VGroup(*[Line(UP, DOWN) for x in range(2)])
        lines.set_color_by_gradient(PINK, GOLD)
        lines.set_stroke(width=5)

        h_line = Line(LEFT, RIGHT, color=WHITE)
        h_line.set_width(0.25)

        def update_lines(lines):
            for line, focus in zip(lines, foci):
                d = get_norm(point.get_center() - focus)
                line.put_start_and_end_on(
                    ORIGIN, d * UP
                )
            lines.arrange(DOWN, buff=0)
            lines.next_to(arrow, RIGHT)
            h_line.move_to(lines[0].get_bottom())
        lines_animation = Mobject.add_updater(
            lines, update_lines
        )

        self.add(point_movement)
        self.add(arrow)
        self.add(q_mark)
        self.add(h_line)
        self.add(lines_animation)

        self.wait(20)


class ReactionToGlimpseOfGenius(TeacherStudentsScene, CreativeConstruction):
    def construct(self):
        morty = self.teacher

        lightbulb = Lightbulb()
        lightbulb.set_stroke(width=4)
        lightbulb.scale(1.5)
        lightbulb.move_to(self.hold_up_spot, DOWN)

        rings = self.get_rings(
            lightbulb.get_center(),
            max_radius=15,
            delta_r=0.1,
        )

        arrow = Vector(RIGHT, color=WHITE)
        arrow.next_to(lightbulb, LEFT)

        clock = Clock()
        clock.next_to(arrow, LEFT)

        pi_lights = VGroup()
        for pi in self.students:
            light = Lightbulb()
            light.scale(0.75)
            light.next_to(pi, UP)
            pi.light = light
            pi_lights.add(light)

        q_marks = VGroup()
        for submob in lightbulb:
            q_mark = TexMobject("?")
            q_mark.move_to(submob)
            q_marks.add(q_mark)
        q_marks.space_out_submobjects(2)

        self.student_says(
            "I think Lockhart was \\\\"
            "speaking more generally.",
            target_mode="sassy",
            added_anims=[morty.change, "guilty"]
        )
        self.wait(2)
        self.play(
            morty.change, "raise_right_hand",
            FadeInFromDown(lightbulb),
            RemovePiCreatureBubble(self.students[1]),
            self.get_student_changes(*3 * ["confused"]),
            run_time=1
        )
        self.play(Transform(
            lightbulb, q_marks,
            run_time=3,
            rate_func=there_and_back_with_pause,
            lag_ratio=0.5
        ))
        self.play(
            ClockPassesTime(clock, hours_passed=4, run_tim=4),
            VFadeIn(clock),
            GrowArrow(arrow),
            self.get_student_changes(
                *3 * ["pondering"],
                look_at_arg=clock
            )
        )
        self.play(
            ClockPassesTime(clock, run_time=1, hours_passed=1),
            VFadeOut(clock),
            FadeOut(arrow),
            lightbulb.scale, 1.5,
            lightbulb.move_to, 2 * UP,
            self.get_student_changes(
                *3 * ["awe"],
                look_at_arg=2 * UP
            ),
            run_time=1
        )
        self.play(self.get_light_shine(lightbulb))
        self.play(
            ReplacementTransform(
                VGroup(lightbulb),
                pi_lights
            ),
            morty.change, "happy",
            *[
                ApplyMethod(pi.change, mode, pi.get_top())
                for pi, mode in zip(self.students, [
                    "hooray", "tease", "surprised"
                ])
            ]
        )
        self.wait(3)


class DandelinEndScreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "Juan Benet",
            "Matt Russell",
            "Soekul",
            "Keith Smith",
            "Burt Humburg",
            "CrypticSwarm",
            "Brian Tiger Chow",
            "Joseph Kelly",
            "Roy Larson",
            "Andrew Sachs",
            "Devin Scott",
            "Akash Kumar",
            "Arthur Zey",
            "Ali Yahya",
            "Mayank M. Mehrotra",
            "Lukas Biewald",
            "Yana Chernobilsky",
            "Kaustuv DeBiswas",
            "Yu Jun",
            "Dave Nicponski",
            "Damion Kistler",
            "Jordan Scales",
            "Markus Persson",
            "Fela",
            "Fred Ehrsam",
            "Gary Kong",
            "Randy C. Will",
            "Britt Selvitelle",
            "Jonathan Wilson",
            "Ryan Atallah",
            "Joseph John Cox",
            "Luc Ritchie",
            "Valeriy Skobelev",
            "Adrian Robinson",
            "Michael Faust",
            "Solara570",
            "George M. Botros",
            "Peter Ehrnstrom",
            "Kai-Siang Ang",
            "Alexis Olson",
            "Ludwig",
            "Omar Zrien",
            "Sindre Reino Trosterud",
            "Jeff Straathof",
            "Matt Langford",
            "Matt Roveto",
            "Marek Cirkos",
            "Magister Mugit",
            "Stevie Metke",
            "Cooper Jones",
            "James Hughes",
            "John V Wertheim",
            "Chris Giddings",
            "Song Gao",
            "Richard Burgmann",
            "John Griffith",
            "Chris Connett",
            "Steven Tomlinson",
            "Jameel Syed",
            "Bong Choung",
            "Ignacio Freiberg",
            "Zhilong Yang",
            "Giovanni Filippi",
            "Eric Younge",
            "Prasant Jagannath",
            "James H. Park",
            "Norton Wang",
            "Kevin Le",
            "Oliver Steele",
            "Yaw Etse",
            "Dave B",
            "supershabam",
            "Delton Ding",
            "Thomas Tarler",
            "1stViewMaths",
            "Jacob Magnuson",
            "Mark Govea",
            "Clark Gaebel",
            "Mathias Jansson",
            "David Clark",
            "Michael Gardner",
            "Mads Elvheim",
            "Awoo",
            "Dr . David G. Stork",
            "Ted Suzman",
            "Linh Tran",
            "Andrew Busey",
            "John Haley",
            "Ankalagon",
            "Eric Lavault",
            "Boris Veselinovich",
            "Julian Pulgarin",
            "Jeff Linse",
            "Robert Teed",
            "Jason Hise",
            "Bernd Sing",
            "James Thornton",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Jerry Ling",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ],
    }
