from big_ol_pile_of_manim_imports import *
from old_projects.lost_lecture import GeometryProofLand
from old_projects.quaternions import SpecialThreeDScene
from old_projects.uncertainty import Flash


class Introduction(TeacherStudentsScene):
    CONFIG = {
        "random_seed": 2,
    }

    def construct(self):
        self.play(
            Animation(VectorizedPoint(self.hold_up_spot)),
            self.teacher.change, "raise_right_hand",
        )
        self.change_student_modes(
            "angry", "sassy", "pleading"
        )
        self.wait()

        movements = []
        for student in self.students:
            student.center_tracker = VectorizedPoint()
            student.center_tracker.move_to(student)
            student.center_tracker.save_state()
            student.add_updater(
                lambda m: m.move_to(m.center_tracker)
            )
            movement = ContinualMovement(
                student.center_tracker,
                direction=DOWN + 3 * LEFT,
                rate=1.5 * random.random()
            )
            movements.append(movement)
        self.add(*movements)
        self.change_student_modes(
            "pondering", "sad", "concerned_musician",
            look_at_arg=10 * LEFT + 2 * DOWN
        )
        self.teacher_says(
            "Wait, wait, wait!",
            target_mode="surprised"
        )
        self.remove(*movements)
        self.play(
            self.get_student_changes(*3 * ["hesitant"]),
            *[
                Restore(student.center_tracker)
                for student in self.students
            ]
        )


class StudentsWatching(TeacherStudentsScene):
    def construct(self):
        self.play(
            self.teacher.change, "raise_right_hand",
            self.get_student_changes(
                *3 * ["thinking"],
                look_at_arg=self.screen
            ),
            VFadeIn(self.pi_creatures, run_time=2)
        )
        self.wait(5)


class UnexpectedConnection(Scene):
    def construct(self):
        primes = TexMobject(
            "2,", "3,", "5,", "7,", "11,", "13,", "17,", "\\dots"
        )
        primes.move_to(2.5 * UP)

        circle = Circle(
            color=YELLOW,
            stroke_width=1,
            radius=1.5,
        )
        circle.shift(1.5 * DOWN)
        center = circle.get_center()
        center_dot = Dot(center)
        radius = Line(center, circle.get_right())
        radius.set_stroke(WHITE, 3)

        arrow = DoubleArrow(primes, circle)
        arrow.tip[1].shift(SMALL_BUFF * UP)
        arrow.save_state()
        arrow.rotate(90 * DEGREES)
        arrow.scale(1.5)
        arrow.fade(1)

        formula = TexMobject(
            "\\frac{\\pi^2}{6} = \\prod_{p \\text{ prime}}"
            "\\frac{1}{1 - p^{-2}}"
        )
        formula.next_to(arrow.get_center(), RIGHT)

        def get_arc():
            angle = radius.get_angle()
            return Arc(
                start_angle=0,
                angle=angle,
                radius=circle.radius,
                stroke_color=YELLOW,
                stroke_width=5
            ).shift(center)

        arc = updating_mobject_from_func(get_arc)

        decimal = DecimalNumber(0)
        decimal.add_updater(
            lambda d: d.move_to(interpolate(
                radius.get_start(),
                radius.get_end(),
                1.5,
            )),
        )
        decimal.add_updater(
            lambda d: d.set_value(radius.get_angle())
        )
        pi = TexMobject("\\pi")
        pi.scale(2)
        pi.next_to(circle, LEFT)

        self.add(circle, radius, center_dot, decimal, arc)
        self.play(
            Rotate(radius, PI - 1e-7, about_point=center),
            LaggedStart(FadeInFromDown, primes),
            run_time=4
        )
        self.remove(decimal)
        self.add(pi)
        self.wait()
        self.play(
            Restore(arrow),
            FadeInFrom(formula, LEFT)
        )
        self.wait()


