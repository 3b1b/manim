from big_ol_pile_of_manim_imports import *
from old_projects.lost_lecture import GeometryProofLand
from old_projects.quaternions import SpecialThreeDScene


class TopologyWordBreak(Scene):
    def construct(self):
        word = TextMobject("Topology")
        word.scale(2)
        colors = [BLUE, YELLOW, RED]
        classes = VGroup(*[VGroup() for x in range(3)])
        for letter in word:
            genus = len(letter.submobjects)
            letter.target_color = colors[genus]
            letter.generate_target()
            letter.target.set_color(colors[genus])
            classes[genus].add(letter.target)
        signs = VGroup()
        for group in classes:
            new_group = VGroup()
            for elem in group[:-1]:
                new_group.add(elem)
                sign = TexMobject("\\simeq")
                new_group.add(sign)
                signs.add(sign)
            new_group.add(group[-1])
            group.submobjects = list(new_group.submobjects)
            group.arrange_submobjects(RIGHT)

        word[2].target.shift(0.1 * DOWN)
        word[7].target.shift(0.1 * DOWN)

        classes.arrange_submobjects(DOWN, buff=LARGE_BUFF, aligned_edge=LEFT)
        classes.shift(2 * RIGHT)

        genus_labels = VGroup(*[
            TextMobject("Genus %d:" % d).scale(1.5).next_to(
                classes[d], LEFT, MED_LARGE_BUFF
            )
            for d in range(3)
        ])
        genus_labels.shift(SMALL_BUFF * UP)

        self.play(Write(word))
        self.play(LaggedStart(
            ApplyMethod, word,
            lambda m: (m.set_color, m.target_color),
            run_time=1
        ))
        self.play(
            LaggedStart(MoveToTarget, word),
            LaggedStart(FadeIn, signs),
            LaggedStart(FadeInFromDown, genus_labels),
        )
        self.wait(3)


class TopologyProofLand(GeometryProofLand):
    CONFIG = {
        "text": "Topology proof land"
    }


class GreenLine(Scene):
    def construct(self):
        self.add(Line(LEFT, RIGHT, color=GREEN))


class Thief(Scene):
    def construct(self):
        self.play(Write(TextMobject("Thief")))
        self.wait()


