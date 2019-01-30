from big_ol_pile_of_manim_imports import *


class ConnectionToOptics(Scene):
    def construct(self):
        e_group, m_group = k_groups = self.get_kinematics_groups()
        c_group, a_group = o_groups = self.get_optics_groups()
        arrows = VGroup()
        for g1, g2 in zip(k_groups, o_groups):
            g2.align_to(g1, UP)
            g2.to_edge(RIGHT)
            arrow = TexMobject("\\Rightarrow")
            arrow.scale(1.5)
            arrow.move_to(interpolate(
                g1[0].get_right(), g2[0].get_left(), 0.5
            ))
            arrows.add(arrow)
        everything = VGroup(k_groups, arrows, o_groups)
        everything.to_edge(UP)

        everything.generate_target()
        everything.target.scale(0.9)
        everything.target.to_edge(DOWN)
        width = max([m.get_width() for m in everything.target])
        width += 2 * MED_SMALL_BUFF
        rects = VGroup()
        for k in [0, 2]:
            rect = DashedMobject(Rectangle(
                height=FRAME_HEIGHT - 1.5,
                width=width
            ), dashes_num=100)
            rect.move_to(everything.target[k])
            rect.to_edge(DOWN, buff=SMALL_BUFF)
            rects.add(rect)
        titles = VGroup(
            TextMobject("Kinematics"),
            TextMobject("Optics"),
        )
        titles.scale(1.5)
        for title, rect in zip(titles, rects):
            title.next_to(rect, UP)
        titles[0].align_to(titles[1], UP)

        self.play(FadeInFromDown(e_group))
        self.play(
            Write(arrows[0]),
            FadeInFrom(c_group, LEFT)
        )
        self.wait()
        self.play(FadeInFromDown(m_group))
        self.play(
            Write(arrows[1]),
            FadeInFrom(a_group, LEFT)
        )
        self.wait(4)
        for k in range(2):
            anims = [
                ShowCreation(rects[k]),
                FadeInFromDown(titles[k]),
            ]
            if k == 0:
                anims.append(MoveToTarget(everything))
            self.play(*anims)
            self.wait()
        self.wait()
        self.wait(4)

    def get_kinematics_groups(self):
        tex_to_color_map = {
            "m_1": BLUE,
            "m_2": BLUE,
            "v_1": RED,
            "v_2": RED,
        }
        energy_eq = TexMobject(
            "\\frac{1}{2} m_1 (v_1)^2 + "
            "\\frac{1}{2} m_2 (v_2)^2 = "
            "\\text{const.}",
            tex_to_color_map=tex_to_color_map
        )
        energy_eq.scale(0.8)
        momentum_eq = TexMobject(
            "m_1 v_1 + m_2 v_2 = \\text{const.}",
            tex_to_color_map=tex_to_color_map
        )
        energy_label = TextMobject(
            "Conservation of energy"
        )
        momentum_label = TextMobject(
            "Conservation of momentum"
        )
        energy_group = VGroup(energy_label, energy_eq)
        momentum_group = VGroup(momentum_label, momentum_eq)
        groups = VGroup(energy_group, momentum_group)
        for group in groups:
            group.arrange_submobjects(DOWN, buff=MED_LARGE_BUFF)
            group[0].set_color(GREEN)
        groups.arrange_submobjects(DOWN, buff=2)
        groups.to_edge(LEFT)
        return groups

    def get_optics_groups(self):
        self.time_tracker = ValueTracker(0)
        self.time_tracker.add_updater(
            lambda m, dt: m.increment_value(dt)
        )
        self.add(self.time_tracker)
        return VGroup(
            self.get_speed_group(),
            self.get_angle_group()
        )

    def get_speed_group(self):
        speed_label = TextMobject("Constant speed of light")
        speed_label.set_color(YELLOW)
        speed_light_template = Line(LEFT, RIGHT)
        speed_light_template.fade(1)
        speed_light_template.match_width(speed_label)
        speed_light_template.next_to(speed_label, DOWN, MED_LARGE_BUFF)
        speed_light = speed_light_template.deepcopy()

        def update_speed_light(light, period=2, time_width=0.05):
            time = self.time_tracker.get_value()
            alpha = (time / period) % 1
            # alpha = 1 - 2 * abs(alpha - 0.5)
            alpha *= 1.5
            a = alpha - time_width / 2
            b = alpha + time_width / 2
            light.pointwise_become_partial(
                speed_light_template, max(a, 0), min(b, 1)
            )
            opacity = speed_label.family_members_with_points()[0].get_fill_opacity()
            light.set_stroke(YELLOW, width=3, opacity=opacity)
            # light.stretch(0.5, 0)
            # point = speed_light_template.point_from_proportion(0.25)
            # light.stretch(2, 0, about_point=point)

        speed_light.add_updater(update_speed_light)
        result = VGroup(
            speed_label, speed_light_template, speed_light
        )
        return result

    def get_angle_group(self):
        title = VGroup(*map(TextMobject, [
            "Angle of\\\\Incidence",
            "=",
            "Angle of\\\\Refraction",
        ])).arrange_submobjects(RIGHT)
        title.set_color(YELLOW)
        h_line = Line(LEFT, RIGHT)
        h_line.match_width(title)
        h_line.set_stroke(LIGHT_GREY)
        h_line.set_sheen(1, UL)
        points = [
            h_line.get_left() + UP,
            h_line.get_center(),
            h_line.get_right() + UP,
        ]
        dashed_lines = VGroup(
            DashedLine(*points[0:2]), DashedLine(*points[1:3])
        )
        dashed_lines.set_stroke(WHITE, 2)
        v_shape = VMobject()
        v_shape.set_points_as_corners(points)
        v_shape.fade(1)

        theta = dashed_lines[1].get_angle()
        arcs = VGroup(
            Arc(start_angle=0, angle=theta),
            Arc(start_angle=PI, angle=-theta),
        )
        arcs.set_stroke(WHITE, 2)
        thetas = VGroup()
        for v in LEFT, RIGHT:
            theta = TexMobject("\\theta")
            theta.next_to(arcs, v, aligned_edge=DOWN)
            theta.shift(SMALL_BUFF * UP)
            thetas.add(theta)

        beam = VMobject()

        def update_beam(beam, period=2, time_width=0.05):
            time = self.time_tracker.get_value()
            alpha = (time / period) % 1
            alpha *= 1.5
            a = alpha - time_width / 2
            b = alpha + time_width / 2
            beam.pointwise_become_partial(
                v_shape, max(a, 0), min(b, 1)
            )
            opacity = title.family_members_with_points()[0].get_fill_opacity()
            beam.set_stroke(YELLOW, width=3, opacity=opacity)

        beam.add_updater(update_beam)
        title.next_to(v_shape, UP, MED_LARGE_BUFF)

        return VGroup(
            title, h_line, arcs, thetas,
            dashed_lines, v_shape, beam
        )


class ConnectionToOpticsTransparent(ConnectionToOptics):
    pass
