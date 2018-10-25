from big_ol_pile_of_manim_imports import *
from active_projects.quaternions import *

W_COLOR = YELLOW
I_COLOR = GREEN
J_COLOR = RED
K_COLOR = BLUE


class QuaternionLabel(VGroup):
    CONFIG = {
        "decimal_config": {}
    }

    def __init__(self, quat, **kwargs):
        VGroup.__init__(self, **kwargs)
        dkwargs = dict(self.decimal_config)
        decimals = VGroup()
        decimals.add(DecimalNumber(quat[0], color=W_COLOR, **dkwargs))
        dkwargs["include_sign"] = True
        decimals.add(
            DecimalNumber(quat[1], color=I_COLOR, **dkwargs),
            DecimalNumber(quat[2], color=J_COLOR, **dkwargs),
            DecimalNumber(quat[3], color=K_COLOR, **dkwargs),
        )
        self.add(
            decimals[0],
            decimals[1], TexMobject("i"),
            decimals[2], TexMobject("j"),
            decimals[3], TexMobject("k"),
        )
        self.arrange_submobjects(RIGHT, buff=SMALL_BUFF)

        self.decimals = decimals

    def set_value(self, quat):
        for decimal, coord in zip(self.decimals, quat):
            decimal.set_value(coord)
        return self


class RandyPrism(Cube):
    CONFIG = {
        "height": 0.25,
        "width": 1,
        "depth": 1.2,
        "fill_color": BLUE_D,
        "fill_opacity": 0.9,
        "stroke_color": WHITE,
        "stroke_width": 1,
    }

    def __init__(self, **kwargs):
        Cube.__init__(self, **kwargs)
        self.set_height(1)
        randy = Randolph(mode="pondering")
        randy.set_height(0.8)
        randy.rotate(TAU / 4, RIGHT)
        randy.shift(0.7 * DOWN)
        randy.set_shade_in_3d(True, z_index_as_group=True)
        self.randy = randy
        self.add(randy)
        self.set_height(self.height, stretch=True)
        self.set_width(self.width, stretch=True)
        self.set_depth(self.depth, stretch=True)
        self.center()


class Gimbal(VGroup):
    CONFIG = {
        "inner_r": 1.2,
        "outer_r": 2.6,
    }

    def __init__(self, alpha=0, beta=0, gamma=0, inner_mob=None, **kwargs):
        VGroup.__init__(self, **kwargs)
        r1, r2, r3, r4, r5, r6, r7 = np.linspace(
            self.inner_r, self.outer_r, 7
        )
        rings = VGroup(
            self.get_ring(r5, r6),
            self.get_ring(r3, r4),
            self.get_ring(r1, r2),
        )
        for i, p1, p2 in [(0, r6, r7), (1, r4, r5), (2, r2, r3)]:
            annulus = rings[i]
            lines = VGroup(
                Line(p1 * UP, p2 * UP),
                Line(p1 * DOWN, p2 * DOWN),
            )
            lines.set_stroke(RED)
            annulus.lines = lines
            annulus.add(lines)
        rings[1].lines.rotate(90 * DEGREES, about_point=ORIGIN)
        rings.rotate(90 * DEGREES, RIGHT, about_point=ORIGIN)
        rings.set_shade_in_3d(True)
        self.rings = rings
        self.add(rings)

        if inner_mob is not None:
            corners = [
                inner_mob.get_corner(v1 + v2)
                for v1 in [LEFT, RIGHT]
                for v2 in [IN, OUT]
            ]
            lines = VGroup()
            for corner in corners:
                corner[1] = 0
                line = Line(
                    corner, self.inner_r * normalize(corner),
                    color=WHITE,
                    stroke_width=1
                )
                lines.add(line)
            lines.set_shade_in_3d(True)
            rings[2].add(lines, inner_mob)

        # Rotations
        angles = [alpha, beta, gamma]
        for i, angle in zip(it.count(), angles):
            vect = rings[i].lines[0].get_vector()
            rings[i:].rotate(angle=angle, axis=vect)

    def get_ring(self, in_r, out_r, angle=TAU / 4):
        result = VGroup()
        for start_angle in np.arange(0, TAU, angle):
            start_angle += angle / 2
            sector = AnnularSector(
                inner_radius=in_r,
                outer_radius=out_r,
                angle=angle,
                start_angle=start_angle
            )
            sector.set_fill(LIGHT_GREY, 0.8)
            arcs = VGroup(*[
                Arc(
                    angle=angle,
                    start_angle=start_angle,
                    radius=r
                )
                for r in [in_r, out_r]
            ])
            arcs.set_stroke(BLACK, 1, opacity=0.5)
            sector.add(arcs)
            result.add(sector)
        return result


# Scenes

class ButFirst(TeacherStudentsScene):
    def construct(self):
        for student in self.students:
            student.change("surprised")

        self.teacher_says("But first!")
        self.change_all_student_modes("happy")
        self.play(RemovePiCreatureBubble(
            self.teacher,
            target_mode="raise_right_hand"
        ))
        self.change_student_modes(
            *["pondering"] * 3,
            look_at_arg=self.screen,
        )
        self.play(self.teacher.look_at, self.screen)
        self.wait(4)