class FunctionGInSymbols(Scene):
    def construct(self):
        p_tex = "\\vec{\\textbf{p}}"
        f_of_p = TexMobject("f", "(", p_tex, ")",)
        f_of_p.shift(2.5 * LEFT + 2.5 * UP)
        f_of_neg_p = TexMobject("f", "(", "-", p_tex, ")")
        g_of_p = TexMobject("g", "(", p_tex, ")")
        g_of_p[0].set_color(YELLOW)
        for mob in f_of_p, f_of_neg_p, g_of_p:
            mob.set_color_by_tex(p_tex, BLUE)
        dec_rhs = DecimalMatrix([[2.71], [8.28]])
        dec_rhs.next_to(f_of_p, RIGHT)
        minus = TexMobject("-")
        equals = TexMobject("=")
        equals.next_to(f_of_p, RIGHT)
        zero_zero = IntegerMatrix([[0], [0]])

        for matrix in dec_rhs, zero_zero:
            matrix.space_out_submobjects(0.8)
            matrix.brackets.scale(0.8)
            matrix.next_to(equals, RIGHT)

        f_of_neg_p.next_to(equals, RIGHT)

        f = f_of_p.get_part_by_tex("f")
        p = f_of_p.get_part_by_tex(p_tex)
        f_brace = Brace(f, UP, buff=SMALL_BUFF)
        f_brace.add(f_brace.get_text("Continuous function"))
        p_brace = Brace(p, DOWN, buff=SMALL_BUFF)
        p_brace.add(p_brace.get_text("Sphere point").match_color(p))

        f_of_p.save_state()
        f_of_p.space_out_submobjects(2)
        f_of_p.scale(2)
        f_of_p.fade(1)

        self.play(f_of_p.restore)
        self.play(GrowFromCenter(f_brace))
        self.wait()
        self.play(GrowFromCenter(p_brace))
        self.wait()
        self.play(
            FadeInFromDown(equals),
            Write(dec_rhs),
            FadeOut(f_brace),
            FadeOut(p_brace),
        )
        self.wait(2)
        self.play(WiggleOutThenIn(f))
        self.wait()
        self.play(
            FadeOutAndShift(dec_rhs, DOWN),
            FadeInFromDown(f_of_neg_p)
        )
        self.wait()

        # Rearrange
        f_of_neg_p.generate_target()
        f_of_p.generate_target()
        group = VGroup(f_of_p.target, minus, f_of_neg_p.target)
        group.arrange_submobjects(RIGHT, buff=SMALL_BUFF)
        group.next_to(equals, LEFT)

        self.play(
            MoveToTarget(f_of_p, path_arc=PI),
            MoveToTarget(f_of_neg_p, path_arc=-PI),
            FadeInFromLarge(minus),
            FadeInFrom(zero_zero, LEFT)
        )
        self.wait()

        # Define g
        def_eq = TexMobject(":=")
        def_eq.next_to(f_of_p, LEFT)
        g_of_p.next_to(def_eq, LEFT)
        rect = SurroundingRectangle(VGroup(g_of_p, f_of_neg_p))
        rect.set_stroke(width=1)

        self.play(
            FadeInFromLarge(g_of_p),
            FadeInFrom(def_eq, LEFT)
        )
        self.play(ShowCreation(rect))
        self.wait()
        self.play(FadeOut(rect))

        # Show g is odd
        g_of_neg_p = TexMobject("g", "(", "-", p_tex, ")")
        eq2 = TexMobject("=")
        rhs = TexMobject(
            "f", "(", "-", p_tex, ")", "-",
            "f", "(", p_tex, ")", "=",
            "-", "g", "(", p_tex, ")",
        )
        for mob in g_of_neg_p, rhs:
            mob.set_color_by_tex(p_tex, BLUE)
            mob.set_color_by_tex("g", YELLOW)
        g_of_neg_p.next_to(g_of_p, DOWN, aligned_edge=LEFT, buff=LARGE_BUFF)
        eq2.next_to(g_of_neg_p, RIGHT, SMALL_BUFF)
        rhs.next_to(eq2, RIGHT, SMALL_BUFF)
        neg_g_of_p = rhs[-5:]
        neg_g_of_p.save_state()
        neg_g_of_p.next_to(eq2, RIGHT, SMALL_BUFF)

        self.play(
            FadeIn(g_of_neg_p),
            FadeIn(eq2),
            FadeIn(neg_g_of_p),
        )
        self.wait()
        self.play(CircleThenFadeAround(g_of_neg_p[2:4]))
        self.wait()
        self.play(CircleThenFadeAround(neg_g_of_p))
        self.wait()
        self.play(neg_g_of_p.restore)
        rects = VGroup(*map(SurroundingRectangle, [f_of_p, f_of_neg_p]))
        self.play(LaggedStart(
            ShowCreationThenDestruction, rects,
            lag_ratio=0.8
        ))
        self.play(
            TransformFromCopy(f_of_p, rhs[6:10]),
            TransformFromCopy(f_of_neg_p, rhs[:5]),
            FadeIn(rhs[5]),
            FadeIn(rhs[-6]),
        )
        self.wait()


class FunctionGInputSpace(SpecialThreeDScene):
    def setup(self):
        # axes = ThreeDAxes()
        # sphere = Sphere(resolution=(24, 48))
        sphere = self.get_sphere()
        sphere.scale(2)

        sphere.set_fill(BLUE_E, opacity=0.5)

        self.set_camera_orientation(
            phi=70 * DEGREES,
            theta=-120 * DEGREES,
        )
        self.begin_ambient_camera_rotation(rate=0.02)
        # self.add(axes)
        self.add(sphere)

        self.sphere = sphere

    def construct(self):
        self.show_input_dot()
        self.show_antipodal_point()
        self.show_equator()
        self.deform_towards_north_pole()

    def show_input_dot(self):
        self.play(Write(sphere))

    def show_antipodal_point(self):
        pass

    def show_equator(self):
        pass

    def deform_towards_north_pole(self):
        pass

    #
    def func(self, point):
        pass

    def draw_path(self, path):
        pass