class MapOfVideo(MovingCameraScene):
    def construct(self):
        images = Group(
            ImageMobject("NecklaceThumbnail"),
            ImageMobject("BorsukUlamThumbnail"),
            ImageMobject("TopologyProofThumbnail"),
            ImageMobject("ContinuousNecklaceThumbnail"),
            ImageMobject("NecklaceSphereAssociationThumbnail")
        )
        for image in images:
            rect = SurroundingRectangle(image, buff=0)
            rect.set_stroke(WHITE, 3)
            image.add(rect)

        image_line = Group(*images[:2], *images[3:])
        image_line.arrange_submobjects(RIGHT, buff=LARGE_BUFF)
        images[2].next_to(image_line, DOWN, buff=1.5)
        images.set_width(FRAME_WIDTH - 1)
        images.to_edge(UP, buff=LARGE_BUFF)

        arrows = VGroup(
            Arrow(images[0], images[1], buff=SMALL_BUFF),
            Arrow(
                images[1].get_corner(DR) + 0.5 * LEFT,
                images[2].get_top() + 0.5 * LEFT,
            ),
            Arrow(
                images[2].get_top() + 0.5 * RIGHT,
                images[3].get_corner(DL) + 0.5 * RIGHT,
            ),
            Arrow(images[3], images[4], buff=SMALL_BUFF),
        )

        self.play(LaggedStart(FadeInFromDown, images, run_time=4))
        self.play(LaggedStart(GrowArrow, arrows))
        self.wait()
        group = Group(images, arrows)
        for image in images:
            group.save_state()
            group.generate_target()
            group.target.shift(-image.get_center())
            group.target.scale(
                FRAME_WIDTH / image.get_width(),
                about_point=ORIGIN,
            )

            self.play(MoveToTarget(group, run_time=3))
            self.wait()
            self.play(Restore(group, run_time=3))

    def get_curved_arrow(self, *points):
        line = VMobject()
        line.set_points(points)
        tip = Arrow(points[-2], points[-1], buff=SMALL_BUFF).tip
        line.pointwise_become_partial(line, 0, 0.9)
        line.add(tip)
        return line


class MathIsDeep(PiCreatureScene):
    def construct(self):
        words = TextMobject(
            "Math", "is", "deep"
        )
        words.scale(2)
        words.to_edge(UP)
        math = words[0].copy()
        math[1].remove(math[1][1])
        math.set_fill(opacity=0)
        math.set_stroke(width=0, background=True)
        numbers = [13, 1, 20, 8]
        num_mobs = VGroup(*[Integer(d) for d in numbers])
        num_mobs.arrange_submobjects(RIGHT, buff=MED_LARGE_BUFF)
        num_mobs.next_to(math, DOWN, buff=1.5)
        num_mobs.set_color(YELLOW)
        top_arrows = VGroup(*[
            Arrow(c.get_bottom(), n.get_top())
            for c, n in zip(math, num_mobs)
        ])
        n_sum = Integer(sum(numbers))
        n_sum.scale(1.5)
        n_sum.next_to(num_mobs, DOWN, buff=1.5)
        low_arrows = VGroup(*[
            Arrow(n.get_bottom(), n_sum.get_top())
            for n in num_mobs
        ])
        VGroup(top_arrows, low_arrows).set_color(WHITE)

        n_sum_border = n_sum.deepcopy()
        n_sum_border.set_fill(opacity=0)
        n_sum_border.set_stroke(YELLOW, width=1)
        n_sum_border.set_stroke(width=0, background=True)

        # pre_num_mobs = num_mobs.copy()
        # for pn, letter in zip(pre_num_mobs, math):
        #     pn.fade(1)
        #     pn.set_color(RED)
        #     pn.move_to(letter)
        # num_mobs[1].add_subpath(num_mobs[1].points)

        self.play(
            LaggedStart(
                FadeInFromLarge, words,
                scale_factor=1.5,
                run_time=0.6,
                lag_ratio=0.6,
            ),
            self.pi_creature.change, "pondering"
        )
        self.play(
            TransformFromCopy(math, num_mobs),
            *map(GrowArrow, top_arrows),
        )
        self.wait()
        self.play(
            TransformFromCopy(num_mobs, VGroup(n_sum)),
            self.pi_creature.change, "thinking",
            *map(GrowArrow, low_arrows),
        )
        self.play(LaggedStart(ShowCreationThenDestruction, n_sum_border))
        self.play(Blink(self.pi_creature))
        self.wait()