class Introduction(QuaternionHistory):
    CONFIG = {
        "names_and_quotes": [
            (
                "Oliver Heaviside",
                """\\Huge ``the quaternion was not only not
                required, but was a positive evil''"""
            ),
            (
                "Lord Kelvin",
                """\\Huge ``Quaternions... though beautifully \\\\ ingenious,
                have been an unmixed evil'' """
            ),
        ]
    }

    def construct(self):
        title_word = TextMobject("Quaternions:")
        title_equation = TexMobject(
            "i^2 = j^2 = k^2 = ijk = -1",
            tex_to_color_map={
                "i": I_COLOR,
                "j": J_COLOR,
                "k": K_COLOR,
            }
        )
        # label = QuaternionLabel([
        #     float(str((TAU * 10**(3 * k)) % 10)[:4])
        #     for k in range(4)
        # ])
        title = VGroup(title_word, title_equation)
        title.arrange_submobjects(RIGHT)
        title.to_edge(UP)

        images_group = self.get_dissenter_images_quotes_and_names()
        images_group.to_edge(DOWN)
        images, quotes, names = images_group
        for pair in images_group:
            pair[1].align_to(pair[0], UP)

        self.play(
            FadeInFromDown(title_word),
            Write(title_equation)
        )
        self.wait()
        for image, name, quote in zip(images, names, quotes):
            self.play(
                FadeInFrom(image, 3 * DOWN),
                FadeInFromLarge(name),
                LaggedStart(
                    FadeIn, VGroup(*it.chain(*quote)),
                    lag_ratio=0.3,
                    run_time=2
                )
            )
        self.wait(2)
        self.play(
            title.shift, 2 * UP,
            *[
                ApplyMethod(mob.shift, FRAME_WIDTH * vect / 2)
                for pair in images_group
                for mob, vect in zip(pair, [LEFT, RIGHT])
            ],
        )


class WhoCares(TeacherStudentsScene):
    def construct(self):
        quotes = Group(*[
            ImageMobject(
                "CoderQuaternionResponse_{}".format(d),
                height=2
            )
            for d in range(4)
        ])
        logos = Group(*[
            ImageMobject(name, height=0.5)
            for name in [
                "TwitterLogo",
                "HackerNewsLogo",
                "RedditLogo",
                "YouTubeLogo",
            ]
        ])
        for quote, logo in zip(quotes, logos):
            logo.move_to(quote.get_corner(UR))
            quote.add(logo)

        quotes.arrange_submobjects_in_grid()
        quotes.set_height(4)
        quotes.to_corner(UL)

        self.student_says(
            "Um...who cares?",
            target_mode="sassy",
            added_anims=[self.teacher.change, "guilty"]
        )
        self.change_student_modes("angry", "sassy", "sad")
        self.wait(2)
        self.play(
            RemovePiCreatureBubble(self.students[1]),
            self.teacher.change, "raise_right_hand"
        )
        # self.play(
        #     LaggedStart(
        #         FadeInFromDown, quotes,
        #         run_time=3
        #     ),
        #     self.get_student_changes(*3 * ["pondering"], look_at_arg=quotes)
        # )
        # self.wait(2)

        # # Show HN
        # hn_quote = quotes[1]
        # hn_context = TextMobject("news.ycombinator.com/item?id=17933908")
        # hn_context.scale(0.7)
        # hn_context.to_corner(UL)

        # vr_headsets = VGroup()
        # for pi in self.students:
        #     vr_headset = SVGMobject("VR_headset")
        #     vr_headset.set_fill(LIGHT_GREY, opacity=0.9)
        #     vr_headset.set_width(pi.eyes.get_width() + 0.3)
        #     vr_headset.move_to(pi.eyes)
        #     vr_headsets.add(vr_headset)

        # self.play(
        #     hn_quote.scale, 2, {"about_edge": DL},
        #     FadeOutAndShift(quotes[0], 5 * UP),
        #     FadeOutAndShift(quotes[2], UR),
        #     FadeOutAndShift(quotes[3], RIGHT),
        #     FadeInFromDown(hn_context),
        # )
        # hn_rect = Rectangle(
        #     height=0.1 * hn_quote.get_height(),
        #     width=0.6 * hn_quote.get_width(),
        #     color=RED
        # )
        # hn_rect.move_to(hn_quote, UL)
        # hn_rect.shift(0.225 * RIGHT + 0.75 * DOWN)
        # self.play(
        #     ShowCreation(hn_rect),
        #     self.get_student_changes(
        #         "erm", "thinking", "confused",
        #         look_at_arg=hn_quote,
        #     )
        # )
        # self.add_foreground_mobjects(vr_headsets)
        # self.play(
        #     LaggedStart(
        #         FadeInFrom, vr_headsets,
        #         lambda m: (m, UP),
        #     ),
        #     self.get_student_changes(
        #         *3 * ["sick"],
        #         look_at_arg=hn_quote,
        #         run_time=3
        #     )
        # )
        # self.wait(3)

        # Show Twitter
        t_quote = quotes[0]
        # t_quote.next_to(FRAME_WIDTH * LEFT / 2 + FRAME_WIDTH * UP / 2, UR)
        # t_quote.set_opacity(0)
        # self.play(
        #     FadeOutAndShift(hn_quote, 4 * LEFT),
        #     FadeOutAndShift(hn_rect, 4 * LEFT),
        #     FadeOutAndShift(hn_context, UP),
        #     FadeOut(vr_headsets),
        #     t_quote.set_opacity, 1,
        #     t_quote.scale, 2,
        #     t_quote.to_corner, UL,
        # )
        # self.remove_foreground_mobjects(vr_headsets)
        t_quote.fade(1)
        t_quote.to_corner(UL)
        self.play(
            self.get_student_changes(*3 * ["pondering"], look_at_arg=quotes),
            t_quote.set_opacity, 1,
            t_quote.scale, 2,
            t_quote.to_corner, UL,
        )
        self.wait(2)
        self.change_student_modes(
            "pondering", "happy", "tease",
            look_at_arg=t_quote
        )
        self.wait(2)
        self.play(FadeOut(t_quote))
        self.wait(5)


