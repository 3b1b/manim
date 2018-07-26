from __future__ import absolute_import
from big_ol_pile_of_manim_imports import *


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

        self.play(LaggedStart(
            FadeInAndShiftFromDirection, definitions,
            lambda m: (m, RIGHT)
        ))
        self.wait()


class StretchACircle(Scene):
    def construct(self):
        pass


class SliceCone(ExternallyAnimatedScene):
    pass


class TiltPlane(ExternallyAnimatedScene):
    pass


class IntroduceConeEllipseFocalSum(ExternallyAnimatedScene):
    pass


class IntroduceSpheres(ExternallyAnimatedScene):
    pass


class ShowTangencyPoints(ExternallyAnimatedScene):
    pass


class ShowFocalLinesAsTangent(ExternallyAnimatedScene):
    pass


class RemindAboutTangencyToCone(ExternallyAnimatedScene):
    pass


class ShowCircleToCircleLine(ExternallyAnimatedScene):
    pass


class ShowCircleToCircleLineAtMultiplePoints(ExternallyAnimatedScene):
    pass


class ConjectureLineEquivalence(ExternallyAnimatedScene):
    pass


class LinesTangentToSphere(ExternallyAnimatedScene):
    pass


class ShowBigSphereTangentLines(ExternallyAnimatedScene):
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