class MinimizeSharding(Scene):
    def construct(self):
        piece_groups = VGroup(*[
            VGroup(*[
                self.get_piece()
                for x in range(3)
            ]).arrange_submobjects(RIGHT, buff=SMALL_BUFF)
            for y in range(4)
        ]).arrange_submobjects(RIGHT, buff=SMALL_BUFF)

        self.add(piece_groups)
        self.play(*[
            ApplyMethod(mob.space_out_submobjects, 0.7)
            for mob in piece_groups
        ])
        self.wait()
        group1 = piece_groups[:2]
        group2 = piece_groups[2:]
        self.play(
            group1.arrange_submobjects, DOWN,
            group1.next_to, ORIGIN, LEFT, LARGE_BUFF,
            group2.arrange_submobjects, DOWN,
            group2.next_to, ORIGIN, RIGHT, LARGE_BUFF,
        )
        self.wait()

    def get_piece(self):
        jagged_spots = [
            ORIGIN, 2 * UP + RIGHT, 4 * UP + LEFT, 6 * UP,
        ]
        corners = list(it.chain(
            jagged_spots,
            [6 * UP + 10 * RIGHT],
            [
                p + 10 * RIGHT
                for p in reversed(jagged_spots)
            ],
            [ORIGIN]
        ))
        piece = VMobject().set_points_as_corners(corners)
        piece.set_width(1)
        piece.center()
        piece.set_stroke(WHITE, width=0.5)
        piece.set_fill(BLUE, opacity=1)
        return piece


class Antipodes(Scene):
    def construct(self):
        word = TextMobject("``Antipodes''")
        word.set_width(FRAME_WIDTH - 1)
        word.set_color(MAROON_B)
        self.play(Write(word))
        self.wait()


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
        neg_p_tex = "-\\vec{\\textbf{p}}"

        def color_tex(tex_mob):
            pairs = [
                (p_tex, YELLOW),
                (neg_p_tex, RED),
                ("{g}", GREEN),
            ]
            for tex, color in pairs:
                tex_mob.set_color_by_tex(
                    tex, color, substring=False
                )

        f_of_p = TexMobject("f", "(", p_tex, ")")
        f_of_p.shift(2.5 * LEFT + 2.5 * UP)
        f_of_neg_p = TexMobject("f", "(", neg_p_tex, ")")
        g_of_p = TexMobject("g", "(", p_tex, ")")
        g_of_p[0].set_color(YELLOW)
        for mob in f_of_p, f_of_neg_p, g_of_p:
            color_tex(mob)
        dec_rhs = DecimalMatrix([[-0.9], [0.5]])
        dec_rhs.next_to(f_of_p, RIGHT)
        minus = TexMobject("-")
        equals = TexMobject("=")
        equals.next_to(f_of_p, RIGHT)
        zero_zero = IntegerMatrix([[0], [0]])

        for matrix in dec_rhs, zero_zero:
            matrix.space_out_submobjects(0.8)
            matrix.brackets.scale(0.9)
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
        seeking_text = TexMobject(
            "\\text{Looking for }", p_tex, "\\text{ where}"
        )
        color_tex(seeking_text)
        seeking_text.next_to(zero_zero, DOWN, MED_LARGE_BUFF)
        seeking_text.to_edge(LEFT)
        g_equals_zero = VGroup(
            g_of_p.copy(), equals, zero_zero
        )
        g_equals_zero.generate_target()
        g_equals_zero.target.arrange_submobjects(RIGHT, SMALL_BUFF)
        g_equals_zero.target.next_to(seeking_text, DOWN)

        self.play(
            FadeInFromLarge(g_of_p),
            FadeInFrom(def_eq, LEFT)
        )
        self.play(
            FadeInFromDown(seeking_text),
            MoveToTarget(g_equals_zero)
        )
        self.play(ShowCreation(rect))
        self.wait()
        self.play(FadeOut(rect))

        # Show g is odd
        g_of_neg_p = TexMobject("{g}", "(", neg_p_tex, ")")
        eq2 = TexMobject("=")
        rhs = TexMobject(
            "f", "(", neg_p_tex, ")", "-",
            "f", "(", p_tex, ")", "=",
            "-", "{g}", "(", p_tex, ")",
        )
        for mob in g_of_neg_p, rhs:
            color_tex(mob)
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
            VGroup(seeking_text, g_equals_zero).shift, 1.5 * DOWN
        )
        self.wait()
        self.play(CircleThenFadeAround(g_of_neg_p[2]))
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
            TransformFromCopy(f_of_p, rhs[5:9]),
            TransformFromCopy(f_of_neg_p, rhs[:4]),
            FadeIn(rhs[4]),
            FadeIn(rhs[-6]),
        )
        self.wait()