class ShowSeveralQuaternionRotations(SpecialThreeDScene):
    CONFIG = {
        "quaternions": [
            [0, 1, 0, 0],
            [1, 0, 0, 0],
            [1, 0, 1, 0],
            [1, 1, 1, -1],
            [0, -1, 2, 1],
            [1, 0, 0, -1],
            [1, -1, 0, 0],
            [1, -1, 1, 0],
            [1, -1, 1, -1],
            [1, 0, 0, 0],
        ],
        "start_phi": 70 * DEGREES,
        "start_theta": -140 * DEGREES,
        "ambient_rotation_rate": 0.01,
    }

    def construct(self):
        self.add_q_tracker()
        self.setup_labels()
        self.setup_camera_position()
        self.add_prism()
        self.add_axes()
        self.apply_quaternions()

    def add_q_tracker(self):
        self.q_tracker = QuaternionTracker()
        self.q_tracker.add_updater(lambda m: m.normalize())
        self.add(self.q_tracker)

    def setup_labels(self):
        left_q_label = QuaternionLabel([1, 0, 0, 0])
        right_q_label = QuaternionLabel([1, 0, 0, 0])
        for label in left_q_label, right_q_label:
            lp, rp = TexMobject("()")
            lp.next_to(label, LEFT, SMALL_BUFF)
            rp.next_to(label, RIGHT, SMALL_BUFF)
            label.add(lp, rp)
        point_label = TexMobject(
            *"(xi+yj+zk)",
            tex_to_color_map={
                "i": I_COLOR,
                "j": J_COLOR,
                "k": K_COLOR,
            }
        )
        left_q_label.next_to(point_label, LEFT)
        right_q_label.next_to(point_label, RIGHT)
        group = VGroup(left_q_label, point_label, right_q_label)
        group.arrange_submobjects(RIGHT)
        group.set_width(FRAME_WIDTH - 1)
        group.to_edge(UP)
        self.add_fixed_in_frame_mobjects(BackgroundRectangle(group))

        for label, text in zip(group, ["$q$", "Some 3d point", "$q^{-1}$"]):
            brace = Brace(label, DOWN)
            text_mob = TextMobject(text)
            if text_mob.get_width() > brace.get_width():
                text_mob.match_width(brace)
            text_mob.next_to(brace, DOWN, buff=SMALL_BUFF)
            text_mob.add_background_rectangle()
            label.add(brace, text_mob)

        self.add_fixed_in_frame_mobjects(*group)

        left_q_label.add_updater(
            lambda m: m.set_value(self.q_tracker.get_value())
        )
        left_q_label.add_updater(lambda m: self.add_fixed_in_frame_mobjects(m))
        right_q_label.add_updater(
            lambda m: m.set_value(quaternion_conjugate(
                self.q_tracker.get_value()
            ))
        )
        right_q_label.add_updater(lambda m: self.add_fixed_in_frame_mobjects(m))

    def setup_camera_position(self):
        self.set_camera_orientation(
            phi=self.start_phi,
            theta=self.start_theta,
        )
        self.begin_ambient_camera_rotation(self.ambient_rotation_rate)

    def add_prism(self):
        prism = self.prism = self.get_prism()
        prism.add_updater(
            lambda p: p.become(self.get_prism(
                self.q_tracker.get_value()
            ))
        )
        self.add(prism)

    def add_axes(self):
        axes = self.axes = updating_mobject_from_func(self.get_axes)
        self.add(axes)

    def apply_quaternions(self):
        for quat in self.quaternions:
            self.change_q(quat)
            self.wait(2)

    #
    def get_unrotated_prism(self):
        return RandyPrism().scale(2)

    def get_prism(self, quaternion=[1, 0, 0, 0]):
        prism = self.get_unrotated_prism()
        angle, axis = angle_axis_from_quaternion(quaternion)
        prism.rotate(angle=angle, axis=axis, about_point=ORIGIN)
        return prism

    def get_axes(self):
        prism = self.prism
        centers = [sm.get_center() for sm in prism[:6]]
        axes = VGroup()
        for i in range(3):
            for u in [-1, 1]:
                vect = np.zeros(3)
                vect[i] = u
                dots = [np.dot(normalize(c), vect) for c in centers]
                max_i = np.argmax(dots)
                ec = centers[max_i]
                prism.get_edge_center(vect)
                p1 = np.zeros(3)
                p1[i] = ec[i]
                p1 *= dots[max_i]
                p2 = 10 * vect
                axes.add(Line(p1, p2))
        axes.set_stroke(LIGHT_GREY, 1)
        axes.set_shade_in_3d(True)
        return axes

    def change_q(self, value, run_time=3, added_anims=None, **kwargs):
        if added_anims is None:
            added_anims = []
        self.play(
            self.q_tracker.set_value, value,
            *added_anims,
            run_time=run_time,
            **kwargs
        )


class PauseAndPlayOverlay(Scene):
    def construct(self):
        pause = TexMobject("=").rotate(TAU / 4)
        pause.stretch(2, 0)
        pause.scale(1.5)
        arrow = Vector(RIGHT, color=WHITE)
        interact = TextMobject("Interact...")
        group = VGroup(pause, arrow, interact)
        group.arrange_submobjects(RIGHT)
        group.scale(2)

        not_yet = TextMobject("...well, not yet")
        not_yet.scale(2)
        not_yet.next_to(group, DOWN, MED_LARGE_BUFF)

        self.play(Write(pause))
        self.play(
            GrowFromPoint(
                interact, arrow.get_left(),
                rate_func=squish_rate_func(smooth, 0.3, 1)
            ),
            VFadeIn(interact),
            GrowArrow(arrow),
        )
        self.wait(2)
        self.play(Write(not_yet))
        self.wait()


