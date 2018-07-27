from __future__ import absolute_import
from big_ol_pile_of_manim_imports import *

from active_projects.lost_lecture import Orbiting


class ThinkingAboutAProof(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature
        randy.scale(0.5, about_edge=DL)
        bubble = ThoughtBubble()
        bubble.pin_to(randy)
        bubble.shift(MED_SMALL_BUFF * RIGHT)
        cloud = bubble[-1]
        cloud.rotate(90 * DEGREES)
        cloud.scale_to_fit_height(FRAME_HEIGHT - 0.5)
        cloud.stretch(2.8, 0)
        cloud.next_to(bubble[0], RIGHT)
        cloud.to_edge(UP, buff=0.25)

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
            FadeInAndShiftFromDirection(you, LEFT),
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
            for tex in "1", "2", "3", "\\cdots", "n",
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

        self.play(LaggedStart(FadeInFromDown, equation[:-1]))
        self.wait()
        self.play(
            LaggedStart(
                MoveToTarget, numbers,
                path_arc=-90 * DEGREES,
                lag_ratio=1,
                run_time=1
            )
        )
        self.play(LaggedStart(Restore, rows))
        self.wait()
        self.play(
            ReplacementTransform(
                rows.copy().set_fill(opacity=0), flipped_rows,
                path_arc=PI,
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
            row.arrange_submobjects(RIGHT, buff=0)
            rows.add(row)
        rows.arrange_submobjects(DOWN, buff=0, aligned_edge=LEFT)
        rows.scale_to_fit_height(5)
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


class HoldUpRedditQuestion(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("From reddit")
        title.to_edge(UP)
        self.add(title)

        alt_title = TextMobject("One of my all-time favorite proofs")
        alt_title.to_edge(UP)

        self.play(
            self.teacher.change, "raise_right_hand", self.screen,
            self.get_student_changes(
                "pondering", "confused", "maybe",
                look_at_arg=title
            )
        )
        self.look_at(title)
        self.wait(5)
        self.play(
            FadeOutAndShift(title, UP),
            FadeInFromDown(alt_title),
            self.teacher.change, "hooray",
            self.get_student_changes(*3 * ["happy"])
        )
        self.look_at(alt_title)
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
        definitions.arrange_submobjects(
            DOWN, buff=LARGE_BUFF,
            aligned_edge=LEFT
        )
        definitions.next_to(title, DOWN, LARGE_BUFF)
        definitions.to_edge(LEFT)

        for definition in definitions:
            definition.saved_state = definition.copy()
            definition.saved_state.set_fill(LIGHT_GREY, 0.5)

        self.play(LaggedStart(
            FadeInAndShiftFromDirection, definitions,
            lambda m: (m, RIGHT)
        ))
        self.wait()
        for definition in definitions:
            others = filter(lambda d: d is not definition, definitions)
            self.play(
                definition.set_fill, WHITE, 1,
                definition.scale, 1.2, {"about_edge": LEFT},
                *map(Restore, others)
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
            LaggedStart(
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
            FadeInAndShiftFromDirection(start_point, UP),
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
        eccentricity_labels = VGroup(*map(
            DecimalNumber, eccentricities
        ))
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
            LaggedStart(GrowArrow, arrows),
            LaggedStart(Restore, eccentricity_labels)
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
            LaggedStart(FadeOutAndShiftDown, group),
            circle.scale_to_fit_height, 5,
            circle.center,
        )

    def get_ellipse(self, eccentricity, width=2):
        result = Circle(color=WHITE)
        result.scale_to_fit_width(width)
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
        result.arrange_submobjects(RIGHT, buff=buff)
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
        earth_orbit.scale_to_fit_height(6)
        comet_orbit.scale_to_fit_width(
            0.7 * FRAME_WIDTH,
            about_point=ORIGIN,
        )

        sun = ImageMobject("Sun")
        earth = ImageMobject("Earth")
        comet = ImageMobject("Comet")
        sun.scale_to_fit_height(1)
        earth.scale_to_fit_height(0.5)
        comet.scale_to_fit_height(0.1)

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
        full_label.arrange_submobjects(RIGHT, SMALL_BUFF)
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
            earth_parts.scale_to_fit_height,
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
        focus_distance_update = ContinualUpdateFromFunc(
            focus_distance,
            lambda m: m.scale_to_fit_width(
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
        numerator_update = ContinualUpdateFromFunc(
            numerator,
            lambda m: m.scale_to_fit_width(focus_distance.get_width()).next_to(
                fraction[1], UP, MED_SMALL_BUFF
            )
        )

        fraction_arrow = Arrow(
            eccentricity_label.get_right(),
            fraction.get_top() + MED_SMALL_BUFF * UP,
            path_arc=-60 * DEGREES,
            use_rectangular_stem=False,
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

        return ContinualUpdateFromFunc(thumbtacks, update_thumbtacks)

    def get_ellipse_point_update(self, ellipse):
        dot = Dot(color=RED)
        return CycleAnimation(MoveAlongPath(
            dot, ellipse,
            run_time=5,
            rate_func=None
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

        return ContinualUpdateFromFunc(lines, update_lines)

    def get_focus_to_focus_line_update(self, ellipse):
        return ContinualUpdateFromFunc(
            Line(LEFT, RIGHT, color=WHITE),
            lambda m: m.put_start_and_end_on(*self.get_foci(ellipse))
        )

    def get_focus_line_to_focus_line_brace_update(self, line):
        brace = Brace(Line(LEFT, RIGHT))
        brace.add_to_back(brace.copy().set_stroke(BLACK, 5))
        return ContinualUpdateFromFunc(
            brace,
            lambda b: b.match_width(line, stretch=True).next_to(
                line, DOWN, buff=SMALL_BUFF
            )
        )

    def get_eccentricity_label(self):
        words = TextMobject("Eccentricity = ")
        decimal = DecimalNumber(0, num_decimal_places=2)
        group = VGroup(words, decimal)
        group.arrange_submobjects(RIGHT)
        group.to_edge(UP)
        return group

    def get_eccentricity_value_update(self, eccentricity_label, ellipse):
        decimal = eccentricity_label[1]
        return ContinualChangingDecimal(
            decimal,
            lambda a: self.get_eccentricity(ellipse)
        )

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
        result.scale_to_fit_height(0.5)
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
            LaggedStart(
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
        egg.scale_to_fit_width(3)
        egg.set_stroke(RED, 5)
        egg.move_to(bubble.get_bubble_center())

        self.play(baby_morty.change, "confused", 2 * DOWN)
        self.wait(2)
        self.play(
            baby_morty.change, "thinking",
            LaggedStart(DrawBorderThenFill, bubble)
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
        rects.scale_to_fit_height(2)
        rects[:2].arrange_submobjects(RIGHT, buff=2)
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

        self.play(LaggedStart(
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
        measurement.scale_to_fit_height(3.5)
        measurement.move_to(self.hold_up_spot, DOWN)

        words = TextMobject("Highly recommended")
        arrow = Vector(RIGHT, buff=WHITE)
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
            FadeInAndShiftFromDirection(words, RIGHT),
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

        self.play(LaggedStart(
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
        randy.scale_to_fit_height(2)
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
        self.play(Write(tip, lag_factor=5, run_time=4))
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
            image.scale_to_fit_height(FRAME_HEIGHT)
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
            LaggedStart(
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
            image.scale_to_fit_height(FRAME_HEIGHT)
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
        equation.arrange_submobjects(RIGHT, buff=SMALL_BUFF)
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

        self.play(LaggedStart(
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


class ShowFocalSumEqualsCircleDistance(ExternallyAnimatedScene):
    pass


class FinalMovingEllipsePoint(ExternallyAnimatedScene):
    pass


class TiltPlaneWithSpheres(ExternallyAnimatedScene):
    pass


class DandelinSpheresInCylinder(ExternallyAnimatedScene):
    pass


class CylinderDandelinSpheresChangingSlope(ExternallyAnimatedScene):
    pass