class FunctionGInputSpace(SpecialThreeDScene):
    def setup(self):
        self.init_tracked_point()

        sphere = self.get_sphere()
        sphere.set_fill(BLUE_E, opacity=0.5)
        self.sphere = sphere

        self.set_camera_orientation(
            phi=70 * DEGREES,
            theta=-120 * DEGREES,
        )
        self.begin_ambient_camera_rotation(rate=0.02)

        self.init_dot()

        self.add(ThreeDAxes())

    def construct(self):
        self.show_input_dot()
        self.show_start_path()
        self.show_antipodal_point()
        self.show_equator()
        self.deform_towards_north_pole()

    def show_input_dot(self):
        sphere = self.sphere
        dot = self.dot
        point_mob = self.tracked_point
        start_point = self.get_start_point()

        arrow = Arrow(
            start_point + (LEFT + OUT + UP), start_point,
            color=BLUE,
            buff=MED_LARGE_BUFF,
        )
        arrow.rotate(90 * DEGREES, axis=arrow.get_vector())
        arrow.add_to_back(arrow.copy().set_stroke(BLACK, 5))

        p_label = self.p_label = TexMobject("\\vec{\\textbf{p}}")
        p_label.set_color(YELLOW)
        p_label.next_to(arrow.get_start(), OUT, buff=0.3)
        p_label.set_shade_in_3d(True)

        self.play(Write(sphere, run_time=3))
        self.add(dot)
        self.add_fixed_orientation_mobjects(p_label)
        self.play(
            point_mob.move_to, start_point,
            GrowArrow(arrow),
            FadeInFrom(p_label, IN)
        )
        self.wait()
        self.play(
            arrow.scale, 0, {"about_point": arrow.get_end()},
            p_label.next_to, dot, OUT + LEFT, SMALL_BUFF
        )
        p_label.add_updater(lambda p: p.next_to(dot, OUT + LEFT, SMALL_BUFF))
        self.wait(4)

    def show_start_path(self):
        path = self.get_start_path()
        self.draw_path(path, uncreate=True)
        self.wait()

    def show_antipodal_point(self):
        path = self.get_antipodal_path()
        end_dot = updating_mobject_from_func(
            lambda: self.get_dot(
                path[-1].point_from_proportion(1)
            ).set_color(RED)
        )

        neg_p = TexMobject("-\\vec{\\textbf{p}}")
        neg_p.add_updater(
            lambda p: p.next_to(end_dot, UP + RIGHT + IN)
        )
        neg_p.set_color(RED)
        neg_p.set_shade_in_3d(True)

        self.move_camera(
            phi=100 * DEGREES,
            theta=30 * DEGREES,
            added_anims=[ShowCreation(path)],
            run_time=4,
        )
        self.wait()
        self.add_fixed_orientation_mobjects(neg_p)
        self.play(
            FadeInFromLarge(end_dot),
            Write(neg_p)
        )
        self.wait(4)
        self.move_camera(
            phi=70 * DEGREES,
            theta=-120 * DEGREES,
            run_time=2
        )
        self.wait(7)
        # Flip
        self.move_camera(
            phi=100 * DEGREES,
            theta=30 * DEGREES,
            run_time=2,
        )
        self.wait(7)
        self.move_camera(
            phi=70 * DEGREES,
            theta=-120 * DEGREES,
            added_anims=[
                FadeOut(end_dot),
                FadeOut(neg_p),
                FadeOut(path),
            ],
            run_time=2,
        )

    def show_equator(self):
        point_mob = self.tracked_point
        equator = self.get_lat_line()

        self.play(point_mob.move_to, equator[0].point_from_proportion(0))
        self.play(ShowCreation(equator, run_time=4))
        for x in range(2):
            self.play(
                Rotate(point_mob, PI, about_point=ORIGIN, axis=OUT),
                run_time=4
            )
            self.wait(3)
        self.play(
            FadeOut(self.dot),
            FadeOut(self.p_label),
        )

        self.equator = equator

    def deform_towards_north_pole(self):
        equator = self.equator

        self.play(UpdateFromAlphaFunc(
            equator,
            lambda m, a: m.become(self.get_lat_line(a * PI / 2)),
            run_time=16
        ))
        self.wait()

    #
    def init_tracked_point(self):
        self.tracked_point = VectorizedPoint([0, 0, 2])
        self.tracked_point.add_updater(
            lambda p: p.move_to(2 * normalize(p.get_center()))
        )
        self.add(self.tracked_point)

    def init_dot(self):
        self.dot = updating_mobject_from_func(
            lambda: self.get_dot(self.tracked_point.get_center())
        )

    def get_start_path(self):
        path = ParametricFunction(
            lambda t: np.array([
                -np.sin(TAU * t + TAU / 4),
                np.cos(2 * TAU * t + TAU / 4),
                0
            ]),
            color=RED
        )
        path.scale(0.5)
        path.shift(0.5 * OUT)
        path.rotate(60 * DEGREES, RIGHT, about_point=ORIGIN)
        path.shift(
            self.get_start_point() - path.point_from_proportion(0)
        )
        path.apply_function(lambda p: 2 * normalize(p))
        return path

    def get_antipodal_path(self):
        start = self.get_start_point()
        path = ParametricFunction(
            lambda t: 2.03 * np.array([
                0,
                np.sin(PI * t),
                np.cos(PI * t),
            ]),
            color=YELLOW
        )
        path.apply_matrix(z_to_vector(start))

        dashed_path = DashedMobject(path)
        dashed_path.set_shade_in_3d(True)

        return dashed_path

    def get_lat_line(self, lat=0):
        equator = ParametricFunction(lambda t: 2.03 * np.array([
            np.cos(lat) * np.sin(TAU * t),
            np.cos(lat) * (-np.cos(TAU * t)),
            np.sin(lat)
        ]))
        equator.rotate(-90 * DEGREES)
        dashed_equator = DashedMobject(
            equator,
            dashes_num=40,
            color=RED,
        )
        dashed_equator.set_shade_in_3d(True)
        return dashed_equator

    def draw_path(self, path,
                  run_time=4,
                  dot_follow=True,
                  uncreate=False,
                  added_anims=None
                  ):
        added_anims = added_anims or []
        point_mob = self.tracked_point
        anims = [ShowCreation(path)]
        if dot_follow:
            anims.append(UpdateFromFunc(
                point_mob,
                lambda p: p.move_to(path.point_from_proportion(1))
            ))
        self.add(path, self.dot)
        self.play(*anims, run_time=run_time)

        if uncreate:
            self.wait()
            self.play(
                Uncreate(path),
                run_time=run_time
            )

    def modify_path(self, path):
        return path

    def get_start_point(self):
        return 2 * normalize([-1, -1, 1])

    def get_dot(self, point):
        dot = Dot(color=WHITE)
        dot.shift(2.05 * OUT)
        dot.apply_matrix(z_to_vector(normalize(point)))
        dot.set_shade_in_3d(True)
        return dot