class RotationMatrix(ShowSeveralQuaternionRotations):
    CONFIG = {
        "start_phi": 60 * DEGREES,
        "start_theta": -60 * DEGREES,
    }

    def construct(self):
        self.add_q_tracker()
        self.setup_camera_position()
        self.add_prism()
        self.add_basis_vector_labels()
        self.add_axes()

        title = TextMobject("Rotation matrix")
        title.scale(1.5)
        title.to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)

        angle = 75 * DEGREES
        axis = [0.3, 1, 0.3]
        matrix = rotation_matrix(angle=angle, axis=axis)
        matrix_mob = DecimalMatrix(matrix, h_buff=1.6)
        matrix_mob.next_to(title, DOWN)
        matrix_mob.to_edge(LEFT)
        title.next_to(matrix_mob, UP)
        self.add_fixed_in_frame_mobjects(matrix_mob)

        colors = [I_COLOR, J_COLOR, K_COLOR]
        matrix_mob.set_column_colors(*colors)

        columns = matrix_mob.get_columns()
        column_rects = VGroup(*[
            SurroundingRectangle(c).match_color(c[0])
            for c in columns
        ])
        labels = VGroup(*[
            TextMobject(
                "Where", tex, "goes",
                tex_to_color_map={tex: rect.get_color()}
            ).next_to(rect, DOWN)
            for letter, rect in zip(["\\i", "\\j", "k"], column_rects)
            for tex in ["$\\hat{\\textbf{%s}}$" % (letter)]
        ])
        labels.space_out_submobjects(0.8)

        quaternion = quaternion_from_angle_axis(angle, axis)

        self.play(Write(matrix_mob))
        self.change_q(quaternion)
        self.wait()
        last_label = VectorizedPoint(matrix_mob.get_bottom())
        last_rect = VMobject()
        for label, rect in zip(labels, column_rects):
            self.add_fixed_in_frame_mobjects(rect, label)
            self.play(
                FadeIn(label),
                FadeOut(last_label),
                ShowCreation(rect),
                FadeOut(last_rect)
            )
            self.wait()
            last_label = label
            last_rect = rect
        self.play(FadeOut(last_label), FadeOut(last_rect))
        self.wait(5)

    def get_unrotated_prism(self):
        prism = RandyPrism()
        prism.scale(1.5)
        arrows = VGroup()
        for i, color in enumerate([I_COLOR, J_COLOR, K_COLOR]):
            vect = np.zeros(3)
            vect[i] = 1
            arrow = Arrow(
                prism.get_edge_center(vect), 2 * vect,
                preserve_tip_size_when_scaling=False,
                color=color,
                buff=0,
            )
            arrows.add(arrow)
        arrows.set_shade_in_3d(True)
        prism.arrows = arrows
        prism.add(arrows)
        return prism

    def add_basis_vector_labels(self):
        labels = VGroup(
            TexMobject("\\hat{\\textbf{\\i}}"),
            TexMobject("\\hat{\\textbf{\\j}}"),
            TexMobject("\\hat{\\textbf{k}}"),
        )

        def generate_updater(arrow):
            return lambda m: m.move_to(
                arrow.get_end() + 0.2 * normalize(arrow.get_vector()),
            )

        for arrow, label in zip(self.prism.arrows, labels):
            label.match_color(arrow)
            label.add_updater(generate_updater(arrow))
            self.add_fixed_orientation_mobjects(label)


class EulerAnglesAndGimbal(ShowSeveralQuaternionRotations):
    def construct(self):
        self.setup_position()
        self.setup_angle_trackers()
        self.setup_gimbal()
        self.add_axes()
        self.add_title()
        self.show_rotations()

    def setup_position(self):
        self.set_camera_orientation(
            theta=-140 * DEGREES,
            phi=70 * DEGREES,
        )
        self.begin_ambient_camera_rotation(rate=0.015)

    def setup_angle_trackers(self):
        self.alpha_tracker = ValueTracker(0)
        self.beta_tracker = ValueTracker(0)
        self.gamma_tracker = ValueTracker(0)

    def setup_gimbal(self):
        gimbal = updating_mobject_from_func(self.get_gimbal)
        self.gimbal = gimbal
        self.add(gimbal)

    def add_title(self):
        title = TextMobject("Euler angles")
        title.scale(1.5)
        title.to_corner(UL)
        angle_labels = VGroup(
            TexMobject("\\alpha").set_color(YELLOW),
            TexMobject("\\beta").set_color(GREEN),
            TexMobject("\\gamma").set_color(PINK),
        )
        angle_labels.scale(2)
        angle_labels.arrange_submobjects(RIGHT, buff=MED_LARGE_BUFF)
        angle_labels.next_to(title, DOWN, aligned_edge=LEFT)
        self.angle_labels = angle_labels

        gl_label = VGroup(
            Arrow(LEFT, RIGHT, color=WHITE),
            TextMobject("Gimbal lock").scale(1.5),
        )
        gl_label.arrange_submobjects(RIGHT)
        gl_label.next_to(title, RIGHT)
        self.gimbal_lock_label = gl_label

        VGroup(title, angle_labels, gl_label).center().to_edge(UP)

        self.add_fixed_in_frame_mobjects(title, angle_labels, gl_label)
        self.remove(angle_labels)
        self.remove(gl_label)

    def show_rotations(self):
        gimbal = self.gimbal
        alpha_tracker = self.alpha_tracker
        beta_tracker = self.beta_tracker
        gamma_tracker = self.gamma_tracker

        angles = [-60 * DEGREES, 50 * DEGREES, 45 * DEGREES]
        trackers = [alpha_tracker, beta_tracker, gamma_tracker]
        in_rs = [0.6, 0.5, 0.6]
        for i in range(3):
            tracker = trackers[i]
            angle = angles[i]
            in_r = in_rs[i]
            ring = gimbal.rings[i]

            vect = ring.lines[0].get_vector()
            line = self.get_dotted_line(vect, in_r=in_r)
            angle_label = self.angle_labels[i]
            line.match_color(angle_label)
            self.play(
                ShowCreation(line),
                FadeInFromDown(angle_label)
            )
            self.play(
                tracker.set_value, angle,
                run_time=3
            )
            self.play(FadeOut(line))
            self.wait()
        self.wait(3)
        self.play(Write(self.gimbal_lock_label))
        self.play(
            alpha_tracker.set_value, 0,
            beta_tracker.set_value, 0,
            run_time=2
        )
        self.play(
            alpha_tracker.set_value, 90 * DEGREES,
            gamma_tracker.set_value, -90 * DEGREES,
            run_time=3
        )
        self.play(
            FadeOut(self.gimbal_lock_label),
            *[ApplyMethod(t.set_value, 0) for t in trackers],
            run_time=3
        )
        self.play(
            alpha_tracker.set_value, 30 * DEGREES,
            beta_tracker.set_value, 120 * DEGREES,
            gamma_tracker.set_value, -50 * DEGREES,
            run_time=3
        )
        self.play(
            alpha_tracker.set_value, 120 * DEGREES,
            beta_tracker.set_value, -30 * DEGREES,
            gamma_tracker.set_value, 90 * DEGREES,
            run_time=4
        )
        self.play(
            beta_tracker.set_value, 150 * DEGREES,
            run_time=2
        )
        self.play(
            alpha_tracker.set_value, 0,
            beta_tracker.set_value, 0,
            gamma_tracker.set_value, 0,
            run_time=4
        )
        self.wait()

    #
    def get_gimbal(self):
        self.prism = RandyPrism()
        return Gimbal(
            alpha=self.alpha_tracker.get_value(),
            beta=self.beta_tracker.get_value(),
            gamma=self.gamma_tracker.get_value(),
            inner_mob=self.prism
        )

    def get_dotted_line(self, vect, in_r=0, out_r=10):
        line = VGroup(*it.chain(*[
            DashedLine(
                in_r * normalize(u * vect),
                out_r * normalize(u * vect),
            )
            for u in [-1, 1]
        ]))
        line.sort_submobjects(get_norm)
        line.set_shade_in_3d(True)
        line.set_stroke(YELLOW, 5)
        line.center()
        return line


