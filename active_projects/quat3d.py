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
        self.play(
            LaggedStart(
                FadeInFrom, images,
                lambda m: (m, 3 * DOWN),
                lag_ratio=0.75
            ),
            LaggedStart(FadeInFromLarge, names, lag_ratio=0.75),
            *[
                LaggedStart(
                    FadeIn, VGroup(*it.chain(*quote)),
                    lag_ratio=0.3,
                    run_time=3
                )
                for quote in quotes
            ],
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
        self.begin_ambient_camera_rotation(0.01)

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
    CONFIG = {
    }

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


class NewSceneName(Scene):
    def construct(self):
        pass