class FunctionGOutputSpace(FunctionGInputSpace):
    def construct(self):
        self.show_input_dot()
        self.show_start_path()
        self.show_antipodal_point()
        self.show_equator()
        self.deform_towards_north_pole()

    def setup(self):
        axes = self.axes = Axes(
            x_min=-2.5,
            x_max=2.5,
            y_min=-2.5,
            y_max=2.5,
            number_line_config={'unit_size': 1.5}
        )
        for axis in axes:
            numbers = list(range(-2, 3))
            numbers.remove(0)
            axis.add_numbers(*numbers)

        self.init_tracked_point()
        self.init_dot()

    def show_input_dot(self):
        axes = self.axes
        dot = self.dot
        point_mob = self.tracked_point

        point_mob.move_to(self.get_start_point())
        self.add(dot)
        self.continual_update(0)
        self.remove(dot)

        p_tex = "\\vec{\\textbf{p}}"
        fp_label = self.fp_label = TexMobject("f(", p_tex, ")")
        fp_label.set_color_by_tex(p_tex, YELLOW)

        self.play(Write(axes, run_time=3))
        self.wait(3)
        dc = dot.copy()
        self.play(
            FadeInFrom(dc, 2 * UP, remover=True),
            UpdateFromFunc(fp_label, lambda fp: fp.next_to(dc, UL, SMALL_BUFF))
        )
        self.add(dot)
        fp_label.add_updater(
            lambda fp: fp.next_to(dot, UL, SMALL_BUFF)
        )
        self.wait(2)

    def draw_path(self, path,
                  run_time=4,
                  dot_follow=True,
                  uncreate=False,
                  added_anims=None
                  ):
        added_anims = added_anims or []
        point_mob = self.tracked_point
        shadow_path = path.deepcopy().fade(1)
        flat_path = self.modify_path(path)
        anims = [
            ShowCreation(flat_path),
            ShowCreation(shadow_path),
        ]
        if dot_follow:
            anims.append(UpdateFromFunc(
                point_mob,
                lambda p: p.move_to(shadow_path.point_from_proportion(1))
            ))
        self.add(flat_path, self.dot)
        self.play(*anims, run_time=run_time)

        if uncreate:
            self.wait()
            self.remove(shadow_path)
            self.play(
                Uncreate(flat_path),
                run_time=run_time
            )

    def show_antipodal_point(self):
        dot = self.dot
        pre_path = VMobject().set_points_smoothly([
            ORIGIN, DOWN, DOWN + 2 * RIGHT,
            3 * RIGHT + 0.5 * UP, 0.5 * RIGHT, ORIGIN
        ])
        pre_path.rotate(-45 * DEGREES, about_point=ORIGIN)
        pre_path.shift(dot.get_center())
        path = DashedMobject(pre_path)

        fp_label = self.fp_label
        equals = TexMobject("=")
        equals.next_to(fp_label, RIGHT, SMALL_BUFF)
        f_neg_p = TexMobject("f(", "-\\vec{\\textbf{p}}", ")")
        f_neg_p[1].set_color(RED)
        f_neg_p.next_to(equals, RIGHT)

        gp_label = TexMobject("g", "(", "\\vec{\\textbf{p}}", ")")
        gp_label[0].set_color(GREEN)
        gp_label[2].set_color(YELLOW)
        gp_label.add_updater(lambda m: m.next_to(dot, UL, SMALL_BUFF))
        self.gp_label = gp_label
        # gp_label.next_to(Dot(ORIGIN), UL, SMALL_BUFF)

        self.play(ShowCreation(path, run_time=4))
        self.wait()
        self.play(
            Write(equals),
            Write(f_neg_p),
        )
        self.wait(6)
        self.play(
            FadeOut(VGroup(path, equals, f_neg_p))
        )
        dot.clear_updaters()
        self.add(fp_label, gp_label)
        gp_label.set_background_stroke(width=0)
        self.play(
            dot.move_to, ORIGIN,
            VFadeOut(fp_label),
            VFadeIn(gp_label),
        )
        self.wait(4)
        self.play(
            dot.move_to, self.odd_func(self.get_start_point())
        )
        # Flip, 2 second for flip, 7 seconds after
        path = self.get_antipodal_path()
        path.apply_function(self.odd_func)
        end_dot = Dot(color=RED)
        end_dot.move_to(path[-1].point_from_proportion(1))
        g_neg_p = TexMobject(
            "g", "(", "-\\vec{\\textbf{p}}", ")"
        )
        g_neg_p[0].set_color(GREEN)
        g_neg_p[2].set_color(RED)
        g_neg_p.next_to(end_dot, UR, SMALL_BUFF)
        reflection_line = DashedLine(
            dot.get_center(), end_dot.get_center(),
            stroke_width=0,
        )
        vector = Vector(dot.get_center())

        self.play(ShowCreation(path, run_time=1))
        self.wait()
        self.play(
            ShowCreationThenDestruction(reflection_line, run_time=2),
            TransformFromCopy(dot, end_dot),
            ReplacementTransform(
                gp_label.deepcopy().clear_updaters(), g_neg_p
            ),
        )
        self.wait()
        self.play(FadeIn(vector))
        self.play(Rotate(vector, angle=PI, about_point=ORIGIN))
        self.play(FadeOut(vector))
        self.play(
            FadeOut(end_dot),
            FadeOut(g_neg_p),
            FadeOut(path),
        )

    def show_equator(self):
        dot = self.dot
        point_mob = self.tracked_point
        equator = self.get_lat_line()
        flat_eq = equator.deepcopy().apply_function(self.odd_func)
        equator.fade(1)

        equator_start = equator[0].point_from_proportion(0)

        # To address
        self.play(
            point_mob.move_to, equator_start,
            dot.move_to, self.odd_func(equator_start)
        )
        dot.add_updater(lambda m: m.move_to(
            self.odd_func(point_mob.get_center())
        ))
        self.play(
            ShowCreation(equator),
            ShowCreation(flat_eq),
            run_time=4,
        )
        for x in range(2):
            self.play(
                Rotate(point_mob, PI, about_point=ORIGIN, axis=OUT),
                run_time=4
            )
            self.wait(3)
        self.play(
            FadeOut(self.dot),
            FadeOut(self.gp_label),
        )

        self.equator = equator
        self.flat_eq = flat_eq

    def deform_towards_north_pole(self):
        equator = self.equator
        flat_eq = self.flat_eq

        self.play(
            UpdateFromAlphaFunc(
                equator,
                lambda m, a: m.become(self.get_lat_line(a * PI / 2)).set_stroke(width=0),
                run_time=16
            ),
            UpdateFromFunc(
                flat_eq,
                lambda m: m.become(
                    equator.deepcopy().apply_function(self.odd_func).set_stroke(
                        color=RED, width=3
                    )
                )
            )
        )
        self.wait()
    #

    def func(self, point):
        x, y, z = point
        return 0.5 * self.axes.coords_to_point(
            2 * x + 0.5 * y + z,
            2 * y - 0.5 * np.sin(PI * x) + z**2 + 1 - x,
        )

    def odd_func(self, point):
        return (self.func(point) - self.func(-point)) / 2

    def get_dot(self, point):
        return Dot(self.func(point))

    def modify_path(self, path):
        path.apply_function(self.func)
        return path