class InterpolationFail(Scene):
    def construct(self):
        words = TextMobject(
            "Sometimes interpolating 3d\\\\"
            "orientations is tricky..."
        )
        words.to_edge(UP)
        self.add(words)


class QuaternionInterpolation(ShowSeveralQuaternionRotations):
    def construct(self):
        self.add_q_tracker()
        self.setup_camera_position()
        self.add_prism()
        self.add_axes()

        self.change_q([1, 1, 1, 0], run_time=0)
        self.wait(2)
        self.change_q([1, 0.2, 0.6, -0.5], run_time=4)
        self.wait(2)
        self.change_q([1, -0.6, 0.2, -1], run_time=4)
        self.wait(2)


class QuaternionInterpolationScematic(Scene):
    def construct(self):
        title = TextMobject("Slice of a hypersphere")
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        self.add(title)

        radius = 3
        circle = Circle(radius=radius)
        circle.set_stroke(LIGHT_GREY, 1)
        qs = [circle.point_from_proportion(p) for p in (0.55, 0.35, 0.15)]
        colors = [YELLOW, PINK, RED]
        q_dots = [Dot(q, color=c) for q, c in zip(qs, colors)]
        q_labels = [
            TexMobject("q_{}".format(i + 1)).next_to(
                dot, normalize(dot.get_center()), SMALL_BUFF
            ).match_color(dot)
            for i, dot in enumerate(q_dots)
        ]

        q1, q2, q3 = qs
        lines = [
            DashedLine(q1, q2)
            for q1, q2 in zip(qs, qs[1:])
        ]
        for color, line in zip([GREEN, BLUE], lines):
            line.set_stroke(color, 3)
            line.proj = line.copy().apply_function(
                lambda p: radius * normalize(p)
            )
        dot = Dot(qs[0], color=WHITE)

        self.add(circle)
        self.add(dot)
        self.add(*q_dots + q_labels)

        self.wait(2)
        for line, q in zip(lines, qs[1:]):
            self.play(
                ShowCreation(line),
                ShowCreation(line.proj),
                dot.move_to, q,
                run_time=4
            )
            self.wait(2)


class RememberComplexNumbers(TeacherStudentsScene):
    def construct(self):
        complex_number = TexMobject(
            "\\cos(\\theta) + \\sin(\\theta)i",
            tex_to_color_map={
                "\\cos(\\theta)": GREEN,
                "\\sin(\\theta)": RED
            }
        )
        complex_number.scale(1.2)
        complex_number.next_to(self.students, UP, MED_LARGE_BUFF)

        self.teacher_says(
            "Remember how \\\\ complex numbers \\\\ compute rotations"
        )
        self.change_all_student_modes("pondering")
        self.wait()
        self.play(
            FadeInFromDown(complex_number),
            self.get_student_changes(
                "thinking", "confused", "happy",
                look_at_arg=complex_number.get_center() + UP
            ),
            run_time=2
        )
        self.change_student_modes(
        )
        self.wait(5)