class RotationOfEquatorGraphInOuputSpace(FunctionGOutputSpace):
    def construct(self):
        self.add(self.axes)
        equator = self.get_lat_line(0)
        equator.remove(*equator[len(equator) // 2:])

        flat_eq = equator.copy().apply_function(self.odd_func)
        vector = Vector(flat_eq[0].point_from_proportion(0))
        vector_copy = vector.copy().fade(0.5)

        self.add(flat_eq)
        self.add(flat_eq.copy())
        self.wait()
        self.play(FadeIn(vector))
        self.add(vector_copy)
        self.play(
            Rotate(
                VGroup(flat_eq, vector),
                PI, about_point=ORIGIN, run_time=5
        ))
        self.play(FadeOut(vector), FadeOut(vector_copy))


class WriteInputSpace(Scene):
    def construct(self):
        self.play(Write(TextMobject("Input space")))
        self.wait()


class WriteOutputSpace(Scene):
    def construct(self):
        self.play(Write(TextMobject("Output space")))
        self.wait()


class LineScene(Scene):
    def construct(self):
        self.add(DashedLine(5 * LEFT, 5 * RIGHT, color=WHITE))


class ShowFlash(Scene):
    def construct(self):
        dot = Dot(ORIGIN, color=YELLOW)
        dot.set_stroke(width=0)
        dot.set_fill(opacity=0)
        self.play(Flash(dot, flash_radius=0.8, line_length=0.6, run_time=2))
        self.wait()


class WaitForIt(Scene):
    def construct(self):
        words = TextMobject("Wait for it", "$\\dots$", arg_separator="")
        words.scale(2)
        self.add(words[0])
        self.play(Write(words[1], run_time=3))
        self.wait()


class DrawSphere(SpecialThreeDScene):
    def construct(self):
        sphere = self.get_sphere()
        sphere.shift(IN)
        question = TextMobject("What \\emph{is} a sphere?")
        question.set_width(FRAME_WIDTH - 3)
        question.to_edge(UP)
        self.move_camera(phi=70 * DEGREES, run_time=0)
        self.begin_ambient_camera_rotation()
        self.add_fixed_in_frame_mobjects(question)
        self.play(
            Write(sphere),
            FadeInFromDown(question)
        )
        self.wait(4)


class DivisionOfUnity(Scene):
    def construct(self):
        factor = 2
        line = Line(factor * LEFT, factor * RIGHT)
        lower_brace = Brace(line, DOWN)
        lower_brace.add(lower_brace.get_text("1"))
        v_lines = VGroup(*[
            DashedLine(0.2 * UP, 0.2 * DOWN).shift(factor * v)
            for v in [LEFT, 0.3 * LEFT, 0.1 * RIGHT, RIGHT]
        ])
        upper_braces = VGroup(*[
            Brace(VGroup(vl1, vl2), UP)
            for vl1, vl2 in zip(v_lines[:-1], v_lines[1:])
        ])
        colors = color_gradient([GREEN, BLUE], 3)
        for i, color, brace in zip(it.count(1), colors, upper_braces):
            label = brace.get_tex("x_%d^2" % i)
            label.set_color(color)
            brace.add(label)

        self.add(line, lower_brace)
        self.play(LaggedStart(
            ShowCreation, v_lines[1:3],
            lag_ratio=0.8,
            run_time=1
        ))
        self.play(LaggedStart(
            GrowFromCenter, upper_braces
        ))
        self.wait()


class ThreeDSpace(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        self.add(axes)
        self.set_camera_orientation(phi=70 * DEGREES, theta=-130 * DEGREES)
        self.begin_ambient_camera_rotation()

        density = 1
        radius = 3
        lines = VGroup(*[
            VGroup(*[
                Line(
                    radius * IN, radius * OUT,
                    stroke_color=WHITE,
                    stroke_width=1,
                    stroke_opacity=0.5,
                ).shift(x * RIGHT + y * UP)
                for x in np.arange(-radius, radius + density, density)
                for y in np.arange(-radius, radius + density, density)
            ]).rotate(n * 120 * DEGREES, axis=[1, 1, 1])
            for n in range(3)
        ])

        self.play(Write(lines))
        self.wait(30)


class NecklaceSphereConnectionTitle(Scene):
    def construct(self):
        text = TextMobject("Necklace Sphere Association")
        text.set_width(FRAME_WIDTH - 1)
        self.add(text)


class BorsukEndScreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "Ali Yahya",
            "Meshal Alshammari",
            "Crypticswarm",
            "Ankit Agarwal",
            "Yu Jun",
            "Shelby Doolittle",
            "Dave Nicponski",
            "Damion Kistler",
            "Juan Benet",
            "Othman Alikhan",
            "Justin Helps",
            "Markus Persson",
            "Dan Buchoff",
            "Derek Dai",
            "Joseph John Cox",
            "Luc Ritchie",
            "Guido Gambardella",
            "Jerry Ling",
            "Mark Govea",
            "Vecht ",
            "Jonathan Eppele",
            "Shimin Kuang",
            "Rish Kundalia",
            "Achille Brighton",
            "Kirk Werklund",
            "Ripta Pasay",
            "Felipe Diniz",
        ],
        "n_patron_columns": 2,
    }


class Thumbnail(SpecialThreeDScene):
    def construct(self):
        sphere = ParametricSurface(
            func=lambda u, v: 2 * np.array([
                np.cos(v) * np.sin(u) + 0.2 * np.cos(3 * u),
                np.sin(v) * np.sin(u),
                np.cos(u) + 0.2 * np.sin(4 * v) - 0.3 * np.cos(3 * u)
            ]),
            resolution=(24, 48),
            u_min=0.001,
            u_max=PI - 0.001,
            v_min=0,
            v_max=TAU,
        )
        sphere.rotate(70 * DEGREES, DOWN)
        self.set_camera_orientation(
            phi=80 * DEGREES,
            theta=-90 * DEGREES,
        )
        # randy = Randolph(mode="telepath")
        # eyes = VGroup(randy.eyes, randy.pupils)
        # eyes.scale(3.5)
        # eyes.rotate(90 * DEGREES, RIGHT)
        # eyes.next_to(sphere, OUT, buff=0)

        self.add(sphere)