class ComplexNumberRotation(Scene):
    CONFIG = {
        "angle": 30 * DEGREES,
    }

    def construct(self):
        self.add_plane()
        self.add_number()
        self.show_complex_unit()
        self.show_product()

    def add_plane(self):
        plane = self.plane = ComplexPlane()
        self.play(Write(plane))

    def add_number(self):
        plane = self.plane
        origin = plane.coords_to_point(0, 0)
        angle = self.angle

        point = plane.coords_to_point(4, 1)
        dot = Dot(point, color=YELLOW)
        label = TexMobject("(4, 1)")
        label.next_to(dot, UR, buff=0)
        line = DashedLine(origin, point)
        rotated_line = line.copy().rotate(angle, about_point=origin)
        rotated_line.set_color(GREY)
        rotated_dot = dot.copy().rotate(angle, about_point=origin)
        rotated_dot.set_color(YELLOW_E)
        mystery_label = TexMobject("(?, ?)")
        mystery_label.next_to(rotated_dot, UR, buff=0)

        arc = Arc(
            start_angle=line.get_angle(),
            angle=angle,
            radius=0.75
        )
        angle_tex = str(int(np.round(angle / DEGREES))) + "^\\circ"
        angle_label = TexMobject(angle_tex)
        angle_label.next_to(
            arc.point_from_proportion(0.3),
            UR, buff=SMALL_BUFF
        )

        self.play(
            FadeInFromDown(label),
            GrowFromCenter(dot),
            ShowCreation(line)
        )
        self.wait()
        self.play(
            ShowCreation(arc),
            FadeInFromDown(angle_label),
            TransformFromCopy(line, rotated_line),
            TransformFromCopy(dot, rotated_dot),
            path_arc=angle,
        )
        self.play(Write(mystery_label))
        self.wait()

        self.rotation_mobs = VGroup(
            arc, angle_label,
            rotated_line, rotated_dot,
            mystery_label
        )
        self.angle_tex = angle_tex
        self.number_label = label

    def show_complex_unit(self):
        plane = self.plane
        angle = self.angle
        angle_tex = self.angle_tex
        complex_coordinate_labels = plane.get_coordinate_labels()
        unit_circle = Circle(radius=1, color=YELLOW)

        origin = plane.number_to_point(0)
        z_point = plane.coords_to_point(np.cos(angle), np.sin(angle))
        one_point = plane.number_to_point(1)
        z_dot = Dot(z_point, color=WHITE)
        one_dot = Dot(one_point, color=WHITE)
        one_dot.fade(1)
        z_line = Line(origin, z_point)
        one_line = Line(origin, one_point)
        VGroup(z_dot, one_dot, z_line, one_line).set_color(BLUE)

        cos_tex = "\\cos(" + angle_tex + ")"
        sin_tex = "\\sin(" + angle_tex + ")"
        label = TexMobject(
            cos_tex, "+", sin_tex, "i",
            tex_to_color_map={cos_tex: GREEN, sin_tex: RED}
        )
        label.add_background_rectangle()
        label.scale(0.8)
        label.next_to(plane.coords_to_point(0, 1), UR, SMALL_BUFF)
        arrow = Arrow(label.get_bottom(), z_point)

        number_label = self.number_label
        new_number_label = TexMobject(
            "4 + 1i", tex_to_color_map={"4": GREEN, "1": RED}
        )
        new_number_label.move_to(number_label, LEFT)
        new_number_label.add_background_rectangle()

        self.play(
            Write(complex_coordinate_labels, run_time=2),
            FadeOut(self.rotation_mobs)
        )
        self.play(ShowCreation(unit_circle))
        self.play(
            TransformFromCopy(one_dot, z_dot),
            TransformFromCopy(one_line, z_line),
            FadeInFromDown(label),
            GrowArrow(arrow),
        )
        self.wait()
        self.play(FadeOutAndShiftDown(number_label))
        self.play(FadeInFromDown(new_number_label))
        self.wait()

        self.left_z_label = label
        self.right_z_label = new_number_label
        self.cos_tex = cos_tex
        self.sin_tex = sin_tex
        self.unit_z_group = VGroup(
            unit_circle, z_line, z_dot, label, arrow
        )

    def show_product(self):
        plane = self.plane
        cos_tex = self.cos_tex
        sin_tex = self.sin_tex
        angle = self.angle

        line = Line(
            FRAME_WIDTH * LEFT / 2 + FRAME_HEIGHT * UP / 2,
            plane.coords_to_point(-0.5, 1.5)
        )
        rect = BackgroundRectangle(line, buff=0)

        left_z = self.left_z_label
        right_z = self.right_z_label
        new_left_z = left_z.copy()
        new_right_z = right_z.copy()

        lp1, rp1, lp2, rp2 = parens = TexMobject("()()")
        top_line = VGroup(
            lp1, new_left_z, rp1,
            lp2, new_right_z, rp2,
        )
        top_line.arrange_submobjects(RIGHT, buff=SMALL_BUFF)
        top_line.set_width(rect.get_width() - 1)
        top_line.next_to(rect.get_top(), DOWN, MED_SMALL_BUFF)

        mid_line = TexMobject(
            "\\big(", "4", cos_tex, "-", "1", sin_tex, "\\big)", "+",
            "\\big(", "1", cos_tex, "+", "4", sin_tex, "\\big)", "i",
            tex_to_color_map={
                cos_tex: GREEN,
                sin_tex: RED,
                "4": GREEN,
                "1": RED,
            }
        )
        mid_line.set_width(rect.get_width() - 0.5)
        mid_line.next_to(top_line, DOWN, MED_LARGE_BUFF)

        new_z = np.exp(angle * complex(0, 1)) * complex(4, 1)
        low_line = TexMobject(
            "\\approx",
            str(np.round(new_z.real, 2)), "+",
            str(np.round(new_z.imag, 2)), "i",
        )
        low_line.next_to(mid_line, DOWN, MED_LARGE_BUFF)

        self.play(FadeIn(rect))
        self.play(
            TransformFromCopy(left_z, new_left_z),
            TransformFromCopy(right_z, new_right_z),
            Write(parens)
        )
        self.wait()
        self.play(FadeInFrom(mid_line, UP))
        self.wait()
        self.play(FadeInFrom(low_line, UP))
        self.wait(2)
        self.play(FadeOut(self.unit_z_group))
        self.rotation_mobs.save_state()
        self.rotation_mobs.rotate(-angle, about_point=ORIGIN)
        self.rotation_mobs.fade(1)
        self.play(self.rotation_mobs.restore)
        self.wait()

        mystery_label = self.rotation_mobs[-1]
        result = low_line[1:].copy()
        result.add_background_rectangle()
        self.play(
            result.move_to, mystery_label, LEFT,
            FadeOutAndShiftDown(mystery_label),
        )
        self.wait()


class ISquaredRule(Scene):
    def construct(self):
        tex = TextMobject("Use", "$i^2 = -1$")
        tex[1].set_color(RED)
        tex.scale(2)
        self.add(tex)
        self.play(Write(tex))
        self.wait()


class RuleForQuaternionRotations(EulerAnglesAndGimbal):
    CONFIG = {
        "start_phi": 70 * DEGREES,
        "start_theta": -120 * DEGREES,
        "ambient_rotation_rate": 0.015,
    }

    def construct(self):
        self.add_q_tracker()
        self.setup_camera_position()
        self.add_prism()
        self.add_axes()

        self.show_axis()
        self.construct_quaternion()
        self.add_point_with_coordinates()
        self.add_inverse()

    def get_axes(self):
        axes = EulerAnglesAndGimbal.get_axes(self)
        for axis in axes:
            vect = normalize(axis.get_vector())
            perp = rotate_vector(vect, TAU / 3, axis=[1, 1, 1])
            for i in range(1, 4):
                tick = Line(-perp, perp).scale(0.1)
                tick.match_style(axis)
                tick.move_to(2 * i * vect)
                axis.add(tick)
        axes.set_shade_in_3d(True)
        return axes

    def show_axis(self):
        vect = normalize([1, -1, -0.5])
        line = self.get_dotted_line(vect, 0, 4)
        quat = np.append(0, vect)

        axis_label = TextMobject("Axis of rotation")
        axis_label.next_to(line.get_corner(DR), DOWN, MED_LARGE_BUFF)
        axis_label.match_color(line)

        self.add_fixed_orientation_mobjects(axis_label)
        self.play(
            ShowCreation(line),
            Write(axis_label)
        )
        self.change_q(quat, run_time=2)
        self.change_q([1, 0, 0, 0], run_time=2)

        # Unit vector
        vect_mob = Vector(2 * vect, use_rectangular_stem=False)
        vect_mob.pointwise_become_partial(vect_mob, 0, 0.95)
        pieces = VGroup(*vect_mob.get_pieces(25))
        pieces.set_stroke(vect_mob.get_color(), 2)
        vect_mob.set_stroke(width=0)
        vect_mob.add_to_back(pieces)
        vect_mob.set_shade_in_3d(True)

        vect_label = TexMobject(
            "{:.2f}".format(vect[0]), "i",
            "{:+.2f}".format(vect[1]), "j",
            "{:+.2f}".format(vect[2]), "k",
        )
        magnitude_label = TexMobject(
            "x", "^2 + ",
            "y", "^2 + ",
            "z", "^2 = 1",
        )
        for label in vect_label, magnitude_label:
            decimals = label[::2]
            colors = [I_COLOR, J_COLOR, K_COLOR]
            for d1, color in zip(decimals, colors):
                d1.set_color(color)
            label.rotate(TAU / 4, RIGHT).scale(0.7)
            label.next_to(vect_mob.get_end(), RIGHT, SMALL_BUFF)

        magnitude_label.next_to(vect_label, IN)

        self.play(
            FadeOut(line),
            FadeOutAndShiftDown(axis_label),
            ShowCreation(vect_mob)
        )
        # self.add_fixed_orientation_mobjects(vect_label)
        self.play(FadeInFromDown(vect_label))
        self.wait(3)
        self.play(TransformFromCopy(vect_label, magnitude_label))
        self.wait(3)

        self.vect = vect
        self.vect_mob = vect_mob
        self.vect_label = vect_label
        self.magnitude_label = magnitude_label

    def construct_quaternion(self):
        full_angle_q = self.get_quaternion_label("40^\\circ")
        half_angle_q = self.get_quaternion_label("40^\\circ / 2")
        for label in full_angle_q, half_angle_q:
            label.to_corner(UL)
        brace = Brace(half_angle_q, DOWN)
        q_label = brace.get_tex("q")
        full_angle_q.align_data(half_angle_q)
        rect = SurroundingRectangle(full_angle_q[5])

        for mob in full_angle_q, half_angle_q, brace, q_label, rect:
            self.add_fixed_in_frame_mobjects(mob)
            self.remove(mob)
        self.play(FadeInFromDown(full_angle_q[1]))
        self.wait()
        self.play(
            FadeInFromDown(full_angle_q[0]),
            LaggedStart(FadeInFromDown, full_angle_q[2:]),
        )
        self.play(
            GrowFromCenter(brace),
            Write(q_label)
        )
        self.wait(2)
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.wait(2)
        self.play(ReplacementTransform(full_angle_q, half_angle_q))
        self.wait(6)
        # TODO

    def add_point_with_coordinates(self):
        prism = self.prism
        point = prism.get_corner(UR + OUT)
        template_sphere = Sphere(radius=0.1)
        template_sphere.set_stroke(width=0)
        template_sphere.set_color(PINK)
        ghost_sphere = template_sphere.copy()
        ghost_sphere.fade(0.8)
        for face in template_sphere:
            c = face.get_center()
            if c[0] < 0 and c[2] < 0:
                template_sphere.remove(face)
        template_sphere.move_to(point)
        ghost_sphere.move_to(point)

        def get_sphere():
            result = template_sphere.copy()
            quat = self.q_tracker.get_value()
            angle, axis = angle_axis_from_quaternion(quat)
            result.rotate(angle=angle, axis=axis, about_point=ORIGIN)
            return result

        sphere = updating_mobject_from_func(get_sphere)

        point_label = TexMobject(
            "p", "=",
            "{:.2f}".format(point[0]), "i", "+"
            "{:.2f}".format(point[1]), "j", "+"
            "{:.2f}".format(point[2]), "k",
        )
        colors = [PINK, I_COLOR, J_COLOR, K_COLOR]
        for part, color in zip(point_label[::2], colors):
            part.set_color(color)
        point_label.scale(0.7)
        point_label.rotate(TAU / 4, RIGHT)
        point_label.next_to(point, RIGHT)

        self.stop_ambient_camera_rotation()
        self.begin_ambient_camera_rotation(-0.01)
        self.play(FadeInFromLarge(sphere))
        self.play(Write(point_label))
        self.wait(3)

        # Rotate
        quat = quaternion_from_angle_axis(40 * DEGREES, self.vect)
        r = get_norm(point)
        curved_arrow = Arrow(
            r * RIGHT, rotate_vector(r * RIGHT, 30 * DEGREES, OUT),
            buff=0,
            use_rectangular_stem=False,
            path_arc=60 * DEGREES,
            color=LIGHT_GREY,
        )
        curved_arrow.pointwise_become_partial(curved_arrow, 0, 0.9)
        curved_arrow.rotate(150 * DEGREES, about_point=ORIGIN)
        curved_arrow.apply_matrix(z_to_vector(self.vect))
        self.add(ghost_sphere, sphere)
        self.change_q(
            quat,
            added_anims=[ShowCreation(curved_arrow)],
            run_time=3
        )

        mystery_label = TexMobject("(?, ?, ?)")
        mystery_label.add_background_rectangle()
        arrow = Vector(0.5 * DR, color=WHITE)
        arrow.next_to(mystery_label, DR, buff=0)
        # mystery_label.add(arrow)
        mystery_label.rotate(TAU / 4, RIGHT)
        mystery_label.next_to(sphere, OUT + LEFT, buff=0)
        self.play(FadeInFromDown(mystery_label))
        self.wait(5)

    def add_inverse(self):
        label = TexMobject(
            "p", "\\rightarrow",
            "q", "\\cdot", "p", "\\cdot", "q^{-1}",
            tex_to_color_map={"p": PINK}
        )
        label.to_corner(UR)
        label.shift(2 * LEFT)
        self.add_fixed_in_frame_mobjects(label)

        self.play(FadeInFromDown(label))
        self.wait(3)
        self.change_q(
            [1, 0, 0, 0],
            rate_func=there_and_back,
            run_time=5
        )
        self.wait(3)

    #
    def get_quaternion_label(self, angle_tex):
        vect_label = self.vect_label.copy()
        vect_label.rotate(TAU / 4, LEFT)
        vect_label.replace(TexMobject(vect_label.get_tex_string()))
        vect_label.add_background_rectangle()
        result = VGroup(
            TexMobject("\\big("),
            TexMobject("\\text{cos}(", angle_tex, ")"),
            TexMobject("+"),
            TexMobject("\\text{sin}(", angle_tex, ")"),
            TexMobject("("),
            vect_label,
            TexMobject(")"),
            TexMobject("\\big)"),
        )
        for i in 1, 3:
            result[i][1].set_color(YELLOW)
        result.arrange_submobjects(RIGHT, buff=SMALL_BUFF)
        result.scale(0.7)
        return result


class ExpandOutFullProduct(TeacherStudentsScene):
    def construct(self):
        product = TexMobject(
            """
            (w_0 + x_0 i + y_0 j + z_0 k)
            (x_1 i + y_1 j + z_1 k)
            (w_0 - x_0 i - y_0 j - z_0 k)
            """,
            tex_to_color_map={
                "w_0": W_COLOR, "(": WHITE, ")": WHITE,
                "x_0": I_COLOR, "y_0": J_COLOR, "z_0": K_COLOR,
                "x_1": I_COLOR, "y_1": J_COLOR, "z_1": K_COLOR,
            }
        )
        product.set_width(FRAME_WIDTH - 1)
        product.to_edge(UP)

        n = 10
        q_brace = Brace(product[:n], DOWN)
        p_brace = Brace(product[n:-n], DOWN)
        q_inv_brace = Brace(product[-n:], DOWN)
        braces = VGroup(q_brace, p_brace, q_inv_brace)
        for brace, tex in zip(braces, ["q", "p", "q^{-1}"]):
            brace.add(brace.get_tex(tex))

        words = TextMobject("= Rotation of $p$")
        words.next_to(braces, DOWN)

        self.play(
            self.teacher.change, "raise_right_hand",
            FadeInFromDown(product)
        )
        self.play(
            LaggedStart(GrowFromCenter, braces),
            self.get_student_changes(
                "confused", "horrified", "confused"
            )
        )
        self.wait(2)
        self.play(Write(words))
        self.change_student_modes(
            "pondering", "confused", "erm",
            look_at_arg=words
        )
        self.wait(5)


class Link(Scene):
    def construct(self):
        word = TextMobject("eater.net/quaternions")
        word.add_background_rectangle()
        rect = SurroundingRectangle(word)
        rect.set_color(BLUE)
        arrow = Vector(UR, color=GREEN)
        arrow.next_to(rect, UP)
        arrow.align_to(rect, RIGHT)
        short_arrow = arrow.copy().scale(0.8, about_edge=DL)

        self.add(word)
        self.play(
            ShowCreation(rect),
            GrowArrow(arrow),
        )
        for x in range(10):
            self.play(Transform(
                arrow, short_arrow,
                rate_func=there_and_back,
                run_time=2
            ))
